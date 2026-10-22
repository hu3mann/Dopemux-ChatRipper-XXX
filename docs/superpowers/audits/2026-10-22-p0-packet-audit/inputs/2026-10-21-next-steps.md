# ChatX — next steps after design rev 2

Status: proposal, supervisor-authored, 2026-10-21. Owner decides.
Inputs: `docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md` (rev 2, 1,261 lines),
`docs/superpowers/audits/2026-10-20-design-audit/README.md` and `out/research-targets-supervisor.md`.

## Where things stand

- Design rev 2 is applied. All 13 owner items and two confirmations are answered (§12).
  The builder check of rev 2 is resolved. The audit README's last line is
  "Next: the owner reads rev 2, then implementation planning per phase."
- §6 sets two rules: risk first (the P0.5 spikes run before anything is built on their
  answers) and each phase's exit uses only that phase's outputs. Each phase gets its own
  implementation plan. Later phases depend on earlier results: schema v2 freezes after
  P0.5(a); the NER engine comes out of the P3 eval; the embedding model and quantization
  out of P5.
- Research targets: 19. Answered 2 (RT-1, RT-8). Partly 4 (RT-4, RT-7, RT-10, RT-12).
  Open 13.
- The TaskMaster list in this repo (5 done, 1 in progress, 49 pending, 10 todo) targets
  the old architecture. Owner decision 1 is a new clean repo (`~/code/chatstack`), so that
  list is a legacy artifact, not the build queue.
- Control Tower has no ChatX worktrees registered.
- Disk: `/` at 97%, 15 GiB free. P0.5(a) snapshots the owner's `chat.db`
  (`~/Library/Messages` is 4.3 GB) and P5 measures at 1M chunks.

## The four options, answered

| Option | Answer | Why |
|---|---|---|
| More architecture work | No | The audit is closed and the owner items are answered. What is left in §10 is "resolve by measurement"; more desk design would guess at those numbers. The four owner follow-ups in §12 are phase-gated (P3 hard-fail definitions, cloud account terms before the first cloud run, P6 second rater) and belong inside those packets. |
| Research | Yes, targeted | The 13 open RTs split in two. Desk research (external facts, 10 targets plus three open halves) can run now. Measurement (RT-4 scan cost, RT-13 calibration, RT-15 inter-rater) is what P0.5, P4 and P6 are for. |
| Astra Pro prompt | Yes, now, in parallel | "GPT-6 Astra Pro" was the ChatGPT web model for the audit. One research prompt covering the desk-research RTs, ordered by when the build needs each answer. Its citations get the same verification pass the audit used. |
| Full packet series | Not all eight | Write P0 and P0.5 now. P1 after P0.5(a) and RT-2/RT-3 return. Later packets are written when the phase before them exits, per §6. |

## Research prompt scope (desk research)

Ordered by the phase that needs the answer.

| Needed by | RT | Topic |
|---|---|---|
| P1 | RT-2 | Canonical JSON: JCS (RFC 8785) vs dNh `canonical_json` — affects `msg_id` in T02 |
| P1 | RT-3 | Generic NSAttributedString typedstream decoders |
| P2 | RT-14 | macOS exposure controls: `.noindex`, Time Machine exclusion, iCloud-synced folder detection |
| P2 | RT-19 | Per-case SQLCipher or encrypted sparsebundle with sqlite-vec and FTS5 |
| P3 | RT-10 (open half) | Presidio V2 changes (`docs/presidio_V2.md`) |
| P3 | RT-11 | Small NER engines for short, slangy chat text (incl. OpenAI Privacy Filter) |
| P3 | RT-16 | Local language identification for short messages |
| P4 | RT-7 (open half) | Anthropic prompt caching and Batch API for this workload |
| P4 | RT-12 (open half) | llama.cpp and LM Studio reproducibility, MLX structured output |
| P4 | RT-17 | Binding a gate token to final request bytes: transport hooks in Anthropic and OpenAI-compatible clients |
| P5 | RT-5 | Local embedding models by dimension (≤768) and quality for chat text |
| P5 | RT-6 | Bundle signing tool and verification UX |
| P5 | RT-18 | Citation-support evaluation (claim-to-span attribution, local judge models) |
| P6 | RT-9 | iOS encrypted backup decryption libraries |

Output contract per RT: current sources with dates, a recommendation, and the spec section
it would change. On return: sonnet-verify checks every citation (same route as the audit,
0 FAIL required) before anything lands in the spec.

## Sequence

| Step | What | Depends on | Owner / model | Acceptance |
|---|---|---|---|---|
| S0 | Owner reads rev 2 — at minimum §3 (lines 116–770), §6 (863–884), §12 (1091–1122) | — | owner | owner says "approved" or lists changes |
| S1 | Astra Pro research prompt, scope above | — | supervisor drafts; owner runs it in ChatGPT; sonnet-verify on return | 0 FAIL citations |
| S2 | P0 packet: `~/code/chatstack`, uv workspace, two empty packages, CI testing the installed wheel | S0 | Sonnet (medium) drafts from §3.2, §4, §5, §6 P0 row, §7; supervisor reviews | matches the §6 P0 exit row and §7 gates |
| S3 | Disk headroom before P0.5(a). Measured candidates: `Downloads/POSSIE_WAVE_A_20261008_131055` 7.9 GB, `~/Library/Caches` 5.7 GB, `~/code/dopemux-mvp` 26 GB (check worktrees), `~/code/DopeTranzScribe` 16 GB | — | owner decides; no agent deletion | ≥ 2× `chat.db` snapshot size free, plus room for P5 |
| S4 | P0.5 packet: spikes (a)–(e) on the owner's real data; records the measurements §10 asks for; freezes schema v2 | S2, S3 | Opus (high) drafts the measurement design; supervisor reviews | each spike has a written pass/fail threshold before it runs |
| S5 | P1 packet | S4 (a), RT-2, RT-3 | Sonnet drafts; supervisor reviews | §6 P1 exit row |
| S6 | Register `chatstack` with Control Tower; archive this repo's TaskMaster list as legacy | S2 | deterministic tooling | worktree listed; list marked legacy |

Cost basis: capability, not price. Prices are UNKNOWN (no receipts). Requested models are
recorded per step; observed identity is UNKNOWN until a runtime receipt exists.

## Not in this plan

- Any edit to the rev 2 spec. Changes come from S1 results after verification, or from
  the owner's read in S0.
- P2–P7 packets. Written when the phase before each one exits.
