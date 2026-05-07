# chinese-thesis-workbench

> 以标准和证据为骨架，以默认格式 DOCX 为输出，把项目源码、学校要求、样文、文献和截图整合成可追溯、可续写、可检查的中文本科论文交付工作台。

[![Skill Type](https://img.shields.io/badge/Codex-Skill-blue)](https://codex.claude.ai)
[![Language](https://img.shields.io/badge/Language-中文-red)]()

---

## 定位

**chinese-thesis-workbench** 不是一键生成论文的工具。它是一套论文标准化交付工作台，把毕业论文拆成可审查、可回退的步骤——收集材料 → 构建证据 → 确认大纲 → 分章写作 → 生成默认格式 DOCX → 质量检查。

输出一份结构完整、素材不丢失的 `.docx`，用户复制粘贴到学校模板中做最终排版。

### 适合

- 有真实项目（软件系统、实验、调研等）需要写成毕业论文的学生
- 需要控制章节字数、管理图表截图、核验参考文献的用户
- 导师批注后需要系统化修订的用户

### 不适合

- 没有真实项目或数据、希望凭空生成论文的用户
- 纯文科论文可参考流程但需重配证据链

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

### 样文/模板分析（可选）

```powershell
python scripts/docx/analyze_docx.py 学校模板.docx --json-out result.json
python scripts/workspace/build_sample_template_outputs.py result.json --target <项目目录>
```

解析结果只用于目录建议和字数预算，不驱动 DOCX 格式生成。

---

## 核心能力

### 标准与证据

| 能力        | 说明                                 |
| --------- | ---------------------------------- |
| 材料摄入      | 按必需/建议/可选分级，说明缺失影响和是否可继续           |
| 项目证据提取    | 按论文类型从源码、数据库、API、测试、实验数据中生成证据索引    |
| 文献治理      | PDF 参考文献抽取 → 候选池 → 核验 → 格式化 → 核验清单 |
| AIGC 风格治理 | 减少空泛表达，不伪造事实                       |
| Word 批注修订 | 抽取导师批注，逐条修订并记录变更日志                 |

### 论文成稿

| 能力      | 说明                                                   |
| ------- | ---------------------------------------------------- |
| 样文分析    | 提取往届样文的目录结构、章级字数和图表节奏                                |
| 章节控字    | 写作前定预算，写完统计，超出自动压缩                                   |
| 图表      | 支持 Mermaid / PlantUML / draw.io 三种图源；Playwright 自动截图 |
| DOCX 成稿 | 内置默认格式 `.docx`（宋体小四正文、黑体标题），不承诺复刻学校模板                |
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
| `user-decisions.md`     | 用户已确认的关键选择归档             |

详细规则和工作流见 [SKILL.md](SKILL.md)。

---

## 架构

```
治理侧 paper-context/
  workflow/         用户仪表盘、材料清单、内容取舍、阻断报告、用户决策、进度日志
  evidence/         项目证据、技术栈、数据库 Schema、API 列表
  literature/       参考文献抽取、交叉引用
  standards/        标准解析、样式提取
  aigc/             AIGC 风格报告
  word-comments/    导师批注待办和修订记录

交付侧 paper-output/
  <论文标题>.md                Markdown 源稿
  <论文标题>.docx              主论文（默认格式）
  <论文标题>-附件.docx         附件（图源码等）
  <论文标题>-image-map.json    图片映射
  <论文标题>-文献核验清单.json 参考文献核验
  figures/                     图表
  screenshots/                 截图
```

---

## 目录

```
chinese-thesis-workbench/
  SKILL.md                  Skill 路由入口
  README.md                 本文件
  requirements.txt           Python 依赖
  package.json               Node.js 依赖（截图）

  references/               按需加载的参考文档
    workflow/               工作流、状态管理、阻断、质量门禁
    standards/              标准解析、样式提取、默认格式
    evidence/               源码证据、文献治理、事实提取
    writing/                样文分析、章节写作、参考文献选择、AIGC 治理
    delivery/               DOCX 成稿、最终检查、Word 批注修订

  scripts/                  可执行脚本
    workspace/              工作区初始化、工作流日志、分析结果归并
    evidence/               项目证据构建
    literature/             PDF 参考文献抽取、交叉引用、候选池
    docx/                   DOCX 分析、生成、批注抽取
    figures/                Mermaid 渲染、图表资产检查、图片映射
    screenshots/            截图占位提取、截图计划、浏览器截图
    review/                 章节字数统计、AIGC 风格分析

  assets/thesis-ai-standard/
    templates/              结构化配置模板（YAML）
    drawio/                 图表模板（6 张）

  tests/                    核心合约测试
```

---

## 依赖

| 包                      | 用途         |
| ---------------------- | ---------- |
| `python-docx`          | DOCX 生成和分析 |
| `PyYAML`               | YAML 配置读写  |
| `pypdf` / `pdfplumber` | PDF 解析     |

Node.js 和 Playwright 仅自动截图功能需要：

```powershell
npm install && npm run install:browsers
```

---

## 验证

```powershell
# Python 编译检查
python -m compileall scripts tests

# 单元测试
python -m unittest discover tests

# 工作区模板校验
python scripts/workspace/check_thesis_workspace.py assets/thesis-ai-standard
```

---

## 合并来源

本 skill 参考了以下两个项目：

| 原 skill                      | 角色                                               |
| ---------------------------- | ------------------------------------------------ |
| **xiaou61/thesis-skills**    | 标准与证据骨架：标准解析、证据构建、质量门禁、AIGC 治理、Word 批注、状态管理      |
| **Doryoku1223/lunwen-skill** | 中文论文成稿引擎：样文分析、章节控字、图表截图、Mermaid/PlantUML、DOCX 成稿 |

详细文件映射见 [`references/merge-map.md`](references/merge-map.md)。

---

## 许可

MIT License

---

## 致谢

- **[xiaou61/thesis-skills](https://github.com/xiaou61/thesis-skills)** — 提供标准与证据骨架
- **[Doryoku1223/lunwen-skill](https://github.com/Doryoku1223/lunwen-skill)** — 提供中文论文成稿引擎

感谢两个项目的作者为中文毕业论文标准化写作做出的贡献。
