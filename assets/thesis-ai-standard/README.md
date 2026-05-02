# 本科论文通用 AI 标准化套件

本套件用于把任意本科毕业论文或毕业设计整理成 AI 能稳定读取、生成、检查和迭代的资料结构。它不绑定某一个学校、专业、项目或技术栈。

适用场景包括：

- 软件系统、网站、小程序、管理系统、物联网平台等设计与实现类论文。
- 实验、调查、数据分析、案例研究等研究类论文。
- 工程设计、产品设计、方案设计等毕业设计说明书。
- 已有 Word 论文的结构审查、图表规范化、证据链整理和终稿自检。

## 推荐使用顺序

1. 先读 `01-本科论文标准化最佳实践.md`，确定学校要求、论文类型和最低通用规则。
2. 再读 `02-公开标准与高校规范来源.md`，了解哪些规则来自国家标准、教育部文件或高校共性规范。
3. 填写 `templates/standard-profile.yaml`，把学校模板、导师要求、参考文献版本和格式默认值配置清楚。
4. 填写 `templates/thesis-ai-spec.yaml`，记录题目、专业、论文类型、章节、研究对象、证据材料和风险项。
5. 维护 `paper-context/workflow/` 里的进度、步骤、证据缺口和修改日志。
6. 使用 `templates/chapter-section-template.md` 逐章生成、改写或检查正文。
7. 使用 `templates/figure-registry.yaml` 管理全部图、表、公式、截图、源文件和正文引用位置。
8. 系统实现类论文先运行 `scripts/evidence/build_project_evidence.py` 生成 `paper-context/evidence/`。
9. 使用 `drawio/` 下的 `.drawio` 模板重画结构性图。
10. 文献综述或相关工作较多时，先用 skill 脚本抽取 PDF 参考文献，再建立文献交叉引用索引，并用 `citation-crossref-register.yaml` 做正文引用与文末参考文献闭环。
11. Word 论文有导师批注时，先抽取批注到 `paper-context/word-comments/`，再逐条修改和记录。
12. 正文写完或已有草稿时，用 `aigc-style-review.yaml` 和本地报告脚本做 AIGC 风格治理。
13. 最后用 `templates/ai-review-rubric.json` 做终稿审查，再进入 Word/PDF 视觉检查。

## 文件结构

```text
thesis-ai-standard/
  README.md
  01-本科论文标准化最佳实践.md
  02-公开标准与高校规范来源.md
  templates/
    standard-profile.yaml
    thesis-ai-spec.yaml
    chapter-section-template.md
    figure-registry.yaml
    literature-review-matrix.yaml
    citation-crossref-register.yaml
    aigc-style-review.yaml
    ai-review-rubric.json
    ai-prompts.md
  drawio/
    system-architecture-template.drawio
    backend-layered-architecture-template.drawio
    business-flow-template.drawio
    er-diagram-template.drawio
    algorithm-workflow-template.drawio
    sequence-diagram-template.drawio
```

## 标准依据优先级

实际使用时按以下顺序执行：

1. 学校或学院正式发布的毕业论文模板、撰写规范、任务书、答辩要求。
2. 导师或课题组明确要求。
3. 教育部本科毕业论文抽检、学术规范、学位论文作假处理等相关文件。
4. 现行国家标准，例如 `GB/T 7713.1-2025`、学校指定的 `GB/T 7714-2015` 或 `GB/T 7714-2025`。
5. 本套件提供的通用默认规则。

说明：截至 2026-05-01，`GB/T 7713.1-2025` 已实施；`GB/T 7714-2025` 已发布，实施日期为 2026-07-01。参考文献格式仍以学校当前通知为准。

## 给 AI 的总原则

- 不编造研究对象、系统功能、实验数据、数据库字段、接口路径、测试结果和参考文献。
- 先读取 `standard-profile.yaml`，再读取 `thesis-ai-spec.yaml`，最后读取章节证据材料。
- 学校没有明确规定的格式，只使用保守默认值，并标记为“可替换”。
- 每张图、表、公式、截图都必须能追溯到正文位置和证据来源。
- 论文正文不得出现“根据用户提供材料”“通过分析代码”“让 AI 生成”等工作流痕迹。

## 迁移方式

新论文不要直接改通用规则文件；应复制或填写 `templates/` 中的空白模板。

通用化迁移时，主要替换四类内容：

- 学校规范：写入 `standard-profile.yaml`。
- 论文事实：写入 `thesis-ai-spec.yaml`。
- 图表清单：写入 `figure-registry.yaml`。
- 专属图形：复制 `drawio/` 模板后按论文对象改节点。

## 证据层建议

系统实现类项目建议建立：

```text
paper-context/
  workflow/
    workflow-status.md
    step-plan.md
    progress-log.md
    material-inventory.md
    evidence-gaps.md
    chapter-progress.md
    revision-log.md
  evidence/
    project-evidence.json
    code-structure.md
    tech-stack.md
    api-list.md
    database-schema.md
    test-results.md
  literature/
    reference-extraction.json
    reference-extraction.md
    citation-crossrefs.md
    citation-crossrefs.json
    citation-crossref-register.yaml
  aigc/
    aigc-style-report.md
    aigc-style-report.json
  word-comments/
    word-comments.json
    word-comment-todos.md
    docx-revision-log.md
```

这些文件是论文事实依据，不是正文。AI 写作时必须把证据转化为论文语体，不能把扫描过程写进正文。

## AIGC 风格治理建议

本套件的 AIGC 模块不是“绕过检测器”，而是帮助论文减少模板化表达、空泛评价、模糊归因和证据不足的问题。推荐流程：

1. 先生成 `paper-context/aigc/aigc-style-report.md`。
2. 用户或 AI 根据报告确认需要修改的段落。
3. 只对高风险段落做定向改写。
4. 改写时保留事实、引用和数据边界。
5. 把未核验的来源、数据或项目事实标为 `needs_source` 或 `needs_evidence`。

## Word 批注修订建议

如果导师或评阅老师在 Word 文档中写了批注，推荐流程：

1. 用 `scripts/docx/extract_docx_comments.py` 抽取批注，生成 `word-comment-todos.md`。
2. AI 先阅读批注待办，不直接整篇重写。
3. 每条批注都对应一个处理结果：resolved / blocked / skipped。
4. 需要新增事实、数据或引用时，先标记 `needs_evidence` 或 `needs_source`。
5. 所有实际改动写入 `docx-revision-log.md` 和 `workflow/revision-log.md`。
