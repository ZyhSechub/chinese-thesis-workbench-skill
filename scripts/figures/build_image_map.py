from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python build_image_map.py <labels.json> <image-dir> <output.json> [--manual manual-map.json]")
        return 1

    labels_path = Path(sys.argv[1])
    image_dir = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    manual_path = None
    if len(sys.argv) >= 6 and sys.argv[4] == "--manual":
        manual_path = Path(sys.argv[5])

    labels = json.loads(labels_path.read_text(encoding="utf-8")).get("labels", [])
    manual_map = {}
    if manual_path and manual_path.exists():
        manual_map = json.loads(manual_path.read_text(encoding="utf-8"))
    result = {}
    for label in labels:
        if label in manual_map:
            manual_target = Path(manual_map[label])
            if manual_target.exists():
                result[label] = str(manual_target)
                continue
        candidates = [
            image_dir / f"{label}.png",
            image_dir / f"{label}.jpg",
            image_dir / f"{label}.jpeg",
        ]
        for candidate in candidates:
            if candidate.exists():
                result[label] = str(candidate)
                break

    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
