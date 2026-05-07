#!/usr/bin/env python3
"""Build workflow outputs from sample/template parser results.

This script intentionally treats DOCX/PDF parsers as input providers. It does
not parse Word or PDF files directly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


AnalysisModel = dict[str, Any]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value).replace("\n", " ").strip()


def _first_text(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return _text(value)
    return ""


def build_analysis_model(raw: dict[str, Any]) -> AnalysisModel:
    """Normalize parser/manual results into the module-six workflow schema."""
    source = _as_mapping(raw.get("source"))
    template_rules = _as_mapping(raw.get("template_rules"))
    sample_patterns = _as_mapping(raw.get("sample_patterns"))
    recommendations = _as_mapping(raw.get("recommendations"))

    return {
        "source": {
            "path": _text(source.get("path")),
            "source_type": _text(source.get("source_type") or "manual_note"),
            "parser": _text(source.get("parser") or "manual"),
            "parser_status": _text(source.get("parser_status") or "manual"),
            "limitations": [_text(item) for item in _as_list(source.get("limitations"))],
        },
        "template_rules": {
            "confirmed": [_as_mapping(item) for item in _as_list(template_rules.get("confirmed"))],
            "needs_confirmation": [
                _as_mapping(item) for item in _as_list(template_rules.get("needs_confirmation"))
            ],
        },
        "sample_patterns": {
            "outline_structure": [
                _as_mapping(item) for item in _as_list(sample_patterns.get("outline_structure"))
            ],
            "chapter_word_distribution": [
                _as_mapping(item)
                for item in _as_list(sample_patterns.get("chapter_word_distribution"))
            ],
            "figure_table_rhythm": [
                _as_mapping(item) for item in _as_list(sample_patterns.get("figure_table_rhythm"))
            ],
            "style_observations": [
                _as_mapping(item) for item in _as_list(sample_patterns.get("style_observations"))
            ],
        },
        "recommendations": {
            "outline_suggestion": [
                _as_mapping(item)
                for item in _as_list(recommendations.get("outline_suggestion"))
            ],
            "word_budget": [
                _as_mapping(item) for item in _as_list(recommendations.get("word_budget"))
            ],
            "user_decisions_needed": [
                _as_mapping(item)
                for item in _as_list(recommendations.get("user_decisions_needed"))
            ],
        },
        "confidence": _as_mapping(raw.get("confidence")),
    }


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    if rows:
        lines.extend("| " + " | ".join(_text(cell) for cell in row) + " |" for row in rows)
    else:
        lines.append("| " + " | ".join("" for _ in headers) + " |")
    return "\n".join(lines)


def render_sample_template_analysis(model: AnalysisModel) -> str:
    source = model["source"]
    limitations = "; ".join(source["limitations"])
    source_rows = [
        [
            source["path"],
            source["source_type"],
            source["parser"],
            source["parser_status"],
            limitations,
        ]
    ]

    rule_rows: list[list[str]] = []
    for item in model["template_rules"]["confirmed"]:
        rule_rows.append(
            [
                _first_text(item, "rule", "name"),
                _first_text(item, "source"),
                _first_text(item, "status") or "confirmed",
                _first_text(item, "notes"),
            ]
        )
    for item in model["template_rules"]["needs_confirmation"]:
        rule_rows.append(
            [
                _first_text(item, "rule", "name"),
                _first_text(item, "source"),
                _first_text(item, "status") or "needs_confirmation",
                _first_text(item, "notes"),
            ]
        )

    pattern_rows: list[list[str]] = []
    for group in ("outline_structure", "chapter_word_distribution", "figure_table_rhythm", "style_observations"):
        for item in model["sample_patterns"][group]:
            label = _first_text(item, "pattern", "chapter", "observation", "name")
            if item.get("words"):
                label = f"{label}: {item['words']} words"
            pattern_rows.append(
                [
                    label,
                    _first_text(item, "source"),
                    _first_text(item, "confidence") or "low",
                    _first_text(item, "notes"),
                ]
            )

    recommendation_rows: list[list[str]] = []
    for item in model["recommendations"]["outline_suggestion"]:
        recommendation_rows.append(
            [
                f"Chapter {_first_text(item, 'chapter')}: {_first_text(item, 'suggested_title', 'title')}",
                _first_text(item, "source", "based_on"),
                _first_text(item, "confidence") or "low",
                _first_text(item, "needs_confirmation") or "yes",
                _first_text(item, "notes"),
            ]
        )
    for item in model["recommendations"]["word_budget"]:
        recommendation_rows.append(
            [
                f"Chapter {_first_text(item, 'chapter')}: {_first_text(item, 'suggested_words')} words",
                _first_text(item, "source"),
                _first_text(item, "confidence") or "low",
                "yes" if _first_text(item, "status") == "provisional" else "no",
                _first_text(item, "notes"),
            ]
        )

    decision_rows = [
        [
            _first_text(item, "item", "decision"),
            _first_text(item, "reason"),
            _first_text(item, "impact"),
            "Ask user before outline confirmation",
        ]
        for item in model["recommendations"]["user_decisions_needed"]
    ]
    outline_rows = _outline_rows(model)
    budget_rows = _budget_rows(model)

    return "\n\n".join(
        [
            "# Sample Template Analysis",
            "Parser Boundary: PDF and Word parsers are input providers only. Partial parser output must stay visible and must not become confirmed school rules.",
            "## Source Summary",
            _markdown_table(["Source", "Type", "Parser / input", "Parser status", "Limitations"], source_rows),
            "## template_rules",
            _markdown_table(["Rule", "Source", "Status", "Notes"], rule_rows),
            "## sample_patterns",
            _markdown_table(["Pattern", "Source", "Confidence", "Notes"], pattern_rows),
            "## recommendations",
            _markdown_table(
                ["Recommendation", "Based on", "Confidence", "Needs user confirmation?", "Notes"],
                recommendation_rows,
            ),
            "## Unparsed Or Needs Confirmation",
            _markdown_table(["Item", "Reason", "Impact", "Next action"], decision_rows),
            "## Outline Suggestion",
            "Do not write this directly into `thesis-ai-spec.yaml` until the user confirms it.",
            _markdown_table(
                ["Chapter", "Suggested title", "Source", "Confidence", "Needs confirmation", "Notes"],
                outline_rows,
            ),
            "## Word Budget",
            "Every budget item must name its source and confidence. Sample ratios do not override school or advisor word-count requirements.",
            _markdown_table(
                ["Chapter", "Suggested words", "Source", "Basis", "Confidence", "Status", "Notes"],
                budget_rows,
            ),
            "",
        ]
    )


def _outline_rows(model: AnalysisModel) -> list[list[str]]:
    return [
        [
            _first_text(item, "chapter"),
            _first_text(item, "suggested_title", "title"),
            _first_text(item, "source", "based_on"),
            _first_text(item, "confidence") or "low",
            _first_text(item, "needs_confirmation") or "yes",
            _first_text(item, "notes"),
        ]
        for item in model["recommendations"]["outline_suggestion"]
    ]


def _budget_rows(model: AnalysisModel) -> list[list[str]]:
    return [
        [
            _first_text(item, "chapter"),
            _first_text(item, "suggested_words"),
            _first_text(item, "source"),
            _first_text(item, "basis"),
            _first_text(item, "confidence") or "low",
            _first_text(item, "status") or "provisional",
            _first_text(item, "notes"),
        ]
        for item in model["recommendations"]["word_budget"]
    ]


def write_sample_template_outputs(input_json: Path, target: Path) -> list[Path]:
    raw = json.loads(input_json.read_text(encoding="utf-8"))
    model = build_analysis_model(raw)
    workflow_dir = target / "paper-context" / "workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    outputs = [(workflow_dir / "sample-template-analysis.md", render_sample_template_analysis(model))]
    for path, content in outputs:
        path.write_text(content, encoding="utf-8")
    return [path for path, _ in outputs]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build sample/template workflow outputs from parser JSON."
    )
    parser.add_argument("input_json", help="Parser or manually normalized JSON input.")
    parser.add_argument(
        "--target",
        default=".",
        help="Thesis workspace root where paper-context/workflow will be written.",
    )
    args = parser.parse_args()

    written = write_sample_template_outputs(Path(args.input_json), Path(args.target))
    for path in written:
        print(f"- wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
