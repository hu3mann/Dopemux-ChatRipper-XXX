# 0. Reviewer identity

| Field | Disclosure |
|---|---|
| Auditor | **chatgpt-web** |
| Model / runner | **GPT-6 Astra Pro**, as identified by this session; ChatGPT with workspace tools. Three parallel reviewers contributed static source analysis, reconciled by the primary reviewer. |
| Training knowledge cutoff | **UNKNOWN: an exact cutoff date is not exposed in this session.** No cutoff date has been invented. Version-sensitive conclusions use the dated primary-source research in §3.15. |
| Review date | 2026-10-20. |
| Approximate time spent | About **53 minutes elapsed**, from 2026-10-20 18:44 UTC to document finalization around 19:37 UTC, including three parallel static reviews, reconciliation, research, drafting, and document checks. No runtime verification was performed. |
| Project evidence | Only `chatx-design-audit-pack-2026-10-20.zip`: both prompts, the complete design, all three prior-review documents as leads, and source blocks in both bundles. |
| Input archive SHA-256 | `d5a733397ab872aa3595b3889319a2a774fc9413627b923999d2a97848924bb2` (computed over the supplied ZIP; identifies these bytes, not repository authenticity). |
| Bundle identity | `source-bundle-chatx.md` declares commit `9c3dd6b`, branch `governance-doctrine-integration`; `source-bundle-dnh.md` declares commit `39c75bde`, branch `migrate-cheaperinference`. These are bundle assertions, not independently authenticated checkouts. Both declare generation at 2026-10-20T18:09:56Z. |
| Reading coverage | Both bundle inventories and all source-block boundaries were inspected; the ChatX inventory was read completely, the much larger dNh inventory selectively and through targeted searches. The exact full-file and excerpt reading ledger is in §7. Not every fenced source block was read completely. |
| Execution and access limits | No project code, tests, builds, probes, databases, model calls, or installations were executed. No project information outside the ZIP was accessed. Web research was limited to scope item 15. |

# ChatX rearchitecture audit — Output A

## Interpretation of evidence and severity

`CONFIRMED` means a cited source statement, code path, or design omission was directly inspected. It does **not** mean a defect was reproduced, an exploit occurred, a test failed, or a deployed configuration was observed. `PLAUSIBLE` identifies a reasoned consequence; `UNKNOWN` identifies evidence unavailable in the pack. Severity describes the consequence if the cited gap reaches the relevant phase. A cloud blocker need not prevent local extraction work.

All `§x.y` citations refer to the design under audit unless explicitly prefixed “Report.” Source line 1 is the first line inside its fenced block. Some bundle headings undercount the visible block by one line; citations follow the actual block, including its final line. Inventoried but unbundled files establish existence only. The inventories themselves say tooling directories were removed, so they do not justify unrestricted repository-wide absence claims.

**Length note:** this report exceeds the brief's indicative word range to retain the field-by-field audit, cited counterexamples, uncertainty qualifications, and complete verification ledger.

## 1. Executive summary

1. **Keep the architectural direction, but do not freeze the canonical contract or authorize cloud activation from this design as written.** Five blockers concern acquisition consistency, historical time, dNh event compatibility, exact-payload authorization, and the meaning of the privacy evaluation gate. These are contract defects that precede implementation polish.
2. **The retained acquisition is not established to be WAL safe.** ChatX separately copies the database, WAL, and SHM without snapshot coordination. Read-only opening and later hashes cannot establish that those copies represent one coherent source state. Actual corruption or loss was not demonstrated. [F01]
3. **The temporal contract cannot represent all intended sources truthfully.** Mandatory aware UTC conflicts with timezone-unknown WhatsApp imports; current iMessage heuristics can choose a plausible wrong epoch/unit; PDF invents current timestamps. Extraction time must never masquerade as historical send time. [F02]
4. **The dNh adapter is not a field-renaming exercise.** Its proposed inbound envelope rejects outbound attachment-only messages. Text recovery also requires historical reconciliation beyond the existing cursor lookback, plus a policy for existing event IDs and changed dedupe hashes. [F03, F14]
5. **A case/run gate token is insufficient without binding to the final outbound bytes and destination.** Raw questions, context, embeddings, metadata, retries, and later payload mutation must be covered. A service named “local” does not establish local inference. [F04]
6. **The stated recall target currently has no complete eligibility rule.** Optional real labels, undefined required class coverage, and an uncalibrated sampled model opinion do not establish real-case recall. Coarse labels separately disclose intimate attributes even when direct identifiers are removed. [F05, F16, F18]
7. **Several “minimal change” ports need substantial correction.** Verified examples include ordinary WhatsApp messages dropped by substring matching, backup/live source confusion, unstable 32-bit chunk IDs, content-insensitive chunk hashes, and lost citation identifiers. [F08, F10–F13, F27]
8. **SQLite, FTS5, and disk CAS remain reasonable owner choices.** Their acceptance needs generation consistency, crash recovery, verified restore, embedding-space identity, and measured capacity. One million 1024-dimensional float32 vectors alone represent 4.096 GB of values; this is arithmetic, not measured RSS or a reason to mandate a server. [F24–F26]
9. **Provider interchangeability must describe capabilities and failures.** Current official documentation confirms the configured Claude 5.5 IDs, but also material structured-output and request-control differences. A common successful-return type cannot represent all supported outcomes or embedding availability. [F19–F21, F38]
10. **Relationship analysis needs a different evidentiary standard from rule conversion.** The existing mapper can turn one label into a saturated “gaslighting” score without actor attribution or causal evidence. Opt-in and YAML do not validate that inference. [F28]
11. **The build/release and phase evidence are incomplete.** Editable sibling paths do not identify immutable core source; installed resource lookup is already fragile; actual workflow bodies and lockfiles are absent; P3/P4 and P4/P5 contain unresolved dependencies. [F29–F33]
12. **Two inherited audit claims require correction.** Optional redaction preflight can exit nonzero, and multi-vector search has CLI call sites. Neither proves a functioning safe pipeline. This report preserves the distinction between reachability, static defects, and unknown runtime behavior. [F15, F35]

## 2. Findings table

Recommendations below are changes to requirements or bounded verification work, not a replacement architecture. “Cost” is a conditional consequence, not an observed incident.

| ID | Severity (BLOCKER/HIGH/MEDIUM/LOW/INFO) | Area | Finding | Evidence | Verdict | Recommended change | Cost of ignoring |
|---|---|---|---|---|---|---|---|
| F01 | BLOCKER | 2, 4 | “WAL-safe” acquisition is unsupported by sequential file copies. | `chatx:src/chatx/imessage/db.py:25–43`, `chatx:src/chatx/imessage/db.py:58–64`; §3.13, §8 | CONFIRMED | Specify a consistent acquisition protocol and independently verify its snapshot. | Incoherent evidence can become the foundation of every later result. |
| F02 | BLOCKER | 1, 2 | Mandatory UTC has no representation for unresolved source time; retained paths also fabricate or misinterpret dates. | §3.4, §10 V6; `chatx:src/chatx/imessage/time.py:27–64`; `chatx:src/chatx/pdf_ingest/reader.py:60–103` | CONFIRMED | Preserve raw time, uncertainty, precision, assumptions, and ordinal order; prohibit substitution with `now()`. | False chronology, unstable IDs, invalid imports. |
| F03 | BLOCKER | 1, 9 | §9's universal inbound mapping conflicts with dNh attachment-only validation. | §9; `dnh:src/dnh_crm/events.py:2007–2015` | CONFIRMED | Approve a platform × direction × content-kind mapping and explicit loss policy. | Valid canonical records are rejected or assigned false event semantics. |
| F04 | BLOCKER | 3, 11 | Gate authorization is not specified for exact serialized payload, operation, destination, or subsequent mutation. | §3.6–3.7, §5, contract 4; `chatx:src/chatx/redaction/policy_shield.py:226–248` | CONFIRMED | Bind authorization to a final allowlisted payload and enforce it at transport on every attempt. Define local trust. | Raw content can bypass a passing case/run gate. |
| F05 | BLOCKER | 3, 10 | Real-data eligibility and required class coverage are unresolved while P3 permits synthetic-only exit. | §3.7, §6 P3, §10 V3, §12, question 3 | CONFIRMED | Define independent required classes/languages, support counts, uncertainty, and whether missing real evaluation forbids cloud. | Synthetic accuracy is presented as applicable privacy assurance. |
| F06 | HIGH | 1 | Message identity, source observation, revision, input hash, and raw evidence integrity are conflated. | §3.4, §9; `dnh:src/dnh_crm/ingest/whatsapp_export.py:165–174` | CONFIRMED | Separate these identities and specify canonical bytes, namespaces, duplicate occurrences, and migration aliases. | Legitimate duplicates disappear or repeat imports become new evidence. |
| F07 | HIGH | 1 | Lifecycle, group membership, raw service/account, related-event identity, and unsupported payload preservation are not complete contracts. | §3.4–3.5; `chatx:src/chatx/imessage/extract.py:88–107`, `chatx:src/chatx/imessage/extract.py:227–259` | CONFIRMED | Add required source-bound preservation and explicit unknown/unresolved states. | Edits, removals, membership, and unsupported content silently lose meaning. |
| F08 | HIGH | 6, 7 | Kept chunker uses run-dependent 32-bit IDs and hashes IDs/time without text; group and multiline reconstruction also need work. | `chatx:src/chatx/transformers/chunker.py:113–122`, `chatx:src/chatx/transformers/chunker.py:150–168`; `chatx:src/chatx/enrichment/enricher.py:290–326` | CONFIRMED | Bind stable chunk IDs to ordered revisions and config; carry structured message associations. | Stale caches, duplicate indexing, collisions, wrong attribution. |
| F09 | HIGH | 2, 12 | The bounded two-layout decoder and synthetic prefix tests do not establish complete real-blob recovery. | `dnh:src/dnh_crm/ingest/imessage_attributed_body.py:168–272`; `dnh:tests/unit/test_imessage_attributed_body.py:30–37`, `dnh:tests/unit/test_imessage_attributed_body.py:59–144`; §10 V2 | CONFIRMED | State partial guarantees; preserve bytes/status; evaluate full blobs and correct the four-byte-length test. | A narrow parser is mistaken for comprehensive evidence recovery. |
| F10 | HIGH | 2, 11 | Contact scope and backup source context differ across extraction, reports, attachment copying, and manifest lifetime. | `chatx:src/chatx/imessage/report.py:76–98`; `chatx:src/chatx/imessage/extract.py:282–286`, `chatx:src/chatx/imessage/extract.py:372–389`; `chatx:src/chatx/cli/main.py:1201–1204`, `chatx:src/chatx/cli/main.py:1301–1308` | CONFIRMED | Use one resolved scope and durable acquisition context throughout. | Unrelated chats/files or live data enter a backup/contact report. |
| F11 | HIGH | 2, 4 | CAS inputs are resolved permissively; hashing precedes a separate copy; existing objects and copy failures are not verified. | `chatx:src/chatx/imessage/attachments.py:90–126`, `chatx:src/chatx/imessage/attachments.py:241–269`; `chatx:src/chatx/imessage/backup.py:129–147` | CONFIRMED | Bound paths, hash staged bytes, verify existing objects, publish atomically, reconcile crashes. | Digest names can misdescribe bytes; unrelated or missing media becomes evidence. |
| F12 | HIGH | 2 | WhatsApp drops ordinary bodies containing broad system markers and loses genuine system/deletion events. | `dnh:src/dnh_crm/ingest/whatsapp_export.py:33–49`, `dnh:src/dnh_crm/ingest/whatsapp_export.py:93–108`, `dnh:src/dnh_crm/ingest/whatsapp_export.py:196–198` | CONFIRMED | Parse source dialects structurally and preserve every record disposition. | Silent loss biases search and relationship analysis. |
| F13 | HIGH | 1, 2 | Instagram, email, and PDF ports do not yet preserve the source identities, times, attachments, and locators promised by v2. | `chatx:src/chatx/instagram/extract.py:64–118`; `dnh:src/dnh_crm/ingest/email_eml.py:107–180`, `dnh:src/dnh_crm/ingest/email_eml.py:256–283`; `chatx:src/chatx/pdf_ingest/reader.py:118–133` | CONFIRMED | Define adapter-specific fidelity contracts and preserve original artifacts/locations. | Unsupported fields disappear; citations cannot recover source evidence. |
| F14 | HIGH | 1, 9, 10 | Wiring the decoder does not backfill records behind dNh's bounded lookback or resolve changed dedupe/event identity. | `dnh:src/dnh_crm/services/ingest_runner.py:85–118`, `dnh:src/dnh_crm/services/ingest_runner.py:133–190`; `dnh:src/dnh_crm/store/migrations.py:5–24`; §9 | CONFIRMED | Make historical reconciliation an explicit migration with replay/conflict tests. | Advertised recovered history remains missing or conflicts with existing events. |
| F15 | HIGH | 3 | Hard-fail definitions are demonstrative; exception handling skips chunks before setting the hard-fail report flag. | `chatx:src/chatx/redaction/patterns.py:159–197`; `chatx:src/chatx/redaction/policy_shield.py:180–205`, `chatx:src/chatx/redaction/policy_shield.py:258–278`; §3.7 | CONFIRMED | Version executable policy; stop the selected run on failure or uncertainty; retain local evidence. | Quiet omissions and inconsistent refusal decisions. |
| F16 | HIGH | 3 | Seeded second-opinion sampling has no stated estimand, sample size, calibrated sensitivity, or uncertainty outcome. | §3.7 condition 3, §6 P3 | CONFIRMED | Specify statistical meaning, selection, calibration, and fail-closed operational outcomes. | Zero detected leaks is mistaken for proof of low leakage. |
| F17 | HIGH | 3, 11 | Token notation, HMAC key lifecycle, rehydration authorization, and case/map protection remain underspecified. | §3.7; `chatx:src/chatx/identity/normalize.py:47–95`; `chatx:src/chatx/redaction/patterns.py:200–249` | CONFIRMED | Define one versioned security contract, exact encoding, secure creation, recovery, and substitution limits. | Collisions, cross-case substitution, lost keys, or disclosure from local replicas. |
| F18 | HIGH | 3, 6 | Coarse “cloud-safe” labels disclose intimate attributes; direct-identifier removal is not a disclosure policy. | `chatx:config/labels.yml:4–13`, `chatx:config/labels.yml:191–253`, `chatx:config/labels.yml:403–410`; §3.7–3.9 | CONFIRMED | Approve category visibility independently; compile separate cloud/local projections and test linkage risk. | Sensitive attributes accumulate across pseudonymous calls. |
| F19 | HIGH | 5 | Provider interface models successful parsing, not capabilities, refusal, truncation, or unavailable embedding. | §3.6, §3.10; Report §3.15 official sources | CONFIRMED | Specify capabilities and typed terminal outcomes; select embedding independently. | False interchangeability, invalid requests, or unsafe fallback. |
| F20 | HIGH | 5, 6 | Retry count for invalid JSON does not bound total time, concurrency, usage, or spend. | §3.6, §3.9; `chatx:src/chatx/enrichment/ollama_client.py:176–210`, `chatx:src/chatx/enrichment/ollama_client.py:263–331` | CONFIRMED | Define per-attempt accounting, deadlines, cancellation, limits, backoff, budget, and resume. | Hangs, repeat charges, overload, and costly full reruns. |
| F21 | HIGH | 5, 6 | Provider identity and cache keys omit a complete immutable per-call effective configuration. | §3.6, §3.9, §5, contract 5; `chatx:src/chatx/enrichment/ollama_client.py:229–232`, `chatx:src/chatx/enrichment/ollama_client.py:361–366` | CONFIRMED | Persist per-call identity/parameters and hash all relevant context, taxonomy, preprocessing, and model artifacts. | Stale results or outputs attributed to the wrong effective model. |
| F22 | HIGH | 6 | Taxonomy loader shape disagrees with YAML; the retained “hysteresis” is stateless and confidence is uncalibrated. | `chatx:src/chatx/enrichment/multi_pass_pipeline.py:93–145`; `chatx:config/labels.yml:8–23`, `chatx:config/labels.yml:307–310`; `chatx:src/chatx/enrichment/enricher.py:149–179`; §3.9 | CONFIRMED | Compile and validate taxonomy semantics; define state or rename the gate; evaluate labels and abstention. | Valid-looking empty/wrong labels and arbitrary certainty. |
| F23 | HIGH | 3, 6, 7 | Schema validity does not address instructions embedded in chat evidence. | `chatx:src/chatx/enrichment/ollama_client.py:234–261`, `chatx:src/chatx/enrichment/ollama_client.py:277–279`; §3.7, §3.9–3.11 | CONFIRMED | Isolate untrusted evidence, constrain model authority, and test schema-valid adversarial outputs. | Privacy judgments, labels, and citations can be manipulated. |
| F24 | HIGH | 4 | Store outline lacks transactional and generation invariants for import, edits, indexes, resume, repair, and migrations. | §3.5, §4, §6 P2/P5 | CONFIRMED | Define coherent generations, foreign keys, run states, invalidation, and repair/restore obligations. | Successful-looking partial or stale cases. |
| F25 | HIGH | 4, 7 | Fixed-dimension dNh schema does not validate multiple embedding spaces or million-chunk capacity. | `dnh:src/dnh_crm/store/migrations.py:181–238`, `dnh:src/dnh_crm/store/migrations.py:327–336`, `dnh:src/dnh_crm/store/migrations.py:375–380`; §10 V4 | CONFIRMED | Define immutable spaces and migration lifecycle; benchmark the chosen workload and runtime. | Mixed vector semantics, exhausted disk, unpredictable queries. |
| F26 | HIGH | 4 | Hash manifest alone does not establish completeness, authenticity, acquisition history, or independent custody. | §1, §3.4–3.5, §3.10 | CONFIRMED | Narrow the forensic claim; preserve source lineage; specify export/restore and any external attestation. | Self-consistent bundles overstate what their hashes prove. |
| F27 | HIGH | 7 | Existing index drops message IDs; proposed RRF/citations lack evidence-span and evaluation contracts. | `chatx:src/chatx/indexing/vector_store.py:170–195`, `chatx:src/chatx/indexing/vector_store.py:329–335`; §3.10, §6 P5 | CONFIRMED | Preserve revision/span links; define filtered fusion, relevance judgments, and claim-support validation. | Answers reference absent, wrong, or unsupported evidence. |
| F28 | HIGH | 8 | Relationship rules produce certainty-shaped claims without actor, causal, or construct validation. | `chatx:src/chatx/storage/psychology_relationship_mapper.py:51–101`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:343–347`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:548–570`; §3.11 | CONFIRMED | Treat rules as hypotheses; require attribution, counterevidence, abstention, and evaluated human review. | Unsupported sensitive conclusions appear evidence-grade. |
| F29 | HIGH | 9 | External editable source plus two locks lacks an immutable consumer/release contract. | §3.2–3.3, §5, contract 1, §9, §10 V8 | CONFIRMED | Keep dev layout; record immutable source pairs or release artifacts and consumer compatibility. | Same dNh revision can run different core source. |
| F30 | HIGH | 9, 12 | Runtime schemas rely on checkout paths; missing report schema can validate by absence. | `chatx:pyproject.toml:121–130`; `chatx:src/chatx/schemas/validator.py:13–36`; `chatx:src/chatx/utils/run_report.py:89–95` | CONFIRMED | Package runtime resources and test a clean installed wheel outside the checkout. | Editable tests pass while installed validation disappears. |
| F31 | HIGH | 11 | “No secrets in logs” does not define all sensitive replicas or local attacker/sync/backup boundaries. | §3.5, §3.13; `chatx:src/chatx/enrichment/ollama_client.py:305–312`, `chatx:src/chatx/enrichment/ollama_client.py:385–392` | CONFIRMED | Use allowlisted diagnostics, protected quarantine, case permissions, retention, and an explicit operational threat model. | Raw or inferred sensitive content escapes case protections. |
| F32 | HIGH | 10 | Phase gates postpone decisive uncertainty and contain P3/P4 and P4/P5 dependencies. | §6, §7, §10 | CONFIRMED | Run bounded risk spikes early and make each gate independently satisfiable and measurable. | Expensive work precedes discovery of architectural infeasibility. |
| F33 | HIGH | 12 | Coverage exclusions are real; actual CI execution and semantic safety gates are not evidenced. | `chatx:pyproject.toml:187–207`; `chatx:config/arch-gates.yml:23–35`, `chatx:config/arch-gates.yml:43–48`; §5, contract 6, §7 | CONFIRMED | Require actual workflow evidence, installed artifacts, failure-path contracts, and corpus-level evaluation. | A nominal coverage percentage hides critical gaps. |
| F34 | MEDIUM | 13 | User contracts for resume, partial success, deletion, portability, and CLI error/status semantics are missing. | §3.5, §3.12, §4, §7 | CONFIRMED | Add acceptance-level behavior and disposition accounting. | Users cannot tell what completed, recover safely, or remove derived data coherently. |
| F35 | MEDIUM | 14 | Several inherited “dead/advisory/real” grades overstate what is verified; silent scope drops need disposition. | §2, §3.12–3.14, §8, Appendix A; `chatx:src/chatx/cli/main.py:336–350`, `chatx:src/chatx/cli/main.py:780–796`, `chatx:src/chatx/cli/main.py:861–882` | CONFIRMED | Correct reachability claims and explicitly accept/defer/drop the listed intents. | Builders preserve defects or remove capabilities for false reasons. |
| F36 | MEDIUM | 9, 11 | Shared-core ownership/license and dependency/model artifact provenance are not settled. | `chatx:pyproject.toml:10`; `dnh:pyproject.toml:7`; §3.3, §8 | CONFIRMED | Confirm owner authority/license; preserve notices and pin executable dependency/model artifacts. | Avoidable release rework or unreviewed code accesses private cases. |
| F37 | HIGH | 4, 15 | No supported SQLite runtime/fix baseline is specified for the case store. | §3.3, §3.5, §11; Report §3.15, SQLite WAL documentation | CONFIRMED | Verify linked runtime and relevant fixes, including the documented WAL-reset fix, before concurrency acceptance. | An avoidable upstream defect remains in the durability boundary; current exposure is UNKNOWN. |
| F38 | MEDIUM | 5, 9, 15 | Current model, server, framework, and standard capabilities require a dated conformance baseline. | §3.3, §3.6–3.7, §3.12; Report §3.15 | CONFIRMED | Pin tested combinations and refresh capability evidence; retain UNKNOWN for installed/observed versions. | Builders implement against obsolete or mismatched API assumptions. |

## 3. Per-area deep dives

### 3.1 Scope 1 — Canonical schema v2

**Assessment: incomplete for its stated evidence-preservation and interoperability role. [F02, F03, F06, F07, F13, F14]**

#### Field coverage and uncertainty

No real database, complete versioned Apple schema dump, or source export is supplied. The following is a contract audit against the fields named in the brief, not a claim that every field exists with identical semantics on every supported OS. The inspected ChatX query reads a small subset; the dNh source row is smaller. Edits and fuller system events are therefore new extraction work. Evidence: `chatx:src/chatx/imessage/extract.py:88–107`; `dnh:src/dnh_crm/ingest/imessage_source.py:24–52`, `dnh:src/dnh_crm/ingest/imessage_source.py:182–197`; §3.4.

| Source concern | Proposed representation | Requirement still missing |
|---|---|---|
| `handle_id`, `is_from_me` | Normalized sender and direction | Raw handle row/value, source account, unknown-value handling, and self-identity scope. “Me” is not one universal account. |
| `date` | Required UTC `sent_at`, optional `source_tz` | Raw value, unit/epoch, precision, conversion evidence, ambiguity, and unresolved time. |
| `date_read`, `date_delivered` | No named fields | Typed status observations or required raw preservation; absent must not mean unread/undelivered. |
| `date_edited`, `date_retracted` | Partial edit time, unsent Boolean, prior texts | Per-version and retraction times, raw values, source links, and unknown versus no history. |
| `associated_message_guid`, `associated_message_type` | Folded reaction/reply state | Related event's own identity, raw code/target, target part, action, order, and unresolved disposition. |
| `thread_originator_guid` | Explicit originator field | Distinguish root from immediate parent and preserve references outside the loaded subset. |
| `balloon_bundle_id`, `expressive_send_style_id` | No named fields | Preserve app/extension and expressive metadata even if not initially interpreted. |
| `item_type`, `group_action_type` | Broad system kind | Specific action, actor, affected participants, time, and raw values. |
| `cache_has_attachments` | No named field | Source's attachment claim independently of successful joins, permissions, or file resolution. |
| `service`, `account` | Platform partly covers service | Preserve raw transport/account and define mapping; current ChatX emits iMessage even when recording another service in metadata. |
| Groups and membership | A participants table is listed | A source-level conversation/membership contract, including silent participants and changes; sender-only messages cannot reconstruct all membership. |
| Stickers, previews, locations, app cards | Broad attachments/text kinds | Body-part/payload associations or mandatory raw capture with unsupported-content status. |
| Audio, OCR, transcription | Attachment plus `text_source` | Derived artifacts with original-byte parent, segment/page offsets, model identity, and independent revision; avoid overwriting the original body. |

Required UTC and timezone-unknown WhatsApp cannot both produce a valid canonical record without an additional rule (§3.4, V6). Either allow a typed unresolved source-time state or refuse canonicalization until the owner supplies a zone. Preserve ambiguous day/month order, daylight-saving ambiguity/nonexistence, and precision. An explicit `--assume-tz` must record an assumption, not retroactively establish fact. PDF can supply ordinal order without knowing send time. Source-observation time and extraction time must remain different fields.

#### Identity, hashing, and preservation

The native-GUID preference is an improvement over ChatX's `msg_<ROWID>` (`chatx:src/chatx/imessage/extract.py:183–198`). However, four identities need separate meanings: an observation in an acquired source, a logical message across sources, a revision/related event, and the exact processing input. Platform/account namespaces and source lineage must be explicit.

The fallback hash has a deterministic ambiguity before cryptography matters: two identical “OK” messages from one sender in a minute-resolution export have identical proposed inputs. So can two attachment-only records. Longer digests cannot distinguish identical preimages. Conversely, correcting text, timezone, or sender normalization can change that tuple for the same source observation. Existing WhatsApp IDs also depend on the export filename, so renaming it changes identity (`dnh:src/dnh_crm/ingest/whatsapp_export.py:165–174`).

The proposed `content_hash` apparently includes pseudonyms, display names, attachment paths/availability, reactions, and edit state, while excluding all provenance and `source_meta` (§3.4). It therefore has neither a defined immutable-source meaning nor a defined revision/dedupe meaning. Specify canonical serialization, normalization, list ordering, timestamp encoding, algorithm version, and which changes invalidate which hash. Frozen models with list/dict members also need a stated nested-mutation policy; a v2 runtime defect cannot be asserted before implementation.

Optional, unhashed metadata is insufficient for raw preservation. ChatX retains attributed bytes only in a particular fallback path; Instagram stores keys without values (`chatx:src/chatx/imessage/extract.py:159–172`, `chatx:src/chatx/imessage/extract.py:206–209`; `chatx:src/chatx/instagram/extract.py:117–118`). Require each observation to bind to an integrity-checked original artifact and locator: database table/row, ZIP member/object position, MIME part, or PDF page/span. A normalized-content hash cannot replace that binding.

#### Events and dNh loss

ChatX collects reaction GUIDs/rows but drops their identity during folding; unmatched targets disappear. Replies outside the loaded GUID set become unresolved without retained links (`chatx:src/chatx/imessage/extract.py:139–149`, `chatx:src/chatx/imessage/extract.py:227–259`). The reaction helper itself is unbundled: its exact 3000-series behavior is **UNKNOWN**. Adding `removed` helps, but the contract must distinguish event history from effective reaction state, including remove/re-add and unknown codes. An empty `prior_texts` must not equate unavailable history with no edits.

| Canonical case | §9 mapping consequence under inspected dNh schema |
|---|---|
| Inbound iMessage text | A compatible starting subset; fidelity still needs explicit field mapping. |
| Outbound text | May validate as ordinary payload while still carrying the wrong inbound event type. |
| Outbound attachment-only | Rejected: the special validator requires inbound event type, iMessage, inbound direction, and client actor. |
| Reactions, replies, edits, system events | Lossless preservation is not specified; allowing fields to be ignored does not establish a lossless adapter. |
| Instagram/PDF/TXT | dNh's channel vocabulary does not establish these mappings. Declare a supported subset or an approved extension. |

Evidence: `dnh:src/dnh_crm/events.py:172–193`, `dnh:src/dnh_crm/events.py:484–488`, `dnh:src/dnh_crm/events.py:519–530`, `dnh:src/dnh_crm/events.py:2007–2015`; §9. Ordinary external/payload models allow extras, so a deliberate canonical-data extension may be possible; the narrow attachment payload has different rules. A separate media-event payload also exists (`dnh:src/dnh_crm/events.py:806–827`). These are candidate seams, not proof that no dNh changes are needed. The shown `conversation_contacts` table maps each conversation to one contact; normalized senders alone do not establish group integration (`dnh:src/dnh_crm/store/migrations.py:52–71`). Other projection/service behavior is unbundled. Version the Python API, canonical serialization, and adapter semantics separately; preserve old-ID aliases and explain intentional losses.

### 3.2 Scope 2 — Extraction correctness

**Assessment: complementary implementations justify the shared core; neither repository supplies a complete extractor ready for minimal-change adoption. [F01, F02, F09–F14]**

| Concern | Better starting point | What is actually supported by the pack |
|---|---|---|
| Typedstream text | dNh | Bounded structural parser, two paired layouts, strict decoding, explicit statuses. It does not validate the entire archive or recover all attributes. |
| Timestamp failure behavior | dNh, cautiously | Rejects when no plausible date exists; both unit/epoch heuristics remain ambiguous. |
| Live acquisition | Neither for the stated guarantee | ChatX stages non-atomically; dNh reads live SQLite without a preserved acquisition and without one explicit transaction spanning all source queries. |
| Backup Manifest/staging | ChatX | Real lookup/staging code; argument, source-context, path-validation, and layout limitations remain. |
| Related events/outbound | ChatX | Collection/folding and self handling exist; raw events, unknown targets, removals, and account semantics need work. |
| Group identity | No verified winner | ChatX joins chats; dNh delegates to an unbundled thread resolver. Neither shown contract establishes complete membership history. |
| Attachments/CAS starting machinery | ChatX | Metadata, MIME/UTI/HEIC classification, and hashing/copy hooks exist; actual HEIC decoding and helper bodies are unbundled. |
| Native IDs | dNh | Prefers GUID; source-scoped fallback and cross-import migration still required. |
| Dedupe technique | dNh as a pattern | Dedicated canonical-hash helper; its called serializer is unbundled, and current hash inputs are not universal message identity. |
| Unsupported/empty body states | dNh decoder | Useful statuses; production source/mapper still disagree about null text with attachments. |

Evidence: `dnh:src/dnh_crm/ingest/imessage_attributed_body.py:69–80`, `dnh:src/dnh_crm/ingest/imessage_attributed_body.py:168–272`; `dnh:src/dnh_crm/ingest/imessage_source.py:55–69`, `dnh:src/dnh_crm/ingest/imessage_source.py:199–218`; `dnh:src/dnh_crm/ingest/imessage_mapper.py:14–19`, `dnh:src/dnh_crm/ingest/imessage_mapper.py:38–72`; `dnh:src/dnh_crm/idempotency.py:7–16`; `chatx:src/chatx/imessage/attachments.py:13–21`, `chatx:src/chatx/imessage/attachments.py:148–214`.

**Time counterexamples are derivable without execution.** ChatX treats `700_000_000_000_000` Apple microseconds as nanoseconds because it is divisible by a billion, obtaining roughly eight days into 2001. Its 1999 lower bound accepts that wrong interpretation. Raising the bound alone does not repair downstream fallback to current time. dNh tries Apple candidates before Unix candidates; Unix seconds `1_700_000_000` also produce a plausible Apple-seconds date, so first-plausible is not proof of epoch. Preserve exact raw values and source-informed conversion evidence. See `chatx:src/chatx/imessage/time.py:16–17`, `chatx:src/chatx/imessage/time.py:27–64`; `chatx:src/chatx/imessage/extract.py:179–187`; `dnh:src/dnh_crm/ingest/imessage_mapper.py:41–56`.

**Snapshot consistency is a release blocker for forensic acquisition.** The main file, WAL, and SHM are copied at different times with no barrier (`chatx:src/chatx/imessage/db.py:25–43`). A concurrent write/checkpoint can intervene. The subsequent immutable open does not create retrospective consistency. This is not a claim that immutable mode always ignores WAL, nor that an observed acquisition was corrupt. Specify a coherent working snapshot, preserve its relationship to acquired originals, and test active-writer/checkpoint races with an independent reference. Relevant current SQLite guidance is evaluated only in Report §3.15.

**Backup and scope defects require a shared source context.** The conversation selector includes every chat in which the user sent any message; extraction then reads each whole selected chat, including unrelated inbound content. The missing-attachment report has its own broad filter; unresolved contacts can leave it unfiltered (`chatx:src/chatx/imessage/extract.py:372–389`, `chatx:src/chatx/imessage/extract.py:407–450`; `chatx:src/chatx/imessage/report.py:76–98`). Resolve conversation membership once and reuse it. During backup import, extraction omits `backup_dir` when calling attachment copying, missing reporting opens the live `db` option, provenance names an expiring stage path, and manifest generation follows stage cleanup (`chatx:src/chatx/imessage/extract.py:195–198`, `chatx:src/chatx/imessage/extract.py:282–286`; `chatx:src/chatx/cli/main.py:1115–1127`, `chatx:src/chatx/cli/main.py:1201–1204`, `chatx:src/chatx/cli/main.py:1301–1308`). The manifest helper is absent, so its eventual behavior is UNKNOWN.

Manifest resolution shown is sharded; flat layouts, completed-backup guarantees, and additional schemas are not established. File IDs and relative paths require validation. Backup evidence must never silently resolve to a similarly named live file. The password flag checks presence without implementing decryption, so removal is correct (`chatx:src/chatx/imessage/backup.py:91–147`, `chatx:src/chatx/imessage/backup.py:178–189`).

**CAS needs byte-level and filesystem invariants.** The source is hashed and then copied separately; existing destinations are trusted and exceptions swallowed (`chatx:src/chatx/imessage/attachments.py:241–269`). Stage within a controlled root, hash the bytes being stored, verify existing objects, publish atomically, and commit references with recoverable ordering. Distinguish missing, unreadable, changed, corrupt, unsupported, and excluded. Preserve original HEIC/audio/image bytes independently of derivatives; the pack proves HEIC classification, not tested rendering/orientation/color fidelity.

**Other formats need explicit fidelity contracts.**

- **WhatsApp:** broad markers such as `left`, `added`, and `joined` classify ordinary authored text as system content and drop it. True membership/deletion records also disappear. Only enumerated prefix/date formats are handled; missing zones become UTC; all events are inbound/client; name slugging does not prove person identity. Preserve dialect, raw text/time, system events, media-omitted state, and self-identity uncertainty. Evidence: `dnh:src/dnh_crm/ingest/whatsapp_export.py:24–49`, `dnh:src/dnh_crm/ingest/whatsapp_export.py:93–149`, `dnh:src/dnh_crm/ingest/whatsapp_export.py:177–244`.
- **Instagram:** IDs depend on per-file array position, source-member identity is insufficient, absent message time becomes epoch zero, and absent reaction time becomes message time. Only selected media references survive; `raw_keys` discards unknown values. Preserve ZIP/member/object identity, raw content, missing-time status, media bytes, and bounded archive limits. Any mojibake repair must retain originals and avoid altering valid multilingual text. Evidence: `chatx:src/chatx/instagram/extract.py:20–40`, `chatx:src/chatx/instagram/extract.py:64–118`, `chatx:src/chatx/instagram/extract.py:150–174`.
- **Email:** useful plain/HTML normalization does not preserve recipients, full threading/MIME provenance, attachment bytes, or an always-present raw-file digest. Duplicate Message-ID with different bytes needs conflict handling. Missing-zone assumptions and bodyless attachment mail require explicit behavior. Evidence: `dnh:src/dnh_crm/ingest/email_eml.py:107–132`, `dnh:src/dnh_crm/ingest/email_eml.py:139–212`, `dnh:src/dnh_crm/ingest/email_eml.py:256–297`.
- **PDF:** nonempty lines become messages, colon prefixes become senders, current times are incremented by seconds, platform is iMessage, and page boundaries are flattened. Preserve transcript-specific parsing status, unknown time/sender, ordinal order, and source page/spans. Silent reader exceptions must not become a successful empty import. Evidence: `chatx:src/chatx/pdf_ingest/reader.py:26–57`, `chatx:src/chatx/pdf_ingest/reader.py:60–103`, `chatx:src/chatx/pdf_ingest/reader.py:118–133`.

Finally, recovering typedstream text is a **data migration**, not just wiring. dNh advances its cursor past skipped/malformed rows and revisits a bounded window, default 500 and maximum 5000 rows. Old omissions require deliberate reconciliation. Existing event-ID uniqueness and dedupe uniqueness can conflict when recovered content changes the hash; repository append behavior is unbundled and UNKNOWN. Evidence: `dnh:src/dnh_crm/services/ingest_runner.py:85–118`, `dnh:src/dnh_crm/services/ingest_runner.py:133–190`; `dnh:src/dnh_crm/store/migrations.py:5–24`.

### 3.3 Scope 3 — Policy Shield v2

**Assessment: the intended replacement is materially better than token-ratio “coverage,” but its approval claim is not yet executable or empirically justified. [F04, F05, F15–F18, F23]**

#### Four conditions need a complete information-flow contract

| Design condition | Gap that must be resolved |
|---|---|
| Exact evaluation passes for classes present | Required classes cannot depend solely on what the same detector happens to find. Missing/zero-support classes and unsupported languages need an explicit refusal or ineligible state. |
| Zero hard-fail hits | Define classes, uncertainty, and whole-run cancellation, including queued requests and retries. A skipped chunk is not a completed clean run. |
| Seeded sampled local-model opinion | Define sample population/size, detector sensitivity, malformed/unavailable outcomes, and how a leak is confirmed. |
| No attachment field in request model | This excludes one representation, not bytes or sensitive metadata embedded in strings, URLs, base64, examples, or context. |

Evidence: §3.6–3.7, §5, contract 4. A provider-construction barrier is useful defense, but the final request must be authorized after assembling the chunk, ±2 turns, question, metadata, schema/examples, and any retrieved or prior context. Bind approval to immutable serialized content, case/source/shield revision, recognizer/config hash, evaluation-report identity, operation, destination, and limited lifetime. Recheck retries and repair prompts. Every cloud route—including document and question embeddings—needs the same boundary. Unknown fields should be rejected. Freeze the selected source/input set and finish its hard-fail evaluation before the first cloud transmission. A later refusal can stop remaining calls but cannot undo completed disclosures; report any calls already sent. The transport can enforce approved-projection-only transmission, while an imperfect detector cannot guarantee that the projection contains no residual personal data. Report those two claims separately.

The old redactor demonstrates the danger of narrow projection: it copies arbitrary chunk fields while replacing only `text`, and empty text passes through unchanged. Fine-label checking examines one metadata key (`chatx:src/chatx/redaction/policy_shield.py:226–248`, `chatx:src/chatx/redaction/policy_shield.py:347–355`). A cloud schema must positively enumerate permitted fields. Decide separately whether OCR/transcripts are allowed as sanitized text; “attachments never uploaded” should not silently answer that question.

“Configured local” is also a policy assertion, not evidence. Establish allowed loopback/Unix-socket transports, DNS resolution, redirects, proxies, and server forwarding. A local privacy judge must satisfy the same local-inference requirements as enrichment. Core-only socket tests cannot prove the full application, native extensions, subprocesses, or serving process have no unintended egress. Current server evidence is in Report §3.15; the owner's configuration is UNKNOWN.

#### Evaluation and recognizer choice

Presidio is a **plausible framework candidate**, not an established best detector for this corpus. There is no implementation or measured comparison in the pack. Compare the proposed spaCy baseline, supported transformer/GLiNER integrations, and custom recognizers on the owner's languages, abbreviations, slang, handles, partial identifiers, and conversational context. Preserve exact model artifacts and recognizer/config versions. Framework selection and achieved recall are different decisions (§3.7, V3; current documentation in Report §3.15).

The existing name recognizer illustrates a realistic failure mode: it locates repeated words with `text.find(word)`; in the static example “John texted John,” both matches point to the first occurrence, and deduplication leaves the second without a recorded span. This was reasoned from code, not tested (`chatx:src/chatx/redaction/patterns.py:115–156`).

Evaluation must distinguish entity recognition, exact-span recovery, and removal of all identifying characters. Report precision/recall by class, language, source, and difficult slice, with support and uncertainty. Zero positive examples is not 100% recall. Keep annotation guidance, adjudication, held-out splits, corpus identity, normalization, overlap resolution, thresholds, and pipeline hashes. Group splits by conversation/person/source so near-duplicate chunks do not appear on both sides.

Synthetic data is repeatable regression evidence; it does not establish applicability to real conversations. §3.7 refers to real-sample targets while P3 accepts synthetic gates and §12, question 3 permits no real labels. Resolve whether that means local-only eligibility or a separately approved reduced claim. A note saying “synthetic only” cannot turn the number into real-case recall.

Define span ownership and offsets across messages and overlapping chunks. Message-only redaction may miss an identifier split across turns; independently redacting overlapping chunks can produce inconsistent replacements. Context can help detection, but only the final serialized request can establish what will leave the device.

#### What sampled review can and cannot bound

For independent, identically distributed random draws from the target population, a perfectly sensitive detector, and zero observed leaking chunks, the one-sided upper bound on a leaking-chunk probability is:

$$p_{upper}=1-\alpha^{1/n},\qquad n\geq\left\lceil\frac{\ln\alpha}{\ln(1-p_0)}\right\rceil.$$

| Zero-leak sample | Approximate 95% upper bound |
|---:|---:|
| 100 chunks | 2.95% |
| 600 chunks | 0.50% |
| 3,000 chunks | 0.10% |

Under those assumptions, at least **598** zero-leak samples support a bound below 0.5%; **2,995** support a bound below 0.1%. These are mathematical examples, not measurements or recommended risk tolerances. The same binomial reasoning can illustrate the positive-entity support required to substantiate recall when no misses are observed.

If second-opinion sensitivity is `s` for that population and the necessary independence holds, the simplified zero-detection probability is `(1 − p·s)^n`. Unmeasured sensitivity prevents converting zero detected leaks into the stated numerical bound on actual leakage. For a fixed population of `N` chunks containing `K` truly leaking chunks, sampled without replacement, use the corresponding hypergeometric probability, `C(N−K,n)/C(N,n)`, rather than treating the case as an infinite independent population. Overlap and repeated entities matter when generalizing beyond that fixed chunk population. Simultaneous per-class assurances also require accounting for multiple claims.

Specify the estimand, sampling frame, corpus digest, seed, sample-size rule, strata, known sensitivity, and uncertainty outcomes. Add targeted adversarial slices separately from random estimation. Treat the model's opinion as a fallible detector exposed to untrusted text; a seeded sample is defense in depth, not anonymity certification.

#### Hard-fail and round-trip security

Legacy hard-fail regexes explicitly describe themselves as demonstrations and include broad categories with no executable treatment of negation, quotation, benign reporting, or uncertainty (`chatx:src/chatx/redaction/patterns.py:159–197`). Do not port them as a validated policy. Use non-sensitive synthetic refusal fixtures, a class/decision registry, and whole-run blocking that preserves local evidence.

The prior audit's “never blocks” shorthand is inaccurate. Optional CLI preflight exits nonzero for reported low coverage or `hardfail_triggered`. However, ordinary redaction only warns; hard-fail raises before returning metadata; the outer loop catches it and skips the chunk before setting the flag. Visibility-only errors do not satisfy the shown CLI exit condition. Evidence: `chatx:src/chatx/redaction/policy_shield.py:180–205`, `chatx:src/chatx/redaction/policy_shield.py:258–278`, `chatx:src/chatx/redaction/policy_shield.py:332–355`; `chatx:src/chatx/cli/main.py:298–307`, `chatx:src/chatx/cli/main.py:336–350`.

Identity HMAC pseudonyms already use 128-bit truncation; the PII tokenizer is a different salted-hash system with eight hex characters. The design's 128-bit intent should replace stale `id8` notation with an exact encoding. A secret HMAC key should be named and handled as a key. Define random generation, purpose/type domain separation, normalization, collision handling, case isolation, rotation, migration, restart consistency, and recovery. Evidence: `chatx:src/chatx/identity/normalize.py:47–95`; `chatx:src/chatx/redaction/patterns.py:200–249`; §3.7.

Current key creation does not explicitly establish restrictive mode, exclusive creation, symlink safety, or validation of existing keys; actual permissions are UNKNOWN. Require private parent directories and secure creation/verification. A reverse map “only in the DB” is a location rule, not encryption. Protect the whole raw case, WAL, backups, exports, and keys according to an explicit local threat model.

Rehydration must reject malformed, unknown, cross-case, and out-of-request tokens; escape literal token syntax in originals; and permit substitution only for values authorized for that response. A valid token is not universal permission to reveal its value. Rehydrated answers must not reenter cloud context without a new projection and approval.

Finally, direct-identifier removal leaves dates, places, relationship sequences, rare events, writing style, and stable-token linkage. The supplied coarse taxonomy includes sexual/substance and relationship attributes, with orientation context explicitly never redacted (`chatx:config/labels.yml:191–253`). Decide disclosure by category and use, independently of PII detector classes. Local-only processing remains necessary where privacy-preserving generalization would remove the utility.

### 3.4 Scope 4 — Storage, durability, and forensic export

**Assessment: no finding requiring a database-server replacement. The chosen local stack needs stronger invariants and measured acceptance. [F11, F24–F26, F37]**

dNh contains a 1024-dimensional `vec0` schema, conversation partitioning, and external-content FTS triggers. It does not prove a deployed index: `sqlite-vec` is optional, loading errors are swallowed, and vector-table creation is conditional. Runtime capability and performance are UNKNOWN. Evidence: `dnh:pyproject.toml:56–59`; `dnh:src/dnh_crm/store/migrations.py:181–238`, `dnh:src/dnh_crm/store/migrations.py:327–336`, `dnh:src/dnh_crm/store/migrations.py:375–380`.

An embedding space must identify model/artifact revision where observable, dimensions, scalar type, distance metric, normalization, task prefixes, tokenizer/preprocessing, redacted versus raw input, and chunker/shield versions. Equal dimensions do not mean compatible vectors. Define building/ready/active/retired states, resumable rebuild, atomic active-generation switch, query compatibility checks, and old-generation retention.

At float32, `N × d × 4` gives **4.096 GB** for one million 1024-dimensional vectors and **12.288 GB** for three million. These exclude text, FTS, metadata, WAL, temporary rebuilding, and old spaces. Disk size is not RSS; local model weights and inference memory are additional budgets. Also define the workload: 40-turn windows with 10-turn overlap advance 30 messages, so one million uniformly chunked messages is not automatically several million chunks. Multiple units, revisions, and spaces can change the count (§3.8; `chatx:src/chatx/transformers/chunker.py:124–156`).

Benchmark the actual target distribution, dimensions, filters, cold/warm queries, concurrent import, checkpointing, rebuild, peak RSS, and migration disk. No current measured threshold is established by the pack.

The table outline must specify source-observation links, chunk-to-message-revision/spans, attachment instances versus shared objects, foreign keys, uniqueness, generation visibility, and invalidation. Editing text or changing Shield must invalidate dependent chunks/labels/vectors/caches consistently. Use bounded write transactions; do not hold them through inference or network calls. State writer ownership, busy deadlines, long-reader/checkpoint behavior, cancellation, and restart. A query must see a coherent generation (§3.5, §4).

`case verify` should check database integrity, foreign keys, source associations, FTS/vector correspondence, manifests, and CAS objects. Define migration ordering/checksums, rollback or forward repair, and how an unsupported extension/version fails visibly. Missing vector capability must not silently present a degraded system as fully indexed.

CAS publication and SQLite commit are separate durability boundaries. Specify crash recovery before/after staging, publication, reference commit, and cleanup. Garbage collection must retain objects referenced by any retained source, revision, or export. Backup/export must capture a consistent DB generation and every referenced attachment; verify restoration into a clean location, including key availability and broken/missing objects.

The forensic claim needs an intended audience. A SHA-256 manifest checks consistency against that manifest; an actor replacing both can create another self-consistent bundle. It does not establish author, acquisition time, source completeness, or truth of an inference (§1, §3.10). Preserve acquired source artifacts or explicitly disclose external-retention dependence; distinguish original bytes, normalized records, and generated interpretation. Record tool/config identity, acquisition method, source inclusion/exclusion, transformations, operator/transfer events, and verification method.

Decide whether signatures or externally anchored timestamps are needed for the intended hand-off. They add authenticity evidence under their trust assumptions; they do not retroactively prove source truth. A logical SQLite snapshot and a byte-preserving acquisition are different artifacts with different claims. The case is already a directory-level object because attachments live outside the database. Its recovery/export contract must reflect that.

### 3.5 Scope 5 — Providers

**Assessment: retain the two-adapter direction, but make capabilities and outcomes part of the contract. [F19–F21, F38]**

`complete_structured(...)->BaseModel` describes only successful parsing (§3.6). Distinguish unsupported schema/parameter/model, refusal, truncation, malformed output, transport failure, quota, cancellation, and quarantined output. One “retry invalid JSON once” rule cannot govern them. Describe the supported structured-output mode and schema subset for each tested endpoint/model pair; validate the original semantic schema after any backend transformation. Current API-specific evidence appears in Report §3.15.

Completion and embedding are independently selectable capabilities. An Anthropic adapter need not pretend to implement an embedding operation unavailable at that destination. Missing local model/embed configuration should fail before an expensive run; no automatic remote fallback is compatible with the stated privacy policy. Record the selected operation and effective destination.

Separate transport retries from schema-repair attempts. Define connect/read/write and total deadlines, cancellation, bounded concurrency, server backoff handling, jitter, quota exhaustion, maximum combined attempts, and run budgets. Do not retry a refusal or deterministic unsupported request as if it were a temporary network failure. An 800-token output limit does not cap input size, repeated context, reasoning usage, elapsed local computation, or total cost (§3.6, §3.9).

The old client contains timeout/concurrency/retry pieces but can replace its retry decorator with a no-op when a dependency is unavailable. Those pieces are requirements leads, not proof of resilience (`chatx:src/chatx/enrichment/ollama_client.py:18–26`, `chatx:src/chatx/enrichment/ollama_client.py:176–210`, `chatx:src/chatx/enrichment/ollama_client.py:263–331`). Persist completed work and per-attempt outcomes so restarts do not repeat all calls. Distinguish provider-reported usage, estimated usage, and unknown usage; unknown is never zero. Expose estimates and a cancellable budget before processing.

Return immutable per-call provenance alongside the parsed result: requested/returned model, available artifact/backend revision, request ID, effective and unsupported parameters, prompt/input/config hashes, response hash, terminal reason, attempts, timing, and usage. A mutable provider `identity` property does not specify correspondence under parallel calls. Returned model strings are provider assertions, not cryptographic attestation.

Temperature zero and a seed are requested controls, not demonstrated cross-backend reproducibility. Record what was actually accepted/applied. Separate replay of a stored response from regeneration. Select Apple-silicon serving through a bounded task benchmark; machine model/RAM, backend versions, quantization, context length, and measured fit are all UNKNOWN here.

### 3.6 Scope 6 — Enrichment and taxonomy

**Assessment: compiling one taxonomy is the right repair, but names, semantics, visibility, state, and evaluation must also align. [F08, F18, F20–F23]**

The supplied YAML has top-level `coarse` and grouped `fine_local_only` mappings. The multi-pass loader expects a nested `categories` structure with coarse/fine lists; successful YAML loading can therefore produce empty sets without activating the exception fallback. The fallback vocabulary is different again. Evidence: `chatx:config/labels.yml:8–23`, `chatx:config/labels.yml:307–310`; `chatx:src/chatx/enrichment/multi_pass_pipeline.py:93–145`.

Compilation should validate unique IDs, references, aliases, co-occurrence/wildcard rules, exclusivity semantics, visibility, and every relationship-rule reference. The declared 55/99 counts are not a substitute for a compiler-derived inventory; no compiler or measurement was executed here. Generate separate cloud/local enums, schemas, descriptions, and examples. Earlier local enrichment must not leak through later cloud context.

Some categories combine opposite evidence: responsiveness with unresponsiveness, or positive consent/boundary discussion with violations. That can be useful as a broad topic label, but cannot alone justify a directional relationship claim. The mutual-exclusion group for relationship arrangements also needs actor/time/quotation semantics: a conversation can mention different people's arrangements or changes over time. Evidence: `chatx:config/labels.yml:29–32`, `chatx:config/labels.yml:94–97`, `chatx:config/labels.yml:465–466`.

The old hysteresis function has no previous state; its branches largely implement the same threshold decision. Real hysteresis requires a state key, transition rules, evidence order, reset conditions, and revision behavior. If the intent is accept/review/reject bands, call it that and define the abstention workflow. Neither the numerical thresholds nor a model's confidence establish calibrated probability. Evidence: `chatx:src/chatx/enrichment/enricher.py:149–179`; §3.9.

Cache identity must include all evidence seen: ordered context, taxonomy/visibility version, full prompt/schema, Shield policy/model/normalization, effective decoding parameters, and observable model artifacts. Handle aliases and UNKNOWN observed identity conservatively. A cache keyed only to the central chunk becomes stale when a neighbor, identity, reaction, or redaction changes.

The chunker hashes IDs/time rather than text and inserts `run_id` into a 32-bit chunk ID (`chatx:src/chatx/transformers/chunker.py:113–122`). Specify stable revision-based identity, actual step versus overlap, and parameter bounds. Daily chunking is a separate method; the shown dispatch does not establish the promised automatic fallback. A single oversized message can exceed fixed-size intent (`chatx:src/chatx/transformers/chunker.py:315–353`, `chatx:src/chatx/transformers/chunker.py:406–422`).

Keep structured messages through enrichment. The old enricher reconstructs messages by splitting rendered lines, assigning IDs by line index, using current timestamps, and supplying the final three messages as context. Multiline bodies and groups can therefore be misassociated; this is not the promised ±2 neighbors (`chatx:src/chatx/enrichment/enricher.py:243–256`, `chatx:src/chatx/enrichment/enricher.py:290–326`).

Evaluate label-level precision/recall, macro/micro aggregates, calibration, abstention, actor attribution, and costly confusions on held-out conversations. Include negation, sarcasm, quotations, slang, roleplay, historical references, contradictory context, and rare labels. Preserve annotation disagreement. Track quality, cost, and latency together; optimizing cache hits or schema validity alone can reward wrong outputs.

Finally, existing prompts interpolate contact, text, and context into one user message containing task instructions (`chatx:src/chatx/enrichment/ollama_client.py:234–261`, `chatx:src/chatx/enrichment/ollama_client.py:277–279`). Treat chat evidence as untrusted data. Schema-valid injection can still change labels, confidence, privacy judgments, or citations. Give models no authority to change the transport gate, resolve arbitrary identities, or treat an embedded instruction as permission.

### 3.7 Scope 7 — Search and query

**Assessment: RRF is a sensible candidate; evidence fidelity and evaluation remain the decisive gaps. [F08, F25, F27]**

The existing chunk schema requires message IDs, but vector-store preparation records only their count. Search later retrieves the omitted IDs with an empty-list default, and the CLI prints citations only when IDs exist. This is a directly traceable hand-off defect: `chatx:schemas/chunk.schema.json:15–21`; `chatx:src/chatx/indexing/vector_store.py:170–195`, `chatx:src/chatx/indexing/vector_store.py:329–335`; `chatx:src/chatx/cli/main.py:958–959`.

Define the common ranked unit before fusion: messages, chunks, or another stable unit. Specify candidate limits, RRF constant/weights, rank origin, ties, duplicates, overlap suppression, and unavailable-retriever behavior. Apply conversation/participant/time/access filters consistently before each candidate search; post-filtering a short global top-k can miss relevant eligible results. Message-level time inclusion differs from requiring a whole chunk inside a date interval (§3.10).

Short exact strings, rare identifiers, emoji/slang, paraphrases, and chronology need separate evaluation. Expand neighboring turns/replies within the selected conversation only after explicit bounds; define whether contact filtering selects authored messages, participant conversations, or bounded conversational context, and apply that scope consistently. Decide label-any/all/not behavior—the current CLI marks some filters unimplemented (`chatx:src/chatx/cli/main.py:829–859`).

Keep chunk-to-message **revision and span** associations. A citation should resolve to case/source snapshot, conversation, logical ID, revision/hash, source locator, and relevant span. Distinguish original text, redacted display, transcript/OCR, and generated analysis. Validate model-generated references against the supplied evidence IDs, and assess whether the cited material supports the particular claim. A retriever provenance link alone is not claim support.

Build a held-out query/relevance set with absent-answer cases, misleading near matches across conversations, groups, replies, edits, unsends, date boundaries, and incomplete histories. Compare lexical-only, vector-only, and fused retrieval; measure candidate recall, ranking quality, source resolution, claim support, abstention, and latency separately. Use grouped/temporal splits to prevent overlapping chunks leaking into evaluation. RRF scores and model confidence are not probabilities of evidentiary truth.

Local RAG is the correct default (§3.10). Cloud query adds a fresh question, retrieval context, and potentially prior answers; all must participate in the final-payload gate, including question embedding. Keep the no-attachment rule even if a provider offers native document citation features.

### 3.8 Scope 8 — Relationship and episode analysis

**Assessment: no finding requiring a graph database. The blocker for trustworthy interpretation is validity, not graph storage. [F28]**

SQLite relationships/episodes can represent local nodes, edges, temporal evidence, and rule outputs. The design should define actor/target roles, relation direction, time interval, source spans, observation versus self-report versus inference, contradictory evidence, and rule/model revision (§3.11).

The current mapper unions both chunks' labels, accepts any matching source label, and computes a clipped score from a base, context multiplier, and overlap. Its temporal condition is a caller Boolean defaulting true. For `GASLIGHTS`, 0.93 multiplied by 1.2 already exceeds 1 before any overlap bonus; one matching label can therefore yield 1.0 by static arithmetic. This does not measure intent or causation. Its explanations include categorical claims about boundary violations and reality distortion. Evidence: `chatx:src/chatx/storage/psychology_relationship_mapper.py:51–101`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:217–220`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:343–347`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:548–570`.

The base registry associates nurturing with candidate manipulation/overload patterns; its function describes commonly involved patterns, not detected episodes. Porting associations as detections would change their meaning (`chatx:src/chatx/storage/base.py:551–588`). Mapper source labels also disagree with actual taxonomy keys (`chatx:src/chatx/storage/psychology_relationship_mapper.py:130`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:217`, `chatx:src/chatx/storage/psychology_relationship_mapper.py:343`; `chatx:config/labels.yml:307–431`).

Retain these rules only as unvalidated hypotheses until construct definitions, actor attribution, confusions, counterexamples, annotation agreement, and evidence-level error are assessed. Label heuristic scores honestly; require abstention and owner correction. Missing messages, sarcasm, quotation, fiction, consensual roleplay, and reports about third parties can change interpretation. A consent statement or opt-in switch does not establish scientific validity.

P6 should have separate permissions and readiness criteria for relationship hypotheses, sensitive attribute analysis, audio, and images. Keep outputs local by default, distinguish them visibly from source evidence, allow disabling/deleting/correcting them, and avoid diagnostic or intent certainty unsupported by the record. The proposed mental-BERT experiment/ADR is a reasonable containment decision; no benchmark or clinical validity is established by this pack.

### 3.9 Scope 9 — Workspace, packaging, and versioning

**Assessment: keep the authorized workspace layout; strengthen the consumer and installed-artifact contracts. [F29, F30, F33, F36, F38]**

The sibling editable path is useful for development. It does not identify the source bytes used when dNh's revision and lockfile remain unchanged while the sibling checkout changes. Define clean-clone acquisition of both repositories, immutable paired revisions or a versioned release artifact, compatibility policy, and coordinated lock updates (§3.2–3.3, V8). Exact current uv options are reviewed in Report §3.15; lockfile bodies and independent confirmation of the design's claimed uv 0.12.11 installation are unavailable.

Test the core as an isolated installed package, not only inside a shared environment that can hide undeclared dependencies. Its network/LLM/storage independence is a good boundary; current ChatX extraction imports transcription/application helpers, so porting needs dependency removal or explicit hooks rather than moving files unchanged (`chatx:src/chatx/imessage/extract.py:268–272`; §3.3, §8).

Runtime assets need packaging requirements. The current validator walks upward from `__file__` to root schemas; wheel selection names `src/chatx`, while root schemas are explicitly included in the sdist. Run-report validation returns success when the schema is missing. These are source assumptions, not an executed wheel failure (`chatx:pyproject.toml:121–130`; `chatx:src/chatx/schemas/validator.py:13–36`; `chatx:src/chatx/utils/run_report.py:89–95`). Package generated schemas, taxonomy, SQL migrations, and recognizer/rule assets; verify a built installation outside the checkout.

Python 3.12 as a floor is a decision requiring both consumers' dependency resolution and supported-platform evidence. Lower/upper bounds are constraints, not proof of compatibility; pre-1.0 packages especially need a tested version policy. Record native runtime and model artifact versions, not only Python package names. Run package-specific coverage as well as the aggregate so one package cannot hide the other's untested surface.

ChatX declares MIT and dNh Proprietary. This is not proof of incompatibility or missing authority; ownership is UNKNOWN. Confirm the core's intended license/distribution and authority to copy code, preserving notices and source provenance (`chatx:pyproject.toml:10`; `dnh:pyproject.toml:7`).

### 3.10 Scope 10 — Phase plan

**Assessment: the broad order is sensible; exit criteria need dependency repair and earlier risk evidence. [F05, F14, F25, F29–F33]**

| Phase | Required correction to the exit evidence |
|---|---|
| P0 workspace/CI | Prove clean paired checkouts, immutable core selection, runtime/extension capability, and ownership/license decisions. Establish isolated installed-package smoke-test infrastructure; require each runtime resource's installed test in its introducing phase. Run short acquisition, schema, storage, and provider spikes before committing dependent work. |
| P1 extraction | Settle time/identity/event contracts first; include scope/backup defects, full source-row accounting, private real-blob applicability, and dNh historical migration. “All messages have text” would be the wrong criterion for media/system/unsent records. |
| P2 storage | Add coherent restart/repair, migration, CAS crash recovery, and restore. A 100k import does not validate several million vectors. |
| P3 Shield | Resolve real-data eligibility and a complete final-payload refusal matrix. The sampled local-provider check depends on capability work otherwise deferred to P4. |
| P4 providers/enrichment | Establish the local provider needed by P3, exact request authorization, accounting, schema semantics, and task quality. “Visible to query” needs either an explicit preliminary query path or movement to P5. |
| P5 search/export | Require relevance and citation-support evaluation, consistent generations, clean restore, and cloud question/embedding gate tests; latency numbers alone are insufficient. |
| P6 analysis/media/backups | Give each feature its own validity, resource, privacy, and source-preservation gate. Case protection for earlier real imports cannot wait for encrypted-backup support. |
| P7 delivery/docs/MCP | Verify installed user workflows, intended authorization, migration guidance, recovery, and cutover before retiring the old workflow. |

Evidence: §6, §7, §10, §11. Fixing dependencies does not require implementing everything at once. A small vertical slice—acquire, preserve, canonicalize, store, gate, retrieve, cite, and verify export—can expose cross-stage losses before breadth increases.

Recording performance is better than repeating unsupported numbers. But promoting a target only after it has been met twice (§7) is not an independent acceptance requirement. Define an owner-relevant workload, hardware envelope, cost/latency/storage constraints, reproducible measurements, and what outcome would trigger revisiting a choice. Distinguish an exploratory measurement from a release gate.

There is no mandatory elapsed schedule in the design that this audit can validate. Relative uncertainty is clear: real extraction coverage, privacy evaluation, cross-provider conformance, target-scale retrieval, and interpretation validity deserve bounded spikes before large dependent phases. Preserve store-before-derived-processing and the later opt-in analysis lane.

### 3.11 Scope 11 — Threat model

**Assessment: the design states an important cloud boundary but leaves much of the local and operational information flow unspecified. Actual exposures below are UNKNOWN. [F04, F11, F17, F23, F31, F36]**

The following are conditional threats to address in §3.5, §3.7, and §3.13, not findings that the owner's machine is compromised or synchronized.

| Threat/channel | Required mitigation or explicit limit |
|---|---|
| Other local users, stolen storage, permissive ACLs | Private directories/files and a documented whole-case encryption/backup strategy. Separate locked-disk protection from an active unlocked session. |
| Same-user malware or compromised executable dependency | State that unlocked case/key/process access defeats file-mode protection. Minimize dependencies/privileges and isolate risky parsing/model components where practical. |
| Temporary snapshots, quarantine, WAL/SHM, FTS/vectors, caches | Inventory sensitive derivatives, create them in controlled locations, and define access, retention, cleanup, and recovery. Derived indexes can reveal content too. |
| Logs, terminal output, exceptions, provider responses | Allowlist operational fields and use opaque IDs. Sanitize validation input values, raw HTTP bodies, paths, query text, provider URL credentials, and generated intimate inferences. |
| Crash dumps, swap, diagnostics | State platform assumptions; avoid application crash uploads containing case data; review support bundles and diagnostic defaults. Do not promise memory erasure beyond what can be verified. |
| Spotlight or other indexing | Choose protected case locations, opt out where supported, and provide verification instructions. Current indexing behavior is UNKNOWN. |
| iCloud Drive or other sync | Check actual configured paths. Do not assume `~/code` or `~/Documents` is or is not synced. Prefer an explicit non-synced case root when that is the owner's policy. |
| Time Machine/other backup | Choose encryption, key handling, retention, and restore deliberately. Blanket exclusion can remove the only recovery copy. |
| Local inference services, proxies, redirects, tunnels | Verify effective destinations and cloud-forwarding settings; no remote fallback. Include service-side logs and process-tree egress in testing. |
| Presidio/spaCy/Hugging Face/sqlite-vec/Typer and transitive components | Actual telemetry is UNKNOWN. Separate model/package installation from offline inference; inspect pinned behavior, caches, subprocesses, and network attempts rather than assuming telemetry exists or does not exist. |
| Dependencies, native extensions, model artifacts, CI actions | Pin and verify artifacts/provenance; inspect executable loading paths, model code requirements, licenses, advisories, and update policy. Load only approved extensions. Keep real case material out of CI artifacts. |
| Untrusted SQLite, ZIP, MIME, PDF, media, and filenames | Bound sizes, counts, decompression, recursion, parsing time, and memory. Reject escaping paths/symlinks and avoid shell interpolation or opening unintended local files. |
| MCP clients and external tools | Local binding does not authenticate clients or authorize case access. Define operation/case permissions and what a connected client may subsequently disclose. |
| Export, rehydration, deletion | Use explicit full-evidence versus redacted export projections; keep keys/maps out of redacted outputs. Propagate deletion/retention decisions through indexes, caches, logs, and backups; disclose limits. |

Concrete legacy regressions support the logging concern: the client logs raw HTTP failure responses and raw model output on JSON errors; the enricher logs contacts and derives filenames from them (`chatx:src/chatx/enrichment/ollama_client.py:305–312`, `chatx:src/chatx/enrichment/ollama_client.py:385–400`; `chatx:src/chatx/enrichment/enricher.py:358`, `chatx:src/chatx/enrichment/enricher.py:384–393`). Whether such logs were ever produced or transmitted is UNKNOWN. “No secrets” should explicitly mean sensitive case content and inferences as well as API keys.

Quarantine is intentionally raw under §3.6, so it needs protected storage, bounded retention, export exclusion, and controlled inspection. Authentication keys in environment variables also need a child-process inheritance policy. A socket-blocked core test verifies only that tested boundary; it cannot establish the complete application/service threat model.

### 3.12 Scope 12 — Testing strategy

**Assessment: source shows useful test intent and real coverage exclusions; no passing gate or production-quality measurement is demonstrated. [F09, F14–F17, F24–F25, F27–F30, F33]**

ChatX's configuration requests 90% coverage while excluding redaction, transformations, enrichment, transcription, validator, and indexing. dNh declares branch coverage and an 80% report threshold. Neither workflow bodies nor lockfiles are bundled, so actual enforcement, runner architecture, optional dependency presence, and results are UNKNOWN. Evidence: `chatx:pyproject.toml:187–207`; `dnh:pyproject.toml:79–98`.

`config/arch-gates.yml` is not proof of an active GitHub workflow. It applies thresholds to the misleading privacy-ratio field, masks some steps with `|| true`, and checks visibility through a narrow projection; malformed JSON can be skipped (`chatx:config/arch-gates.yml:23–35`, `chatx:config/arch-gates.yml:43–48`, `chatx:config/arch-gates.yml:55–68`, `chatx:config/arch-gates.yml:76`). If later used for artifact uploads, fixture-only provenance must be enforced. Current execution is UNKNOWN.

The complete bundled dNh typedstream test file contains valuable malformed/unsupported-input, prefix, reference, UTF-8, and limit tests. Its “four-byte length” success test uses `0x8000`, while the fixture encoder uses two bytes through `0xFFFF`; it therefore does not exercise successful four-byte-length decoding. An oversized-output test does exercise a four-byte length, so the entire branch should not be called untested. Evidence: `dnh:tests/unit/test_imessage_attributed_body.py:30–37`, `dnh:tests/unit/test_imessage_attributed_body.py:140–161`.

Two asserted observed prefixes are combined with synthetic content; the original full blobs and expected real-message ground truth are absent. This establishes fixture intent, not population recovery accuracy (`dnh:tests/unit/test_imessage_attributed_body.py:59–113`). Probe tests use positive public schemas, reject injected PII before public writes, and prohibit raw artifacts under repository paths; the probe implementation is unbundled (`dnh:tests/unit/test_imessage_attributed_body.py:623–694`, `dnh:tests/unit/test_imessage_attributed_body.py:796–835`, `dnh:tests/unit/test_imessage_attributed_body.py:866–870`).

The release test matrix should assert preserved evidence and refusal semantics:

| Layer | Required meaningful cases |
|---|---|
| Time and schema | Unit/epoch counterexamples, null/non-finite/out-of-range values, unknown zone, ambiguous dates/DST, precision, cross-field kinds, invalid hashes, nested mutation, generated-schema parity. |
| Extraction and source accounting | Active WAL/checkpoints; missing/multiple chat links; contact not found; group membership; null text with attachments; text/blob disagreement; add/remove/re-add reactions; edits/unsends; unresolved/unknown codes. |
| Format fidelity | Backup/live name collisions and cleanup; WhatsApp ordinary system-marker words and locale dialects; Instagram paginated overlaps/encoding; MIME attachment-only/conflicting Message-ID; PDF multiline/page/time uncertainty. |
| Storage/CAS | Interrupted writes at each boundary, changed sources, corrupt existing CAS, missing media, concurrent imports, partial index generations, migration failure, clean restore, disk exhaustion. |
| Shield and transport | Missing/stale evaluation, zero class support, unsupported language, repeated/split PII, unknown local server, altered context, raw question/embedding, fine labels in examples, cross-case/stale token, retries, malformed detector response, all-run hard-fail before send. |
| Providers/enrichment | Unsupported parameters/schema, refusal, truncation, timeout, rate/quota limits, cancellation, unknown usage/model identity, taxonomy reference errors, cache invalidation, calibrated abstention, schema-valid injection. |
| Retrieval and interpretation | Stable IDs/spans, wrong-conversation decoys, date boundaries, absent answers, edits/replies, citation support, actor attribution, contradictory evidence, sensitive false allegations, and export round-trip. |
| Packaging/operations | Installed wheel outside checkout, both consumer locks, Python floor/macOS arm64, absent optional capabilities, safe log/error/quarantine sentinels, full process-tree egress, and independent restore instructions. |

The attachment-null case is a concrete integration requirement: dNh's classifier permits it when attachments exist, but the mapper's required-text function rejects `None` (`dnh:src/dnh_crm/ingest/imessage_source.py:55–69`; `dnh:src/dnh_crm/ingest/imessage_mapper.py:14–16`, `dnh:src/dnh_crm/ingest/imessage_mapper.py:69–72`).

Use property tests for canonical serialization, ID stability, idempotent reimport, token round-trip/isolation, and evidence association preservation. Use contracts/fault injection for boundary failures and held-out corpora for quality; line coverage cannot substitute for either. Real fixtures should be consented, private, access-controlled, versioned, and reviewed for structural and annotation integrity. Format-aware synthetic replacements can preserve structural cases, but must not be misrepresented as full authentic corpus coverage.

Every import should reconcile its inspected source population to mutually exclusive dispositions: accepted logical observations, known duplicates/links, related/system events, quarantined or unsupported records, and explicit exclusions/deferred work. A positive message count or “all tests pass” without this accounting can miss silent loss.

### 3.13 Scope 13 — Omissions affecting users

**Assessment: several acceptance-level user contracts are missing; these should not be left as incidental CLI details. [F14, F20, F24, F26, F31, F34]**

The design names stages and commands but does not explain the following outcomes sufficiently (§3.5, §3.12, §4, §7):

- **Planning and progress:** dry-run source scope, supported/unsupported format detection, estimated disk/model cost, visible cancellation, and reconciliation of partial success.
- **Resume and incremental updates:** durable checkpoints, recovery from interruption, edits/deletions discovered later, source replacement/ROWID reuse, and historical backfill.
- **Existing corpus migration:** old canonical IDs, stored outputs, citations, pseudonyms, keys, annotations, and dedupe cannot be handled by source-code porting alone.
- **Case portability:** cloning/moving cases without absolute-path breakage, selecting full versus redacted exports, key recovery, incompatible-version refusal, and verified restoration.
- **Retention and correction:** how owner corrections invalidate derived analysis; how deletion reaches raw/derived data, indexes, caches, quarantine, logs, and retained backups. Do not promise secure physical erasure of all historical storage copies.
- **Failure/status semantics:** distinguish not found, permission denied/TCC, unsupported, corrupt, partial, empty, refused, and cancelled. Define machine-readable output, stderr/stdout, stable problem codes, and exit status allocation, including framework usage errors.
- **Workflow completeness:** §1 promises an integrated pipeline while §3.12 lists stages without an orchestration command. Either specify one reproducible resumable workflow or qualify that promise.
- **Source access instructions:** define supported backup completeness, required source permissions, and actionable recovery steps. A permission failure must never become “no messages.”

These are product behavior requirements, not demands for extra services, a UI, or every old command. Their exact defaults can be chosen by the builder only after the evidence, privacy, and recovery contracts are settled.

### 3.14 Scope 14 — Intent reconciliation

**Assessment: old documentation is correctly treated as inspiration, but the design needs an explicit disposition ledger. [F35]**

The original documents cited by `evidence/03-docs-parity-inventory.md` are mostly only inventoried, not supplied as source bodies. Their original claims and line citations are therefore **UNKNOWN** to this reviewer. The table below uses that evidence file only to identify questions, then checks the design's stated intent. It does not restore old prose as requirements.

| Intent raised by evidence/03 | Verified design disposition / needed clarification |
|---|---|
| HTTP API, multiuser/server operation, live capture, Telegram export, differential privacy | Explicitly excluded or retained in dNh by §2/§3.14. **No finding** requiring their return. |
| Chroma, Neo4j, psychology-specific multi-vector implementations | Explicit retirement/experiment choices in §3.14. Keep the choice if desired; correct unsupported “dead to CLI” reasoning. |
| Image/audio analysis and encrypted backups | Deferred to P6 with ADR/evaluation. Define independent feature gates; raw source preservation must already work before optional interpretation. |
| PDF OCR and generic TXT import | OCR appears in extraction ambitions while media is deferred; TXT appears in the platform enum without a corresponding import contract. Mark supported, deferred, or out of scope explicitly (§3.4, §3.11–3.12, §4). |
| Simulate/reply, timeline/factors/token inspection, label/issues/episode commands | Some analysis intent is retained, but command-level disposition is unclear. Decide which user outcomes survive rather than silently carrying old command names (§3.11–3.12). |
| Metadata-only index updates, backfill, checkpoints, cost ledger, dry-run | Not adequately resolved by “one DB.” Add acceptance behavior or explicit non-goals (§3.5, §3.9–3.12). |
| Manual QA, support matrix, old performance/cache promises | Replace unsupported numbers with actual evaluation and supported-platform contracts. State that old targets are retired, rather than leaving contradictory promises (§7, §11). |
| One-command pipeline | Broad promise remains; orchestration/resume behavior is not enumerated (§1, §3.12, §4). |

The source also corrects inherited grades:

1. **Redaction is not uniformly non-blocking:** optional preflight has nonzero exits, with the important holes detailed in Report §3.3 (`chatx:src/chatx/cli/main.py:336–350`).
2. **Multi-vector is not dead to CLI:** index constructs its store and query calls `search_multi_vector`; insights have a call site. The imported implementation is unbundled, so successful execution remains UNKNOWN (`chatx:src/chatx/cli/main.py:734–745`, `chatx:src/chatx/cli/main.py:780–796`, `chatx:src/chatx/cli/main.py:821–839`, `chatx:src/chatx/cli/main.py:861–882`, `chatx:src/chatx/cli/main.py:917–924`).
3. **“WAL-safe,” broadly “well-tested extraction,” and “keep with minimal change” are unsupported endorsements:** the cited snapshot, timestamp, scope, backup, and parser defects require rework (§8; F01–F14).
4. **“dNh already runs this stack” exceeds schema evidence:** code declares optional vector capability; actual installation, runtime, and workload are UNKNOWN (`dnh:src/dnh_crm/store/migrations.py:327–336`, `dnh:src/dnh_crm/store/migrations.py:375–380`).
5. **Counts and machine state remain claims:** declared taxonomy counts, tooling-directory motivation, installed uv, passing CI, and real decoder coverage require direct evidence. The filtered inventory cannot reconstruct the complete tooling count (§3.2–3.3, Appendix A).

The correct response is a short accepted/deferred/dropped/unknown ledger linked to the new design. It prevents builders from both reviving unapproved scope and discarding intended workflows accidentally.

### 3.15 Scope 15 — Ecosystem currency

**Research date: 2026-10-20. Training cutoff: UNKNOWN/not exposed.** Only this scope used external sources. The following are primary documentation/model-card observations, not facts about the installed repositories. Confidence is **HIGH** that the cited pages state the listed capability; fitness, installed availability, and benchmark results for ChatX remain **UNKNOWN** unless separately qualified. Dynamic documentation should be pinned or archived as implementation evidence.

| Item | Current primary-source evidence | Consequence / confidence in recommendation |
|---|---|---|
| SQLite WAL correctness | SQLite documents a rare WAL-reset race affecting WAL databases with concurrent write/checkpoint connections. It identifies fixes in **3.51.3 and later**, with backports **3.44.6** and **3.50.7**; likely affected history extends through 3.51.2. [SQLite WAL, §11](https://sqlite.org/wal.html). | **HIGH:** verify the actual linked runtime and fix provenance before concurrency acceptance [F37]. Do not infer vulnerability from Python's version or claim an incident occurred. |
| Consistent database copying | SQLite documents its [Online Backup API](https://sqlite.org/backup.html) and alternative snapshot-copy techniques. WAL documentation also permits some read-only/immutable WAL use; immutable does not universally mean WAL is ignored. | **HIGH:** evaluate a supported coherent working-snapshot mechanism. Separately define preserved original evidence; a logical backup is not automatically a byte-identical forensic acquisition [F01, F26]. |
| sqlite-vec maturity | The [upstream repository](https://github.com/asg017/sqlite-vec) still identifies the project as pre-v1 and warns of breaking changes. The current tree/documentation must be evaluated at a pinned release. | **MEDIUM:** retain as a candidate under the owner's choice, with compatibility and workload gates [F25]. Do not present a 2024 “brute-force only” description or a historical in-memory benchmark as a complete account of 2026 capabilities. No current ANN/scale winner was established. |
| Claude model identifiers | Official pages identify [Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) and [Claude Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/overview), including the configured `claude-sonnet-5-5` and `claude-opus-5-5` IDs. | **HIGH:** these IDs should not be called invented or obsolete. Account access, selected aliases, observed responses, task quality, and cost remain unverified [F19–F21]. |
| Claude request controls | [Sonnet 5.5 migration notes](https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5) describe adaptive thinking and 400 errors for `thinking.type=disabled` and forced `tool_choice` values `any`/`tool`. | **HIGH:** test the default model's actual controls. Do not implement universal structured output by blindly forcing tools or forwarding legacy thinking/seed/temperature settings [F19, F38]. |
| Claude structured output | [Structured-output documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) uses `output_config.format`; describes refusal, truncation, schema limitations/SDK transformations, and enum-case caveats. [Citation documentation](https://platform.claude.com/docs/en/build-with-claude/citations) says native citations and strict structured outputs cannot be combined. | **HIGH:** preserve typed failure outcomes and validate the original schema. Use an application-owned evidence-ID contract when strict JSON is required. Native document features do not override the no-attachment policy [F19, F27]. |
| Anthropic embeddings | The official [embeddings guide](https://platform.claude.com/docs/en/build-with-claude/embeddings) says Anthropic does not offer its own embedding model. | **HIGH:** select an embedding capability independently; fail early if unavailable [F19]. A separate hosted service would be a separately authorized cloud destination. |
| Ollama trust and compatibility | [OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility) covers a subset. The [FAQ](https://docs.ollama.com/faq) documents cloud operation through the local service and disabling it with `disable_ollama_cloud` or `OLLAMA_NO_CLOUD=1`, followed by restart. [Structured-output docs](https://docs.ollama.com/capabilities/structured-outputs) currently exclude Ollama Cloud support. | **HIGH:** loopback alone does not prove local inference. Verify effective offline settings and model route; maintain endpoint-specific conformance cases [F04, F19]. No claim is made about the owner's settings. |
| Presidio governance and engines | Current [transition documentation](https://presidio.dataprivacystack.org/project_transition/) describes movement from Microsoft ownership to Data Privacy Stack community governance, MIT continuity, and changed container publishing. [Analyzer documentation](https://presidio.dataprivacystack.org/analyzer/) describes configurable NLP integrations; the [project home](https://presidio.dataprivacystack.org/) warns that detection cannot be guaranteed complete. | **MEDIUM** for framework suitability; **UNKNOWN** for this corpus's recall. Verify package/image provenance during the transition. Benchmark the proposed spaCy, transformer, and GLiNER options instead of equating framework adoption with target recall [F05, F36, F38]. |
| uv external consumers | Current [workspace docs](https://docs.astral.sh/uv/concepts/projects/workspaces/) describe a shared workspace lock and an external-workspace source path pointing to the other workspace's root. They also warn that Python dependency isolation is not enforced. [Dependency docs](https://docs.astral.sh/uv/concepts/projects/dependencies/) explain source overrides and checking standard dependency resolution without them. | **HIGH** for evaluating documented workflows, not for claiming compatibility with the asserted installed uv 0.12.11. Preserve the owner's dev layout; test immutable consumer inputs and isolated installation [F29–F30]. |
| Apple-silicon serving | Current [vLLM installation docs](https://docs.vllm.ai/en/latest/getting_started/installation/) include Apple Silicon via [vLLM Metal](https://docs.vllm.ai/projects/vllm-metal/en/latest/), using MLX integration. [LM Studio](https://lmstudio.ai/docs/developer/openai-compat) documents compatible endpoints; [MLX LM](https://github.com/ml-explore/mlx-lm) targets Apple-silicon language-model operation. | **MEDIUM:** benchmark supported pinned model/backend pairs. A blanket “vLLM cannot run on Apple Silicon” would be outdated. No claim of equal feature maturity, arbitrary-model support, or fit on the owner's unknown hardware [F19–F21]. |
| Conversation-embedding candidates | The official [Qwen3-Embedding-0.6B card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) documents configurable dimensions up to 1024. Google's current [EmbeddingGemma 2 card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2) describes `google/embeddinggemma-2`, modular text/multimodal encoders and a 768-dimensional space with supported truncations. | **MEDIUM:** these are concrete candidates for the local evaluation shortlist, not selected winners. Verify licenses, exact artifacts, serving support, query/document prefixes, normalization, truncated-vector quality, RAM, and chat-specific retrieval. Multimodal experimentation stays in the local P6 lane [F25, F27]. |
| Independent iMessage comparator | [imessage-exporter](https://github.com/ReagentX/imessage-exporter) advertises broad message/media/lifecycle support and declares GPL-3.0. These are maintainer claims, not this audit's validation. | **MEDIUM:** use controlled differential comparisons to discover missing cases. Do not treat a second parser as ground truth or copy source without license/ownership review [F07, F09, F36]. |
| Problem details | [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html) obsoletes RFC 7807. | **HIGH, low-cost correction:** cite the current specification; explicitly adapt HTTP-oriented fields to CLI status/error behavior [F34, F38]. No HTTP API is implied. |
| Forensic preservation baseline | NIST's publication page identifies [NISTIR 8387, Digital Evidence Preservation](https://www.nist.gov/publications/digital-evidence-preservation-considerations-evidence-handlers). | **HIGH** as a primary research starting point; appropriateness for the owner's intended evidentiary use remains UNKNOWN. Investigate preservation/custody beyond checksum manifests without claiming compliance or admissibility [F26]. |

No model leaderboard, vendor throughput claim, price, or historical benchmark is used as a ChatX acceptance result. Model identifiers remain configuration as the owner decided. The meaningful alternative is a measured candidate set and a pinned capability record, not replacing one unverified default with another.

## 4. Decision challenges

The six owner decisions are respected below. These challenges concern consequential interpretations, with costs in both directions.

### DECISION CHALLENGE DC1 — Decisions 3 and 6: case layout versus the forensic promise

**Argument:** the case layout names a DB, attachments, exports, logs, and manifest, but does not require immutable acquisition artifacts or complete custody (§3.5, §3.10; F26). Permit an explicit source-preservation area or equivalent source-bound retention contract.

**Cost if challenged unnecessarily:** extra storage, key/backup complexity, and a heavier personal workflow. **Cost if left too weak:** a portable bundle cannot independently establish its source lineage or completeness. **Evidence to settle:** owner-defined audience/claim, expected source-retention obligations, and a clean independent export/restore/verification exercise.

### DECISION CHALLENGE DC2 — Decision 3: unconditional commitment before target-scale evidence

**Argument:** retain SQLite/FTS5/sqlite-vec as the starting choice, but make the target workload and migration envelope an explicit acceptance condition rather than assuming dNh schema precedent proves them (F24–F25, F37).

**Cost of an unnecessary change:** migration work, service complexity, and damage to the local single-user goal. **Cost of refusing to reconsider after contrary evidence:** unacceptable latency, rebuild/disk failure, or fragile recovery. **Evidence to settle:** pinned-runtime benchmark at the actual corpus/space sizes, filtered/unfiltered query mix, concurrent workloads, and verified restore. No evidence in this pack currently requires replacement.

### DECISION CHALLENGE DC3 — Decision 4: “one interface” must not require false capability equivalence

**Argument:** retain two adapters, but allow completion and embedding capabilities and typed outcomes to differ (§3.6; F19). A uniform happy-path signature is not a complete protocol.

**Cost of excessive abstraction:** more types/configuration and unnecessary framework work. **Cost of flattening differences:** unsupported requests, misclassified refusals, missing embedding routes, or silent fallback. **Evidence to settle:** a small conformance matrix against the selected local server and configured Claude model, using synthetic inputs, original-schema validation, and terminal error cases.

### DECISION CHALLENGE DC4 — Decision 2: editable path as the sole reproducibility mechanism

**Argument:** retain `~/code/chatstack/` and dNh's path dependency for development, but require immutable paired source identities or a release artifact for reproducible consumption (§3.2, §9; F29).

**Cost of overcorrecting:** release overhead and slower shared development. **Cost of accepting only mutable paths:** dNh revision/lock identity no longer determines extraction behavior. **Evidence to settle:** clean two-checkout and installed-consumer builds with recorded core identity, including reconstruction of an older case.

### DECISION CHALLENGE DC5 — Retained policy in §3.7/§3.9: “cloud-safe” coarse attributes

This challenges a design policy rather than one of the six structural choices. **Argument:** the supplied taxonomy intentionally preserves sensitive categories; passing direct-identifier recall does not decide whether that disclosure is acceptable (F05, F18).

**Cost of overly restrictive disclosure:** lower cloud utility or more local computation. **Cost of overly permissive disclosure:** intimate attribute/linkage exposure despite a “passing” PII gate. **Evidence to settle:** an owner-approved category policy, representative payload review, and measured residual/linkage risk with explicit uncertainty. Until settled, cloud eligibility is not established.

**No challenge** to decision 1's shared core or decision 5's design-as-intent rule. Both directly address duplication and contradictory legacy documentation.

## 5. What the design gets right

- Shared extraction with a network/LLM/storage-independent core matches the complementary source implementations (§3.2–3.3, §8).
- Native IDs, strict canonical models, generated JSON Schema, explicit provenance, and source uncertainty questions are the right direction (§3.4, §5, §10).
- One local case store with disk CAS reduces hand-off and operational complexity without requiring a service (§3.5, §4).
- Explicit requested/observed model identity, UNKNOWN, configuration-based IDs, structured validation, and protected invalid-output handling are valuable requirements (§3.6).
- Replacing token ratios with labelled evaluation, whole-run refusal, stronger tokens, and local defaults addresses real weaknesses (§3.7).
- Evidence-linked hybrid retrieval and later opt-in analysis are better scoped than retaining unvalidated graph/psychology machinery (§3.10–3.11).
- Removing fake decryption, unsupported differential privacy, and fixed performance claims avoids carrying forward unearned guarantees (§3.13–3.14, §7).

Preserve these decisions while repairing their acceptance contracts; the findings do not justify restoring the old collection of loosely connected stages.

## 6. Open questions for the owner

Only decisions that change implementation are listed. They are not requests to reconfirm already accepted architecture.

1. What must “forensic” support: personal reproducible analysis, independent technical hand-off, or an external evidentiary process with defined custody/attestation requirements? Must originals travel with a case?
2. May canonical records retain unknown/ambiguous historical time, or must affected imports stop until the owner supplies a timezone/interpretation? How should genuinely undated transcripts behave?
3. Which platform/direction/content-kind combinations must dNh consume, and is any loss allowed? Must historical skipped rows be recovered during initial cutover?
4. Should overlapping device/backup/export imports automatically merge logical messages, or preserve source observations and propose duplicate groups? Is complete edit/reaction history required alongside effective state?
5. Does lack of representative local real-data evaluation prohibit cloud use? Which sensitive attribute categories, if any, may leave the device after direct-identifier removal?
6. What local attacker, sync, backup, key recovery, and retention model should default case placement support? What is the acceptable workflow for redacted versus full-evidence exports?
7. What hardware, corpus/chunk/space counts, latency, disk, and spend envelope should acceptance target? Which languages/source versions are mandatory initially?
8. What license and distribution scope are intended for the shared core, and what immutable consumer identity is acceptable alongside the editable development path?
9. Should contact queries select authored messages, conversations containing that participant, or bounded surrounding context? Which time/label filters and chronology guarantees are essential?
10. What uses and evidence language are acceptable for relationship hypotheses, and must owners be able to annotate, correct, suppress, and delete them before export?

## 7. Verification log

### 7.1 Access and method

`PROMPT-master.md` was read before the design. The complete design and wrapper prompt were then read. All three evidence documents were read by the primary reviewer; truncated tool displays were supplemented where needed. Findings were derived from source blocks/design, not accepted solely from their inherited grades.

The primary reviewer and three parallel reviewers inspected the following **complete fenced source blocks in aggregate**. This is a team reading ledger, not a claim that the primary reviewer personally reread every specialist block. Directory prefixes plus filenames below identify exact bundle paths.

| Bundle / prefix | Complete files read |
|---|---|
| `chatx:` | `pyproject.toml`; `schemas/message.schema.json`; `schemas/chunk.schema.json`; `config/labels.yml`; `config/arch-gates.yml` |
| `chatx:src/chatx/schemas/` | `message.py`, `validator.py` |
| `chatx:src/chatx/imessage/` | `extract.py`, `db.py`, `backup.py`, `time.py`, `body_normalize.py`, `attachments.py`, `report.py` |
| `chatx:src/chatx/instagram/` | `extract.py` |
| `chatx:src/chatx/pdf_ingest/` | `reader.py` |
| `chatx:src/chatx/identity/` | `normalize.py` |
| `chatx:src/chatx/redaction/` | `policy_shield.py`, `patterns.py` |
| `chatx:src/chatx/transformers/` | `chunker.py` |
| `chatx:src/chatx/enrichment/` | `enricher.py`, `ollama_client.py`, `multi_pass_pipeline.py` |
| `chatx:src/chatx/indexing/` | `vector_store.py` |
| `chatx:src/chatx/storage/` | `base.py`, `psychology_relationship_mapper.py` |
| `chatx:src/chatx/utils/` | `json_output.py`, `run_report.py` |
| `dnh:` | `pyproject.toml`; `src/dnh_crm/idempotency.py`; `tests/unit/test_imessage_attributed_body.py` |
| `dnh:src/dnh_crm/ingest/` | `imessage.py`, `imessage_mapper.py`, `imessage_source.py`, `imessage_attributed_body.py`, `normalizer.py`, `dedupe.py`, `whatsapp_export.py`, `email_eml.py` |
| `dnh:src/dnh_crm/services/` | `ingest_runner.py` |
| `dnh:src/dnh_crm/store/` | `migrations.py` |

**Excerpt coverage:** ChatX `src/chatx/cli/main.py`, including 210–440, 732–968, and the complete iMessage pull function around 974–1315, plus targeted call-site searches; dNh `src/dnh_crm/events.py`, covering relevant event types, channels/directions/actors, external/payload models, media model, and complete envelope validators. Other bundle sections were searched for file boundaries, imports, names, and relevant references without a claim of full-file reading.

The full ChatX filtered inventory was read. The dNh inventory's relevant source/test/config/probe regions were inspected and its full text searched, but its thousands of governance/proof entries were not all read line by line. No absent body was reconstructed from an inventory name.

### 7.2 Commands and verification performed

Archive listing/member reading/extraction used `unzip -l`, `unzip -p`, and `unzip -q`. Static discovery and reading used `rg`, `rg --files`, `cat`, `sed -n`, `awk`, and `nl -ba`. These commands selected bundled text and counted source-relative lines. `sha256sum` identified the supplied ZIP bytes. Output-only work used document patches, text/structure checks, word counts, and artifact delivery.

No repository program, import, test suite, build, benchmark, model inference, database query, source probe, package installation, or external project checkout was executed. No source file was modified. Timestamp, sampling, score, and vector-size examples are explicitly static derivations, not executed tests.

Three bounded independent consolidation reviews checked the draft's extraction/schema, privacy/statistics, and storage/provider/packaging sections. Corrections included the full multi-pass filename, precise numbered-contract/question citations, whole-conversation contact scope, and privacy preflight sequencing. Final document checks cover required sections, unique finding/target IDs, cited bundle paths/line bounds, and research-to-finding references. Such checks validate the documents, not the application.

External research used primary official documentation, project repositories/model cards, and a NIST publication page solely for scope 15. URLs are provided beside claims. Historical claims and vendor benchmark numbers were not promoted into ChatX measurements. The NIST publication page was inspected; a full standards-compliance or legal-admissibility review was not performed.

**Elapsed review window:** approximately 2026-10-20 18:44–19:37 UTC, about 53 minutes through document finalization, with three parallel source reviewers. This is elapsed session time, not a claim of equivalent human working hours or multi-hour runtime testing.

### 7.3 Important UNKNOWNs

- Actual OS/device versions, machine/RAM, TCC/permissions, live data, database integrity, SQLite/FTS/vec availability, linked-runtime fixes, uv installation, lock resolution, CI runs, builds, tests, and performance.
- Real typedstream layout frequencies and full-blob recovery; actual source schema evolution; reaction helper behavior; backup/media/HEIC/transcription helper behavior beyond the supplied code; malformed-input prevalence.
- ChatX's unbundled reaction, alternative extraction, embedding/indexing pipeline, multi-vector implementation, media helpers, manifest implementation, and listed test/fixture bodies.
- dNh's unbundled thread resolver, canonical serializer helper, event repository/ingest service, retrieval workers/repositories, backup/restore implementation, BlueBubbles path, real probe, and WhatsApp/email/source tests.
- Original legacy documentation and workflow bodies; full commit identities, working-tree state, source ownership/authority, and reproducibility of a build from the abbreviated bundle commit declarations.
- Real PII precision/recall, second-opinion sensitivity, residual linkage/attribute leakage, model behavior, provider account access/usage/cost, enrichment accuracy, retrieval relevance, and interpretation validity.
- Actual key/ACL/encryption, indexing/sync/backup, telemetry, local-server forwarding, crash/swap, or operational security exposure.

### 7.4 Unverified impressions

**None are presented as findings without a cited basis.** Predicted incidents, corpus frequency, achievable performance, a “best” model/NER engine, and external evidentiary acceptance remain PLAUSIBLE consequences or explicit UNKNOWNs. This report does not claim a demonstrated exploit, reproduced data loss, passing test, or validated psychological conclusion.

Companion deliverable: `research-targets-chatgpt-web.md`, with 55 bounded research targets linked to these findings and phases.

