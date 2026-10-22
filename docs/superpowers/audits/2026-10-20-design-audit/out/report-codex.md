# 0. Reviewer identity

| Item | Disclosure |
|---|---|
| Auditor | **codex** |
| Runner / model | Codex agent runtime; described to this session as GPT-6 based. Exact supervisor model identifier, reasoning effort, and execution receipt: **UNKNOWN**. |
| Knowledge cutoff | **UNKNOWN: no authoritative cutoff date was supplied by the runtime.** I do not claim intrinsic knowledge current to October 2026. Ecosystem claims below use explicitly cited primary sources retrieved during this audit. |
| Audit date / time | 2026-10-20; approximately 35 minutes of wall-clock work, estimated, including concurrent review. |
| Independence | This audit session did not implement or supervise the subject design. Supplied automated evidence was treated as leads. |
| Subject | On-disk working trees, not a clean checkout. ChatX branch `governance-doctrine-integration`, HEAD `9c3dd6b01197a1205fc12c6b5bde6ba7cba258f9`; dNh branch `migrate-cheaperinference`, HEAD `39c75bdec38d0fb4853d914056669615c1c1e1b6`. Both dirty. |
| Design SHA-256 | `c481b18880dae379ff2b39bfdeb0bd2d9e4a81956ee84deda4aae1cc8bd9f2a7` |
| Access | Repository text, synthetic fixture definitions, configuration, CI, and native web search. No personal database, runtime environment, credentials, model endpoint, test execution, or package installation. |
| Files actually opened | Full brief, supplied design, evidence 01–03, ChatX `AGENTS.md`, `CLAUDE.md`, `docs/agent-workflows.md`; selected source, schema, test and build files enumerated in §7.1. The supervisor directly opened both repositories' product files; delegated reads are identified separately. “Opened” includes selected line ranges, not necessarily whole-file review. |
| Delegation | Three bounded read-only slices: extraction/CRM; privacy/enrichment; storage/packaging/testing/intent. Each requested `gpt-6.1-sol`, medium effort, one pass, no fallback or retry. Observed execution identity and billing: **UNKNOWN**. Selection followed repository audit routing; no measured savings claimed. Supervisor checked decisive citations and retained synthesis. |

Notation: `ChatX:` means `/Users/hue/code/Dopemux-ChatRipperXXX/`; `dNh:` means `/Users/hue/code/dNh_CRM/`. Bare `§` references identify sections of the supplied design. **CONFIRMED** means the cited text/code establishes the stated property or omission; it does not mean the resulting failure was executed. **PLAUSIBLE** identifies inferred consequences. **UNKNOWN** identifies unavailable evidence.

# 1. Executive summary

- **Design verdict: FAIL for implementation approval in its current form; acceptance NOT_GRANTED.** The architectural direction is useful, but source fidelity and cloud authorization contracts need correction before dependent work.
- **BLOCKER:** §3.7 cannot establish real-world privacy using an optional real corpus, an unspecified sample, and “classes present” determined by an imperfect detector. Synthetic recall is not a release assurance.
- **BLOCKER:** constructing a cloud provider with a gate token does not bind every request to approved bytes, context, destination, policy, and case revision. Localhost is also insufficient evidence of local execution.
- **HIGH:** the retained “WAL-safe” copier has no consistent snapshot boundary. Its WAL test copies fake text files.
- **HIGH:** the canonical contract lacks source-event fidelity, uncertainty in time, stable occurrence identity, and a reproducible content-hash definition.
- **HIGH:** canonical-to-dNh mapping is intentionally lossy in places but is presented as an uncomplicated gain; changing dedupe inputs can change replay behavior.
- **HIGH:** reused parsers carry material defects: reaction removals treated as additions, backup binary-copy context omitted, unrestricted attachment paths, and WhatsApp ordinary text discarded as system content.
- **HIGH:** case transactions, CAS publication, migration recovery, backup/restore, and export custody are left unspecified.
- **HIGH:** the provider protocol promises embedding support across implementations although Anthropic documents no native embedding model; capabilities and result receipts need explicit contracts.
- **HIGH:** dimension alone does not identify an embedding space; retrieval lacks a rigorous relevance and citation evaluation contract.
- **HIGH:** taxonomy labels include sensitive inferences; schema validity and model confidence do not establish label truth or psychology validity.
- **HIGH:** phase dependencies are inconsistent: P3 needs P4's local provider; P4 needs P5's query; chunking has no assigned delivery phase.
- **Current-source corrections:** SQLite documents a 2026 WAL corruption fix; Presidio's project stewardship has changed; OpenAI Privacy Filter merits a local evaluation; RFC 9457 supersedes RFC 7807.
- Tests, performance, installed wheels, real-data coverage and deployment state are **NOT_RUN/UNKNOWN**, not passing by inference.

# 2. Findings table

| ID | Severity | Area | Finding | Evidence | Verdict | Recommended change | Cost of ignoring |
|---|---|---|---|---|---|---|---|
| F01 | HIGH | Schema | Source-specific facts and historical membership lack guaranteed preservation. | §3.4; ChatX:src/chatx/imessage/extract.py:88–108 | CONFIRMED | Add versioned source evidence and capability/loss accounting. | Irrecoverable evidentiary loss. |
| F02 | HIGH | Identity | Derived IDs collapse identical occurrences; content hash includes mutable representation fields. | §3.4 fields `msg_id`, `content_hash`, `sender`, `attachments` | CONFIRMED | Separate source occurrence, revision and representation identities. | False dedupe and unstable replay. |
| F03 | HIGH | Time | Unknown export zones cannot satisfy unconditional aware-UTC timestamps. | §3.4, V6; dNh:src/dnh_crm/ingest/whatsapp_export.py:177–193 | CONFIRMED | Preserve unresolved local time; require explicit resolution. | Invented chronology. |
| F04 | HIGH | Integration | dNh mapping omits facts and changes existing dedupe semantics. | §9; dNh:src/dnh_crm/ingest/normalizer.py:26–47; ingest/dedupe.py:15–25 | CONFIRMED | Publish mapping/loss and compatibility contracts. | Duplicate or missing downstream events. |
| F05 | HIGH | Acquisition | Sequential DB/WAL/SHM copying is called WAL-safe without snapshot control. | §3.13; ChatX:src/chatx/imessage/db.py:25–43 | CONFIRMED | Specify consistent acquisition and live-WAL tests. | Inconsistent evidence. |
| F06 | HIGH | Extraction | Typedstream coverage is narrow; reaction/reply/edit reuse needs rework. | §8, V1–V2; dNh:src/dnh_crm/ingest/imessage_attributed_body.py:69–80; ChatX:src/chatx/imessage/reactions.py:33–37 | CONFIRMED | Preserve source events and unsupported statuses; qualify real layouts. | Missing text or false conversation history. |
| F07 | HIGH | Attachments | Backup context is lost at the caller; source paths lack containment. | ChatX:src/chatx/imessage/extract.py:283–286; imessage/attachments.py:97–124; imessage/backup.py:129–147; §8 | CONFIRMED | Isolate source roots and fix end-to-end contracts before reuse. | Wrong-source or unrelated local files copied. |
| F08 | HIGH | Other imports | WhatsApp substring filtering drops ordinary messages; PDF invents timestamps. | dNh:src/dnh_crm/ingest/whatsapp_export.py:33–49,105–108,196–198; ChatX:src/chatx/pdf_ingest/reader.py:68–102; §8 | CONFIRMED | Source-specific grammars, uncertainty and completeness tests. | Silent loss and fabricated facts. |
| F09 | BLOCKER | Shield | Evaluation eligibility and statistical assurance are insufficiently defined. | §3.7, §6 P3, §12.3 | CONFIRMED | Require representative held-out evidence or keep cloud disabled. | Undetected private data released. |
| F10 | BLOCKER | Egress | Gate token is not bound to each exact request; local routing can hide cloud execution. | §3.6–3.7, §5.4; [Ollama compatibility](https://docs.ollama.com/api/openai-compatibility) | CONFIRMED | Authorize final serialized payload and verified route at dispatch. | Gate bypass despite valid construction. |
| F11 | HIGH | Pseudonyms | Token width conflicts; key/map/export lifecycle is unspecified. | §3.7; ChatX:src/chatx/identity/normalize.py:47–64; redaction/patterns.py:227–234 | CONFIRMED | Explicit 128-bit encoding, protected key/map and scoped rehydration. | Reidentification or irreversible identity loss. |
| F12 | HIGH | Storage | Transaction, writer, migration and recovery invariants are absent. | §3.5, §6 P2, §7 | CONFIRMED | Define durability/replay invariants before DDL. | Partial cases falsely marked complete. |
| F13 | HIGH | Scale | 100k-message measurements do not qualify millions of chunks. | §6 P2/P5, V4; dNh:src/dnh_crm/store/migrations.py:197–237 | CONFIRMED | Early capacity spike with explicit workloads and bounds. | Late redesign or unusable imports. |
| F14 | HIGH | CAS/export | Hash paths and a ZIP manifest omit publication and custody guarantees. | §3.5, §3.10; ChatX:src/chatx/imessage/attachments.py:246–269 | CONFIRMED | Atomic CAS and consistent export with independent verification. | Corrupt or unauthenticated bundles. |
| F15 | HIGH | Providers | Universal generation/embed protocol hides unsupported capabilities. | §3.6; [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) | CONFIRMED | Capability negotiation; separate embedding binding. | Runtime failures or undisclosed provider substitution. |
| F16 | HIGH | Provider operation | Retry, timeout, usage and determinism semantics are missing. | §3.6–3.9; [structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | CONFIRMED | Typed result/error receipts and bounded call policy. | Duplicate spend and unverifiable outputs. |
| F17 | HIGH | Taxonomy | “Coarse” does not establish privacy or construct validity. | ChatX:config/labels.yml:191–238,248–285,307–425; §3.9 | CONFIRMED | Reviewed visibility policy and label-specific evaluation. | Sensitive false claims exported. |
| F18 | MEDIUM | Enrichment | Existing hysteresis has no state; proposed cache key is incomplete. | ChatX:src/chatx/enrichment/enricher.py:164–176; §3.9 | CONFIRMED | Specify state machine or rename gate; bind full input/config. | Order-dependent or stale classifications. |
| F19 | HIGH | Retrieval | Citation fidelity and derivative invalidation need contracts. | §3.10; ChatX:src/chatx/indexing/vector_store.py:170–181,329–335 | CONFIRMED | Referential links, versioned spaces and citation checks. | Unsupported answers with plausible references. |
| F20 | HIGH | Analysis | Ported pattern rules do not establish psychology validity or direction. | §3.11; ChatX:src/chatx/storage/psychology_relationship_mapper.py:67–94 | CONFIRMED | Evidence-linked, abstaining, non-diagnostic hypotheses. | Harmful allegations presented as findings. |
| F21 | HIGH | Packaging | Editable sibling path does not freeze core bytes for dNh. | §3.2, §5.1, V8 | CONFIRMED | Pin source revision/build and test both consumer environments. | Unreviewed behavior drift. |
| F22 | MEDIUM | Packaging | Installed resources and isolated core dependencies are unqualified. | §3.3–3.4; ChatX:pyproject.toml:121–130; src/chatx/schemas/validator.py:14–36 | CONFIRMED | Wheel/resource smoke outside checkout. | Clean installation fails despite workspace tests. |
| F23 | HIGH | Phases | Provider/query prerequisites and chunk delivery are inconsistent. | §3.7–3.10, §4, §6 | CONFIRMED | Correct dependency order and measurable exits. | Premature phase acceptance. |
| F24 | HIGH | Threat model | Local data exposure and malicious input boundaries are largely unspecified. | §3.5, §3.13, §7 | CONFIRMED | Add the threat/control inventory in area 11. | Raw histories escape outside the model gate. |
| F25 | HIGH | Tests | Coverage is currently hollow; fixture names overstate realism. | ChatX:pyproject.toml:187–206; tests/imessage/test_db_copy.py:38–50; dNh:tests/integration/test_imessage_real_source_ingest.py:13–41 | CONFIRMED | Realistic differential/contract tests plus honest denominators. | Green checks preserve wrong assumptions. |
| F26 | MEDIUM | Operations | Resume, deletion, repair and partial-result behavior lack user contracts. | §3.12, §6–7 | CONFIRMED | Define lifecycle and operator-visible outcomes. | Unrecoverable long jobs or stale sensitive derivatives. |
| F27 | MEDIUM | Intent | Several useful old requirements disappear without disposition. | §2, §3.12; ChatX:docs/interfaces.md:48–62,281–298; docs/operations/non-functional-requirements.md:44,111,142 | CONFIRMED | Explicit keep/defer/non-goal ledger. | Scope expectations remain contradictory. |
| F28 | HIGH | Currency | SQLite WAL fix qualification is missing from the runtime contract. | §3.3, §3.5; [SQLite WAL-reset bug](https://sqlite.org/wal.html#walreset) | CONFIRMED | Require fixed runtime or documented backport; verify linked SQLite. | Known corruption exposure on affected runtimes. |
| F29 | MEDIUM | Currency | Presidio selection needs current stewardship/model comparison. | §3.7; [Presidio FAQ](https://github.com/data-privacy-stack/presidio/blob/main/docs/faq.md); [Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) | CONFIRMED | Evaluate current local candidates without assumed recall. | Stale dependency/research decisions. |
| F30 | LOW | Currency | Error-standard reference is superseded. | §3.12; [RFC 9457](https://www.rfc-editor.org/info/rfc9457/) | CONFIRMED | Use current problem-details reference with CLI-specific semantics. | Unnecessary specification drift. |

# 3. Per-area deep dives

## 3.1 Canonical schema v2

The generated-schema approach corrects a real mismatch: Pydantic defaults allow omitted text/reaction/attachment fields while the checked-in schema requires them; JSON Schema forbids extras whereas the current message model lacks that setting (ChatX:src/chatx/schemas/message.py:43–76; schemas/message.schema.json:6–18). However, one generated schema still needs semantic validation: content-kind consistency, identifiers, finite sizes, time uncertainty, unique attachment/reaction identities and immutable revisions.

The brief's requested Apple field accounting is:

| Source fields | Proposed representation / missing contract |
|---|---|
| `handle_id`, `is_from_me` | Normalized sender/direction; original handle row, account-relative self identity and recipient set missing. |
| `date` | `sent_at`; raw integer, unit, precision and conversion decision not required. |
| `date_read`, `date_delivered` | No typed destination or receipt semantics. |
| `date_edited`, `date_retracted` | Partial edit/unsent representation; no mandatory retraction time or ordered revision evidence. |
| `associated_message_guid`, `_type` | Reactions/reply projection; no raw code, source reaction ID, target part or unresolved-reference record. |
| `thread_originator_guid` | Explicit field, but extraction/mapping needs real fixtures. |
| `balloon_bundle_id`, `item_type`, `group_action_type` | No guaranteed representation of app payloads/system actions. |
| `cache_has_attachments` | Attachment list/missing flag cannot explain source flag versus missing join inconsistency. |
| `expressive_send_style_id` | No explicit effect/style preservation. |
| `service`, `account` | SMS/iMessage enum helps, but transport/account evidence and transitions are not preserved explicitly. |

These omissions are **CONFIRMED in §3.4**; the actual Apple schemas across releases remain **UNKNOWN**. Preserve original row/blob evidence and a versioned source extension instead of forcing every field into a universal message. A generic optional, unhashed `source_meta` is not a preservation guarantee. Conversation participants need temporal membership, join/leave actor and group-name history, not just a table name in §3.5. Stickers need association/placement; link previews need target/payload provenance; audio needs duration and derivative links; shared locations need time, coordinate precision and privacy classification. None is fully specified.

Instagram requires export/member path, original sender identity, timestamp precision, reaction semantics and media references. The current parser uses file-local index in IDs and preserves only raw key names, not values (ChatX:src/chatx/instagram/extract.py:65–118). WhatsApp needs locale, exporter identity, media-omitted/system/deleted records and unresolved timezone. Email additionally needs recipients, headers, threading and MIME-part evidence. The platform enum includes `telegram` and `txt`, but `source_kind` has no corresponding kinds: choose supported combinations or reject them explicitly (§3.4, §2).

F02 is a deterministic identity defect, not a probabilistic SHA collision: two identical messages by the same sender in the same timestamp resolution have identical proposed tuples. Attachment-only messages can collide despite different binaries; edits change a derived ID. Require stable source occurrence identifiers plus a separately versioned cross-import dedupe policy. Scope native IDs by platform/account/source identity rather than assuming global uniqueness. Specify canonical serialization, null/default treatment, ordering of arrays, Unicode preservation, UTC precision and hash-domain version. `sender.pseudonym`, attachment storage paths, later hashes and reaction updates currently fall inside the proposed content-hash domain. Separate immutable source/revision hashes from mutable view hashes. Frozen containers also need an explicit policy for nested lists/dicts.

The dNh mapping is not lossless. Its envelope forbids extra fields, while `EventExternal` and text `EventPayload` permit them; attachment-only payload does not (dNh:src/dnh_crm/events.py:484–530,1902–1918). Attachment detail already has a separate event model (:806–827). A future adapter could retain more, but §9 does not define that. Empty, system, reaction-only, edited and outbound records require deliberate mapping, exclusion or separate events; `MSG_INBOUND_RECEIVED` cannot be the unexplained label for all of them. Existing dedupe excludes attachments and uses a specific tuple; its store has both unique event ID and unique dedupe keys (dNh:src/dnh_crm/ingest/dedupe.py:15–25; store/migrations.py:8,23). Test migration against existing imports before changing hashes.

## 3.2 Extraction correctness

“Better” below means a better starting point from inspected code, not validated acceptance.

| Concern | Better implementation | What remains missing |
|---|---|---|
| Typedstream | dNh | Two pinned layouts only, unwired, trailing archive validity and real coverage unproven. |
| Apple epochs | dNh for rejecting invalid values; neither for unit certainty | First-plausible date heuristics remain ambiguous; ChatX substitutes current time. |
| Live WAL reading | dNh uses SQLite-managed read-only access | Neither establishes an archived consistent acquisition with custody. |
| Backup Manifest.db | ChatX | fileID validation, containment, correct caller context, encrypted support deliberately deferred. |
| Attachment resolution | ChatX has richer functionality | Untrusted path/symlink handling and cross-source fallback need correction. |
| HEIC | ChatX for identification | Actual decoder availability and safe derivative behavior unverified. |
| Content dedupe | ChatX for binaries; dNh for message idempotency | Atomic CAS publication and historical replay compatibility. |
| Reactions/replies/outbound | ChatX has relevant structure | Removal semantics, target-part resolution, source-event preservation, scope bug. |
| Edits/unsends | Neither inspected iMessage path | Source-version fixtures and lifecycle projection. |

The dNh decoder bounds input/output and validates recognized inheritance layouts; it extracts the string then returns without validating the entire suffix (dNh:src/dnh_crm/ingest/imessage_attributed_body.py:23–24,69–80,220–246). State its capability accurately. V2's fallback instruction is internally inconsistent: fallback text should say `text_source=text_column`; `none` should identify no decoded text. Do not turn unsupported blobs into empty successful messages. Preserve decoder status, raw blob hash and unresolved counts.

ChatX copies three live files sequentially (ChatX:src/chatx/imessage/db.py:25–43), while the test writes “fake db”/“fake wal” (tests/imessage/test_db_copy.py:38–50). That does not establish snapshot consistency. SQLite's supported [backup API](https://www.sqlite.org/backup.html) provides a consistent copy mechanism; qualify its acquisition behavior and source-side effects before selection. Do not run a checkpoint against the owner's original merely to simplify copying.

ChatX's query omits edit/unsend/thread-originator columns, uses exact GUID matches, and treats removal-range rows as custom additions (imessage/extract.py:88–108,226–259; imessage/reactions.py:33–37). Preserve raw events, unresolved targets and deterministic ordering before deriving the visible reaction state. Its contact query includes every chat containing an outgoing message (:379–385); the design correctly identifies that bug.

Backup binary copying omits `backup_dir` even though the helper accepts it (imessage/extract.py:283–286; tests/imessage/test_backup_attachments_copy.py:63). Attachment resolution can select arbitrary local paths and fall back from a backup to host files (imessage/attachments.py:97–124). Hashing before copy, trusting an existing destination and swallowing errors are unsafe reuse defaults (:246–269). HEIC extension recognition is distinct from successful decoding: thumbnail code calls Pillow, with exceptions suppressed by its caller (media/thumbnail.py:16–21; imessage/attachments.py:320–324).

WhatsApp's filter treats ordinary words such as “left” and “added” anywhere in a body as system markers; supported date parsing assumes month/day forms (dNh:src/dnh_crm/ingest/whatsapp_export.py:33–49,105–108,177–198). Email's naive-date fallback assigns UTC (ingest/email_eml.py:203–212). ChatX's PDF reader synthesizes present-day timestamps and labels transcripts iMessage (pdf_ingest/reader.py:68–102). These are data-quality defects to fix before port acceptance, not merely future feature requests.

## 3.3 Policy Shield v2

Presidio is a reasonable recognizer/anonymizer framework; the design's pluggable engine and measured recall are improvements. Its own [FAQ](https://github.com/data-privacy-stack/presidio/blob/main/docs/faq.md) explicitly disclaims complete detection. Engine selection must compare multilingual short-chat cases, aliases, misspellings, code-switching, emoji, fragmented identifiers, quoted messages and contextual names. Evaluate spaCy, transformer/GLiNER candidates and the newer local candidate in area 15; no engine is qualified here.

Define entity classes independently of detector outputs. Gate condition 1 cannot safely infer absent classes from a detector that might miss them. No positives in a class means **UNKNOWN**, not perfect recall. The report must bind corpus hashes, annotation policy, recognizer/model/tokenizer artifacts, language, thresholds and evaluation-code version. A shield version/config hash alone does not demonstrate these identities. Require held-out conversation/person splits, annotator disagreement resolution, false-positive measurement and strict-span versus partial-span metrics. Synthetic generation is valuable for controlled edge cases but cannot establish real-distribution coverage. §12.3 makes real samples optional while §3.7 invokes real recall; without representative evidence, cloud should remain disabled.

For zero observed misses in `n` independent labelled positive entities, a one-sided 95% upper bound on miss probability is `1 - 0.05^(1/n)`. Therefore at least **598** positives with zero misses are needed to bound the miss rate below 0.005, or **2,995** below 0.001, for one class. These are mathematical sample requirements, not measured outcomes. Multiple classes need simultaneous-confidence treatment; clustered names within one conversation are not independent evidence.

The same formula describes zero observed leaking chunks only under random independent sampling and perfect leak adjudication. At `n=100`, the upper bound is about 2.95%; at 600, about 0.50%; at 3,000, about 0.10%. Imperfect local-model detection makes the bound weaker. Repeated overlapping chunks, seeded samples reused across runs and adaptive adversaries invalidate simplistic independence assumptions. Define the sampling unit, stratification, adjudicator sensitivity, and behavior on malformed/refused/uncertain judgments. “Confirmed leak” must not allow an unresolved suspicion to pass.

Hard-fail classes need a versioned policy definition: which content blocks the entire run, whether checks apply before and after redaction, and how quoted/test material is handled. Existing regex comments describe demo patterns (ChatX:src/chatx/redaction/patterns.py:162–176); they are not a policy specification. The old token-ratio metric and warning-only behavior are directly confirmed (redaction/policy_shield.py:138–194). Dropped chunks must count as failure, never improved recall.

Redact at message level with cross-turn context, then validate the complete assembled payload. Chunk-only redaction can miss split identifiers, duplicate inconsistent pseudonyms, or leak dates/speakers/context headers. Scan query text, citations, filenames, schema descriptions, context and retry diagnostics too. A request model without an attachment field can still carry base64, URLs, OCR/transcripts or raw metadata inside text. Decide explicitly whether attachment-derived text is eligible; original binaries remain prohibited by the owner.

§3.7 combines `id8` tokens with 128-bit identifiers. Existing identity HMAC already uses 32 hex characters; the separate redaction tokenizer uses eight hex characters and a salted non-HMAC hash (identity/normalize.py:47–54; redaction/patterns.py:227–234). Standardize the encoding and distinguish a secret HMAC key from a public salt. Specify atomic exclusive key creation, parent-directory protection, validation, backup, rotation and loss. A plaintext reversible map in the same case database is not protected by the salt file's mode. Encrypt or otherwise protect it under the defined local threat model, exclude it from ordinary exports, and authorize rehydration only for tokens actually sent in that request. Reject forged, unknown and cross-case tokens.

Finally, dates, places, rare events, relationship networks and writing style can identify someone after direct identifiers are removed. Stable pseudonyms also expose linkage. Report pseudonymization and measured residual risk, not anonymity; allow stronger date/location generalization and case-specific cloud restrictions.

## 3.4 Storage

dNh implements vec0, FTS5 triggers and RRF (dNh:src/dnh_crm/store/migrations.py:197–237; rag_repo.py:153–179). That is useful precedent, not evidence that a deployed extension is present: loading errors are tolerated and vector tests can skip (migrations.py:327–336; tests/integration/test_rag_mvp.py:82–87). New `case status` must expose missing capabilities and incomplete indexes.

Before DDL, specify canonical immutable source/revision rows, foreign keys, compound uniqueness, normalized participant membership, chunk-message spans, source acquisition records, invalid/quarantined rows and derivative version references. Avoid overwriting raw messages with redacted versions. Define the sole writer, transaction-sized batches, cancellation/resume cursors, import completion markers and deterministic duplicate handling. SQLite WAL still has one writer and requires checkpoint management; a case database alone is not necessarily the entire live state ([SQLite WAL](https://sqlite.org/wal.html)).

SQL migrations need checksums, transactional application where supported, interrupted-run recovery, schema-version compatibility and restore-before-migration procedures. A small runner is adequate if these contracts are tested. Backup must capture a consistent DB and corresponding CAS inventory, then restore and verify elsewhere.

Capacity arithmetic: one million 1024-dimensional float32 vectors occupy **4.096 GB decimal of vector payload alone**; three million occupy **12.288 GB**, excluding text, FTS, metadata, WAL and additional spaces. This is not an RSS or latency benchmark. Test cold/warm retrieval, filters, parallel import/query, disk-full behavior, extension versions, chosen dimensions and target corpus shape. The 100k-message P2 measurement does not settle V4. Do not assume current `sqlite-vec` development features are available in the deployed wheel.

CAS requires bounded staging, hash-as-copied, atomic publication, collision/existing-object verification, regular-file/containment checks, missing-byte states and crash reconciliation. Deduplication preserves content, not source occurrence metadata. Original HEIC/audio bytes and derivatives need separate hashes.

A ZIP whose manifest and contents are replaceable together proves internal consistency, not authorship or custody. Define acquisition identity, operator/action times, transformation versions, completeness, exclusions and an offline verifier. An independently stored manifest hash, signature and possibly trusted timestamp can anchor authenticity where the owner needs it; none alone proves collection history. [NIST IR 8387](https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8387.pdf) describes preservation and separately protected hashes. This audit makes no legal admissibility determination.

## 3.5 Providers

Keep the two adapter families, but qualify exact endpoint/model capabilities. “OpenAI-compatible” is a transport claim, not a guarantee of every schema, seed or embedding operation. Anthropic's [embedding documentation](https://platform.claude.com/docs/en/build-with-claude/embeddings) says it has no native embedding model. `AnthropicProvider.embed` therefore needs an explicit unsupported capability or separately configured embedding implementation; silently routing elsewhere would violate provider and privacy authority.

Return a result envelope containing parsed output or typed failure, finish/refusal reason, requested/observed identity, effective parameters, usage, request ID and latency. A bare `BaseModel` loses operational evidence. Distinguish constrained decoding, JSON mode and prompt-only JSON. Anthropic's [structured-output documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) describes schema limitations and exceptional refusal/token-limit outputs; validation remains necessary. Repeating a deterministic schema incompatibility is not useful retry behavior.

Define connection/read/overall timeouts, concurrency, rate limits, backoff and maximum attempts across both SDK and wrapper. Record every paid attempt, uncertain completion after transport failure, and quarantine retention without leaking raw output to ordinary logs. Record reported usage separately from estimates; include input/context/schema/cache/reasoning usage when exposed. Refuse work exceeding a run budget before dispatch and reconcile actual spend afterward. No price assumptions are made here.

Temperature zero and seed 42 do not promise identical outputs across versions/backends/hardware. Unsupported controls must be rejected or reported as unsupported, never silently accepted. Store response/model artifact identity where obtainable; an echoed model name is a server assertion, not attestation of weights.

Most critically, gate the final payload at dispatch, bound to case revision, policy/evaluation hash, exact serialized request, destination and purpose. Retries and retrieval-augmented queries must use the same boundary. A configured “local” label is untrusted: [Ollama explicitly supports cloud models through its local server](https://docs.ollama.com/api/openai-compatibility). Verify model placement and constrain serving-process egress; cover redirects, proxies and per-case overrides. Apple's actual machine capacity and local endpoint capabilities were not inspected.

## 3.6 Enrichment and taxonomy

The taxonomy contains coarse substance/relationship labels and fine sexual, health and third-party details (ChatX:config/labels.yml:191–238,248–285,307–425). Coarsening does not automatically make those inferences safe to transmit. Carry explicit visibility annotations into generated types, serialization and export. Test rejection of local-only labels in every cloud payload.

An indentation inventory yields 55 coarse labels, 12 fine groups and 99 fine leaves; a semantic YAML parse was **NOT_RUN**. The existing loader expects different top-level structure (enrichment/multi_pass_pipeline.py:102–124), reinforcing the need for compiler validation. Keep duplicate-key detection, mapping validation, version/hash identity and deprecated-label migration in P4.

Current “hysteresis” is a threshold comparison without prior state (enrichment/enricher.py:164–176). True hysteresis needs prior accepted state, explicit transitions, ordering and reset conditions; otherwise name it a confidence threshold. Self-reported confidence needs calibration against labelled data, with class-level precision/recall, abstention and agreement. Evaluate negation, sarcasm, quotation and speaker attribution.

Cache all effective context and generation parameters, taxonomy hash, chunker/redactor versions, language and model/artifact identity. The §3.9 tuple omits several of these unless “input content hash” is explicitly defined over the complete request. Unknown observed identity should not be treated as immutable model identity. Untrusted message instructions must remain quoted evidence, with no tool access or authority to change labels, policies or budgets. Validate output label references against the input set and quarantine unsupported claims.

## 3.7 Search and query

RRF is a sensible baseline. Specify candidate counts, rank constant, tie-breaking, BM25 order, filter timing and overlap dedupe. Use the same case/conversation/time eligibility on both retrieval branches; filtering only after top-k can destroy recall. Group overlapping chunks and expand nearby turns under a token budget so pronouns and replies retain context.

The existing Chroma path saves message count but omits message IDs, then searches for those IDs when creating results (ChatX:src/chatx/indexing/vector_store.py:170–181,329–335). SQLite only helps if chunk-message spans are explicit and preserved through retrieval and rendering. Cite immutable message revision, source row, offset/span, and redaction/translation derivative where applicable. Verify every generated citation resolves and supports its claim; existence of an ID alone is insufficient.

Embedding spaces need model/revision, dimension, normalization, metric, tokenizer/truncation policy and preprocessing/shield/chunker identity. Same dimension does not mean compatible spaces. Define stale/rebuild states after edits, unsends or redaction changes, including synchronized FTS updates and resumable indexing.

The evaluation set should cover exact identifiers, paraphrases, time constraints, multi-turn answers, group speakers, rare terms, multilingual queries, contradictions and unanswerable questions. Measure retrieval recall/ranking separately from answer correctness, citation precision/completeness and abstention. Hold out conversations and compare FTS-only/vector-only/RRF. dNh's small near-exact fixture is not general quality proof (dNh:tests/integration/test_rag_eval_integration.py:34–66).

## 3.8 Analysis lane

Rows and joins can represent relationships and episodes without a graph service; no finding against that owner decision. Define directed participants, time intervals, evidence/revision links, competing interpretations and rule version. Avoid double-counting overlapping chunks.

The old mapper unions labels from two chunks and fires when any source label matches (ChatX:src/chatx/storage/psychology_relationship_mapper.py:67–94). That is not validation of temporal sequences, causation or a person's psychology. Porting as YAML preserves the same risk unless semantics are reviewed. Require per-construct evidence standards, human disagreement analysis, explicit abstention, reversible annotations and non-diagnostic wording.

Opt-in must specify which people and features, local/cloud eligibility, exports and deletion. A tool owner's consent does not establish another participant's consent or the truth of sensitive inferences. Distinguish observed communication, hypothesis and clinical construct; avoid diagnostic scores, coercive recommendations and claims of intent unsupported by messages. Image/audio analysis and encrypted backups need separate gates as the design already proposes (§3.11, §6 P6).

## 3.9 Workspace and packaging

The shared core is appropriate. A sibling editable dependency is useful for development but can change behavior without a new lockfile. Record core package version, schema version, source revision and build hash independently; specify paired checkout layout and compatible dNh revision. Test both lockfiles and a source-independent wheel consumer. This challenges release custody, not the owner's directory choice.

[uv documents](https://docs.astral.sh/uv/concepts/projects/workspaces/) a shared workspace lock and warns that workspace installation cannot enforce dependency isolation between members. [Its source overrides](https://docs.astral.sh/uv/concepts/dependencies/) are uv-specific; publishing must also work without them. Test core installation with only its declared dependencies. Clarify “no storage dependencies” as no application persistence coupling: SQLite source acquisition necessarily uses storage access.

Python 3.12 matches dNh's declared floor; actual installed interpreter versions in the evidence conflict and were not verified. Bound-style consistency alone does not create compatibility. Choose tested ranges per dependency, especially pre-1.0 libraries, and add a controlled update process. Hatchling must include schema/taxonomy resources. The old loader assumes a checkout root while wheel configuration includes only `src/chatx` (ChatX:src/chatx/schemas/validator.py:14–36; pyproject.toml:121–130).

CI needs isolated core/app wheel jobs, macOS arm64 runtime capability checks, mandatory vectors, and external dNh adapter tests. Define whether 90% applies separately to each package; a combined denominator can hide an undertested core or application.

## 3.10 Phase plan

Retain the broad sequence but correct dependencies before approval (F23). Put installable-core/external-consumer feasibility in P0; source/schema/time/identity spikes before P1 commitment; snapshot/CAS/recovery rules before P2; chunking before shield; a minimal verified local-provider path before P3's second opinion. P4 can require queryable SQL results, or query must move earlier.

P1's “real smoke counts” must include input rows, exclusions, unknown layouts, system/reaction events, missing attachments and unsupported features. Counts alone cannot show correctness. P3 needs held-out real evidence and exact payload refusal tests. P4 needs capability/error/budget tests. P5 needs scaled retrieval and an independently restored export, not merely matching hashes. P6 should separate psychology, media and decryption rather than bundle three unrelated risk programs. MCP needs an explicit threat/permission review before P7.

P2/P5 measurements need corpus, machine, versions, dimensions, percentiles and resources. “Promoted to gates once met twice” (§7) is not enough: define user requirements independently to avoid setting acceptance from whichever runs happened to be fast.

## 3.11 Threat model

The following are missing or insufficiently specified in §§3.5/3.13/7. These are threats to address, **not observations that this machine is exposed**.

| Boundary / threat | Required mitigation or decision |
|---|---|
| Other local user / stolen disk | Private case directories, least-privilege permissions, encryption at rest and key separation. |
| Same-user malware / administrator | State limits: mode 0600 and application tokens do not defeat a compromised account; isolate high-value cases and secrets. |
| Cloud leakage | Final-payload allowlist, provider placement/egress verification, no redirects or accidental fallback, retention policy review. |
| Logs, debug traces, raw-response quarantine, crash dumps | Metadata-only ordinary logs, bounded restricted quarantine, exception scrubbing and deliberate retention. |
| Temp copies, swap, caches, previews | Private bounded scratch, cleanup/recovery, encrypted storage; avoid claiming secure erasure on SSDs. |
| Spotlight indexing | Explicit case-location/indexing policy; verify behavior rather than assuming an exclusion works. |
| iCloud Drive / synced Documents or code paths | Detect or disclose sync-sensitive locations; never assume `~/code` is automatically synced or automatically safe. |
| Time Machine / other backups | Deliberate encrypted backup scope, access, retention and key-recovery policy. |
| Presidio, spaCy, Hugging Face, sqlite-vec, Typer dependencies | Inventory actual pinned artifacts, model download behavior, telemetry/update paths and transitive networking; offline inference checks. No blanket telemetry accusation is established here. |
| Model artifacts / native extensions / parsers | Hash-pinned trusted artifacts, license/SBOM tracking, no unreviewed remote code, bounded decoding and extension loading. |
| ZIPs, PDFs, MIME, typedstream, HEIC | Size/decompression/depth/time limits, root containment, symlink/device rejection, sandboxed heavy parsers. |
| Prompt injection / output spoofing | Treat messages as evidence only; no tool authority; output escaping, citation checks and request-scoped token rehydration. |
| Case import/export and MCP | Explicit case selection, read/write capabilities, path restrictions, safe filenames and no automatic actions from imported content. |

A no-socket fixture is useful but narrower than no network: subprocesses/native code, startup downloads and the serving process need separate containment. Lower/upper dependency bounds and vulnerability scanning do not authenticate artifacts. These controls should appear as testable requirements, not security prose alone.

## 3.12 Testing strategy

Coverage deficiency is verified: key pipeline modules are omitted (ChatX:pyproject.toml:198–206), CI uses 60%, and one workflow makes lint/types advisory (.github/workflows/ci.yml:29–33; python-ci.yml:68–81). Design §§5–7 correctly rejects that. Verify collected package inventory and per-package denominators, include branch coverage where useful, and use a negative-control check proving critical failures fail CI. No actual percentage was measured.

Fixture realism matters more than counts. The SQL fixture says attributed blobs are simplified and represents edit history synthetically (ChatX:tests/fixtures/imessage_test_data.sql:135–158). dNh's “real source” test creates a reduced table (tests/integration/test_imessage_real_source_ingest.py:13–41); its typedstream builders pin prefixes but do not prove full real-world coverage (tests/unit/test_imessage_attributed_body.py:59–113).

Obtain owner-authorized local samples with OS/exporter version, feature inventory and acquisition hashes. Keep raw private blobs local; derive reviewed structural fixtures without assuming binary replacement preserves format. Use independently generated expected records and differential checks against another parser, recording disagreement rather than voting it away.

Property tests should cover timestamp unit ambiguity/DST, identifier occurrence multiplicity, normalization idempotence without false merges, serialization stability, reaction add/remove replay, and import retry after partial failure. Add contract tests for actual CLI→store→index→citation flow, backup attachment copying, schema loading from a wheel, SDK refusal/truncation/rate-limit responses and network-denied cloud paths. Crash tests must cover migration, CAS and export boundaries. The performance test currently prints speed on a small synthetic set and asserts counts (ChatX:tests/perf/test_extract_perf.py:89–117); it is not scale qualification.

## 3.13 Omissions

Beyond the main findings, the CLI needs dry-run/import preview; disk-space estimation; progress/cancellation; resumable jobs; a partial-success policy; quarantine inspection/retry; source reconciliation after edits/deletions; backup/restore; verification/repair; and deletion of every derivative, embedding, cache and map (§3.12). Define what remains in backups and immutable exports.

Users also need source coverage reports, explicit timezone/locale/self-identity controls, missing-iCloud-attachment explanations, supported export-format versions, and errors that distinguish unsupported data from empty data. Identity merging must preserve original handles and reversible decisions; lowercasing or phone cleanup cannot prove two handles belong to one person (§3.4; ChatX:src/chatx/identity/normalize.py:26–44).

Export needs explicit raw/private/redacted modes, recipient warnings, deterministic inventory and provenance-preserving interoperability. No proposed default should accidentally distribute the reversible map. The core's boundary between parsing bytes, staging SQLite and writing media needs clarity: §4 says no storage, yet source acquisition inherently uses files and SQLite. Define ownership instead of relying on that slogan.

## 3.14 Intent reconciliation

Evidence 03 was read and key older promises checked. The old docs are inspiration, as instructed; these are disposition requests, not demands to restore everything:

| Older intent | Proposed disposition |
|---|---|
| Generic TXT import; `simulate`/`reply`; timeline/factors/backfill/token inspection | Mark explicit non-goals or assign a phase; enum presence is not support. |
| Checkpoints/restart (§NFR lines 44,55) | Retain as correctness/recovery requirements, even while retiring old speed promises. |
| Metadata-only enrichment update (interfaces:281–298) | Preserve incremental invalidation semantics or document rebuild behavior. |
| Dry-run/self-test/prompt preview (NFR:111,163) | Give concrete CLI equivalents; `providers check` is insufficient. |
| Input token limits, QPS/concurrency, cost ledger, log rotation (NFR:85,89,102,117–124) | Retain bounded operation requirements. |
| Fine labels local-only (NFR:65–67) | Explicitly enforce in types/serialization, not only taxonomy comments. |
| Intel macOS/Linux support (NFR:142) | Declare changed support policy; §11 makes only arm64 required. |
| Pluggable storage backends (architecture:157–161) | Explicitly retire under owner-selected SQLite. |

Here NFR is `ChatX:docs/operations/non-functional-requirements.md`; interfaces and architecture are `ChatX:docs/interfaces.md` and `docs/architecture.md`. Those sources establish each older intent.

Explicit retirement/deferment is already adequate for HTTP/web UI, live capture, Telegram export, differential privacy, Chroma/Neo4j, media research and encrypted backups. Retained premises needing correction are WAL safety, complete parser reuse, dNh deployment assumptions, real fixture coverage and “hysteresis.” Evidence 01 itself repeats the unsafe-copy characterization; repetition across design and evidence does not validate it.

## 3.15 Ecosystem currency

Primary sources were retrieved through native web search on the audit date. These are available-document observations, not installed-version or account-entitlement checks.

- **SQLite — HIGH confidence in published advisory.** The [WAL documentation](https://sqlite.org/wal.html) describes a WAL-reset corruption bug fixed in 3.51.3 and later, with backports 3.44.6 and 3.50.7. Qualify the Python-linked SQLite runtime, extension compatibility and concurrency path; the owner's current version is **UNKNOWN**.
- **Presidio — HIGH confidence in project documentation, UNKNOWN chat recall.** The [current FAQ](https://github.com/data-privacy-stack/presidio/blob/main/docs/faq.md) describes independent community stewardship after Microsoft. Verify release provenance and maintenance expectations. [Anonymizer documentation](https://microsoft.github.io/presidio/anonymizer/) also describes changed random-salt defaults; never rely on default hashing for stable case pseudonyms.
- **Local PII alternative — HIGH confidence in existence; suitability UNKNOWN.** [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) is an open-weight local span detector with eight privacy categories. Evaluate taxonomy coverage, licensing/artifact provenance, Apple hardware support and per-class held-out recall. Its published aggregate benchmark is not proof of this design's 99.5%/99.9% targets.
- **Anthropic — HIGH confidence in documented names, entitlement UNKNOWN.** The [model overview](https://platform.claude.com/docs/en/models/overview) currently lists `claude-sonnet-5-5` and `claude-opus-5-5`; they should not be rejected as invented on this evidence. Keep them in config and verify actual account capability. Structured-output and embedding constraints remain F15–F16.
- **Local serving — HIGH confidence in available projects; performance UNKNOWN.** [MLX LM](https://github.com/ml-explore/mlx-lm) targets Apple silicon; [llama.cpp](https://github.com/ggml-org/llama.cpp) documents Metal and an OpenAI-compatible server. Benchmark pinned local artifacts on the owner's machine for schema support, context, memory, latency and offline behavior. Do not assume vLLM, LM Studio and MLX are interchangeable implementations.
- **sqlite-vec — HIGH confidence in published compatibility warning.** Its [upstream README](https://github.com/asg017/sqlite-vec) still warns of pre-v1 breaking changes. Current main contains ANN-related development files; that does not prove a released production capability. Pin and test the chosen release; evaluate quantization/partitioning before proposing another database.
- **uv — HIGH confidence in documented options.** Current [workspace docs](https://docs.astral.sh/uv/concepts/projects/workspaces/) describe external-workspace sources as well as path-based composition. Verify support in the builder's pinned uv; do not replace the owner's chosen path strategy without evidence.
- **Error standard — CONFIRMED supersession.** [RFC 9457](https://www.rfc-editor.org/info/rfc9457/) obsoletes 7807. Define how HTTP-oriented status fields map to CLI errors and exit codes.

No evidence here establishes that Presidio, SQLite or the shared-core architecture must be replaced. The concrete need is qualification and stronger contracts.

# 4. Decision challenges

| DECISION CHALLENGE | Argument | Cost of being wrong either way | Settling evidence |
|---|---|---|---|
| DC1 — SQLite/vec as unconditional scale commitment (§3.5) | Keep SQLite as baseline, but make the several-million-chunk envelope conditional on an early spike. | Underestimating scale causes late storage redesign; premature replacement adds service and custody complexity. | Representative filtered/cold/warm workload, recovery tests and storage budget. |
| DC2 — One universal provider protocol (§3.6) | Retain two adapters; separate generation and embedding capabilities rather than requiring every method everywhere. | Forced symmetry creates hidden routing; over-fragmentation complicates configuration. | Capability matrix and contract tests for exact endpoints. |
| DC3 — Editable path as consumer release mechanism (§3.2) | Preserve development layout; require immutable revision/build custody for accepted dNh consumption. | Mutable source undermines replay; mandatory publishing too early adds release burden. | Clean paired clones, source drift test, wheel install and version policy. |
| DC4 — Case layout and forensic claim (§3.5) | Keep layout, but separate private operational material from distributable evidence; establish protected authenticity anchors. | Broad exports expose maps/raw logs; excessive ceremony obstructs personal use. | Owner's intended recipient/use, threat model and independent export verification. |
| DC5 — Shared core boundary (§3.1/§4) | Own parsers and evidence types centrally; keep side-effectful identity/key creation and case writes under explicit orchestration. | Overbroad core couples consumers; overly narrow core duplicates correctness logic. | Public API dependency map and isolated consumer fixtures. |
| DC6 — Retiring old specification (§2/§8) | Retain the decision, but publish an explicit intent disposition ledger before archival. | Carrying obsolete promises bloats scope; silent retirement loses recovery/privacy requirements. | Owner decisions on the small area-14 list. |

These are proposed amendments, not silently adopted redesigns.

# 5. What the design gets right

Preserve the shared extraction core, generated schema with drift checks, source provenance, honest unsupported states, case-scoped SQLite/CAS, explicit cloud refusal, requested-versus-observed model identity, whole-package coverage, separate dNh governance, and deferred psychology/media gates (§§3–7,9–10). Removing dead Chroma/Neo4j integration and stub commands reduces the number of unproven contracts. Measured performance is preferable to recycled numerical promises. None of these strengths requires accepting the gaps above.

# 6. Open questions for the owner

1. Is “forensic” personal reproducibility, third-party verification, or externally anchored custody? This changes acquisition/export requirements.
2. If representative local labels are unavailable or recall cannot meet the lower confidence bound, should cloud remain disabled? The current privacy anti-goal implies yes.
3. Must unknown-timezone/undated messages be importable before manual time resolution?
4. Should the dNh adapter preserve all canonical evidence or explicitly consume a supported projection? How must historical dedupe remain compatible?
5. What corpus/attachment size and memory/storage budget must be usable on the actual machine?
6. Which sensitive taxonomy/relationship constructs may be inferred, exported, or sent to cloud, and which are local-only regardless of pseudonyms?
7. Are new-repo history, case-per-import-set default, platform-support changes and area-14 retirements approved?

# 7. Verification log

## 7.1 Files actually opened

Full inputs: audit `PROMPT-master.md`, `design/2026-10-20-chatx-rearchitecture-design.md`, evidence `01-code-reality-audit.md`, `02-dnh-ingest-trace.md`, `03-docs-parity-inventory.md`. Both repository `AGENTS.md` files were read; ChatX `CLAUDE.md` and `docs/agent-workflows.md` were read. The independent-audit skill was read at `/Users/hue/.agents/skills/independent-audit/SKILL.md`; the user brief controls its output-format and test-execution exceptions.

Supervisor directly inspected these product files, sometimes in selected ranges:

- ChatX: `src/chatx/schemas/{message,validator}.py`, `schemas/message.schema.json`, `src/chatx/enrichment/{llm_client,models,enricher}.py`, `src/chatx/instagram/extract.py`, `src/chatx/pdf_ingest/reader.py`, `src/chatx/imessage/{db,extract,reactions,attachments}.py`, `src/chatx/redaction/{policy_shield,patterns}.py`, `src/chatx/identity/normalize.py`, `src/chatx/transformers/chunker.py`, `src/chatx/indexing/vector_store.py`, `src/chatx/storage/psychology_relationship_mapper.py`, `tests/fixtures/imessage_test_data.sql`, `tests/imessage/test_db_copy.py`, `.github/workflows/{ci,python-ci}.yml`, `pyproject.toml`, and selected `config/labels.yml` content.
- dNh: `src/dnh_crm/events.py`, `src/dnh_crm/idempotency.py`, `src/dnh_crm/ingest/{normalizer,dedupe,whatsapp_export,imessage_source,imessage_attributed_body}.py`, `src/dnh_crm/store/{migrations,rag_repo}.py`, `tests/integration/test_imessage_real_source_ingest.py`.

Additional delegated inspection, with cited results checked during synthesis:

- ChatX: `src/chatx/imessage/{time,body_normalize,reactions,backup,attachments}.py`, `src/chatx/media/thumbnail.py`, `src/chatx/redaction/patterns.py`, `src/chatx/enrichment/multi_pass_pipeline.py`, `src/chatx/storage/{base,psychology_relationship_mapper}.py`, `src/chatx/indexing/pipeline.py`, selected `src/chatx/cli/main.py`; `tests/imessage/{test_db_copy,test_time_normalization,test_backup_attachments_copy,test_thumbnails}.py`; `tests/perf/test_extract_perf.py`; `.github/workflows/{ci,python-ci}.yml`; `config/arch-gates.yml`; `docs/{interfaces,architecture,acceptance-criteria}.md`; `docs/operations/non-functional-requirements.md`.
- dNh: `pyproject.toml`, `.github/workflows/ci.yml`; `src/dnh_crm/ingest/{imessage_attributed_body,imessage_mapper,imessage,email_eml,imessage_thread_identity}.py`; selected `src/dnh_crm/store/event_repo.py`; `tests/unit/{test_imessage_attributed_body,test_imessage_source_mapper,test_imessage_source_reader}.py`; `tests/integration/{test_imessage_real_source_ingest,test_rag_mvp,test_rag_eval_integration}.py`.

The privacy slice additionally opened ChatX `src/chatx/enrichment/ollama_client.py`, `src/chatx/utils/logging.py`, `tests/identity/test_normalize.py`, `tests/unit/redaction/test_policy_shield.py`, and `tests/unit/storage/test_psychology_relationship_mapper.py`. Inventory distinguishes full inputs from partial source reads; discovery listings alone do not count as opened content. Excluded tooling directories and secret locations were not opened. Existing output runner logs were counted by `wc`, not read as evidence.

## 7.2 Commands and evidence identity

Read-only commands: `cat`, `nl -ba` with `sed -n`, scoped `rg`/`rg --files`, `awk` for counts/arithmetic/artifact checks, `wc`, `shasum -a 256`, `git -c core.fsmonitor=false status --short --branch`, `git rev-parse HEAD`, and `git diff --stat`/`--name-only`. Native web searches/opens/finds supplied the linked sources. Report creation and final checks were confined to the two output files. No SQLite databases were opened.

Input SHA-256 values:

```text
PROMPT-master.md  7b785076d674738fbe45c1ca099e1f2d73999ee683e2a049505f2ac455d89dc5
design           c481b18880dae379ff2b39bfdeb0bd2d9e4a81956ee84deda4aae1cc8bd9f2a7
evidence/01      09382fd873f8313e9d0dfb8202e86b969a413e3b3fb3374c2c8340a86394f99d
evidence/02      2b24ce86ef04bb9e3806125cb3842db9cbe84a390ec66beccbccd022e10a9c82
evidence/03      2fe3e508a93ee3e5eb6f1d5fb87683c0c90f34bef1568dfe2ae107c7d971cf12
```

Some combined reads were truncated; the design was completed in a subsequent read and relied-on citations used visible ranges. Discovery against guessed dNh `models`, `contracts`, plural `normalizers`, ingest-local `idempotency`, and a worker search against `workers` produced missing-path errors. Correct paths were subsequently read; those errors do not establish repository-wide absence. Two worker reads used the wrong repository cwd and were corrected. Two `docs.rs` source URLs failed to open; no finding relies on them.

## 7.3 Validation performed

- **PASS:** Static trace and citation review across all fifteen areas; prescribed artifact structure and finding/research cross-references reviewed; final output counts and scope checked.
- **FAIL:** Design completeness/consistency for implementation approval, for the cited blocker/high findings. This is a design verdict, not a failing executed test suite.
- **NOT_RUN:** Tests, lint/type checks, coverage, package builds/installs, uv sync, benchmarks, source/database imports, SQLite capability checks, model calls, real-data PII evaluation and export/restore exercises. The audit wrapper forbids these operations.
- **UNKNOWN:** Actual deployed library/model versions, account capabilities, machine capacity, extension availability, personal-source schemas, real typedstream coverage, current CI status and measured performance.

Final readback found 30 findings, all 15 area subsections, and 50 uniquely identified research targets with the required eight columns. The placeholder search returned no matches (the expected `rg` exit 1). Input hashes matched their initial values; both git status listings retained the same pre-existing changes, and tracked product-path diff checks were empty.

## 7.4 Unverified impressions

No uncited impression is promoted to a finding. No ranking of detector/model quality on the owner's chats, actual telemetry behavior of the future dependency set, local compromise, cloud leakage incident, database corruption incident, or legal admissibility is established. Such claims require new evidence.

## 7.5 Completion record

**Change Summary:** Two audit deliverables only; no design or implementation repair. **Authority Used:** latest access/output wrapper, full master brief and applicable repository instructions. **Analysis Performed:** static extraction/contract/security/storage/phase trace, delegated bounded reviews, primary-source currency check and supervisor challenge.

**Remaining Uncertainty / Risk:** Runtime and real-data qualification remain outstanding. **Files Touched:** `out/report-codex.md` and `out/research-targets-codex.md` only. **Git State:** Both repositories began dirty; no staging, commit, branch change or cleanup was performed. Audit outputs are inside the existing untracked audit tree. **Rollback Plan:** Remove only these two new output files if the audit is withdrawn; no product rollback is needed. **Requested Next Step:** Resolve F09/F10 and the P0/P1 identity/acquisition contracts, then commission the P0 research targets before approving implementation. No deployment, merge or product acceptance is granted.
