# DOCX Delivery

用于将论文源稿转成 `.docx`。核心原则是：生成一份结构清晰、素材完整、可复制粘贴的默认格式 Word 文档，不复刻各学校的 Word 模板。

## Supported Scope

默认 DOCX 只负责内置格式：

- 题目
- 摘要 / Abstract
- 关键词 / Keywords
- 目录标题或目录占位
- 一级、二级、三级标题
- 正文
- 图题、表题
- 表格
- 公式
- 参考文献
- 致谢
- 附录
- 代码块
- 缺失素材占位

如果学校要求严格模板格式，交付时告知用户：先用本工具生成内容完整的 DOCX，再由用户复制粘贴到学校官方模板中做最终排版。

## Default Command

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --image-map image-map.json
```

公式默认保留为 LaTeX 文本，便于用户后续手动转 Word 公式：

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --formula-mode latex_text
```

如果用户已经提供渲染好的公式图片，并在 image map 中用公式文本作为 key，可以选择图片模式：

```powershell
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx --image-map image-map.json --formula-mode formula_image
```

生成器不提供学校模板匹配参数。即使用户提供学校模板，也不应承诺自动匹配学校模板格式。

## Asset Rules

- 截图、图表和公式图片通过 image map 插入。
- Markdown 表格应尽量转成 Word 表格。
- 无法解析为表格时，保留文本或明确占位，不能静默丢失。
- Mermaid / PlantUML / draw.io 源码仍进入附件 DOCX。

## Markdown Cleanup

导出前必须确认正文已经清理掉 Markdown 痕迹，例如：

- `**加粗**`
- `` `code` ``
- `[链接文字](https://example.com)`

这些不能原样进入最终 `.docx`，但 LaTeX 公式源码在 `latex_text` 模式下可以保留。
