from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an empty reference verification checklist template for thesis work.")
    parser.add_argument("target_json", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.target_json.parent.mkdir(parents=True, exist_ok=True)
    template = {
        "references": [
            {
                "title": "",
                "authors": [],
                "year": "",
                "source": "",
                "doi_or_url": "",
                "citation_count_if_available": "",
                "relevance_note": "",
                "status": "verified"
            }
        ]
    }
    args.target_json.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.target_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
