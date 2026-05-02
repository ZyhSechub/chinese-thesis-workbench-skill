# Stop And Report

## Mechanism Definition

`stop_and_report` is a global blocking mechanism. At any phase, stop and report when continuing would require invented facts, unverifiable formatting, distorted figures, unreliable citations, or DOCX delivery that cannot be checked.

The report must be written into `paper-context/workflow/workflow-status.md`, and the chat response must summarize the same blocker without weakening it.

## Blocking Conditions By Phase

| Phase | Stop when |
| --- | --- |
| `intake_materials` | Missing school template, task book, proposal/opening report, sample paper, or word-count requirements, unless the user explicitly confirms there are no more materials. |
| `resolve_standards` | School template, task book, and advisor requirements conflict and priority cannot be determined. |
| `analyze_sample_and_template` | Sample paper cannot be read, template cannot be parsed, or style conflicts are unresolved. |
| `build_evidence` | Missing source code, database schema, APIs, screenshots, test reports, or data needed for key claims. |
| `build_thesis_spec` | Thesis type, chapter structure, research object, or system functions cannot be confirmed. |
| `build_figure_registry` | Key figures lack sources; system-design papers lack E-R diagrams, architecture diagrams, screenshots, or equivalent evidence. |
| `draft_chapters` | Formal prose would need non-existent facts, functions, data, literature, screenshots, or test results. |
| `produce_docx` | DOCX dependencies are missing, image mapping fails, main DOCX cannot be generated, or appendix DOCX cannot be generated. |
| `quality_gates` | A verification script fails or a required check cannot run. |

## Missing Material Format

Use this format when status is `blocked`:

```yaml
phase: evidence_built
status: blocked
blocked_reason:
  - "缺少数据库 schema，不能生成 E-R 图。"
missing_materials:
  - type: database_schema
    required_for: "第3章数据库设计、E-R 图、第4章实现说明"
    acceptable_inputs:
      - "建表 SQL"
      - "数据库迁移文件"
      - "实体类目录"
next_action:
  - "请提供数据库迁移文件、建表 SQL 或实体类目录。"
can_continue_with_limitations: false
```

## Recovery Flow

| New material or event | Return phase |
| --- | --- |
| New sample paper or template | `sample_analysis_done` |
| New source code, database, screenshots, or tests | `evidence_built` |
| New advisor Word comments | `writing_allowed` |
| New school template | `standards_resolved` |

## Limited Continuation Rules

- Without a school template, a draft may be produced, but do not claim it satisfies school formatting.
- Without a test report, write a test plan, but do not claim tests passed.
- Without screenshots, write module descriptions, but do not mark Chapter 4 delivery complete.
- Without verified literature, leave citations pending or use only confirmed sources.

## Chat Response Contract

When blocked, report:

1. Current phase and status.
2. The exact missing materials.
3. Which thesis sections or deliverables are affected.
4. Whether limited continuation is allowed.
5. The next action needed from the user.
