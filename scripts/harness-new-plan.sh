#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: scripts/harness-new-plan.sh <task-slug>" >&2
  exit 1
fi

slug="$1"
case "$slug" in
  *[!a-zA-Z0-9._-]*)
    echo "Task slug may only contain letters, numbers, dots, underscores, and hyphens." >&2
    exit 1
    ;;
esac

mkdir -p plans
path="plans/${slug}.md"

if [ -e "$path" ]; then
  echo "Plan already exists: $path" >&2
  exit 1
fi

today="$(date +%Y-%m-%d)"

cat > "$path" <<EOF
# ${slug} Plan

日期：${today}

## 背景

[需求来源、业务目标、当前问题]

## 目标

- [目标 1]
- [目标 2]

## 非目标

- [本轮明确不做的事情]

## 任务分级

[S / M / L]：[判断依据]

## 影响范围

- 代码：[模块/文件]
- 文档：[文档]
- 测试：[测试入口]
- 发布：[配置/CI/CD/迁移]

## 任务拆解

- [T1] [任务点]：验收 [标准]
- [T2] [任务点]：验收 [标准]

## 验证计划

- [检查项]：[命令/人工步骤]
- [检查项]：[命令/人工步骤]

## 风险与假设

- [风险/假设]：[处理方式]

## 验收标准

- [标准 1]
- [标准 2]
EOF

echo "Created $path"
