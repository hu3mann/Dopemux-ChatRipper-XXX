## Harness constraints for this run — read before anything else

Your runner is `cmd` in print mode. In this mode the harness **blocks** `write_file`, `edit_file` and `shell_command`: every such call returns "requires permissions" and wastes a turn. Attempt 1 of this audit failed because the auditor kept trying. Therefore:

1. Do **not** call `write_file`, `edit_file` or `shell_command` at all — not even once "to check". Use only `read_file`, `grep`, `glob`, `ls` (and your runner's web search for scope area 15, if it is available to you).
2. **Read only inside `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/`.** The runner denies any read outside that folder (that is how attempt 2 died, on its very first read), and a single denial ends the run with no deliverable. Do not open `/Users/hue/code/dNh_CRM/...`, `/Users/hue/code/Dopemux-ChatRipperXXX/...` outside this folder, or `~/...`. Wherever the brief names a repository file, use the copy provided here: ChatX packet/spec/next-steps → `inputs/` (sha256 in `inputs/SHA256SUMS`); dNh `pyproject.toml`, `uv.lock` header, `.python-version`, CI/release workflows → `bundles/dnh-packaging-bundle.md`. State in your report that you worked from these snapshots.
3. You cannot run `git`, `wc`, `shasum`, `uv` or `python3`. The harness has precomputed those facts in `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/out/HARNESS-FACTS.md`. Read it first and cite its values as **harness-supplied (not independently verified)**; never present them as your own measurements.
4. You cannot write the two deliverable files. Deliver them **inline**: your final message must consist of both files in full, each preceded by a line `=== FILE: <filename> ===` and closed by a final line `=== END ===`, exactly as the Output section below requires. The harness splits that text into the files. Print nothing after `=== END ===`.
5. Work in one pass: read the brief, `HARNESS-FACTS.md`, the inputs and the bundle; then produce the final message. Do not narrate progress between tool calls, and do not stop with a partial message — a final message without both `=== FILE:` blocks counts as no deliverable at all.

---

