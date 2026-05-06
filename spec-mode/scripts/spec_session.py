#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ACTIVE_FILE = ".active-spec-mode.json"
SESSION_RE = re.compile(r"[^a-zA-Z0-9_.-]+")
PHASES = {
    "intake",
    "requirements",
    "bugfix",
    "design",
    "tasks",
    "implementation",
    "acceptance",
    "iteration",
    "ended",
}
TASK_RE = re.compile(r"^\s*-\s*\[( |x|~|\*|-)\]\s+(.+)$", re.MULTILINE)
TASK_LABELS = {" ": "pending", "x": "completed", "~": "in_progress", "*": "optional", "-": "skipped"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_session_id(raw: str | None) -> str:
    value = raw or os.environ.get("TERM_SESSION_ID") or "default"
    value = SESSION_RE.sub("-", value.strip()).strip("-._")
    return value[:80] or "default"


def read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def load_config(spec_dir: Path) -> dict[str, Any]:
    config_path = spec_dir / ".config.json"
    if not config_path.exists():
        raise SystemExit(f"Missing config: {config_path}")
    config = read_json(config_path, {})
    if not config.get("specId"):
        raise SystemExit(f"Missing specId in config: {config_path}")
    return config


def document_root_for(spec_dir: Path, config: dict[str, Any]) -> Path:
    root = config.get("documentRoot")
    if root:
        return Path(root).expanduser().resolve()
    return spec_dir.resolve().parent


def active_path(document_root: Path) -> Path:
    return document_root.resolve() / ACTIVE_FILE


def ensure_within_root(spec_dir: Path, document_root: Path) -> None:
    spec_resolved = spec_dir.resolve()
    root_resolved = document_root.resolve()
    try:
        spec_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise SystemExit(f"Spec dir is outside document root: {spec_resolved} not under {root_resolved}") from exc


def load_active(document_root: Path) -> dict[str, Any]:
    path = active_path(document_root)
    data = read_json(path, {})
    if not data:
        data = {
            "version": 1,
            "documentRoot": str(document_root.resolve()),
            "updatedAt": None,
            "sessions": {},
        }
    data.setdefault("version", 1)
    data["documentRoot"] = str(document_root.resolve())
    data.setdefault("sessions", {})
    return data


def save_active(document_root: Path, data: dict[str, Any]) -> None:
    data["documentRoot"] = str(document_root.resolve())
    data["updatedAt"] = now()
    write_json(active_path(document_root), data)


def active_sessions(config: dict[str, Any]) -> list[str]:
    sessions = config.get("sessions") or {}
    return [
        session_id
        for session_id, session in sessions.items()
        if session.get("status") == "active"
    ]


def update_config_session(
    spec_dir: Path,
    config: dict[str, Any],
    session_id: str,
    status: str,
    phase: str,
    reason: str | None = None,
) -> dict[str, Any]:
    timestamp = now()
    sessions = config.setdefault("sessions", {})
    session = sessions.setdefault(session_id, {"startedAt": timestamp})
    session["status"] = status
    session["currentPhase"] = phase
    session["lastActivityAt"] = timestamp
    if status == "active":
        session.setdefault("startedAt", timestamp)
        session["endedAt"] = None
        session["endedReason"] = None
    else:
        session["endedAt"] = timestamp
        session["endedReason"] = reason or "ended"

    config["currentSessionId"] = session_id
    config["sessionStatus"] = status
    config["currentPhase"] = phase
    config["lastActivityAt"] = timestamp
    config["persistentMode"] = bool(active_sessions(config))
    if status != "active" and not config["persistentMode"]:
        config["endedAt"] = timestamp
        config["endedReason"] = reason or "ended"
    else:
        config["endedAt"] = None
        config["endedReason"] = None
    write_json(spec_dir / ".config.json", config)
    return config


def entry_for(spec_dir: Path, config: dict[str, Any], session_id: str, phase: str) -> dict[str, Any]:
    return {
        "sessionId": session_id,
        "specId": config["specId"],
        "specDir": str(spec_dir.resolve()),
        "requirementName": config.get("requirementName"),
        "slug": config.get("slug") or spec_dir.name,
        "workflowType": config.get("workflowType"),
        "specType": config.get("specType"),
        "status": "active",
        "currentPhase": phase,
        "updatedAt": now(),
    }


def resolve_active(document_root: Path, session_id: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    active = load_active(document_root)
    entry = active.get("sessions", {}).get(session_id)
    if not entry or entry.get("status") != "active":
        raise SystemExit(f"No active spec session '{session_id}' under {document_root}")
    spec_dir = Path(entry["specDir"]).expanduser().resolve()
    config = load_config(spec_dir)
    ensure_within_root(spec_dir, document_root)
    if config.get("specId") != entry.get("specId"):
        raise SystemExit(
            f"Active pointer specId mismatch for session '{session_id}'. "
            f"Refusing to continue to avoid cross-spec contamination."
        )
    return spec_dir, config, entry


def command_start(args: argparse.Namespace) -> int:
    session_id = normalize_session_id(args.session)
    spec_dir = Path(args.spec_dir).expanduser().resolve()
    config = load_config(spec_dir)
    document_root = document_root_for(spec_dir, config)
    ensure_within_root(spec_dir, document_root)
    phase = args.phase or config.get("currentPhase") or "intake"
    if phase not in PHASES or phase == "ended":
        raise SystemExit(f"Invalid active phase: {phase}")

    config = update_config_session(spec_dir, config, session_id, "active", phase)
    active = load_active(document_root)
    active["sessions"][session_id] = entry_for(spec_dir, config, session_id, phase)
    save_active(document_root, active)

    print(json.dumps({"active": active["sessions"][session_id], "activeFile": str(active_path(document_root))}, ensure_ascii=False, indent=2))
    return 0


def command_status(args: argparse.Namespace) -> int:
    session_id = normalize_session_id(args.session)
    if args.spec_dir:
        spec_dir = Path(args.spec_dir).expanduser().resolve()
        config = load_config(spec_dir)
        document_root = document_root_for(spec_dir, config)
        ensure_within_root(spec_dir, document_root)
        entry = load_active(document_root).get("sessions", {}).get(session_id)
    else:
        if not args.root:
            raise SystemExit("status without spec_dir requires --root")
        document_root = Path(args.root).expanduser().resolve()
        spec_dir, config, entry = resolve_active(document_root, session_id)

    result = {
        "sessionId": session_id,
        "specDir": str(spec_dir),
        "specId": config.get("specId"),
        "requirementName": config.get("requirementName"),
        "workflowType": config.get("workflowType"),
        "specType": config.get("specType"),
        "persistentMode": config.get("persistentMode", False),
        "sessionStatus": (config.get("sessions") or {}).get(session_id, {}).get("status", config.get("sessionStatus")),
        "currentPhase": (config.get("sessions") or {}).get(session_id, {}).get("currentPhase", config.get("currentPhase")),
        "activeFile": str(active_path(document_root)),
        "activePointer": entry,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Session: {result['sessionId']}")
        print(f"Spec: {result['requirementName'] or Path(result['specDir']).name}")
        print(f"Path: {result['specDir']}")
        print(f"Status: {result['sessionStatus'] or 'unknown'}")
        print(f"Phase: {result['currentPhase'] or 'unknown'}")
        print(f"Persistent: {str(result['persistentMode']).lower()}")
        print(f"Active file: {result['activeFile']}")
    return 0


def command_end(args: argparse.Namespace) -> int:
    session_id = normalize_session_id(args.session)
    if args.spec_dir:
        spec_dir = Path(args.spec_dir).expanduser().resolve()
        config = load_config(spec_dir)
        document_root = document_root_for(spec_dir, config)
        ensure_within_root(spec_dir, document_root)
    else:
        if not args.root:
            raise SystemExit("end without spec_dir requires --root")
        document_root = Path(args.root).expanduser().resolve()
        spec_dir, config, _entry = resolve_active(document_root, session_id)

    update_config_session(spec_dir, config, session_id, "ended", "ended", args.reason)
    active = load_active(document_root)
    entry = active.get("sessions", {}).get(session_id)
    if entry:
        if entry.get("specId") != config.get("specId"):
            raise SystemExit(
                f"Active pointer specId mismatch for session '{session_id}'. "
                f"Refusing to end a different spec."
            )
        active["sessions"].pop(session_id, None)
        save_active(document_root, active)

    print(json.dumps({"sessionId": session_id, "specDir": str(spec_dir), "status": "ended"}, ensure_ascii=False, indent=2))
    return 0


def command_list(args: argparse.Namespace) -> int:
    document_root = Path(args.root).expanduser().resolve()
    active = load_active(document_root)
    sessions = active.get("sessions", {})
    if args.json:
        print(json.dumps({"documentRoot": str(document_root), "sessions": sessions}, ensure_ascii=False, indent=2))
    else:
        print(f"Document root: {document_root}")
        if not sessions:
            print("No active spec sessions.")
            return 0
        for session_id, entry in sorted(sessions.items()):
            print(
                f"- {session_id}: {entry.get('requirementName') or entry.get('slug')} "
                f"({entry.get('currentPhase')}, {entry.get('specDir')})"
            )
    return 0


def command_load(args: argparse.Namespace) -> int:
    spec_dir = Path(args.spec_dir).expanduser().resolve()
    config = load_config(spec_dir)
    document_root = document_root_for(spec_dir, config)
    ensure_within_root(spec_dir, document_root)

    def file_info(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {"exists": False}
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
        return {"exists": True, "modifiedAt": mtime, "text": path.read_text(encoding="utf-8")}

    req_info = file_info(spec_dir / "requirements.md")
    bug_info = file_info(spec_dir / "bugfix.md")
    design_info = file_info(spec_dir / "design.md")
    tasks_info = file_info(spec_dir / "tasks.md")

    req_doc = req_info if req_info["exists"] else bug_info
    req_name = "requirements.md" if req_info["exists"] else "bugfix.md"
    shall_count = 0
    req_open_questions = False
    if req_doc.get("exists"):
        shall_count = req_doc["text"].count("SHALL")
        req_open_questions = "待确认问题" in req_doc["text"]

    design_open_questions = False
    if design_info.get("exists"):
        design_open_questions = "待确认问题" in design_info["text"]

    counts: dict[str, int] = {label: 0 for label in TASK_LABELS.values()}
    counts["total"] = 0
    in_progress: list[str] = []
    if tasks_info.get("exists"):
        for match in TASK_RE.finditer(tasks_info["text"]):
            status_label = TASK_LABELS.get(match.group(1), "pending")
            counts["total"] += 1
            counts[status_label] += 1
            if status_label == "in_progress":
                in_progress.append(match.group(2).strip())

    result: dict[str, Any] = {
        "specDir": str(spec_dir),
        "slug": config.get("slug") or spec_dir.name,
        "specId": config.get("specId"),
        "requirementName": config.get("requirementName"),
        "currentPhase": config.get("currentPhase"),
        "sessionStatus": config.get("sessionStatus"),
        "currentSessionId": config.get("currentSessionId"),
        "lastActivityAt": config.get("lastActivityAt"),
        "documents": {
            req_name: {
                "exists": req_doc.get("exists", False),
                "modifiedAt": req_doc.get("modifiedAt"),
                "shallCount": shall_count,
                "hasOpenQuestions": req_open_questions,
            },
            "design.md": {
                "exists": design_info.get("exists", False),
                "modifiedAt": design_info.get("modifiedAt"),
                "hasOpenQuestions": design_open_questions,
            },
            "tasks.md": {
                "exists": tasks_info.get("exists", False),
                "modifiedAt": tasks_info.get("modifiedAt"),
                "counts": counts,
                "inProgress": in_progress,
            },
        },
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        slug = result["slug"]
        phase = result["currentPhase"] or "unknown"
        session_id = result["currentSessionId"] or "unknown"
        s_status = result["sessionStatus"] or "unknown"
        print(f"已加载 spec: {slug}")
        print(f"  specId:  {result['specId']}")
        print(f"  phase:   {phase}")
        print(f"  session: {session_id} ({s_status})")
        print()
        req_d = result["documents"][req_name]
        if req_d["exists"]:
            q = " | 有待确认问题" if req_d["hasOpenQuestions"] else ""
            print(f"  {req_name:<22} ← {req_d['shallCount']} 条验收标准{q}  |  修改: {req_d['modifiedAt']}")
        else:
            print(f"  {req_name:<22} ← 不存在")
        design_d = result["documents"]["design.md"]
        if design_d["exists"]:
            q = " | 有待确认问题" if design_d["hasOpenQuestions"] else ""
            print(f"  {'design.md':<22} ←{q}  |  修改: {design_d['modifiedAt']}")
        else:
            print(f"  {'design.md':<22} ← 不存在")
        tasks_d = result["documents"]["tasks.md"]
        if tasks_d["exists"]:
            c = tasks_d["counts"]
            prog = f", 进行中: {', '.join(tasks_d['inProgress'])}" if tasks_d["inProgress"] else ""
            print(f"  {'tasks.md':<22} ← {c['completed']}/{c['total']} 已完成, {c['pending']} 待处理{prog}  |  修改: {tasks_d['modifiedAt']}")
        else:
            print(f"  {'tasks.md':<22} ← 不存在")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage persistent spec-mode sessions.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    session_help = "Window/thread/session id. Defaults to $TERM_SESSION_ID or 'default'."

    start = subparsers.add_parser("start", help="Bind a session to a spec and mark it active.")
    start.add_argument("spec_dir")
    start.add_argument("--session", help=session_help)
    start.add_argument("--phase", choices=sorted(PHASES - {"ended"}), default="intake")
    start.set_defaults(func=command_start)

    cont = subparsers.add_parser("continue", help="Resume or switch the current session to a spec.")
    cont.add_argument("spec_dir")
    cont.add_argument("--session", help=session_help)
    cont.add_argument("--phase", choices=sorted(PHASES - {"ended"}), default="iteration")
    cont.set_defaults(func=command_start)

    status = subparsers.add_parser("status", help="Show session/spec lifecycle status.")
    status.add_argument("spec_dir", nargs="?")
    status.add_argument("--root", help="Document root used when spec_dir is omitted.")
    status.add_argument("--session", help=session_help)
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=command_status)

    end = subparsers.add_parser("end", help="End the active session without deleting spec documents.")
    end.add_argument("spec_dir", nargs="?")
    end.add_argument("--root", help="Document root used when spec_dir is omitted.")
    end.add_argument("--session", help=session_help)
    end.add_argument("--reason", default="user ended")
    end.set_defaults(func=command_end)

    list_cmd = subparsers.add_parser("list", help="List active sessions under a document root.")
    list_cmd.add_argument("--root", required=True)
    list_cmd.add_argument("--json", action="store_true")
    list_cmd.set_defaults(func=command_list)

    load_cmd = subparsers.add_parser("load", help="Load and summarize spec documents for context restoration.")
    load_cmd.add_argument("spec_dir")
    load_cmd.add_argument("--json", action="store_true")
    load_cmd.set_defaults(func=command_load)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
