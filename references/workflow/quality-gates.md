# Quality Gates

Use before saying a thesis package, chapter draft, or review is complete.

## Gate 1: Standards

- `standard-profile.yaml` exists and identifies school/advisor rules.
- Reference style version is explicit.
- Bundled defaults are marked as fallback, not school requirements.
- Standard conflicts are resolved using `standards-and-template-resolution.md`.
- Word/PDF layout-sensitive items are not claimed verified unless they were checked.

## Gate 2: Evidence

- `thesis-ai-spec.yaml` contains the thesis type and real facts.
- `figure-registry.yaml` lists each figure, table, equation, screenshot, and source.
- Claimed functions map to code, screenshots, tests, or user-provided materials.
- Claimed tests or experiments map to reports, logs, tables, or screenshots.
- Literature claims map to verified references or explicit `needs_check` candidates.
- `paper-context/workflow/evidence-gaps.md` lists unresolved unsupported claims.

## Gate 3: Academic Integrity

- No fabricated references, DOI values, years, journals, APIs, fields, test results, samples, or metrics.
- No AI workflow leakage in body text.
- PDF reference extraction is treated as candidate evidence until verified.
- Private data, tokens, account names, phone numbers, and keys are not exposed in screenshots or prose.
- AIGC style work is framed as academic writing quality review, not detector evasion.

## Gate 4: Structure

- Chapter structure matches `type_profile`.
- Chapter titles and numbering are continuous.
- Introduction does not promise work absent from later chapters.
- Conclusion summarizes completed work only.

## Gate 4.5: AIGC Style Governance

- `aigc-style-report.md` exists when the user requested AIGC/style reduction.
- High-risk paragraphs were revised or explicitly left unchanged with reasons.
- Vague attribution was removed, verified, or marked `needs_source`.
- Generic positive conclusions were replaced with concrete claims, limits, or future work.
- Revisions did not add unsupported facts or citations.

## Gate 4.6: Workflow Logs

- `paper-context/workflow/user-dashboard.md` gives the user a current, scan-friendly view of progress, pending decisions, missing materials, and next action.
- `paper-context/workflow/material-inventory.md` classifies materials by priority and explains missing impact, continuation limits, and user next steps.
- `paper-context/workflow/content-decisions.md` is checked when active candidates exist; rejected, excluded, deferred, or evidence-pending content is not silently written into the thesis body.
- `paper-context/workflow/sample-template-analysis.md` exists after sample/template analysis and includes template rules, sample patterns, outline suggestions, and word budget sections.
- Parser outputs marked `partial`, `failed`, or `needs_confirmation` are not treated as confirmed school rules.
- The outline suggestion section remains provisional until user confirmation and does not silently overwrite `thesis-ai-spec.yaml`.
- The word budget section names the source and confidence for each chapter budget; sample ratios do not override school or advisor word-count requirements.
- `paper-context/workflow/blocker-report.md` records the latest blocker options when work is blocked or limited; generic optional artifacts do not become blockers unless required by the actual thesis scope.
- `paper-context/workflow/user-decisions.md` records user-approved scope, unavailable-material handling, limited continuation, standards, outline, delivery, and filename decisions.
- `paper-context/workflow/workflow-status.md` reflects the current stage.
- `paper-context/workflow/step-plan.md` shows completed, blocked, and pending steps.
- `paper-context/workflow/progress-log.md` has a current session entry.
- `paper-context/workflow/revision-log.md` records content and Word-comment changes.

## Gate 4.7: Word Comment Revision

- Word comments were extracted to `paper-context/word-comments/word-comment-todos.md` when a commented `.docx` was provided.
- Each comment is marked resolved, skipped, or blocked with a reason.
- DOCX edits are logged in `docx-revision-log.md`.
- Layout-sensitive comment fixes were verified through Word/PDF when possible.

## Gate 5: Figures, Tables, Equations

- Figure captions are below figures unless school rules differ.
- Table captions are above tables unless school rules differ.
- Every figure/table/equation is mentioned in text before or near placement.
- Structural diagrams have editable sources.
- Formula variables and units are explained.
- Formula delivery mode is recorded as `latex_text` or `formula_image`; `latex_text` preserves source formula text, and `formula_image` requires matching image assets.
- Generated DOCX files use the built-in default thesis format. Do not claim that the generated DOCX faithfully reproduces a school Word template.

## Gate 6: Script Validation

Run applicable checks:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$env:PYTHONUTF8='1'; python (Join-Path $codexHome 'skills\.system\skill-creator\scripts\quick_validate.py') .
Get-ChildItem .\scripts -Recurse -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
python .\scripts\workspace\check_thesis_workspace.py .\assets\thesis-ai-standard
python .\scripts\workspace\init_workflow_logs.py .\tmp-thesis-workspace
python .\scripts\review\analyze_aigc_style.py .\sample-draft.md --out .\paper-context\aigc\aigc-style-report.md
```

When sample/template parser JSON exists, run:

```powershell
python .\scripts\workspace\build_sample_template_outputs.py .\paper-context\workflow\sample-parser-result.json --target .
```

Run `extract_docx_comments.py` when a real `.docx` draft with comments exists:

```powershell
python .\scripts\docx\extract_docx_comments.py .\draft.docx --out .\paper-context\word-comments
```

For generated thesis workspaces:

```powershell
python - <<'PY'
import json, yaml
from pathlib import Path
base = Path('thesis-ai-standard/templates')
for name in ['standard-profile.yaml', 'thesis-ai-spec.yaml', 'figure-registry.yaml']:
    yaml.safe_load((base / name).read_text(encoding='utf-8'))
json.loads((base / 'ai-review-rubric.json').read_text(encoding='utf-8'))
print('OK')
PY
```

On Windows PowerShell, use a here-string piped into Python if shell heredoc is unavailable.

## Completion Language

Report:

- what was generated or changed
- what was verified
- what still needs human/school-template review
- which evidence is missing, if any
