#!/usr/bin/env bash
# Build source bundles for auditors that cannot read the repos directly (e.g. web chat UIs).
# Usage: make_bundle.sh <out_dir>
# Deterministic; skips secret-like paths; reports MISSING files on stderr instead of failing.
set -euo pipefail

OUT="${1:?usage: make_bundle.sh <out_dir>}"
CHATX=/Users/hue/code/Dopemux-ChatRipperXXX
DNH=/Users/hue/code/dNh_CRM
mkdir -p "$OUT"

bundle() {
  local name="$1" root="$2"; shift 2
  local f="$OUT/source-bundle-$name.md"
  : > "$f"
  {
    echo "# Source bundle: $name"
    echo
    echo "Root: \`$root\` · generated $(date -u +%FT%TZ) · commit $(git -C "$root" rev-parse --short HEAD 2>/dev/null || echo UNKNOWN) · branch $(git -C "$root" rev-parse --abbrev-ref HEAD 2>/dev/null || echo UNKNOWN)"
    echo
    echo "## Tracked file inventory (git ls-files, tooling dirs removed)"
    echo
    echo '```'
    git -C "$root" ls-files | grep -vE '^(node_modules|awesome-claude-code|claude-platform-evolution|\.taskmaster|\.serena|context_portal|\.claude|htmlcov|site)/' || true
    echo '```'
  } >> "$f"

  for rel in "$@"; do
    case "$rel" in
      *.env*|*secret*|*credential*|*token*) echo "SKIP(secret-like) $rel" >&2; continue ;;
    esac
    local p="$root/$rel"
    if [[ -f "$p" ]]; then
      local lang="${rel##*.}"
      local lines; lines=$(wc -l < "$p" | tr -d ' ')
      {
        printf '\n\n## FILE: %s (%s lines)\n\n```%s\n' "$rel" "$lines" "$lang"
        cat "$p"
        printf '\n```\n'
      } >> "$f"
    else
      echo "MISSING $rel" >&2
      printf '\n\n## FILE: %s — MISSING at bundle time\n' "$rel" >> "$f"
    fi
  done
  wc -c "$f" >&2
}

bundle chatx "$CHATX" \
  pyproject.toml \
  AGENTS.md \
  src/chatx/__init__.py \
  src/chatx/cli/main.py \
  src/chatx/cli_errors.py \
  src/chatx/schemas/message.py \
  src/chatx/schemas/validator.py \
  schemas/message.schema.json \
  schemas/chunk.schema.json \
  src/chatx/imessage/extract.py \
  src/chatx/imessage/db.py \
  src/chatx/imessage/backup.py \
  src/chatx/imessage/time.py \
  src/chatx/imessage/body_normalize.py \
  src/chatx/imessage/attachments.py \
  src/chatx/imessage/report.py \
  src/chatx/instagram/extract.py \
  src/chatx/pdf_ingest/reader.py \
  src/chatx/identity/normalize.py \
  src/chatx/redaction/policy_shield.py \
  src/chatx/redaction/patterns.py \
  src/chatx/transformers/chunker.py \
  src/chatx/transformers/pipeline.py \
  src/chatx/enrichment/enricher.py \
  src/chatx/enrichment/ollama_client.py \
  src/chatx/enrichment/models.py \
  src/chatx/enrichment/multi_pass_pipeline.py \
  src/chatx/indexing/vector_store.py \
  src/chatx/storage/base.py \
  src/chatx/storage/psychology_relationship_mapper.py \
  src/chatx/privacy/differential_privacy.py \
  src/chatx/utils/json_output.py \
  src/chatx/utils/run_report.py \
  config/labels.yml \
  config/arch-gates.yml

bundle dnh "$DNH" \
  pyproject.toml \
  src/dnh_crm/config.py \
  src/dnh_crm/events.py \
  src/dnh_crm/idempotency.py \
  src/dnh_crm/ingest/imessage.py \
  src/dnh_crm/ingest/imessage_mapper.py \
  src/dnh_crm/ingest/imessage_source.py \
  src/dnh_crm/ingest/imessage_attributed_body.py \
  src/dnh_crm/ingest/normalizer.py \
  src/dnh_crm/ingest/dedupe.py \
  src/dnh_crm/ingest/whatsapp_export.py \
  src/dnh_crm/ingest/email_eml.py \
  src/dnh_crm/services/ingest_runner.py \
  src/dnh_crm/store/migrations.py \
  tests/unit/test_imessage_attributed_body.py

echo "bundles written to $OUT" >&2
