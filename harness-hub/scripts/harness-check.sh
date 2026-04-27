#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_root="$(cd "$script_dir/.." && pwd)"
failures=0

check_file() {
  if [ ! -f "$skill_root/$1" ]; then
    echo "Missing file: $1" >&2
    failures=$((failures + 1))
  fi
}

require_text() {
  file="$1"
  text="$2"
  if ! grep -Fq "$text" "$skill_root/$file"; then
    echo "Missing '$text' in $file" >&2
    failures=$((failures + 1))
  fi
}

check_file "SKILL.md"
check_file "references/usage-guide.md"
check_file "references/templates.md"
check_file "agents/openai.yaml"

check_file "docs/harness/architecture.md"
check_file "docs/harness/workflows.md"
check_file "docs/harness/quality-gates.md"
check_file "docs/harness/roles.md"
check_file "docs/harness/acceptance.md"

if [ -f "$skill_root/SKILL.md" ]; then
  require_text "SKILL.md" "name: harness-hub"
  require_text "SKILL.md" "description:"
  require_text "SKILL.md" "## 核心定位"
  require_text "SKILL.md" "## 任务分级"
  require_text "SKILL.md" "## 工作流"
  require_text "SKILL.md" "## 子代理协作"
  require_text "SKILL.md" "## 项目记忆"
  require_text "SKILL.md" "## 交付原则"
fi

if [ -f "$skill_root/references/templates.md" ]; then
  require_text "references/templates.md" "## 计划文件模板"
  require_text "references/templates.md" "## 验收文档模板"
  require_text "references/templates.md" "## 子代理任务检查清单模板"
  require_text "references/templates.md" "## 交接文档模板"
fi

if [ "$failures" -gt 0 ]; then
  echo "Harness check failed with $failures issue(s)." >&2
  exit 1
fi

echo "Harness check passed."
