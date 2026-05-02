from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


TITLE_PATTERNS = {
    "heading1": re.compile(r"^第.+章"),
    "heading2": re.compile(r"^\d+\.\d+(?!\.)"),
    "heading3": re.compile(r"^\d+\.\d+\.\d+"),
}


def alignment_name(value: int | None) -> str:
    mapping = {
        None: "left",
        WD_ALIGN_PARAGRAPH.LEFT: "left",
        WD_ALIGN_PARAGRAPH.CENTER: "center",
        WD_ALIGN_PARAGRAPH.RIGHT: "right",
        WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
        WD_ALIGN_PARAGRAPH.DISTRIBUTE: "distribute",
    }
    return mapping.get(value, "left")


def east_asia_font(run) -> str | None:
    if run._element.rPr is None or run._element.rPr.rFonts is None:
        return None
    return run._element.rPr.rFonts.get(qn("w:eastAsia"))


def paragraph_signature(paragraph) -> dict[str, Any]:
    run_fonts = []
    run_sizes = []
    bold_values = []

    for run in paragraph.runs:
        if not run.text.strip():
            continue
        run_fonts.append((east_asia_font(run) or run.font.name or "").strip())
        if run.font.size:
            run_sizes.append(round(run.font.size.pt, 1))
        if run.bold is not None:
            bold_values.append(bool(run.bold))

    first_line_indent = paragraph.paragraph_format.first_line_indent
    line_spacing = paragraph.paragraph_format.line_spacing
    page_break_before = False
    p_pr = paragraph._p.pPr
    if p_pr is not None and p_pr.pageBreakBefore is not None:
        page_break_before = True

    return {
        "font": most_common(run_fonts),
        "size_pt": most_common(run_sizes),
        "bold": most_common(bold_values, default=False),
        "alignment": alignment_name(paragraph.alignment),
        "first_line_indent_pt": round(first_line_indent.pt, 1) if first_line_indent else 0.0,
        "line_spacing": round(float(line_spacing), 2) if isinstance(line_spacing, (int, float)) else None,
        "space_before_pt": round(paragraph.paragraph_format.space_before.pt, 1)
        if paragraph.paragraph_format.space_before
        else 0.0,
        "space_after_pt": round(paragraph.paragraph_format.space_after.pt, 1)
        if paragraph.paragraph_format.space_after
        else 0.0,
        "page_break_before": page_break_before,
    }


def most_common(values: list[Any], default: Any = None) -> Any:
    filtered = [value for value in values if value not in ("", None)]
    if not filtered:
        return default
    return Counter(filtered).most_common(1)[0][0]


def classify_paragraph(text: str, in_reference_section: bool) -> str | None:
    normalized = text.strip()
    if not normalized:
        return None

    if normalized == "摘要":
        return "abstract_heading_cn"
    if normalized.lower() == "abstract":
        return "abstract_heading_en"
    if normalized == "参考文献":
        return "references_heading"
    if normalized == "致谢":
        return "ack_heading"
    if normalized.startswith("关键词"):
        return "keywords_cn"
    if normalized.startswith("Keywords"):
        return "keywords_en"
    if normalized.startswith("图"):
        return "figure_caption"
    if normalized.startswith("表"):
        return "table_caption"
    if in_reference_section and re.match(r"^\[\d+\]", normalized):
        return "references_body"

    if TITLE_PATTERNS["heading3"].match(normalized):
        return "heading3"
    if TITLE_PATTERNS["heading2"].match(normalized):
        return "heading2"
    if TITLE_PATTERNS["heading1"].match(normalized):
        return "heading1"

    if re.search(r"[A-Za-z]{3,}", normalized) and not re.search(r"[\u4e00-\u9fff]", normalized):
        return "body_en"
    return "body_cn"


def aggregate_styles(document: Document) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    in_reference_section = False

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text == "参考文献":
            in_reference_section = True
        elif re.match(r"^第.+章", text):
            in_reference_section = False

        category = classify_paragraph(text, in_reference_section)
        if category is None:
            continue
        grouped[category].append(paragraph_signature(paragraph))

    result = {}
    for category, signatures in grouped.items():
        result[category] = {
            "font": most_common([item["font"] for item in signatures]),
            "size_pt": most_common([item["size_pt"] for item in signatures]),
            "bold": most_common([item["bold"] for item in signatures], default=False),
            "alignment": most_common([item["alignment"] for item in signatures], default="left"),
            "first_line_indent_pt": most_common([item["first_line_indent_pt"] for item in signatures], default=0.0),
            "line_spacing": most_common([item["line_spacing"] for item in signatures]),
            "space_before_pt": most_common([item["space_before_pt"] for item in signatures], default=0.0),
            "space_after_pt": most_common([item["space_after_pt"] for item in signatures], default=0.0),
            "page_break_before": most_common([item["page_break_before"] for item in signatures], default=False),
            "sample_count": len(signatures),
        }

    return result


def print_summary(path: Path, styles: dict[str, Any]) -> None:
    print(f"FILE\t{path}")
    ordered_keys = [
        "heading1",
        "heading2",
        "heading3",
        "body_cn",
        "body_en",
        "abstract_heading_cn",
        "abstract_heading_en",
        "keywords_cn",
        "keywords_en",
        "figure_caption",
        "table_caption",
        "references_body",
    ]
    for key in ordered_keys:
        if key not in styles:
            continue
        style = styles[key]
        print(
            f"{key}\tfont={style['font']}\tsize_pt={style['size_pt']}\tbold={style['bold']}"
            f"\talignment={style['alignment']}\tfirst_line_indent_pt={style['first_line_indent_pt']}"
            f"\tline_spacing={style['line_spacing']}\tpage_break_before={style['page_break_before']}"
        )


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python analyze_docx.py <docx> [--json-out path]")
        return 1

    docx_path = Path(sys.argv[1])
    document = Document(docx_path)
    styles = aggregate_styles(document)
    payload = {
        "source_file": str(docx_path),
        "styles": styles,
    }

    if len(sys.argv) >= 4 and sys.argv[2] == "--json-out":
        output_path = Path(sys.argv[3])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print_summary(docx_path, styles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
