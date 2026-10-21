Role: **evidence verifier** (runner name: `sonnet-verify`, third pass — the auditor `chatgpt-web`)

The auditor `chatgpt-web` has produced a findings table about the design at
`/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md`.
Your job is narrow and mechanical: for every finding, open what it cites and say whether the citation supports the claim. You do not re-grade severity, do not add findings, do not judge whether the design is good, and do not edit anything outside the output file named below.

## Inputs

- `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/out/report-chatgpt-web.md` — section "## 2. Findings table", rows `F01`–`F38` (38 rows; IDs have no hyphen). Columns: ID | Severity | Area | Finding | Evidence | Verdict | Recommended change | Cost of ignoring. `Area` holds scope-area numbers from the audit brief, not names.
- The report's per-area deep dives follow the table; read the matching paragraph when a table row is too terse to check.
- Repositories (read-only): ChatX at `/Users/hue/code/Dopemux-ChatRipperXXX` (HEAD `9c3dd6b`), dNh_CRM at `/Users/hue/code/dNh_CRM` (HEAD `39c75bde`).
- Citation forms used by chatgpt-web: `chatx:<path>:<lines>` (ChatX repo), `dnh:<path>:<lines>` (dNh_CRM repo), bare `§x.y` (a section of the design file above), and `Report §x.y` (a section of chatgpt-web's own report — not evidence; skip it). chatgpt-web had no repo access: it read source bundles that contain whole files verbatim, so its line numbers are repo line numbers (its line 1 is the file's line 1). It says some bundle headings undercount a file by one line; that does not shift numbering. Its web citations are external facts (UNKNOWN unless the claim also rests on a repo line you can check).
- The bundles were generated at 2026-10-20T18:09:56Z from ChatX HEAD `9c3dd6b` and dNh_CRM HEAD `39c75bde`. Record each repo's current `git rev-parse --short HEAD` in your identity line. If a cited file changed since then (`git log --since=2026-10-20T18:09:56Z -- <path>`), say so in the row's note.
- Some Verdict cells are mixed, e.g. `CONFIRMED (code); PLAUSIBLE (iOS semantics)`. Check the CONFIRMED part against its citations. The PLAUSIBLE part is a claim about runtime or external behaviour: it does not lower the result by itself.

## Rules

- Read-only on both repos. Never open `.env*`, `secrets/`, `data/`, `auth.json`, or anything under `~/`.
- Use `sed -n 'A,Bp' <file>` or the Read tool with offset/limit for line ranges; use `rg -n` to locate design sections and symbols. Do not run the product or its tests.
- Do not fetch URLs. A claim that rests only on external documentation, a real database, or runtime behaviour is UNKNOWN.
- A citation PASSES when the cited lines show what the finding says they show. It FAILS when the lines do not exist, say something different, or the claim rests on a behaviour the lines do not exhibit. PARTIAL when some citations pass and others fail, or the lines support a weaker version of the claim. UNKNOWN as above.
- Line numbers that are off by a few lines but clearly point at the quoted code count as PASS; say "offset" in the note.
- Quote the decisive line (≤ 120 chars) in the note. Keep notes ≤ 30 words.
- Do not read `out/report-codex.md`, `out/report-grok.md`, `out/report-agy.md`, `out/report-opus.md`, any `research-targets-*.md`, `cross-audit-matrix.md` or `design-revision-plan.md`. You may read only the "Citations checked" column of `out/claim-verification.md` and of `out/claim-verification-opus.md`, and only for section 5 below.
- Stop and write what you have if you exceed 200 tool calls; mark remaining rows NOT_RUN.

## Output

One file: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/out/claim-verification-chatgpt.md`

Structure:

1. Identity line: runner name, model as you know it (say "no runtime receipt" if you have none), timestamp, tool-call count.
2. Summary table: auditor | rows | PASS | PARTIAL | FAIL | UNKNOWN | NOT_RUN (one row, `chatgpt-web`).
3. One table, one row per finding, in the report's order:
   `| ID | Sev (as claimed) | Verdict (as claimed) | Citations checked | Result | Note |`
   `Result` is exactly one of PASS, PARTIAL, FAIL, UNKNOWN, NOT_RUN.
4. "Failures and partials": a bullet list restating every FAIL/PARTIAL with the exact mismatch.
5. "Overlaps with earlier verification passes": chatgpt-web citations (same file, overlapping line ranges) that also appear in the "Citations checked" column of `out/claim-verification.md` or `out/claim-verification-opus.md`, with the chatgpt-web ID and the other row's ID. This is mechanical: list them, do not interpret.

Write the file once at the end with the Write tool, then print its absolute path and byte size.
