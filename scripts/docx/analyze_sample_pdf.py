from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader


def clean_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def walk_outline(items, reader, level=1, out=None):
    if out is None:
        out = []
    for item in items:
        if isinstance(item, list):
            walk_outline(item, reader, level + 1, out)
        else:
            title = item.get("/Title", "").strip()
            if not title:
                continue
            try:
                page = reader.get_destination_page_number(item) + 1
            except Exception:
                continue
            out.append({"level": level, "title": title, "page": page})
    return out


def find_end_page(items, idx, total_pages):
    cur = items[idx]
    for j in range(idx + 1, len(items)):
        if items[j]["level"] <= cur["level"]:
            return max(cur["page"], items[j]["page"] - 1)
    return total_pages


def analyze_pdf(path: Path) -> dict:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    outline = walk_outline(reader.outline, reader)
    sections = []
    for idx, item in enumerate(outline):
        end_page = find_end_page(outline, idx, len(pages))
        text = "\n".join(pages[item["page"] - 1 : end_page])
        sections.append(
            {
                "level": item["level"],
                "title": item["title"],
                "start_page": item["page"],
                "end_page": end_page,
                "char_count": clean_count(text),
            }
        )
    return {
        "file": str(path),
        "total_pages": len(pages),
        "sections": sections,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python analyze_sample_pdf.py <pdf> [--json-out path]")
        return 1

    pdf_path = Path(sys.argv[1])
    result = analyze_pdf(pdf_path)

    json_out = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--json-out":
        json_out = Path(sys.argv[3])

    if json_out:
        json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"FILE\t{result['file']}")
    print(f"TOTAL_PAGES\t{result['total_pages']}")
    for section in result["sections"]:
        if section["level"] <= 2:
            print(
                f"{section['title']}\t"
                f"p.{section['start_page']}-{section['end_page']}\t"
                f"{section['char_count']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
