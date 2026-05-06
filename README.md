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
- 需要跨会话持续迭代同一个需求，支持多窗口并行推进不同 spec。

命令说明：

| 命令 | 说明 |
|------|------|
| `/spec <需求>` | **一次性模式**。执行完整的 requirements → design → tasks 结构化流程，不保留持续状态，对话结束后不跨会话继续。 |
| `/spec-mode <需求>` | 同 `/spec`，别名入口。 |
| `/spec --persist <需求>` | **持续模式**。创建 spec 文档并绑定当前会话，后续补充需求、调整设计、追加任务均自动落在同一个 spec 上。 |
| `/spec-continue [spec名称]` | **恢复 spec**。从 spec 文档中加载上下文（当前阶段、未完成任务等），恢复跨会话记忆后继续迭代。不指定名称时列出所有可用 spec 供选择。 |
| `/spec-status` | 查看当前 session 绑定的 spec、阶段、任务完成情况和 active pointer 状态。 |
| `/spec-end` | 结束当前持续 session，从 active pointer 中移除该 session，不删除任何 spec 文档。 |

示例：

```text
# 一次性流程
/spec 为 Markdown 编辑器增加撤销重做支持
/spec-mode 修复登录接口 500，不能改变现有错误码

# 持续模式：开启
/spec --persist 为用户中心增加 OAuth2 登录

# 持续模式：跨会话恢复
/spec-continue oauth2-login

# 持续模式：列出所有 spec 选择恢复
/spec-continue

# 退出持续模式
/spec-end
```

主要文件：

- `spec-mode/SKILL.md`：skill 入口、Activation Guard、命令集、阶段门禁、document-first 纪律和命令遵从规则。
- `spec-mode/references/workflow.md`：完整工作流程、上下文加载协议、边界防污染规则。
- `spec-mode/assets/templates/`：脚本初始化文档时使用的 Markdown 模板（requirements.md、bugfix.md、design.md、tasks.md）。
- `spec-mode/scripts/spec_session.py`：持续 session 生命周期管理（start / continue / status / end / list / load）。
- `spec-mode/scripts/spec_init.py`：初始化 spec 目录结构和文档。
- `spec-mode/scripts/spec_lint.py`：校验 spec 结构、session 状态和目录边界。
- `spec-mode/scripts/spec_status.py`：输出 spec 阶段、session 状态和任务统计。
- `spec-mode/scripts/spec_choice.py`：CLI 交互式选择器。

## 本地检查

修改 `harness-hub` 文档后，可以运行：

```sh
./harness-hub/scripts/harness-check.sh
./harness-hub/scripts/harness-validate-docs.sh
```
