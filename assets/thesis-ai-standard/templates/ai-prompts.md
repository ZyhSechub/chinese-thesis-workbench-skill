# AI 协作提示词模板

所有提示词默认先读取：

1. `standard-profile.yaml`
2. `thesis-ai-spec.yaml`
3. `figure-registry.yaml`
4. `paper-context/evidence/` 中的证据索引
5. 当前章节正文和证据材料

如果学校模板与本套件默认规则冲突，必须以学校模板为准。

## 1. 论文结构检查

```text
请读取 standard-profile.yaml、thesis-ai-spec.yaml 和当前论文目录，检查章节层级是否符合该论文类型。

输出：
1. 学校模板中必须保留的结构
2. 缺失章节
3. 章节顺序问题
4. 小节命名不一致问题
5. 需要新增、合并或删除的章节
6. 需要新增或调整的图表、公式、表格

要求：
- 只基于已提供材料，不要编造学校要求。
- 如果论文类型不明确，先列出可判断依据和需要确认的信息。
```

## 1.5 程序证据抽取

```text
请先检查项目中是否已有 paper-context/evidence/。
如果没有，请运行 chinese-thesis-workbench 的 scripts/evidence/build_project_evidence.py。

然后读取：
- project-evidence.json
- code-structure.md
- tech-stack.md
- api-list.md
- database-schema.md
- test-results.md

输出：
1. 可用于论文的真实技术栈
2. 可用于架构图的模块边界
3. 可用于数据库设计的表/实体线索
4. 可用于接口说明的 API 线索
5. 可用于测试章节的证据
6. 仍需人工确认的源码事实

要求：脚本扫描结果只是索引，重要结论必须回看源码或用户材料确认。
```

## 2. 标准配置检查

```text
请读取 standard-profile.yaml，检查论文规范来源是否完整。

重点检查：
1. 是否填写学校模板来源
2. 是否填写参考文献标准版本
3. 是否明确学校规则优先于通用默认规则
4. 是否存在“未确认却被当成硬规则”的项目
5. 是否存在可能影响 Word/PDF 排版的高风险项

输出：
- 已确认规则
- 待确认规则
- 可用默认规则
- 不应自动修改的格式项
```

## 3. 图表规范检查

```text
请读取 figure-registry.yaml，检查每张图、表、公式是否满足：
1. 编号连续
2. 标题明确
3. 有正文引用位置
4. 有源文件、截图来源或数据来源
5. 类型正确
6. 与章节内容匹配
7. 不含隐私、调试脏数据或无关截图内容

输出可执行修改建议，并按 critical / major / minor 分级。
```

## 4. 单章改写

```text
请基于以下材料改写第X章：
- standard-profile.yaml
- thesis-ai-spec.yaml
- chapter-section-template.md
- 本章已有正文
- 本章相关图表、公式、表格
- 本章证据材料

要求：
1. 保留真实事实。
2. 改善论文语体和逻辑衔接。
3. 不新增无证据结论。
4. 不改变学校格式要求。
5. 图表必须先解释再出现。
6. 不出现“根据用户提供材料”“通过分析代码”等 AI 工作流表述。

输出：
- 改写正文
- 修改说明
- 证据不足清单
- 需要人工确认的问题
```

## 5. 图表生成说明

```text
请根据以下输入生成可编辑图：
- 图编号：
- 图题：
- 图类型：
- 参与角色、模块、实体、变量或步骤：
- 节点关系：
- 数据流、业务流、调用顺序或研究流程：
- 所属章节：
- 证据来源：

要求：
1. 使用简洁中文标签。
2. 架构图、流程图、时序图、ER 图、模型图必须可编辑。
3. 不使用装饰性图标、复杂渐变和长段落节点。
4. 图中术语必须与正文一致。
5. 输出 draw.io XML 或 Mermaid 初稿，并说明每个节点的证据来源。
6. 证据不足时先列缺失材料，不要补造节点。
```

## 6. 终稿审查

```text
请按 ai-review-rubric.json 对论文进行终稿审查。

重点检查：
1. 学校规则优先级
2. 结构完整性
3. 章节逻辑
4. 图表与公式规范
5. 证据链
6. 参考文献闭环
7. 测试、实验或分析结果可信度
8. 学术诚信风险
9. 是否出现 AI 工作流痕迹

输出：
- 总体评分
- critical 问题
- major 问题
- minor 问题
- 建议修改顺序
- 必须人工复核的 Word/PDF 排版项
```

## 7. 文献交叉引用闭环

```text
请读取：
- paper-context/literature/reference-extraction.json
- paper-context/literature/citation-crossrefs.md
- thesis-ai-standard/templates/citation-crossref-register.yaml
- 当前正文引用位置
- 当前参考文献列表

输出：
1. 正文已有引用与文末条目的对应表
2. 文末条目但正文未引用的问题
3. 正文引用但文末缺条目的问题
4. PDF 抽取候选但尚未核验的文献
5. 与章节论点弱相关或不应引用的文献
6. 需要补充核验的作者、年份、题名、来源、DOI 或 URL

要求：候选文献不能直接当作最终参考文献；必须标注 verified / needs_check / rejected。
```

## 8. 论文资料包自检

```text
请运行 chinese-thesis-workbench 的 scripts/workspace/check_thesis_workspace.py 检查 thesis-ai-standard。

然后根据报告输出：
1. 缺失文件
2. 解析失败文件
3. 仍是占位内容的关键字段
4. 可以继续写作的部分
5. 必须先补齐的材料
```

## 9. AIGC 风格风险报告

```text
Use $chinese-thesis-workbench，请读取当前章节草稿，运行 AIGC style-governance 模块。

要求：
1. 先输出风格风险报告，不要直接改写。
2. 按段落列出命中的公式化表达、模糊归因、空泛结论、枚举过密、节奏重复等问题。
3. 标注 high / medium / low 风险。
4. 单独列出 needs_source 和 needs_evidence。
5. 给出建议修改顺序。

注意：目标是提升学术写作质量，不承诺规避任何检测器。
```

## 10. 基于报告定向改写

```text
请基于 aigc-style-report.md 和 aigc-style-review.yaml 只修改高风险段落。

要求：
1. 保留原有事实、数据、引用和论文观点。
2. 不新增未核验来源、实验、项目事实或 DOI。
3. 删除空泛评价句，改为具体结论、限制或后续工作。
4. 模糊归因必须补真实来源或标注 needs_source。
5. 输出改写正文、关键改动说明、仍需补证据清单。
```

## 11. 论文工作台进度更新

```text
Use $chinese-thesis-workbench，请读取 paper-context/workflow/ 下的 workflow-status.md、step-plan.md、progress-log.md、evidence-gaps.md、chapter-progress.md 和 revision-log.md。

请输出：
1. 当前论文执行到哪一步
2. 已完成事项
3. 正在进行事项
4. 阻塞事项和缺失材料
5. 下一步 3 个动作

然后更新对应 markdown 文件，保持状态一致。
```

## 12. Word 批注读取与修订

```text
Use $chinese-thesis-workbench，请先运行 scripts/docx/extract_docx_comments.py 读取 Word 文档批注，生成 paper-context/word-comments/word-comment-todos.md。

然后：
1. 按批注类型分组：内容、结构、引用、格式、图表、证据不足。
2. 对每条批注给出处理策略：resolved / blocked / skipped。
3. 能直接修改的批注，按 chinese-thesis-workbench DOCX 规则修改 Word 文档。
4. 需要新增事实、数据或引用的批注，不要编造，标注 needs_evidence 或 needs_source。
5. 修改后更新 docx-revision-log.md 和 paper-context/workflow/revision-log.md。
6. 输出已解决批注、未解决批注、修改后的文档路径和需要人工复核的内容。
```
