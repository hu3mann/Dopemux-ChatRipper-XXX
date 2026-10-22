Auditor name: **deepseek**
Finding-ID prefix: **DSK**

Read and follow, in full, the brief at `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/PROMPT-master.md`. It defines your role, the fifteen scope areas, the two deliverables and their required structure. Everything below only tells you what you can reach and where to write.

## Access

- ChatX repository (read-only): `/Users/hue/code/Dopemux-ChatRipperXXX`, branch `governance-doctrine-integration`, commit `cc18536`. Audit inputs are the snapshot copies under `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/inputs/` (identical to `docs/superpowers/plans/2026-10-21-p0-workspace-packet.md`, `docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md`, `docs/superpowers/plans/2026-10-21-next-steps.md` at that commit). Context only: `docs/superpowers/audits/2026-10-20-design-audit/out/cross-audit-matrix.md`, `design-revision-plan.md`, `builder-check-rev2.md`. Ignore `node_modules/`, `awesome-claude-code/`, `claude-platform-evolution/`, `.taskmaster/`, `.serena/`, `context_portal/`, `.claude/`.
- dNh_CRM repository (read-only): `/Users/hue/code/dNh_CRM` — `pyproject.toml`, `uv.lock`, `.python-version`, `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `src/dnh_crm/` (how it would consume the core). A generated digest is at `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/bundles/dnh-packaging-bundle.md`.
- `~/code/chatstack` does not exist yet; P0 creates it. If you find it exists, say so in the identity block and do not treat it as input.
- Allowed: reading any file in both repositories; `rg`/`grep`; `git log`/`show`/`blame`; `wc`; `uv --version`; `python3 -c "import sqlite3; print(sqlite3.sqlite_version)"`; your runner's web search for scope area 15 (cite URLs).
- Not allowed: creating or editing files outside `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/out`; installing packages; running test suites; `uv sync`/`uv lock`/`uv build` in either repository; anything that writes to either repository; network calls other than your runner's web search.
- Never open `.env*`, `secrets/`, `auth.json`, or anything under `~/.codex`, `~/.grok`, `~/.kimi-code`, `~/.config/opencode`, `~/.cmd`.

## Output

- Directory: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/out/`
- Files: `report-deepseek.md` (Output A) and `preapproval-deepseek.md` (Output B).
- Whether or not you can write there, your final message MUST end with both files printed in full, each preceded by a line `=== FILE: <filename> ===`, and closed by a line `=== END ===`. Print nothing after `=== END ===`.
- Begin the report with the reviewer identity block (model/runner as you know it, knowledge cutoff, files actually opened).
