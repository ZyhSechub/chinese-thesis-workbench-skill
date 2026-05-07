# Sample And Template Analysis

用于把学校模板、往届样文、PDF/Word 解析结果转换为可进入工作流决策的中间层。

模块六只负责“分析结果治理”和“用户可读输出”，不负责学校 DOCX 模板复刻。PDF 和 Word 解析脚本提供轻量 JSON：目录结构、章级字数、版式观察、图表节奏、标题或表格候选；如果解析脚本输出较弱，仍可基于可用字段生成带限制说明的报告，不把解析脚本能力不足伪装成已确认规则。

## Source Priority

按来源优先级区分结果：

1. `template_rules`：学校模板、学院规范、导师要求中可确认的规则。它们优先于样文。
2. `sample_patterns`：往届样文中观察到的结构、节奏和表达习惯。它们只能作为参考。
3. `recommendations`：结合当前论文类型、学校规则和样文模式得到的建议。它们必须等待用户确认后才能进入正式目录或字数预算。

## Parser Boundary

解析器只提供输入，不直接决定论文结构或 DOCX 排版。

- 可接受输入：`analyze_docx.py` 输出、`analyze_sample_pdf.py` 输出、手工整理的样文摘要、模板规则摘录、用户提供的目录截图或文本。
- 当解析字段缺失时，报告中标记为 `unparsed` 或 `needs_confirmation`。
- 不得因为解析脚本猜到了标题或字数，就声称学校规则已确认。

## Unified Analysis Schema

分析结果建议统一归并为这些字段：

```yaml
source:
  path: ""
  source_type: "school_template | sample_docx | sample_pdf | manual_note"
  parser: ""
  parser_status: "parsed | partial | failed | manual"
  limitations: []
template_rules:
  confirmed: []
  needs_confirmation: []
sample_patterns:
  outline_structure: []
  chapter_word_distribution: []
  figure_table_rhythm: []
  style_observations: []
recommendations:
  outline_suggestion: []
  word_budget: []
  user_decisions_needed: []
confidence:
  structure: "high | medium | low"
  word_count: "high | medium | low"
  style: "high | medium | low"
```

## Required User-Facing Output

模块六优先生成一个综合输出，减少重复文件：

`sample-template-analysis.md` 必须包含：

- 已解析来源、解析状态、可确认规则、样文模式、未解析项和待确认项。
- `Outline Suggestion` 章节：只给建议目录，不直接覆盖 `thesis-ai-spec.yaml`；每个章节建议都标明来源。
- `Word Budget` 章节：给出章节级字数预算；每个预算项都标明来源和置信度；如果缺少总字数要求，预算只能标记为 provisional。

## What To Extract When Available

从样文/模板输入中尽量提取：

- 目录层级
- 章级或节级字数
- 图、表、代码或公式出现节奏
- 摘要、Abstract、参考文献、致谢是否独立成节或分页
- 标题、正文、摘要、关键词、图题、表题的样式观察
- 样文中可参考但不可硬套的语言节奏

## Output Rules

- 学校模板和导师要求优先于样文。
- 样文模式不得直接写入正式正文；只能影响建议目录、字数预算和风格提示。
- 样文或模板解析结果不得直接驱动 `generate_thesis_docx.py` 的格式；DOCX 交付使用内置默认格式。
- 解析失败或字段缺失时，不阻断 intake、standards 或 evidence；只限制目录确认和格式声明。
- 如果用户同时给了多个样文，比较共同结构与差异，并说明推荐采用哪一套目录节奏及原因。
- 输出完成后，更新或提示更新 `user-dashboard.md`、`content-decisions.md` 和 `sample-template-analysis.md`。
