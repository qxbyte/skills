#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: scripts/harness-new-handoff.sh <task-slug>" >&2
  exit 1
fi

slug="$1"
case "$slug" in
  *[!a-zA-Z0-9._-]*)
    echo "Task slug may only contain letters, numbers, dots, underscores, and hyphens." >&2
    exit 1
    ;;
esac

mkdir -p handoffs
path="handoffs/${slug}.md"

if [ -e "$path" ]; then
  echo "Handoff already exists: $path" >&2
  exit 1
fi

today="$(date +%Y-%m-%d)"

cat > "$path" <<EOF
# ${slug} Handoff

日期：${today}

## 当前状态

[完成到哪里，哪些已验证]

## 完成范围

- [已完成事项]

## 非范围

- [本轮未做事项]

## 关键文件

- [文件]：[作用]

## 决策记录

- [决策]：[原因]

## 验证结果

| 检查项 | 命令或步骤 | 结果 | 证据 |
| --- | --- | --- | --- |
| [检查项] | \`[命令]\` | [通过/失败/未运行] | [摘要] |

## 未覆盖项

- [未覆盖项]：[原因]

## 剩余风险

- [风险]：[缓解方式]

## 人工 double check

- [ ] 需求理解正确
- [ ] 范围没有漂移
- [ ] 验收标准逐条覆盖
- [ ] 验证结果可信
- [ ] 剩余风险可接受

## 继续工作的入口

- [下一步命令/文件/测试/PR]
EOF

echo "Created $path"
