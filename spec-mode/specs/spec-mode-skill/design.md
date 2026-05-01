# 设计文档：Spec Mode Skill（spec-mode-skill）

Spec Type: Feature
Workflow: requirements-first
Status: Design Accepted
Review Status: implemented

## 概述

本设计将项目实现为一个可安装的 Agent Skill 包，并配套轻量脚本实现稳定的 spec 文档初始化、检查和状态汇总。

项目采用四层结构：

1. `SKILL.md`：agent 触发入口和核心执行规则。
2. `references/`：长流程说明、模板说明、Kiro 样例分析。
3. `assets/templates/`：脚本可使用的 Markdown 模板。
4. `scripts/`：可执行辅助程序。

生成的用户 spec 文档不放在 `.kiro/specs`，而是放在：

```text
<document-root>/<requirement-name>/
```

该结构满足用户“先指定文档管理根目录，再根据需求内容分层”的要求。

## 架构

### 项目结构

```text
spec-mode/
├── SKILL.md
├── kiro-spec-mode-skill-design.md
├── references/
│   ├── workflow.md
│   ├── templates.md
│   └── kiro-sample-analysis.md
├── assets/
│   └── templates/
│       ├── requirements.md
│       ├── bugfix.md
│       ├── design.md
│       └── tasks.md
├── scripts/
│   ├── spec_init.py
│   ├── spec_lint.py
│   ├── spec_status.py
│   └── spec_choice.py
└── specs/
    └── spec-mode-skill/
        ├── requirements.md
        ├── design.md
        ├── tasks.md
        └── .config.json
```

### 运行时数据流

```text
User: /spec <需求或文档路径> [补充说明]
  or /spec-mode <需求或文档路径> [补充说明]
  or explicit request to use spec mode
  -> Agent loads SKILL.md
  -> Agent verifies explicit spec-mode activation
  -> Agent classifies workflow
  -> Agent asks user to choose Requirements / Technical Design / Bugfix if needed
     (interactive selector when available, numbered prompt fallback)
  -> Agent optionally calls scripts/spec_init.py
  -> Agent writes or updates requirements.md / bugfix.md
  -> Codex displays the diff; Agent shows path, summary, key changes, and questions
  -> Agent runs spec_choice.py; User chooses Confirm, View full document, or Continue discussing
  -> Review gate
  -> Agent writes or updates design.md
  -> Codex displays the diff; Agent shows path, summary, key changes, and questions
  -> Agent runs spec_choice.py; User chooses Confirm, View full document, or Continue discussing
  -> Review gate
  -> Agent writes or updates tasks.md
  -> Codex displays the diff; Agent shows path, summary, key changes, and questions
  -> Agent runs spec_choice.py; User chooses Confirm, View full document, or Continue discussing
  -> Review gate
  -> Agent runs spec_choice.py; User chooses whether to execute required tasks, required + optional tasks, or stop
  -> Agent executes tasks from tasks.md
  -> Agent runs validation
  -> Agent updates task status and acceptance summary
```

## 组件与接口

### 1. `SKILL.md`

**职责**：定义什么时候触发 spec mode，以及 agent 在文档生成、任务执行、验收时必须遵守的行为。

**关键设计**：

- 明确 `/spec` 命令入口。
- 明确 Activation Guard：只有 `/spec`、`/spec-mode` 或明确要求 spec 模式时才启用。
- 明确目录规则：`<document-root>/<requirement-name>/`。
- 明确默认根目录：当前项目 `specs/`，无项目时 `~/new project/specs`。
- 明确 phase gates。
- 明确 Kiro 风格文档结构。
- 指向脚本和 references。

### 2. `references/workflow.md`

**职责**：保存完整流程细节，避免 `SKILL.md` 过长。

**内容**：

- `/spec` 解析规则。
- 选择弹窗或 CLI 选择问题。
- Requirements-first、Design-first、Bugfix 流程。
- Task execution 和 acceptance 规则。

### 3. `references/kiro-sample-analysis.md`

**职责**：记录对 `/Users/xueqiang/Git/markdown/.kiro/specs/undo-redo-support` 样例的观察结论。

**内容**：

- Kiro 原生目录结构。
- `requirements.md`、`design.md`、`tasks.md` 的标题、章节和任务状态风格。
- `.config.kiro` 到 portable `.config.json` 的映射。

### 4. `assets/templates/*.md`

**职责**：提供脚本初始化文档时使用的最小模板。

**设计原则**：

- 模板只做 seed，不假装已经完成需求分析。
- 使用 `{{name}}`、`{{slug}}`、`{{summary}}`、`{{workflow}}`、`{{spec_type}}` 占位。
- 保留“待确认”内容，提醒 agent 后续必须细化。

### 5. `scripts/spec_init.py`

**职责**：创建目录和初始文档。

**接口**：

```text
python3 scripts/spec_init.py \
  --root <document-root> \
  --name <requirement-name> \
  --source-text <requirement-text> \
  --workflow requirements-first
```

**行为**：

- 计算 slug。
- 创建 `<root>/<slug>/`。
- 按 feature 或 bugfix 写入首阶段文档。
- 写入 `design.md`、`tasks.md` seed。
- 写入 `.config.json`。
- 默认不覆盖已有文件，除非传入 `--force`。

### 6. `scripts/spec_lint.py`

**职责**：检查 spec 文件是否完整。

**检查项**：

- feature spec 是否有 `requirements.md`、`design.md`、`tasks.md`。
- bugfix spec 是否有 `bugfix.md`、`design.md`、`tasks.md`。
- 是否同时存在 `requirements.md` 和 `bugfix.md`。
- 是否有 EARS 风格 `SHALL`。
- `tasks.md` 是否有 checkbox、验证字段和需求追踪。

### 7. `scripts/spec_status.py`

**职责**：汇总 `tasks.md` 中任务状态。

**状态映射**：

```text
[ ] pending
[~] in_progress
[x] completed
[*] optional
[-] skipped
```

状态统计只读取 `## 任务` 段，避免把 `## 验收` 清单误算为执行任务。

### 8. `scripts/spec_choice.py`

**职责**：为 workflow 选择、文档确认和 task 执行确认提供 CLI 选择器。

**接口**：

```text
python3 scripts/spec_choice.py --title "Confirm requirements.md?" \
  --option "确认::Accept this document and continue::recommended" \
  --option "继续沟通::Revise this document before continuing"
```

**行为**：

- 在 TTY 中使用 curses 支持上下键和回车。
- 支持数字键快速选择。
- 在非 TTY 中退化为编号输入。
- 支持 `--print-default` 便于自动化验证。
- 支持 `--json` 便于 agent 或脚本读取结构化结果。

**使用要求**：

- 文档确认必须优先调用该脚本。
- tasks 执行确认必须优先调用该脚本。
- 只有在工具执行不可用时才退化为纯文本确认。

## 数据模型

### `.config.json`

```json
{
  "specId": "uuid",
  "workflowType": "requirements-first",
  "specType": "feature",
  "documentRoot": "/path/to/specs",
  "requirementName": "spec-mode-skill",
  "slug": "spec-mode-skill",
  "sourceFile": null,
  "createdBy": "spec-mode",
  "createdAt": "2026-05-01T..."
}
```

## 错误处理

- 若 source file 不存在，脚本直接失败，由 agent 向用户说明路径无效。
- 若目录已存在且未使用 `--force`，脚本不覆盖已有文档。
- 若 lint 发现缺失核心文件，返回非零退出码。
- 若 lint 只有 warning，返回零退出码，允许流程继续但提醒用户 review。
- 若选择器运行在不支持 TTY 的环境，退化为编号选择；若没有输入，使用推荐选项。

## 安全与隐私

- 脚本只在指定文档根目录中创建或更新 spec 文档。
- 脚本不删除文件。
- 脚本不上传内容。
- 脚本不执行项目代码、部署或网络操作。
- 文档中不应写入密钥、私钥、生产连接串或真实敏感数据。

## 测试策略

- 初始化测试：使用 `/private/tmp` 作为 root，验证目录结构与文件生成。
- Lint 测试：对生成的 spec 目录运行 `spec_lint.py`。
- Status 测试：对生成的 spec 目录运行 `spec_status.py --json`，验证任务统计。
- Choice 测试：运行 `spec_choice.py --print-default --json`，验证选择器输出。
- 当前项目自举测试：在 `specs/spec-mode-skill/` 生成本项目自身 spec。

## 正确性属性

### 属性 1：目录结构稳定

*对任意* 有效 document root 和 requirement name，执行 `spec_init.py` 后，生成路径应始终为 `<root>/<slug>/`。

**验证：需求 2**

### 属性 2：任务统计不包含验收清单

*对任意* 包含 `## 任务` 和 `## 验收` 的 `tasks.md`，`spec_status.py` 只统计 `## 任务` 段内的 checkbox。

**验证：需求 5**

### 属性 3：默认不破坏已有文档

*对任意* 已存在的 spec 文档，未传入 `--force` 时，`spec_init.py` 不应覆盖已有文件。

**验证：需求 6**

### 属性 4：阶段门禁必须由用户确认推进

*对任意* 生成的 requirements、design 或 tasks 文档，agent 必须展示路径、概要、关键改动点和确认选项，并在用户确认后才能进入下一阶段。只有用户选择查看全文时，才在聊天中粘贴完整文档。

**验证：需求 8**

## 风险

- 不同 CLI 对“弹窗选择”的支持不同：设计上将弹窗抽象为“支持则使用 choice dialog，否则用文本问题”。
- 中文 slug 无法完美自动转换：脚本提供少量常见词替换，agent 仍可根据语义指定 `--name`。
- 模板只是 seed：真正高质量文档仍依赖 agent 读取项目上下文后细化。
