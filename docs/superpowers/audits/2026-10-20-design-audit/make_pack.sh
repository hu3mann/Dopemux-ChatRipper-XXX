#!/usr/bin/env bash
# Package the audit inputs for auditors that cannot read the repos (e.g. chatgpt.com web upload).
# Produces chatx-design-audit-pack-2026-10-20.zip next to this script, with relative paths preserved.
set -euo pipefail
A="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIP="$A/chatx-design-audit-pack-2026-10-20.zip"
rm -f "$ZIP"
cd "$A"
for req in PROMPT-master.md PROMPT-chatgpt-web.md design evidence bundles/source-bundle-chatx.md bundles/source-bundle-dnh.md; do
  [[ -e "$req" ]] || { echo "missing: $req" >&2; exit 1; }
done
zip -q -r "$ZIP" PROMPT-master.md PROMPT-chatgpt-web.md design evidence bundles/source-bundle-chatx.md bundles/source-bundle-dnh.md -x '*.DS_Store'
unzip -l "$ZIP" | tail -n +2
shasum -a 256 "$ZIP"
