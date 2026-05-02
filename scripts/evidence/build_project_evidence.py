#!/usr/bin/env python3
"""Build first-pass evidence files from a source project for thesis drafting."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    "coverage",
    "venv",
    ".venv",
}

TECH_MARKERS = {
    "package.json": "Node.js / JavaScript / TypeScript",
    "vite.config.ts": "Vite",
    "vite.config.js": "Vite",
    "next.config.js": "Next.js",
    "pom.xml": "Maven / Java",
    "build.gradle": "Gradle / Java",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "manage.py": "Django",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "composer.json": "PHP",
    "pubspec.yaml": "Flutter / Dart",
    "app.json": "Mini program / mobile app config",
    "project.config.json": "WeChat Mini Program",
}

SOURCE_EXTS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".py",
    ".go",
    ".rs",
    ".php",
    ".vue",
    ".sql",
    ".xml",
    ".yml",
    ".yaml",
    ".json",
}

TEST_HINTS = ("test", "tests", "spec", "__tests__", "junit", "pytest", "coverage")
SCHEMA_HINTS = ("schema", "migration", "migrations", "sql", "entity", "model", "mapper")
API_HINT_EXTS = {".js", ".ts", ".java", ".py", ".go", ".php"}


@dataclass
class Evidence:
    root: str
    tech_markers: list[dict[str, str]]
    source_files: list[str]
    possible_api_files: list[str]
    possible_schema_files: list[str]
    possible_test_files: list[str]
    route_candidates: list[dict[str, str]]


def should_skip(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return True
    return any(part in IGNORE_DIRS for part in rel.parts)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and not should_skip(path, root):
            files.append(path)
    return sorted(files)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def detect_routes(path: Path, root: Path) -> list[dict[str, str]]:
    if path.suffix.lower() not in API_HINT_EXTS:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    patterns = [
        r"@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(([^)]*)\)",
        r"\b(router|app)\.(get|post|put|delete|patch)\s*\(([^)]*)\)",
        r"\b(GET|POST|PUT|DELETE|PATCH)\s+['\"]([^'\"]+)['\"]",
        r"@app\.(route|get|post|put|delete|patch)\s*\(([^)]*)\)",
    ]
    found: list[dict[str, str]] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            snippet = " ".join(match.group(0).split())
            found.append({"file": rel(path, root), "candidate": snippet[:220]})
    return found[:30]


def build_evidence(root: Path) -> Evidence:
    files = iter_files(root)
    tech_markers = []
    source_files = []
    possible_api_files = []
    possible_schema_files = []
    possible_test_files = []
    route_candidates = []

    for path in files:
        r = rel(path, root)
        lower = r.lower()
        if path.name in TECH_MARKERS:
            tech_markers.append({"file": r, "technology": TECH_MARKERS[path.name]})
        if path.suffix.lower() in SOURCE_EXTS:
            source_files.append(r)
        if path.suffix.lower() in API_HINT_EXTS and any(term in lower for term in ("controller", "route", "api", "handler", "service")):
            possible_api_files.append(r)
        if path.suffix.lower() == ".sql" or any(term in lower for term in SCHEMA_HINTS):
            possible_schema_files.append(r)
        if any(term in lower for term in TEST_HINTS):
            possible_test_files.append(r)
        route_candidates.extend(detect_routes(path, root))

    return Evidence(
        root=str(root),
        tech_markers=tech_markers,
        source_files=source_files[:500],
        possible_api_files=possible_api_files[:200],
        possible_schema_files=possible_schema_files[:200],
        possible_test_files=possible_test_files[:200],
        route_candidates=route_candidates[:300],
    )


def write_list_md(path: Path, title: str, items: list[str], empty: str) -> None:
    lines = [f"# {title}", ""]
    if items:
        lines.extend(f"- `{item}`" for item in items)
    else:
        lines.append(empty)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(evidence: Evidence, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "project-evidence.json").write_text(
        json.dumps(asdict(evidence), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    write_list_md(
        out / "code-structure.md",
        "Code Structure Evidence",
        evidence.source_files,
        "No source files detected by extension.",
    )

    tech_lines = ["# Technology Stack Evidence", ""]
    if evidence.tech_markers:
        tech_lines.extend(f"- `{item['file']}`: {item['technology']}" for item in evidence.tech_markers)
    else:
        tech_lines.append("No common technology marker files detected.")
    (out / "tech-stack.md").write_text("\n".join(tech_lines) + "\n", encoding="utf-8")

    api_lines = ["# API Evidence", ""]
    if evidence.possible_api_files:
        api_lines.append("## Possible API Files")
        api_lines.extend(f"- `{item}`" for item in evidence.possible_api_files)
        api_lines.append("")
    if evidence.route_candidates:
        api_lines.append("## Route Candidates")
        api_lines.extend(f"- `{item['file']}`: `{item['candidate']}`" for item in evidence.route_candidates)
    if len(api_lines) == 2:
        api_lines.append("No API candidates detected. Inspect the project manually.")
    (out / "api-list.md").write_text("\n".join(api_lines) + "\n", encoding="utf-8")

    write_list_md(
        out / "database-schema.md",
        "Database Schema Evidence",
        evidence.possible_schema_files,
        "No schema/entity/migration candidates detected.",
    )

    write_list_md(
        out / "test-results.md",
        "Test Evidence",
        evidence.possible_test_files,
        "No test files or reports detected.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build first-pass thesis evidence from a project folder.")
    parser.add_argument("project", nargs="?", default=".", help="Project directory to scan.")
    parser.add_argument("--out", default="paper-context/evidence", help="Output evidence directory.")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    out = Path(args.out).resolve()
    evidence = build_evidence(root)
    write_outputs(evidence, out)
    print(f"Wrote evidence files to {out}")
    print(f"Source files: {len(evidence.source_files)}")
    print(f"Tech markers: {len(evidence.tech_markers)}")
    print(f"API candidates: {len(evidence.possible_api_files)}")
    print(f"Schema candidates: {len(evidence.possible_schema_files)}")
    print(f"Test candidates: {len(evidence.possible_test_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
