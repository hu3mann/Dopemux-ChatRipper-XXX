Auditor name: **grok**

Read and follow, in full, the brief at
`/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/PROMPT-master.md`.
It defines your role, the fifteen scope areas, the two deliverables and their required structure. Everything below only tells you what you can reach and where to write.

## Access

- ChatX repository (read-only): `/Users/hue/code/Dopemux-ChatRipperXXX` — branch `governance-doctrine-integration`; audit the working tree as it is on disk. Product code: `src/chatx/`, `schemas/`, `config/`, `tests/`. Ignore `node_modules/`, `awesome-claude-code/`, `claude-platform-evolution/`, `.taskmaster/`, `.serena/`, `context_portal/`, `.claude/`.
- dNh_CRM repository (read-only): `/Users/hue/code/dNh_CRM` — product code `src/dnh_crm/`, `tests/`.
- Design under audit: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md`
- Evidence: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/evidence/01-code-reality-audit.md`, `02-dnh-ingest-trace.md`, `03-docs-parity-inventory.md`
- Allowed: reading any file in both repositories; `rg`/`grep`, `git log`/`blame`/`show`, `wc`, `sqlite3 ".schema"` on fixture databases under `tests/fixtures/`; your runner's web search for scope item 15 (cite URLs).
- Not allowed: creating or editing files outside the output directory; installing packages; running test suites or anything that writes to either repository; network calls other than your runner's web search.
- Never open `.env*`, `secrets/`, `auth.json`, or anything under `~/.codex`, `~/.grok`, `~/.agy`.

## Output

- Directory: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/out/`
- Files: `report-grok.md` (Output A) and `research-targets-grok.md` (Output B).
- If you cannot write there, print both files in full, each preceded by `=== FILE: <name> ===`, as the very last thing you output.
- Begin the report with the reviewer identity block (model/runner as you know it, knowledge cutoff, files actually opened). End your final message with the two file paths and their word counts.
