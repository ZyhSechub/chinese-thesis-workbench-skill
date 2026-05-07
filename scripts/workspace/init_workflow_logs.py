#!/usr/bin/env python3
"""Create markdown workflow logs for a thesis workspace."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path


WORKFLOW_FILES: dict[str, str] = {
    "user-dashboard.md": """# User Dashboard

Generated: {today}

This file is the user-facing progress view. Keep it short, current, and decision-oriented.

## Current Progress

| Item | Value |
| --- | --- |
| Phase | intake_only |
| Status | in_progress |
| Current focus | Collect materials and confirm constraints before drafting |
| Can continue? | Yes, with limitations until school/template/evidence inputs are confirmed |

## Completed Work

| Work item | Status | Notes |
| --- | --- | --- |
| Workflow workspace initialized | done | Created workflow tracking files |

## Needs User Confirmation

| Decision | Why it matters | Options / expected input | Status |
| --- | --- | --- | --- |
| Thesis title and type | Controls outline, chapter model, and filenames | Provide title and thesis type | pending |
| School template availability | Controls formatting and standards claims | Provide template path or confirm no template | pending |
| Final DOCX requirement | Controls delivery scope | Confirm whether main DOCX and appendix DOCX are needed | pending |

## Missing Materials

| Material | Affected work | Can continue without it? | Notes |
| --- | --- | --- | --- |
| School template | Formatting, standard compliance, DOCX layout | Limited | Do not claim school formatting compliance without it |
| Task book / proposal | Topic scope, chapter emphasis, cover fields | Limited | Use project facts only until confirmed |
| Sample paper | Outline rhythm, word budget, style reference | Yes | Use conservative default rhythm if absent |
| Source evidence | Implementation chapters and factual claims | No for formal drafting | Needed before writing project-specific body text |

## Next Recommended Action

1. Fill `material-inventory.md` with available paths.
2. Confirm thesis title, type, word-count requirement, and DOCX delivery requirement.
3. Resolve school/advisor standards before formal drafting.

## Limited Continuation

- A draft outline can be proposed before all materials are complete, but it must be marked provisional.
- Formal thesis body text should wait until standards, sample/template analysis, and evidence are confirmed.
- Missing materials must stay visible here and in `evidence-gaps.md`.
""",
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

Use this file as the intake control table. Keep the user informed about what each missing material affects and whether work can continue with limitations.

Status values: `missing`, `provided`, `parsed`, `needs_confirmation`, `not_available`, `deferred`.

## Intake Priority Guide

| Priority | Meaning | How to handle |
| --- | --- | --- |
| required | Needed to make core thesis decisions or avoid false claims | Ask early; block formal drafting if absent and no limitation is confirmed |
| strongly_recommended | Improves standards, outline, evidence, or delivery quality | Ask once, explain impact, allow limited continuation if user defers |
| optional | Useful for polish, verification, or richer delivery | Track when available; do not block unless user explicitly requires it |

## School And Advisor Materials

| Material | Priority | Path / Input | Status | Missing impact | Can continue? | User next step | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Thesis title and type | required |  | missing | Cannot finalize outline, chapter model, or output filenames | no for formal drafting | Provide title and thesis type |  |
| School template | required |  | missing | Cannot claim school-format compliance or final layout correctness | limited | Provide `.docx` / `.pdf` path or confirm no template |  |
| Word-count requirement | required |  | missing | Cannot set reliable chapter budgets | limited | Provide total word count or confirm school has no clear requirement |  |
| Final DOCX requirement | required |  | missing | Cannot lock delivery scope | limited | Confirm whether main DOCX and appendix DOCX are needed |  |
| Task book | strongly_recommended |  | missing | Topic scope, objectives, and cover fields may be incomplete | limited | Provide file path or mark unavailable |  |
| Proposal/opening report | strongly_recommended |  | missing | Background, methods, and planned work may lack official source | limited | Provide file path or mark unavailable |  |
| Advisor requirements | strongly_recommended |  | missing | Chapter emphasis and special constraints may be missed | limited | Paste notes or provide file path |  |
| Advisor Word comments | optional |  | missing | Comment-based revision workflow cannot run | yes | Provide commented `.docx` when revision is needed |  |

## Sample And Style Materials

| Material | Priority | Path / Input | Status | Missing impact | Can continue? | User next step | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sample paper | strongly_recommended |  | missing | Outline rhythm, word distribution, and style imitation are weaker | yes | Provide `.docx` / `.pdf` sample or confirm none |  |
| Existing draft | optional |  | missing | Cannot reuse prior wording or compare revisions | yes | Provide draft path if available |  |
| Style notes | optional |  | missing | Tone and formatting preferences remain generic | yes | Paste school/advisor style notes if any |  |

## Software Project Evidence (when applicable)

| Material | Priority | Path / Input | Status | Missing impact | Can continue? | User next step | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Source code | required |  | missing | Implementation chapters cannot be evidence-based | no for project-specific body | Provide repository path or confirm non-code thesis |  |
| Database schema | strongly_recommended |  | missing | E-R diagram and data-design sections may be blocked | limited | Provide SQL, migration files, model/entity paths, or mark unavailable |  |
| API docs / routes | strongly_recommended |  | missing | Interface and module descriptions may lack source support | limited | Provide API docs, route files, or controller paths |  |
| Screenshots | strongly_recommended |  | missing | System demonstration and figure registry remain incomplete | limited | Provide screenshots or system access/start command |  |
| Test reports | strongly_recommended |  | missing | Cannot claim tests passed or report test results | limited | Provide reports/logs/screenshots or allow test-plan-only writing |  |

## Research / Survey / Experiment Evidence (when applicable)

| Material | Priority | Path / Input | Status | Missing impact | Can continue? | User next step | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Research object / corpus / case materials | required |  | missing | Research scope and factual claims cannot be grounded | no for research-specific body | Provide data, case documents, corpus path, or confirm software-system thesis |  |
| Survey or interview materials | strongly_recommended |  | missing | Survey analysis, findings, and tables may be blocked | limited | Provide questionnaire, interview notes, consent-safe summaries, or mark unavailable |  |
| Experiment protocol and raw results | strongly_recommended |  | missing | Experiment design and result claims cannot be verified | limited | Provide protocol, raw data, logs, or approve design-only writing |  |
| Analysis scripts / notebooks | optional |  | missing | Computation steps may need manual explanation | yes | Provide scripts or notebooks if analysis reproducibility matters |  |
| Experiment/data files | optional |  | missing | Analysis claims and tables may be limited | yes | Provide data path if the thesis needs experiments |  |

## Literature

| Material | Priority | Path / Input | Status | Missing impact | Can continue? | User next step | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PDF papers | strongly_recommended | `papers/` | missing | Literature pool and verification checklist cannot be built from local PDFs | limited | Provide PDF folder or approve using existing verified references |  |
| Existing reference list | strongly_recommended |  | missing | Citation formatting and cross-reference work starts from scratch | limited | Provide reference list if available |  |

## Intake Questions To Confirm

1. What is the thesis title and thesis type?
2. Is there a school or college template? If yes, provide the path.
3. Is there a word-count requirement?
4. Is final delivery expected as `.docx`, and is an appendix DOCX required?
5. Are there task-book, proposal, or advisor requirements?
6. Is there a sample paper to imitate?
7. Where is the project source code or research evidence?
8. Are screenshots, database schema, API docs, test reports, or literature PDFs available?
""",
    "content-decisions.md": """# Content Decisions

This file is useful when content candidates are available, but it must not block the main workflow when they are not.

Use it to record what should be emphasized, summarized, moved to appendix, deferred, or excluded. If the user has not provided enough candidates yet, keep the placeholder rows and continue with intake, standards, evidence building, or a provisional outline.

Decision values: `待确认`, `已同意`, `已拒绝`, `待补证据`, `暂缓`.

Suggested use values: `正文重点`, `正文简写`, `附录`, `暂缓`, `不写`.

## Current Content Decisions

| Content | Evidence | Suggested use | Decision | Reason | Notes |
| --- | --- | --- | --- | --- | --- |
| 论文主题和研究对象 | title/type/spec missing | 暂缓 | 待确认 | 需要先确认题目、论文类型和研究对象 | 不阻断材料收集和标准解析 |
| 核心功能或研究主线 | source/evidence pending | 正文重点 | 待补证据 | 通常支撑第 3-5 章，但必须先有证据 | 有源码或材料后再细化 |
| 数据库设计 / E-R 图 | schema missing | 暂缓 | 待补证据 | 仅系统设计类论文通常需要数据设计证据 | 没有 schema 时不要声称 E-R 图完整；非系统设计类可排除 |
| 测试结果或实验结果 | report/log missing | 不写 | 待确认 | 没有报告时不能声称测试通过或实验有效 | 可改写为测试方案或待验证计划 |
| 图表源文件和截图 | figure/screenshot source missing | 附录 | 待补证据 | 有源文件时可进入图表登记和附件 DOCX | 没有时不阻断文字草案，但限制最终交付 |

## Optional Candidate Backlog

Use this section for user-provided modules, diagrams, datasets, experiments, documents, or special advisor requirements that are not yet ready for the decision table.

| Candidate | Source / path | Why it may matter | Next review point |
| --- | --- | --- | --- |
|  |  |  |  |

## Update Rules

- After evidence extraction, update evidence status and suggested use for each candidate.
- Before confirming the outline, ask the user to review items marked `正文重点`, `暂缓`, or `不写`.
- Do not write formal body text from items marked `已拒绝`, `不写`, or `待补证据`.
- If the user cannot provide candidate details, keep this file light and continue the main workflow with clear limitations.
- When a content decision changes, update `user-dashboard.md`, `thesis-ai-spec.yaml`, or `figure-registry.yaml` only if the change affects progress, thesis facts, or figures.
""",
    "sample-template-analysis.md": """# Sample Template Analysis

Use this file to normalize parser outputs from school templates and sample papers into user-readable workflow decisions.

Parser Boundary: PDF and Word parsers are input providers only. If parser output is partial or weak, mark the affected field as `partial`, `unparsed`, or `needs_confirmation`; do not turn parser guesses into confirmed school rules.

## Source Summary

| Source | Type | Parser / input | Parser status | Limitations |
| --- | --- | --- | --- | --- |
|  | school_template / sample_docx / sample_pdf / manual_note |  | pending |  |

## template_rules

Confirmed rules from school templates, advisor notes, or official requirements. These outrank sample patterns.

| Rule | Source | Status | Notes |
| --- | --- | --- | --- |
|  |  | needs_confirmation |  |

## sample_patterns

Observed patterns from prior sample papers. These are references, not hard rules.

| Pattern | Source | Confidence | Notes |
| --- | --- | --- | --- |
| Outline rhythm |  | low | Pending sample analysis |
| Chapter word distribution |  | low | Pending word-count data |
| Figure/table rhythm |  | low | Pending figure/table extraction |

## recommendations

Recommendations for the current thesis. User confirmation is required before formal outline or body writing.

| Recommendation | Based on | Confidence | Needs user confirmation? | Notes |
| --- | --- | --- | --- | --- |
|  |  | low | yes |  |

## Unparsed Or Needs Confirmation

| Item | Reason | Impact | Next action |
| --- | --- | --- | --- |
|  |  |  |  |

## Outline Suggestion

Do not write this directly into `thesis-ai-spec.yaml` until the user confirms it.

| Chapter | Suggested title | Source | Confidence | Needs confirmation | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 |  | template_rules / sample_patterns / thesis_type / user_requirement / default_rule | low | yes |  |

## Source Notes

- `template_rules`: confirmed school or advisor rule.
- `sample_patterns`: observed in sample paper only.
- `thesis_type`: inferred from confirmed thesis type.
- `user_requirement`: explicitly provided by user.
- `default_rule`: fallback when no stronger source is available.

## Word Budget

Use this file for chapter-level word-count planning. Every budget item must name its source and confidence.

If the total word-count requirement is missing, all budgets are provisional.

| Chapter | Suggested words | Source | Basis | Confidence | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  | school_requirement / sample_ratio / user_requirement / default_rule |  | low | provisional |  |

## Budget Rules

- School or advisor word-count requirements outrank sample ratios.
- Sample ratios are references only.
- Do not use this file to claim final compliance until the word-count requirement is confirmed.
- Update `user-dashboard.md` when the budget needs user confirmation.
""",
    "blocker-report.md": """# Blocker Report

Use this file for the latest blocker that needs a user decision, missing material, or verification result. Keep it generic: not every thesis needs the same project artifacts.

Blocker types: `hard_blocker`, `limited_continue`, `user_choice_needed`.

## Current Blocker

| Item | Value |
| --- | --- |
| Phase | intake_only |
| Status | none |
| Blocker type | none |
| Blocker | none |
| Missing material / decision | none |
| Affected chapters or sections | none |
| Affected deliverables | none |
| Can continue with limitations? | yes |

## Options

| Option | Action | What becomes possible | Limitation / risk | Recommended |
| --- | --- | --- | --- | --- |
| A | Provide the missing material or decision | The affected part can be verified and completed | Requires user input before that part proceeds | yes when the item is required |
| B | Continue only with unaffected work | Main workflow can keep moving where evidence is sufficient | The blocked part must stay marked incomplete or provisional | yes when the missing item is optional or deferrable |
| C | Defer or exclude the affected content | Avoids inventing facts and keeps delivery scope honest | The scope, outline, or appendix plan may need adjustment | no unless user chooses this scope |

## Recommended Path

Recommended: pending

Reason: pending

## User Decision

| Decision | Date | Scope | Notes |
| --- | --- | --- | --- |
| pending |  |  |  |

## Sync Checklist

- [ ] Update `workflow-status.md`.
- [ ] Update `user-dashboard.md`.
- [ ] Update `material-inventory.md` if a material is missing or deferred.
- [ ] Update `content-decisions.md` if content scope changes.
- [ ] Update `evidence-gaps.md` if evidence is missing.
""",
    "user-decisions.md": """# User Decisions

Use this file to record user-approved choices that affect scope, evidence, standards, outline, delivery, or limitations.

Keep it short. This is a decision log, not a duplicate of `material-inventory.md`, `content-decisions.md`, or `blocker-report.md`.

## Decision Log

| ID | Date | Decision | Scope | Reason | Impact | Revisit when |
| --- | --- | --- | --- | --- | --- | --- |
| DEC-001 |  |  |  |  |  |  |

## When To Record

Record a decision when the user confirms:

- missing material should be treated as unavailable
- limited continuation is allowed
- a content item should be emphasized, deferred, or excluded
- school/template/advisor conflict is resolved
- outline, word count, DOCX, appendix, or filename scope is confirmed

## Relationship To Other Workflow Files

- `material-inventory.md` records material status.
- `content-decisions.md` records content emphasis and exclusion candidates.
- `blocker-report.md` records current blocker options.
- `user-decisions.md` records the user's final approved choice.
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
