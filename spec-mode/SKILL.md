---
name: spec-mode
description: Specification-driven workflow for requirements, technical design, task lists, implementation, acceptance, and ongoing spec iteration. Use when the user explicitly invokes /spec or /spec-mode, explicitly says to use spec mode, or the current conversation has an active persistent spec-mode session that has not been ended. Do not use for ordinary coding, planning, requirements, design, or documentation requests unless spec mode is explicitly requested or already active.
---

# Spec Mode

Use this skill to run a specification-driven workflow in CLI agents such as Codex and Claude Code. The workflow is file-first: generated Markdown documents are the source of truth, and coding starts only after requirements, design, and tasks are confirmed or explicitly skipped by the user.

## Activation Guard

This skill is opt-in only.

Use this skill when the user's current request explicitly contains one of:

- `/spec`
- `/spec-mode`
- `/spec-continue`
- `/spec-status`
- `/spec-end`
- `使用 spec 模式`
- `启用 spec 模式`
- `用 spec 模式`
- `use spec mode`

Hard rule: `/spec` and `/spec-mode` always activate the spec workflow. This is true even when the requested work is to inspect, modify, or improve the `spec-mode` skill itself. Do not bypass requirements, design, tasks, review gates, or persistent-session handling after an explicit `/spec` or `/spec-mode` invocation.

Command compliance rule: when any standard spec command is triggered, follow the corresponding workflow exactly. Do not skip phases, phase gates, or confirmation steps for any reason — not because the requirement seems simple, the user appears to already know the design, the target is the skill itself, or any other inferred justification. Commands are absolute. The assistant's judgment cannot override a command.

Exception for non-command requests: if the current conversation already has an active persistent spec-mode session, continue using this skill for follow-up messages until the user ends that session.

Do not use this skill when the user merely asks for normal coding, planning, requirement analysis, design docs, task lists, bug fixes, implementation, or documentation. In those cases, handle the request normally without creating spec folders or following the spec-mode phase gates.

If the user asks about this skill or asks to modify the skill itself without `/spec`, `/spec-mode`, or an active persistent session, you may edit the skill files normally. If the request includes `/spec` or `/spec-mode`, apply the spec workflow first.

## Persistent Sessions

Default `/spec` usage is one-shot: after document generation, implementation, and acceptance, the conversation returns to normal unless the user asks to continue.

Default `/spec <requirement>` is one-shot: it runs the structured requirements → design → tasks workflow without creating an active pointer or persistent state.

Use persistent mode only when the user explicitly uses `/spec --persist`. Keep the user-facing surface minimal:

```text
/spec <requirement or path>              ← one-shot, no active pointer
/spec --persist <requirement or path>    ← persistent, writes active pointer
/spec-continue [spec-name-or-dir]        ← resume or switch, loads context from documents
/spec-status                             ← show current session status
/spec-end                                ← end current session
```

Persistent mode uses two state files:

- `<spec-dir>/.config.json`: per-spec lifecycle, spec identity, sessions, phase, and review state.
- `<document-root>/.active-spec-mode.json`: document-root active pointer, keyed by `sessionId`.

Never store active state only in chat memory. For cross-session continuation, read `.active-spec-mode.json` or ask the user to provide/select a spec. For multi-window or parallel specs, each window/thread must have a distinct `sessionId`; if none is available, use `default` for simple single-window use and ask before switching away from an already active default session.

Before continuing, switching, editing, or ending a persistent spec, verify all of the following:

1. The active pointer's `specId` matches `<spec-dir>/.config.json`.
2. The `specDir` is inside the active pointer's `documentRoot`.
3. Only files inside the selected spec folder are treated as the active spec documents.
4. Changes to one spec never update another spec's documents, config, task state, or active pointer entry.

Use `scripts/spec_session.py` for lifecycle operations:

```text
python3 scripts/spec_session.py start    <spec-dir> --session <id> --phase requirements
python3 scripts/spec_session.py continue <spec-dir> --session <id>
python3 scripts/spec_session.py status   --root <document-root> --session <id>
python3 scripts/spec_session.py end      --root <document-root> --session <id>
python3 scripts/spec_session.py list     --root <document-root>
python3 scripts/spec_session.py load     <spec-dir>
```

`continue` resumes or switches the current session to a spec (replaces the former `switch` subcommand). `load` reads spec documents and outputs a structured context summary used by `/spec-continue` to restore cross-session memory.

When handling natural-language follow-up in an active persistent session, route it by intent:

- Requirement change -> update `requirements.md` or `bugfix.md`, then check whether `design.md` and `tasks.md` are stale.
- Design change -> update `design.md`, then check whether `tasks.md` is stale.
- Task change -> update `tasks.md` and preserve `_需求：..._` traceability.
- Execution request -> load only the active spec's documents and execute the selected or next pending task.
- Acceptance feedback -> update task/review state and add regression or follow-up tasks if needed.

After every response in an active persistent session, include a status footer using exactly this single-line format — no variations:

```
─── spec-mode ─── spec: <slug> | session: <sessionId> | phase: <phase> | /spec-end 退出
```

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
/spec --persist <requirement or requirement-document-path> [extra instructions]
/spec-continue [spec-name-or-dir]
/spec-status
/spec-end
```

Examples:

```text
/spec 为 Markdown 编辑器增加撤销重做支持
/spec-mode 为 Markdown 编辑器增加撤销重做支持
/spec /absolute/path/to/requirement.md 使用 requirements-first
/spec 修复登录接口 500，不能改变现有错误码
/spec --persist 为 Markdown 编辑器增加撤销重做支持
/spec-continue undo-redo-support
/spec-end
```

If the text after `/spec` or `/spec-mode` is an existing file path, read that file as the requirement source. Otherwise treat it as the requirement description.

`/spec-continue` resumes or switches the active spec for the current session. When triggered, it must run the context loading protocol (see §Context Loading for /spec-continue) before responding to any user request. If there is no active pointer and no spec name is given, list all specs under the document root and ask the user to choose. `/spec-end` ends only the current session and does not delete spec documents.

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

The document root may also contain:

```text
<document-root>/
└── .active-spec-mode.json    # active session pointers keyed by sessionId
```

Default root selection:

1. If the user gives a root directory, use it.
2. Else if working inside a project, use `<current-project>/specs`.
3. Else create and use `~/new project/specs`.

Default to the user-provided document root. Do not create tool-specific hidden directories. The only document-root hidden file this skill may create is `.active-spec-mode.json`, used to prevent cross-session and cross-spec contamination.

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
2. Resolve the active spec folder from the command, `.active-spec-mode.json`, or explicit user selection.
3. Validate `specId`, `documentRoot`, and `specDir` boundaries before loading documents.
4. Load existing documents only from the selected `<document-root>/<requirement-name>/`.
5. Read project guidance files such as `AGENTS.md`, `CLAUDE.md`, README, package/build/test config, and relevant source files.
6. If facts are missing, ask the user when the answer affects the result. Only record an assumption when the user explicitly approves it or when it is harmless and clearly labeled.

## Context Loading for /spec-continue

When the user triggers `/spec-continue`, the following steps are mandatory and must not be skipped or silenced:

1. Resolve the target spec: use the current session's active pointer, or the name provided by the user, or present a list from `spec_session.py list --root <document-root>`.
2. Validate `specId` consistency between the active pointer and `.config.json`. If they differ, stop and report a boundary error — do not proceed.
3. Run `python3 scripts/spec_session.py load <spec-dir>` and capture the output.
4. Present the loaded context to the user clearly:
   ```
   已加载 spec: <slug>
     specId:  <id>
     phase:   <phase>
     session: <sessionId> (<status>)

     <req-doc>     ← N 条验收标准  |  修改: <time>
     design.md     ←               |  修改: <time>
     tasks.md      ← N/M 已完成, P 待处理  |  修改: <time>
   ```
5. Activate the persistent session and output the footer.
6. Only then respond to the user's actual request or await instructions.

Do not skip step 3 or 4 under any circumstance. The spec documents are the cross-session memory; loading them is how continuity works.

## Document-first Discipline

In an active persistent session, spec documents are the sole persistent memory. Any change not written to a document is invisible to the next session.

Rules that apply from the moment a persistent session is active:

1. **Requirement change** → update `requirements.md` (or `bugfix.md`) before continuing discussion or implementation. Do not defer writing.
2. **Design decision** → update `design.md` before implementation begins.
3. **Task status change** → update `tasks.md` immediately when a task starts, completes, or is blocked.
4. **New task or sub-task** → append to `tasks.md` before starting work on it.

These writes are non-negotiable. If the user asks to skip writing and just proceed, acknowledge the request, write the document update first, then proceed. The write comes first, always.

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

1. Resolve and validate the active spec session if persistent mode is active.
2. Load all spec files from the selected `<document-root>/<requirement-name>/`.
3. Identify the selected task ID or next pending required task.
4. Mark the task in `tasks.md` as in-progress using `[~]`.
5. Make the smallest code change that satisfies the linked requirement.
6. Run the validation command or the nearest relevant project test.
7. Mark completed with `[x]` only after validation passes.
8. If validation cannot run, keep the task incomplete and record the reason.
9. Finish with an acceptance summary: changed files, completed tasks, validation result, remaining risks.

Task menu semantics:

- "Run all tasks" means execute required tasks only unless the user says to include optional tasks.
- "Run required and optional tasks" includes optional tasks.
- Stop at checkpoints if validation fails or user confirmation is needed.

## Helper Scripts

Prefer the bundled scripts when useful:

- `scripts/spec_init.py`: create the required directory structure and seed Markdown files from templates.
- `scripts/spec_session.py`: start, continue, switch, list, status, and end persistent sessions with specId and document-root boundary checks.
- `scripts/spec_lint.py`: validate that a spec has the expected files, traceability, and task validation fields.
- `scripts/spec_status.py`: summarize phase, session lifecycle, and pending/completed tasks.
- `scripts/spec_choice.py`: show a terminal selector for workflow choice, document confirmation, and task execution confirmation.

Read `references/workflow.md` for the full workflow and `references/templates.md` for document templates.
