# RT desk-research round — 2026-10-21

Purpose: settle the open research targets from design rev 2 (§13) that can be answered
from current sources, so the P1–P6 packets are written against facts rather than
assumptions. Measurement targets (RT-4 scan cost, RT-13 calibration, RT-15 inter-rater)
are not here; they belong to P0.5, P4 and P6.

Step S1 of `docs/superpowers/plans/2026-10-21-next-steps.md`.

## Scope

14 items: RT-2, RT-3, RT-5, RT-6, RT-9, RT-11, RT-14, RT-16, RT-17, RT-18, RT-19 and the
open halves of RT-7, RT-10, RT-12. Status source:
`docs/superpowers/audits/2026-10-20-design-audit/out/research-targets-supervisor.md`.

Section each target would change (from the spec text, first mention at or after §3):

| RT | Spec section | Needed by |
|---|---|---|
| RT-2, RT-3 | §3.4 Canonical message contract v2 | P1 |
| RT-14, RT-19 | §3.5 Storage (and §3.15 for RT-19) | P2 |
| RT-10, RT-11 | §3.7 Policy Shield v2 (RT-10 also §3.3 pin) | P3 |
| RT-16 | §4 Target architecture, P3 exit | P3 |
| RT-7, RT-12, RT-17 | §3.6 Model access | P4 |
| RT-5, RT-6, RT-18 | §3.10 Search, query, reports (RT-5/RT-6 also §11) | P5 |
| RT-9 | §4, P6 row | P6 |

## How to run

1. Open a ChatGPT web session with browsing on (the audit run self-reported as
   "GPT-6 Astra Pro"; the owner recorded it as GPT-6 Pro — record whatever this
   session reports in its identity block).
2. Attach `docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md` (rev 2).
3. Paste `PROMPT-chatgpt-web.md` from the `---` line down.
4. Save the two outputs here as `out/research-rt-chatgpt-web.md` and
   `out/research-rt-sources.md`. If the session printed them inline, paste them into
   files with those names.

## Verification before anything lands in the spec

Route: `sonnet-verify` (Claude Code `Agent`, `model: sonnet`), same as the audit, but
this round is about external facts, so the verifier may fetch URLs. Per Output A
evidence row: open the Source ID's URL from Output B; PASS when the ≤120-char quote is
found on the page and the page date matches; FAIL when the quote is absent or the page
says otherwise; UNKNOWN when the page is unreachable or paywalled. Rows marked
`from memory, unverified` are UNKNOWN by definition. Output:
`out/claim-verification-research.md` with one row per evidence row and a count of
PASS/FAIL/UNKNOWN per RT.

Only `adopt` / `adopt with change` recommendations whose evidence rows all PASS are
candidates for a spec edit, and each spec edit is a separate, owner-approved change
with a §14 change-log entry.

## Status

- 2026-10-21: prompt written. Not yet run. Owner is reading design rev 2 (step S0).
