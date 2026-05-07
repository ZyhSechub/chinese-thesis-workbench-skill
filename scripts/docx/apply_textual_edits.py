from __future__ import annotations

import argparse
import json
import re
import shutil
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

import yaml
from docx import Document
from docx.text.paragraph import Paragraph


CHAPTER_RE = re.compile(r"^##\s+(第?[一二三四五六七八九十百0-9]+章\s*.*)$")
CHAPTER_KEY_RE = re.compile(r"第?([一二三四五六七八九十百0-9]+)章")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$")
IMAGE_PLACEHOLDER_RE = re.compile(r"^\[.*?(截图|图片|图|image|figure).*?\]$", re.IGNORECASE)

PLACEHOLDERS = {
    "title": ["论文题目", "[填写论文题目]", "XXX"],
    "author": ["作者姓名", "[填写姓名]"],
    "student_id": ["学号", "[填写学号]"],
    "major": ["专业", "[填写专业]"],
    "advisor": ["指导教师", "[填写导师]"],
    "abstract_cn": ["[填写摘要]", "摘要内容"],
    "keywords_cn": ["[填写关键词]", "关键词内容"],
    "abstract_en": ["[Fill Abstract]", "Abstract content"],
    "keywords_en": ["[Fill Keywords]", "Keywords content"],
}

FIELD_PATHS = {
    "title": [("paper", "title"), ("title",), ("论文题目",)],
    "author": [("paper", "author"), ("author",), ("student", "name"), ("姓名",)],
    "student_id": [("paper", "student_id"), ("student_id",), ("student", "id"), ("学号",)],
    "major": [("paper", "major"), ("major",), ("student", "major"), ("专业",)],
    "advisor": [("paper", "advisor"), ("advisor",), ("teacher",), ("指导教师",)],
    "abstract_cn": [("abstract", "cn"), ("abstract_cn",), ("摘要",)],
    "keywords_cn": [("abstract", "keywords_cn"), ("keywords_cn",), ("关键词",)],
    "abstract_en": [("abstract", "en"), ("abstract_en",)],
    "keywords_en": [("abstract", "keywords_en"), ("keywords_en",)],
}


def iter_paragraphs(document: Document) -> Iterable[Paragraph]:
    for paragraph in document.paragraphs:
        yield paragraph
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    yield paragraph


def paragraph_parent(paragraph: Paragraph):
    return paragraph._parent


def find_unique_paragraph(document: Document, anchor: str) -> Paragraph:
    matches = [paragraph for paragraph in iter_paragraphs(document) if anchor in paragraph.text]
    if len(matches) != 1:
        raise ValueError(f"Anchor must match exactly one paragraph: {anchor!r}; found {len(matches)}")
    return matches[0]


def replace_paragraph_text(paragraph: Paragraph, text: str) -> None:
    if not paragraph.runs:
        paragraph.add_run(text)
        return
    paragraph.runs[0].text = text
    for run in paragraph.runs[1:]:
        run.text = ""


def apply_replace(document: Document, anchor: str, text: str) -> dict[str, Any]:
    paragraph = find_unique_paragraph(document, anchor)
    replace_paragraph_text(paragraph, text)
    return {"operation": "replace", "anchor": anchor, "matches": 1}


def _clear_numbering(paragraph: Paragraph) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = p_pr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr")
    if num_pr is not None:
        p_pr.remove(num_pr)


def clone_paragraph_after(paragraph: Paragraph, text: str) -> Paragraph:
    new_p = deepcopy(paragraph._p)
    paragraph._p.addnext(new_p)
    new_paragraph = Paragraph(new_p, paragraph_parent(paragraph))
    replace_paragraph_text(new_paragraph, text)
    _clear_numbering(new_paragraph)
    return new_paragraph


def clone_source_paragraph_after(anchor: Paragraph, source: Paragraph, text: str) -> Paragraph:
    new_p = deepcopy(source._p)
    anchor._p.addnext(new_p)
    new_paragraph = Paragraph(new_p, paragraph_parent(anchor))
    replace_paragraph_text(new_paragraph, text)
    _clear_numbering(new_paragraph)
    return new_paragraph


def apply_insert_after(document: Document, anchor: str, text: str) -> dict[str, Any]:
    paragraph = find_unique_paragraph(document, anchor)
    clone_paragraph_after(paragraph, text)
    return {"operation": "insert_after", "anchor": anchor, "matches": 1}


def apply_delete(document: Document, anchor: str) -> dict[str, Any]:
    paragraph = find_unique_paragraph(document, anchor)
    paragraph._element.getparent().remove(paragraph._element)
    return {"operation": "delete", "anchor": anchor, "matches": 1}


def chapter_key(text: str) -> str | None:
    match = CHAPTER_KEY_RE.search(text)
    return match.group(1) if match else None


def split_markdown_chapters(path: Path) -> list[dict[str, Any]]:
    chapters: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = CHAPTER_RE.match(line.strip())
        if match:
            if current:
                chapters.append(current)
            heading = match.group(1).strip()
            current = {"heading": heading, "key": chapter_key(heading), "lines": []}
            continue
        if current is not None:
            current["lines"].append(line)
    if current:
        chapters.append(current)
    return chapters


def template_chapter_paragraphs(document: Document) -> list[dict[str, Any]]:
    chapters: list[dict[str, Any]] = []
    for index, paragraph in enumerate(iter_paragraphs(document)):
        text = paragraph.text.strip()
        if CHAPTER_KEY_RE.match(text):
            chapters.append({"index": index, "paragraph": paragraph, "text": text, "key": chapter_key(text)})
    return chapters


def match_chapters(
    template_chapters: list[dict[str, Any]],
    markdown_chapters: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any], str]]:
    matches: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    used_markdown: set[int] = set()
    markdown_by_key = {chapter["key"]: index for index, chapter in enumerate(markdown_chapters) if chapter.get("key")}
    for template in template_chapters:
        md_index = markdown_by_key.get(template.get("key"))
        if md_index is not None and md_index not in used_markdown:
            matches.append((template, markdown_chapters[md_index], "chapter_number"))
            used_markdown.add(md_index)

    remaining_templates = [
        template for template in template_chapters if all(template is not matched[0] for matched in matches)
    ]
    remaining_markdown = [chapter for index, chapter in enumerate(markdown_chapters) if index not in used_markdown]
    for template, chapter in zip(remaining_templates, remaining_markdown):
        matches.append((template, chapter, "appearance_order"))
    return matches


def value_at_path(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def normalize_field_value(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, list):
        return "；".join(str(item) for item in value if item not in (None, ""))
    return str(value)


def load_spec_fields(path: Path) -> dict[str, str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    fields: dict[str, str] = {}
    for field, paths in FIELD_PATHS.items():
        for candidate_path in paths:
            value = normalize_field_value(value_at_path(data, candidate_path))
            if value:
                fields[field] = value
                break
    return fields


def replace_placeholder(document: Document, placeholder: str, text: str) -> str:
    matches = [paragraph for paragraph in iter_paragraphs(document) if placeholder in paragraph.text]
    if len(matches) == 0:
        return "unmatched"
    if len(matches) > 1:
        return "ambiguous"
    replace_paragraph_text(matches[0], matches[0].text.replace(placeholder, text))
    return "replaced"


def apply_metadata_fill(document: Document, spec_path: Path) -> dict[str, Any]:
    fields = load_spec_fields(spec_path)
    report = {"replaced": [], "unmatched": [], "ambiguous": []}
    for field, placeholders in PLACEHOLDERS.items():
        value = fields.get(field)
        if not value:
            report["unmatched"].append({"field": field, "reason": "missing_spec_value"})
            continue
        field_replaced = False
        field_ambiguous = False
        for placeholder in placeholders:
            status = replace_placeholder(document, placeholder, value)
            if status == "replaced":
                report["replaced"].append({"field": field, "placeholder": placeholder})
                field_replaced = True
                break
            if status == "ambiguous":
                report["ambiguous"].append({"field": field, "placeholder": placeholder})
                field_ambiguous = True
                break
        if not field_replaced and not field_ambiguous:
            report["unmatched"].append({"field": field, "reason": "placeholder_not_found"})
    return report


def markdown_body_lines(lines: list[str]) -> tuple[list[str], list[str]]:
    body: list[str] = []
    skipped: list[str] = []
    in_code = False
    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            skipped.append("fenced_code_block")
            continue
        if in_code:
            continue
        if not stripped:
            continue
        if IMAGE_PLACEHOLDER_RE.match(stripped) or stripped.startswith("!["):
            skipped.append(stripped)
            continue
        heading = HEADING_RE.match(stripped)
        if heading:
            body.append(heading.group(1).strip())
        else:
            body.append(stripped)
    return body, skipped


def find_body_clone_source(document: Document, heading: Paragraph) -> Paragraph:
    paragraphs = list(iter_paragraphs(document))
    try:
        heading_index = paragraphs.index(heading)
    except ValueError:
        heading_index = -1
    for paragraph in paragraphs[heading_index + 1 :]:
        if paragraph.text.strip() and not CHAPTER_KEY_RE.match(paragraph.text.strip()):
            return paragraph
    for paragraph in paragraphs:
        if paragraph.text.strip() and not CHAPTER_KEY_RE.match(paragraph.text.strip()):
            return paragraph
    return heading


def insert_chapter_body(document: Document, heading: Paragraph, lines: list[str]) -> list[str]:
    source = find_body_clone_source(document, heading)
    anchor = heading
    inserted: list[str] = []
    for line in lines:
        anchor = clone_source_paragraph_after(anchor, source, line if line else "")
        inserted.append(line)
    return inserted


def apply_template_fill(document: Document, thesis_md: Path, spec: Path) -> dict[str, Any]:
    metadata = apply_metadata_fill(document, spec)
    template_chapters = template_chapter_paragraphs(document)
    markdown_chapters = split_markdown_chapters(thesis_md)
    matches = match_chapters(template_chapters, markdown_chapters)
    skipped_assets: list[str] = []
    chapter_report: list[dict[str, Any]] = []

    for template, chapter, method in matches:
        body, skipped = markdown_body_lines(chapter["lines"])
        skipped_assets.extend(skipped)
        insert_chapter_body(document, template["paragraph"], body)
        chapter_report.append(
            {
                "template": template["text"],
                "markdown": chapter["heading"],
                "method": method,
                "inserted_paragraphs": len(body),
            }
        )

    matched_template_ids = {id(template) for template, _, _ in matches}
    matched_markdown_ids = {id(chapter) for _, chapter, _ in matches}
    return {
        "metadata": metadata,
        "chapters": chapter_report,
        "unmatched_template_chapters": [
            chapter["text"] for chapter in template_chapters if id(chapter) not in matched_template_ids
        ],
        "unmatched_markdown_chapters": [
            chapter["heading"] for chapter in markdown_chapters if id(chapter) not in matched_markdown_ids
        ],
        "skipped_markdown_assets": skipped_assets,
    }


def report_path_for(output: Path, spec_fields: dict[str, str] | None = None) -> Path:
    title = (spec_fields or {}).get("title") or output.stem
    return output.with_name(f"{title}-template-fill-report.md")


def write_template_fill_report(
    template: Path,
    output: Path,
    spec: Path,
    fill_report: dict[str, Any],
) -> Path:
    spec_fields = load_spec_fields(spec) if spec.exists() else {}
    report_path = report_path_for(output, spec_fields)
    lines = [
        "# Template Fill Report",
        "",
        f"- copied template path: `{template}`",
        f"- output path: `{output}`",
        "",
        "## Replaced Metadata Fields",
    ]
    for item in fill_report["metadata"]["replaced"]:
        lines.append(f"- {item['field']} via `{item['placeholder']}`")
    lines.extend(["", "## Unmatched Metadata Fields"])
    for item in fill_report["metadata"]["unmatched"]:
        lines.append(f"- {item['field']}: {item['reason']}")
    lines.extend(["", "## Ambiguous Metadata Fields"])
    for item in fill_report["metadata"]["ambiguous"]:
        lines.append(f"- {item['field']} via `{item['placeholder']}`")
    lines.extend(["", "## Chapter Insertion Matches"])
    for item in fill_report["chapters"]:
        lines.append(
            f"- {item['template']} <= {item['markdown']} "
            f"({item['method']}, inserted={item['inserted_paragraphs']})"
        )
    lines.extend(["", "## Skipped Markdown Assets Or Code Blocks"])
    for item in fill_report["skipped_markdown_assets"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Manual Checks",
            "- update TOC in Word",
            "- verify cover fields",
            "- verify figures/tables",
            "- verify page layout",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def apply_template_copy_fill(template: Path, thesis_md: Path, spec: Path, output: Path) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, output)
    document = Document(output)
    fill_report = apply_template_fill(document, thesis_md, spec)
    document.save(output)
    report_path = write_template_fill_report(template, output, spec, fill_report)
    return {"output": str(output), "report": str(report_path), **fill_report}


def parse_operation_args(tokens: list[str]) -> list[tuple[str, str, str | None]]:
    operations: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--replace":
            operations.append(("replace", tokens[index + 1], tokens[index + 2]))
            index += 3
        elif token == "--insert-after":
            operations.append(("insert_after", tokens[index + 1], tokens[index + 2]))
            index += 3
        elif token == "--delete":
            operations.append(("delete", tokens[index + 1], None))
            index += 2
        else:
            raise ValueError(f"Unknown operation argument: {token}")
    return operations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply text-only edits to DOCX files.")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--from-template", type=Path, default=None)
    parser.add_argument("--thesis-md", type=Path, default=None)
    parser.add_argument("--spec", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--in-place", action="store_true")
    args, operations = parser.parse_known_args()
    args.operations = parse_operation_args(operations)
    return args


def run_text_edits(args: argparse.Namespace) -> dict[str, Any]:
    if not args.paths:
        raise ValueError("input DOCX is required unless --from-template is supplied")
    input_path = args.paths[0]
    if args.in_place:
        output_path = input_path
    elif len(args.paths) >= 2:
        output_path = args.paths[1]
    else:
        raise ValueError("output DOCX is required unless --in-place is supplied")

    document = Document(input_path)
    reports = []
    for operation, anchor, text in args.operations:
        if operation == "replace":
            reports.append(apply_replace(document, anchor, text or ""))
        elif operation == "insert_after":
            reports.append(apply_insert_after(document, anchor, text or ""))
        elif operation == "delete":
            reports.append(apply_delete(document, anchor))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)
    return {"input": str(input_path), "output": str(output_path), "operations": reports}


def run_template_fill(args: argparse.Namespace) -> dict[str, Any]:
    missing = [
        name
        for name, value in {
            "--from-template": args.from_template,
            "--thesis-md": args.thesis_md,
            "--spec": args.spec,
            "--out": args.out,
        }.items()
        if value is None
    ]
    if missing:
        raise ValueError(f"Missing required template-fill arguments: {', '.join(missing)}")
    return apply_template_copy_fill(args.from_template, args.thesis_md, args.spec, args.out)


def main() -> int:
    args = parse_args()
    report = run_template_fill(args) if args.from_template else run_text_edits(args)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
