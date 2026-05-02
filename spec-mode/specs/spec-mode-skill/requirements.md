# 需求文档

Spec Type: Feature
Workflow: requirements-first
Status: Requirements Accepted
Review Status: implemented

## 简介

本项目实现一个可安装的 Spec Mode Skill，供 Codex、Claude Code 以及其他支持 Agent Skills / `SKILL.md` 的 CLI 工具使用。

Skill 通过 `/spec <需求或需求文档路径> [其他说明]` 进入 spec 模式，根据需求内容创建文档目录、生成 requirements/design/tasks 或 bugfix 文档、引导用户逐步确认，并能基于已确认文档执行 coding、验证和验收。

文档输出目录使用用户指定的文档管理根目录，并在其下按具体需求名分层；文档直接放在具体需求目录中，不再额外创建 `spec/` 子目录：

```text
<document-root>/
└── <具体需求名>/
    ├── requirements.md
    ├── design.md
    ├── tasks.md
    └── .config.json
```

若用户没有指定项目或文档根目录，默认在当前项目的 `specs/` 下生成；若没有项目上下文，则创建 `~/new project/specs`。

---

## 词汇表

- **Spec Mode Skill**：以 `SKILL.md` 为入口的可安装 agent skill，用于执行规范化开发流程。
- **Document Root**：用户指定的文档管理根目录，不是最终 spec 目录。
- **Requirement Folder**：由具体需求名生成的目录，例如 `undo-redo-support/`。
- **Spec Folder**：具体需求目录本身，保存 spec 模式生成的全部文档。
- **Phase Gate**：requirements、design、tasks、coding、acceptance 之间的确认门禁。
- **EARS**：Easy Approach to Requirements Syntax，用 `WHEN/IF/WHILE ... THE SYSTEM SHALL ...` 描述可测试需求。
- **Task Execution**：基于 `tasks.md` 的任务执行流程，包含任务状态更新、代码修改、验证和验收。

---

## 需求

### 需求 1：仅通过显式命令或明确说明启用 spec 模式

**用户故事：** 作为 CLI agent 用户，我希望只有在我明确使用 `/spec`、`/spec-mode` 或明确说使用 spec 模式时才启动 spec 流程，以免普通开发需求被错误套用 spec 模式。

#### 验收标准

1. WHEN 用户输入 `/spec <文字需求>`，THE Skill SHALL 将 `<文字需求>` 作为需求来源并启动 spec 流程。
2. WHEN 用户输入 `/spec-mode <文字需求>`，THE Skill SHALL 将 `<文字需求>` 作为需求来源并启动 spec 流程。
3. WHEN 用户明确说“使用 spec 模式”“启用 spec 模式”或 “use spec mode”，THE Skill SHALL 启动 spec 流程。
4. WHEN 用户没有使用 `/spec`、`/spec-mode` 或明确要求 spec 模式，THE Skill SHALL NOT 启动 spec 流程。
5. WHEN 用户只是要求编码、规划、需求分析、设计文档、任务拆解、bug 修复或普通文档，THE Skill SHALL NOT 自动启用 spec 模式。
6. WHEN 用户输入 `/spec <需求文档路径>` 或 `/spec-mode <需求文档路径>` 且路径存在，THE Skill SHALL 读取该文档内容作为需求来源。
7. WHEN 用户在显式 spec 命令后追加其他说明，THE Skill SHALL 将其作为约束、偏好或上下文补充纳入需求分析。
8. IF 显式 spec 命令后缺少需求内容，THEN THE Skill SHALL 要求用户补充需求，而不是生成空文档。

---

### 需求 2：按用户指定的文档根目录生成分层文档

**用户故事：** 作为项目维护者，我希望 spec 文档被生成到当前项目的 `specs/<具体需求名>/`，以便和代码项目分离但仍可版本化管理。

#### 验收标准

1. WHEN 用户指定文档管理根目录，THE Skill SHALL 在该根目录下创建 `<具体需求名>/`。
2. WHEN 用户没有指定文档管理根目录但当前处于项目目录，THE Skill SHALL 默认使用 `<当前项目>/specs`。
3. WHEN 没有项目上下文，THE Skill SHALL 创建并使用 `~/new project/specs`。
4. THE Skill SHALL NOT 创建工具专属的隐藏目录作为文档输出目录。
5. THE Skill SHALL 在 spec 文件夹中保存 `.config.json`，记录 workflow type、spec type、需求名和路径。

---

### 需求 3：提供阶段化文档生成流程

**用户故事：** 作为需求提出者，我希望 AI 先帮我确认需求方向，再依次生成 requirements、design、tasks，以便每个阶段都可审查和调整。

#### 验收标准

1. WHEN 工作流不明确，THE Skill SHALL 提供 Requirements、Technical Design、Bugfix 等选项，并给出推荐项。
2. WHEN 用户选择 Requirements，THE Skill SHALL 先生成 `requirements.md`。
3. WHEN 用户确认 `requirements.md`，THE Skill SHALL 继续生成 `design.md`。
4. WHEN 用户确认 `design.md`，THE Skill SHALL 继续生成 `tasks.md`。
5. WHEN 用户确认 `tasks.md`，THE Skill SHALL 才能开始 coding，除非用户明确要求只生成文档。
6. WHILE 任一阶段未确认，THE Skill SHALL 支持继续沟通并修改当前阶段文档。

---

### 需求 4：提供规范化文档内容结构

**用户故事：** 作为 spec-mode 用户，我希望生成文档使用一致的结构和格式，以便在不同 CLI 工具之间保持一致的阅读和执行体验。

#### 验收标准

1. THE `requirements.md` SHALL 包含简介、词汇表、需求、用户故事和 EARS 验收标准。
2. THE `design.md` SHALL 包含概述、架构、组件与接口、数据模型、流程、测试策略、正确性属性和风险。
3. THE `tasks.md` SHALL 包含概述、嵌套复选框任务、检查点、验证方式和需求追踪。
4. WHEN 需求属于 bugfix，THE Skill SHALL 生成 `bugfix.md`，并区分当前行为、期望行为和保持不变的行为。
5. THE Skill SHALL 使用 `[ ]`、`[~]`、`[x]` 风格的任务状态标记。

---

### 需求 5：支持基于文档执行任务和验收

**用户故事：** 作为开发者，我希望 skill 不只是生成文档，还能按照前面生成的 spec 执行 coding 流程，以便需求、设计、任务和代码实现闭环。

#### 验收标准

1. WHEN 用户要求执行某个任务，THE Skill SHALL 先读取该需求目录下的全部 spec 文档。
2. WHEN 任务开始执行，THE Skill SHALL 将对应任务状态更新为 `[~]`。
3. WHEN 任务验证通过，THE Skill SHALL 将对应任务状态更新为 `[x]`。
4. IF 验证失败或无法运行，THEN THE Skill SHALL 保持任务未完成并记录原因。
5. THE Skill SHALL 在最终验收中总结完成任务、修改文件、验证命令、风险和待办。

---

### 需求 6：允许借助脚本实现可靠流程

**用户故事：** 作为 skill 维护者，我希望项目不仅依赖提示词，还能通过脚本创建目录、初始化文档、检查文档和查看状态，以便在不同 CLI 工具中稳定执行。

#### 验收标准

1. THE 项目 SHALL 提供 `scripts/spec_init.py` 创建目录和初始文档。
2. THE 项目 SHALL 提供 `scripts/spec_lint.py` 检查 spec 文件完整性、EARS、任务验证和需求追踪。
3. THE 项目 SHALL 提供 `scripts/spec_status.py` 汇总任务状态。
4. WHEN 脚本生成文档，THE output SHALL 符合 `<document-root>/<具体需求名>/` 结构。
5. THE scripts SHALL NOT 执行代码删除、部署、上传或其他高风险副作用。

---

### 需求 7：需求落地过程中优先提问而不是使用假设

**用户故事：** 作为需求提出者，我希望 AI 在需求不明确时直接问我，而不是自行假设，以便生成的文档更贴近真实意图。

#### 验收标准

1. WHEN 缺失信息会影响范围、行为、用户体验、架构、数据、测试或验收，THE Skill SHALL 向用户提问。
2. WHEN 有多个确认点，THE Skill SHALL 将确认点整理为简洁列表供用户选择或回复。
3. IF CLI 支持选择器，THEN THE Skill SHALL 优先使用选择器让用户通过数字或上下键加回车确认。
4. THE Skill SHALL NOT 在 requirements、design 或 tasks 中默认填写未经确认的关键假设。
5. IF 必须记录未确认内容，THEN THE Skill SHALL 将其放入“待确认问题”，而不是“假设”。

---

### 需求 8：每个阶段文档生成后必须摘要确认

**用户故事：** 作为审阅者，我希望 Codex 负责展示文件 diff，而 assistant 只展示路径、概要、关键改动点和确认选项，以便减少重复内容和 token 消耗。

#### 验收标准

1. WHEN `requirements.md` 或 `bugfix.md` 生成完成，THE Skill SHALL 展示文档路径、概要、关键改动点和待确认问题。
2. WHEN `design.md` 生成完成，THE Skill SHALL 展示文档路径、概要、关键改动点和待确认问题。
3. WHEN `tasks.md` 生成完成，THE Skill SHALL 展示文档路径、概要、关键改动点和待确认问题。
4. THE Skill SHALL NOT 默认在聊天中粘贴完整文档内容。
5. THE confirmation prompt SHALL provide at least `确认`、`查看全文` and `继续沟通` options.
6. WHEN 用户选择 `查看全文`，THE Skill SHALL 读取并展示完整文档内容。
7. WHEN 用户选择 `继续沟通` 或直接反馈问题，THE Skill SHALL 根据反馈更新当前文档并重新展示路径、概要、关键改动点和确认选项。
8. WHEN 所有文档确认完成，THE Skill SHALL 询问是否开始执行 tasks。
9. THE task execution prompt SHALL provide options for required tasks, required plus optional tasks, and no coding yet.

---

### 需求 9：确认动作优先使用 CLI 选择器

**用户故事：** 作为 CLI 用户，我希望确认文档和执行 tasks 时能通过上下键加回车选择，而不是手动输入确认文本。

#### 验收标准

1. WHEN 需要确认 `requirements.md`、`bugfix.md`、`design.md` 或 `tasks.md`，THE Skill SHALL 优先调用 CLI 选择器。
2. WHEN CLI 选择器运行在 TTY 中，THE Skill SHALL 支持上下键和回车选择。
3. WHEN CLI 选择器无法交互运行，THE Skill SHALL 退化为编号选择。
4. THE document confirmation selector SHALL provide `确认`、`查看全文` and `继续沟通` options.
5. THE task execution selector SHALL provide `开始 required tasks`、`开始 required + optional tasks` and `暂不 coding` options.
6. THE Skill SHALL NOT 在可执行选择器的情况下只输出“请回复确认”作为唯一确认方式。

---

## 边界情况

1. WHEN 需求名包含中文或特殊字符，THE Skill SHALL 生成安全、稳定、可读的 slug。
2. WHEN 目标 spec 目录已存在，THE Skill SHALL 复用现有文档，除非用户明确要求覆盖。
3. WHEN 用户提供的是 bug 描述而不是 feature，THE Skill SHALL 进入 bugfix 流程。
4. WHEN 用户要求一次性生成全部文档，THE Skill SHALL 允许执行，但标记 `Review Status: unreviewed`。
5. WHEN 当前客户端不支持交互式选择器，THE Skill SHALL 退化为编号列表并等待用户输入。

---

## 非功能需求

1. WHEN Skill 被安装到不同 CLI 工具，THE Skill SHALL 主要依赖 Agent Skills 标准结构：`SKILL.md`、`references/`、`assets/`、`scripts/`。
2. THE Skill SHALL 使用 Markdown 作为所有 spec 文档格式。
3. THE Skill SHALL 基于文件优先的规范化流程实现，不依赖任何特定 IDE 或工具的私有能力。
4. THE scripts SHALL 使用 Python 标准库，避免额外依赖。
