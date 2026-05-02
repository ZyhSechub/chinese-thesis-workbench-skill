#!/usr/bin/env python3
"""Build a citation cross-reference index from extracted PDF references."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "this",
    "that",
    "研究",
    "系统",
    "方法",
    "设计",
    "实现",
    "分析",
    "基于",
    "本文",
    "论文",
}

CJK_KEY_TERMS = {
    "总体设计",
    "详细设计",
    "需求分析",
    "系统架构",
    "总体架构",
    "功能模块",
    "业务流程",
    "数据库",
    "数据库设计",
    "数据结构",
    "接口设计",
    "系统测试",
    "测试方法",
    "测试用例",
    "实验设计",
    "实验结果",
    "数据分析",
    "问卷调查",
    "样本",
    "变量",
    "模型",
    "算法",
    "可视化",
    "前端",
    "后端",
    "管理系统",
    "小程序",
    "移动端",
    "用户",
    "权限",
    "安全",
    "性能",
    "可靠性",
}


def tokenize(text: str) -> list[str]:
    raw_words = re.findall(r"[A-Za-z][A-Za-z0-9_+-]{2,}|[\u4e00-\u9fff]{2,}", text.lower())
    words: list[str] = []
    for word in raw_words:
        if word in STOPWORDS:
            continue
        words.append(word)
        if re.fullmatch(r"[\u4e00-\u9fff]{2,}", word):
            words.extend(term for term in CJK_KEY_TERMS if term in word)
    return [word for word in words if word not in STOPWORDS]


def topic_blocks(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    blocks: list[dict[str, str]] = []
    current_title = "General"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_lines:
                blocks.append({"topic": current_title, "text": "\n".join(current_lines)})
                current_lines = []
            current_title = line.lstrip("#").strip() or "Untitled"
        else:
            current_lines.append(line)
    if current_lines:
        blocks.append({"topic": current_title, "text": "\n".join(current_lines)})
    if not blocks:
        blocks.append({"topic": "General", "text": text})
    return blocks


def load_references(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    refs: list[dict[str, str]] = []
    for result in payload.get("results", []):
        title = result.get("title_guess", "")
        pdf = result.get("pdf", "")
        for ref in result.get("references", []):
            refs.append({"source_pdf": pdf, "source_title": title, "reference": ref})
    return refs


def score(topic_text: str, reference: str) -> tuple[int, list[str]]:
    topic_counts = Counter(tokenize(topic_text))
    ref_tokens = tokenize(reference)
    overlaps = []
    total = 0
    for token in ref_tokens:
        if token in topic_counts:
            total += topic_counts[token]
            if token not in overlaps:
                overlaps.append(token)
    year_bonus = 1 if re.search(r"\b20[0-2]\d\b", reference) else 0
    return total + year_bonus, overlaps[:10]


def build_crossrefs(refs: list[dict[str, str]], topics: list[dict[str, str]]) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for topic in topics:
        ranked = []
        for ref in refs:
            value, overlaps = score(topic["text"] + " " + topic["topic"], ref["reference"])
            if value > 0:
                confidence = "strong" if value >= 4 else "needs_check"
                ranked.append(
                    {
                        "score": value,
                        "confidence": confidence,
                        "matched_terms": overlaps,
                        "reference": ref["reference"],
                        "source_pdf": ref["source_pdf"],
                        "source_title": ref["source_title"],
                    }
                )
        ranked.sort(key=lambda item: int(item["score"]), reverse=True)
        blocks.append({"topic": topic["topic"], "matches": ranked[:8]})
    return blocks


def write_crossrefs(refs: list[dict[str, str]], topics: list[dict[str, str]], out: Path) -> list[dict[str, object]]:
    crossrefs = build_crossrefs(refs, topics)
    lines = ["# Citation Cross-Reference Index", ""]
    if not refs:
        lines.append("No extracted references available. Run extract_pdf_references.py first.")
        out.write_text("\n".join(lines), encoding="utf-8")
        return crossrefs

    for topic in crossrefs:
        lines.extend([f"## {topic['topic']}", ""])
        matches = topic.get("matches", [])
        if not matches:
            lines.append("- No strong match. Needs AI/human review.")
            lines.append("")
            continue

        for match in matches:
            overlaps = match.get("matched_terms", [])
            lines.append(f"- Confidence: `{match['confidence']}`; score: `{match['score']}`")
            lines.append(f"  - Matched terms: {', '.join(overlaps) if overlaps else 'year/recentness only'}")
            lines.append(f"  - Reference: {match['reference']}")
            lines.append(f"  - Source PDF: `{match['source_pdf']}`")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return crossrefs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build citation cross-references by keyword overlap.")
    parser.add_argument("reference_json", help="reference-extraction.json from extract_pdf_references.py")
    parser.add_argument("--topics", required=True, help="Markdown file containing thesis topics or chapter outline.")
    parser.add_argument("--out", default="paper-context/literature/citation-crossrefs.md", help="Output markdown file.")
    parser.add_argument("--json-out", help="Optional structured JSON output path.")
    args = parser.parse_args()

    refs = load_references(Path(args.reference_json))
    topics = topic_blocks(Path(args.topics))
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    crossrefs = write_crossrefs(refs, topics, out)
    print(f"Wrote {out}")
    if args.json_out:
        json_out = Path(args.json_out).resolve()
        json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "1.0",
            "source": str(Path(args.reference_json).resolve()),
            "topics": str(Path(args.topics).resolve()),
            "crossrefs": crossrefs,
        }
        json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
