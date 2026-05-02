from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_JSON = REPO_ROOT / "package.json"


def npm_command() -> list[str]:
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("npm is required for Playwright bootstrap, but it was not found in PATH.")
    return [npm]


def ensure_playwright_installed() -> None:
    node_modules = REPO_ROOT / "node_modules" / "playwright"
    if node_modules.exists():
        return

    subprocess.run(npm_command() + ["install"], cwd=REPO_ROOT, check=True)
    subprocess.run(npm_command() + ["run", "install:browsers"], cwd=REPO_ROOT, check=True)


def run_capture(plan_path: Path) -> None:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node.js is required for browser capture, but it was not found in PATH.")

    script = REPO_ROOT / "scripts" / "screenshots" / "browser" / "capture_screenshots.mjs"
    subprocess.run([node, str(script), str(plan_path)], cwd=REPO_ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture thesis screenshots with the repository-bundled Playwright flow.")
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--skip-bootstrap", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not PACKAGE_JSON.exists():
        print("package.json not found; Playwright bootstrap is unavailable.")
        return 1

    try:
        if not args.skip_bootstrap:
            ensure_playwright_installed()
        run_capture(args.plan_json)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        return exc.returncode
    except RuntimeError as exc:
        print(str(exc))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
