from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader


SCHEMA_VERSION = "1.0"

HEADING_PATTERNS = [
    (1, re.compile(r"^第[一二三四五六七八九十\d]+章\s+\S+")),
    (2, re.compile(r"^\d+\.\d+\s+\S+")),
    (3, re.compile(r"^\d+\.\d+\.\d+\s+\S+")),
]


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
            out.append({"level": level, "title": title, "page": page, "source": "pypdf_outline"})
    return out


def find_end_page(items, idx, total_pages):
    cur = items[idx]
    for j in range(idx + 1, len(items)):
        if items[j]["level"] <= cur["level"]:
            return max(cur["page"], items[j]["page"] - 1)
    return total_pages


def extract_pypdf_pages(reader) -> list[str]:
    return [page.extract_text() or "" for page in reader.pages]


def extract_pdfplumber_pages(path: Path) -> list[dict[str, Any]]:
    pages = []
    with pdfplumber.open(str(path)) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            tables = page.extract_tables() or []
            pages.append({"page": index, "text": text, "table_count": len(tables)})
    return pages


def detect_heading(line: str) -> tuple[int, str] | None:
    normalized = re.sub(r"\s+", " ", line).strip()
    for level, pattern in HEADING_PATTERNS:
        if pattern.match(normalized):
            return level, normalized
    return None


def outline_from_pdfplumber(layout_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outline = []
    for page in layout_pages:
        for line in page["text"].splitlines():
            heading = detect_heading(line)
            if heading:
                level, title = heading
                outline.append(
                    {
                        "level": level,
                        "title": title,
                        "page": page["page"],
                        "source": "pdfplumber_text",
                    }
                )
    return outline


def sections_from_outline(outline: list[dict[str, Any]], pages: list[str], total_pages: int) -> list[dict[str, Any]]:
    sections = []
    for idx, item in enumerate(outline):
        end_page = find_end_page(outline, idx, total_pages)
        text = "\n".join(pages[item["page"] - 1 : end_page])
        sections.append(
            {
                "level": item["level"],
                "title": item["title"],
                "start_page": item["page"],
                "end_page": end_page,
                "char_count": clean_count(text),
                "source": item.get("source", "unknown"),
            }
        )
    return sections


def caption_patterns(layout_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    patterns = []
    caption_rules = [
        ("figure_caption", re.compile(r"^图\s*\d+[-.]\d+\s*\S+|^图\d+[-.]\d+\s*\S+")),
        ("table_caption", re.compile(r"^表\s*\d+[-.]\d+\s*\S+|^表\d+[-.]\d+\s*\S+")),
    ]
    for page in layout_pages:
        for line in page["text"].splitlines():
            normalized = re.sub(r"\s+", " ", line).strip()
            for label, pattern in caption_rules:
                if pattern.match(normalized):
                    patterns.append(
                        {
                            "pattern": f"{label}: {normalized}",
                            "source": f"page {page['page']} pdfplumber_text",
                            "confidence": "medium",
                            "notes": "Detected from visible PDF text; confirm against original sample.",
                        }
                    )
        if page["table_count"]:
            patterns.append(
                {
                    "pattern": f"table_objects: {page['table_count']} table candidate(s)",
                    "source": f"page {page['page']} pdfplumber_table",
                    "confidence": "medium",
                    "notes": "Detected by pdfplumber table extraction.",
                }
            )
    return patterns


def build_payload(path: Path, pages: list[str], sections: list[dict[str, Any]], layout_pages: list[dict[str, Any]], used_fallback: bool) -> dict[str, Any]:
    limitations = []
    if used_fallback:
        limitations.append("PDF outline was missing or unusable; headings were inferred from visible text.")
    if not sections:
        limitations.append("No section headings were detected.")
    if not layout_pages:
        limitations.append("pdfplumber layout extraction was unavailable.")

    outline_structure = [
        {
            "level": section["level"],
            "title": section["title"],
            "start_page": section["start_page"],
            "end_page": section["end_page"],
            "source": section["source"],
            "confidence": "medium" if section["source"] == "pdfplumber_text" else "high",
            "notes": f"char_count={section['char_count']}",
        }
        for section in sections
    ]
    word_distribution = [
        {
            "chapter": section["title"],
            "words": section["char_count"],
            "source": section["source"],
            "confidence": "medium" if section["source"] == "pdfplumber_text" else "high",
            "notes": f"pages {section['start_page']}-{section['end_page']}",
        }
        for section in sections
        if section["level"] == 1
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "parser": {
            "name": "analyze_sample_pdf.py",
            "version": SCHEMA_VERSION,
            "engine": ["pypdf", "pdfplumber"],
        },
        "source": {
            "path": str(path),
            "source_type": "sample_pdf",
            "parser": "analyze_sample_pdf.py",
            "parser_status": "parsed" if sections else "partial",
            "limitations": limitations,
        },
        "template_rules": {
            "confirmed": [],
            "needs_confirmation": [],
        },
        "sample_patterns": {
            "outline_structure": outline_structure,
            "chapter_word_distribution": word_distribution,
            "figure_table_rhythm": caption_patterns(layout_pages),
            "style_observations": [],
        },
        "recommendations": {
            "outline_suggestion": [],
            "word_budget": [],
            "user_decisions_needed": [],
        },
        "confidence": {
            "structure": "medium" if used_fallback and sections else ("high" if sections else "low"),
            "word_count": "medium" if sections else "low",
            "style": "low",
        },
        "file": str(path),
        "total_pages": len(pages),
        "sections": sections,
    }


def analyze_pdf(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    pages = extract_pypdf_pages(reader)
    try:
        outline = walk_outline(reader.outline, reader)
    except Exception:
        outline = []

    layout_pages: list[dict[str, Any]] = []
    used_fallback = False
    if not outline:
        try:
            layout_pages = extract_pdfplumber_pages(path)
            outline = outline_from_pdfplumber(layout_pages)
            pages = [page["text"] for page in layout_pages] or pages
            used_fallback = True
        except Exception:
            layout_pages = []
    else:
        try:
            layout_pages = extract_pdfplumber_pages(path)
        except Exception:
            layout_pages = []

    total_pages = max(len(pages), len(layout_pages))
    sections = sections_from_outline(outline, pages, total_pages)
    return build_payload(path, pages, sections, layout_pages, used_fallback)


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
        json_out.parent.mkdir(parents=True, exist_ok=True)
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
