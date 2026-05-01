# Spec Mode Workflow

This reference expands the behavior required by `SKILL.md`.

## 0. Activation Guard

This workflow is opt-in only.

Run it only when the user explicitly invokes `/spec`, `/spec-mode`, or clearly says to use spec mode. Do not infer spec mode from ordinary requests for coding, planning, design, requirements, documentation, bug fixing, or task lists.

If the request does not explicitly activate spec mode, do not create a spec directory and do not run the phase-gated workflow.

## 1. `/spec` Intake

Parse user input as:

```text
/spec <requirement-or-path> [extra instructions]
/spec-mode <requirement-or-path> [extra instructions]
```

Intake rules:

- If `<requirement-or-path>` points to a readable file, summarize it and use it as the source requirement.
- If it is prose, use it directly.
- Extract likely requirement name, project/document root hints, workflow hints, constraints, and validation expectations.
- If the user only gives a root directory and no requirement, ask for the requirement.
- Do not invent missing scope, business rules, UI behavior, data fields, acceptance criteria, or validation commands. Ask for clarification when those details affect the resulting document.
- If there are multiple unclear points, group them into a compact confirmation list and ask before generating the next document.

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

Default selection:

1. Explicit root from user.
2. Current project directory: `<cwd>/specs`.
3. No project context: `~/new project/specs`.

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

1. Load every file in the spec directory.
2. Find target task or next pending required task.
3. Update that task marker to `[~]`.
4. Implement only the linked scope.
5. Run validation.
6. Mark `[x]` only when validation passes.
7. If blocked, leave `[ ]` or `[~]` and add a note with the blocker.

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
