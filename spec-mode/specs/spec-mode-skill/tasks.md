# 实现计划：Spec Mode Skill（spec-mode-skill）

Spec Type: Feature
Workflow: requirements-first
Status: Implemented
Review Status: implemented

## 概述

本实现计划将 Kiro-style Spec Mode Skill 拆分为文档入口、参考资料、模板、脚本、项目自举 spec 和验证几个部分。

## 任务

- [x] 1. 建立 skill 入口
  - [x] 1.1 创建 `SKILL.md`
    - 定义 `/spec` 命令触发方式
    - 定义文档输出目录 `<document-root>/<具体需求名>/`
    - 定义 requirements/design/tasks/coding/acceptance 阶段门禁
    - 定义基于 `tasks.md` 的任务执行规则
    - 文件：`SKILL.md`
    - 验证：人工检查文件存在且包含关键规则
    - _需求：1、2、3、5_

- [x] 2. 补充参考资料
  - [x] 2.1 创建完整流程参考文档
    - 说明 `/spec` intake、workflow selection、directory resolution、task execution
    - 文件：`references/workflow.md`
    - 验证：人工检查
    - _需求：1、2、3、5_

  - [x] 2.2 创建 Kiro 样例分析文档
    - 研究 `/Users/xueqiang/Git/markdown/.kiro/specs/undo-redo-support`
    - 记录 requirements/design/tasks/.config.kiro 的结构特点
    - 文件：`references/kiro-sample-analysis.md`
    - 验证：人工检查
    - _需求：4_

  - [x] 2.3 创建模板参考文档
    - 提供 requirements、bugfix、design、tasks 的完整 Markdown 模板
    - 文件：`references/templates.md`
    - 验证：人工检查
    - _需求：4_

- [x] 3. 实现脚本可用模板
  - [x] 3.1 创建 `assets/templates/requirements.md`
    - 包含简介、词汇表、需求、EARS 验收标准、边界情况、非功能需求
    - _需求：4、6_

  - [x] 3.2 创建 `assets/templates/bugfix.md`
    - 包含当前行为、期望行为、保持不变行为、证据和约束
    - _需求：4、6_

  - [x] 3.3 创建 `assets/templates/design.md`
    - 包含架构、组件接口、数据模型、流程、测试策略、正确性属性
    - _需求：4、6_

  - [x] 3.4 创建 `assets/templates/tasks.md`
    - 包含嵌套任务、检查点、验证和验收清单
    - _需求：4、5、6_

- [x] 4. 实现辅助脚本
  - [x] 4.1 实现 `scripts/spec_init.py`
    - 支持 `--root`、`--project-dir`、`--name`、`--source-text`、`--source-file`、`--workflow`、`--spec-type`、`--force`
    - 生成 `<root>/<slug>/`
    - 写入 Markdown 文档和 `.config.json`
    - 文件：`scripts/spec_init.py`
    - 验证：`python3 scripts/spec_init.py --root /private/tmp/spec-mode-test/specs --name undo-redo-support --source-text ... --workflow requirements-first`
    - _需求：1、2、6_

  - [x] 4.2 实现 `scripts/spec_lint.py`
    - 检查核心文件、EARS、任务验证和需求追踪
    - 文件：`scripts/spec_lint.py`
    - 验证：`python3 scripts/spec_lint.py /private/tmp/spec-mode-test/specs/undo-redo-support/spec`
    - _需求：5、6_

  - [x] 4.3 实现 `scripts/spec_status.py`
    - 汇总 `[ ]`、`[~]`、`[x]`、`[*]`、`[-]` 状态
    - 只统计 `## 任务` 段，排除 `## 验收`
    - 文件：`scripts/spec_status.py`
    - 验证：`python3 scripts/spec_status.py /private/tmp/spec-mode-test/specs/undo-redo-support/spec --json`
    - _需求：5、6_

- [x] 5. 自举生成当前项目 spec
  - [x] 5.1 使用脚本生成当前项目 spec 目录
    - 输出目录：`specs/spec-mode-skill/`
    - 文件：`specs/spec-mode-skill/requirements.md`
    - 文件：`specs/spec-mode-skill/design.md`
    - 文件：`specs/spec-mode-skill/tasks.md`
    - 文件：`specs/spec-mode-skill/.config.json`
    - 验证：目录和文件存在
    - _需求：2、4_

  - [x] 5.2 将自举 spec 细化为本项目真实需求、设计和任务
    - 替换脚本初始 seed 内容
    - 标记已完成任务
    - _需求：3、4、5_

- [x] 6. 检查点 —— 验证脚本和目录结构
  - [x] 6.1 运行临时目录初始化验证
    - 命令：`python3 scripts/spec_init.py --root /private/tmp/spec-mode-test/specs --name undo-redo-support --source-text ... --workflow requirements-first`
    - 结果：生成 `/private/tmp/spec-mode-test/specs/undo-redo-support/spec`
    - _需求：2、6_

  - [x] 6.2 运行 lint 验证
    - 命令：`python3 scripts/spec_lint.py /private/tmp/spec-mode-test/specs/undo-redo-support/spec`
    - 结果：返回 0；仅提示模板中仍有待确认项
    - _需求：6_

  - [x] 6.3 运行 status 验证
    - 命令：`python3 scripts/spec_status.py /private/tmp/spec-mode-test/specs/undo-redo-support/spec --json`
    - 结果：正确统计 `## 任务` 段内 7 个 pending task
    - _需求：5、6_

- [x] 7. 优化确认与选择器能力
  - [x] 7.1 更新 `SKILL.md` 的低假设规则
    - 增加 Confirmation First 规则
    - 要求缺少关键事实时向用户提问
    - 要求每份文档生成后展示全文并确认
    - 文件：`SKILL.md`
    - 验证：人工检查
    - _需求：7、8_

  - [x] 7.2 更新完整流程参考文档
    - 增加文档确认 prompt 规则
    - 增加 tasks 执行前确认规则
    - 文件：`references/workflow.md`
    - 验证：人工检查
    - _需求：7、8_

  - [x] 7.3 实现 CLI 选择器脚本
    - 支持 TTY 上下键/回车
    - 支持非 TTY 编号输入 fallback
    - 支持 `--json` 和 `--print-default`
    - 文件：`scripts/spec_choice.py`
    - 验证：`python3 scripts/spec_choice.py --title ... --option ... --print-default --json`
    - _需求：7、8_

  - [x] 7.4 移除模板中的默认假设表达
    - 将 `requirements.md` 模板中的“假设”替换为待确认问题
    - 增加阶段确认提示
    - 文件：`assets/templates/requirements.md`
    - 文件：`assets/templates/design.md`
    - 文件：`assets/templates/tasks.md`
    - 文件：`references/templates.md`
    - 验证：人工检查
    - _需求：7、8_

- [x] 8. 修正目录结构，不再生成最后的 `spec/` 文件夹
  - [x] 8.1 更新 `spec_init.py`
    - 将输出从 `<root>/<slug>/spec/` 改为 `<root>/<slug>/`
    - 文件：`scripts/spec_init.py`
    - 验证：临时目录初始化
    - _需求：2、6_

  - [x] 8.2 更新 skill 和参考文档中的目录规则
    - 文件：`SKILL.md`
    - 文件：`references/workflow.md`
    - 文件：`references/kiro-sample-analysis.md`
    - 验证：人工检查
    - _需求：2_

  - [x] 8.3 将当前项目自举 spec 移到新结构
    - 从 `specs/spec-mode-skill/spec/` 移到 `specs/spec-mode-skill/`
    - 验证：`python3 scripts/spec_lint.py specs/spec-mode-skill`
    - _需求：2_

- [x] 9. 收窄 spec mode 触发条件
  - [x] 9.1 更新 `SKILL.md` activation guard
    - 只有 `/spec`、`/spec-mode` 或明确说使用 spec 模式时启用
    - 普通 coding、planning、requirements、design docs、tasks、bugfix 请求不得自动启用
    - 文件：`SKILL.md`
    - 验证：人工检查
    - _需求：1_

  - [x] 9.2 更新流程参考和项目 spec
    - 文件：`references/workflow.md`
    - 文件：`specs/spec-mode-skill/requirements.md`
    - 文件：`specs/spec-mode-skill/design.md`
    - 文件：`specs/spec-mode-skill/tasks.md`
    - 验证：`python3 scripts/spec_lint.py specs/spec-mode-skill`
    - _需求：1_

- [x] 10. 优化文档确认展示，避免默认粘贴全文
  - [x] 10.1 更新确认规则
    - 默认只显示文档路径、概要、关键改动点和待确认问题
    - 增加 `查看全文` 选项
    - 文件：`SKILL.md`
    - 文件：`references/workflow.md`
    - _需求：8_

  - [x] 10.2 更新项目 spec
    - 将“展示完整内容”改为“摘要确认，按需查看全文”
    - 文件：`specs/spec-mode-skill/requirements.md`
    - 文件：`specs/spec-mode-skill/design.md`
    - 文件：`specs/spec-mode-skill/tasks.md`
    - 验证：`python3 scripts/spec_lint.py specs/spec-mode-skill`
    - _需求：8_

- [x] 11. 将确认动作改为优先使用 CLI 选择器
  - [x] 11.1 更新 `SKILL.md`
    - 增加 Interactive Selectors 章节
    - 要求每个确认点优先调用 `scripts/spec_choice.py`
    - 文件：`SKILL.md`
    - _需求：9_

  - [x] 11.2 更新流程参考
    - 明确 selector 结果如何驱动下一步
    - 文件：`references/workflow.md`
    - _需求：9_

  - [x] 11.3 更新项目 spec
    - 增加选择器确认需求
    - 更新设计和任务记录
    - 文件：`specs/spec-mode-skill/requirements.md`
    - 文件：`specs/spec-mode-skill/design.md`
    - 文件：`specs/spec-mode-skill/tasks.md`
    - 验证：`python3 scripts/spec_choice.py --title ... --print-default --json`
    - _需求：9_

## 验收

- [x] Skill 可通过 `SKILL.md` 安装和触发。
- [x] `/spec` 命令约定已写入 skill。
- [x] 文档目录为当前项目 `specs/<具体需求名>/`，不使用 `.kiro`。
- [x] 已参考 Kiro 样例文档结构。
- [x] 已提供脚本辅助初始化、lint 和状态查看。
- [x] 已提供 CLI 选择器辅助 workflow、文档确认和 task 执行确认。
- [x] 已生成当前项目自身 spec 文档。
