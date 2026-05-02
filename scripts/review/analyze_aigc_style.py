#!/usr/bin/env python3
"""Generate a thesis prose style-risk report.

This helper flags formulaic academic prose patterns. It is not an AI detector
and does not predict institutional AIGC scores.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


PATTERNS = [
    ("theory_start", r"^(依据|基于|根据|按照|遵循).{0,20}(理论|框架|原则|观点)"),
    ("summary_tail", r"(由此可见|综上所述|不难发现|可以看出|因此可以得出结论|这提示我们)"),
    ("case_tail", r"(此案例|该案例|这一案例).{0,12}(印证|揭示|表明|体现|挑战)"),
    ("rigid_sequence", r"(首先|其次|再次|最后|第一|第二|第三)"),
    ("passive_shell", r"(该处理|该设计|该方法|该决策|这一做法|上述选择).{0,16}(体现|基于|反映|展现|印证)"),
    ("core_problem_shell", r"(核心问题是|核心问题在于|核心挑战在于|主要矛盾体现在|关键问题是如何)"),
    ("vague_attribution", r"(专家认为|研究表明|业内普遍认为|有观点认为|一些学者指出)"),
    ("filler_phrase", r"(值得注意的是|不难发现|需要指出的是|总体而言|从某种程度上)"),
    ("generic_positive", r"(具有重要意义|意义深远|意义重大|前景广阔|提供了新思路|开辟了新方向|不可或缺)"),
    ("copula_avoidance", r"(作为.{0,12}重要载体|扮演着.{0,12}角色|充当着.{0,12}功能|起到了.{0,12}作用)"),
]

CLICHE_TERMS = [
    "深刻揭示",
    "深入探讨",
    "系统梳理",
    "综合运用",
    "理论支撑",
    "有效解决",
    "充分说明",
    "进一步",
    "不可或缺",
    "重要意义",
]

HARD_FAILURE_PATTERNS = {
    "vague_attribution": "vague attribution needs a verified source or removal",
    "generic_positive": "generic positive conclusion needs concrete academic claim",
}


@dataclass
class ParagraphFinding:
    paragraph: int
    score: int
    risk: str
    patterns: list[str]
    cliche_terms: list[str]
    repeated_start: bool
    text_preview: str


def read_text(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def strip_markup(text: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>", " ", text)
    text = re.sub(r"(?is)<style.*?</style>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    text = strip_markup(text)
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    if len(blocks) <= 1:
        blocks = [block.strip() for block in re.split(r"(?<=[。！？!?])\s*", text) if len(block.strip()) >= 30]
    return blocks


def sentence_start(text: str) -> str:
    clean = re.sub(r"^[\s#>*\-0-9.、（）()]+", "", text.strip())
    match = re.match(r"[\u4e00-\u9fffA-Za-z]{1,6}", clean)
    return match.group(0) if match else ""


def classify(score: int) -> str:
    if score >= 5:
        return "high"
    if score >= 3:
        return "medium"
    if score >= 1:
        return "low"
    return "clear"


def analyze_paragraphs(paragraphs: list[str]) -> list[ParagraphFinding]:
    starts = [sentence_start(paragraph) for paragraph in paragraphs]
    findings: list[ParagraphFinding] = []

    for idx, paragraph in enumerate(paragraphs, 1):
        hits: list[str] = []
        for name, pattern in PATTERNS:
            if re.search(pattern, paragraph):
                hits.append(name)

        cliches = [term for term in CLICHE_TERMS if term in paragraph]
        score = len(hits) + max(0, len(cliches) - 1)

        repeated_start = False
        if idx >= 3 and starts[idx - 1] and starts[idx - 1] == starts[idx - 2] == starts[idx - 3]:
            repeated_start = True
            score += 1

        bold_count = paragraph.count("**") // 2 + len(re.findall(r"<b>|<strong>", paragraph, re.I))
        if bold_count > 2:
            hits.append("excessive_bold")
            score += 1

        findings.append(
            ParagraphFinding(
                paragraph=idx,
                score=score,
                risk=classify(score),
                patterns=hits,
                cliche_terms=cliches,
                repeated_start=repeated_start,
                text_preview=paragraph[:120].replace("\n", " "),
            )
        )
    return findings


def summarize(findings: list[ParagraphFinding]) -> dict[str, object]:
    counts = {"clear": 0, "low": 0, "medium": 0, "high": 0}
    pattern_counts: dict[str, int] = {}
    hard_failures: list[dict[str, object]] = []
    for finding in findings:
        counts[finding.risk] += 1
        for pattern in finding.patterns:
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            if pattern in HARD_FAILURE_PATTERNS:
                hard_failures.append(
                    {
                        "paragraph": finding.paragraph,
                        "pattern": pattern,
                        "message": HARD_FAILURE_PATTERNS[pattern],
                    }
                )

    if counts["high"]:
        overall = "high"
    elif counts["medium"]:
        overall = "medium"
    elif counts["low"]:
        overall = "low"
    else:
        overall = "clear"

    return {
        "overall_risk": overall,
        "paragraph_count": len(findings),
        "risk_counts": counts,
        "pattern_counts": dict(sorted(pattern_counts.items())),
        "hard_failures": hard_failures,
    }


def write_markdown(payload: dict[str, object], path: Path) -> None:
    summary = payload["summary"]
    findings = payload["findings"]
    assert isinstance(summary, dict)
    assert isinstance(findings, list)

    lines = [
        "# AIGC Style Governance Report",
        "",
        "This is a style-risk report, not an AI-detector score.",
        "",
        f"- Overall risk: `{summary['overall_risk']}`",
        f"- Paragraphs: `{summary['paragraph_count']}`",
        f"- Risk counts: `{summary['risk_counts']}`",
        "",
        "## Pattern Counts",
        "",
    ]
    pattern_counts = summary.get("pattern_counts", {})
    if pattern_counts:
        for name, count in pattern_counts.items():
            lines.append(f"- `{name}`: {count}")
    else:
        lines.append("- No major formulaic patterns detected.")

    hard_failures = summary.get("hard_failures", [])
    lines.extend(["", "## Hard Failures", ""])
    if hard_failures:
        for item in hard_failures:
            lines.append(f"- Paragraph {item['paragraph']}: `{item['pattern']}` - {item['message']}")
    else:
        lines.append("- None.")

    lines.extend(["", "## Paragraph Findings", ""])
    for item in findings:
        if item["risk"] == "clear":
            continue
        lines.append(f"### Paragraph {item['paragraph']} - {item['risk']} risk")
        lines.append(f"- Score: `{item['score']}`")
        lines.append(f"- Patterns: {', '.join(item['patterns']) if item['patterns'] else 'none'}")
        lines.append(f"- Cliche terms: {', '.join(item['cliche_terms']) if item['cliche_terms'] else 'none'}")
        lines.append(f"- Preview: {item['text_preview']}")
        lines.append("")

    lines.extend(
        [
            "## Suggested Revision Order",
            "",
            "1. Fix vague attribution with verified sources or remove it.",
            "2. Replace generic conclusions with concrete claims, limits, or next-step questions.",
            "3. Break rigid enumeration and repeated paragraph rhythm.",
            "4. Remove filler phrases and excessive academic cliches.",
            "5. Preserve facts and mark unsupported claims as `needs_source`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze thesis prose for formulaic AIGC-style risks.")
    parser.add_argument("input", nargs="?", help="Draft text/markdown/html file. Reads stdin when omitted.")
    parser.add_argument("--out", default="paper-context/aigc/aigc-style-report.md", help="Markdown report path.")
    parser.add_argument("--json-out", default="paper-context/aigc/aigc-style-report.json", help="JSON report path.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve() if args.input else None
    text = read_text(input_path)
    paragraphs = split_paragraphs(text)
    findings = analyze_paragraphs(paragraphs)
    payload = {
        "schema_version": "1.0",
        "source": str(input_path) if input_path else "stdin",
        "summary": summarize(findings),
        "findings": [asdict(item) for item in findings],
    }

    out = Path(args.out).resolve()
    json_out = Path(args.json_out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(payload, out)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {out}")
    print(f"Wrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
