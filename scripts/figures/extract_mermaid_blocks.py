from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CAPTION_RE = re.compile(r"^(图\s*\d+(?:\.\d+)?\s+.+)$")


def safe_name(text: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", text).strip("-")
    return cleaned[:80] or "diagram"


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python extract_mermaid_blocks.py <markdown-file> <output-dir> [--manifest path]")
        return 1

    source = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    manifest_path = None
    if len(sys.argv) >= 5 and sys.argv[3] == "--manifest":
        manifest_path = Path(sys.argv[4])

    out_dir.mkdir(parents=True, exist_ok=True)
    lines = source.read_text(encoding="utf-8").splitlines()
    in_mermaid = False
    buffer: list[str] = []
    pending_blocks: list[dict] = []
    results: list[dict] = []
    index = 0

    for line in lines:
        stripped = line.strip()
        if in_mermaid:
            if stripped.startswith("```"):
                pending_blocks.append({"content": "\n".join(buffer)})
                in_mermaid = False
                buffer = []
            else:
                buffer.append(line.rstrip())
            continue

        if stripped.startswith("```mermaid"):
            in_mermaid = True
            buffer = []
            continue

        cap = CAPTION_RE.match(stripped)
        if cap and pending_blocks:
            block = pending_blocks.pop(0)
            index += 1
            caption = cap.group(1).strip()
            filename = f"{index:02d}-{safe_name(caption)}.mmd"
            file_path = out_dir / filename
            file_path.write_text(block["content"], encoding="utf-8")
            results.append(
                {
                    "caption": caption,
                    "mmd": str(file_path),
                    "png": str(file_path.with_suffix(".png")),
                    "svg": str(file_path.with_suffix(".svg")),
                }
            )

    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"COUNT\t{len(results)}")
    for item in results:
        print(f"{item['caption']}\t{item['mmd']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
