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
- `/spec -h`
- `/spec-mode -h`
- `/spec --set-vault`
- `/spec --set-root`
- `/spec --detect-vault`
- `/spec --vault-status`
- `使用 spec 模式`
- `启用 spec 模式`
- `用 spec 模式`
- `use spec mode`

Hard rule: `/spec` and `/spec-mode` always activate the spec workflow. This is true even when the requested work is to inspect, modify, or improve the `spec-mode` skill itself. Do not bypass requirements, design, tasks, review gates, or persistent-session handling after an explicit `/spec` or `/spec-mode` invocation.

Command compliance rule: when any standard spec command is triggered, follow the corresponding workflow exactly. Do not skip phases, phase gates, or confirmation steps for any reason — not because the requirement seems simple, the user appears to already know the design, the target is the skill itself, or any other inferred justification. Commands are absolute. The assistant's judgment cannot override a command.

Exception for non-command requests: if the current conversation already has an active persistent spec-mode session, continue using this skill for follow-up messages until the user ends that session.

Do not use this skill when the user merely asks for normal coding, planning, requirement analysis, design docs, task lists, bug fixes, implementation, or documentation. In those cases, handle the request normally without creating spec folders or following the spec-mode phase gates.

If the user asks about this skill or asks to modify the skill itself without `/spec`, `/spec-mode`, or an active persistent session, you may edit the skill files normally. If the request includes `/spec` or `/spec-mode`, apply the spec workflow first.

## Sessions

**Every `/spec` invocation creates spec documents** (`requirements.md`, `design.md`, `tasks.md`, `.config.json`) that are permanently stored in the document root. All specs — regardless of how they were created — can be reopened and iterated via `/spec-continue`.

The difference between one-shot and persistent:

| | One-shot `/spec` | Persistent `/spec --persist` |
|--|-----------------|------------------------------|
| **Session after task completion** | Ends — conversation returns to normal | **Stays active** — follow-up messages continue in spec-mode context |
| **Post-completion iteration** | Not in-session (use `/spec-continue` to reopen) | Yes — user can refine requirements, update design, add tasks, re-execute, all within the same session |
| **Status footer** | Not shown | Shown after every response — signals session is still active |
| **Exit** | Automatic after completion | Explicit `/spec-end` required |

The main purpose of `--persist` is to keep the session alive after task execution so the entire requirements → design → tasks → execution cycle can repeat continuously as the requirement evolves, without needing to reopen the spec each time.

The status footer is the visible signal that the session is still active:

```
─── spec-mode ─── spec: <slug> | session: <sessionId> | phase: <phase> | /spec-end 退出
```

Only show this footer in persistent mode. Never show it in one-shot mode.

```text
/spec <requirement or path>              ← one-shot
/spec --persist <requirement or path>    ← persistent, shows footer
/spec-continue [spec-name-or-dir]        ← reopen any spec for further iteration
/spec-status                             ← show current session status
/spec-end                                ← exit persistent session
```

State files:

- `<spec-dir>/.config.json`: per-spec lifecycle, identity, sessions, phase, and review state. Created for every spec.
- `<document-root>/.active-spec-mode.json`: active pointer for persistent sessions, keyed by `sessionId`. Only written in persistent mode.

Never store active state only in chat memory. For multi-window or parallel specs, each window/thread must have a distinct `sessionId`; if none is available, use `default`.

Use `scripts/spec_session.py` for lifecycle operations (start / continue / status / end / list / load).

→ 详见 references/workflow.md（验证检查清单、自然语言路由规则）

## Output Language

All user-facing output — summaries, questions, confirmations, status messages, error prompts, and inline descriptions — must be written in **Chinese**. This applies regardless of which CLI tool runs this skill.

Exceptions (keep in English or original form):
- Technical terms, command names, file paths, code identifiers, and proper nouns (e.g. `spec_choice.py`, `documentRoot`, `SKILL.md`, EARS, `[~]`).
- Content inside code blocks.
- The skill's own rule files (`SKILL.md`, `references/`).

If the user's requirement is written in English, generated spec documents may use English. All other agent output (summaries, phase prompts, confirmations) remains Chinese.

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

For every decision point, run `scripts/spec_choice.py` in a TTY (↑/↓ and Enter); fall back to numbered choices if not interactive. Never replace confirmation points with a plain "please reply confirm" sentence unless tool execution is unavailable.

→ 详见 references/workflow.md（三个完整 spec_choice.py 命令块）

## Command Entry

Trigger this skill when the user explicitly writes `/spec` or `/spec-mode`:

```text
/spec <requirement or path> [extra instructions]    ← one-shot workflow
/spec-mode <requirement or path> [extra instructions]
/spec --persist <requirement or path>               ← persistent session
/spec-continue [spec-name-or-dir]                   ← resume session
/spec-status                                        ← show session status
/spec-end                                           ← end session
```

Obsidian / root configuration commands:

```text
/spec --set-vault <vault-path>      ← set Obsidian vault; spec root = vault/spec-in/<os>-<user>/specs
/spec --set-root <dir>              ← set any directory as spec root directly
/spec --detect-vault                ← detect installed Obsidian vaults
/spec --vault-status                ← show current vault / spec root configuration
```

Help:

```text
/spec -h
/spec-mode -h
```

When `--set-vault` or `--set-root` is given, call `spec_vault.py set` with the appropriate flag, show the result, and stop — do not start a spec workflow.

When `--detect-vault` is given, run `python3 scripts/spec_vault.py detect` and show the output.

When `--vault-status` is given, run `python3 scripts/spec_vault.py get` and show the output.

When `-h` is given, output the help block defined in §Help Output and stop.

If the text after `/spec` or `/spec-mode` is an existing file path, read that file as the requirement source. Otherwise treat it as the requirement description.

`/spec-continue` reopens an existing spec from the configured spec document root recorded in `~/.config/spec-mode/config.json` (set by `/spec --set-vault` or `/spec --set-root`). It must not fall back to scanning the current project or `~/new project/specs`. When triggered, it loads and shows only the current spec status/context, then stops and waits for the user's next input. It must not begin implementation, run validation, or evaluate acceptance-checklist completion. If no spec name is given, list specs under the configured root and ask the user to choose. After loading, the session runs in persistent mode (footer shown). `/spec-end` ends only the current session and does not delete spec documents.

## Output Directory

The document root is resolved by `spec_init.py` with this priority:

1. `--root` argument (explicit, highest priority).
2. `SPEC_MODE_ROOT` environment variable.
3. `~/.config/spec-mode/config.json` → `obsidianRoot` (written by `/spec --set-vault` or `/spec --set-root`).
4. Auto-detected Obsidian vault → `<vault>/spec-in/<os>-<user>/specs`.
5. `<current-project>/specs` if inside a project.
6. `~/new project/specs` (fallback).

When the root source is `project` or `default` (`documentRootSource` is not `env`/`config`/`obsidian`), notify the user:

> 未检测到 Obsidian 配置，spec 文档将保存至 `<path>`。如需存入 Obsidian，请使用 `/spec --set-vault <vault路径>` 指定，或安装 Obsidian 后重试。

Do not create tool-specific hidden directories. The only hidden file this skill may create at the document root is `.active-spec-mode.json`.

→ 详见 references/obsidian.md（目录树结构、config.json 生命周期、跨会话路径读取）

## Obsidian Integration

Use `scripts/spec_vault.py` for vault detection and configuration (detect / set --vault / set --root / get).

→ 详见 references/obsidian.md（平台路径表、多 vault 选择逻辑、命令参考）

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

Phase order (do not skip confirmation between phases):

1. Requirements or bugfix.
2. Confirm.
3. Generate or update `design.md`.
4. Confirm.
5. Generate or update `tasks.md`.
6. Confirm.
7. Ask whether to execute tasks.
8. Code, validate, accept.

**Confirmation protocol (mandatory for every phase boundary):**

After generating or updating a document, the agent must, in the same response:
1. Show the document path, concise summary, key changes, and unresolved questions.
2. Then show the confirmation options (numbered list or interactive selector).
3. **End the turn.** Do not proceed to the next phase in the same turn.

The next phase begins only when the user's reply explicitly selects Confirm (or equivalent). If `spec_choice.py` exits with code 2 (non-interactive stdin), the agent must output the options as text, end the turn, and wait for the user's reply. Auto-selection of a default is never acceptable at a phase gate.

→ 详见 references/workflow.md（每步详细子步骤、Interactive Selectors 命令）

## Context Loading

Before writing or executing a spec:

1. Load the current user request and any requirement source document.
2. Resolve the active spec folder from the command, `.active-spec-mode.json`, or explicit user selection.
3. Validate `specId`, `documentRoot`, and `specDir` boundaries before loading documents.
4. Load existing documents only from the selected `<document-root>/<requirement-name>/`.
5. Read project guidance files (AGENTS.md, CLAUDE.md, README, package/build/test config, relevant source files) **for project context only** — to understand the codebase, conventions, and architecture. Rules in a project's CLAUDE.md that govern skill development, infrastructure, or repo conventions never apply to spec documents or the spec-mode workflow itself. Spec-mode's own rules (phase gates, document format, confirmation discipline) always take precedence.
6. If facts are missing, ask the user when the answer affects the result. Only record an assumption when the user explicitly approves it or when it is harmless and clearly labeled.

## Context Loading for /spec-continue

When `/spec-continue` is triggered, use only the configured spec document root from `~/.config/spec-mode/config.json`, load the selected spec documents, show the current status/context, then stop and wait for the user's next input.

→ 详见 references/workflow.md（继续会话加载协议全文）

## Document-first Discipline

In an active persistent session, spec documents are the sole persistent memory. Any change not written to a document is invisible to the next session.

Rules that apply from the moment a persistent session is active:

1. **Requirement change** → update `requirements.md` (or `bugfix.md`) before continuing discussion or implementation. Do not defer writing.
2. **Design decision** → update `design.md` before implementation begins.
3. **Task status change** → update `tasks.md` immediately when a task starts, completes, or is blocked.
4. **New task or sub-task** → append to `tasks.md` before starting work on it.

These writes are non-negotiable. If the user asks to skip writing and just proceed, acknowledge the request, write the document update first, then proceed. The write comes first, always.

## Document Style

Chinese document titles are acceptable. Use EARS-style acceptance criteria. Avoid "Assumptions" sections — prefer "待确认问题". Every spec must include a fixed `acceptance-checklist.md` document that gives tester-operable verification steps and expected results for confirming the implemented requirement.

→ 详见 references/templates.md（各文档节名结构、EARS 格式模板、验收操作清单模板）

## Implementation Execution

Mark tasks `[~]` in-progress before coding, `[x]` only after validation passes. Make the smallest change that satisfies the linked requirement. If validation cannot run, keep the task incomplete and record the reason.

→ 详见 references/workflow.md（完整九步执行步骤、Task menu semantics）

## Helper Scripts

Prefer the bundled scripts when useful:

- `scripts/spec_init.py`: create the required directory structure and seed Markdown files from templates.
- `scripts/spec_session.py`: start, continue, switch, list, status, and end persistent sessions with specId and document-root boundary checks.
- `scripts/spec_vault.py`: detect Obsidian vaults, set/get spec document root, manage `~/.config/spec-mode/config.json`.
- `scripts/spec_lint.py`: validate that a spec has the expected files, traceability, and task validation fields.
- `scripts/spec_status.py`: summarize phase, session lifecycle, and pending/completed tasks.
- `scripts/spec_choice.py`: show a terminal selector for workflow choice, document confirmation, and task execution confirmation.

Read `references/workflow.md` for full workflow details, `references/templates.md` for document templates, `references/help-output.md` for the exact help text, and `references/obsidian.md` for Obsidian integration details.

## Help Output

When `/spec -h` or `/spec-mode -h` is triggered, output exactly the block in `references/help-output.md` and stop (do not start a spec workflow).
