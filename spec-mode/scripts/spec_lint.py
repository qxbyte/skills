#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


TASK_RE = re.compile(r"^\s*-\s*\[( |x|~|\*|-)\]\s+(.+)$", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def task_section(text: str) -> str:
    start = text.find("## 任务")
    if start == -1:
        return text
    tail = text[start:]
    end_match = re.search(r"\n##\s+", tail[len("## 任务"):])
    if not end_match:
        return tail
    return tail[: len("## 任务") + end_match.start()]


def lint(spec_dir: Path) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []

    req = spec_dir / "requirements.md"
    bug = spec_dir / "bugfix.md"
    design = spec_dir / "design.md"
    tasks = spec_dir / "tasks.md"
    config = spec_dir / ".config.json"

    if req.exists() and bug.exists():
        errors.append("Spec should not contain both requirements.md and bugfix.md.")
    if not req.exists() and not bug.exists():
        errors.append("Missing requirements.md or bugfix.md.")
    if not design.exists():
        errors.append("Missing design.md.")
    if not tasks.exists():
        errors.append("Missing tasks.md.")
    if not config.exists():
        warnings.append("Missing .config.json.")

    first_doc = bug if bug.exists() else req
    if first_doc and first_doc.exists():
        text = read(first_doc)
        if "SHALL" not in text:
            warnings.append(f"{first_doc.name} has no EARS-style SHALL criteria.")
        placeholder_markers = ["待补充", "[问题]", "[需求", "[触发条件]", "[期望行为]"]
        if any(marker in text for marker in placeholder_markers):
            warnings.append(f"{first_doc.name} still contains template placeholder markers.")

    if design.exists():
        text = read(design)
        for heading in ["## 概述", "## 架构", "## 测试策略"]:
            if heading not in text:
                warnings.append(f"design.md is missing {heading}.")

    if tasks.exists():
        text = read(tasks)
        section = task_section(text)
        task_matches = list(TASK_RE.finditer(section))
        if not task_matches:
            errors.append("tasks.md has no checkbox tasks.")
        if "验证：" not in section and "Validation:" not in section:
            warnings.append("tasks.md does not contain validation notes.")
        if "_需求：" not in section and "Requirements:" not in section and "Behavior:" not in section:
            warnings.append("tasks.md does not contain requirement traceability.")

    return [f"ERROR: {item}" for item in errors] + [f"WARNING: {item}" for item in warnings]


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a spec-mode folder.")
    parser.add_argument("spec_dir", type=Path)
    args = parser.parse_args()
    messages = lint(args.spec_dir)
    if messages:
        print("\n".join(messages))
    else:
        print("Spec lint passed.")
    return 1 if any(msg.startswith("ERROR:") for msg in messages) else 0


if __name__ == "__main__":
    raise SystemExit(main())
