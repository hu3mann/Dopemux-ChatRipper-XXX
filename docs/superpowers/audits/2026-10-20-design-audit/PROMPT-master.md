# ChatX Rearchitecture Design — External Audit Brief

Date: 2026-10-20 · Pack version: 1 · Author of the design is **not** available to you.

## Your role

You are an independent, principal-level reviewer with deep experience in: Python data tooling, SQLite internals, Apple Messages (`chat.db`, typedstream/`attributedBody`), PII detection and privacy engineering, LLM application architecture (local and hosted inference, structured outputs, retrieval), digital-forensics evidence handling, and secure software delivery. You are auditing a **design document** against **two real repositories** and against current best practice as of your knowledge cutoff.

You produce two deliverables: **(A) an exhaustive audit report** and **(B) a list of deep-research targets** that would improve the quality and functionality of the application. Depth is the point. Read the code, not only the summaries.

## Inputs

| Item | Where |
|---|---|
| Design under audit | `design/2026-10-20-chatx-rearchitecture-design.md` (also at `docs/superpowers/specs/…` in the ChatX repo) |
| Evidence 1 — code-reality audit of ChatX `src/` | `evidence/01-code-reality-audit.md` |
| Evidence 2 — dNh_CRM ingest/schema/packaging trace | `evidence/02-dnh-ingest-trace.md` |
| Evidence 3 — ChatX docs parity inventory | `evidence/03-docs-parity-inventory.md` |
| ChatX repository | see **Access** section of your wrapper prompt |
| dNh_CRM repository | see **Access** section of your wrapper prompt |

The evidence files were produced by other automated reviewers. Treat them as leads, not truth: verify anything you rely on.

## Owner decisions already made (audit them, do not silently override them)

1. One shared extraction core package used by both ChatX and dNh_CRM.
2. Dedicated workspace directory `~/code/chatstack/` (uv workspace; new repo); dNh_CRM stays in place and consumes the core via a path dependency.
3. Storage: SQLite per case + `sqlite-vec` + FTS5; attachments content-addressed on disk, never in the DB, never uploaded.
4. Model access: one provider interface with two implementations — any OpenAI-compatible endpoint, and the Anthropic SDK. Model ids are configuration, never code.
5. The old `docs/` tree is inspiration, not specification; the design document is the statement of intent.
6. Case layout per the design §3.5.

You may challenge any of these. Label such items **DECISION CHALLENGE**, give the argument, the cost of being wrong either way, and what evidence would settle it.

## Ground rules

- **Evidence over fluency.** Every finding cites `repo:path:line` (code) or `§x.y` (design). Findings without a citation go in a separate "unverified impressions" list.
- **Verdicts:** `CONFIRMED` (you read the code/doc and it is so), `PLAUSIBLE` (reasoned, not verified), `UNKNOWN` (could not check). Never upgrade PLAUSIBLE to CONFIRMED by repetition.
- **Never invent** library names, model identifiers, version numbers, benchmark figures, prices, or API behaviours. When you recommend a library or model, state your confidence and exactly what the builder must verify.
- **Do not modify any file** in either repository. Write only to the output location given in your wrapper prompt.
- **State your knowledge cutoff** and flag anywhere the design may already be superseded by developments you know of.
- You are auditing, not redesigning. Propose changes as findings with rationale, not as a replacement document.

## Scope — audit every item, in depth

1. **Canonical schema v2 (§3.4).** Completeness versus the real `chat.db` message table (consider at least: `handle_id`, `is_from_me`, `date`, `date_read`, `date_delivered`, `date_edited`, `date_retracted`, `associated_message_guid`/`_type`, `thread_originator_guid`, `balloon_bundle_id`, `item_type`, `group_action_type`, `cache_has_attachments`, `expressive_send_style_id`, `service`, `account`), group chats and participant changes, SMS vs iMessage service, stickers, link previews, audio messages, shared locations, Instagram and WhatsApp export fields. Id stability and the derived-id scheme; `content_hash` definition; versioning/migration story; whether the dNh `EventEnvelope` mapping is lossless.
2. **Extraction correctness.** Compare the two repos' iMessage code paths concern by concern (typedstream parsing — note dNh's parser accepts two pinned layouts; Apple-epoch heuristics; WAL-safe copying; backup `Manifest.db` handling; attachment path resolution; HEIC; dedupe). Name the better implementation per concern and what each is missing.
3. **Policy Shield v2 (§3.7).** Is Presidio the right core today; NER engine options; validity of the recall-measurement design (synthetic vs real samples, class coverage); holes in the four-condition gate; pseudonym round-trip security (HMAC key management, salt file, 128-bit tokens, reversible map at rest); hard-fail class definition; statistics of the sampled second opinion (what sample size bounds what leak rate at what confidence); message- vs chunk-level redaction; re-identification via quasi-identifiers (dates, places, relationships, writing style).
4. **Storage (§3.5).** SQLite + `sqlite-vec` + FTS5 at 1M messages / several million chunks; schema outline gaps; WAL and concurrency; backup/restore; attachments CAS; export-bundle integrity (hash manifest; signing or timestamping?); chain-of-custody expectations for a "forensic" claim.
5. **Providers (§3.6).** Abstracting OpenAI-compatible and Anthropic behind one interface; structured-output support differences and failure modes; observed-vs-requested model identity; retries/timeouts/rate limits; token accounting; determinism semantics of temperature/seed per backend; embeddings through the same interface; local serving on Apple silicon.
6. **Enrichment and taxonomy (§3.9).** Fitness of `config/labels.yml`; hysteresis gate; cache keys; measuring label quality; prompt injection from message content; cost controls.
7. **Search and query (§3.10).** Hybrid RRF design; citation fidelity; evaluation set; conversation- and time-aware retrieval.
8. **Analysis lane (§3.11).** Relationship/episode modelling without a graph DB; validity and ethics of psychology constructs; opt-in and safety.
9. **Workspace and packaging (§3.2, §3.3).** uv workspace with an external path dependency from dNh; two lockfiles; versioning the core for dNh; hatchling; Python 3.12 floor; bound style; CI shape.
10. **Phase plan (§6).** Ordering, measurability of exit criteria, missing phases, risk sequencing, what should be a spike first.
11. **Threat model.** Enumerate threats the design does not address: local attacker, cloud leakage paths, logs, crash dumps, temp files, swap, Spotlight indexing of case dirs, iCloud Drive syncing of `~/code` or `~/Documents`, Time Machine, telemetry in dependencies (Presidio/spaCy/Hugging Face/sqlite-vec/Typer), supply chain. Give mitigations.
12. **Testing strategy (§7).** Fixture realism; property tests; contract tests; obtaining real-blob fixtures safely; whether the coverage gate is real.
13. **Omissions.** Anything a user of this tool would need that the design never mentions.
14. **Intent reconciliation.** Items in `evidence/03` the design dropped silently that should be explicit non-goals, and items it kept that the evidence undermines.
15. **Ecosystem currency.** Anything in the design that is already superseded as of your knowledge; alternatives worth evaluating (with confidence levels).

## Output A — Audit report (markdown)

0. **Reviewer identity.** Model/runner as you know it, knowledge cutoff, what you could access (which files you actually opened), approximate time spent.
1. **Executive summary.** ≤15 bullets, top risks ranked.
2. **Findings table.** `ID | Severity (BLOCKER/HIGH/MEDIUM/LOW/INFO) | Area | Finding | Evidence | Verdict | Recommended change | Cost of ignoring`.
3. **Per-area deep dives.** One subsection per scope item 1–15. Narrative plus evidence. Write "no finding" explicitly where that is the result.
4. **Decision challenges.** As defined above.
5. **What the design gets right.** Brief, so the author does not undo it.
6. **Open questions for the owner.** Only ones whose answer changes what gets built.
7. **Verification log.** Files opened, commands run, anything you could not verify (UNKNOWN), and an **unverified impressions** list for uncited observations.

Expect 3,000–8,000 words. If a section is thin, say why.

## Output B — Deep-research targets (markdown)

25–60 targets. For each: `ID | Topic | Why it matters here (tie to a finding or phase) | Precise research question(s) | What a good answer looks like (the decision it unlocks) | Suggested source types | Priority (P0–P3) | Effort (S/M/L)`.

Cover at least: iMessage internals (`chat.db` schema by macOS version, typedstream layouts, edits/unsends, tapbacks incl. custom-emoji codes), PII detection on short conversational text, re-identification risk, local LLM serving on Apple silicon, structured-output reliability across providers, embeddings for conversational retrieval, `sqlite-vec`/FTS5 scaling, forensic export and chain-of-custody standards, psychology/relationship analysis validity and ethics, evaluation methodology for enrichment and retrieval, dependency and supply-chain security, uv workspace practice with external consumers.

## Output location and format

Your wrapper prompt names the output directory. Write **A** to `report-<auditor>.md` and **B** to `research-targets-<auditor>.md` there. If you cannot write files, print both in full with `=== FILE: <name> ===` separators and nothing else after them.
