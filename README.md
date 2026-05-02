# chinese-thesis-workbench

> 以标准和证据为骨架，以中文论文成稿流水线为输出层，把项目源码、学校模板、样文、文献、截图和 Word 成稿整合成可追溯、可续写、可检查的本科论文交付工作台。

[![Skill Type](https://img.shields.io/badge/Codex-Skill-blue)](https://codex.claude.ai)
[![Language](https://img.shields.io/badge/Language-中文-red)]()

---

## 目录

- [定位](#定位)
- [核心能力](#核心能力)
- [架构](#架构)
- [目录结构](#目录结构)
- [快速开始](#快速开始)
- [完整工作流](#完整工作流)
- [状态模型](#状态模型)
- [硬约束规则](#硬约束规则)
- [交付物](#交付物)
- [依赖安装](#依赖安装)
- [验证](#验证)
- [合并来源](#合并来源)
- [许可](#许可)

---

## 定位

**chinese-thesis-workbench** 不是一个"一键生成论文"的工具。它是一套**论文标准化交付工作台**，把本科毕业论文（毕业设计）的撰写过程拆解为可审查、可回退、可验证的工程链路：

```
学校标准 → 项目证据 → 论文事实 → 图表登记 → 样文仿写 → 正文生成 → DOCX 交付 → 质量门禁
```

### 它适合谁

- 需要把真实软件项目（网站、小程序、管理系统、物联网平台等）写成毕业设计论文的开发者
- 需要按学校模板和样文风格交付 `.docx` 成稿的学生
- 需要控制章节字数、管理图表截图、核验参考文献的论文写作者
- 导师批注后需要系统化修订的学生

### 它不适合谁

- 没有真实项目源码或实验数据、希望"凭空生成"论文的用户
- 不需要中文论文格式的非中文场景
- 纯文科论文（本工作台目前以理工科尤其是系统设计类论文为主）

---

## 核心能力

### 标准与证据治理

| 能力 | 说明 |
|------|------|
| 学校标准解析 | 学校模板、任务书、开题报告、导师要求的优先级排序与冲突处理 |
| 项目证据提取 | 从源码、数据库 Schema、API 路由、测试报告中自动生成证据索引 |
| 文献治理 | PDF 参考文献抽取、交叉引用索引、真实性核验清单生成 |
| AIGC 风格治理 | 报告式学术表达审查，降低模板化空泛表达，不伪造事实 |
| Word 批注修订 | 从导师批注的 `.docx` 中抽取评论，逐条修订并记录变更日志 |
| 质量门禁 | 7 道质量关卡：标准、证据、学术诚信、结构、AIGC、图表、脚本验证 |

### 中文论文成稿

| 能力 | 说明 |
|------|------|
| 样文分析 | 从往届样文/模板中提取目录结构、各章字数、版式样式、图表节奏 |
| 章节控字 | 写作前确定字数预算，写完一章统计一章，超出自动压缩 |
| 图表截图双轨 | 支持 Mermaid / PlantUML / draw.io 三种图表源，Playwright 自动截图 |
| DOCX 成稿 | 生成符合中文论文排版规范的 `.docx`，含附件 DOCX（图源码） |
| 文献闭环 | 建候选池 → 真实性核验 → 相关性筛选 → 格式化 → 生成核验清单 |
| 文件名规范 | 所有交付物使用论文标题命名，不出现 `final`、`draft`、`doc1` 等通用名 |

### 工作流状态管理

- 双层状态模型（阶段 × 状态）
- `stop_and_report` 全流程阻断机制：证据不足时停止并向用户报告缺失清单
- 合法回退规则：支持中途补材料后精确回退到对应阶段
- 持久化进度文件（`paper-context/workflow/`），中断后可恢复

---

## 架构

| 层级 | 模块 / 目录 | 说明 |
|---|---|---|
| 项目根目录 | `chinese-thesis-workbench` | 中文论文写作工作台 |
| 治理侧 | `paper-context/` | 论文上下文与项目背景材料 |
| 治理侧 | `workflow/` | 写作流程、任务拆分与执行记录 |
| 治理侧 | `evidence/` | 实验依据、数据证据、结果支撑材料 |
| 治理侧 | `literature/` | 文献资料、引用来源与阅读记录 |
| 治理侧 | `aigc/` | AIGC 使用记录、提示词与生成过程管理 |
| 治理侧 | `word-comments/` | Word 批注、修改建议与审阅记录 |
| 交付侧 | `paper-output/` | 最终论文交付文件目录 |
| 交付侧 | `论文标题.md` | Markdown 格式论文正文 |
| 交付侧 | `论文标题.docx` | Word 格式论文正文 |
| 交付侧 | `论文标题-附件.docx` | 附件材料 |
| 交付侧 | `论文标题-image-map.json` | 图片映射关系记录 |
| 交付侧 | `论文标题-文献核验清单.json` | 文献核验清单 |
| 交付侧 | `figures/` | 论文插图、流程图、结构图等 |
| 交付侧 | `screenshots/` | 系统截图、实验截图等 |
| 接口层（结构化配置） | `standard-profile.yaml` | 论文标准配置文件 |
| 接口层（结构化配置） | `thesis-ai-spec.yaml` | AI 辅助写作规范配置 |
| 接口层（结构化配置） | `figure-registry.yaml` | 图片注册与编号管理配置 |
| 接口层（结构化配置） | `thesis-ai-standard/templates/` | 论文模板与规范模板目录 |

**设计原则**：正文写作只能消费 `thesis-ai-spec.yaml`、`figure-registry.yaml` 和 `paper-context/evidence/` 中的结构化事实。不允许直接从 README、旧说明文档或猜测中扩写正文。

---

## 目录结构

```
chinese-thesis-workbench/
  SKILL.md                         # 路由入口
  README.md                        # 本文件
  agents/openai.yaml               # 中文论文专用 Agent 定义
  requirements.txt                 # Python 依赖
  package.json                     # Node.js 依赖（浏览器截图）

  references/                      # 按需加载的参考文档
    workflow/                      # 工作流、状态管理、阻断机制、质量门禁
    standards/                     # 标准解析、样式提取、默认格式
    evidence/                      # 源码证据、文献治理、事实提取
    writing/                       # 样文分析、章节写作、参考文献选择、AIGC 治理
    delivery/                      # DOCX 成稿、最终检查、Word 批注修订
    merge-map.md                   # 合并来源映射

  scripts/                         # 可执行脚本
    workspace/                     # 工作区初始化、工作流日志
    evidence/                      # 项目证据构建
    literature/                    # PDF 参考文献抽取、交叉引用、候选池
    docx/                          # DOCX 分析、生成、批注抽取
    figures/                       # Mermaid 渲染、图表资产检查、图片映射
    screenshots/                   # 截图占位提取、截图计划、浏览器截图
      browser/                     # Playwright 截图脚本
    review/                        # 章节字数统计、AIGC 风格分析

  assets/thesis-ai-standard/       # 论文标准化套件（原样继承）
    README.md
    01-本科论文标准化最佳实践.md
    02-公开标准与高校规范来源.md
    templates/                     # 结构化配置模板
    drawio/                        # draw.io 图表模板（6 张）
```

---

## 快速开始

### 前置条件

- Python 3.9+
- Node.js（仅截图功能需要）
- 可选：Playwright Chromium（`npm run install:browsers`）

### 安装依赖

```powershell
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖（如需浏览器截图）
npm install
npm run install:browsers
```

### 三步上手

**1. 初始化论文工作区**

```powershell
python scripts/workspace/init_thesis_workspace.py <你的论文项目目录>
```

这会在你的项目目录下创建 `thesis-ai-standard/` 和 `paper-context/workflow/`。

**2. 填写标准配置**

编辑 `<项目目录>/thesis-ai-standard/templates/standard-profile.yaml`，填入学校、导师、参考文献格式要求。

**3. 让 AI 接管**

在 Claude Code 中加载本 skill，然后告诉 AI：

> 帮我把这个项目整理成一篇符合学校模板和样文风格的毕业论文。

AI 会按 14 步工作流依次收集资料、解析标准、提取证据、分析样文、确认目录、分章写作、生成 DOCX。

---

## 完整工作流

```
 1. intake_materials         收集学校模板、任务书、样文、源码、截图、文献
 2. init_workspace           创建 thesis-ai-standard/ 和 paper-context/
 3. resolve_standards        填写 standard-profile.yaml
 4. analyze_sample_and_template  分析 DOCX/PDF 样文和模板
 5. build_evidence           生成 paper-context/evidence/
 6. stop_and_report          证据不足则阻断，输出缺失清单 ← 全流程机制
 7. build_thesis_spec        填写 thesis-ai-spec.yaml
 8. build_figure_registry    填写 figure-registry.yaml
 9. confirm_outline          回传目录表、字数预算表、样式冲突表，等用户确认
10. draft_chapters           分章写作（只能消费结构化事实和证据）
11. produce_assets           生成图表、截图、图片映射
12. produce_docx             生成主论文 .docx 和附件 .docx
13. quality_gates            运行质量门禁
14. delivery_report          报告交付物、验证结果、剩余风险
```

**stop_and_report 不是单独一步**——任何阶段发现继续写作会导致编造、格式误判或引用不可信时，都必须停止并报告缺失清单。

---

## 状态模型

采用双层状态，记录在 `paper-context/workflow/workflow-status.md` 中。

### Phase（流程阶段）

| Phase | 含义 |
|-------|------|
| `intake_only` | 仅收资料，不写正文 |
| `workspace_ready` | 工作区已初始化 |
| `standards_resolved` | 标准与模板已解析 |
| `sample_analysis_done` | 样文/模板分析完成 |
| `evidence_built` | 证据已建立 |
| `spec_confirmed` | 论文事实规格已确认 |
| `outline_confirmed` | 目录、字数和样式已确认 |
| `writing_allowed` | 允许写正文 |
| `delivery_done` | 已完成交付 |

### Status（阶段状态）

`pending` → `in_progress` → `blocked` / `needs_review` / `done` / `deprecated`

### 阻断示例

```yaml
phase: evidence_built
status: blocked
blocked_reason:
  - "缺少数据库 schema，不能生成 E-R 图"
  - "缺少系统运行截图（当前 2 张，需要至少 6 张）"
missing_materials:
  - type: database_schema
    required_for: "第3章数据库设计、E-R 图、第4章实现说明"
    acceptable_inputs:
      - "建表 SQL"
      - "数据库迁移文件"
      - "实体类目录"
next_action:
  - "请提供数据库迁移文件、建表 SQL 或实体类目录"
can_continue_with_limitations: false
```

### 合法回退

| 当前阶段 | 触发事件 | 回退到 |
|----------|----------|--------|
| `writing_allowed` | 用户补充新样文/模板 | `sample_analysis_done` |
| `writing_allowed` | 用户补充新源码/数据库/截图 | `evidence_built` |
| `outline_confirmed` | 用户修改目录/字数/样式 | `sample_analysis_done` |
| `delivery_done` | 导师 Word 批注 | `writing_allowed` |
| `delivery_done` | 学校模板变更 | `standards_resolved` |
| `delivery_done` | 新证据推翻旧事实 | `evidence_built` |

---

## 硬约束规则

1. **学校/导师要求优先于默认规则**。国家标准是兜底参考。
2. **未收集资料或用户确认"无更多资料"前，不写正文**。
3. **未完成标准解析、样文分析和证据构建前，不写正式正文**。
4. **证据不足时触发 stop_and_report，不得猜测补齐**。
5. **`thesis-ai-spec.yaml` 是论文事实唯一入口**。
6. **`figure-registry.yaml` 是图表截图唯一入口**。
7. **正文只能消费结构化事实和证据**，不直接从 README 或旧说明扩写。
8. **不编造**：功能、字段、接口、测试结果、实验数据、参考文献。
9. **AIGC 风格治理必须在证据链完整之后执行**。
10. **AIGC 优化只能做学术表达、证据密度、空泛表达治理**，不能伪造事实。
11. **论文正文不得暴露 AI 工作流语言**。
12. **第 4 章实现部分必须绑定真实模块、截图、核心代码或 SQL**。
13. **数据库设计缺 E-R 图时，系统设计类论文不得标记完成**。
14. **必须生成主论文 DOCX 和附件 DOCX**，附件保存图源码、ER 源码、流程图源码。
15. **文件名必须使用论文标题**，禁止 `final`、`draft`、`paper-final`、`doc1` 等通用名。
16. **参考文献必须优先真实可核验来源**，不确定就不用。
17. **文献工作流必须执行**：建池 → 核验 → 筛选 → 格式化 → 生成核验清单。

---

## 交付物

论文最终交付物统一在 `paper-output/` 目录下：

```
paper-output/
  <论文标题>.md                                    # 论文 Markdown 源稿
  <论文标题>.docx                                   # 主论文 Word 文档
  <论文标题>-附件.docx                              # 附件（图源码、ER 源码等）
  <论文标题>-image-map.json                         # 图片映射文件
  <论文标题>-文献核验清单.json                       # 参考文献核验清单
  figures/                                         # 图表导出图片
  screenshots/                                     # 系统截图
```

对应的治理侧产物在 `paper-context/` 下：

```
paper-context/
  workflow/          # 状态、步骤、进度、修订日志
  evidence/          # 源码证据、技术栈、数据库 Schema、API 列表
  literature/        # 参考文献抽取、交叉引用
  aigc/              # AIGC 风格报告
  word-comments/     # 导师批注待办和修订记录
```

---

## 依赖安装

### Python

```powershell
pip install -r requirements.txt
```

主要依赖：

| 包 | 用途 |
|----|------|
| `python-docx` | DOCX 生成和分析 |
| `PyYAML` | YAML 配置读写 |
| `pypdf` / `pdfplumber` | PDF 样文和文献解析 |
| *(playwright 由 Node.js 侧管理)* | |

### Node.js（仅截图功能）

```powershell
npm install
npm run install:browsers   # 安装 Chromium
```

仅当需要使用自动截图功能时才需要。如果系统已有 Chrome MCP 连接或手动截图，可跳过。

---

## 验证

运行以下命令确认 skill 完整性：

```powershell
# Python 脚本语法检查
Get-ChildItem .\scripts -Recurse -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }

# Node.js 脚本语法检查
node --check .\scripts\screenshots\browser\capture_screenshots.mjs

# package.json 合法性
python -m json.tool .\package.json

# Skill 结构校验（需要 Codex 环境）
$env:PYTHONUTF8='1'; python (Join-Path $env:CODEX_HOME 'skills\.system\skill-creator\scripts\quick_validate.py') .
```

---

## 合并来源

本 skill 由以下两个 skill 融合而成：

| 原 skill | 角色 | 详情 |
|----------|------|------|
| **thesis-standardizer** | 标准与证据骨架 | 标准解析、证据构建、质量门禁、AIGC 治理、Word 批注、工作流状态管理 |
| **lunwen** | 中文论文成稿引擎 | 样文分析、章节控字、图表截图、Mermaid/PlantUML、DOCX 成稿、附件 DOCX |

详细文件映射见 [`references/merge-map.md`](references/merge-map.md)。

---

## 许可

MIT License

---

## 相关文档

- [SKILL.md](SKILL.md) — Skill 路由入口和完整能力说明
- [assets/thesis-ai-standard/README.md](assets/thesis-ai-standard/README.md) — 论文标准化套件使用指南
- [references/workflow/stop-and-report.md](references/workflow/stop-and-report.md) — 阻断与报告机制
- [references/workflow/quality-gates.md](references/workflow/quality-gates.md) — 质量门禁检查清单
- [references/merge-map.md](references/merge-map.md) — 合并来源文件映射

---

## 致谢

本 skill 基于以下两个开源项目融合而成，特此致谢：

- **[xiaou61/thesis-skills](https://github.com/xiaou61/thesis-skills)** — 提供 thesis-standardizer 标准与证据骨架，包括标准解析、证据构建、质量门禁、AIGC 风格治理、工作流状态管理和 Word 批注修订等核心能力。
- **[Doryoku1223/lunwen-skill](https://github.com/Doryoku1223/lunwen-skill)** — 提供中文论文成稿引擎，包括样文分析、章节控字、Mermaid/PlantUML 图表、Playwright 截图闭环和 DOCX 格式化交付等核心能力。

感谢两个项目的作者为中文毕业论文标准化写作做出的贡献。
