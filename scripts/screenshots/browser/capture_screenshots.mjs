import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

function resolveUrl(baseUrl, entryUrl) {
  if (!entryUrl) {
    return baseUrl;
  }
  if (/^https?:\/\//i.test(entryUrl)) {
    return entryUrl;
  }
  if (!baseUrl) {
    throw new Error(`Entry url "${entryUrl}" requires base_url in the plan.`);
  }
  return new URL(entryUrl, baseUrl).toString();
}

function slugify(label) {
  const normalized = label.replace(/[\\/:*?"<>|]/g, "-").replace(/\s+/g, "-").trim();
  return normalized || "screenshot";
}

async function waitForEntry(page, entry) {
  if (entry.wait_for_timeout_ms) {
    await page.waitForTimeout(entry.wait_for_timeout_ms);
  }
  if (entry.wait_for_text) {
    await page.getByText(entry.wait_for_text, { exact: false }).first().waitFor({ state: "visible", timeout: entry.timeout_ms ?? 15000 });
  }
  if (entry.wait_for_selector) {
    await page.waitForSelector(entry.wait_for_selector, { state: "visible", timeout: entry.timeout_ms ?? 15000 });
  }
}

async function applyActions(page, entry) {
  for (const action of entry.actions ?? []) {
    switch (action.type) {
      case "click":
        await page.locator(action.selector).first().click();
        break;
      case "fill":
        await page.locator(action.selector).first().fill(action.value ?? "");
        break;
      case "press":
        await page.locator(action.selector).first().press(action.key);
        break;
      case "wait_for_selector":
        await page.waitForSelector(action.selector, { state: action.state ?? "visible", timeout: action.timeout_ms ?? 15000 });
        break;
      case "wait_for_text":
        await page.getByText(action.text, { exact: false }).first().waitFor({ state: "visible", timeout: action.timeout_ms ?? 15000 });
        break;
      case "wait_for_timeout":
        await page.waitForTimeout(action.timeout_ms ?? 1000);
        break;
      default:
        throw new Error(`Unsupported action type: ${action.type}`);
    }
  }
}

async function main() {
  const planPath = process.argv[2];
  if (!planPath) {
    console.error("Usage: node scripts/screenshots/browser/capture_screenshots.mjs <plan.json>");
    process.exit(1);
  }

  const absolutePlanPath = path.resolve(planPath);
  const plan = JSON.parse(fs.readFileSync(absolutePlanPath, "utf8").replace(/^\uFEFF/, ""));
  const workspaceRoot = plan.workspace_root
    ? path.resolve(path.dirname(absolutePlanPath), plan.workspace_root)
    : path.dirname(absolutePlanPath);
  const outputDir = path.resolve(workspaceRoot, plan.output_dir ?? "paper-output/screenshots");
  fs.mkdirSync(outputDir, { recursive: true });

  const browser = plan.cdp_url
    ? await chromium.connectOverCDP(plan.cdp_url)
    : await chromium.launch({ headless: plan.headless !== false });

  const context = plan.cdp_url
    ? browser.contexts()[0]
    : await browser.newContext({
        viewport: plan.viewport ?? { width: 1440, height: 900 },
        ignoreHTTPSErrors: true
      });

  const page = context.pages()[0] ?? await context.newPage();
  const imageMap = {};

  try {
    for (const entry of plan.entries ?? []) {
      const targetUrl = resolveUrl(plan.base_url, entry.url);
      await page.goto(targetUrl, { waitUntil: entry.wait_until ?? "networkidle", timeout: entry.timeout_ms ?? 30000 });
      await applyActions(page, entry);
      await waitForEntry(page, entry);

      const filename = entry.filename ?? `${slugify(entry.label)}.png`;
      const outputPath = path.resolve(outputDir, filename);
      const locator = entry.clip_selector ? page.locator(entry.clip_selector).first() : null;

      if (locator) {
        await locator.screenshot({ path: outputPath, type: "png" });
      } else {
        await page.screenshot({ path: outputPath, fullPage: entry.full_page !== false, type: "png" });
      }

      imageMap[entry.label] = outputPath;
      console.log(`CAPTURED\t${entry.label}\t${outputPath}`);
    }
  } finally {
    const imageMapPath = path.resolve(workspaceRoot, plan.image_map_output ?? "paper-output/image-map.json");
    fs.writeFileSync(imageMapPath, JSON.stringify(imageMap, null, 2), "utf8");
    console.log(`IMAGE_MAP\t${imageMapPath}`);
    if (plan.cdp_url) {
      await browser.close();
    } else {
      await context.close();
      await browser.close();
    }
  }
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
