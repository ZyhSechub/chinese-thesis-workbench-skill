# Chapter Writer Prompt

用于按样文章节节奏写作。

要求：

- 先看样文对应章节字数
- 控制当前章节篇幅
- 语言风格贴近本科软件类论文
- 第 4 章或“系统详细设计与实现”默认必须是全文最长章节
- 系统详细设计与实现默认按“模块说明 -> 流程图/结构图 -> 关键实现 -> 页面截图”展开
- 系统详细设计与实现中的每个主要模块至少包含 1 张页面截图
- 系统详细设计与实现中的每个主要模块至少包含 1 段简要核心代码、SQL 或关键实现片段
- 第 3 章默认至少包含 5 张设计图
- 第 3 章数据库设计默认至少包含“总表设计图 + 核心表设计图”两张 E-R 图；如果总图过大，必须拆分
- 如果任务书要求与源码实现不一致，正文必须优先按源码事实写，并在相关段落中保持口径一致
- 写完立即统计字数，优先使用 `python scripts/review/count_chapter_words.py <thesis.md>`
- 超出就压缩
- 不能残留 `**`、反引号、Markdown 链接等标记
- 如果正文缺少架构图、E-R 图、关键流程图、数据表、测试用例表或页面截图占位，必须执行
  `python scripts/figures/ensure_thesis_assets.py <thesis.md> --check-only`
  并在继续写作前补齐缺失项
- 数据库设计部分必须出现 E-R 图
- 若页面截图总数少于 6 张，默认继续补图，不得直接交付
- 参考文献必须先核验后回填，不能边猜边写
- 文风应贴近本科论文样文，但避免空泛套话和机械排比
- 如果正文存在截图占位，优先执行：
  `python scripts/screenshots/extract_screenshot_placeholders.py <thesis.md> --json-out labels.json`
  `python scripts/screenshots/build_screenshot_plan.py labels.json paper-context/workflow/screenshot-plan.json --base-url <system-url>`
  `python scripts/screenshots/capture_thesis_screenshots.py paper-context/workflow/screenshot-plan.json`
- 如果正文存在 Mermaid / PlantUML 图，完成主文稿后必须额外生成附件 `.docx`，收录这些图的源码版本
