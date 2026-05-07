# Spec Mode Workflow

This reference expands the behavior required by `SKILL.md`.

## 0. Activation Guard

This workflow is opt-in only.

Run it when the user explicitly invokes `/spec`, `/spec-mode`, or clearly says to use spec mode. Do not infer spec mode from ordinary requests for coding, planning, design, requirements, documentation, bug fixing, or task lists.

Hard rule: `/spec` and `/spec-mode` always activate the spec workflow, including requests to inspect, modify, or improve the `spec-mode` skill itself. Do not use the "modify the skill itself" case to skip requirements, design, tasks, or confirmation gates after an explicit spec command.

Command compliance rule: when any standard spec command is triggered, the assistant must follow the corresponding workflow exactly. No phases, phase gates, or confirmation steps may be skipped for any reason — not because the requirement seems simple, the user appears to already know the design, or any other inferred justification. Commands are absolute. The assistant's judgment cannot override a command.

Exception for non-command requests: if a persistent spec-mode session is already active for the current conversation/session, continue routing follow-up messages through spec-mode until the user ends that session.

If the request does not explicitly activate spec mode, do not create a spec directory and do not run the phase-gated workflow.

## 1. `/spec` Intake

Parse user input as:

```text
/spec <requirement-or-path> [extra instructions]
/spec-mode <requirement-or-path> [extra instructions]
/spec --persist <requirement-or-path> [extra instructions]
/spec-continue [spec-name-or-dir]
/spec-status
/spec-end
```

Intake rules:

- If `<requirement-or-path>` points to a readable file, summarize it and use it as the source requirement.
- If it is prose, use it directly.
- Extract likely requirement name, project/document root hints, workflow hints, constraints, and validation expectations.
- If the user only gives a root directory and no requirement, ask for the requirement.
- Do not invent missing scope, business rules, UI behavior, data fields, acceptance criteria, or validation commands. Ask for clarification when those details affect the resulting document.
- If there are multiple unclear points, group them into a compact confirmation list and ask before generating the next document.

Persistent command rules:

- `/spec <requirement>` — one-shot mode. Runs the structured workflow without creating or updating `.active-spec-mode.json`.
- `/spec --persist <requirement>` — persistent mode. Initializes the spec and starts an active session.
- `/spec-continue [name]` — resumes or switches the current session to a spec and runs the mandatory context loading protocol. If no active pointer and no name is given, list all specs under the document root for the user to choose.
- `/spec-status` — prints the current session, spec path, phase, task counts, and active pointer file.
- `/spec-end` — ends only the current session and does not delete or modify other sessions.

## 1.1 Persistent Session Model

Persistent mode exists to support cross-session continuation and safe parallel specs. It is explicit and structured, not an implicit natural-language guess.

State files:

```text
<document-root>/
├── .active-spec-mode.json
└── <requirement-name>/
    ├── requirements.md or bugfix.md
    ├── design.md
    ├── tasks.md
    └── .config.json
```

`.active-spec-mode.json` is keyed by `sessionId`, so multiple windows can work on different specs under the same document root:

```json
{
  "version": 1,
  "documentRoot": "<vault>/spec-in/<os>-<user>/specs",
  "updatedAt": "2026-05-06T00:00:00Z",
  "sessions": {
    "window-a": {
      "sessionId": "window-a",
      "specId": "uuid",
      "specDir": "<vault>/spec-in/<os>-<user>/specs/undo-redo",
      "status": "active",
      "currentPhase": "tasks"
    }
  }
}
```

Each spec folder's `.config.json` stores its own lifecycle and session map. The active pointer and spec config must agree on `specId` before any document is loaded or edited.

Boundary rules:

1. A session can point to only one active spec at a time.
2. Multiple sessions may point to the same spec only if the user intentionally chooses that.
3. Switching a session never changes other sessions.
4. Ending a session never deletes spec documents and never ends other sessions.
5. Follow-up updates must touch only the selected spec folder.
6. If `specId`, `documentRoot`, or `specDir` validation fails, stop before reading or editing spec documents.

Use `scripts/spec_session.py` for lifecycle operations. Prefer simple defaults for single-window use; use explicit `--session` ids when multiple windows/specs are active.

At the end of every assistant response while persistent mode is active, include this exact single-line footer — no variations:

```
─── spec-mode ─── spec: <slug> | session: <sessionId> | phase: <phase> | /spec-end 退出
```

When the user provides natural-language follow-up in an active persistent session, apply document-first discipline — write the document update before continuing discussion or implementation:

- Requirement scope change → write `requirements.md` or `bugfix.md` first; then evaluate whether `design.md` and `tasks.md` need updates.
- Technical strategy change → write `design.md` first; then evaluate task impact.
- New work items → write to `tasks.md` first, preserving requirement traceability.
- Execution requests → mark the task `[~]` in `tasks.md` before editing code; mark `[x]` only after validation.
- Acceptance feedback → update task/review state in `tasks.md` inside the active spec only.

Document-first is non-negotiable. If the user asks to skip writing and proceed directly, acknowledge the request, write the document first, then proceed.

## 2. Choice Prompt

When the workflow is unclear, present a compact choice prompt.

Recommended options:

| Option | When to choose |
| --- | --- |
| Requirements | Feature request where desired behavior is clearer than architecture. Recommended by default. |
| Technical Design | Architecture, low-level design, algorithms, APIs, or non-functional constraints are primary. |
| Bugfix | A defect, regression, failing test, incident, or incorrect behavior is described. |

If the client supports interactive selections, use them. If running in a terminal, prefer:

```text
python3 scripts/spec_choice.py --title "What do you want to start with?" \
  --option "Requirements::Begin by gathering and documenting requirements::recommended" \
  --option "Technical Design::Begin with the technical design, then derive requirements" \
  --option "Bugfix::Document current, expected, and unchanged behavior"
```

If the selector is unavailable, ask the user to reply with a number.

Selectors are preferred over plain text confirmation. Use plain text only when tool execution is unavailable or the terminal cannot accept interactive input.

## 2.1 Document Confirmation Prompt

After every generated document:

1. Do not paste the full document by default.
2. Rely on the Codex client file diff/change preview as the detailed review surface.
3. Show the file path.
4. Show a concise summary.
5. Show key changed points.
6. Show unresolved questions, if any.
7. Ask for confirmation at the bottom.

Required selector when tool execution is available:

```text
python3 scripts/spec_choice.py --title "Confirm requirements.md?" \
  --option "确认::Accept this document and continue::recommended" \
  --option "查看全文::Print the full document in chat" \
  --option "继续沟通::I want to revise this document before continuing"
```

Rules:

- If the user chooses `确认`, proceed to the next phase.
- If the user chooses `查看全文`, print the full document and ask for confirmation again.
- If the user chooses `继续沟通`, ask for feedback or accept free-form feedback.
- Apply the feedback to the current document.
- Show the updated path, summary, key changed points, and unresolved questions again.
- Repeat until confirmed.

After `tasks.md` is confirmed, ask:

```text
python3 scripts/spec_choice.py --title "Start executing tasks?" \
  --option "开始 required tasks::Run required tasks only::recommended" \
  --option "开始 required + optional tasks::Run all tasks including optional tasks" \
  --option "暂不 coding::Stop after document generation"
```

The selector result controls the next step:

- `确认`: continue to the next document phase or task execution prompt.
- `查看全文`: display the document content, then run the confirmation selector again.
- `继续沟通`: collect feedback, update the current document, then run the confirmation selector again.
- `开始 required tasks`: execute required tasks only.
- `开始 required + optional tasks`: execute required and optional tasks.
- `暂不 coding`: stop after documenting the spec.

## 3. Directory Resolution

The output root is a document management root. The actual spec directory is:

```text
<document-root>/<requirement-name>/
```

Persistent mode also creates `<document-root>/.active-spec-mode.json`. This is a file, not a directory, and is the only hidden document-root state file used by this workflow.

Default selection (resolved by `spec_vault.py`, priority high → low):

1. Explicit `--root` argument.
2. `SPEC_MODE_ROOT` environment variable.
3. `~/.config/spec-mode/config.json` → `obsidianRoot`.
4. Auto-detected Obsidian vault → `<vault>/spec-in/<os>-<user>/specs`.
5. Current project directory: `<cwd>/specs`.
6. No project context: `~/new project/specs`.

Requirement name slug rules:

- Prefer a short semantic name over a raw prompt copy.
- Use lower-case ASCII where possible.
- Replace spaces and separators with `-`.
- Remove unsafe filename characters.
- Keep under 64 characters when possible.
- If the user's requirement is Chinese, use a stable pinyin/English-style slug if obvious; otherwise use a compact generated English slug.

## 4. Requirements-first Flow

1. Create `requirements.md`.
2. Include:
   - 简介
   - 词汇表
   - 需求
   - 用户故事
   - EARS 验收标准
   - 边界情况
   - 非功能需求
   - 待确认问题
3. If the requirement has unresolved details, ask the user before filling them with assumptions.
4. Stop for review and show path, summary, key changed points, and unresolved questions.
5. After confirmation, create `design.md`.
6. Stop for review and show path, summary, key changed points, and unresolved questions.
7. After confirmation, create `tasks.md`.
8. Stop for review and show path, summary, key changed points, and unresolved questions.
9. Ask whether to execute tasks.

## 5. Technical-design-first Flow

1. Create `design.md` first.
2. Choose design level:
   - High level: architecture, components, interactions, system qualities.
   - Low level: algorithms, interfaces, data structures, protocol details.
3. Stop for review and show path, summary, key changed points, and unresolved questions.
4. Derive `requirements.md` from the approved design.
5. Create `tasks.md`.
6. Display each generated document and confirm before continuing.
7. Ask whether to execute tasks.

## 6. Bugfix Flow

1. Create `bugfix.md`.
2. Capture:
   - Current Behavior
   - Expected Behavior
   - Unchanged Behavior
   - Reproduction
   - Evidence
   - Impact
3. Investigate code before claiming root cause.
4. Create `design.md` with root cause status, fix strategy, regression risks, and testing strategy.
5. Create `tasks.md` with:
   - reproduction test first
   - minimal fix second
   - unchanged behavior regression tests third
   - final validation checkpoint
6. Display and confirm each generated document before moving to the next phase.

## 7. Task Execution

Before editing code:

1. Resolve the selected spec directory from the command or active session.
2. Validate `specId`, `documentRoot`, and `specDir` boundaries.
3. Load every file in that spec directory only.
4. Find target task or next pending required task.
5. Update that task marker to `[~]`.
6. Implement only the linked scope.
7. Run validation.
8. Mark `[x]` only when validation passes.
9. If blocked, leave `[ ]` or `[~]` and add a note with the blocker.

Task markers:

```text
[ ] pending
[~] in progress
[x] completed
[-] skipped or intentionally not applicable
[*] optional
```

## 8. Acceptance

Final acceptance must include:

- Documents created or updated.
- Tasks completed.
- Validation commands and results.
- Any skipped validation.
- Remaining risks or open questions.
- Persistent session footer when the session remains active, including `/spec-end`.

## 9. /spec-continue Context Loading Protocol

When the user triggers `/spec-continue`, the following steps are mandatory in order. None may be skipped.

1. **Resolve target spec**: use the current session's active pointer from `.active-spec-mode.json`; if the user provided a name or path, use that; if neither exists, run `spec_session.py list --root <document-root>` and present the list.
2. **Validate boundaries**: run `spec_session.py status` to confirm `specId` in the active pointer matches `.config.json`. If they differ, stop and report a boundary error.
3. **Load documents**: run `python3 scripts/spec_session.py load <spec-dir>` and capture the output.
4. **Present context**: display the loaded summary to the user before any other response:
   ```
   已加载 spec: <slug>
     specId:  <id>
     phase:   <phase>
     session: <sessionId> (<status>)

     <req-doc>     ← N 条验收标准  |  修改: <time>
     design.md     ←               |  修改: <time>
     tasks.md      ← N/M 已完成, P 待处理  |  修改: <time>
   ```
5. **Activate session**: run `spec_session.py continue <spec-dir> --session <id>` to update the active pointer.
6. **Output footer** and await user instruction.

## 10. Boundary Anti-contamination Rules

Enforced by `scripts/spec_session.py` for every continue, switch, edit, and end operation:

1. `specDir` must be inside `documentRoot`. Refuse if not.
2. Active pointer `specId` must match `<spec-dir>/.config.json`. Refuse if not.
3. Only files inside the selected spec folder are treated as active spec documents.
4. Changes to one spec never update another spec's documents, config, task state, or active pointer entry.
5. All writes to `.active-spec-mode.json` use atomic temp-file + `os.replace()` to prevent concurrent corruption.

## Interactive Selectors

Run the following selector commands at each decision point. Use a TTY so the user can navigate with ↑/↓ and Enter; fall back to numbered choices if not interactive.

**Workflow type selector** (before creating the first document):

```text
python3 scripts/spec_choice.py --title "What do you want to start with?" \
  --option "Requirements::Begin by gathering and documenting requirements::recommended" \
  --option "Technical Design::Begin with the technical design, then derive requirements" \
  --option "Bugfix::Document current, expected, and unchanged behavior"
```

**Document confirmation selector** (after generating or updating each document — replace filename in title):

```text
python3 scripts/spec_choice.py --title "确认 requirements.md？" \
  --option "确认::继续生成下一阶段文档::recommended" \
  --option "查看全文::在聊天中展示完整文档" \
  --option "继续沟通::先根据反馈修改当前文档"
```

**Task execution selector** (after tasks.md is confirmed):

```text
python3 scripts/spec_choice.py --title "是否开始执行 tasks？" \
  --option "开始 required tasks::只执行必需任务::recommended" \
  --option "开始 required + optional tasks::执行必需任务和可选任务" \
  --option "暂不 coding::只保留文档，不开始实现"
```

## Persistent Sessions — Verification Checklist and Routing

**Before continuing, switching, editing, or ending a persistent spec, verify all of the following:**

1. The active pointer's `specId` matches `<spec-dir>/.config.json`.
2. The `specDir` is inside the active pointer's `documentRoot`.
3. Only files inside the selected spec folder are treated as the active spec documents.
4. Changes to one spec never update another spec's documents, config, task state, or active pointer entry.

**Natural-language follow-up routing in an active session:**

| Intent | Action |
|--------|--------|
| Requirement change | Update `requirements.md` or `bugfix.md`, then check whether `design.md` and `tasks.md` are stale |
| Design change | Update `design.md`, then check whether `tasks.md` is stale |
| Task change | Update `tasks.md`, preserve `_需求：..._` traceability |
| Execution request | Load only active spec's documents, execute selected or next pending task |
| Acceptance feedback | Update task/review state, add regression or follow-up tasks if needed |

## Context Loading for /spec-continue — Full Protocol

When the user triggers `/spec-continue`, all six steps are mandatory and must not be skipped or silenced:

1. Resolve the target spec using the first match found:
   a. Spec name or path provided by the user.
   b. Active pointer in `.active-spec-mode.json` for the current session.
   c. Scan the document root for all subdirectories that contain a `.config.json` — these are all available specs, regardless of whether they were created in one-shot or persistent mode. Present the list and ask the user to choose.
2. Validate `specId` consistency: read `.config.json` in the resolved spec dir. If an active pointer exists for this session, verify `specId` matches. If they differ, stop and report a boundary error — do not proceed. If no active pointer exists (e.g. one-shot spec), skip this check and proceed.
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

The spec documents are the cross-session memory; loading them is how continuity works.

## Phase Gates — Detailed Sub-steps

**Output order within each confirmation step (strictly follow this order):**

1. Generate or update the document (write the file).
2. **First:** show in the agent's text response — document path, concise summary, key changed points, unresolved questions.
3. **Then:** show the confirmation options (try `spec_choice.py`; if it exits with code 2 due to non-interactive stdin, output the numbered options as plain text instead).
4. **End the turn.** Do not continue to the next phase in the same response.

The user's next reply drives the next action:

- **"确认" / "1" / "confirm"** → proceed to the next phase.
- **"查看全文" / "2"** → read and display the full document, then show confirmation options again. End the turn.
- **"继续沟通" / "3" / any feedback** → update the document, show revised summary and options. End the turn.

Full phase sequence:

1. Generate or update `requirements.md` (feature) or `bugfix.md` (bugfix). Show summary + options. End turn. Wait for confirm.
2. Only after Confirm: generate or update `design.md`. Show summary + options. End turn. Wait for confirm.
3. Only after Confirm: generate or update `tasks.md`. Show summary + options. End turn. Wait for confirm.
4. Only after Confirm: show task execution options (required only / required + optional / hold). End turn. Wait for choice.
5. Only after explicit execution choice: begin coding tasks, validate, accept.

Do not skip any confirmation turn. If the user asks for one-pass generation, still show paths, summaries, key changed points per document, and mark `Review Status: unreviewed`.

## Implementation Execution — Full Steps

1. Resolve and validate the active spec session if persistent mode is active.
2. Load all spec files from the selected `<document-root>/<requirement-name>/`.
3. Identify the selected task ID or next pending required task.
4. Mark the task in `tasks.md` as in-progress using `[~]`.
5. Make the smallest code change that satisfies the linked requirement.
6. Run the validation command or the nearest relevant project test.
7. Mark completed with `[x]` only after validation passes.
8. If validation cannot run, keep the task incomplete and record the reason.
9. Finish with an acceptance summary: changed files, completed tasks, validation result, remaining risks.

**Task menu semantics:**
- "Run all tasks" means execute required tasks only unless the user says to include optional tasks.
- "Run required and optional tasks" includes optional tasks.
- Stop at checkpoints if validation fails or user confirmation is needed.
