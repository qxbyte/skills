---
name: spec-mode
description: Specification-driven workflow for requirements, technical design, task lists, implementation, and acceptance. Use ONLY when the user explicitly invokes /spec or /spec-mode, or explicitly says to use spec mode. Do not use for ordinary coding, planning, requirements, design, or documentation requests unless spec mode is explicitly requested.
---

# Spec Mode

Use this skill to run a specification-driven workflow in CLI agents such as Codex and Claude Code. The workflow is file-first: generated Markdown documents are the source of truth, and coding starts only after requirements, design, and tasks are confirmed or explicitly skipped by the user.

## Activation Guard

This skill is opt-in only.

Use this skill only when the user's current request explicitly contains one of:

- `/spec`
- `/spec-mode`
- `使用 spec 模式`
- `启用 spec 模式`
- `用 spec 模式`
- `use spec mode`

Do not use this skill when the user merely asks for normal coding, planning, requirement analysis, design docs, task lists, bug fixes, implementation, or documentation. In those cases, handle the request normally without creating spec folders or following the spec-mode phase gates.

If the user asks about this skill or asks to modify the skill itself, you may edit the skill files, but do not apply the spec workflow to unrelated user work.

## Confirmation First

When this skill is active, minimize assumptions during requirement landing. If a missing detail affects scope, behavior, user experience, architecture, data, testing, acceptance, or task execution, ask the user instead of guessing.

Use a selector when the client or terminal can support it. Prefer `scripts/spec_choice.py` for CLI selection:

```text
python3 scripts/spec_choice.py --title "What do you want to start with?" \
  --option "Requirements::Begin by gathering and documenting requirements::recommended" \
  --option "Technical Design::Begin with the technical design, then derive requirements" \
  --option "Bugfix::Document current, expected, and unchanged behavior"
```

If the selector cannot run, present numbered choices and ask the user to reply with a number. Do not silently choose for the user unless the request is unambiguous.

## Interactive Selectors

For every spec-mode decision point, prefer the CLI selector over plain text prompts. Run it in a TTY when possible so the user can choose with ↑/↓ and Enter.

Use this confirmation selector after each generated or updated document:

```text
python3 scripts/spec_choice.py --title "确认 requirements.md？" \
  --option "确认::继续生成下一阶段文档::recommended" \
  --option "查看全文::在聊天中展示完整文档" \
  --option "继续沟通::先根据反馈修改当前文档"
```

Use the document name in the title, for example `确认 design.md？` or `确认 tasks.md？`.

Use this selector after `tasks.md` is confirmed:

```text
python3 scripts/spec_choice.py --title "是否开始执行 tasks？" \
  --option "开始 required tasks::只执行必需任务::recommended" \
  --option "开始 required + optional tasks::执行必需任务和可选任务" \
  --option "暂不 coding::只保留文档，不开始实现"
```

If the selector cannot run interactively, fall back to numbered choices with the same options. Never replace these confirmation points with a single "please reply confirm" sentence unless tool execution is unavailable.

## Command Entry

Trigger this skill when the user explicitly writes `/spec` or `/spec-mode`:

```text
/spec <requirement or requirement-document-path> [extra instructions]
/spec-mode <requirement or requirement-document-path> [extra instructions]
```

Examples:

```text
/spec 为 Markdown 编辑器增加撤销重做支持
/spec-mode 为 Markdown 编辑器增加撤销重做支持
/spec /absolute/path/to/requirement.md 使用 requirements-first
/spec 修复登录接口 500，不能改变现有错误码
```

If the text after `/spec` or `/spec-mode` is an existing file path, read that file as the requirement source. Otherwise treat it as the requirement description.

## Output Directory

The user provides a document management root. Under that root, create a folder per concrete requirement and put all spec-mode documents directly in that requirement folder:

```text
<document-root>/
└── <requirement-name>/
    ├── requirements.md    # feature specs
    ├── bugfix.md          # bugfix specs, instead of requirements.md
    ├── design.md
    ├── tasks.md
    └── .config.json
```

Default root selection:

1. If the user gives a root directory, use it.
2. Else if working inside a project, use `<current-project>/specs`.
3. Else create and use `~/new project/specs`.

Default to the user-provided document root. Do not create any tool-specific hidden directories.

## Workflow Selection

Before creating documents, classify the request:

- Feature + behavior-first requirement -> Requirements-first, recommended.
- Feature + architecture/design-first requirement -> Technical design first.
- Bug report, regression, failing test, production defect -> Bugfix spec.

If the choice materially affects the result, ask for input using a short selection prompt. In clients that support choice dialogs, present options similar to:

- Requirements: Begin by gathering and documenting requirements. Recommended for behavior-first feature work.
- Technical Design: Begin with the technical design, then derive requirements from that design.
- Bugfix: Begin by documenting current behavior, expected behavior, and unchanged behavior.

In plain CLI clients, ask a concise textual question and recommend Requirements unless the request is clearly design-first or bugfix. When possible, call `scripts/spec_choice.py` so the user can choose with number keys or arrow keys plus Enter.

## Phase Gates

Run the workflow in this order:

1. Generate or update `requirements.md` for feature specs, or `bugfix.md` for bugfix specs.
2. Do not paste the full document by default. Codex already shows file diffs/changes; use that as the detailed review surface.
3. Show only:
   - document path
   - concise summary
   - key changed points
   - unresolved questions
   - confirmation options
4. Offer a selector with:
   - Confirm
   - View full document
   - Continue discussing
5. If the user chooses View full document, read and display the full document, then ask for confirmation again.
6. If the user chooses Continue discussing or provides free-form feedback, update the document and show the path, summary, changed points, and confirmation options again.
7. Only after Confirm, generate or update `design.md`.
8. Repeat the same summary-confirmation loop for `design.md`.
9. Only after Confirm, generate or update `tasks.md`.
10. Repeat the same summary-confirmation loop for `tasks.md`.
11. After all documents are confirmed, ask whether to start executing tasks:
    - Start required tasks
    - Start required and optional tasks
    - Do not start coding yet
12. Execute coding tasks only after task confirmation and explicit execution confirmation.
13. Run validation and perform acceptance.

Do not skip the confirmation loop. If the user asks for one-pass generation, still show document paths, summaries, key changed points, and clearly mark `Review Status: unreviewed`.

Summary of the phase order:

1. Requirements or bugfix.
2. Confirm.
3. Generate or update `design.md`.
4. Confirm.
5. Generate or update `tasks.md`.
6. Confirm.
7. Ask whether to execute tasks.
8. Code, validate, accept.

## Context Loading

Before writing or executing a spec:

1. Load the current user request and any requirement source document.
2. Load existing documents from `<document-root>/<requirement-name>/` if present.
3. Read project guidance files such as `AGENTS.md`, `CLAUDE.md`, README, package/build/test config, and relevant source files.
4. Read project guidance files such as `CLAUDE.md`, `AGENTS.md`, or README when present.
5. If facts are missing, ask the user when the answer affects the result. Only record an assumption when the user explicitly approves it or when it is harmless and clearly labeled.

## Document Style

Use the following document structure:

- Chinese document titles are acceptable when the user's requirement is Chinese.
- `requirements.md` should include 简介, 词汇表, 需求, 用户故事, and EARS-style 验收标准.
- `design.md` should include 概述, 架构, 组件与接口, 数据模型, 错误处理, 测试策略, 正确性属性, 风险.
- `tasks.md` should include 概述, 任务, nested checkbox task items, `_需求：..._` traceability, optional markers, and checkpoint tasks.
- `bugfix.md` should distinguish Current Behavior, Expected Behavior, and Unchanged Behavior.
- Avoid "Assumptions" sections by default. Prefer "待确认问题" and ask before continuing.

Use EARS acceptance criteria where possible:

```text
WHEN [condition/event], THE [system/component] SHALL [expected behavior].
WHILE [state], THE [system/component] SHALL [expected behavior].
IF [condition], THEN THE [system/component] SHALL [expected behavior].
```

For bugfix unchanged behavior:

```text
WHEN [condition], THE [system/component] SHALL CONTINUE TO [existing behavior].
```

## Implementation Execution

When the user asks to code from a spec:

1. Load all spec files from `<document-root>/<requirement-name>/`.
2. Identify the selected task ID or next pending required task.
3. Mark the task in `tasks.md` as in-progress using `[~]`.
4. Make the smallest code change that satisfies the linked requirement.
5. Run the validation command or the nearest relevant project test.
6. Mark completed with `[x]` only after validation passes.
7. If validation cannot run, keep the task incomplete and record the reason.
8. Finish with an acceptance summary: changed files, completed tasks, validation result, remaining risks.

Task menu semantics:

- "Run all tasks" means execute required tasks only unless the user says to include optional tasks.
- "Run required and optional tasks" includes optional tasks.
- Stop at checkpoints if validation fails or user confirmation is needed.

## Helper Scripts

Prefer the bundled scripts when useful:

- `scripts/spec_init.py`: create the required directory structure and seed Markdown files from templates.
- `scripts/spec_lint.py`: validate that a spec has the expected files, traceability, and task validation fields.
- `scripts/spec_status.py`: summarize phase status and pending/completed tasks.
- `scripts/spec_choice.py`: show a terminal selector for workflow choice, document confirmation, and task execution confirmation.

Read `references/workflow.md` for the full workflow and `references/templates.md` for document templates.
