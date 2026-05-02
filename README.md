# Skills

这个仓库用于维护可复用的 CLI coding agent skills。每个 skill 独立放在一个目录中，包含 `SKILL.md`、使用说明、参考模板、脚本和必要的工程规范文档。

## 已创建的 Skills

### harness-hub

`harness-hub` 是面向项目开发工程师的工程交付工作流。它用于把需求推进到可验证的工程结果：理解需求、建立上下文、设计方案、实现修改、补充测试、运行验证，并输出清晰的交付总结。

适合场景：

- 需求落地、功能开发、bug 修复和小范围重构。
- 需求文档、PRD 或较长 issue 的逐步解析和实现。
- PR review 处理、CI 失败排查、测试补齐和发布验收。
- 多角色协作任务：主代理负责方案、分派、复核和整合；实现、勘察、验证、评审、文档子代理按需协作。

常用触发方式：

```text
/harness-hub

目标：...
上下文：...
约束：...
验收：...
```

多角色 Checklist 示例：

```text
/harness-hub

使用 Harness Hub 多角色模式处理这个任务。
请开启任务拆分 Checklist，并按“勘察-方案-实现-验证-交付”逐步推进。

目标：...
上下文：...
约束：...
验收：...

交付时请说明：
1. 完成了什么
2. 修改了哪些文件
3. 运行了哪些验证
4. 未验证项和剩余风险
```

主要文件：

- `harness-hub/SKILL.md`：skill 入口和核心行为约定。
- `harness-hub/README.md`：使用说明和 `/harness-hub` 命令示例。
- `harness-hub/docs/harness/`：工程交付规范、角色契约、质量门禁和验收要求。
- `harness-hub/references/`：技术方案、任务拆解、测试计划、PR 描述和交接文档模板。
- `harness-hub/scripts/`：计划、交接和文档检查脚本。

### spec-mode

`spec-mode` 是规范化 Spec 工作流 skill，用于在 CLI Agent（如 Codex、Claude Code）中执行文件优先的规范化开发流程。它以 Markdown 文档作为唯一事实来源，在编码前完成需求确认、技术设计和任务拆分，并通过阶段门禁（phase gates）确保每个环节都经过审查。

适合场景：

- 功能开发或缺陷修复的规范化需求到交付流程。
- 需要结构化文档（requirements.md / bugfix.md、design.md、tasks.md）来对齐需求、设计和实现。
- 要求可追踪的验收标准（EARS）和任务执行状态。
- 需要 Requirements-First、Design-First 或 Bugfix Spec 多种工作流。

常用触发方式：

```text
/spec <需求或需求文档路径> [补充说明]
/spec-mode <需求或需求文档路径> [补充说明]
```

示例：

```text
/spec 为 Markdown 编辑器增加撤销重做支持
/spec-mode 修复登录接口 500，不能改变现有错误码
/spec /absolute/path/to/requirement.md 使用 requirements-first
```

主要文件：

- `spec-mode/SKILL.md`：skill 入口、Activation Guard、阶段门禁和核心行为约定。
- `spec-mode/spec-mode-skill-design.md`：设计与落地文档，包含可落地方案和推荐 Skill 包内容。
- `spec-mode/references/`：完整工作流程和文档模板。
- `spec-mode/assets/templates/`：脚本初始化文档时使用的 Markdown 模板（requirements.md、bugfix.md、design.md、tasks.md）。
- `spec-mode/scripts/`：spec 初始化（`spec_init.py`）、lint（`spec_lint.py`）、状态汇总（`spec_status.py`）和 CLI 选择器（`spec_choice.py`）。

## 本地检查

修改 `harness-hub` 文档后，可以运行：

```sh
./harness-hub/scripts/harness-check.sh
./harness-hub/scripts/harness-validate-docs.sh
```
