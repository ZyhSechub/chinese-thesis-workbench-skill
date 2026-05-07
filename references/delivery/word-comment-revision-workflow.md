# Word Comment Revision Workflow

Use this reference when the user uploads a `.docx` thesis draft with Word comments or asks to revise the paper according to advisor comments.

## Goal

Turn Word comments into a structured revision workflow:

1. Extract comments.
2. Convert them into markdown todos.
3. Plan safe changes.
4. Modify the document using this skill's DOCX delivery workflow and `scripts/docx/` helpers.
5. Log each change and verify the document.

## Extract Comments

Run:

```powershell
python .\scripts\docx\extract_docx_comments.py .\draft.docx --out .\paper-context\word-comments
```

Outputs:

```text
paper-context/word-comments/
  word-comments.json
  word-comment-todos.md
  docx-revision-log.md
```

The script extracts comment author, date, text, and the nearest paragraph preview. It does not decide the correct academic revision.

## Revision Process

1. Read `word-comment-todos.md`.
2. Group comments by type:
   - content addition
   - deletion or compression
   - logic/structure adjustment
   - citation/reference issue
   - formatting issue
   - figure/table issue
   - unclear or conflicting comment
3. Map each comment to evidence:
   - thesis specs
   - source code / experiment data
   - literature references
   - school template
   - existing draft text
4. Modify only what the comment justifies.
5. Update `docx-revision-log.md` and `paper-context/workflow/revision-log.md`.

## DOCX Editing Rules

- Prefer Microsoft Word automation or a manual Word/PDF review for layout-sensitive changes.
- For content edits, preserve existing styles and section structure.
- For comments that require new facts, first add `needs_evidence` instead of inventing content.
- For comments that require citations, first add `needs_source` unless the source is already verified.
- For formatting comments, follow school template first and preserve unspecified formatting.

## Text-Only Edit Mode

When the user already has a formatted `.docx` draft and only asks for local paragraph text additions, deletions, or replacements, prefer text-only edit mode:

```powershell
python scripts/docx/apply_textual_edits.py draft.docx draft-edited.docx --replace "原文锚点" "新文本"
```

This mode only changes paragraph text. It does not rebuild styles, handle layout comments, or fill missing facts. If an anchor matches zero paragraphs or multiple paragraphs, stop and ask the user to confirm a unique anchor.

## Output Contract

After revising by comments, return:

1. comment summary: total / resolved / unresolved
2. revised document path
3. `docx-revision-log.md` path
4. unresolved comments with reasons
5. verification performed or not performed

## Stop Conditions

Do not auto-apply a comment when:

- the comment conflicts with school rules
- the comment requires missing data, source, or screenshot
- the target location is ambiguous
- applying the change would rewrite a large chapter without user approval
- Word/PDF layout fidelity cannot be checked but the change is layout-sensitive
