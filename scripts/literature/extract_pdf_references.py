#!/usr/bin/env python3
"""Extract likely reference sections from PDF files.

This is a lightweight helper. It produces candidate evidence for an AI or human
reviewer; it does not guarantee citation-quality bibliographic metadata.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


REFERENCE_HEADINGS = [
    "references",
    "bibliography",
    "works cited",
    "参考文献",
    "参考资料",
]


@dataclass
class PdfReferenceExtraction:
    pdf: str
    title_guess: str
    extraction_method: str
    reference_section_found: bool
    reference_count_guess: int
    references: list[str]
    needs_check: bool
    notes: str


def iter_pdfs(path: Path) -> Iterable[Path]:
    if path.is_file() and path.suffix.lower() == ".pdf":
        yield path
        return
    for pdf in sorted(path.rglob("*.pdf")):
        if pdf.is_file():
            yield pdf


def extract_text(pdf: Path) -> tuple[str, str]:
    errors: list[str] = []

    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(pdf))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text, "pypdf"
    except Exception as exc:  # pragma: no cover - environment dependent
        errors.append(f"pypdf: {exc}")

    try:
        import PyPDF2  # type: ignore

        reader = PyPDF2.PdfReader(str(pdf))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text, "PyPDF2"
    except Exception as exc:  # pragma: no cover - environment dependent
        errors.append(f"PyPDF2: {exc}")

    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(pdf)) as doc:
            text = "\n".join(page.extract_text() or "" for page in doc.pages)
        if text.strip():
            return text, "pdfplumber"
    except Exception as exc:  # pragma: no cover - environment dependent
        errors.append(f"pdfplumber: {exc}")

    raise RuntimeError(
        "Could not extract text. Install pypdf, PyPDF2, or pdfplumber. "
        + " | ".join(errors)
    )


def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"-\n(?=[a-zA-Z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def title_guess(text: str, pdf: Path) -> str:
    for line in text.splitlines()[:30]:
        clean = line.strip()
        if 12 <= len(clean) <= 180 and not re.match(r"^\d+$", clean):
            if clean.lower() not in REFERENCE_HEADINGS:
                return clean
    return pdf.stem


def reference_section(text: str) -> tuple[bool, str]:
    lower = text.lower()
    candidates: list[int] = []
    for heading in REFERENCE_HEADINGS:
        pattern = re.compile(rf"(^|\n)\s*{re.escape(heading)}\s*(\n|$)", re.IGNORECASE)
        matches = list(pattern.finditer(text))
        if matches:
            candidates.extend(match.start() for match in matches)

    if not candidates:
        return False, ""

    start = max(candidates)
    section = text[start:]
    cut = re.search(
        r"\n\s*(appendix|acknowledg(e)?ments?|附录|致谢)\s*\n",
        section,
        re.IGNORECASE,
    )
    if cut:
        section = section[: cut.start()]
    return True, section


def split_references(section: str) -> list[str]:
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    if lines and lines[0].lower() in REFERENCE_HEADINGS:
        lines = lines[1:]

    joined = "\n".join(lines)

    # Common forms: [1] ..., 1. ..., or Chinese full-width variants.
    parts = re.split(r"\n(?=(?:\[\d+\]|\d{1,3}[.．、]\s))", joined)
    refs = [clean_reference(part) for part in parts if clean_reference(part)]

    if len(refs) <= 1:
        refs = []
        buffer: list[str] = []
        for line in lines:
            starts_new = bool(re.match(r"^(?:\[\d+\]|\d{1,3}[.．、]\s)", line))
            if starts_new and buffer:
                refs.append(clean_reference(" ".join(buffer)))
                buffer = [line]
            else:
                buffer.append(line)
        if buffer:
            refs.append(clean_reference(" ".join(buffer)))

    return [ref for ref in refs if len(ref) >= 20]


def clean_reference(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(references|bibliography|works cited|参考文献)\s*", "", text, flags=re.I)
    return text.strip()


def extract_one(pdf: Path) -> PdfReferenceExtraction:
    text, method = extract_text(pdf)
    text = normalize_text(text)
    found, section = reference_section(text)
    refs = split_references(section) if found else []
    return PdfReferenceExtraction(
        pdf=str(pdf),
        title_guess=title_guess(text, pdf),
        extraction_method=method,
        reference_section_found=found,
        reference_count_guess=len(refs),
        references=refs,
        needs_check=(not found or not refs),
        notes="" if found and refs else "Reference section not found or could not be split reliably.",
    )


def write_markdown(results: list[PdfReferenceExtraction], path: Path) -> None:
    lines = ["# PDF Reference Extraction", ""]
    for item in results:
        lines.extend(
            [
                f"## {item.title_guess}",
                "",
                f"- PDF: `{item.pdf}`",
                f"- Method: `{item.extraction_method}`",
                f"- Reference section found: `{item.reference_section_found}`",
                f"- Reference count guess: `{item.reference_count_guess}`",
                f"- Needs check: `{item.needs_check}`",
                "",
            ]
        )
        for idx, ref in enumerate(item.references, 1):
            lines.append(f"{idx}. {ref}")
        if not item.references:
            lines.append("- No reliable references extracted.")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract candidate reference sections from PDFs.")
    parser.add_argument("input", help="PDF file or directory containing PDF files.")
    parser.add_argument("--out", default="paper-context/literature", help="Output directory.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[PdfReferenceExtraction] = []
    errors: list[dict[str, str]] = []
    for pdf in iter_pdfs(input_path):
        try:
            results.append(extract_one(pdf))
        except Exception as exc:
            errors.append({"pdf": str(pdf), "error": str(exc)})

    payload = {
        "schema_version": "1.0",
        "source": str(input_path),
        "results": [asdict(item) for item in results],
        "errors": errors,
    }
    json_path = out_dir / "reference-extraction.json"
    md_path = out_dir / "reference-extraction.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(results, md_path)

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if errors:
        print(f"Completed with {len(errors)} extraction error(s).")
    return 0 if results else 2


if __name__ == "__main__":
    raise SystemExit(main())
