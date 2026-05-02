# Standards And Template Resolution

Use this reference when a thesis task mentions school templates, undergraduate thesis standards, national standards, reference formatting, or conflicts between bundled defaults and a real school requirement.

## Resolution Order

Apply requirements in this order:

1. School or college thesis template, writing guide, defense notice, and official forms.
2. Advisor, research group, task book, proposal, or project-specific requirement.
3. Ministry-level academic integrity and undergraduate thesis inspection rules.
4. School-specified national standards.
5. Bundled fallback defaults in `thesis-ai-standard/`.

Never let a bundled default override a real school template. If a requirement is missing, label the fallback as `default_not_school_confirmed`.

## Current Public Standard Baseline

As of 2026-05-01:

- `GB/T 7713.1-2025` is the current public baseline for thesis/dissertation writing structure and composition. Use it as a structural reference only unless the school explicitly adopts it.
- `GB/T 7714-2025` has been released and is scheduled for implementation on 2026-07-01. Many schools may still require `GB/T 7714-2015` during the transition. The `standard-profile.yaml` file must record the actual school-required version.
- Education ministry thesis inspection and academic-integrity rules are quality and integrity baselines, not page-layout templates.

## Standard Profile Fields To Fill First

Before drafting, update `thesis-ai-standard/templates/standard-profile.yaml`:

- school, college, major, update date
- exact template path or URL
- advisor or task-book requirement source
- reference style standard and version
- thesis writing standard version if specified by the school
- fallback items that are not school-confirmed
- Word/PDF layout-sensitive items that still need visual review

## Conflict Handling

When two sources conflict:

| Conflict | Action |
| --- | --- |
| school template vs bundled default | follow school template |
| advisor requirement vs bundled chapter model | follow advisor if academically reasonable |
| school requires `GB/T 7714-2015` but bundled docs mention 2025 | use 2015 and record the school source |
| school is silent on an item | use fallback default and mark it as replaceable |
| source is unclear or unofficial | do not enforce it; list as `needs_confirmation` |

## Output Contract

When resolving standards, return:

1. confirmed hard rules
2. fallback defaults
3. conflicts and chosen source
4. missing confirmations
5. layout items that require Word/PDF visual review

Do not write final thesis prose until hard rules and fallback assumptions are separated.
