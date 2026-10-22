## Harness constraints for this run — read before anything else

Your runner is `cmd` in print mode. In this mode the harness **blocks** `write_file`, `edit_file` and `shell_command`: every such call returns "requires permissions" and wastes a turn. Attempt 1 of this audit failed because the auditor kept trying. Therefore:

1. Do **not** call `write_file`, `edit_file` or `shell_command` at all — not even once "to check". Use only `read_file`, `grep`, `glob`, `ls` (and your runner's web search for scope area 15, if it is available to you).
2. **Read only inside `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/`.** The runner denies any read outside that folder (that is how attempt 2 died, on its very first read), and a single denial ends the run with no deliverable. Do not open `/Users/hue/code/dNh_CRM/...`, `/Users/hue/code/Dopemux-ChatRipperXXX/...` outside this folder, or `~/...`. Wherever the brief names a repository file, use the copy provided here: ChatX packet/spec/next-steps → `inputs/` (sha256 in `inputs/SHA256SUMS`); dNh `pyproject.toml`, `uv.lock` header, `.python-version`, CI/release workflows → `bundles/dnh-packaging-bundle.md`. State in your report that you worked from these snapshots.
3. You cannot run `git`, `wc`, `shasum`, `uv` or `python3`. The harness has precomputed those facts in `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/out/HARNESS-FACTS.md`. Read it first and cite its values as **harness-supplied (not independently verified)**; never present them as your own measurements.
4. You cannot write the two deliverable files. Deliver them **inline**: your final message must consist of both files in full, each preceded by a line `=== FILE: <filename> ===` and closed by a final line `=== END ===`, exactly as the Output section below requires. The harness splits that text into the files. Print nothing after `=== END ===`.
5. Work in one pass: read the brief, `HARNESS-FACTS.md`, the inputs and the bundle; then produce the final message. Do not narrate progress between tool calls, and do not stop with a partial message — a final message without both `=== FILE:` blocks counts as no deliverable at all.

---

Auditor name: **argon**
Finding-ID prefix: **ARG**

Read and follow, in full, the brief at `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/PROMPT-master.md`. It defines your role, the fifteen scope areas, the two deliverables and their required structure. Everything below only tells you what you can reach and where to write.

## Access (read-only print mode — this section replaces the full-tool wording other lanes receive)

- You may read **only** files under `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/` (your working directory). The runner denies every read outside it, and a single denial ends the run with no deliverable.
- ChatX inputs: `inputs/2026-10-21-p0-workspace-packet.md`, `inputs/2026-10-20-chatx-rearchitecture-design.md` (rev 2.1), `inputs/2026-10-21-next-steps.md` — snapshot copies taken at ChatX commit `cc18536`; `inputs/SHA256SUMS` is authoritative. Do **not** open the live repository at `/Users/hue/code/Dopemux-ChatRipperXXX`.
- dNh_CRM inputs: `bundles/dnh-packaging-bundle.md` — generated digest of `pyproject.toml`, the `uv.lock` header, `.python-version`, `.github/workflows/ci.yml`, `.github/workflows/release.yml` and the other files listed in its header, taken at dNh commit `e8bbcadb`; per-file sha256 in `out/HARNESS-FACTS.md`. Do **not** open the live repository at `/Users/hue/code/dNh_CRM`. If a scope area needs a dNh file that is not in the bundle (for example `src/dnh_crm/`), mark that specific check NOT_RUN with the reason instead of guessing.
- `~/code/chatstack` does not exist (harness-verified in `out/HARNESS-FACTS.md`); P0 creates it. Treat it as absent.
- Facts you would normally measure (`git` HEADs, hashes, line counts, `uv`/Python/SQLite versions) come from `out/HARNESS-FACTS.md` only — you cannot run `git`, `rg`, `wc`, `uv` or `python3`. Cite them as harness-supplied.
- Allowed tools: `read_file`, `grep`, `glob`, `ls` inside the folder above; your runner's web search for scope area 15 (cite URLs).
- Not allowed: `write_file`, `edit_file`, `shell_command`; any read outside the folder above; anything under `~/.codex`, `~/.grok`, `~/.kimi-code`, `~/.config/opencode`, `~/.cmd`; `.env*`, `secrets/`, `auth.json`.

## Output

- Directory: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/out/`
- Files: `report-argon.md` (Output A) and `preapproval-argon.md` (Output B).
- Whether or not you can write there, your final message MUST end with both files printed in full, each preceded by a line `=== FILE: <filename> ===`, and closed by a line `=== END ===`. Print nothing after `=== END ===`.
- Begin the report with the reviewer identity block (model/runner as you know it, knowledge cutoff, files actually opened).
