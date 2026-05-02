#!/usr/bin/env python3
"""Extract Word DOCX comments into thesis revision todo files."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


@dataclass
class WordComment:
    id: str
    author: str
    date: str
    initials: str
    comment_text: str
    anchor_text: str
    paragraph_preview: str
    status: str = "todo"
    suggested_action: str = "review_and_revise"
    risk: str = "needs_human_or_ai_judgment"


def read_zip_text(docx: Path, name: str) -> str | None:
    with zipfile.ZipFile(docx) as archive:
        try:
            return archive.read(name).decode("utf-8")
        except KeyError:
            return None


def text_content(element: ET.Element) -> str:
    parts = []
    for node in element.iter():
        if node.tag == f"{{{NS['w']}}}t":
            parts.append(node.text or "")
        elif node.tag == f"{{{NS['w']}}}tab":
            parts.append("\t")
        elif node.tag == f"{{{NS['w']}}}br":
            parts.append("\n")
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def attr(element: ET.Element, name: str, default: str = "") -> str:
    return element.attrib.get(f"{{{NS['w']}}}{name}", default)


def load_comments(docx: Path) -> dict[str, WordComment]:
    comments_xml = read_zip_text(docx, "word/comments.xml")
    if not comments_xml:
        return {}
    root = ET.fromstring(comments_xml)
    comments: dict[str, WordComment] = {}
    for comment in root.findall("w:comment", NS):
        comment_id = attr(comment, "id")
        comments[comment_id] = WordComment(
            id=comment_id,
            author=attr(comment, "author"),
            date=attr(comment, "date"),
            initials=attr(comment, "initials"),
            comment_text=text_content(comment),
            anchor_text="",
            paragraph_preview="",
        )
    return comments


def paragraph_comment_ids(paragraph: ET.Element) -> set[str]:
    ids: set[str] = set()
    for node in paragraph.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local in {"commentRangeStart", "commentRangeEnd", "commentReference"}:
            comment_id = attr(node, "id")
            if comment_id:
                ids.add(comment_id)
    return ids


def enrich_with_anchors(docx: Path, comments: dict[str, WordComment]) -> None:
    document_xml = read_zip_text(docx, "word/document.xml")
    if not document_xml:
        return
    root = ET.fromstring(document_xml)
    for paragraph in root.findall(".//w:p", NS):
        ids = paragraph_comment_ids(paragraph)
        if not ids:
            continue
        paragraph_text = text_content(paragraph)
        preview = paragraph_text[:240]
        for comment_id in ids:
            if comment_id in comments:
                comments[comment_id].anchor_text = paragraph_text
                comments[comment_id].paragraph_preview = preview


def extract_comments(docx: Path) -> list[WordComment]:
    comments = load_comments(docx)
    enrich_with_anchors(docx, comments)
    return [
        comments[key]
        for key in sorted(
            comments,
            key=lambda value: (0, int(value)) if value.isdigit() else (1, value),
        )
    ]


def write_markdown(comments: list[WordComment], path: Path, docx: Path) -> None:
    lines = [
        "# Word Comment Todos",
        "",
        f"- Source document: `{docx}`",
        f"- Comment count: `{len(comments)}`",
        "",
        "Use this file as the bridge between Word comments and thesis revisions.",
        "",
    ]
    if not comments:
        lines.append("No Word comments found.")
    for item in comments:
        lines.extend(
            [
                f"## COMMENT-{item.id}",
                "",
                f"- Author: {item.author or 'unknown'}",
                f"- Date: {item.date or 'unknown'}",
                f"- Status: `{item.status}`",
                f"- Suggested action: `{item.suggested_action}`",
                "",
                "### Comment",
                "",
                item.comment_text or "(empty comment)",
                "",
                "### Anchor / Paragraph Preview",
                "",
                item.paragraph_preview or "(anchor not found in document.xml)",
                "",
                "### Revision Notes",
                "",
                "- Decision: pending",
                "- Evidence needed: pending",
                "- Applied change: pending",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_revision_log(path: Path, docx: Path) -> None:
    if path.exists():
        return
    lines = [
        "# DOCX Revision Log",
        "",
        f"- Source document: `{docx}`",
        "",
        "| Comment ID | Location | Decision | Change Applied | Evidence | Status |",
        "| --- | --- | --- | --- | --- | --- |",
        "| COMMENT-001 |  | pending |  |  | open |",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract DOCX comments into thesis revision todo files.")
    parser.add_argument("docx", help="Word .docx file with comments.")
    parser.add_argument("--out", default="paper-context/word-comments", help="Output directory.")
    args = parser.parse_args()

    docx = Path(args.docx).resolve()
    if docx.suffix.lower() != ".docx":
        raise ValueError("Input must be a .docx file.")
    if not docx.exists():
        raise FileNotFoundError(docx)

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    comments = extract_comments(docx)
    payload = {
        "schema_version": "1.0",
        "source_docx": str(docx),
        "comment_count": len(comments),
        "comments": [asdict(item) for item in comments],
    }
    json_path = out / "word-comments.json"
    md_path = out / "word-comment-todos.md"
    revision_log = out / "docx-revision-log.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(comments, md_path, docx)
    write_revision_log(revision_log, docx)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {revision_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
