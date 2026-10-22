#!/usr/bin/env bash
# Usage: run_audits.sh [--dry-run] [--argon-via-opencode] <auditor>...   (auditor: astra argon grok deepseek kimi | all)
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHATX=/Users/hue/code/Dopemux-ChatRipperXXX
DNH=/Users/hue/code/dNh_CRM
DRY=0; OPENCODE=0; AUDITORS=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --argon-via-opencode) OPENCODE=1 ;;
    all) AUDITORS+=(astra argon grok deepseek kimi) ;;
    astra|argon|grok|deepseek|kimi) AUDITORS+=("$a") ;;
    *) echo "unknown argument: $a" >&2; exit 64 ;;
  esac
done
[[ ${#AUDITORS[@]} -gt 0 ]] || { echo "usage: $0 [--dry-run] [--argon-via-opencode] <astra|argon|grok|deepseek|kimi|all>..." >&2; exit 64; }

cmd_line() { # prints human-readable command line for auditor
  local a="$1"
  case "$a" in
    astra) echo "codex exec -m gpt-6-astra -c 'model_reasoning_effort=\"xhigh\"' -s workspace-write -C \"$D/out\" -o \"$D/out/astra.last-message.md\" - < \"$D/PROMPT-astra.md\"" ;;
    grok) echo "grok --prompt-file \"$D/PROMPT-grok.md\" -m grok-4.7 --sandbox chatx-p0-audit --max-turns 400 --output-format plain --cwd \"$D/out\"" ;;
    argon)
      if [[ $OPENCODE -eq 1 ]]; then
        echo "opencode run -m perplexity-agent/google/gemini-4-argon --dir \"$D/out\" --format default \"\$(cat \"$D/PROMPT-argon.md\")\""
      else
        echo "( cd \"$D/out\" && cmd -p \"\$(cat \"$D/PROMPT-argon.md\")\" --model google/gemini-4-argon --permission-mode plan -t --no-session --max-turns 300 --output-format text --add-dir $CHATX --add-dir $DNH )"
      fi ;;
    deepseek) echo "( cd \"$D/out\" && cmd -p \"\$(cat \"$D/PROMPT-deepseek.md\")\" --model deepseek/deepseek-v4-pro --permission-mode plan -t --no-session --max-turns 300 --output-format text --add-dir $CHATX --add-dir $DNH )" ;;
    kimi) echo "( cd \"$D/out\" && cmd -p \"\$(cat \"$D/PROMPT-kimi.md\")\" --model moonshotai/kimi-k3 --permission-mode plan -t --no-session --max-turns 300 --output-format text --add-dir $CHATX --add-dir $DNH )" ;;
  esac
}
model_of() {
  case "$1" in
    astra) echo gpt-6-astra ;; grok) echo grok-4.7 ;;
    argon) [[ $OPENCODE -eq 1 ]] && echo perplexity-agent/google/gemini-4-argon || echo google/gemini-4-argon ;;
    deepseek) echo deepseek/deepseek-v4-pro ;; kimi) echo moonshotai/kimi-k3 ;;
  esac
}
effort_of() { [[ "$1" == astra ]] && echo 'xhigh (model_reasoning_effort)' || echo 'runner default'; }

run_one() { # executes the real command; stdout/stderr redirected by caller
  local a="$1" P="$D/PROMPT-$1.md"
  case "$a" in
    astra) codex exec -m gpt-6-astra -c 'model_reasoning_effort="xhigh"' -s workspace-write -C "$D/out" -o "$D/out/astra.last-message.md" - < "$P" ;;
    grok) grok --prompt-file "$P" -m grok-4.7 --sandbox chatx-p0-audit --max-turns 400 --output-format plain --cwd "$D/out" ;;
    argon)
      if [[ $OPENCODE -eq 1 ]]; then
        opencode run -m perplexity-agent/google/gemini-4-argon --dir "$D/out" --format default "$(cat "$P")"
      else
        ( cd "$D/out" && cmd -p "$(cat "$P")" --model google/gemini-4-argon --permission-mode plan -t --no-session --max-turns 300 --output-format text --add-dir "$CHATX" --add-dir "$DNH" )
      fi ;;
    deepseek) ( cd "$D/out" && cmd -p "$(cat "$P")" --model deepseek/deepseek-v4-pro --permission-mode plan -t --no-session --max-turns 300 --output-format text --add-dir "$CHATX" --add-dir "$DNH" ) ;;
    kimi) ( cd "$D/out" && cmd -p "$(cat "$P")" --model moonshotai/kimi-k3 --permission-mode plan -t --no-session --max-turns 300 --output-format text --add-dir "$CHATX" --add-dir "$DNH" ) ;;
  esac
}
snap() { # $1 = outfile
  {
    echo "## chatx"; git -C "$CHATX" status --porcelain -- src tests pyproject.toml config schemas docs
    echo "## dnh";   git -C "$DNH" status --porcelain -- src tests pyproject.toml uv.lock
  } > "$1" 2>&1 || true
}

for a in "${AUDITORS[@]}"; do
  P="$D/PROMPT-$a.md"
  O="$D/out"
  echo "=== $a ==="
  if [[ $DRY -eq 1 ]]; then
    echo "prompt:  $P"
    echo "command: $(cmd_line "$a")"
    echo "targets: $O/$a.stdout.md  $O/$a.stderr.log  $O/_run-$a.txt  $O/_gitstatus-pre-$a.txt  $O/_gitstatus-post-$a.txt"
    [[ $a == astra ]] && echo "         $O/astra.last-message.md"
    continue
  fi
  [[ -f "$P" ]] || { echo "missing prompt: $P" >&2; exit 1; }
  mkdir -p "$O"
  snap "$O/_gitstatus-pre-$a.txt"
  START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  set +e
  run_one "$a" > "$O/$a.stdout.md" 2> "$O/$a.stderr.log"
  RC=$?
  set -e
  END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  BYTES="$(wc -c < "$O/$a.stdout.md" | tr -d ' ')"
  {
    echo "auditor: $a"
    echo "requested model: $(model_of "$a")"
    echo "requested effort: $(effort_of "$a")"
    echo "command: $(cmd_line "$a")"
    echo "start: $START"
    echo "end: $END"
    echo "exit code: $RC"
    echo "stdout bytes: $BYTES"
  } > "$O/_run-$a.txt"
  snap "$O/_gitstatus-post-$a.txt"
  if ! diff -q "$O/_gitstatus-pre-$a.txt" "$O/_gitstatus-post-$a.txt" >/dev/null; then
    echo "DIFF: repo status changed during $a (see _gitstatus-pre/post-$a.txt)"
  fi
  echo "$a done: exit $RC, $BYTES bytes"
done
