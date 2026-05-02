from __future__ import annotations

import json
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"^\[此处插入截图：(.+?)\]$")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python extract_screenshot_placeholders.py <markdown-file> [--json-out path]")
        return 1

    source = Path(sys.argv[1])
    labels = []
    for line in source.read_text(encoding="utf-8").splitlines():
        m = PLACEHOLDER_RE.match(line.strip())
        if m:
            labels.append(m.group(1).strip())

    print("COUNT\t" + str(len(labels)))
    for label in labels:
        print(label)

    if len(sys.argv) >= 4 and sys.argv[2] == "--json-out":
        Path(sys.argv[3]).write_text(
            json.dumps({"labels": labels}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
