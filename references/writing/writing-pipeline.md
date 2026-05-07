# Chapter Writer Prompt

用于按样文章节节奏写作。样文节奏是参考，不得覆盖学校/导师要求、证据链和当前论文类型。

要求：

- 先看样文对应章节字数
- 控制当前章节篇幅
- 语言风格贴近本科论文样文，但避免机械套用样文结构
- 软件系统/系统设计类论文中，第 4 章或“系统详细设计与实现”通常是全文最长章节；其他论文类型按研究问题和学校要求安排篇幅
- 软件系统/系统设计类论文的实现章节可按“模块说明 -> 流程图/结构图 -> 关键实现 -> 页面截图”展开
- 软件系统/系统设计类论文的主要模块建议提供页面截图、核心代码、SQL 或关键实现片段；非软件类论文使用实验、调研、文本分析或数据材料替代
- 系统设计类论文可在设计章放置架构图、流程图、数据模型图等；图数量由证据和学校要求决定，不设固定张数
- 只有涉及数据库设计的系统设计类论文才要求 E-R 图或等价数据设计证据
- 如果任务书要求与源码实现不一致，正文必须优先按源码事实写，并在相关段落中保持口径一致
- 写完立即统计字数，优先使用 `python scripts/review/count_chapter_words.py <thesis.md>`
- 超出就压缩
- 不能残留 `**`、反引号、Markdown 链接等标记
- 如果软件系统/系统设计类正文缺少架构图、E-R 图、关键流程图、数据表、测试用例表或页面截图占位，执行
  `python scripts/figures/ensure_thesis_assets.py <thesis.md> --check-only`
  并在继续写作前确认缺失项是否确实由当前论文范围需要
- 数据库设计部分只有在论文实际包含数据库设计时才要求 E-R 图或等价数据设计证据
- 页面截图数量不设通用下限；按系统功能、论文范围和学校要求决定
- 参考文献必须先核验后回填，不能边猜边写
- 文风应贴近本科论文样文，但避免空泛套话和机械排比
- 如果正文存在截图占位，优先执行：
  `python scripts/screenshots/extract_screenshot_placeholders.py <thesis.md> --json-out labels.json`
  `python scripts/screenshots/build_screenshot_plan.py labels.json paper-context/workflow/screenshot-plan.json --base-url <system-url>`
  `python scripts/screenshots/capture_thesis_screenshots.py paper-context/workflow/screenshot-plan.json`
- 如果正文存在 Mermaid / PlantUML 图，完成主文稿后必须额外生成附件 `.docx`，收录这些图的源码版本
