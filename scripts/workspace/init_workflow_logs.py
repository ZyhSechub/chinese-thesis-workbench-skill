#!/usr/bin/env python3
"""Create markdown workflow logs for a thesis workspace."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


WORKFLOW_FILES: dict[str, str] = {
    "workflow-status.md": """# Thesis Workflow Status

Generated: {today}

## Current State

```yaml
phase: intake_only
status: in_progress
current_owner: AI + user
next_action:
  - Fill material inventory.
  - Fill `standard-profile.yaml`, `thesis-ai-spec.yaml`, and evidence inputs.
blocked_reason: []
missing_materials: []
can_continue_with_limitations: true
```

## Stage Tracker

| Stage | Status | Output | Notes |
| --- | --- | --- | --- |
| intake_materials | in_progress | material inventory | Upload school template, task book, draft, code, PDFs, screenshots |
| init_workspace | done | `thesis-ai-standard/`, `paper-context/workflow/` | Created by this script |
| resolve_standards | pending | `standard-profile.yaml` | School/advisor rules first |
| analyze_sample_and_template | pending | sample/template analysis | Must precede thesis spec |
| build_evidence | pending | `paper-context/evidence/` | Source code, tests, screenshots, data |
| stop_and_report | pending | blocker report | Global mechanism |
| build_thesis_spec | pending | `thesis-ai-spec.yaml` | Facts only from evidence |
| build_figure_registry | pending | `figure-registry.yaml` | Every item needs source and first mention |
| confirm_outline | pending | confirmed outline | Confirm chapters, word count, style |
| draft_chapters | pending | chapter drafts | Evidence first, prose second |
| produce_assets | pending | figures/screenshots/tables | Source and image paths tracked |
| produce_docx | pending | main DOCX + appendix DOCX | Title-based filenames |
| quality_gates | pending | review report | Standards, evidence, references, DOCX |
| delivery_report | pending | delivery report | Include verification and limitations |

## Latest Decision

- None yet.
""",
    "step-plan.md": """# Thesis Step Plan

## How To Use

Keep this file as the task board for the thesis. Move each item through:
`pending -> in_progress -> blocked -> done`.

## Steps

| ID | Step | Status | Depends On | Deliverable |
| --- | --- | --- | --- | --- |
| S1 | Collect school template, task book, advisor notes | pending | none | material inventory |
| S2 | Fill standards profile | pending | S1 | `standard-profile.yaml` |
| S3 | Scan program/source evidence | pending | source project | `paper-context/evidence/` |
| S4 | Extract PDF references | pending | PDF folder | `paper-context/literature/reference-extraction.md` |
| S5 | Build citation cross-references | pending | S4 + topic outline | `citation-crossrefs.md` |
| S6 | Fill thesis facts | pending | S2-S5 | `thesis-ai-spec.yaml` |
| S7 | Plan figures/tables/equations | pending | S6 | `figure-registry.yaml` |
| S8 | Draft chapters | pending | S6-S7 | chapter drafts |
| S9 | Extract Word comments | pending | `.docx` draft | `word-comment-todos.md` |
| S10 | Revise by comments | pending | S9 | revised `.docx` + `docx-revision-log.md` |
| S11 | Run AIGC style report | pending | chapter drafts | `aigc-style-report.md` |
| S12 | Final quality gate | pending | S8-S11 | final review report |
""",
    "progress-log.md": """# Thesis Progress Log

Use one entry per work session.

## Entries

### {today}

- Action: Initialized thesis workflow logs.
- Inputs used: none
- Outputs created: workflow markdown files
- Decisions: none
- Blockers: fill real project and school materials
- Next action: complete material inventory and standards profile
""",
    "material-inventory.md": """# Material Inventory

## School And Advisor Materials

| Material | Path | Status | Notes |
| --- | --- | --- | --- |
| School template |  | missing |  |
| Task book |  | missing |  |
| Proposal/opening report |  | missing |  |
| Advisor comments |  | missing |  |

## Project / Research Evidence

| Material | Path | Status | Notes |
| --- | --- | --- | --- |
| Source code |  | missing |  |
| Database schema |  | missing |  |
| API docs |  | missing |  |
| Screenshots |  | missing |  |
| Test reports |  | missing |  |
| Experiment/data files |  | missing |  |

## Literature

| Material | Path | Status | Notes |
| --- | --- | --- | --- |
| PDF papers | `papers/` | missing |  |
| Existing reference list |  | missing |  |
""",
    "evidence-gaps.md": """# Evidence Gaps

Record every claim that cannot yet be supported.

| ID | Claim or section | Missing evidence | Severity | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| GAP-001 |  |  | major | user/AI | open |
""",
    "chapter-progress.md": """# Chapter Progress

| Chapter | Purpose | Evidence Ready | Draft Status | Review Status | Notes |
| --- | --- | --- | --- | --- | --- |
| Chapter 1 Introduction | background, value, scope | no | not_started | not_started | write after core facts are known |
| Chapter 2 Theory/Technology | method and stack | no | not_started | not_started |  |
| Chapter 3 Requirements/Design | requirements or research design | no | not_started | not_started |  |
| Chapter 4 Overall Design/Process | architecture, process, data | no | not_started | not_started |  |
| Chapter 5 Implementation/Results | implementation or analysis | no | not_started | not_started |  |
| Chapter 6 Testing/Discussion | tests, validation, discussion | no | not_started | not_started |  |
| Conclusion | summary and limits | no | not_started | not_started | write last |
""",
    "revision-log.md": """# Revision Log

Use this file for all thesis changes, including Word comments, AIGC style edits, figure/table changes, and standard fixes.

| ID | Date | Source | Location | Change | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| REV-001 | {today} | initialization | workspace | Created workflow logs | script output | done |
""",
}


def write_workflow_logs(target: Path, overwrite: bool = False) -> list[Path]:
    workflow_dir = target / "paper-context" / "workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    written: list[Path] = []
    for name, template in WORKFLOW_FILES.items():
        path = workflow_dir / name
        if path.exists() and not overwrite:
            continue
        path.write_text(template.format(today=today), encoding="utf-8")
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize thesis workflow markdown logs.")
    parser.add_argument("target", nargs="?", default=".", help="Project directory.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing workflow files.")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    written = write_workflow_logs(target, overwrite=args.overwrite)
    print(f"Workflow directory: {target / 'paper-context' / 'workflow'}")
    if written:
        for path in written:
            print(f"- wrote {path}")
    else:
        print("No files written; existing files were preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
