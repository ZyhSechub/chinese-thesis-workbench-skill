from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def safe_filename(label: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "-", label).strip() or "screenshot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a screenshot capture plan from thesis screenshot placeholders.")
    parser.add_argument("labels_json", type=Path)
    parser.add_argument("output_plan", type=Path)
    parser.add_argument("--base-url", dest="base_url", default="")
    parser.add_argument("--output-dir", dest="output_dir", default="paper-output/screenshots")
    parser.add_argument("--image-map", dest="image_map_output", default="paper-output/image-map.json")
    parser.add_argument("--cdp-url", dest="cdp_url", default="")
    parser.add_argument("--workspace-root", dest="workspace_root", default=".")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.labels_json.read_text(encoding="utf-8-sig"))
    labels = payload.get("labels", [])
    entries = []

    for label in labels:
        entries.append(
            {
                "label": label,
                "url": "",
                "wait_for_selector": "",
                "wait_for_text": "",
                "clip_selector": "",
                "filename": f"{safe_filename(label)}.png",
                "full_page": True,
                "actions": [],
            }
        )

    plan = {
        "base_url": args.base_url,
        "cdp_url": args.cdp_url,
        "workspace_root": args.workspace_root,
        "output_dir": args.output_dir,
        "image_map_output": args.image_map_output,
        "headless": True,
        "viewport": {"width": 1440, "height": 900},
        "entries": entries,
    }

    args.output_plan.parent.mkdir(parents=True, exist_ok=True)
    args.output_plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output_plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
