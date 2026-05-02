# DOCX Formatter Prompt

用于将论文源稿转成 `.docx`。

默认样式：

- 摘要、Abstract、参考文献、致谢标题居中
- 摘要与 Abstract 各自独立分页
- 一级标题分页开始
- 中文正文宋体
- 英文正文 Times New Roman
- 中文关键词单独成段，顶格，不首行缩进，“关键词：”标签黑体小四加粗，内容宋体小四
- 中英文摘要正文除关键词行外，保持正常首行缩进 2 字符
- 英文摘要正文 Times New Roman 小四
- 英文关键词单独成段，顶格，不首行缩进，`Keywords:` 标签加粗且为 Times New Roman 小四，内容为 Times New Roman 小四
- 图题、表题均使用单倍行距，段前段后为 0
- 参考文献悬挂缩进

必须优先让生成脚本真实实现这些规则，而不是只在说明里写规则。

如果存在截图或渲染图，优先嵌入真实图片。

生成时优先使用：

- `python scripts/docx/generate_thesis_docx.py thesis.md thesis.docx --style-profile paper-context/workflow/style-profile.json --image-map image-map.json`

导出前必须确认正文已经清理掉 Markdown 痕迹，例如：

- `**加粗**`
- `` `code` ``
- `[链接文字](https://example.com)`

这些都不能原样进入最终 `.docx`。
