#!/usr/bin/env bash
# Package audit inputs for the owner-run web auditor (astra-pro).
set -euo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$D"
ZIP="$D/chatx-p0-packet-audit-pack-2026-10-22.zip"
for req in PROMPT-master.md PROMPT-astra-pro-web.md inputs/SHA256SUMS inputs/2026-10-21-p0-workspace-packet.md inputs/2026-10-20-chatx-rearchitecture-design.md inputs/2026-10-21-next-steps.md; do
  [[ -e "$req" ]] || { echo "missing required input: $req" >&2; exit 1; }
done
[[ -e bundles/dnh-packaging-bundle.md ]] || { echo "missing: bundles/dnh-packaging-bundle.md -- run make_bundle.sh first" >&2; exit 1; }
{
  echo "Packed files for chatx-p0-packet-audit-pack-2026-10-22.zip (sha256, generated $(date -u +%Y-%m-%dT%H:%M:%SZ))"
  for f in PROMPT-master.md PROMPT-astra-pro-web.md inputs/* bundles/dnh-packaging-bundle.md; do
    [[ -f "$f" ]] && shasum -a 256 "$f"
  done
} > README-INPUTS.txt
rm -f "$ZIP"
zip -q -r "$ZIP" PROMPT-master.md PROMPT-astra-pro-web.md inputs bundles/dnh-packaging-bundle.md README-INPUTS.txt -x '*.DS_Store'
cp "$ZIP" "$HOME/Downloads/"
unzip -l "$ZIP"
shasum -a 256 "$ZIP"
echo "copied to: $HOME/Downloads/$(basename "$ZIP")"
