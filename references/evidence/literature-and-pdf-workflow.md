# Literature And PDF Workflow

Use this reference when a thesis needs literature review, related work, citation cleanup, citation placement, or reference extraction from PDF papers.

## Inputs

Preferred inputs:

- PDF papers in one folder
- thesis title, abstract, keywords, chapter outline, or `thesis-ai-spec.yaml`
- school reference style requirement
- existing reference list, if any

## PDF Reference Extraction

Run:

```powershell
python .\scripts\literature\extract_pdf_references.py .\papers --out .\paper-context\literature
```

Outputs:

```text
paper-context/literature/
  reference-extraction.json
  reference-extraction.md
```

The script extracts candidate reference sections. Treat output as raw evidence. Verify bibliographic fields manually or with trusted sources before final formatting.

## Citation Cross-References

If a topic outline exists, create a citation cross-reference index:

`paper-context/topics.md` is a lightweight topic file. It can be drafted from the confirmed outline, `thesis-ai-spec.yaml`, or user-provided keywords. Use one topic per bullet; include methods, domain terms, chapter names, and known acronyms that should guide citation placement.

Example:

```markdown
# Thesis Topics

- Chapter 1: research background; domestic and international status; problem definition
- Chapter 2: key theories; core technologies; evaluation methods
- Chapter 3: requirement analysis; system architecture; database design
- Chapter 4: implementation modules; algorithms; user workflow
- Chapter 5: testing; experiment results; comparison baseline
- Keywords: recommender system; collaborative filtering; Vue; Spring Boot
```

```powershell
python .\scripts\literature\build_literature_crossrefs.py .\paper-context\literature\reference-extraction.json --topics .\paper-context\topics.md --out .\paper-context\literature\citation-crossrefs.md --json-out .\paper-context\literature\citation-crossrefs.json
```

Cross-reference rules:

- Match references to claims by overlap with topic terms, methods, domain words, and known acronyms.
- Prefer recent and directly relevant papers for research status sections.
- Prefer method papers for method/theory sections.
- Prefer system/application papers for design comparison sections.
- Do not cite a paper merely because a keyword appears once.
- Mark weak matches as `needs_check`.

After generating cross-references, update `thesis-ai-standard/templates/citation-crossref-register.yaml` or a project copy of it. The register is the closure layer:

- body claim -> citation candidate
- citation candidate -> verified reference-list entry
- reference-list entry -> body citation location
- unresolved candidate -> `needs_check`, `rejected`, or `missing_source`

## Writing Literature Review

Structure by theme, not by one-paper-per-paragraph:

1. Define the research or engineering problem.
2. Group literature into 2-4 themes.
3. Compare methods, data, systems, or conclusions.
4. Identify the gap that the thesis addresses.
5. Connect the gap to the thesis work.

Avoid:

- fabricated author/year/venue
- references not cited in body text
- body citations missing from final reference list
- DOI or URL hallucination
- "AI found" or "the uploaded paper says" wording

## Final Checks

- Every cited source appears in the reference list.
- Every reference-list item is cited, unless school rules allow uncited background references.
- `citation-crossref-register.yaml` or equivalent notes record the body/reference closure.
- Reference format follows `standard-profile.yaml`.
- Extraction uncertainty is resolved before final submission.
