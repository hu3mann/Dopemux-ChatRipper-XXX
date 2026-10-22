# Downstream handoff to dNh — P0 exit record entry (X6)

| | |
|---|---|
| Status | **DRAFT — not issued.** Becomes ISSUED only when the four inputs below are filled from P0 Task 7 artifacts and the "Record of issuance" block is completed. |
| Created | 2026-10-22, from owner decision 5 (audit brief `docs/superpowers/audits/2026-10-22-p0-packet-audit/PROMPT-master.md`) |
| Spec basis | `docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md` rev 2.2, §6 P0 row (line 871): "a downstream handoff to dNh (branch resolution by both uv source forms; CI installing the pinned wheel) is issued and recorded in the P0 exit record; completing and merging it are dNh decisions, not ChatX exit criteria" |
| Packet basis | `docs/superpowers/plans/2026-10-21-p0-workspace-packet.md` rev 2.2, exit criterion X6 (line 100), section "Downstream handoff to dNh" (lines 130–156), Task 7 Step 6 (line 323) |
| Issuer | ChatX (the P0 builder, at Task 7 Step 6) |
| Recipient | Whoever holds dNh authority for `/Users/hue/code/dNh_CRM` — UNKNOWN until named by the owner |
| Canonical copy once issued | `docs/p0-exit-record.md` in the `chatstack` repo (packet line 136). This file is the ChatX-side draft and the record that the handoff was issued. |

## What this handoff is and is not

- **ChatX's obligation (X6):** issue this handoff with the four inputs filled, and record that it was issued. That is the whole of the ChatX exit criterion.
- **Not ChatX exit criteria:** running H1 and H2, creating or completing the dNh branch, and merging it. Those are dNh decisions under dNh authority (packet line 132). H1 and H2 carry no PASS/FAIL state in the P0 completion and are never counted as NOT_RUN gates there.
- **Authority boundary:** `/Users/hue/code/dNh_CRM` is governed by dNh's own `AGENTS.md` and task packets (spec line 151). Neither the P0 packet nor this record authorizes any edit, branch creation, commit or push there.

## Inputs the handoff gives dNh

All four are recorded in `docs/p0-exit-record.md` when issued. Placeholders stay literally `UNKNOWN` until Task 7 produces them; do not pre-fill proposed values as if observed.

| # | Input | Value | Source |
|---|---|---|---|
| 1 | Release URL | UNKNOWN (proposed form: `https://github.com/DDD-Enterprises/chatstack/releases/tag/core-v0.0.1a0`; the recorded value is whatever `release.yml` produced) | Task 7 Step 5 |
| 2 | Wheel filename and sha256 | UNKNOWN (expected filename `chat_extraction_core-0.0.1a0-py3-none-any.whl`; take the filename from the release asset list and the sha256 from `SHA256SUMS`) | Task 7 Step 5, `SHA256SUMS` |
| 3 | Both uv source forms | `{ path = "../chatstack/packages/chat-extraction-core", editable = true }` and `{ workspace = "../chatstack" }` (spec lines 146–147) | Spec; verified against uv 0.12.11 in audit check ARG-C01 |
| 4 | chatstack commit SHA the tag points to, and the uv version used by the build | UNKNOWN | Task 7 Step 5 (`git rev-parse core-v0.0.1a0^{commit}`; `uv --version` from the CI log) |

## Open owner decision carried with this handoff

**B14 — repository visibility.** If `DDD-Enterprises/chatstack` is private, dNh CI needs a read route to the release assets (a fine-grained token scoped to that repo, or a vendored wheel). This must be chosen **before** the handoff is issued; the choice and its rationale go in the "Record of issuance" block below and in packet row B14. State: OPEN (packet line 141).

## Checks for whoever holds dNh authority

Verbatim from packet lines 145–148 (former exit criteria X3 and X4 of rev 2.1):

| ID | Check | How it would be checked |
|---|---|---|
| H1 | a dNh dev branch resolves the core by both the `path` and `workspace` forms | CROSS-REPO, needs separate authority (see this section). Check: from clean clones of dNh and chatstack, `uv lock` and `uv sync` succeed with `{ path = "../chatstack/packages/chat-extraction-core", editable = true }`, then with `{ workspace = "../chatstack" }`; `uv pip show chat-extraction-core` resolves in both |
| H2 | that branch's CI installs a pinned wheel and passes (merging it is dNh's decision, not a ChatX exit criterion) | CROSS-REPO, needs separate authority. Check: the dNh branch's CI run is green and its log shows the core installed from a wheel pinned by version and sha256 (`--require-hashes` or equivalent in the lock). Source of the wheel: the `core-v0.0.1a0` pre-release assets — version and sha256 from `SHA256SUMS` (B9, decided 2026-10-22) |

Procedure: packet lines 150–156 (clean side-by-side clones at `~/code/dNh_CRM` and `~/code/chatstack`; path form, then workspace form, then the pinned-wheel CI install). Two facts from that procedure that dNh should not have to rediscover:

- The three forms are **not interchangeable** (ARG-C01, receipt `docs/superpowers/audits/2026-10-22-p0-packet-audit/out/arg-c01-uv-workspace-syntax.txt`, uv 0.12.11, `uv lock --offline`): `{ workspace = "../ws" }` locks as `source = { editable = … }`; bare `{ path = … }` locks as `{ directory = … }`; `{ path = …, editable = true }` locks as editable. Keep `editable = true` on the path form so H1 compares like with like, and expect the workspace form to install the core editable from source, not as a wheel. H2's pinned-wheel install is a third, separate configuration.
- Stop condition S6 (packet line 372): if the uv version pinned for the build rejects `{ workspace = "../chatstack" }`, stop and return to the supervisor rather than substituting a different form.

Branch name: UNKNOWN — builder default (proposed) `dev/chatstack-core-resolve`. Naming only; creating it waits for dNh authority (packet line 135).

## Record of issuance

Fill at Task 7 Step 6. Until every row is filled, the Status row at the top stays DRAFT.

| Field | Value |
|---|---|
| Issued on | UNKNOWN |
| Issued by | UNKNOWN |
| Issued to (dNh authority holder) | UNKNOWN |
| Channel / reference | UNKNOWN (e.g. dNh task packet ID, issue URL, or commit of `docs/p0-exit-record.md` in chatstack) |
| B14 decision recorded | UNKNOWN |
| Inputs 1, 2, 4 filled from | UNKNOWN (CI run URL and `SHA256SUMS` commit) |
| X6 state in P0 exit record | NOT_RUN |

## Change log

- 2026-10-22: created as DRAFT. Spec sha256 `3f60d5123b3cb5d10b9a68cc5004bfa1084293bee17b1c026679fa80cc2cea78` (rev 2.2), packet at ChatX commit `941cf78`. The packet does not yet point at this file; adding that pointer is a rev 2.3 packet change.
