# Final Delivery Check

交付前逐项检查：

1. 章节结构完整，标题层级连续。
2. 字数接近已确认目标；优先核对 `python scripts/review/count_chapter_words.py <thesis.md>` 的 `APPROX_WORDS`。
3. 参考文献数量、年份范围和格式符合已确认要求。
4. 图、表、公式编号连续，正文有首次引用。
5. 没有残留占位符、待补说明或未处理批注。
6. 主 `.docx` 真实存在，文件名使用论文题目或用户确认的交付名。
7. 摘要、Abstract、目录、参考文献、致谢、附录等关键部分存在且样式一致。
8. 中英文和数字字体无明显混乱。
9. 图表和公式素材已真实插入，或明确保留为可复制的文本/占位。
10. 最终正文没有残留 `**`、反引号、裸 Markdown 链接等排版痕迹。
11. 如果需要附件 `.docx`，确认附件真实存在。
12. 已生成或更新文献核验清单，例如 `references-verified.json` 或等价记录。
13. 没有混入低可信旧说明文档中的事实。

软件系统、系统设计或数据库设计类论文还需要检查：

1. 实现/设计章节是否覆盖主要模块，而不是只堆技术介绍。
2. 主要模块是否绑定真实项目证据，例如代码路径、接口、SQL、运行截图、测试记录或等价材料。
3. 数据库内容是否在需要时提供 E-R 图、表结构或实体关系说明。
4. 页面截图数量是否与功能范围匹配；不设置通用下限。
5. 设计图数量是否与章节论证需要匹配；不设置通用下限。
6. 如果存在截图占位，确认 `image-map.json` 已生成或用户已提供对应图片。
7. 如果存在 Mermaid / PlantUML 图，确认附件 `.docx` 已生成并收录源码。

最低验证命令：

```powershell
python scripts/review/count_chapter_words.py <thesis.md>
python scripts/figures/ensure_thesis_assets.py <thesis.md> --check-only
```
