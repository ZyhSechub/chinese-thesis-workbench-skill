from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


REF_RE = re.compile(r"^\[(\d+)\]\s*(.+)$")


def classify_language(text: str) -> str:
    return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"


def extract_year(text: str) -> int | None:
    years = re.findall(r"\b(20\d{2})\b", text)
    return int(years[0]) if years else None


def parse_references(path: Path) -> list[dict]:
    refs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        m = REF_RE.match(line)
        if not m:
            continue
        body = m.group(2).strip()
        refs.append(
            {
                "raw": line,
                "index": int(m.group(1)),
                "language": classify_language(body),
                "year": extract_year(body),
                "has_doi": "doi" in body.lower(),
            }
        )
    return refs


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python build_reference_pool.py <reference-markdown-file>")
        return 1

    path = Path(sys.argv[1])
    refs = parse_references(path)
    lang_counts = Counter(ref["language"] for ref in refs)
    bad_years = [ref for ref in refs if ref["year"] is None or ref["year"] < 2020]
    print(f"TOTAL\t{len(refs)}")
    print(f"ZH\t{lang_counts.get('zh', 0)}")
    print(f"EN\t{lang_counts.get('en', 0)}")
    print(f"BAD_YEAR\t{len(bad_years)}")
    for ref in bad_years:
        print(f"BAD\t{ref['raw']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
