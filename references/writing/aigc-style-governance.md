# AIGC Style Governance Module

Use this module when the user asks for AIGC reduction, AI-flavor cleanup, humanized academic writing, style reports, or thesis prose polishing.

## Boundary

This module improves academic writing quality. It must not promise to bypass or defeat any detector. AI-writing detectors are imperfect and institution-specific, so the safe target is:

- clearer argumentation
- higher information density
- fewer formulaic academic cliches
- specific citations and evidence boundaries
- transparent revision notes
- thesis voice without AI workflow leakage

Do not fabricate citations, author names, DOI values, data, interviews, experiments, or project facts to make prose look more human.

## Best-Practice Workflow

Default to a report-first workflow:

1. Intake the draft, chapter, or detector report.
2. Run `scripts/review/analyze_aigc_style.py` when a text file is available.
3. Output a short style-risk report first, unless the user explicitly says "directly revise".
4. Ask for or infer the revision scope: light polish, paragraph rewrite, chapter rewrite, or final pass.
5. Revise only the high-risk passages and preserve facts.
6. Return revised text plus a revision log and unresolved evidence/citation gaps.

If the user provides an external AIGC report, treat it as one signal, not truth. Extract the highlighted paragraphs, compare them with the actual prose, then produce a local report.

## Risk Patterns To Scan

Scan paragraphs for these patterns:

- formulaic theory starts: "依据/基于/根据...理论"
- repetitive endings: "由此可见/综上所述/此案例表明"
- rigid enumeration: "首先/其次/再次/最后"
- passive analysis shells: "该设计体现了/该方法基于/这一做法反映了"
- vague problem statements: "核心问题在于/主要矛盾体现在"
- symmetric three-part claims with equal-length clauses
- vague attribution without a source: "研究表明/专家认为/有观点认为"
- filler phrases: "值得注意的是/不难发现/需要指出的是"
- generic positive conclusions: "具有重要意义/前景广阔/提供新思路"
- overuse of high-frequency academic cliches
- excessive bold text in thesis body
- adjacent paragraphs with identical rhythm or sentence starts

## Revision Moves

Use these moves in order:

1. Move theory names from the first sentence into the explanation where they are needed.
2. Replace generic summary endings with a concrete inference, limitation, or transition.
3. Break equal-weight enumeration; let the strongest reason carry more space.
4. Replace passive shells with a concrete design/research reason.
5. Delete filler phrases that do not carry information.
6. Replace vague attribution with a verified citation or mark `needs_source`.
7. Add precise boundaries: sample, data source, project path, method condition, limitation.
8. Keep academic register; do not make thesis prose chatty.

## Report Format

Return:

1. overall risk: low / medium / high
2. paragraph findings with pattern labels
3. hard failures: fabricated source risk, vague attribution, generic conclusion, missing evidence
4. suggested revision order
5. whether direct rewriting is safe now

## Rewrite Output Format

When rewriting, return:

1. revised text
2. key changes
3. facts preserved
4. `needs_source` or `needs_evidence` list
5. remaining style risks, if any

## Thesis-Specific Guardrails

- Use "本文" or neutral academic narration by default.
- Use "笔者" only when the school style allows it or the original text already uses it.
- Do not add personal experience, surprise, or uncertainty unless it is supported by real research notes, data, or project evidence.
- For system-design papers, concrete project facts are better than generic "important significance" claims.
- For literature reviews, style revision must not change author claims or source meanings.

## Suggested Prompts

Report first:

```text
Use $chinese-thesis-workbench. Read the chapter draft, run the AIGC style-governance module, and output only a style-risk report first. Do not rewrite yet.
```

Targeted revision:

```text
Use the style-risk report to revise only the high-risk paragraphs. Preserve facts, citations, and thesis voice. Mark unsupported claims as needs_source instead of inventing evidence.
```

## Source Notes

This module is informed by:

- `Yezery/aigc-down-skill`: report-first AIGC style-risk workflow and Chinese academic formulaic-pattern categories.
- OpenAI's public note that AI-text classifiers have reliability limits and should not be treated as a sole decision tool.
- Turnitin's guidance that AI indicators support educator judgment rather than automatically determining misconduct.
- Purdue OWL academic writing guidance on concision, nominalizations, and direct expression.
