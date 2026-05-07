# chinese-thesis-workbench

> 以标准和证据为骨架，以四种 DOCX 交付路径为输出，把项目源码、学校模板、往届样文、文献和截图整合成可追溯、可续写、可检查的中文本科论文交付工作台。

[![Skill Type](https://img.shields.io/badge/Codex-Skill-blue)](https://codex.claude.ai)
[![Language](https://img.shields.io/badge/Language-中文-red)]()

---

## 定位

**chinese-thesis-workbench** 不是一键生成论文的工具。它是一套论文标准化交付工作台，把毕业论文拆成可审查、可回退的步骤——收集材料 → 选择交付路径 → 构建证据 → 确认大纲 → 分章写作 → 生成/填充/编辑 DOCX → 质量检查。

核心原则：**能复制/编辑就保留原 DOCX 格式，不能复制时再生成结构清晰的默认格式文档**。

### 适合

- 有真实项目（软件系统、实验、调研等）需要写成毕业论文的学生
- 需要控制章节字数、管理图表截图、核验参考文献的用户
- 需要严格匹配学校模板格式的用户
- 导师批注后需要系统化修订、且不能丢失已有排版格式的用户
- 素材不足、需要联网检索同领域文献或头脑风暴写作思路的用户

### 不适合

- 没有真实项目或数据、希望凭空生成论文的用户
- 纯文科论文可参考流程但需重配证据链

---

## 四种 DOCX 交付路径

v1.0.0 起提供四种路径，用户 intake 阶段选择并记录到 `user-decisions.md`：

| 路径            | 输入                                  | 输出          | 格式策略                                |
| ------------- | ----------------------------------- | ----------- | ----------------------------------- |
| **M1** 默认样式生成 | Markdown                            | 全新 `.docx`  | 内置默认格式（宋体小四正文、黑体标题）                 |
| **M2** 样文版式贴近 | Markdown + 样文分析 JSON                | 全新 `.docx`  | 从样文提取高置信度字号/字体/缩进，deep_merge 进默认值   |
| **M3** 模板副本填充 | Markdown + 学校模板 `.docx` + spec YAML | 模板副本被填充     | 复制模板 OOXML 底座，仅替换占位文本 + 插入章节正文，不动样式 |
| **M4** 已有稿编辑  | 初稿 `.docx` + 编辑指令                   | 同一份 `.docx` | 只改段落文本，不动 pPr/rPr/sectPr/批注         |

**M3 是格式要求严格的学校的推荐路径**——它复制模板后只做文本替换和插入，模板的 styles.xml、页眉页脚、分节符全部原封不动。M2 是轻量近似，不承诺模板复刻。

---

## 快速开始

```powershell
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 初始化论文工作区
python scripts/workspace/init_thesis_workspace.py <你的论文项目目录>

# 3. 编辑模板
#    <项目目录>/thesis-ai-standard/templates/standard-profile.yaml

# 4. 在 Claude Code 中加载本 skill，告诉 AI：
#    "帮我把这个项目整理成一篇结构完整的毕业论文"
```

### M3 学校模板副本填充

```powershell
# 先用 analyze_docx.py 分析模板结构（可选但推荐）
python scripts/docx/analyze_docx.py 学校模板.docx --json-out result.json

# 从 markdown 论文 + 学校模板生成填充好的 docx
python scripts/docx/apply_textual_edits.py --from-template 学校模板.docx \
  --thesis-md paper-output/<论文标题>.md \
  --spec thesis-ai-standard/templates/thesis-ai-spec.yaml \
  --out paper-output/<论文标题>.docx
```

模板原文件不被修改。输出报告 `paper-output/<论文标题>-template-fill-report.md` 列出已替换的占位、未匹配字段和章节插入位置。

### M2 样文版式贴近

```powershell
python scripts/docx/analyze_docx.py 样文.docx --json-out paper-context/workflow/sample-docx-analysis.json
python scripts/docx/generate_thesis_docx.py thesis.md output/thesis.docx \
  --sample-analysis paper-context/workflow/sample-docx-analysis.json
```

高置信度（sample_count ≥ 3）的样式值会被合并进默认 profile。低频出现但高置信的类别（如标题、摘要标题）降为 sample_count ≥ 1 即可采用。

### M4 已有初稿编辑

```powershell
python scripts/docx/apply_textual_edits.py draft.docx draft-edited.docx \
  --replace "原文锚点" "新文本" \
  --insert-after "锚点段落" "新增段落" \
  --delete "要删除的段落锚点"
```

只改段落文本，不重建样式。锚点命中 0 次或多于 1 次时报错退出。

### 样文/模板分析（所有路径通用）

```powershell
python scripts/docx/analyze_docx.py 学校模板.docx --json-out result.json
python scripts/workspace/build_sample_template_outputs.py result.json --target <项目目录>
```

---

## 核心能力

### 标准与证据

| 能力        | 说明                                 |
| --------- | ---------------------------------- |
| 材料摄入      | 按必需/建议/可选分级，说明缺失影响和是否可继续           |
| 项目证据提取    | 按论文类型从源码、数据库、API、测试、实验数据中生成证据索引    |
| 文献治理      | PDF 参考文献抽取 → 候选池 → 核验 → 格式化 → 核验清单 |
| 素材稀缺处置    | 素材不足时征得用户同意，联网检索同领域文献或头脑风暴写作思路     |
| AIGC 风格治理 | 减少空泛表达，不伪造事实                       |
| Word 批注修订 | 抽取导师批注，逐条修订并记录变更日志                 |

### 论文成稿

| 能力      | 说明                                                   |
| ------- | ---------------------------------------------------- |
| 样文分析    | 提取往届样文的目录结构、章级字数、图表节奏和段落样式                           |
| 模板分析    | 提取学校模板的页面设置、样式定义和段落格式特征                              |
| 章节控字    | 写作前定预算，写完统计，超出自动压缩                                   |
| 图表      | 支持 Mermaid / PlantUML / draw.io 三种图源；Playwright 自动截图 |
| DOCX 成稿 | 四种交付路径：默认生成 / 样文贴近 / 模板填充 / 初稿编辑                     |
| 模板填充报告  | M3 输出已替换占位、未匹配字段、章节配对方法、需人工核对项                       |
| 公式      | 支持 LaTeX 文本保留或图片插入两种模式                               |
| 文件命名    | 所有交付物使用论文标题命名                                        |

### 用户可见性

工作流初始化后在 `paper-context/workflow/` 下生成五类控制文件：

| 文件                      | 作用                       |
| ----------------------- | ------------------------ |
| `user-dashboard.md`     | 当前进度、待确认事项、下一步建议         |
| `material-inventory.md` | 材料等级、缺失影响、是否可继续          |
| `content-decisions.md`  | 候选内容的取舍：正文重点/简写/附录/暂缓/不写 |
| `blocker-report.md`     | 阻断原因、影响范围、可选路径、是否可有限继续   |
| `user-decisions.md`     | 用户已确认的关键选择归档（含交付路径选择）    |

详细规则和工作流见 [SKILL.md](SKILL.md)。

### 素材稀缺与头脑风暴

当材料摄入后发现素材过少（两个以上必需材料缺失、文献池为空、或证据仅停留在 README 级别），工作台不会直接阻断，而是走 `material-gap-handoff` 流程：

1. **联网检索**：征得用户同意后，检索近五年同领域文献，写入 `paper-context/literature/web-suggested.md`（标记 `needs_check`），不直接加入参考文献。
2. **头脑风暴**：征得用户同意后启动头脑风暴，写作思路只写入 `content-decisions.md` 的候选区，供用户审批取舍。
3. 用户确认的进入大纲和正文；拒绝的标记 `discarded`，论文正文、spec、图表注册表都不会引用。
4. 用户拒绝联网检索和头脑风暴的，记录到 `blocker-report.md`，在可见限制下继续推进。

---

## 架构

```
治理侧 paper-context/
  workflow/         用户仪表盘、材料清单、内容取舍、阻断报告、用户决策、进度日志
  evidence/         项目证据、技术栈、数据库 Schema、API 列表
  literature/       参考文献抽取、交叉引用、联网检索建议
  standards/        标准解析、样式提取
  aigc/             AIGC 风格报告
  word-comments/    导师批注待办和修订记录

交付侧 paper-output/
  <论文标题>.md                       Markdown 源稿
  <论文标题>.docx                     主论文（默认格式 / 样文贴近 / 模板填充）
  <论文标题>-附件.docx               附件（图源码等）
  <论文标题>-template-fill-report.md 模板填充报告（仅 M3）
  <论文标题>-image-map.json          图片映射
  <论文标题>-文献核验清单.json       参考文献核验
  figures/                            图表
  screenshots/                        截图
```

---

## 目录

```
chinese-thesis-workbench/
  SKILL.md                  Skill 路由入口
  README.md                 本文件
  requirements.txt          Python 依赖
  package.json              Node.js 依赖（截图）

  references/              按需加载的参考文档
    workflow/              工作流、状态管理、阻断、质量门禁、素材稀缺交接
    standards/             标准解析、样式提取、默认格式
    evidence/              源码证据、文献治理、事实提取
    writing/               样文分析、章节写作、参考文献选择、AIGC 治理
    delivery/              DOCX 成稿（含四种路径）、最终检查、Word 批注修订

  scripts/                 可执行脚本
    workspace/             工作区初始化、工作流日志、分析结果归并
    evidence/              项目证据构建
    literature/            PDF 参考文献抽取、交叉引用、候选池
    docx/                  DOCX 分析、生成、模板填充、文本编辑、批注抽取
    figures/               Mermaid 渲染、图表资产检查、图片映射
    screenshots/           截图占位提取、截图计划、浏览器截图
    review/                章节字数统计、AIGC 风格分析

  assets/thesis-ai-standard/
    templates/             结构化配置模板（YAML）
    drawio/                图表模板（6 张）

  tests/                   核心合约测试（9 个）
```

---

## 与上一版本（v0.1.0）的比较

### 功能差异

| 功能                     | v0.1.0               | v1.0.0                                   |
| ---------------------- | -------------------- | ---------------------------------------- |
| DOCX 生成                | 仅默认样式                | 四种路径（M1/M2/M3/M4）                        |
| 学校模板处理                 | 只能分析，格式靠用户手动贴        | M3 复制模板底座直接填充文本                          |
| 样文样式利用                 | 分析后不进生成器             | M2 `--sample-analysis` 直通生成器             |
| 已有初稿编辑                 | 不支持                  | M4 `--replace/--insert/--delete`         |
| 素材稀缺场景                 | `stop_and_report` 阻断 | 可征得同意后联网检索 / 头脑风暴                        |
| `load_style_profile()` | 无参数，只返回默认值           | 可选 `sample_analysis` 参数，deep_merge 高置信样式 |
| 测试数量                   | 5 个                  | 9 个                                      |

### 改动范围

- **新增** `scripts/docx/apply_textual_edits.py`（466 行）—— M3 + M4 文本编辑内核
- **新增** `references/workflow/material-gap-handoff.md`（9 行）—— 素材稀缺流程
- **修改** `scripts/docx/generate_thesis_docx.py` —— 新增 `sample_style_override` + `--sample-analysis` 参数
- **修改** `SKILL.md` —— 4 处更新（交付路径、格式例外、硬规则、资源映射）
- **修改** `references/workflow/intake.md` —— 新增四选一交付路径问题
- **修改** `references/delivery/docx-delivery.md` —— 四种模式说明和命令示例
- **修改** `references/delivery/word-comment-revision-workflow.md` —— 追加 M4 文本编辑模式一节
- **修改** `tests/test_core_contracts.py` —— 新增 4 个测试

### 向后兼容

- M1 默认路径代码零改动，`build_doc()` 一行未变
- `load_style_profile()` 无参调用行为与 v2.x 完全一致
- v2.x 所有 5 个测试在新版中全部通过
- 无新增 Python 依赖（`pyyaml` 已在 requirements.txt 中）

---

## 依赖

| 包                      | 用途            |
| ---------------------- | ------------- |
| `python-docx`          | DOCX 生成、分析、编辑 |
| `PyYAML`               | YAML 配置读写     |
| `pypdf` / `pdfplumber` | PDF 解析        |

Node.js 和 Playwright 仅自动截图功能需要：

```powershell
npm install && npm run install:browsers
```

---

## 验证

```powershell
# Python 编译检查
python -m compileall scripts tests

# 单元测试（当前 9 个）
python -m unittest discover tests

# 工作区模板校验
python scripts/workspace/check_thesis_workspace.py assets/thesis-ai-standard
```

---

## 参考项目

本 skill 参考了以下两个项目：

| skill                        | 角色                                               |
| ---------------------------- | ------------------------------------------------ |
| **xiaou61/thesis-skills**    | 标准与证据骨架：标准解析、证据构建、质量门禁、AIGC 治理、Word 批注、状态管理      |
| **Doryoku1223/lunwen-skill** | 中文论文成稿引擎：样文分析、章节控字、图表截图、Mermaid/PlantUML、DOCX 成稿 |

---

## 许可

MIT License

---

## 致谢

- **[xiaou61/thesis-skills](https://github.com/xiaou61/thesis-skills)** — 提供标准与证据骨架
- **[Doryoku1223/lunwen-skill](https://github.com/Doryoku1223/lunwen-skill)** — 提供中文论文成稿引擎

感谢两个项目的作者为中文毕业论文标准化写作做出的贡献。
