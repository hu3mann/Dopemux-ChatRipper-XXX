Role: **evidence verifier** (runner name: `sonnet-verify`)

Three independent auditors (codex, grok, agy) have each produced a findings table about the design at
`/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md`.
Your job is narrow and mechanical: for every finding, open what it cites and say whether the citation supports the claim. You do not re-grade severity, do not add findings, do not judge whether the design is good, and do not edit anything outside the output directory.

## Inputs

- `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/out/report-codex.md` — section "2." findings table, rows `F01`–`F30`. Columns: ID | Severity | Area | Finding | Evidence | Verdict | Recommended change | Cost of ignoring.
- `.../out/report-grok.md` — section "## 2. Findings", rows `F1`–`F20`. Columns: ID | Sev. | Area | Finding | Evidence.
- `.../out/report-agy.md` — section "## 2. Findings Table", rows `F-01`–`F-25`. Columns: ID | Area | Severity | Verdict | Evidence | Finding | ….
- Each report also has per-area deep dives after the table; read the matching deep-dive paragraph when a table row is too terse to check.
- Repositories (read-only): ChatX at `/Users/hue/code/Dopemux-ChatRipperXXX` (HEAD `9c3dd6b`), dNh_CRM at `/Users/hue/code/dNh_CRM` (HEAD `39c75bde`). Citations use `ChatX:path:lines`, `dNh:path:lines`, bare `path:lines` (ChatX unless the path starts with `src/dnh_crm`), or `§n.n` (design sections).

## Rules

- Read-only on both repos. Never open `.env*`, `secrets/`, `data/`, `auth.json`, or anything under `~/`.
- Use `sed -n 'A,Bp' <file>` or the Read tool with offset/limit for line ranges; use `rg -n` to locate design sections. Do not run the product.
- A citation PASSES when the cited lines show what the finding says they show. It FAILS when the lines do not exist, say something different, or the claim rests on a behaviour the lines do not exhibit. PARTIAL when some citations pass and others fail, or the lines support a weaker version of the claim. UNKNOWN when the claim is about runtime behaviour, external documentation, or a real database that cannot be checked by reading.
- Quote the decisive line (≤ 120 chars) in the note. Keep notes ≤ 30 words.
- Do not read the other `out/report-*.md` files' conclusions into your judgement; you check citations, not opinions.
- Stop and write what you have if you exceed 300 tool calls; mark remaining rows NOT_RUN.

## Output

One file: `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-20-design-audit/out/claim-verification.md`

Structure:

1. Identity line: runner name, model as you know it (say "no runtime receipt" if you have none), timestamp, tool-call count.
2. Summary table: auditor | rows | PASS | PARTIAL | FAIL | UNKNOWN | NOT_RUN.
3. One table per auditor, one row per finding, in the auditor's order:
   `| ID | Sev (as claimed) | Verdict (as claimed) | Citations checked | Result | Note |`
4. "Failures and partials" — a bullet list restating every FAIL/PARTIAL with the exact mismatch.
5. "Cross-auditor citation overlaps" — citations (same file, overlapping line ranges) used by two or more auditors, with the finding IDs. This is mechanical: list them, do not interpret.

Write the file once at the end with the Write tool, then print its absolute path and byte size.
