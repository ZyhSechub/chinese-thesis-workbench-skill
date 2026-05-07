#!/usr/bin/env python3
"""Validate a thesis-ai-standard workspace.

The check is intentionally lightweight: it verifies required files, parses
machine-readable templates when dependencies are available, and reports missing
core evidence paths without pretending to validate thesis quality.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "01-本科论文标准化最佳实践.md",
    "02-公开标准与高校规范来源.md",
    "templates/standard-profile.yaml",
    "templates/thesis-ai-spec.yaml",
    "templates/figure-registry.yaml",
    "templates/literature-review-matrix.yaml",
    "templates/citation-crossref-register.yaml",
    "templates/aigc-style-review.yaml",
    "templates/chapter-section-template.md",
    "templates/ai-prompts.md",
    "templates/ai-review-rubric.json",
]

DRAWIO_FILES = [
    "drawio/system-architecture-template.drawio",
    "drawio/backend-layered-architecture-template.drawio",
    "drawio/business-flow-template.drawio",
    "drawio/er-diagram-template.drawio",
    "drawio/algorithm-workflow-template.drawio",
    "drawio/sequence-diagram-template.drawio",
]


@dataclass
class CheckResult:
    status: str
    path: str
    message: str


def load_yaml(path: Path) -> object:
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(f"PyYAML not installed; skipped YAML parse: {exc}") from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check_required(base: Path, rel_path: str) -> CheckResult:
    path = base / rel_path
    if not path.exists():
        return CheckResult("error", rel_path, "missing required file")
    if path.is_file() and path.stat().st_size == 0:
        return CheckResult("error", rel_path, "file is empty")
    return CheckResult("ok", rel_path, "present")


def check_parse(base: Path, rel_path: str) -> CheckResult:
    path = base / rel_path
    try:
        if rel_path.endswith(".json"):
            json.loads(path.read_text(encoding="utf-8"))
        elif rel_path.endswith((".yaml", ".yml")):
            load_yaml(path)
        elif rel_path.endswith(".drawio"):
            ET.parse(path)
        else:
            return CheckResult("ok", rel_path, "no parser required")
    except RuntimeError as exc:
        return CheckResult("warn", rel_path, str(exc))
    except Exception as exc:
        return CheckResult("error", rel_path, f"parse failed: {exc}")
    return CheckResult("ok", rel_path, "parsed")


def inspect_core_fields(base: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []
    spec_path = base / "templates" / "thesis-ai-spec.yaml"
    profile_path = base / "templates" / "standard-profile.yaml"

    try:
        spec = load_yaml(spec_path)
        if isinstance(spec, dict):
            paper = spec.get("paper") or {}
            if isinstance(paper, dict):
                title = str(paper.get("title", "")).strip()
                type_profile = str(paper.get("type_profile", "")).strip()
                if not title or title == "填写论文题目":
                    checks.append(CheckResult("warn", spec_path.name, "paper.title still looks unfilled"))
                if "|" in type_profile or type_profile in {"", "other"}:
                    checks.append(CheckResult("warn", spec_path.name, "paper.type_profile needs a concrete value"))
    except Exception as exc:
        checks.append(CheckResult("warn", spec_path.name, f"core-field inspection skipped: {exc}"))

    try:
        profile = load_yaml(profile_path)
        if isinstance(profile, dict):
            versions = profile.get("standard_versions") or {}
            refs = versions.get("references") if isinstance(versions, dict) else None
            if isinstance(refs, dict):
                version = str(refs.get("version", "")).strip()
                if "填写" in version or not version:
                    checks.append(CheckResult("warn", profile_path.name, "reference standard version is not confirmed"))
    except Exception as exc:
        checks.append(CheckResult("warn", profile_path.name, f"core-field inspection skipped: {exc}"))

    return checks


def render(results: list[CheckResult]) -> str:
    lines = ["# Thesis Workspace Check", ""]
    for result in results:
        lines.append(f"- {result.status.upper()}: `{result.path}` - {result.message}")
    errors = sum(1 for item in results if item.status == "error")
    warnings = sum(1 for item in results if item.status == "warn")
    lines.extend(["", f"Summary: {errors} error(s), {warnings} warning(s)."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a thesis-ai-standard workspace.")
    parser.add_argument("workspace", nargs="?", default="thesis-ai-standard", help="Path to thesis-ai-standard.")
    parser.add_argument("--out", help="Optional markdown report path.")
    args = parser.parse_args()

    base = Path(args.workspace).resolve()
    results: list[CheckResult] = []
    if not base.exists():
        results.append(CheckResult("error", str(base), "workspace does not exist"))
    else:
        for rel_path in REQUIRED_FILES + DRAWIO_FILES:
            result = check_required(base, rel_path)
            results.append(result)
            if result.status == "ok" and rel_path.endswith((".json", ".yaml", ".yml", ".drawio")):
                results.append(check_parse(base, rel_path))
        results.extend(inspect_core_fields(base))

    report = render(results)
    if args.out:
        Path(args.out).resolve().write_text(report, encoding="utf-8")
        print(f"Wrote {Path(args.out).resolve()}")
    else:
        sys.stdout.write(report)

    return 1 if any(item.status == "error" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
