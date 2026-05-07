#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import spec_session
import spec_vault


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "assets" / "templates"


def slugify(value: str) -> str:
    value = value.strip().lower()
    replacements = {
        "撤销": "undo",
        "重做": "redo",
        "登录": "login",
        "注册": "register",
        "用户": "user",
        "需求": "requirement",
        "修复": "fix",
        "错误": "bug",
        "项目": "project",
    }
    for source, target in replacements.items():
        value = value.replace(source, f" {target} ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value[:64].strip("-") or "new-spec")


def infer_name(text: str, explicit: str | None) -> tuple[str, str]:
    if explicit:
        slug = slugify(explicit)
        return explicit.strip(), slug

    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "new spec")
    first_line = re.sub(r"^/spec\s+", "", first_line).strip()
    first_line = re.sub(r"[/\\:*?\"<>|]+", " ", first_line)
    words = first_line[:80].strip()
    slug = slugify(words)
    return words or slug, slug


def resolve_document_root(root: str | None, project_dir: str | None) -> tuple[Path, str]:
    """Return (resolved_root, source_tag)."""
    if root:
        return Path(root).expanduser().resolve(), "explicit"
    vault_root, source = spec_vault.resolve_spec_root()
    if vault_root is not None:
        return vault_root, source
    if project_dir:
        return Path(project_dir).expanduser().resolve() / "specs", "project"
    cwd = Path.cwd().resolve()
    if cwd != Path.home().resolve():
        return cwd / "specs", "project"
    return Path.home().resolve() / "new project" / "specs", "default"


def read_source(args: argparse.Namespace) -> str:
    chunks: list[str] = []
    if args.source_file:
        chunks.append(Path(args.source_file).expanduser().read_text(encoding="utf-8"))
    if args.source_text:
        chunks.append(args.source_text)
    if not chunks:
        chunks.append("New spec initialized without a source requirement.")
    return "\n\n".join(chunks).strip()


def render(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def write_if_missing(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a Kiro-style spec-mode document folder.")
    parser.add_argument("--root", help="Document management root. The script creates <root>/<name>/.")
    parser.add_argument("--project-dir", help="Project directory. Used as <project-dir>/specs when --root is omitted.")
    parser.add_argument("--name", help="Concrete requirement name.")
    parser.add_argument("--source-text", help="Requirement text, usually the text after /spec.")
    parser.add_argument("--source-file", help="Path to a requirement source document.")
    parser.add_argument("--workflow", choices=["requirements-first", "design-first", "bugfix"], default="requirements-first")
    parser.add_argument("--spec-type", choices=["feature", "bugfix"], default="feature")
    parser.add_argument("--persistent", action="store_true", help="Bind this spec to an active persistent session.")
    parser.add_argument("--session", help="Window/thread/session id for persistent mode.")
    parser.add_argument(
        "--current-phase",
        choices=sorted(spec_session.PHASES - {"ended"}),
        default="intake",
        help="Initial phase for persistent mode.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated documents.")
    args = parser.parse_args()

    source = read_source(args)
    name, slug = infer_name(source, args.name)
    spec_type = "bugfix" if args.workflow == "bugfix" else args.spec_type
    document_root, root_source = resolve_document_root(args.root, args.project_dir)
    spec_dir = document_root / slug
    spec_dir.mkdir(parents=True, exist_ok=True)

    summary = source
    if len(summary) > 1200:
        summary = summary[:1200].rstrip() + "\n\n[Source truncated in seed document. Read the source file for full context.]"

    values = {
        "name": name,
        "slug": slug,
        "summary": summary,
        "workflow": args.workflow,
        "spec_type": "Bugfix" if spec_type == "bugfix" else "Feature",
    }

    created: list[str] = []
    first_doc = "bugfix.md" if spec_type == "bugfix" or args.workflow == "bugfix" else "requirements.md"
    for template_name, output_name in [
        (first_doc, first_doc),
        ("design.md", "design.md"),
        ("tasks.md", "tasks.md"),
    ]:
        template = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        target = spec_dir / output_name
        if write_if_missing(target, render(template, values), args.force):
            created.append(str(target))

    config = {
        "specId": str(uuid.uuid4()),
        "workflowType": args.workflow,
        "specType": spec_type,
        "documentRoot": str(document_root),
        "requirementName": name,
        "slug": slug,
        "sourceFile": str(Path(args.source_file).expanduser().resolve()) if args.source_file else None,
        "createdBy": "spec-mode",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "persistentMode": False,
        "sessionStatus": None,
        "currentSessionId": None,
        "currentPhase": None,
        "lastActivityAt": None,
        "endedAt": None,
        "endedReason": None,
        "sessions": {},
    }
    config_path = spec_dir / ".config.json"
    if write_if_missing(config_path, json.dumps(config, ensure_ascii=False, indent=2) + "\n", args.force):
        created.append(str(config_path))

    session: dict[str, object] | None = None
    if args.persistent:
        current_config = json.loads(config_path.read_text(encoding="utf-8"))
        session_id = spec_session.normalize_session_id(args.session)
        current_config = spec_session.update_config_session(
            spec_dir,
            current_config,
            session_id,
            "active",
            args.current_phase,
        )
        active = spec_session.load_active(document_root)
        active["sessions"][session_id] = spec_session.entry_for(
            spec_dir,
            current_config,
            session_id,
            args.current_phase,
        )
        spec_session.save_active(document_root, active)
        session = {
            "sessionId": session_id,
            "status": "active",
            "currentPhase": args.current_phase,
            "activeFile": str(spec_session.active_path(document_root)),
        }

    print(json.dumps({
        "specDir": str(spec_dir),
        "documentRoot": str(document_root),
        "documentRootSource": root_source,
        "created": created,
        "session": session,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
