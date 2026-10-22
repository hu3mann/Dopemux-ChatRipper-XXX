#!/usr/bin/env bash
# Read-only relaunch (attempt 3) of the cmd lanes: argon, deepseek, kimi.
# Why: `cmd -p` blocks write_file/edit_file/shell_command in print mode unless --yolo, and --yolo is not
# authorised for this audit (classifier-denied even under a Seatbelt profile). Attempt 1 died on that.
# So the auditors run with read tools only, cite harness-computed facts (out/HARNESS-FACTS.md), and print
# both deliverables inline; extract_deliverables.py splits the NDJSON final text into the files.
# Attempt 2 (cwd out/) died on the first read: `cmd -p` v1.87.1 only permits reads inside the cwd-rooted
# project and --add-dir does not widen that headlessly (proof: out/_attempt2-cmd-failed/smokes/). Attempt 3
# therefore runs from $D itself in plan mode; everything the auditor may read lives under $D.
# This is a separate script on purpose: run_audits.sh executed the astra/grok lanes and bash reads scripts
# incrementally, so it was not edited while those ran.
# Usage: run_audits_ro.sh [--dry-run] <argon|deepseek|kimi>...
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHATX=/Users/hue/code/Dopemux-ChatRipperXXX
DNH=/Users/hue/code/dNh_CRM
DRY=0; AUDITORS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    argon|deepseek|kimi) AUDITORS+=("$a") ;;
    *) echo "unknown argument: $a" >&2; exit 64 ;;
  esac
done
[[ ${#AUDITORS[@]} -gt 0 ]] || { echo "usage: $0 [--dry-run] <argon|deepseek|kimi>..." >&2; exit 64; }

model_of() {
  case "$1" in
    argon) echo google/gemini-4-argon ;;
    deepseek) echo deepseek/deepseek-v4-pro ;;
    kimi) echo moonshotai/kimi-k3 ;;
  esac
}
cmd_line() { # human-readable form for the receipt
  echo "( cd \"$D\" && cmd -p \"\$(cat \"$D/PROMPT-$1.readonly.md\")\" --model $(model_of "$1") --permission-mode plan -t --max-turns 300 --output-format json )"
}
run_one() {
  ( cd "$D" && cmd -p "$(cat "$D/PROMPT-$1.readonly.md")" --model "$(model_of "$1")" --permission-mode plan -t --max-turns 300 --output-format json )
}
snap() { # $1 = outfile
  {
    echo "## chatx"; git -C "$CHATX" status --porcelain -- src tests pyproject.toml config schemas docs
    echo "## dnh";   git -C "$DNH" status --porcelain -- src tests pyproject.toml uv.lock
  } > "$1" 2>&1 || true
}

for a in "${AUDITORS[@]}"; do
  P="$D/PROMPT-$a.readonly.md"
  O="$D/out"
  echo "=== $a (read-only, attempt 3) ==="
  if [[ $DRY -eq 1 ]]; then
    echo "prompt:  $P"
    echo "command: $(cmd_line "$a")"
    echo "targets: $O/$a.stdout.md (NDJSON)  $O/$a.final.md  $O/$a.usage.txt  $O/report-$a.md  $O/preapproval-$a.md  $O/_run-$a.txt"
    continue
  fi
  [[ -f "$P" ]] || { echo "missing prompt: $P" >&2; exit 1; }
  [[ -f "$O/HARNESS-FACTS.md" ]] || { echo "missing $O/HARNESS-FACTS.md" >&2; exit 1; }
  snap "$O/_gitstatus-pre-$a.txt"
  START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  set +e
  run_one "$a" > "$O/$a.stdout.md" 2> "$O/$a.stderr.log"
  RC=$?
  python3 "$D/extract_deliverables.py" "$a" "$O" > "$O/_extract-$a.txt" 2>&1
  XRC=$?
  set -e
  END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  {
    echo "auditor: $a"
    echo "attempt: 3 (read-only print mode, cwd=\$D, plan mode; attempt-1/2 artefacts in out/_attempt1-cmd-failed/ and out/_attempt2-cmd-failed/)"
    echo "requested model: $(model_of "$a")"
    echo "requested effort: runner default"
    echo "command: $(cmd_line "$a")"
    echo "start: $START"
    echo "end: $END"
    echo "exit code: $RC"
    echo "stdout bytes (NDJSON): $(wc -c < "$O/$a.stdout.md" | tr -d ' ')"
    echo "extract exit code: $XRC (0 = both deliverables written, 4 = missing block(s), 3 = no final text)"
    echo "observed usage: $(cat "$O/$a.usage.txt" 2>/dev/null || echo UNKNOWN)"
  } > "$O/_run-$a.txt"
  snap "$O/_gitstatus-post-$a.txt"
  if ! diff -q "$O/_gitstatus-pre-$a.txt" "$O/_gitstatus-post-$a.txt" >/dev/null; then
    echo "DIFF: repo status changed during $a (see _gitstatus-pre/post-$a.txt)"
  fi
  echo "$a done: exit $RC, extract $XRC"
  cat "$O/_extract-$a.txt"
done
