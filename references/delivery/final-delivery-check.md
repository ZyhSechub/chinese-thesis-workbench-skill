# Final Checker Prompt

交付前必须逐项检查：

1. 章节完整
2. 字数接近样文目标，优先核对 `python scripts/review/count_chapter_words.py <thesis.md>` 的 `APPROX_WORDS`
3. 参考文献比例符合要求
4. 图表编号连续
5. 是否残留占位符
6. `.docx` 是否真实存在
7. 摘要 / Abstract / 参考文献 / 致谢样式是否正确
8. 英文字体是否正确
9. 图表是否真实插入
10. 最终正文是否还残留 `**`、反引号或 Markdown 链接
11. 主论文文件名是否使用论文标题
12. 附件 `.docx` 是否真实存在
13. 第 4 章或“系统详细设计与实现”是否为全文最长章节或接近最长章节
14. 第 4 章每个主要模块是否包含截图
15. 第 4 章每个主要模块是否包含简要核心代码
16. 数据库部分是否包含 E-R 图
17. 第 3 章设计图数量是否达到 5 张及以上
18. E-R 图是否在需要时拆分为总表图和核心表图
19. 是否生成 `references-verified.json` 或等价文献核验清单
20. 文献是否全部在目标时间范围内
21. 是否混入了低可信旧说明文档中的事实
22. 页面截图总数是否达到 6 张及以上

最终检查时，必须至少执行：

- `python scripts/review/count_chapter_words.py <thesis.md>`
- `python scripts/figures/ensure_thesis_assets.py <thesis.md> --check-only`
- 如果存在截图占位，还必须确认 `image-map.json` 已由 `python scripts/screenshots/capture_thesis_screenshots.py <plan.json>` 生成
- 如果存在 Mermaid / PlantUML 图，还必须确认附件 `.docx` 已生成
- 还必须确认文献核验清单文件已生成
