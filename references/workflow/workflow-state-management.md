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
| `workflow-status.md` | Current stage, next action, overall status |
| `step-plan.md` | Step-by-step task board with dependencies |
| `progress-log.md` | Chronological work-session log |
| `material-inventory.md` | School, project, evidence, and literature inventory |
| `evidence-gaps.md` | Unsupported claims and missing materials |
| `chapter-progress.md` | Chapter-level drafting/review status |
| `revision-log.md` | All changes from comments, AIGC pass, standards, figures, and final review |

## Update Rules

At the start of a thesis task:

1. Read `workflow-status.md`.
2. Read `step-plan.md`.
3. Read the module-specific files for the user's request.
4. Update current stage and next action before doing substantial work.

At the end of a thesis task:

1. Append an entry to `progress-log.md`.
2. Update `step-plan.md` statuses.
3. Update `chapter-progress.md` if chapter work changed.
4. Add unresolved materials to `evidence-gaps.md`.
5. Add actual edits to `revision-log.md`.

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
| `writing_allowed` | User adds a new sample paper or school template | `sample_analysis_done` |
| `writing_allowed` | User adds new source code, database, screenshots, or tests | `evidence_built` |
| `outline_confirmed` | User changes outline, word count, or style | `sample_analysis_done` |
| `delivery_done` | Advisor Word comments arrive | `writing_allowed` |
| `delivery_done` | School template changes | `standards_resolved` |
| `delivery_done` | New evidence invalidates old facts | `evidence_built` |

## Non-Negotiable Rule

Do not silently skip log updates after changing thesis content or workflow state. The workbench is the memory of the thesis project.
