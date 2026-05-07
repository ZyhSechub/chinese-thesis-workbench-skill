# Stop And Report

## Mechanism Definition

`stop_and_report` is a global blocking mechanism. At any phase, stop and report when continuing would require invented facts, unverifiable formatting, distorted figures, unreliable citations, or DOCX delivery that cannot be checked.

The report must be written into `paper-context/workflow/workflow-status.md` and `paper-context/workflow/blocker-report.md`, and the chat response must summarize the same blocker without weakening it.

Do not assume every thesis needs the same artifacts. Name the missing material or decision only when it is actually required by the user's topic, school requirements, evidence, or delivery scope.

## Blocker Type

Classify blockers before asking the user to act:

| Type | Meaning | Handling |
| --- | --- | --- |
| `hard_blocker` | Continuing the affected part would require invented or unverifiable content | Stop that part until the user provides material or changes scope |
| `limited_continue` | Unaffected work can continue, but a claim, section, figure, or deliverable must stay provisional | Continue only with visible limitations |
| `user_choice_needed` | Two valid sources, formats, scopes, or priorities conflict | Ask the user to choose or approve the recommended path |

## Blocking Conditions By Phase

| Phase | Stop when |
| --- | --- |
| `intake_materials` | Missing required title/type, delivery scope, school constraints, or user confirmation needed to proceed. Optional materials should be tracked, not treated as blockers by default. |
| `resolve_standards` | School template, task book, advisor requirement, or default rule conflicts and priority cannot be determined. |
| `analyze_sample_and_template` | A provided sample/template cannot be read, parsed, or reconciled with known requirements. If no sample exists, continue with explicit limitations. |
| `build_evidence` | Evidence required for a planned claim, section, figure, result, or deliverable is missing. Do not block on artifacts the user's thesis does not need. |
| `build_thesis_spec` | Thesis type, chapter structure, research object, or core facts cannot be confirmed. |
| `build_figure_registry` | Required figures/tables/screenshots lack sources for the selected thesis scope. Optional visuals may be deferred. |
| `draft_chapters` | Formal prose would need non-existent facts, functions, data, literature, screenshots, or test results. |
| `produce_docx` | DOCX dependencies are missing, image mapping fails, main DOCX cannot be generated, or appendix DOCX cannot be generated when required. |
| `quality_gates` | A required verification script fails or a required check cannot run. |

## Missing Material Format

Use this generic format when status is `blocked`:

```yaml
phase: evidence_built
status: blocked
blocker_type: limited_continue
blocked_reason:
  - "Missing required evidence or user decision for the affected section."
missing_materials:
  - type: "fill exact material or decision type"
    required_for: "fill affected section, claim, figure, citation, or deliverable"
    acceptable_inputs:
      - "file path"
      - "screenshot or report"
      - "user confirmation"
next_action:
  - "Choose one option in blocker-report.md or provide the missing input."
can_continue_with_limitations: true
```

Also update `blocker-report.md` with:

1. the blocker type
2. affected chapters or deliverables
3. whether limited continuation is allowed
4. two or three options
5. the recommended path and reason

## Recovery Flow

| New material or event | Return phase |
| --- | --- |
| New sample paper or template | `sample_analysis_done` |
| New source evidence, screenshots, tests, datasets, or equivalent project material | `evidence_built` |
| New advisor Word comments | `writing_allowed` |
| New school template | `standards_resolved` |
| User changes delivery scope or content scope | nearest affected phase |

## Limited Continuation Rules

- Without a school template, a draft may be produced, but do not claim it satisfies school formatting.
- Without a test report, write a test plan, but do not claim tests passed.
- Without optional visual proof, write only the supported description and do not mark the related figure, screenshot, or demonstration complete.
- Without verified literature, leave citations pending or use only confirmed sources.
- Without a project artifact that the topic does not require, do not block the project only because the generic template mentions it.

## Chat Response Contract

When blocked, report:

1. Current phase and status.
2. The blocker type.
3. The exact missing material, decision, or verification result.
4. Which thesis sections or deliverables are affected.
5. Whether limited continuation is allowed.
6. Two or three options the user can choose from.
7. The recommended option and reason.
