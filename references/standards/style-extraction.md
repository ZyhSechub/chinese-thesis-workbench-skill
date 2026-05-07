# Style Observation Prompt

用于轻量观察模板或样文的版式特征。观察结果只进入样文/模板分析报告、目录确认和字数预算，不直接驱动 DOCX 排版。

优先关注：

- 目录层级
- 章级或节级字数
- 图、表、公式、代码出现节奏
- 一级、二级、三级标题的可见样式
- 正文、摘要、Abstract、关键词的可见样式
- 图题、表题、表格内容的可见样式
- 参考文献、致谢、附录的可见组织方式
- 是否分页、是否居中、字体字号、段前段后、行距、首行缩进等观察项

输出时必须区分：

1. 已观察到的样文模式
2. 不能确认的字段
3. 需要用户或学校规范确认的项目
4. 可用于建议目录或字数预算的依据

如果样文是 `.docx`，可以执行：

```powershell
python scripts/docx/analyze_docx.py <sample.docx> --json-out paper-context/workflow/sample-docx-analysis.json
```

后续生成 `.docx` 时仍使用内置默认格式。不要把解析 JSON 当成 Word 样式配置传给生成器，也不要承诺自动复刻学校模板。
