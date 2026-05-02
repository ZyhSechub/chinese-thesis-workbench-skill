# Merge Map

| Source file | New location | Change note |
| --- | --- | --- |
| thesis-standardizer/SKILL.md | SKILL.md | Rewritten as the routing entry point and integrated with the Chinese thesis drafting pipeline. |
| thesis-standardizer/agents/openai.yaml | agents/openai.yaml | Rewritten for the new Chinese thesis workbench positioning. |
| thesis-standardizer/references/standards-and-template-resolution.md | references/standards/standards-and-template-resolution.md | Moved under standards. |
| thesis-standardizer/references/source-to-thesis-workflow.md | references/evidence/source-to-thesis-workflow.md | Moved under evidence. |
| thesis-standardizer/references/literature-and-pdf-workflow.md | references/evidence/literature-and-pdf-workflow.md | Moved under evidence. |
| thesis-standardizer/references/aigc-style-governance.md | references/writing/aigc-style-governance.md | Moved under writing. |
| thesis-standardizer/references/workflow-state-management.md | references/workflow/workflow-state-management.md | Moved under workflow and extended with phase/status rollback rules. |
| thesis-standardizer/references/word-comment-revision-workflow.md | references/delivery/word-comment-revision-workflow.md | Moved under delivery. |
| thesis-standardizer/references/rapid-thesis-workflow.md | references/workflow/rapid-thesis-workflow.md | Moved under workflow. |
| thesis-standardizer/references/quality-gates.md | references/workflow/quality-gates.md | Moved under workflow. |
| thesis-standardizer/scripts/init_thesis_workspace.py | scripts/workspace/init_thesis_workspace.py | Moved and path root adapted to the new nested script location. |
| thesis-standardizer/scripts/init_workflow_logs.py | scripts/workspace/init_workflow_logs.py | Moved and state model updated. |
| thesis-standardizer/scripts/check_thesis_workspace.py | scripts/workspace/check_thesis_workspace.py | Moved under workspace. |
| thesis-standardizer/scripts/build_project_evidence.py | scripts/evidence/build_project_evidence.py | Moved under evidence. |
| thesis-standardizer/scripts/extract_pdf_references.py | scripts/literature/extract_pdf_references.py | Moved under literature. |
| thesis-standardizer/scripts/build_literature_crossrefs.py | scripts/literature/build_literature_crossrefs.py | Moved under literature. |
| thesis-standardizer/scripts/extract_docx_comments.py | scripts/docx/extract_docx_comments.py | Moved under docx. |
| thesis-standardizer/scripts/analyze_aigc_style.py | scripts/review/analyze_aigc_style.py | Moved under review. |
| thesis-standardizer/assets/thesis-ai-standard/* | assets/thesis-ai-standard/* | Preserved as bundled standard assets. |
| lunwen/SKILL.md | references/writing/writing-pipeline.md | Not copied verbatim; core drafting constraints are lifted into SKILL.md and writing references. |
| lunwen/prompts/intake.md | references/workflow/intake.md | Moved as intake material collection guide. |
| lunwen/prompts/style_extractor.md | references/standards/style-extraction.md | Moved as style extraction guide. |
| lunwen/prompts/fact_extractor.md | references/evidence/fact-extraction.md | Moved as project fact extraction guide. |
| lunwen/prompts/sample_analyzer.md | references/writing/sample-analysis.md | Moved as sample analysis guide. |
| lunwen/prompts/chapter_writer.md | references/writing/writing-pipeline.md | Moved as chapter drafting guide. |
| lunwen/prompts/reference_selector.md | references/writing/reference-selection.md | Moved as reference selection guide. |
| lunwen/prompts/docx_formatter.md | references/delivery/docx-delivery.md | Moved as DOCX formatting guide. |
| lunwen/prompts/final_checker.md | references/delivery/final-delivery-check.md | Moved as final delivery guide. |
| lunwen/references/default-style.md | references/standards/default-style.md | Moved under standards. |
| lunwen/references/chapter-patterns.md | references/writing/chapter-patterns.md | Moved under writing. |
| lunwen/tools/analyze_docx.py | scripts/docx/analyze_docx.py | Moved under docx. |
| lunwen/tools/analyze_sample_pdf.py | scripts/docx/analyze_sample_pdf.py | Moved under docx. |
| lunwen/tools/markdown_utils.py | scripts/docx/markdown_utils.py | Moved under docx. |
| lunwen/tools/generate_thesis_docx.py | scripts/docx/generate_thesis_docx.py | Moved under docx. |
| lunwen/tools/generate_diagram_appendix_docx.py | scripts/docx/generate_diagram_appendix_docx.py | Moved under docx. |
| lunwen/tools/count_chapter_words.py | scripts/review/count_chapter_words.py | Moved under review and import path adapted. |
| lunwen/tools/build_reference_pool.py | scripts/literature/build_reference_pool.py | Moved under literature. |
| lunwen/tools/write_reference_verification_template.py | scripts/literature/write_reference_verification_template.py | Moved under literature. |
| lunwen/tools/render_mermaid.py | scripts/figures/render_mermaid.py | Moved under figures. |
| lunwen/tools/extract_mermaid_blocks.py | scripts/figures/extract_mermaid_blocks.py | Moved under figures. |
| lunwen/tools/ensure_thesis_assets.py | scripts/figures/ensure_thesis_assets.py | Moved under figures. |
| lunwen/tools/build_image_map.py | scripts/figures/build_image_map.py | Moved under figures. |
| lunwen/tools/extract_screenshot_placeholders.py | scripts/screenshots/extract_screenshot_placeholders.py | Moved under screenshots. |
| lunwen/tools/build_screenshot_plan.py | scripts/screenshots/build_screenshot_plan.py | Moved under screenshots and default output adapted to `paper-output/screenshots`. |
| lunwen/tools/capture_thesis_screenshots.py | scripts/screenshots/capture_thesis_screenshots.py | Moved under screenshots and browser script path adapted. |
| lunwen/tools/browser/capture_screenshots.mjs | scripts/screenshots/browser/capture_screenshots.mjs | Moved under screenshots/browser and usage/default output adapted. |
| lunwen/package.json | package.json | Rewritten to point npm scripts at the new screenshot path. |
| lunwen/requirements.txt | requirements.txt | Merged with imports from both source script sets. |
| lunwen/examples/screenshot-plan.json | not migrated | Checked for script references; no copied script hard-references this example file. It remains an example and does not participate in runtime. |
| lunwen/docs/PRD.md | not migrated | Product background document, not required by the runtime skill. |
| lunwen/INSTALL.md | not migrated | Source installation note, superseded by bundled script/dependency files. |
| lunwen/README.md | not migrated | Source readme, not part of final skill payload. |
| lunwen/examples/sample-outline.md | not migrated | Example file, not required by runtime. |
| lunwen/.claude/* | not migrated | Platform-specific source agent commands. |
| lunwen/.trae/* | not migrated | Platform-specific source agent commands. |
