---
name: chinese-thesis-workbench
description: Standardize, draft, revise, check, and package Chinese undergraduate thesis or graduation-design papers from school templates, task books, proposals, sample papers, source code, screenshots, databases, APIs, tests, literature PDFs, Word comments, and existing drafts. Use when the user asks to write, generate, refactor, polish, reduce AIGC style, verify, format, or deliver a Chinese thesis with evidence traceability, figure registries, workflow logs, chapter word control, screenshots, references, DOCX output, and appendix DOCX.
---

# Chinese Thesis Workbench

## Operating Model

Use standards and evidence as the control layer, then use the Chinese thesis drafting pipeline as the output layer. Treat school templates, advisor requirements, task books, sample papers, source code, databases, APIs, tests, literature PDFs, screenshots, Word comments, and existing drafts as materials that must be resolved into structured state before formal prose is written.

The workbench has two sides:

- Governance side: `paper-context/` stores workflow state, standards, evidence, literature, AIGC reports, and Word comment revisions.
- Delivery side: `paper-output/` stores thesis Markdown, DOCX, appendix DOCX, figures, screenshots, image maps, and reference verification artifacts.
- User-facing visibility and decision side: `paper-context/workflow/user-dashboard.md` summarizes current progress, missing materials, user decisions needed, and the next recommended action. `paper-context/workflow/content-decisions.md` records optional content emphasis and exclusion decisions when candidate content is available. `paper-context/workflow/blocker-report.md` records the latest blocker, options, recommendation, and limited-continuation status. `paper-context/workflow/user-decisions.md` records user-approved choices that affect scope, evidence, standards, outline, delivery, or limitations. These files improve transparency; they do not override standards, evidence, or delivery quality gates.

## Required Workflow

Run the workflow in this order unless the user is only asking for a narrow inspection or revision:

1. `intake_materials`: collect materials and record priority, gaps, missing impact, continuation limits, and user next steps in `paper-context/workflow/material-inventory.md`.
2. `init_workspace`: initialize `thesis-ai-standard/`, `paper-context/`, and workflow logs.
3. `resolve_standards`: fill `thesis-ai-standard/templates/standard-profile.yaml`.
4. `analyze_sample_and_template`: normalize school template and sample-paper parser outputs into lightweight analysis reports, outline suggestions, and word budgets before drafting; parser output does not drive DOCX formatting unless the user explicitly selects sample-style generation via `--sample-analysis` or template-copy filling via `--from-template`.
5. `build_evidence`: extract project facts into `paper-context/evidence/`.
6. `stop_and_report`: stop or limit only the affected scope whenever evidence, standards, figures, citations, or DOCX delivery cannot be verified; record options in `blocker-report.md`.
7. `build_thesis_spec`: fill `thesis-ai-standard/templates/thesis-ai-spec.yaml`.
8. `build_figure_registry`: fill `thesis-ai-standard/templates/figure-registry.yaml`.
9. `confirm_outline`: confirm chapter structure, word counts, sample/template observations, and any available content emphasis/exclusion decisions before writing.
10. `draft_chapters`: write only from confirmed structured facts and evidence.
11. `produce_assets`: generate or collect figures, diagrams, screenshots, tables, and appendix sources.
12. `produce_docx`: generate or edit the main DOCX and appendix DOCX into `paper-output/` using the recorded delivery path.
13. `quality_gates`: run standards, evidence, reference, figure, DOCX, and AIGC checks.
14. `delivery_report`: report outputs, limitations, remaining human decisions, and verification evidence.

`stop_and_report` is a global blocking mechanism, not just step 6. Read `references/workflow/stop-and-report.md` whenever continuing may require guessing.

## Phase + Status State Model

Use this two-layer state model in `paper-context/workflow/workflow-status.md`, and mirror the user-facing summary in `paper-context/workflow/user-dashboard.md`:

| Field | Allowed values |
| --- | --- |
| `phase` | `intake_only`, `workspace_ready`, `standards_resolved`, `sample_analysis_done`, `evidence_built`, `spec_confirmed`, `outline_confirmed`, `writing_allowed`, `delivery_done` |
| `status` | `pending`, `in_progress`, `blocked`, `needs_review`, `done`, `deprecated` |

When status becomes `blocked`, write `blocked_reason`, `missing_materials`, `next_action`, and `can_continue_with_limitations` in the status file. Do not hide blockers in chat only.

After any meaningful phase, blocker, material, outline, or delivery-scope change, update `user-dashboard.md` so the user can see:

- current phase and status
- completed work
- decisions waiting for user confirmation
- missing materials and their impact
- next recommended action
- limited-continuation options, if any

## Decision Tree

1. If there is no workspace, run `scripts/workspace/init_thesis_workspace.py`.
2. If school/advisor/template rules are missing or conflicting, resolve standards first.
3. If sample/template analysis is missing, analyze it before `thesis-ai-spec.yaml`.
4. If source evidence or literature is missing, build evidence and reference pools before writing.
5. If `thesis-ai-spec.yaml` is not confirmed, do not write formal thesis body.
6. If `figure-registry.yaml` is not ready, do not claim figures/tables/screenshots are complete.
7. If asked to revise Word comments, extract comments and route back to `writing_allowed`.
8. If asked for final delivery, run quality gates and produce both main and appendix DOCX.

## Hard Rules

- School and advisor requirements override default rules.
- Do not write formal thesis body before materials are collected or the user explicitly confirms there are no more materials.
- During intake, classify materials as `required`, `strongly_recommended`, or `optional`, and explain the effect of each missing required or strongly recommended material.
- Use `content-decisions.md` when the user provides feature/module/experiment/appendix candidates, but do not block the main workflow only because no candidate content has been provided yet.
- Record user-approved scope, material-unavailable, limited-continuation, standard-conflict, content-exclusion, outline, word-count, DOCX, appendix, and filename decisions in `user-decisions.md`.
- User-facing workflow files are decision aids only. They must not weaken school/advisor requirements, evidence requirements, citation verification, figure provenance, or DOCX delivery checks.
- Do not write formal thesis body before standards, sample/template analysis, and evidence building are complete.
- When evidence is insufficient, trigger `stop_and_report`; do not guess missing facts.
- When blocked, classify the issue as `hard_blocker`, `limited_continue`, or `user_choice_needed`, then provide user options and a recommended path.
- `thesis-ai-spec.yaml` is the single entry point for thesis facts.
- `figure-registry.yaml` is the single entry point for figures, tables, screenshots, and diagram sources.
- Thesis prose may consume structured facts and evidence only; do not expand directly from README files or old notes.
- Do not write content that `content-decisions.md` marks as rejected, excluded, or waiting for evidence.
- Do not invent features, fields, APIs, test results, experiment data, or references.
- AIGC style governance runs after the evidence chain is complete and may only improve academic expression, evidence density, and vague wording.
- Thesis body must not expose AI workflow language.
- Chapter 4 implementation must bind to real modules, screenshots, core code, SQL, or equivalent evidence.
- System-design theses without an E-R diagram or equivalent data-design evidence cannot be marked complete.
- Generate both the main thesis DOCX and appendix DOCX. For strict school formatting, prefer template-copy filling via `scripts/docx/apply_textual_edits.py --from-template`; otherwise use default or sample-style generation. Do not promise full template reproduction. Preserve diagram source, E-R source, flowchart source, and related assets in the appendix.
- Formula delivery must be explicit: `latex_text` preserves source formula text, while `formula_image` requires matching image assets.
- Output filenames must use the thesis title, not generic names such as `final`, `draft`, `paper-final`, or `doc1`.
- Literature workflow must be: build pool -> verify -> filter -> format -> generate verification checklist.

## Resource Map

| Need | Resource |
| --- | --- |
| Intake and fast workflow | `references/workflow/intake.md`, `references/workflow/rapid-thesis-workflow.md` |
| Workflow state, blockers, and sparse-material handoff | `references/workflow/workflow-state-management.md`, `references/workflow/stop-and-report.md`, `references/workflow/material-gap-handoff.md` |
| Standards and template resolution | `references/standards/standards-and-template-resolution.md`, `references/standards/style-extraction.md`, `references/standards/default-style.md` |
| Evidence extraction | `references/evidence/source-to-thesis-workflow.md`, `references/evidence/fact-extraction.md` |
| Literature/PDF workflow | `references/evidence/literature-and-pdf-workflow.md`, `scripts/literature/` |
| Writing and chapter control | `references/writing/writing-pipeline.md`, `references/writing/chapter-patterns.md`, `references/writing/sample-analysis.md` |
| AIGC style governance | `references/writing/aigc-style-governance.md`, `scripts/review/analyze_aigc_style.py` |
| DOCX delivery and Word comments | `references/delivery/docx-delivery.md`, `references/delivery/word-comment-revision-workflow.md`, `scripts/docx/` |
| Figures and screenshots | `scripts/figures/`, `scripts/screenshots/`, `thesis-ai-standard/templates/figure-registry.yaml` |
| Merge provenance | `references/merge-map.md` |

## Quality Gates

Before claiming delivery quality, check:

- `standard-profile.yaml`, `thesis-ai-spec.yaml`, and `figure-registry.yaml` exist and are internally consistent.
- Every major factual claim has a source in `paper-context/evidence/` or verified literature.
- Every figure/table has `source_kind`, `source_path`, `image_path`, `evidence_source`, `first_mention`, and `status`.
- References are real, selected from a verified pool, and have a generated verification checklist.
- AIGC style changes do not add facts.
- Main DOCX and appendix DOCX exist in `paper-output/`.
- Screenshot, diagram, and image-map paths resolve on Windows.
- Workflow logs reflect the current phase, status, blockers, and delivery limitations.
- `user-dashboard.md` reflects the user-visible progress, pending decisions, missing materials, and next action.
- `blocker-report.md` reflects the latest blocker, affected scope, user options, recommended path, and whether limited continuation is allowed.
- `user-decisions.md` records user-approved choices that affect scope, missing-material handling, limitations, standards, outline, or delivery.
- If `content-decisions.md` has active candidates, their approved/deferred/excluded status is consistent with the outline, thesis spec, and figure registry.

## Delivery Contract

Deliver thesis artifacts under `paper-output/`:

- `<论文标题>.md`
- `<论文标题>.docx`
- `<论文标题>-附件.docx`
- `<论文标题>-image-map.json`
- `<论文标题>-文献核验清单.json`
- `figures/`
- `screenshots/`

Report what was verified, what could not be verified, and what still needs human confirmation. If verification cannot run, state the command and the reason.
