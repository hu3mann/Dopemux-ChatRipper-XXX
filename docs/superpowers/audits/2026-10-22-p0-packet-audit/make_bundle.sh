#!/usr/bin/env bash
# Generate bundles/dnh-packaging-bundle.md from the dNh_CRM repo (read-only).
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
R=/Users/hue/code/dNh_CRM
OUT="$D/bundles/dnh-packaging-bundle.md"
mkdir -p "$D/bundles"
for f in pyproject.toml .python-version .github/workflows/ci.yml .github/workflows/release.yml uv.lock; do
  [[ -f "$R/$f" ]] || { echo "missing: $R/$f" >&2; exit 1; }
done
TMP="$OUT.tmp.$$"
trap 'rm -f "$TMP"' EXIT
sec() { printf '\n## %s\n\n```\n' "$1"; }
end() { printf '```\n'; }
{
  echo "# dNh_CRM packaging bundle (generated, read-only digest)"
  sec "header"
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "repo: $R"
  echo "HEAD: $(git -C "$R" rev-parse HEAD)"
  echo "last commit: $(git -C "$R" log -1 --format='%h %ci %s')"
  echo "branch: $(git -C "$R" rev-parse --abbrev-ref HEAD)"
  end
  sec "top-level listing (ls -la, names only)"
  ls -la "$R" | awk 'NR>1{ $1=$2=$3=$4=$5=$6=$7=$8=""; sub(/^ +/,""); print }'
  end
  for f in pyproject.toml .python-version .github/workflows/ci.yml .github/workflows/release.yml; do
    sec "$f"; cat "$R/$f"; end
  done
  sec "uv.lock (first 30 lines)"
  head -n 30 "$R/uv.lock"
  end
  sec "uv.lock package count"
  echo "[[package]] entries: $(grep -c '^\[\[package\]\]' "$R/uv.lock" || true)"
  end
  sec "uv.lock matches for chatx|chat-extraction|chat_extraction"
  m="$(grep -n -i -E 'chatx|chat-extraction|chat_extraction' "$R/uv.lock" | head || true)"
  if [[ -n "$m" ]]; then echo "$m"; else echo "(none)"; fi
  end
  sec "pyproject.toml [tool.uv] / [tool.uv.sources] lines"
  m="$(grep -n -E '^\[tool\.uv|^\s*(sources|index|extra-index-url|find-links)\b' "$R/pyproject.toml" || true)"
  if [[ -n "$m" ]]; then echo "$m"; else echo "(none)"; fi
  end
  sec "tool versions (owner machine, default python3)"
  echo "uv: $(uv --version 2>&1 || echo 'uv not found')"
  echo "python3 / sqlite3 (owner machine, default python3): $(python3 -c 'import sqlite3,sys;print(sys.version.split()[0], sqlite3.sqlite_version)')"
  end
} > "$TMP"
mv "$TMP" "$OUT"
trap - EXIT
echo "wrote: $OUT"
shasum -a 256 "$OUT"
