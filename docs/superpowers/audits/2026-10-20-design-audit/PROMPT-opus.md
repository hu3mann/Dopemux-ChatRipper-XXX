Auditor name: **opus**

Read and follow, in full, the brief at
`/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/PROMPT-master.md`.
It defines your role, the fifteen scope areas, the two deliverables and their required structure. Everything below only tells you where things are and where to write.

You are one of five independent auditors. Do not read `out/report-*.md`, `out/research-targets-*.md`, or `out/claim-verification.md` from the other auditors; your value is independence. Do not read `out/_findings-extract.tmp.md`.

## Access

- ChatX repository (read-only): `/Users/hue/code/Dopemux-ChatRipperXXX` — branch `governance-doctrine-integration`, HEAD `9c3dd6b`. Product code is `src/chatx/`, `tests/`, `config/`, `pyproject.toml`. Ignore `node_modules/`, `awesome-claude-code/`, `claude-platform-evolution/`, `.claude/`, `.taskmaster/`, `.serena/`.
- dNh_CRM repository (read-only): `/Users/hue/code/dNh_CRM` — branch `migrate-cheaperinference`, HEAD `39c75bde`. Product code `src/dnh_crm/`, `tests/`, `scripts/`.
- Design under audit: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md`.
- Evidence notes (prior read-only audits; treat as leads, not as proof): `.../2026-10-20-design-audit/evidence/01-code-reality-audit.md`, `02-dnh-ingest-trace.md`, `03-docs-parity-inventory.md`.
- Allowed: reading any file in both repositories; `rg`/`grep`, `git log`/`blame`/`show`, `wc`, `sqlite3` against fixture databases only; running existing unit tests read-only if useful (`uv run --directory <repo> pytest <path> -q`), but no test is required.
- Not allowed: creating or editing files outside the output directory; installing packages; running the product against the owner's live `~/Library/Messages/chat.db` or any real export; network calls other than documentation lookups for scope area 15 (if web fetch is unavailable, mark those claims UNKNOWN rather than guessing).
- Never open `.env*`, `secrets/`, `auth.json`, `data/`, or anything under `~/.codex`, `~/.grok`, `~/.agy`, `~/.gemini`, `~/.claude`.

## Output

- Directory: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/out/`
- Files: `report-opus.md` (Output A) and `research-targets-opus.md` (Output B). Write them with the Write tool. Do not write anything else.
- Begin the report with the reviewer identity block (model/runner as you know it, knowledge cutoff, repos/HEADs, files actually opened). State plainly that you have no runtime receipt of your model id or effort if that is the case.
- Severity scale: BLOCKER / HIGH / MEDIUM / LOW. Verdict per finding: CONFIRMED only when you personally read the cited line range; otherwise PLAUSIBLE or UNKNOWN. Every CONFIRMED finding cites `repo:path:line-range` and/or `§n.n` of the design.
- Research targets: at least 40 rows, columns exactly as the brief specifies, each tied to a finding ID.
- Finish by printing the absolute paths of the two files and their byte sizes.
