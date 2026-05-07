from __future__ import annotations

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn


SCHEMA_VERSION = "1.0"

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

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


def latin_font(run) -> str | None:
    if run._element.rPr is not None and run._element.rPr.rFonts is not None:
        return run._element.rPr.rFonts.get(qn("w:ascii")) or run._element.rPr.rFonts.get(qn("w:hAnsi"))
    return run.font.name


def line_spacing_rule_name(value: Any) -> str | None:
    mapping = {
        WD_LINE_SPACING.SINGLE: "single",
        WD_LINE_SPACING.ONE_POINT_FIVE: "multiple",
        WD_LINE_SPACING.DOUBLE: "multiple",
        WD_LINE_SPACING.AT_LEAST: "at_least",
        WD_LINE_SPACING.EXACTLY: "exactly",
        WD_LINE_SPACING.MULTIPLE: "multiple",
    }
    return mapping.get(value)


def paragraph_signature(paragraph) -> dict[str, Any]:
    run_fonts = []
    east_asia_fonts = []
    latin_fonts = []
    run_sizes = []
    bold_values = []

    for run in paragraph.runs:
        if not run.text.strip():
            continue
        ea_font = east_asia_font(run)
        lat_font = latin_font(run)
        run_fonts.append((ea_font or lat_font or "").strip())
        east_asia_fonts.append((ea_font or "").strip())
        latin_fonts.append((lat_font or "").strip())
        if run.font.size:
            run_sizes.append(round(run.font.size.pt, 1))
        if run.bold is not None:
            bold_values.append(bool(run.bold))

    first_line_indent = paragraph.paragraph_format.first_line_indent
    left_indent = paragraph.paragraph_format.left_indent
    line_spacing = paragraph.paragraph_format.line_spacing
    line_spacing_rule = paragraph.paragraph_format.line_spacing_rule
    page_break_before = False
    p_pr = paragraph._p.pPr
    if p_pr is not None and p_pr.pageBreakBefore is not None:
        page_break_before = True

    return {
        "font": most_common(run_fonts),
        "east_asia_font": most_common(east_asia_fonts),
        "latin_font": most_common(latin_fonts),
        "size_pt": most_common(run_sizes),
        "bold": most_common(bold_values, default=False),
        "alignment": alignment_name(paragraph.alignment),
        "first_line_indent_pt": round(first_line_indent.pt, 1) if first_line_indent is not None else None,
        "left_indent_pt": round(left_indent.pt, 1) if left_indent is not None else None,
        "line_spacing": round(float(line_spacing), 2) if isinstance(line_spacing, (int, float)) else None,
        "line_spacing_rule": line_spacing_rule_name(line_spacing_rule),
        "space_before_pt": round(paragraph.paragraph_format.space_before.pt, 1)
        if paragraph.paragraph_format.space_before
        else None,
        "space_after_pt": round(paragraph.paragraph_format.space_after.pt, 1)
        if paragraph.paragraph_format.space_after
        else None,
        "page_break_before": page_break_before if page_break_before else None,
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


def clean_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def detect_heading_level(text: str) -> int | None:
    normalized = re.sub(r"\s+", " ", text).strip()
    if TITLE_PATTERNS["heading3"].match(normalized):
        return 3
    if TITLE_PATTERNS["heading2"].match(normalized):
        return 2
    if TITLE_PATTERNS["heading1"].match(normalized):
        return 1
    return None


def outline_structure(document: Document) -> list[dict[str, Any]]:
    outline = []
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        level = detect_heading_level(text)
        if level is None:
            continue
        outline.append(
            {
                "level": level,
                "title": re.sub(r"\s+", " ", text),
                "source": "python-docx paragraphs",
                "confidence": "medium",
                "notes": "Detected from heading-like paragraph text.",
            }
        )
    return outline


def chapter_word_distribution(document: Document) -> list[dict[str, Any]]:
    chapters: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        level = detect_heading_level(text)
        if level == 1:
            if current is not None:
                chapters.append(current)
            current = {
                "chapter": re.sub(r"\s+", " ", text),
                "words": 0,
                "source": "python-docx paragraphs",
                "confidence": "medium",
                "notes": "Approximate count from visible paragraph text.",
            }
            continue
        if current is not None and level is None:
            current["words"] += clean_count(text)
    if current is not None:
        chapters.append(current)
    return chapters


def figure_table_rhythm(document: Document) -> list[dict[str, Any]]:
    patterns = []
    caption_rules = [
        ("figure_caption", re.compile(r"^图\s*\d+[-.]\d+\s*\S+|^图\d+[-.]\d+\s*\S+")),
        ("table_caption", re.compile(r"^表\s*\d+[-.]\d+\s*\S+|^表\d+[-.]\d+\s*\S+")),
    ]
    for paragraph in document.paragraphs:
        normalized = re.sub(r"\s+", " ", paragraph.text).strip()
        for label, pattern in caption_rules:
            if pattern.match(normalized):
                patterns.append(
                    {
                        "pattern": f"{label}: {normalized}",
                        "source": "python-docx paragraphs",
                        "confidence": "medium",
                        "notes": "Detected from visible DOCX text; confirm against original sample.",
                    }
                )
    return patterns


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
            "east_asia_font": most_common([item["east_asia_font"] for item in signatures]),
            "latin_font": most_common([item["latin_font"] for item in signatures]),
            "size_pt": most_common([item["size_pt"] for item in signatures]),
            "bold": most_common([item["bold"] for item in signatures]),
            "alignment": most_common([item["alignment"] for item in signatures], default="left"),
            "first_line_indent_pt": most_common([item["first_line_indent_pt"] for item in signatures]),
            "left_indent_pt": most_common([item["left_indent_pt"] for item in signatures]),
            "line_spacing": most_common([item["line_spacing"] for item in signatures]),
            "line_spacing_rule": most_common([item["line_spacing_rule"] for item in signatures]),
            "space_before_pt": most_common([item["space_before_pt"] for item in signatures]),
            "space_after_pt": most_common([item["space_after_pt"] for item in signatures]),
            "page_break_before": most_common([item["page_break_before"] for item in signatures]),
            "sample_count": len(signatures),
        }

    return result


def read_docx_part(docx_path: Path, part_name: str) -> str | None:
    with zipfile.ZipFile(docx_path) as archive:
        try:
            return archive.read(part_name).decode("utf-8")
        except KeyError:
            return None


def ooxml_text(element: ET.Element) -> str:
    parts = []
    for node in element.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local == "t":
            parts.append(node.text or "")
        elif local == "tab":
            parts.append("\t")
        elif local == "br":
            parts.append("\n")
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def w_attr(element: ET.Element | None, name: str, default: str = "") -> str:
    if element is None:
        return default
    return element.attrib.get(f"{{{NS['w']}}}{name}", default)


def header_footer_texts(docx_path: Path) -> list[dict[str, Any]]:
    observations = []
    with zipfile.ZipFile(docx_path) as archive:
        part_names = [
            name
            for name in archive.namelist()
            if re.match(r"word/(header|footer)\d+\.xml$", name)
        ]
        for part_name in sorted(part_names):
            root = ET.fromstring(archive.read(part_name))
            text = ooxml_text(root)
            if text:
                observations.append(
                    {
                        "observation": "header_footer_text",
                        "source": part_name,
                        "confidence": "high",
                        "notes": text[:240],
                    }
                )
    return observations


def section_property_observations(docx_path: Path) -> list[dict[str, Any]]:
    document_xml = read_docx_part(docx_path, "word/document.xml")
    if not document_xml:
        return []
    root = ET.fromstring(document_xml)
    observations = []
    for idx, sect_pr in enumerate(root.findall(".//w:sectPr", NS), start=1):
        page_size = sect_pr.find("w:pgSz", NS)
        page_margin = sect_pr.find("w:pgMar", NS)
        details = []
        if page_size is not None:
            details.append(
                f"page_size width={w_attr(page_size, 'w')} height={w_attr(page_size, 'h')}"
            )
        if page_margin is not None:
            details.append(
                "margins "
                f"top={w_attr(page_margin, 'top')} right={w_attr(page_margin, 'right')} "
                f"bottom={w_attr(page_margin, 'bottom')} left={w_attr(page_margin, 'left')}"
            )
        observations.append(
            {
                "observation": "section_properties",
                "source": f"word/document.xml sectPr[{idx}]",
                "confidence": "high",
                "notes": "; ".join(details) if details else "section properties present",
            }
        )
    return observations


def section_page_setup(docx_path: Path) -> dict[str, int]:
    document_xml = read_docx_part(docx_path, "word/document.xml")
    if not document_xml:
        return {}
    root = ET.fromstring(document_xml)
    sect_pr = root.find(".//w:sectPr", NS)
    if sect_pr is None:
        return {}

    page_size = sect_pr.find("w:pgSz", NS)
    page_margin = sect_pr.find("w:pgMar", NS)
    setup: dict[str, int] = {}
    if page_size is not None:
        width = w_attr(page_size, "w")
        height = w_attr(page_size, "h")
        if width.isdigit():
            setup["page_width_twips"] = int(width)
        if height.isdigit():
            setup["page_height_twips"] = int(height)
    if page_margin is not None:
        for attr, key in [
            ("top", "margin_top_twips"),
            ("right", "margin_right_twips"),
            ("bottom", "margin_bottom_twips"),
            ("left", "margin_left_twips"),
        ]:
            value = w_attr(page_margin, attr)
            if value.isdigit():
                setup[key] = int(value)
    return setup


def style_definition_observations(docx_path: Path) -> list[dict[str, Any]]:
    styles_xml = read_docx_part(docx_path, "word/styles.xml")
    if not styles_xml:
        return []
    root = ET.fromstring(styles_xml)
    styles = root.findall("w:style", NS)
    heading_names = []
    for style in styles:
        style_id = w_attr(style, "styleId")
        name = style.find("w:name", NS)
        display_name = w_attr(name, "val") if name is not None else style_id
        if style_id.lower().startswith("heading") or "heading" in display_name.lower():
            heading_names.append(display_name)
    notes = f"style_count={len(styles)}"
    if heading_names:
        notes += "; headings=" + ", ".join(heading_names[:8])
    return [
        {
            "observation": "style_definitions",
            "source": "word/styles.xml",
            "confidence": "high",
            "notes": notes,
        }
    ]


def numbering_observations(docx_path: Path) -> list[dict[str, Any]]:
    numbering_xml = read_docx_part(docx_path, "word/numbering.xml")
    if not numbering_xml:
        return []
    root = ET.fromstring(numbering_xml)
    abstract_count = len(root.findall("w:abstractNum", NS))
    instance_count = len(root.findall("w:num", NS))
    return [
        {
            "observation": "numbering_definitions",
            "source": "word/numbering.xml",
            "confidence": "high",
            "notes": f"abstract_numbering={abstract_count}; numbering_instances={instance_count}",
        }
    ]


def collect_ooxml_observations(docx_path: Path) -> list[dict[str, Any]]:
    observations = []
    observations.extend(header_footer_texts(docx_path))
    observations.extend(section_property_observations(docx_path))
    observations.extend(style_definition_observations(docx_path))
    observations.extend(numbering_observations(docx_path))
    return observations


def style_observations(styles: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "observation": category,
            "source": "python-docx paragraph styles",
            "confidence": "medium",
            "notes": (
                f"font={style.get('font')}; size_pt={style.get('size_pt')}; "
                f"bold={style.get('bold')}; alignment={style.get('alignment')}; "
                f"sample_count={style.get('sample_count')}"
            ),
        }
        for category, style in sorted(styles.items())
    ]


def analyze_docx(docx_path: Path) -> dict[str, Any]:
    document = Document(docx_path)
    styles = aggregate_styles(document)
    observations = style_observations(styles) + collect_ooxml_observations(docx_path)
    page_setup = section_page_setup(docx_path)
    outline = outline_structure(document)
    word_distribution = chapter_word_distribution(document)
    rhythm = figure_table_rhythm(document)
    limitations = []
    if not styles:
        limitations.append("No classifiable paragraph styles were detected.")
    if not outline:
        limitations.append("No heading-like outline structure was detected.")
    if not observations:
        limitations.append("No DOCX style or OOXML observations were extracted.")

    return {
        "schema_version": SCHEMA_VERSION,
        "parser": {
            "name": "analyze_docx.py",
            "version": SCHEMA_VERSION,
            "engine": ["python-docx", "zipfile", "xml.etree.ElementTree"],
        },
        "source": {
            "path": str(docx_path),
            "source_type": "sample_docx",
            "parser": "analyze_docx.py",
            "parser_status": "parsed" if observations else "partial",
            "limitations": limitations,
        },
        "template_rules": {
            "confirmed": [],
            "needs_confirmation": [],
        },
        "sample_patterns": {
            "outline_structure": outline,
            "chapter_word_distribution": word_distribution,
            "figure_table_rhythm": rhythm,
            "style_observations": observations,
        },
        "page_setup": page_setup,
        "recommendations": {
            "outline_suggestion": [],
            "word_budget": [],
            "user_decisions_needed": [],
        },
        "confidence": {
            "structure": "low",
            "word_count": "low",
            "style": "medium" if observations else "low",
        },
        "source_file": str(docx_path),
        "styles": styles,
    }


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
    payload = analyze_docx(docx_path)
    styles = payload["styles"]

    if len(sys.argv) >= 4 and sys.argv[2] == "--json-out":
        output_path = Path(sys.argv[3])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print_summary(docx_path, styles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
