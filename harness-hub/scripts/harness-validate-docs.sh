#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_root="$(cd "$script_dir/.." && pwd)"
failures=0

check_headings() {
  file="$1"
  if ! grep -Eq '^# ' "$file"; then
    echo "Missing top-level heading: $file" >&2
    failures=$((failures + 1))
  fi
}

check_relative_links() {
  file="$1"
  links="$(grep -Eo '\[[^]]+\]\([^):#][^)]*\)' "$file" || true)"
  printf '%s\n' "$links" | while IFS= read -r link; do
    [ "$link" = "" ] && continue
    target="$(printf '%s' "$link" | sed -E 's/^.*\]\(([^)#]+).*/\1/')"
    case "$target" in
      http*|mailto:*|/*)
        continue
        ;;
    esac
    base_dir="$(dirname "$file")"
    if [ ! -e "$base_dir/$target" ] && [ ! -e "$target" ]; then
      echo "Broken relative link in $file: $target" >&2
      exit 2
    fi
  done
}

while IFS= read -r file; do
  check_headings "$file"
  if ! check_relative_links "$file"; then
    failures=$((failures + 1))
  fi
done <<EOF
$(find "$skill_root" -name '*.md' ! -name 'harness-engineering-research.md' -type f | sort)
EOF

if [ "$failures" -gt 0 ]; then
  echo "Markdown validation failed with $failures issue(s)." >&2
  exit 1
fi

echo "Markdown validation passed."
