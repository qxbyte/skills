#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import spec_session


TASK_RE = re.compile(r"^\s*-\s*\[( |x|~|\*|-)\]\s+(.+)$", re.MULTILINE)


LABELS = {
    " ": "pending",
    "x": "completed",
    "~": "in_progress",
    "*": "optional",
    "-": "skipped",
}


def task_section(text: str) -> str:
    start = text.find("## 任务")
    if start == -1:
        return text
    tail = text[start:]
    end_match = re.search(r"\n##\s+", tail[len("## 任务"):])
    if not end_match:
        return tail
    return tail[: len("## 任务") + end_match.start()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize spec-mode status.")
    parser.add_argument("spec_dir", type=Path, nargs="?")
    parser.add_argument("--root", help="Document root. Required when spec_dir is omitted.")
    parser.add_argument("--session", help="Window/thread/session id. Defaults to SPEC_MODE_SESSION_ID or 'default'.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    session_id = spec_session.normalize_session_id(args.session)
    active_entry = None
    if args.spec_dir:
        spec_dir = args.spec_dir.expanduser().resolve()
    else:
        if not args.root:
            raise SystemExit("status without spec_dir requires --root")
        spec_dir, _active_config, active_entry = spec_session.resolve_active(
            Path(args.root).expanduser().resolve(),
            session_id,
        )

    tasks_path = spec_dir / "tasks.md"
    config_path = spec_dir / ".config.json"
    config = {}
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
    document_root = Path(config.get("documentRoot") or spec_dir.parent).expanduser().resolve()
    if active_entry is None:
        active_entry = spec_session.load_active(document_root).get("sessions", {}).get(session_id)
    session_config = (config.get("sessions") or {}).get(session_id, {})

    counts = {label: 0 for label in LABELS.values()}
    tasks: list[dict[str, str]] = []
    if tasks_path.exists():
        text = task_section(tasks_path.read_text(encoding="utf-8"))
        for match in TASK_RE.finditer(text):
            marker = match.group(1)
            title = match.group(2).strip()
            status = LABELS[marker]
            counts[status] += 1
            tasks.append({"status": status, "title": title})

    result = {
        "specDir": str(spec_dir),
        "workflowType": config.get("workflowType"),
        "specType": config.get("specType"),
        "requirementName": config.get("requirementName"),
        "specId": config.get("specId"),
        "sessionId": session_id,
        "persistentMode": config.get("persistentMode", False),
        "sessionStatus": session_config.get("status", config.get("sessionStatus")),
        "currentPhase": session_config.get("currentPhase", config.get("currentPhase")),
        "activeFile": str(spec_session.active_path(document_root)),
        "activePointer": active_entry,
        "counts": counts,
        "tasks": tasks,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Spec: {result['requirementName'] or spec_dir.name}")
        print(f"Path: {spec_dir}")
        print(f"Workflow: {result['workflowType'] or 'unknown'}")
        print(f"Type: {result['specType'] or 'unknown'}")
        print(f"Session: {session_id}")
        print(f"Session status: {result['sessionStatus'] or 'unknown'}")
        print(f"Phase: {result['currentPhase'] or 'unknown'}")
        print(f"Persistent: {str(result['persistentMode']).lower()}")
        print(
            "Tasks: "
            f"{counts['completed']} completed, "
            f"{counts['in_progress']} in progress, "
            f"{counts['pending']} pending, "
            f"{counts['optional']} optional, "
            f"{counts['skipped']} skipped"
        )
        print(f"Active file: {result['activeFile']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
