# Workflow State Management

Use this reference when a thesis project needs persistent progress tracking, step-by-step execution records, or a clear "where are we now" state.

## Goal

Create a thesis workbench under `paper-context/workflow/` so the agent can resume work without guessing.

## Bootstrap

Run:

```powershell
python .\scripts\workspace\init_workflow_logs.py .
```

`init_thesis_workspace.py` runs this automatically unless `--no-workflow-logs` is used.

## Generated Files

| File | Purpose |
| --- | --- |
| `user-dashboard.md` | User-facing snapshot of progress, pending decisions, missing materials, and next action |
| `workflow-status.md` | Current stage, next action, overall status |
| `step-plan.md` | Step-by-step task board with dependencies |
| `progress-log.md` | Chronological work-session log |
| `material-inventory.md` | Interactive intake matrix with material priority, missing impact, continuation limits, and user next steps |
| `content-decisions.md` | Optional content emphasis, appendix, defer, and exclusion decisions when candidates are available |
| `sample-template-analysis.md` | Sample/template analysis report containing parser status, template rules, sample patterns, outline suggestions, and word budget |
| `blocker-report.md` | Latest blocker, affected scope, user options, recommendation, and sync checklist |
| `user-decisions.md` | User-approved choices affecting scope, evidence, standards, outline, delivery, or limitations |
| `evidence-gaps.md` | Unsupported claims and missing materials |
| `chapter-progress.md` | Chapter-level drafting/review status |
| `revision-log.md` | All changes from comments, AIGC pass, standards, figures, and final review |

## Update Rules

At the start of a thesis task:

1. Read `workflow-status.md`.
2. Read `user-dashboard.md`.
3. Read `step-plan.md`.
4. Read `blocker-report.md` when current status is blocked or the request may unblock prior work.
5. Read `user-decisions.md` when the request depends on prior user-approved scope, limitation, or delivery choices.
6. Read `content-decisions.md` when the request affects outline, chapter emphasis, figures, experiments, appendices, or exclusions.
7. Read `sample-template-analysis.md` when the request affects sample/template analysis, provisional outline, or word budget.
8. Read the module-specific files for the user's request.
9. Update current stage and next action before doing substantial work.

At the end of a thesis task:

1. Update `user-dashboard.md` with user-visible progress, pending decisions, missing materials, and next action.
2. Update `blocker-report.md` when work is blocked, limited, unblocked, or waiting for a user choice.
3. Update `user-decisions.md` when the user approves a choice affecting scope, unavailable materials, limited continuation, standards, outline, delivery, or filename rules.
4. Update `content-decisions.md` when new evidence changes what should be emphasized, summarized, moved to appendix, deferred, or excluded.
5. Update `sample-template-analysis.md` when sample/template parser output, outline suggestions, or word budget changes.
6. Append an entry to `progress-log.md`.
7. Update `step-plan.md` statuses.
8. Update `chapter-progress.md` if chapter work changed.
9. Add unresolved materials to `evidence-gaps.md`.
10. Add actual edits to `revision-log.md`.

## Status Vocabulary

Use these values consistently:

- `pending`: not started
- `in_progress`: currently being worked on
- `blocked`: cannot proceed without material or decision
- `needs_review`: generated but needs human/school/template review
- `done`: verified enough for the current stage
- `deprecated`: no longer used

## Phase Vocabulary

Use these workflow phases:

- `intake_only`
- `workspace_ready`
- `standards_resolved`
- `sample_analysis_done`
- `evidence_built`
- `spec_confirmed`
- `outline_confirmed`
- `writing_allowed`
- `delivery_done`

When a phase is blocked, write the state in `workflow-status.md`:

```yaml
phase: evidence_built
status: blocked
blocked_reason:
  - "缺少数据库 schema，不能生成 E-R 图。"
next_action:
  - "请提供数据库迁移文件、建表 SQL 或实体类目录。"
```

## Legal Rollback Table

| Current phase | Trigger event | Target phase |
| --- | --- | --- |
| `writing_allowed` | User adds a new sample paper, school template, or advisor requirement | `sample_analysis_done` |
| `writing_allowed` | User adds new source code, database, screenshots, or tests | `evidence_built` |
| `outline_confirmed` | User changes outline, word count, or sample/template observation | `sample_analysis_done` |
| `delivery_done` | Advisor Word comments arrive | `writing_allowed` |
| `delivery_done` | School/advisor requirement changes | `standards_resolved` |
| `delivery_done` | New evidence invalidates old facts | `evidence_built` |

## Non-Negotiable Rule

Do not silently skip log updates after changing thesis content or workflow state. The workbench is the memory of the thesis project.

## User Dashboard Rules

Keep `user-dashboard.md` short enough for the user to scan before making decisions.

Update it whenever any of these change:

- phase or status
- missing materials
- material priority, missing impact, or continuation limits
- user confirmation requests
- content emphasis, appendix, defer, or exclusion decisions
- blockers, options, recommendations, or limited-continuation status
- user-approved scope, limitation, standard, outline, or delivery decisions
- outline or word-count decisions
- delivery scope
- limited-continuation options

The dashboard should answer five questions:

1. Where are we now?
2. What has already been handled?
3. What does the user need to decide?
4. What is missing, and what does it affect?
5. What is the next recommended action?

## Content Decision Rules

`content-decisions.md` is an assistive decision layer, not a blocker by itself.

Use it when the user provides modules, features, experiments, datasets, diagrams, screenshots, appendix candidates, or special advisor preferences. If no candidate content is available, keep its placeholder rows and continue the main workflow with the normal material and evidence limitations.

Before confirming an outline or drafting a chapter, check active rows:

- `正文重点` can shape chapter emphasis after evidence is confirmed.
- `正文简写` can be summarized without over-expanding.
- `附录` should feed appendix/DOCX asset planning when sources exist.
- `暂缓` and `待补证据` should not become formal claims.
- `不写` and rejected items must stay out of the thesis body unless the user revises the decision.

## User Decision Rules

`user-decisions.md` is the durable record of user-approved choices. It should stay concise and reference the affected scope rather than duplicating full material tables or blocker reports.

Record a decision when the user confirms:

- a missing material is unavailable or deferred
- limited continuation is allowed
- a content item should be emphasized, deferred, excluded, or moved to appendix
- school/advisor requirement or sample/template observation conflict is resolved
- outline, word count, DOCX, appendix, filename, or delivery scope is confirmed
