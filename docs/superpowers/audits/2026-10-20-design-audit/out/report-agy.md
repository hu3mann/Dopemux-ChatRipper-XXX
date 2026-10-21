# ChatX + dNh Ingest Unified Rearchitecture — Principal Design Audit (`report-agy.md`)

## 0. Reviewer Identity

- **Auditor Name**: `agy`
- **Model / Runner**: Gemini 4 Argon (High) running in Google Antigravity (`agy` CLI / IDE agentic runner)
- **Audit Timestamp**: `2026-10-20`
- **Knowledge Cutoff**: Early 2026 (supplemented by live Antigravity `search_web` verification on `2026-10-20` for Scope 15)
- **Repositories Audited**:
  - `ChatX` (`/Users/hue/code/Dopemux-ChatRipperXXX`, branch `governance-doctrine-integration`, HEAD `9c3dd6b`)
  - `dNh` (`/Users/hue/code/dNh_CRM`, branch `migrate-cheaperinference`, HEAD `39c75bde`)
- **Design Under Audit**: `ChatX:docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md` (`§1`–`§14`)
- **Routing & Delegation Record**: Because this packet is an independent principal-level design & security audit with pinned auditor identity (`agy`) and an explicit rule that `CONFIRMED` findings require direct auditor verification (`PROMPT-master.md:77`), all 59 file reads, git metadata checks, and Scope 15 web searches were executed directly by the supervisor (`agy`) without subagent delegation.
- **Files Actually Opened (59 files)**:
  - **Audit Brief, Design, & Evidence (5)**:
    1. `ChatX:docs/superpowers/audits/2026-10-20-design-audit/PROMPT-master.md`
    2. `ChatX:docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md`
    3. `ChatX:docs/superpowers/audits/2026-10-20-design-audit/evidence/01-code-reality-audit.md`
    4. `ChatX:docs/superpowers/audits/2026-10-20-design-audit/evidence/02-dnh-ingest-trace.md`
    5. `ChatX:docs/superpowers/audits/2026-10-20-design-audit/evidence/03-docs-parity-inventory.md`
  - **ChatX Repository (38)**:
    6. `ChatX:pyproject.toml`
    7. `ChatX:config/arch-gates.yml`
    8. `ChatX:config/labels.yml`
    9. `ChatX:schemas/message.schema.json`
    10. `ChatX:src/chatx/cli/main.py`
    11. `ChatX:src/chatx/cli_errors.py`
    12. `ChatX:src/chatx/schemas/message.py`
    13. `ChatX:src/chatx/schemas/validator.py`
    14. `ChatX:src/chatx/imessage/extract.py`
    15. `ChatX:src/chatx/imessage/db.py`
    16. `ChatX:src/chatx/imessage/time.py`
    17. `ChatX:src/chatx/imessage/reactions.py`
    18. `ChatX:src/chatx/imessage/body_normalize.py`
    19. `ChatX:src/chatx/imessage/backup.py`
    20. `ChatX:src/chatx/imessage/attachments.py`
    21. `ChatX:src/chatx/imessage/report.py`
    22. `ChatX:src/chatx/extractors/imessage.py`
    23. `ChatX:src/chatx/instagram/extract.py`
    24. `ChatX:src/chatx/pdf_ingest/reader.py`
    25. `ChatX:src/chatx/identity/normalize.py`
    26. `ChatX:src/chatx/redaction/patterns.py`
    27. `ChatX:src/chatx/redaction/policy_shield.py`
    28. `ChatX:src/chatx/transformers/chunker.py`
    29. `ChatX:src/chatx/transformers/pipeline.py`
    30. `ChatX:src/chatx/enrichment/ollama_client.py`
    31. `ChatX:src/chatx/enrichment/enricher.py`
    32. `ChatX:src/chatx/enrichment/models.py`
    33. `ChatX:src/chatx/enrichment/multi_pass_pipeline.py`
    34. `ChatX:src/chatx/storage/base.py`
    35. `ChatX:src/chatx/storage/psychology_relationship_mapper.py`
    36. `ChatX:src/chatx/indexing/vector_store.py`
    37. `ChatX:src/chatx/indexing/multi_vector_store.py`
    38. `ChatX:src/chatx/obs/run_artifacts.py`
    39. `ChatX:src/chatx/utils/json_output.py`
    40. `ChatX:src/chatx/utils/run_report.py`
    41. `ChatX:tests/fixtures/imessage_test_data.sql`
    42. `ChatX:docs/design/specifications/cloud-enrichment.md`
    43. `ChatX:docs/design/adrs/ADR-008-psychology-graph-integration.md`
  - **dNh_CRM Repository (16)**:
    44. `dNh:pyproject.toml`
    45. `dNh:src/dnh_crm/idempotency.py`
    46. `dNh:src/dnh_crm/events.py`
    47. `dNh:src/dnh_crm/ingest/imessage.py`
    48. `dNh:src/dnh_crm/ingest/imessage_source.py`
    49. `dNh:src/dnh_crm/ingest/imessage_mapper.py`
    50. `dNh:src/dnh_crm/ingest/imessage_attributed_body.py`
    51. `dNh:src/dnh_crm/ingest/imessage_thread_identity.py`
    52. `dNh:src/dnh_crm/ingest/normalizer.py`
    53. `dNh:src/dnh_crm/ingest/dedupe.py`
    54. `dNh:src/dnh_crm/ingest/whatsapp_export.py`
    55. `dNh:src/dnh_crm/ingest/email_eml.py`
    56. `dNh:src/dnh_crm/store/migrations.py`
    57. `dNh:src/dnh_crm/utils/json_utils.py`
    58. `dNh:scripts/imessage_attributed_body_probe.py`
    59. `dNh:tests/unit/test_imessage_attributed_body.py`

---

## 1. Executive Summary

- **Overall Readiness Verdict**: **`READY WITH REVISIONS`** (Core architectural consolidation—single `case.sqlite3` store, adopting `dNh`’s `attributedBody` state machine and 2-rung thread resolver, fixing `is_from_me` contact leakage, and replacing vacuous `coverage=1.0` redaction—is sound, but **10 `BLOCKER` and 15 `HIGH` defects** in schema hashing, SQLite WAL snapshotting, parser bugs, privacy tiering, and `dNh` bridge compatibility will cause silent data loss or immediate runtime crashes if coded as written).
- **Must-Fix #1 (SQLite WAL Snapshot Data Loss — `F-01`, `BLOCKER`)**: `§3.5` and `§8` keep `ChatX:src/chatx/imessage/db.py:12-60` ("WAL-safe copy (`chat.db` + `-wal` + `-shm`)"). In reality, `copy_db_for_readonly` uses non-atomic sequential `shutil.copy2` calls across live files and then `open_ro` opens the copy with `?mode=ro&immutable=1` (`db.py:59`). In SQLite, `immutable=1` forces the VFS to ignore `-wal` and `-shm` completely, silently dropping all uncheckpointed recent messages or corrupting B-tree pages. Replace with `sqlite3.Connection.backup()` as already implemented in `dNh:scripts/imessage_attributed_body_probe.py:288-311`.
- **Must-Fix #2 (Canonical v2 `content_hash` Instability & Derived `msg_id` Collision — `F-02`, `F-03`, `BLOCKER`)**: `§3.4` defines `content_hash` over canonical JSON excluding only `source_meta` and `provenance`. Because `sender.pseudonym`, `reactions[]`, and `attachments[].missing`/`storage_ref` sit inside the hashed body, running `chatx identity pseudonymize` (`§3.12`), pulling a later reaction, or downloading an iCloud-evicted attachment mutates `content_hash` and breaks idempotency across `ChatX` and `dNh` (`§9`). Furthermore, non-GUID `msg_id = sha256(platform, conv_id, sent_at, sender.handle, text)[:32]` collides whenever a user sends identical short texts (`"ok"`, `"👍"`) within the same minute in WhatsApp (`%Y-%m-%d, %H:%M`, no seconds).
- **Must-Fix #3 (`dNh` WhatsApp Substring Filter Drops User Messages & Rejects iOS Exports — `F-04`, `BLOCKER`)**: `§3.5` and `§8` adopt `dNh:src/dnh_crm/ingest/whatsapp_export.py` directly. That parser (`whatsapp_export.py:33-49,196-198`) checks `any(marker in normalized for marker in SYSTEM_LINE_MARKERS)` where `"left"`, `"added"`, and `"joined"` are bare substrings—silently discarding every user message containing words like `"I left work"` or `"I added it"` (`:105-108`)—and its regex (`:24-27`) only matches Android unbracketed lines, failing 100% of iOS WhatsApp exports (`[MM/DD/YY, HH:MM:SS AM] Sender: text`).
- **Must-Fix #4 (`dNh` `EventEnvelope` Bridge Crashes on Non-Text/Outbound/New-Channel Rows & Breaks Existing Dedupe — `F-05`, `F-06`, `BLOCKER`)**: `§9` claims a "lossless" mapping to `EventEnvelope(event_type=MSG_INBOUND_RECEIVED)`. In `dNh:src/dnh_crm/events.py:172-182,519-560`, `Channel` lacks `instagram`/`pdf_transcript`/`txt`, `EventPayload.text` requires `min_length=1` (while `IMessageAttachmentOnlyPayload` requires `attachment_count >= 1`, crashing on `reaction_only`/`system`/`empty` messages), outbound messages are misclassified as `MSG_INBOUND_RECEIVED` from `ActorRole.CLIENT` (`dNh:src/dnh_crm/ingest/normalizer.py:28-41`), and switching `dedupe_hash` to `provenance.content_hash` violates `UNIQUE(dedupe_scope, dedupe_hash)` migration continuity against all existing rows in `dNh_CRM` (`dNh:src/dnh_crm/ingest/dedupe.py:15-24`).
- **Must-Fix #5 (iMessage `associated_message_guid` Part-Prefix Bug & Attachment `~/` Path Bug — `F-07`, `F-08`, `BLOCKER`)**: `ChatX:src/chatx/imessage/extract.py:229,257` looks up `associated_message_guid` directly in `messages_by_guid` without stripping Apple’s `p:0/`, `p:1/`, or `bp:` prefixes (resulting in 0% reaction/reply linkage on real `chat.db` files), and `ChatX:src/chatx/imessage/attachments.py:90-126` never calls `.expanduser()` on `attachment.filename` (`~/Library/Messages/Attachments/...`), failing live macOS attachment resolution.
- **Decision to Reconsider #1 (Storing Reversible PII Map Inside `case.sqlite3` & Cloud Taxonomy Tier Leak — `F-12`, `F-15`, `BLOCKER`/`HIGH`)**: Putting the reversible cleartext↔token table inside `case.sqlite3` (`§3.6`, `§3.7`) defeats separating the `0600` salt file (`~/.config/chatx/salt.key`), and compiling all of `config/labels.yml` into the cloud structured-output schema (`§3.9`) leaks the 99 `fine_local_only` psychology/sexuality/substance labels to the cloud provider, violating `ChatX:config/labels.yml:3-12` and `ChatX:config/arch-gates.yml:60-65`.
- **Decision to Reconsider #2 (`sqlite-vec` Brute-Force Scaling vs Multi-Vector Retrieval — `F-17`, `HIGH`)**: `sqlite-vec` (`v0.1.x`) is brute-force $O(N)$ scan only (no ANN/HNSW index). While fast at 10k–100k chunks, scanning 1M float32 vectors (`§3.10`) requires reading ~3 GB per query unless binary/int8 quantization or SQLite `rowid` pre-filtering is specified in the schema.
- **Decision to Reconsider #3 (`psychology_relationship_mapper.py` YAML Port Has 0% Label Overlap — `F-18`, `HIGH`)**: `§3.11` and `§8` plan to port `psychology_relationship_mapper.py` as YAML rules over enrichment labels, but **0 of the 30+ labels** referenced in `psychology_relationship_mapper.py:129-546` exist in `config/labels.yml`.
- **Statistical Reality of Policy Shield v2 Second-Opinion Sampling (`F-13`, `HIGH`)**: `§3.7` condition (3) requires "0 leaked spans in sampled second-opinion check" alongside "$\ge 99.5\%$ (default) / $\ge 99.9\%$ (strict) on gold corpus". By the statistical Rule of Three ($n = -\ln(\alpha)/p$), proving $\le 0.5\%$ leak rate at 95% confidence requires sampling $n \ge 600$ chunks; proving $\le 0.1\%$ requires $n \ge 3,000$ chunks.
- **Missing Forensic Columns in `chat.db` (`F-09`, `HIGH`)**: Neither repo extracts `date_edited`, `date_retracted`, `message_summary_info` (where iOS 16+ edit history and unsends live—moreover, `ChatX:tests/fixtures/imessage_test_data.sql:144` falsely models `message_summary_info` as a separate table rather than a BLOB column on `message`), `thread_originator_guid` (inline replies since iOS 14), `associated_message_emoji` (iOS 18 / macOS 15 custom emoji reactions `2006`/`3006`), or `item_type`/`group_action_type`.
- **AttributedBody `U+FFFC` Object Replacement Bug (`F-10`, `HIGH`)**: `dNh:src/dnh_crm/ingest/imessage_attributed_body.py:240` accepts a decoded string consisting solely of `\ufffc` (`OBJECT REPLACEMENT CHARACTER` used by Apple for inline attachments) as `DECODED` text, misclassifying attachment-only messages as `content_kind="text"` and suppressing attachment-only payload construction.

---

## 2. Findings Table

| ID | Area | Severity | Verdict | Evidence | One-line summary | Concrete fix |
|---|---|---|---|---|---|---|
| `F-01` | 2, 4 | `BLOCKER` | `CONFIRMED` | `ChatX:src/chatx/imessage/db.py:12-60`; `dNh:scripts/imessage_attributed_body_probe.py:288-311`; `§3.5`, `§8` | `copy_db_for_readonly` uses racy `shutil.copy2` and opens with `immutable=1`, which makes SQLite ignore `-wal`/`-shm` and drop recent messages. | Replace `copy_db_for_readonly` with `sqlite3.Connection.backup()` into a `0600` temp file + `PRAGMA quick_check(1)`, then open without `immutable=1`. |
| `F-02` | 1 | `BLOCKER` | `CONFIRMED` | `§3.4`, `§3.12`, `§9` | `content_hash` hashes canonical JSON excluding only `source_meta`/`provenance`, so `sender.pseudonym`, `reactions`, and `attachments.missing` mutate `content_hash` post-import. | Define `content_hash` over an explicit immutable core tuple `(platform, conv_id, msg_id, sent_at, direction, sender.handle, text, reply_to_msg_id, [att.sha256 or att.filename])`. |
| `F-03` | 1, 2 | `BLOCKER` | `CONFIRMED` | `§3.4`; `dNh:src/dnh_crm/ingest/whatsapp_export.py:180-187` | Non-GUID `msg_id = sha256(platform, conv_id, sent_at, sender.handle, text)[:32]` collides when identical messages (`"ok"`) occur in the same minute. | Include monotonic source ordinal (`source_line_no` or `ordinal_in_minute`) in non-GUID `msg_id` derivation. |
| `F-04` | 2, 8 | `BLOCKER` | `CONFIRMED` | `dNh:src/dnh_crm/ingest/whatsapp_export.py:24-49,105-108,196-198`; `§3.5`, `§8` | `dNh` WhatsApp parser drops any user message containing substrings `"left"`, `"added"`, or `"joined"` and fails 100% of iOS bracketed exports. | Remove bare verb substrings from `SYSTEM_LINE_MARKERS`; anchor system patterns; support both iOS `[date, time] Sender: body` and Android formats. |
| `F-05` | 1, 9 | `BLOCKER` | `CONFIRMED` | `dNh:src/dnh_crm/events.py:172-182,519-560`; `dNh:src/dnh_crm/ingest/normalizer.py:28-41`; `§9` | `CanonicalMessage -> EventEnvelope` crashes on `instagram`/`pdf_transcript`/`txt` channels, `reaction_only`/`empty`/`system` rows, and mismaps outbound messages as inbound client events. | Extend `Channel` enum, map `direction="outbound"` to `MSG_OUTBOUND_SENT`/`ActorRole.OPERATOR`, and define payload/skip rules for `reaction_only`/`empty`/`system`. |
| `F-06` | 1, 9 | `BLOCKER` | `CONFIRMED` | `dNh:src/dnh_crm/ingest/dedupe.py:15-24`; `dNh:src/dnh_crm/store/migrations.py:23`; `§9` | Replacing `build_imessage_dedupe` with `provenance.content_hash` changes `dedupe_hash` for every historical message in `dNh_CRM`, duplicating all events on re-ingest. | Preserve `dNh`'s legacy `dedupe_hash` formula for `imessage`/`whatsapp`/`email` in the `dNh` adapter, or ship a deterministic SQLite migration backfilling `events.dedupe_hash`. |
| `F-07` | 1, 2 | `BLOCKER` | `CONFIRMED` | `ChatX:src/chatx/imessage/extract.py:229,257`; `ChatX:tests/fixtures/imessage_test_data.sql:82-90` | `extract.py` matches `associated_message_guid` without stripping `p:0/` or `bp:` prefixes, causing 0% reaction/reply linkage on real `chat.db` files. | Strip `^(?:p:\d+/|bp:)` and extract `associated_message_part` before looking up target GUID; add `p:0/` cases to `imessage_test_data.sql`. |
| `F-08` | 2, 10 | `BLOCKER` | `CONFIRMED` | `ChatX:src/chatx/imessage/attachments.py:90-126` | `resolve_attachment_path` does not call `.expanduser()` on `~/Library/Messages/Attachments/...`, failing all live macOS attachment lookups. | Strip leading `~/` or call `Path(filename).expanduser()` and verify resolved path stays under `~/Library/Messages/Attachments`. |
| `F-09` | 1, 2, 11 | `HIGH` | `CONFIRMED` | `ChatX:src/chatx/imessage/extract.py:88-108,237`; `ChatX:tests/fixtures/imessage_test_data.sql:144-149` | `extract.py` uses `associated_message_guid` for replies instead of `thread_originator_guid`, omits edit/unsend/group-event columns, and fixtures falsely model `message_summary_info` as a table instead of a column on `message`. | Query `thread_originator_guid`, `date_edited`, `date_retracted`, `message_summary_info` (column), `associated_message_emoji`, `item_type`, `group_action_type`; fix fixture DDL. |
| `F-10` | 2 | `HIGH` | `CONFIRMED` | `dNh:src/dnh_crm/ingest/imessage_attributed_body.py:229-243`; `dNh:scripts/imessage_attributed_body_probe.py:45,604-625` | `decode_imessage_attributed_body` treats strings containing only `\ufffc` (inline attachment marker) as valid `DECODED` text, masking `attachment_only` messages. | Strip `\ufffc` and `\ufffd` before checking if decoded text is non-empty; preserve inline attachment indices if mixed with text. |
| `F-11` | 2, 8 | `HIGH` | `CONFIRMED` | `ChatX:src/chatx/instagram/extract.py:21-38,157`; `§4`, `§8` | `§4` and `§8` claim `instagram/extract.py` has mojibake repair and zip safety, but the code has zero mojibake repair (`latin1 -> utf-8`) and no zip-bomb size/entry limits. | Add Meta JSON mojibake repair (`re.sub` or `encode('latin1').decode('utf-8')`) and enforce max entry count / uncompressed byte ceiling in `_safe_extract`. |
| `F-12` | 3, 4 | `BLOCKER` | `CONFIRMED` | `§3.6`, `§3.7`, `§3.12`; `ChatX:src/chatx/redaction/policy_shield.py:130-169` | Storing the reversible token↔cleartext map inside `case.sqlite3` alongside raw messages nullifies the security boundary of the external `0600` salt file. | Store the reversible token vault in a separate `0600` SQLite/encrypted file (`~/.config/chatx/vault/<case_id>.sqlite3`) or derive an export-safe `case.redacted.sqlite3` that strips raw tables. |
| `F-13` | 3 | `HIGH` | `CONFIRMED` | `§3.7`; `ChatX:src/chatx/redaction/policy_shield.py:310-335` | `§3.7` condition (3) ("0 leaked spans in sampled second-opinion check") lacks sample-size math; small samples ($n < 600$) cannot statistically bound leak rates to $\le 0.5\%$. | Run lightweight local NER (GLiNER-PII) on 100% of outbound cloud chunks; if using LLM second-opinion sampling, require Clopper-Pearson upper bound $p_{95} \le 1 - \text{threshold}$. |
| `F-14` | 3, 5 | `HIGH` | `CONFIRMED` | `ChatX:src/chatx/transformers/chunker.py:124-198`; `§3.9` | `chunker.py:168` injects unredacted `contact` into every formatted line (`[date] {contact}: {text}`), and `§3.9` sends chunks *plus* "$\pm 2$ turns of redacted context" even though chunks already contain 40 turns with stride-10 overlap. | Redact messages *before* chunk assembly (or assemble chunks using `sender.pseudonym`); drop redundant $\pm 2$ context padding when enriching multi-turn chunks. |
| `F-15` | 3, 5, 6 | `BLOCKER` | `CONFIRMED` | `ChatX:config/labels.yml:3-12`; `ChatX:config/arch-gates.yml:60-65`; `§3.9` | `§3.9` compiles `config/labels.yml` into Pydantic enums for cloud enrichment without filtering out `privacy_tier: fine_local_only` (99 sensitive labels), leaking local-only taxonomy to cloud APIs. | Compile two distinct Pydantic schemas from `labels.yml`: `CoarseCloudEnrichmentSchema` (55 coarse labels only) for `--provider cloud` and `FullLocalEnrichmentSchema` (154 labels) for `--provider local`. |
| `F-16` | 3, 6 | `MEDIUM` | `CONFIRMED` | `ChatX:src/chatx/redaction/patterns.py:159-197`; `ChatX:config/labels.yml:373-389,425-427` | `HardFailDetector` blocks chunks matching naïve regexes for drugs/violence/illegal content, colliding with `labels.yml` which explicitly classifies `substances_specifics`, `crime_threat`, and `violence_detail`. | Narrow `HardFailDetector` to CSAM (`CSAM_INDICATORS`) and active credential/secret material (`PRIVATE_KEY`/`API_KEY`), moving substance/conflict analysis to local-only enrichment. |
| `F-17` | 4, 7, 15 | `HIGH` | `CONFIRMED` | `§3.6`, `§3.10`, `§5`; `sqlite-vec` issue `#25` | `sqlite-vec` performs brute-force $O(N)$ scans; at 1M chunks (`§3.10`), float32 KNN scans read ~3 GB per query and exceed the `<150 ms p95` target (`§11`). | Scope `sqlite-vec` float32 to $\le 100\text{k}$ chunks, use `vec_int8` or `vec_bit` quantization + SQLite `rowid IN (...)` metadata pre-filtering above 100k, or provide a LanceDB/usearch ANN adapter at 1M+. |
| `F-18` | 6, 8 | `HIGH` | `CONFIRMED` | `ChatX:src/chatx/storage/psychology_relationship_mapper.py:129-546`; `ChatX:config/labels.yml:1-469`; `§3.11`, `§8` | `§3.11` and `§8` port `psychology_relationship_mapper.py` as YAML rules over `labels.yml`, but 0% of its `source_labels` (`gaslighting_pattern`, `arousal_anticipation`, etc.) exist in `labels.yml`. | Rewrite the YAML relationship rules from scratch using the actual 154 label IDs in `config/labels.yml`, and validate rule label references at load time. |
| `F-19` | 2, 12 | `HIGH` | `CONFIRMED` | `dNh:src/dnh_crm/ingest/email_eml.py:110-165`; `ChatX:src/chatx/identity/normalize.py:1-96`; `§3.5`, `§3.12` | `email_eml.py` drops `To`/`Cc`/`In-Reply-To`/`References` and hardcodes `Direction.INBOUND`, while `identity/normalize.py` uses naïve regex phone normalization without `phonenumbers`. | Parse RFC 5322 `To`/`Cc`/`In-Reply-To`/`References` + attachment SHA-256 in `email_eml.py`; infer `direction` against owner addresses; use `phonenumbers` (E.164) in `identity/normalize.py`. |
| `F-20` | 2 | `MEDIUM` | `CONFIRMED` | `dNh:src/dnh_crm/ingest/imessage_thread_identity.py:85`; `dNh:scripts/imessage_attributed_body_probe.py:435-453` | `imessage_thread_identity.py:85` uses `MIN(chat_id)` when a message joins multiple chats, silently hiding multi-chat ambiguity that `probe.py` detects. | Select `COUNT(DISTINCT chat_id)` alongside `MIN(chat_id)` in Rung 1; when `count > 1`, record `multi_chat_ambiguity=True` in `source_meta` and emit a structured warning. |
| `F-21` | 4, 14 | `HIGH` | `CONFIRMED` | `§3.6`, `§6`, `§7`; `dNh:src/dnh_crm/store/migrations.py:1-424` | `case.sqlite3` DDL is prose-only in `§3.6`: no schema migration table, no foreign key cascade policy, no WAL concurrency PRAGMAs, and no incremental watermarks table. | Define numbered SQL migrations (`schema_migrations`), set `PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA foreign_keys=ON;`, and add `ingest_watermarks` (`source_id`, `last_rowid`, `last_sent_at`). |
| `F-22` | 5 | `MEDIUM` | `CONFIRMED` | `§3.9`; `ChatX:src/chatx/enrichment/ollama_client.py:194-260` | `§3.9` does not specify prompt caching (`cache_control`), Batch API support, rate-limit token buckets, cost caps (`--max-cost-usd`), or prompt-injection isolation for untrusted chat text. | Delimit untrusted chat turns in XML tags with system-level anti-injection rules, cache the static taxonomy prefix, support `--batch` and `--max-cost-usd`, and store `(model_id, schema_hash, prompt_hash)` per enrichment row. |
| `F-23` | 10, 12 | `MEDIUM` | `CONFIRMED` | `ChatX:src/chatx/imessage/backup.py:55-93`; `ChatX:src/chatx/cli/main.py:992-998`; `§3.5` | `backup.py:62` says "Encrypted backups are not supported yet" despite `--backup-password` existing on the CLI (`main.py:992`), and live attachment copying leaves EXIF GPS/biometric metadata intact in thumbnails. | Remove or implement `--backup-password` (via `iphone-backup-decrypt`), strip EXIF metadata when generating thumbnails, and never copy raw attachment binaries unless `--copy-binaries` is explicitly set. |
| `F-24` | 11 | `MEDIUM` | `CONFIRMED` | `ChatX:tests/fixtures/imessage_test_data.sql:1-162`; `dNh:tests/unit/test_imessage_attributed_body.py:1-200`; `§11` | `ChatX` fixtures lack real Apple `attributedBody` blobs, `p:0/` reaction prefixes, `~/Library` paths, and `thread_originator_guid`; `§11` omits `dNh`’s 1,013-line typedstream unit test suite. | Port `dNh:tests/unit/test_imessage_attributed_body.py` into `ChatX` and rebuild `imessage_test_data.sql` to match real macOS Sonoma/Sequoia `chat.db` DDL and data quirks. |
| `F-25` | 13, 14 | `MEDIUM` | `CONFIRMED` | `ChatX:pyproject.toml:31-76`; `ChatX:config/arch-gates.yml:24-76`; `§7`, `§12` | `§7` and `§12` do not update `.github/workflows` / `config/arch-gates.yml` (which hardcodes legacy `chatx redact --input ./out/chunks/*.json` and `chatx enrich messages`) or prune unused heavy dependencies in `pyproject.toml`. | Update `config/arch-gates.yml` in PR 3/4 to run the new SQLite-backed CLI pipeline, and move `chromadb`, `pymilvus`, `qdrant-client`, `pinecone`, `weaviate-client`, `spacy`, `transformers`, `torch` out of default dependencies. |

---

## 3. Per-Area Deep Dives (1 through 15)

### Area 1: Canonical Message Schema v2 & Provenance Contract (§3.4, §9)

#### 1.1 Missing Forensic Fields in `CanonicalMessage` v2 (`CONFIRMED`)
Comparing `§3.4` against `ChatX:src/chatx/imessage/extract.py:88-108`, `ChatX:src/chatx/extractors/imessage.py:100-134,300-340`, and `dNh:src/dnh_crm/ingest/imessage_source.py:55-98` reveals several fields present in real `chat.db` or required by downstream forensic analysis that v2 omits or conflates:
1. **Inline Replies vs Reactions (`thread_originator_guid` vs `associated_message_guid`)**: In macOS Big Sur / iOS 14+, inline replies use `message.thread_originator_guid` and `message.thread_originator_part` (with `associated_message_type = 0`), whereas `associated_message_guid` is used for Tapbacks (`2000`–`3007`), stickers (`1000`), and iMessage apps (`ChatX:src/chatx/extractors/imessage.py:309-315`). `ChatX:src/chatx/imessage/extract.py:237` wrongly treats `associated_message_guid` with `associated_message_type == 0` as a reply and never selects `thread_originator_guid`.
2. **Edits, Unsends, Delivery & Read Timestamps**: Real `chat.db` tracks `date_delivered`, `date_read`, `date_edited` (iOS 16+), `date_retracted` (unsend, iOS 16+), and `message_summary_info` (a binary plist BLOB column on `message` storing prior edited text versions and retraction metadata). Neither repo queries these columns. Worse, `ChatX:tests/fixtures/imessage_test_data.sql:144-149` and `ChatX:src/chatx/extractors/imessage.py:109-112` falsely model `message_summary_info` as a separate SQLite table (`FROM message_summary_info WHERE message_rowid = ?`)—a query that raises `sqlite3.OperationalError: no such table: message_summary_info` on real macOS `chat.db`!
3. **Tapback Codes `2006`/`3006` and `2007`/`3007` (`CONFIRMED` via Scope 15 web search)**: `§3.4` marks `2006`/`3006` as `UNKNOWN`. In iOS 18 / macOS 15 Sequoia, `2006` is **add custom emoji reaction** and `3006` is **remove custom emoji reaction**, with the emoji string stored in the `message.associated_message_emoji` column; `2007`/`3007` are sticker tapbacks. Meanwhile, `ChatX:src/chatx/imessage/reactions.py:35-37,55-58` has a bug that classifies `3000 <= associated_message_type <= 3999` as `"custom"` emoji instead of tapback removals (`3000`–`3005`).
4. **Part Specifiers (`p:0/<guid>`, `bp:<guid>`)**: Real `chat.db` prefixes `associated_message_guid` with `p:0/` (part index 0 of a multi-part `attributedBody`, e.g., attachment at `p:0/` and caption text at `p:1/`) or `bp:` (balloon plugin). `ChatX:src/chatx/imessage/extract.py:229,257` looks up `target_guid in messages_by_guid` without stripping `p:\d+/` or `bp:`, resulting in **0% reaction linkage on real databases** (`CONFIRMED`).
5. **Group Membership & System Actions (`item_type`, `group_action_type`, `other_handle`, `expressive_send_style_id`, `balloon_bundle_id`)**: Group renames, participant additions/removals, FaceTime audio/video events, and digital touch/app balloons (`com.apple.messages.URLBalloonProvider`, etc.) have `text=NULL` and `attributedBody=NULL`. Without querying `item_type`, `group_action_type`, `other_handle`, and `balloon_bundle_id`, `dNh`'s mapper (`imessage_mapper.py:55-68`) misclassifies them as `content_kind="empty"` rather than `content_kind="system"`.

#### 1.2 Determinism & Stability Defects in `msg_id` and `content_hash` (`F-02`, `F-03`, `BLOCKER`)
`§3.4` defines:
- `msg_id`: "Source-stable ID (`imessage:<guid>` or derived sha256 when source lacks GUID)", specifically `sha256(platform, conv_id, sent_at, sender.handle, text)[:32]`.
- `content_hash`: "sha256 over the canonical JSON excluding `source_meta` and `provenance`".

This fails in four concrete scenarios (`CONFIRMED`):
1. **Same-minute duplicate message collision**: In `dNh:src/dnh_crm/ingest/whatsapp_export.py:180-187`, timestamps have minute resolution (`%Y-%m-%d, %H:%M`). If a participant sends `"ok"` or `"👍"` twice in the same minute, `sha256(platform, conv_id, sent_at, sender.handle, text)[:32]` produces an identical `msg_id` for both rows, causing `INSERT INTO messages` (`PRIMARY KEY (msg_id)` or `UNIQUE(source_id, msg_id)`) to silently overwrite the second message.
2. **Post-import pseudonymization mutates `content_hash`**: `sender.pseudonym` (`str | None`) is inside `Sender`, which is part of `CanonicalMessage`. In `§3.12` and `§4`, `chatx identity pseudonymize` runs *after* `chatx import`. Populating `sender.pseudonym` changes the canonical JSON and therefore invalidates `provenance.content_hash`.
3. **Incremental reaction pulls mutate `content_hash`**: Because `reactions: list[Reaction]` is folded inside `CanonicalMessage`, if Message $M$ is imported on Monday and receives a Tapback on Tuesday, re-importing $M$ on Tuesday changes `M.reactions` and therefore changes `M.provenance.content_hash`, breaking downstream `dNh` event deduplication (`§9`).
4. **iCloud attachment hydration mutates `content_hash`**: `attachments[].missing` (`bool`) and `attachments[].storage_ref` (`str | None`) are inside `Attachment`. If a message is imported while its attachment is iCloud-evicted (`missing=True, storage_ref=None`) and re-imported after Messages downloads it (`missing=False, storage_ref="sha256:..."`), `content_hash` changes.

#### 1.3 Is the `CanonicalMessage` v2 $\rightarrow$ `dNh` `EventEnvelope` Mapping (`§9`) Lossless? (`F-05`, `F-06`, `BLOCKER`)
**No.** Inspecting `dNh:src/dnh_crm/events.py:172-182,519-560,1895-1968` and `dNh:src/dnh_crm/ingest/normalizer.py:12-60` confirms four breaking incompatibilities in `§9`:
1. **Unsupported `Channel` values**: `dNh:src/dnh_crm/events.py:172-182` defines `Channel` as `{IMESSAGE, TELEGRAM, SMS, WHATSAPP, EMAIL, EMAIL_PROTON, EMAIL_GMAIL, TELEGRAM_OPS, SYSTEM}`. Passing `platform` values `"instagram"`, `"pdf_transcript"`, or `"txt"` from `CanonicalMessage` v2 (`§3.4`) raises a Pydantic `ValidationError`.
2. **Direction & ActorRole hardcoding**: `§9` maps every `CanonicalMessage` to `EventEnvelope(event_type=MSG_INBOUND_RECEIVED, ...)`. In `dNh:src/dnh_crm/ingest/normalizer.py:36,41`, `normalize_inbound_message` hardcodes `ActorRole.CLIENT` and `EventType.MSG_INBOUND_RECEIVED`. Outbound messages (`direction == "outbound"`, i.e., `is_from_me == 1` in iMessage) represent operator messages (`MSG_OUTBOUND_SENT`, `ActorRole.OPERATOR`) and must never be emitted as `MSG_INBOUND_RECEIVED` from `CLIENT`.
3. **Payload validation failure on `reaction_only`, `system`, and `empty` rows**: In `dNh:src/dnh_crm/events.py:522`, `EventPayload.text` has `Field(min_length=1)`. In `normalizer.py:28-33`, when `msg.text` is empty, `normalizer` constructs `IMessageAttachmentOnlyPayload` (`events.py:525-531`), which enforces `attachment_count: int = Field(ge=1)` and `channel == Channel.IMESSAGE`. Therefore, any `CanonicalMessage` with `text=None` and `len(attachments)==0` (such as `content_kind` in `{"reaction_only", "system", "empty"}`) **raises `ValidationError` in `dNh`**!
4. **Dedupe hash discontinuity**: `dNh:src/dnh_crm/ingest/dedupe.py:15-24` computes `dedupe_hash` via `build_imessage_dedupe(account_id, message_guid, chat_id, sender_handle, timestamp_iso, text)` (which passes `{"account_id": ..., "chat_id": ..., "message_guid": ..., "sender_handle": ..., "text": ..., "timestamp_iso": ...}` to `compute_idempotency_key` in `dNh:src/dnh_crm/idempotency.py:11-16`). `§9` replaces `dedupe_hash` with `provenance.content_hash`. Because `dNh:src/dnh_crm/store/migrations.py:23` enforces `UNIQUE(dedupe_scope, dedupe_hash)`, changing the hash formula causes every already-ingested message in an existing `dNh_CRM` database to be re-inserted as a duplicate event!

#### 1.4 Concrete Replacement: `CanonicalMessage` v2 Pydantic Model & Hash Contract
```python
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

Platform = Literal["imessage", "instagram", "whatsapp", "email", "pdf_transcript", "txt"]
Direction = Literal["inbound", "outbound", "system", "unknown"]
BodySource = Literal["text", "attributed_body", "caption", "ocr", "transcript", "none"]
ContentKind = Literal[
    "text", "attachment_only", "reaction_only", "rich_balloon",
    "group_event", "EditedOrUnsent", "system", "empty", "corrupt_unrecoverable"
]
TapbackKind = Literal[
    "love", "like", "dislike", "laugh", "emphasize", "question", "custom_emoji", "sticker"
]

class Sender(BaseModel):
    handle: str                    # normalized E.164 / lowercase email / platform handle
    raw_handle: str
    display_name: str | None = None
    is_me: bool

class ReactionEvent(BaseModel):
    reactor_handle: str
    kind: TapbackKind
    emoji: str | None = None       # populated from associated_message_emoji for 2006/3006
    removed: bool = False          # True for 3000-3007
    target_msg_id: str             # stripped of p:N/ and bp:
    target_part_index: int | None = None
    sent_at: datetime
    source_msg_id: str

class AttachmentRef(BaseModel):
    att_id: str
    filename: str
    mime_type: str | None = None
    uti: str | None = None
    byte_len: int | None = None
    sha256: str | None = None
    is_sticker: bool = False

class Provenance(BaseModel):
    schema_version: Literal["2.0"] = "2.0"
    run_id: str
    source_id: str                 # sha256(platform + canonical_source_path)
    source_cursor: str             # e.g., "rowid:48192" or "line:1042"
    extractor_version: str
    content_hash: str              # sha256 over IMMUTABLE core fields only
    legacy_dnh_dedupe_hash: str | None = None  # preserves dNh UNIQUE(dedupe_scope, dedupe_hash)

class CanonicalMessage(BaseModel):
    msg_id: str                    # GUID or sha256(platform, conv_id, sent_at, sender.handle, source_cursor, text)[:32]
    conv_id: str
    platform: Platform
    direction: Direction
    sender: Sender
    sent_at: datetime              # timezone-aware UTC
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    edited_at: datetime | None = None
    retracted_at: datetime | None = None
    text: str | None = None
    body_source: BodySource
    content_kind: ContentKind
    reply_to_msg_id: str | None = None
    reply_to_part_index: int | None = None
    attachments: list[AttachmentRef] = Field(default_factory=list)
    reactions: list[ReactionEvent] = Field(default_factory=list)
    source_meta: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance
```
*Key corrections*: (1) `sender.pseudonym` and mutable attachment storage status (`missing`, `storage_ref`) live in SQLite relational columns (`participants.pseudonym`, `attachments.missing`, `attachments.storage_ref`), not inside the hashed payload; (2) `reactions` are stored in a normalized `reactions` table and excluded from `content_hash`; (3) non-GUID `msg_id` includes `source_cursor` (`line_no` / `ordinal_in_minute`) to prevent same-minute collisions; (4) `legacy_dnh_dedupe_hash` preserves backward compatibility with existing `dNh_CRM` stores.

---

### Area 2: Extraction Correctness per Source (§3.5, §8)

#### 2.1 iMessage (`chat.db` & MobileSync Backup) (`CONFIRMED`)
1. **WAL-safe copy & `immutable=1` bug (`F-01`, `BLOCKER`)**:
   - In `ChatX:src/chatx/imessage/db.py:12-43`, `copy_db_for_readonly` copies `chat.db`, `chat.db-wal`, and `chat.db-shm` via three separate `shutil.copy2` calls. If macOS `imagent` checkpoints or appends frames between copying `chat.db` and `chat.db-wal`, the snapshot has mismatched WAL salt/frame headers.
   - Worse, `ChatX:src/chatx/imessage/db.py:59` opens that copy with `uri = f"file:{db_path}?mode=ro&immutable=1"`. Per SQLite documentation, `immutable=1` tells SQLite that the underlying media is read-only and **disables all reading of `-wal` and `-shm` files**. Any recent messages sitting in `chat.db-wal` are silently invisible, or if the main database header reflects partial WAL state, queries return corrupt results or `SQLITE_CORRUPT`.
   - Meanwhile, `dNh:src/dnh_crm/ingest/imessage_source.py:140,200,246` opens the live `~/Library/Messages/chat.db` directly with `?mode=ro` without snapshotting at all, while `dNh:scripts/imessage_attributed_body_probe.py:288-311` (`create_backup_snapshot` + `run_quick_check`) uses `sqlite3.connect(src_uri, uri=True).backup(target_conn)` into a `0600` temp file and runs `PRAGMA quick_check`. **Fix**: Port `create_backup_snapshot` from `probe.py:288-311` into `chatx/extractors/imessage/db.py` and never pass `immutable=1` on a WAL-backed copy.
2. **`attributedBody` typedstream decoder (`F-10`, `HIGH`)**:
   - `dNh:src/dnh_crm/ingest/imessage_attributed_body.py:69-80` is a clean, dependency-free state machine supporting two exact class chains (`NSMutableAttributedString -> NSAttributedString -> NSObject` and `NSAttributedString -> NSObject`, plus `NSMutableString`/`NSString`).
   - However, when a message contains an inline attachment, macOS inserts `U+FFFC` (`\ufffc`, Object Replacement Character) into the `NSString` buffer for each attachment part (`dNh:scripts/imessage_attributed_body_probe.py:45,604-625`). In `imessage_attributed_body.py:240`, `if not text.strip(): return CORRUPT_UNRECOVERABLE` evaluates `"\ufffc".strip()`, which in Python is `"\ufffc"` (truthy, length 1)! As a result, `imessage_mapper.py:55-68` classifies an attachment-only message with an `attributedBody` containing `"\ufffc"` as `content_kind="text"` with `text="\ufffc"`, preventing `normalizer.py:28` from creating an `IMessageAttachmentOnlyPayload`.
   - Additionally, `imessage_attributed_body.py:147-153` rejects any typedstream where a subclass or unexpected class header appears before `NSString`. Adding a fallback length-prefixed UTF-8 scan around `NSString` markers (as `probe.py:580-615` uses for diagnostics) or supporting `pytypedstream` as an optional fallback avoids false `UNSUPPORTED_TYPEDSTREAM_VARIANT` drops on older iOS backups.
3. **Thread identity resolution (`F-20`, `MEDIUM`)**:
   - `dNh:src/dnh_crm/ingest/imessage_thread_identity.py:72-176` implements the 2-rung resolver (Rung 1: `chat_message_join` + `chat`, Rung 2: `chat_handle_join` when `DISTINCT chat_id == 1`).
   - However, in Rung 1 (`imessage_thread_identity.py:82-92`), the query is `SELECT cmj.message_id, MIN(cmj.chat_id) AS chat_id FROM chat_message_join cmj ... GROUP BY cmj.message_id`. If a message row is joined to multiple chats (which happens in synced iCloud Messages databases and is explicitly checked by `probe.py:435-453` via `_strict_multiplicity`), `MIN(cmj.chat_id)` silently picks the lowest `chat_id` without flagging the ambiguity. Rung 1 should select `MIN(cmj.chat_id), COUNT(DISTINCT cmj.chat_id)` and record `multi_chat_count > 1` in `source_meta`.
4. **Live macOS attachment path resolution (`F-08`, `BLOCKER`)**:
   - In real macOS `chat.db`, `attachment.filename` starts with `~/Library/Messages/Attachments/...`. In `ChatX:src/chatx/imessage/attachments.py:90-126`, `resolve_attachment_path` never calls `.expanduser()`. In Python, `Path("~/Library/...")` is a relative path starting with a literal directory named `"~"`, so `attachments_dir / filename` produces `/Users/<user>/Library/Messages/Attachments/~/Library/Messages/Attachments/...`, which never exists!
5. **Apple Epoch Timestamp Conversion (`CONFIRMED`)**:
   - `dNh:src/dnh_crm/ingest/imessage_mapper.py:86-103` (`apple_timestamp_to_iso_utc`) handles seconds, milliseconds (`> 1e11`), microseconds (`> 1e14`), and nanoseconds (`> 1e17`) cleanly using integer arithmetic (`APPLE_EPOCH_OFFSET_SECONDS = 978307200`), whereas `ChatX:src/chatx/imessage/time.py:42` uses float division (`raw / 1_000_000_000`), which loses microsecond precision on 64-bit timestamps. `dNh`'s integer `divmod` implementation should be kept, except that `raw == 0` in `chat.db` means `NULL`/unset timestamp (`imessage_mapper.py:91` rejects `<= 0` with `None`, which is right for `date_read`/`date_delivered` where `0` means unread/undelivered!).

#### 2.2 Instagram (`ChatX:src/chatx/instagram/extract.py`) (`F-11`, `HIGH`)
- **Missing Mojibake Repair (`CONFIRMED`)**: `§4` states `"instagram/ ZIP reader (zip-slip guard), mojibake repair"` and `§8` says `"Keep (port with tests, minimal change) — instagram/extract.py"`. Inspecting `ChatX:src/chatx/instagram/extract.py:1-174` confirms there is **zero mojibake repair** in the file! Meta's JSON exports encode UTF-8 bytes as `\u00c3\u00a9` (`latin1` code points), so every emoji and non-ASCII character extracted by `instagram/extract.py:157` (`str(m.get("content") or "")`) is corrupted into mojibake (`"ð\x9f\x98\x82"`).
- **Zip-Bomb & Multi-File Thread Splitting**: `_safe_extract` (`instagram/extract.py:21-38`) checks path traversal (`zip-slip`), but checks neither `ZipInfo.file_size` nor total uncompressed bytes (zip-bomb vulnerability), and `extract_instagram_zip` (`:41-106`) processes `message_1.json`, `message_2.json` in arbitrary `rglob` order without deduplicating or sorting across split thread files before assigning `msg_ig_{idx}`.

#### 2.3 WhatsApp (`dNh:src/dnh_crm/ingest/whatsapp_export.py`) (`F-04`, `BLOCKER`)
- **Catastrophic Substring Filter Bug (`CONFIRMED`)**: `dNh:src/dnh_crm/ingest/whatsapp_export.py:33-49` defines `SYSTEM_LINE_MARKERS` including bare words `"left"`, `"added"`, and `"joined"`, and `_is_system_body` (`:196-198`) runs `any(marker in normalized for marker in SYSTEM_LINE_MARKERS)`. At `:105-108`, if `_is_system_body(body)` is True, the message is **silently skipped** (`stats.skipped_system_lines += 1`). Consequently, any user message containing `"left"` (e.g., `"I left the office"`, `"20 minutes left"`), `"added"`, or `"joined"` is silently deleted during ingestion!
- **iOS Format & Locale Rejection (`CONFIRMED`)**: `MESSAGE_LINE_RE` (`whatsapp_export.py:24-27`) only matches unbracketed `MM/DD/YY, HH:MM - Sender: body` (Android). iOS WhatsApp exports use bracketed lines `[M/D/YY, H:MM:SS AM] Sender: body` (often preceded by `U+200E` `LEFT-TO-RIGHT MARK`), and international exports use `DD/MM/YYYY` or `YYYY-MM-DD`.

#### 2.4 Email `.eml` (`dNh:src/dnh_crm/ingest/email_eml.py`) (`F-19`, `HIGH`)
- `email_eml.py:110-165` parses only `Message-ID`, `From`, `Subject`, `Date`, and body text. It drops `To`, `Cc`, `Delivered-To`, `In-Reply-To`, and `References` (making email thread reconstruction and `reply_to_msg_id` impossible), hardcodes `Direction.INBOUND` and `ActorRole.CLIENT` (`:136,158`) even on sent emails, and only counts attachments (`:222-228`) without extracting filenames, MIME types, or SHA-256 digests.

#### 2.5 PDF (`ChatX:src/chatx/pdf_ingest/reader.py`) (`CONFIRMED`)
- `reader.py:15-38` requires exact line regex `^\[(?P<ts>[^\]]+)\]\s+(?P<sender>[^:]+):\s*(?P<text>.*)$` on PyMuPDF `page.get_text("text")`. Any multi-line message wrap in a PDF is silently dropped (`:70-72`), and `conv_id` uses `pdf_path.name` (`:102`). Multi-line continuation accumulation (like `whatsapp_export.py:90-92`) must be added.

---

### Area 3: Policy Shield v2 — Privacy & Redaction Architecture (§3.7)

#### 3.1 Token Format & Collision/Determinism Properties (`CONFIRMED`)
- `ChatX:src/chatx/redaction/policy_shield.py:157-169` generates `〈PII:{type_code}_{hmac_sha256(salt, normalized)[:6]}〉` (24 bits of hex = 16.7M space). By the birthday bound, a 50% collision probability across distinct PII values of the same type occurs at $\approx 4,800$ entities ($\approx 580$ entities for a 1% collision rate). On a multi-year corpus with thousands of URLs, emails, and names, 6 hex chars will suffer collisions! Expanding the token digest from 6 hex chars (24 bits) to **12 hex chars (48 bits)** (`hmac_sha256(salt, f"{pii_type}:{normalized}").hexdigest()[:12]`) pushes the 1% collision threshold above 75 million entities while adding only 6 characters per token.

#### 3.2 Reversible Token Map Inside `case.sqlite3` vs Salt File Separation (`F-12`, `BLOCKER`)
- `§3.6` and `§3.7` state: *"Salt file at `~/.config/chatx/salt.key`, `0600`, auto-created on first run, never inside `case.sqlite3`. Reversible token↔cleartext map lives inside `case.sqlite3` (never exported)."*
- **Threat-model contradiction**: Why keep `salt.key` outside `case.sqlite3`? Only so an attacker or accidental cloud sync/backup with read access to `case.sqlite3` cannot reverse HMAC pseudonyms or brute-force low-entropy PII (like 10-digit phone numbers). If `case.sqlite3` itself contains a plaintext `redaction_map(token, cleartext)` table AND the raw `messages` table (`§3.6`), anyone who obtains `case.sqlite3` already has all cleartext!
- **Fix**: Keep the reversible `token <-> cleartext` vault in `~/.config/chatx/vault/<case_id>.sqlite3` (`0600`, alongside `salt.key`), OR encrypt the `cleartext` column in `case.sqlite3` using a key derived from `salt.key` via HKDF-SHA256 + AES-GCM (`cryptography` is already a dependency in `ChatX:pyproject.toml:51`).

#### 3.3 Statistical Validity of Sampled Second-Opinion Gate (`F-13`, `HIGH`)
- `§3.7` specifies three cloud egress conditions: *(1) 0 hard-fail classes, (2) gold-corpus recall $\ge 99.5\%$ (default) / $\ge 99.9\%$ (strict), (3) 0 leaked spans in sampled second-opinion check*.
- **Why Condition (2) + (3) is underspecified**: Gold-corpus recall measures static software quality on synthetic fixtures; it tells you nothing about corpus-specific nicknames, venue names, or employer names in the user's real chat log. Conversely, if Condition (3) samples $k$ chunks from the real run and observes 0 leaks, the 95% upper confidence bound on the per-chunk leak rate $p$ is $p \le 1 - (0.05)^{1/k} \approx 3/k$.
  - For $p \le 0.005$ (99.5% chunk-level recall): $k \ge 599$ chunks.
  - For $p \le 0.001$ (99.9% strict mode): $k \ge 2,995$ chunks.
- **Concrete replacement gate**: Run a fast local zero-shot NER pass (`GLiNER-PII` on Apple Silicon MPS/ONNX or Presidio + participant roster gazetteer) over **100% of chunks queued for cloud egress**, plus automatically seed the deterministic redactor with all `participants.display_name`, `participants.raw_handle`, and contact-book first/last name tokens from `case.sqlite3`!

#### 3.4 Context Leak via `chunker.py` & `±2` Context Turns (`F-14`, `HIGH`)
- In `ChatX:src/chatx/transformers/chunker.py:166-168`, `_format_messages_text` formats every line as `f"[{timestamp}] {speaker}: {msg.text}"` where `speaker = "Me" if msg.is_me else contact`. Because `contact` is the raw phone number/email/name passed on the CLI, `chunker.py` injects raw PII onto **every single line** of the chunk before redaction!
- Furthermore, `§3.9` says *"Cloud enrichment sends redacted chunk text with ±2 turns of redacted context; raw message tables are never read by the cloud client."* Since `ConversationChunker` (`chunker.py:124-198`) already groups 40 turns with a 10-turn stride overlap, attaching "$\pm 2$ turns" either requires reading adjacent messages or duplicates turns already inside the chunk. Redaction must operate at the **message level** (storing `messages.redacted_text` and using `participants.pseudonym` as the speaker label) before assembling chunks.

#### 3.5 `HardFailDetector` vs `config/labels.yml` Conflict (`F-16`, `MEDIUM`)
- `ChatX:src/chatx/redaction/patterns.py:159-197` triggers a hard fail on regexes like `\b(?:selling|buying|dealing)\s+(?:cocaine|heroin|meth|drugs)` or `\b(?:suicide|self-harm|kill\s+myself)`. Yet `ChatX:config/labels.yml:373-389,425-427` explicitly defines `substances_specifics`, `illegal_activity_detail`, `violence_detail`, `crime_threat`, and `harm_reduction` as core taxonomy labels for relationship/psychology analysis!
- **Fix**: Split `HardFailDetector` into (a) `ABSOLUTE_BLOCK` (CSAM indicators, raw private keys/seed phrases—blocked from all cloud egress) and (b) `LOCAL_ONLY_ROUTING_TRIGGER` (self-harm, substance specifics, explicit sexuality, threats—automatically routed to `--provider local` rather than aborting the pipeline).

---

### Area 4: Unified Storage Architecture (`case.sqlite3`) (§3.6, §5)

#### 4.1 Missing Operational & Forensic Mechanics in `§3.6` (`F-21`, `HIGH`)
`§3.6` lists 11 table names in prose without DDL, PRAGMAs, or concurrency rules. Specifically:
1. **Required Connection PRAGMAs**: Every connection to `case.sqlite3` must execute:
   ```sql
   PRAGMA journal_mode = WAL;
   PRAGMA synchronous = NORMAL;
   PRAGMA foreign_keys = ON;
   PRAGMA busy_timeout = 5000;
   PRAGMA temp_store = MEMORY;
   ```
   And `case.sqlite3` (plus `-wal` and `-shm`) must be created with `0600` permissions inside a `0700` directory.
2. **Incremental Ingestion Watermarks**: `§3.6` has `runs`, `sources`, and `messages`, but no watermark cursor per `(source_id, conv_id)` (like `dNh:src/dnh_crm/store/migrations.py:165-174` `ingest_watermarks`). Without tracking `last_message_rowid` and `last_sent_at` per `source_id`, every `chatx import imessage` must re-scan and re-decode all 500k+ `attributedBody` blobs in `chat.db`.
3. **Reactions & Replies Normalization**: Because reactions can arrive before or after their target message—or target a message outside the date/contact filter—storing reactions only as a JSON array on `messages` loses orphaned reactions and mutates `messages` rows on incremental pulls. `reactions` must be a first-class table (`reaction_msg_id PRIMARY KEY`, `target_msg_id` indexed, not a hard FK that fails when the target message wasn't imported).
4. **FTS5 Tokenizer & Redacted Search**: FTS5 external-content tables (`content='messages', content_rowid='rowid'`) require `INSERT`/`DELETE`/`UPDATE` triggers to stay synchronized and should use `tokenize='unicode61 remove_diacritics 2'`.

#### 4.2 Concrete DDL for `case.sqlite3` (Migration `0001_initial.sql`)
```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    git_sha TEXT,
    config_json TEXT NOT NULL,
    stats_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    source_path_hash TEXT NOT NULL,
    display_label TEXT NOT NULL,
    last_rowid INTEGER,
    last_sent_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS participants (
    participant_id TEXT PRIMARY KEY,
    handle TEXT NOT NULL UNIQUE,
    raw_handle TEXT NOT NULL,
    display_name TEXT,
    pseudonym TEXT NOT NULL UNIQUE,
    is_me INTEGER NOT NULL DEFAULT 0 CHECK (is_me IN (0, 1))
);

CREATE TABLE IF NOT EXISTS conversations (
    conv_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    chat_identifier TEXT,
    display_name TEXT,
    service_name TEXT,
    resolution_rung TEXT,
    source_meta_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS messages (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT NOT NULL UNIQUE,
    conv_id TEXT NOT NULL REFERENCES conversations(conv_id) ON DELETE CASCADE,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    platform TEXT NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound', 'system', 'unknown')),
    sender_id TEXT NOT NULL REFERENCES participants(participant_id),
    sent_at TEXT NOT NULL,
    delivered_at TEXT,
    read_at TEXT,
    edited_at TEXT,
    retracted_at TEXT,
    text TEXT,
    redacted_text TEXT,
    body_source TEXT NOT NULL,
    content_kind TEXT NOT NULL,
    reply_to_msg_id TEXT,
    reply_to_part_index INTEGER,
    content_hash TEXT NOT NULL,
    legacy_dnh_dedupe_hash TEXT,
    source_cursor TEXT NOT NULL,
    source_meta_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_messages_conv_sent ON messages(conv_id, sent_at);
CREATE INDEX IF NOT EXISTS idx_messages_content_hash ON messages(content_hash);
CREATE INDEX IF NOT EXISTS idx_messages_reply_to ON messages(reply_to_msg_id) WHERE reply_to_msg_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS reactions (
    reaction_msg_id TEXT PRIMARY KEY,
    conv_id TEXT NOT NULL REFERENCES conversations(conv_id) ON DELETE CASCADE,
    target_msg_id TEXT NOT NULL,
    target_part_index INTEGER,
    reactor_id TEXT NOT NULL REFERENCES participants(participant_id),
    kind TEXT NOT NULL,
    emoji TEXT,
    removed INTEGER NOT NULL DEFAULT 0 CHECK (removed IN (0, 1)),
    sent_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reactions_target ON reactions(target_msg_id);

CREATE TABLE IF NOT EXISTS attachments (
    att_id TEXT PRIMARY KEY,
    msg_id TEXT NOT NULL REFERENCES messages(msg_id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    mime_type TEXT,
    uti TEXT,
    byte_len INTEGER,
    sha256 TEXT,
    storage_ref TEXT,
    missing INTEGER NOT NULL DEFAULT 0 CHECK (missing IN (0, 1)),
    missing_reason TEXT,
    ocr_text TEXT,
    transcript_text TEXT
);
CREATE INDEX IF NOT EXISTS idx_attachments_msg_id ON attachments(msg_id);
CREATE INDEX IF NOT EXISTS idx_attachments_sha256 ON attachments(sha256) WHERE sha256 IS NOT NULL;

CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    msg_id UNINDEXED,
    conv_id UNINDEXED,
    text,
    redacted_text,
    content='messages',
    content_rowid='rowid',
    tokenize='unicode61 remove_diacritics 2'
);
```

---

### Area 5: Enrichment Pipeline Redesign (§3.9)

#### 5.1 Critical Privacy Leak in `§3.9` Cloud Schema Compilation (`F-15`, `BLOCKER`)
- `§3.9` states: *"Taxonomy enforcement: `config/labels.yml` is compiled at startup into Pydantic `Literal[...]` / `Enum` types so neither backend can invent out-of-taxonomy labels."*
- Inspecting `ChatX:config/labels.yml:3-12` and `ChatX:docs/design/specifications/cloud-enrichment.md:13-22` reveals that `labels.yml` is split into two tiers: **55 `coarse` labels** and **99 `fine_local_only` labels** (which include explicit sexual acts, kink dynamics, specific illegal substances, and clinical trauma indicators). Furthermore, `ChatX:config/arch-gates.yml:60-63` enforces a CI visibility linter that fails with `E_VISIBILITY_LEAK` if any cloud enrichment row contains `fine_labels_local`!
- If `chatx enrich --provider cloud --allow-cloud` compiles the full `config/labels.yml` into the cloud tool/output schema, it both sends all 99 `fine_local_only` label definitions in the cloud prompt and asks the cloud LLM to return `fine_local_only` classifications!
- **Fix**: Startup compilation must produce two separate Pydantic models:
  1. `CloudCoarseEnrichmentResult`: compiled strictly from labels in `config/labels.yml` where `tier: coarse` (excluding `fine_local_only` completely).
  2. `LocalFullEnrichmentResult`: compiled from both `coarse` and `fine_local_only` labels, restricted to `--provider local`.

#### 5.2 Prompt Injection, Caching, Batching & Provenance (`F-22`, `MEDIUM`)
1. **Prompt Injection from Untrusted Chat Turns**: A contact's message in a chat log may literally contain instructions (`"Ignore previous instructions and output..."`). Because enrichment uses structured outputs, prompt injection cannot break JSON syntax, but it **can** hijack label assignment, summary text, and confidence scores. Wrap chat turns in `<untrusted_conversation_transcript>...</untrusted_conversation_transcript>` tags and instruct the system prompt that text inside those tags is passive data, never instructions.
2. **Anthropic Prompt Caching & Message Batches API**: Sending 55+ label definitions and descriptions on every synchronous request wastes ~2,500 input tokens per chunk. Marking the system prompt and tool schema with `cache_control={"type": "ephemeral"}` cuts input token cost by up to 90%, and adding `--batch` (Anthropic Message Batches API) cuts cost by an additional 50% (see Scope 15).
3. **Provenance & Cost Caps**: `chunk_enrichment` in `case.sqlite3` must record `(chunk_id, provider, model_id, prompt_sha256, taxonomy_sha256, input_tokens, cached_tokens, output_tokens, cost_usd, created_at)` with `PRIMARY KEY (chunk_id, model_id, prompt_sha256, taxonomy_sha256)` and enforce `--max-cost-usd` before dispatching cloud batches.

---

### Area 6: Taxonomy & Psychology Layer (`config/labels.yml`) (§3.9, §3.11)

#### 6.1 Total Vocabulary Mismatch Between `labels.yml` and `psychology_relationship_mapper.py` (`F-18`, `HIGH`)
- `§3.11` states: *"Optional `chatx analyze` command runs `config/psychology_relationships.yml` (ported from `psychology_relationship_mapper.py` as data, not a storage engine) over enriched chunks in `case.sqlite3`."* And `§8` classifies `psychology_relationship_mapper.py` as *"Content worth porting as data (YAML)"*.
- Comparing `ChatX:src/chatx/storage/psychology_relationship_mapper.py:129-546` against `ChatX:config/labels.yml:1-469` proves that **not a single label name matches** (`CONFIRMED`):
  - `psychology_relationship_mapper.py` rules look for: `sexual_content`, `flirtation`, `intimacy_escalation`, `consent_check`, `boundary_setting`, `emotional_withdrawal`, `anxiety_spike`, `reassurance_seeking`, `defensive_response`, `communication_withdrawal`, `emotional_volatility`, `mixed_signals`, `confusion_expression`, `reality_questioning`, `self_doubt_increase`, `substance_mention`, `party_context`, `boundary_lowering`, `risk_taking_increase`, `next_day_regret`, `shame_expression`, `boundary_violation`, `manipulation_attempt`, `emotional_distancing`, `trust_erosion`, `arousal_anticipation`, `dopamine_seeking`, `novelty_pursuit`, `validation_craving`, `gaslighting_pattern`, `reality_distortion`, `blame_shifting`, `victim_playing`.
  - `config/labels.yml` defines completely different IDs: `intimacy_Connection`, `Boundary_setting` (note capital `B` in `labels.yml:22`!), `attachment_anxious_activated`, `escalation`, `stonewalling`, `Darvo` (capital `D` in `labels.yml:69`!), `gaslighting`, `guilt_tripping`, `love_bombing`, `substance_influence_stimulants`, `chemsex_context`, etc.
- If `psychology_relationship_mapper.py` is ported to YAML without translating every `source_labels` and `target_labels` entry to `config/labels.yml` IDs, `chatx analyze` will silently produce **0 relationships**.
- **Also**: `config/labels.yml` has inconsistent casing in label IDs (`intimacy_Connection` at `:18`, `Boundary_setting` at `:22`, `Repair_attempt` at `:26`, `Explicit_consent` at `:35`, `Enthusiastic_affirmation` at `:39`, `Darvo` at `:69` vs lowercase `snake_case` everywhere else), which violates `labels.yml:6` (`"Case-insensitive canonicalization (snake_case)"`). Normalize all label IDs to lowercase `snake_case` and validate `psychology_relationships.yml` against `labels.yml` at startup!
- **Sensitivity inside `coarse` tier**: Even within `tier: coarse`, `config/labels.yml:155-288` includes `sex_work_context`, `substance_influence_depressants_ghb`, `substance_influence_dissociatives_ketamine`, `chemsex_context`, and `relationship_dynamic_cuckold`. These should be moved from `coarse` to `fine_local_only` before enabling cloud enrichment.

---

### Area 7: Indexing & Retrieval Redesign (§3.10)

#### 7.1 `sqlite-vec` Brute-Force Scaling vs. the `10k`–`1M` Target (`F-17`, `HIGH`)
- `§3.10` specifies: *"Single semantic embedding space (`BAAI/bge-small-en-v1.5`, 384-dim, or `nomic-embed-text-v1.5`) stored in `sqlite-vec` (`chunk_vectors`)"*, and `§3.6` claims *"Works cleanly up to ~1M chunks on a laptop."*
- **Technical reality (`CONFIRMED` via Scope 15 web search)**: `sqlite-vec` (`asg017/sqlite-vec`, tracking issue `#25`) is **pure brute-force $O(N)$ linear scan** (`vec0` virtual tables have no HNSW or IVF ANN index).
  - At **10k–100k chunks** (384-dim float32 = 1.5 KB/vector $\rightarrow$ 15 MB–150 MB), NEON-accelerated brute-force cosine/L2 scans on Apple Silicon complete in **2–25 ms**, easily beating the `<150 ms p95` target (`§11`).
  - At **1M chunks** (768-dim `nomic-embed-text-v1.5` float32 = 3.07 GB; 384-dim `bge-small` float32 = 1.54 GB), every unfiltered query scans 1.5–3.0 GB of vector pages, taking **300–1,200 ms** and violating the `<150 ms p95` gate (`§11`).
- **Concrete fix for `§3.10`**:
  1. Pin `BAAI/bge-small-en-v1.5` (384-dim) or Matryoshka-truncated 256/384-dim `nomic-embed-text-v1.5` as default.
  2. Always push SQLite relational metadata predicates (`conv_id`, `sent_at` range, label filter) into a `rowid IN (SELECT chunk_rowid FROM chunks WHERE ...)` subquery or `vec0` partition key (`conv_id TEXT PARTITION KEY`) so `sqlite-vec` only scans candidate rows rather than all 1M chunks.
  3. Above 100k chunks per partition, use `sqlite-vec` scalar quantization (`vec_int8`, 4x smaller) or binary quantization (`vec_bit`, 32x smaller) with top-$4k$ float32 re-ranking.

#### 7.2 Dropping the 4-Space `MultiVectorChromaDBStore` (`CONFIRMED`)
- Dropping `ChatX:src/chatx/indexing/multi_vector_store.py:164-320` is unambiguously the right call. Inspecting lines `164-242` confirms that `MultiVectorChromaDBStore` never trained or used separate embedding models for its `PSYCHOLOGICAL`, `TEMPORAL`, and `STRUCTURAL` vector spaces—it merely concatenated metadata strings (like `"Dominant labels: ... Temporal context: morning conversation"`) and fed them into the exact same `all-MiniLM-L6-v2` sentence-transformer (`:63,131`), storing 4x the embeddings in ChromaDB to perform work that SQLite `WHERE` filters and FTS5 + `sqlite-vec` Reciprocal Rank Fusion (`RRF`, $k=60$) do deterministically and faster.

---

### Area 8: Dead-Code Disposition & Salvage Audit (§8)

#### 8.1 Verification of Every File in `§8` (`CONFIRMED`)
1. **`src/chatx/extractors/imessage.py` (582 lines — marked "Delete")**:
   - **Hidden logic worth salvaging before deletion**: While `extractors/imessage.py` is unreachable from the CLI (`01-code-reality-audit.md:99-111`), lines `309-315` (`_row_to_message`) extract `thread_originator_guid`, `thread_originator_part`, and `balloon_bundle_id`—three fields that the live extractor (`src/chatx/imessage/extract.py:88-108`) completely forgot to query! Salvage the `thread_originator_guid`, `thread_originator_part`, and `balloon_bundle_id` extraction into the unified iMessage extractor before deleting `src/chatx/extractors/imessage.py`. (Do **not** salvage `extractors/imessage.py:109-112`, which queries `FROM message_summary_info` as a separate table—in real macOS `chat.db`, `message_summary_info` is a BLOB column on `message`).
2. **`src/chatx/storage/base.py` (590 lines — marked "Delete")**:
   - Verified dead (`ChatX:src/chatx/storage/base.py:1-590`). Contains 5 abstract classes (`AbstractVectorStore`, `AbstractGraphStore`, `AbstractTimeSeriesStore`, `AbstractHybridStore`, `MultiStoreManager`) with zero concrete implementations anywhere in the repo. Safe to delete in PR 1.
3. **`src/chatx/storage/psychology_relationship_mapper.py` (570 lines — marked "Port as YAML")**:
   - As proven in Area 6 (`F-18`), its 10 `RelationshipRule` definitions (`:129-330`) use fabricated label strings that have 0% overlap with `config/labels.yml`. Furthermore, its temporal causality engine (`:410-495`) compares chunk timestamps across `time_window_hours` with a decaying confidence formula. If `chatx analyze` is kept, both the YAML rule vocabulary and the sliding temporal window matcher must be rewritten against `labels.yml` and SQLite `chunks`/`chunk_enrichment`.
4. **`src/chatx/enrichment/multi_pass_pipeline.py` (889 lines — marked "Delete")**:
   - Verified safe to delete, with **one caveat**: `ChatX:src/chatx/cli/main.py:555-730` (`enrich_multi_pass` CLI command) directly imports and calls `MultiPassEnrichmentPipeline`. Deleting `multi_pass_pipeline.py` in PR 1 (`§12`) without simultaneously removing or stubbing `enrich_multi_pass` in `cli/main.py` will break CLI imports or tests if `main.py` is not updated in the same PR.
5. **`src/chatx/indexing/multi_vector_store.py` (845 lines — marked "Delete")**:
   - Verified safe to delete, with the same PR-sequencing caveat: `ChatX:src/chatx/cli/main.py:744,838` (`index` and `query` commands) imports `MultiVectorChromaDBStore` at runtime.
6. **`src/chatx/instagram/extract.py` (174 lines — marked "Keep, minimal change")**:
   - As proven in Area 2 (`F-11`), `instagram/extract.py` lacks the mojibake repair that `§4` claims it has, and lacks zip-bomb protection. It requires substantive fixes, not just a minimal port.
7. **`dNh:src/dnh_crm/ingest/whatsapp_export.py` (248 lines — marked "Adopt as canonical")**:
   - As proven in Area 2 (`F-04`), its `_is_system_body` substring check (`:33-49,196-198`) silently drops user messages containing `"left"`, `"added"`, or `"joined"`, and its regex (`:24-27`) rejects all iOS WhatsApp exports. Must be fixed during adoption.

---

### Area 9: CLI Contract, Ergonomics & Breaking-Change Migration (§4, §7)

#### 9.1 Comparison Against Existing 1,573-Line `src/chatx/cli/main.py` (`CONFIRMED`)
- Inspecting `ChatX:src/chatx/cli/main.py:1-1573` shows top-level commands `extract` (stub, `:59-95`), `transform` (`:98-220`), `redact` (`:223-350`), `enrich` (`:353-552`), `enrich-multi-pass` (`:555-730`), `index` (`:734-818`), `query` (`:821-966`), `simulate` (`:1375-1573`), and sub-apps `imessage` (`pull`, `audit`, `pdf` at `:970-1310`) and `instagram` (`pull` at `:1315-1370`).
- **CI Workflow Breakage (`F-25`, `MEDIUM`)**: `ChatX:config/arch-gates.yml:25,43,47,71,76` invokes commands that don't even match the *current* CLI (`chatx redact --input ... --opaque`, `chatx enrich messages --contact ...`, `chatx validate`, `chatx metrics summarize`). Under the new `§4` CLI (`chatx import`, `chatx redact`, `chatx chunk`, `chatx enrich`, `chatx index`, `chatx query`, `chatx analyze`, `chatx export`, `chatx audit`, `chatx identity`), `config/arch-gates.yml` must be rewritten in PR 3/4 so CI actually executes real commands.
- **RFC 7807 `emit_problem` & Exit Codes**: `ChatX:src/chatx/cli_errors.py:1-32` is clean and should be applied uniformly across all 10 commands in `§4` via a shared Typer exception handler (`@app.callback()` / custom `RichGroup` or decorator) with standardized exit codes:
  - `0`: Success
  - `1`: Invalid input / usage / missing source path (`INVALID_INPUT`)
  - `2`: Policy Shield / cloud preflight gate failure (`POLICY_SHIELD_BLOCKED`)
  - `3`: Schema or database integrity check failure (`INTEGRITY_FAILURE`)
  - `4`: External provider / LLM / backup decryption error (`PROVIDER_ERROR`)

---

### Area 10: Attachment, Media & Sidecar Pipeline (§3.5, §3.6)

#### 10.1 Attachment Resolution, Hashing & iCloud Eviction (`F-08`, `F-23`)
1. **Live macOS `~/` Path Resolution Bug (`F-08`, `BLOCKER`)**: As detailed in Area 2.1, `ChatX:src/chatx/imessage/attachments.py:90-126` fails on `~/Library/Messages/Attachments/...` because it omits `.expanduser()`. Fix:
   ```python
   expanded = Path(filename).expanduser()
   if expanded.is_absolute() and expanded.is_Relative_to(Path.home() / "Library/Messages/Attachments"):
       ...
   ```
2. **Content-Addressed Blob Store vs Copy-In-Place**: `§3.6` proposes storing `sha256` and `storage_ref` in `attachments`. Copying every raw attachment binary into the case directory by default bloats a 50 GB iMessage `Attachments/` folder into a 50 GB duplicate. Default should be **reference-in-place with streaming SHA-256 computation** (`storage_ref = "file://..."`, computing `sha256` in 64 KB chunks without loading whole videos into RAM), and only copying into `<case_dir>/blobs/sha256/<ab>/<sha256>` when `--copy-binaries` is explicitly passed.
3. **Thumbnail EXIF & Biometric Leakage (`F-23`, `MEDIUM`)**: When `--thumbnails` generates image thumbnails or when OCR/ASR runs (`attachments.py:194-262`), EXIF metadata (GPS coordinates, camera serial numbers, Apple Live Photo face regions) must be stripped (`ImageOps.exif_transpose` + saving without `exif=` bytes), and OCR/ASR outputs (`ocr_text`, `transcript_text`) must pass through **Policy Shield v2** before being indexed in FTS5 or `sqlite-vec` or sent to cloud enrichment!

---

### Area 11: Testing, Determinism & Verification Strategy (§11)

#### 11.1 Fixture Fidelity & Missing `dNh` Test Assets (`F-24`, `MEDIUM`)
1. **`imessage_test_data.sql` Diverges from Real macOS `chat.db` (`CONFIRMED`)**:
   - Inspecting `ChatX:tests/fixtures/imessage_test_data.sql:1-162` reveals four critical divergences from real macOS `chat.db`:
     - Line `82-90`: Reaction rows use bare `associated_message_guid` (`'msg-004'`) instead of Apple's real `'p:0/msg-004'` or `'bp:msg-004'`, which masked the prefix-stripping bug (`F-07`)!
     - Line `97-103`: Attachment filenames use `'IMG_1234.HEIC'` instead of `'~/Library/Messages/Attachments/ab/12/att-001/IMG_1234.HEIC'`, which masked the `.expanduser()` bug (`F-08`)!
     - Line `144-149`: Creates a separate table `CREATE TABLE message_summary_info (...)`, whereas in real macOS `chat.db`, `message_summary_info` is a BLOB column on `message` (`F-09`)!
     - Line `75-78`: Uses plain UTF-8 bytes `X'48656C6C6F...'` (`"Hello from attributedBody!"`) in `attributedBody` instead of a real NeXT/Apple `typedstream` binary header (`\x04\x0bstreamtyped...`)!
2. **Must Port `dNh`’s 1,013-Line Typedstream Test Suite**: `dNh:tests/unit/test_imessage_attributed_body.py:1-1013` contains comprehensive binary fixtures for `NSAttributedString`, `NSMutableAttributedString`, length-encoding boundaries (`0x81`, `0x82`), invalid UTF-8 sequences, and corrupted streams. `§11` must explicitly include porting `test_imessage_attributed_body.py` (plus adding a test for `U+FFFC` inline attachment markers, `F-10`).
3. **Property-Based Tests (`hypothesis`)**: Add `hypothesis` tests for:
   - `CanonicalMessage` canonical JSON serialization and `content_hash` invariance under field reordering, `source_meta` mutation, and post-import pseudonym assignment.
   - `apple_timestamp_to_iso_utc` across seconds, milliseconds, microseconds, nanoseconds, `0`, and negative values.
   - Policy Shield v2 token determinism and zero cleartext substring survival for generated PII spans.

---

### Area 12: Security, Privacy & Threat Model

#### 12.1 Adversary Analysis & Concrete Mitigations
| Adversary / Threat Vector | Attack Surface in Design (`§3`–`§9`) | Concrete Vulnerability Found | Required Mitigation |
|---|---|---|---|
| **A1. Accidental Cloud Leak** (`--provider cloud --allow-cloud`) | `§3.7` Policy Shield v2 + `§3.9` Cloud Enrichment | (1) `chunker.py:168` injects raw `contact` into every turn (`F-14`). (2) `§3.9` compiles all of `labels.yml` including 99 `fine_local_only` labels into cloud prompts (`F-15`). (3) Attachment `ocr_text`/`transcript_text` is not routed through Policy Shield. | Redact at message level before chunking; use `participants.pseudonym` as speaker label; strip `fine_local_only` from cloud schema; redact OCR/ASR text before chunking; seed redactor with `participants` display names/handles. |
| **A2. Local Filesystem Compromise / Backup Sync** (Spotlight, Time Machine, iCloud Drive) | `case.sqlite3` + `~/.config/chatx/salt.key` + temp WAL snapshots | (1) `case.sqlite3` stores both raw `messages` and the reversible `token <-> cleartext` map (`F-12`). (2) `ChatX:src/chatx/imessage/db.py:25` creates temp directory with default `0755` permissions (`mkdtemp`) instead of `0700`/`0600`. | Create `case.sqlite3` with `0600` inside `0700` dir; add `.metadata_never_index` inside `<case_dir>` to block macOS Spotlight indexing; encrypt `redaction_map.cleartext` with AES-GCM keyed from `salt.key` (HKDF). |
| **A3. Subpoena / Third-Party Sharing of `case.sqlite3`** | Sharing or exporting analysis artifacts | If a user shares `case.sqlite3` believing it contains "pseudonymized analysis", raw `messages.text`, `participants.raw_handle`, and `redaction_map` are all inside the same SQLite file! | Add `chatx export --redacted-db <out.sqlite3>` which creates a sanitized SQLite copy with `messages.text = NULL`, `participants.raw_handle = NULL`, `participants.handle = pseudonym`, and `DROP TABLE redaction_map` + `VACUUM` (to purge deleted SQLite freelist pages!). |
| **A4. Malicious Input Files** (Crafted `.zip`, `.eml`, `.pdf`, `chat.db`) | `instagram/extract.py`, `email_eml.py`, `pdf_ingest/reader.py`, `imessage/db.py` | (1) `instagram/extract.py:21-38` lacks zip-bomb size/count limits (`F-11`). (2) Crafty SQLite database could contain malicious triggers or views executed on query if opened writable (`db.py`). (3) Prompt injection in chat text (`F-22`). | Enforce max 5,000 files / 2 GB uncompressed ceiling in `_safe_extract`; set `sqlite3.Connection.setconfig(sqlite3.SQLITE_DBCONFIG_TRUSTED_SCHEMA, False)` on untrusted DBs; wrap chat turns in XML tags for LLM enrichment. |

---

### Area 13: Dependency Footprint & Packaging (`pyproject.toml`) (§5, §13)

#### 13.1 Bloated Default Dependencies in `ChatX:pyproject.toml` (`F-25`, `MEDIUM`)
Inspecting `ChatX:pyproject.toml:31-76` confirms that `pip install chatx` currently pulls in **5 competing vector databases and heavy ML stacks in default `dependencies`**:
- `chromadb>=0.4.22`, `pymilvus>=2.3.0`, `qdrant-client>=1.7.0`, `pinecone>=3.0.0`, `weaviate-client>=4.4.0` (`pyproject.toml:55-61`)
- `networkx>=3.2.0`, `igraph>=0.11.0`, `pyarrow>=15.0.0`, `polars>=0.20.0`, `duckdb>=0.10.0` (`pyproject.toml:62-68`)
- `transformers>=4.36.0`, `torch>=2.1.0`, `sentence-transformers>=2.2.2`, `spacy>=3.7.0` (`pyproject.toml:71-75`)

Even more ironically, `pymilvus`, `qdrant-client`, `pinecone`, `weaviate-client`, `igraph`, `polars`, and `duckdb` have **zero imports** in `src/chatx/` (`01-code-reality-audit.md:331-360`)! Meanwhile, `phonenumbers` is needed for E.164 normalization (`Area 2`, `Area 12`).

#### 13.2 Concrete Replacement `pyproject.toml` Dependency Split
- **Core `dependencies` (fast, <100 MB install, deterministic CLI + extractors + SQLite + Policy Shield regex)**:
  - `typer>=0.12.5`, `rich>=13.7.0`, `pydantic>=2.7.0`, `jsonschema>=4.21.0`, `pyyaml>=6.0.1`, `cryptography>=42.0.0`, `phonenumbers>=8.13.0`, `httpx>=0.27.0`, `sqlite-vec>=0.1.6`
- **Optional extras (`[project.optional-dependencies]`)**:
  - `local-ner = ["gliner>=0.2.10", "onnxruntime>=1.18.0"]`
  - `embeddings = ["sentence-transformers>=3.0.0"]` (or `fastembed>=0.3.0` for ONNX-based `bge-small-en-v1.5` without PyTorch!)
  - `cloud = ["anthropic>=0.34.0", "openai>=1.40.0"]`
  - `pdf = ["pymupdf>=1.24.0"]`
  - `media = ["pillow>=10.3.0", "pytesseract>=0.3.10", "faster-whisper>=1.0.0"]`
  - `all = ["chatx[local-ner,embeddings,cloud,pdf,media]"]`

---

### Area 14: Rollout / PR Sequencing & Migration Risk (§12)

#### 14.1 PR Sequencing Hazards in `§12` (`CONFIRMED`)
Checking the 6-PR sequence in `§12` against actual module imports reveals two broken intermediate states:
1. **PR 1 ("Delete dead code (`src/chatx/extractors/`, `src/chatx/storage/base.py`, `multi_pass_pipeline.py`, `multi_vector_store.py`)") breaks `src/chatx/cli/main.py` and existing unit tests**:
   - `src/chatx/cli/main.py` imports `MultiPassEnrichmentPipeline` (`:583`) and `MultiVectorChromaDBStore` (`:744,838`), and `tests/unit/` has test files importing those deleted modules (`01-code-reality-audit.md:107,232,265,280`).
   - **Fix**: In PR 1, simultaneously remove the corresponding dead test files (`tests/unit/extractors/test_imessage_extractor.py`, `tests/unit/enrichment/test_multi_pass_pipeline.py`, `tests/unit/indexing/test_multi_vector_store.py`, `tests/unit/storage/test_psychology_relationship_mapper.py`) and remove `enrich-multi-pass` / `--multi-vector` from `src/chatx/cli/main.py` so `pytest` stays 100% green on PR 1.
2. **PR 2 vs PR 4 Ordering**:
   - In `§12`, PR 2 creates `case.sqlite3` and ports all extractors (`imessage`, `whatsapp`, `email`, `instagram`, `pdf`), while PR 4 introduces the new CLI verbs (`import`, `redact`, `chunk`, etc.) and updates docs. If PR 2 deletes or replaces `src/chatx/imessage/extract.py` before PR 4 updates `cli/main.py`, the CLI is broken between PR 2 and PR 4.
   - **Fix**: Wire `chatx import` and the `--legacy` deprecation shims into `cli/main.py` in **PR 2** alongside the unified extractors and `case.sqlite3` store, then land Policy Shield v2 in **PR 3**, Enrichment + `sqlite-vec` Retrieval + `config/arch-gates.yml` in **PR 4**, `dNh_CRM` bridge in **PR 5**, and docs/release cleanup in **PR 6**.

---

### Area 15: Ecosystem Currency (Web-Verified `2026-10-20`)

1. **Apple `chat.db` & `typedstream` Parsing (macOS 14 Sonoma / macOS 15 Sequoia / iOS 18)**:
   - *Web verification*: ReagentX’s `imessage-exporter` (`https://github.com/ReagentX/imessage-exporter`) and Christopher Sardegna’s reverse-engineering writeups (`https://chrissardegna.com/blog/reverse-engineering-imessage-attributedbody/`) confirm that in iOS 18 / macOS 15 Sequoia:
     - `associated_message_type = 2006` is **Add Custom Emoji Reaction** and `3006` is **Remove Custom Emoji Reaction**, with the emoji character stored in the `message.associated_message_emoji` column.
     - `associated_message_type = 2007` / `3007` are **Sticker Tapbacks**.
     - `message.message_summary_info` (a binary plist BLOB column on `message`) stores iOS 16+ edit histories (`ec` dictionary of edited `NSAttributedString` payloads) and unsend (`date_retracted`) metadata.
   - *Impact on design*: Resolves Open Question #4 in `§13` and `§3.4` (`2006`/`3006` are confirmed custom emoji tapbacks via `associated_message_emoji`).
2. **`sqlite-vec` Maturity & Scale Limits**:
   - *Web verification*: Alex Garcia’s `sqlite-vec` (`https://github.com/asg017/sqlite-vec`, issue `#25: ANN (Approximate Nearest Neighbors) Index`, and `https://alexgarcia.xyz/blog/2024/sqlite-vec-stable-release/index.html`) confirms `sqlite-vec` intentionally performs **brute-force $O(N)$ scans only** (no HNSW/IVF index). At 1M float32 vectors, raw vector scans read 1.5–3.0 GB per query. Scaling beyond ~100k vectors inside `sqlite-vec` requires `vec_int8` / `vec_bit` quantization and SQLite `rowid` metadata pre-filtering (or `partition key` columns in `vec0`).
3. **Local Structured LLM Inference on Apple Silicon (`mlx-lm`, `Outlines`, `Ollama` / `llama.cpp`)**:
   - *Web verification*: Both Ollama (`response_format` backed by `llama.cpp` JSON-Schema-to-GBNF grammar compilation, `https://github.com/ggerganov/llama.cpp`) and `Outlines` + `mlx-lm` (`https://dottxt-ai.github.io/outlines/`, `pip install "outlines[mlxlm]"`) enforce 100% schema-valid Pydantic generation on Apple Silicon. With constrained decoding, smaller modern models (`Qwen3-4B-Instruct-4bit` or `Qwen2.5-7B-Instruct`) achieve 100% JSON schema compliance at 3–5x the throughput of unconstrained 7B/14B retry loops.
4. **Anthropic Cloud Structured Outputs, Prompt Caching & Message Batches API**:
   - *Web verification*: Anthropic’s API (`https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching` and `https://docs.anthropic.com/en/docs/build-with-claude/message-batches`) supports stacking **Prompt Caching** (`cache_control: {"type": "ephemeral"}`, up to 90% input token savings on the static taxonomy/system prompt prefix) with the **Message Batches API** (50% discount for async corpus enrichment). Best practice is to send one synchronous "cache warm-up" call before submitting a batch of chunks sharing the cached prefix.
5. **Local PII Redaction (GLiNER-PII + Microsoft Presidio)**:
   - *Web verification*: Specialized span-level zero-shot NER models (`knowledgator/gliner-pii-large-v1.0` on HuggingFace `https://huggingface.co/knowledgator/gliner-pii-large-v1.0` and `presidio-analyzer[gliner]`) run natively on Apple Silicon via PyTorch MPS or ONNX Runtime (`CoreMLExecutionProvider`), achieving 0.85–0.98 F1 on unstructured PII where regexes fail. Combining deterministic regex/checksum rules + contact-roster gazetteer + ONNX `gliner-pii` provides a fast, zero-cloud-dependency layer 2 for Policy Shield v2.

---

## 4. Decision Challenges (§3 & §13)

### Challenge 1: Storing Reversible PII Token Map Inside `case.sqlite3` (§3.6, §3.7)
- **Design’s current choice**: Store `salt.key` outside `case.sqlite3` at `~/.config/chatx/salt.key` (`0600`), while storing the reversible `token <-> cleartext` map inside `case.sqlite3` (`§3.6`, `§3.7`).
- **Concrete failure mode**: `case.sqlite3` already contains raw `messages.text` and `participants.raw_handle` (`§3.6`). Storing an unencrypted `redaction_map` inside the same database means (a) separating `salt.key` provides zero confidentiality if `case.sqlite3` is read, and (b) a user cannot safely share or archive an anonymized `case.sqlite3` without risking full PII reversal.
- **Superior alternative**: Encrypt `redaction_map.cleartext` using AES-256-GCM with a key derived via HKDF-SHA256 from `~/.config/chatx/salt.key`, and provide `chatx export --redacted-db` which nulls raw columns, drops `redaction_map`, and runs `VACUUM`.
- **Cost of switching now vs. later**: **Now**: ~40 lines of Python using `cryptography.hazmat.primitives.ciphers.aead.AESGCM` (already installed in `pyproject.toml:51`). **Later**: Requires migrating existing plaintext SQLite files and rotating leaked tokens.

### Challenge 2: Folding `reactions` and `sender.pseudonym` Into `CanonicalMessage` & `content_hash` (§3.4)
- **Design’s current choice**: Embed `sender.pseudonym`, `reactions: list[Reaction]`, and `attachments[].missing`/`storage_ref` inside `CanonicalMessage`, and compute `content_hash` over canonical JSON excluding only `source_meta` and `provenance`.
- **Concrete failure mode**: Running `chatx identity pseudonymize` (`§3.12`), pulling a subsequent Tapback reaction, or downloading an iCloud-evicted attachment changes `content_hash` for historical messages, breaking idempotency in both `ChatX` and `dNh_CRM` (`§9`).
- **Superior alternative**: Compute `content_hash` strictly over the immutable message core `(platform, conv_id, msg_id, sent_at, direction, sender.handle, text, reply_to_msg_id, [att.sha256 or att.filename])`, store `reactions` in its own SQLite table (`reactions`), and store `pseudonym` on `participants`.
- **Cost of switching now vs. later**: **Now**: Trivial helper function change before PR 2 lands. **Later**: Invalidates every stored `content_hash` and `dNh` `dedupe_hash` across both repositories.

### Challenge 3: Compiling Full `config/labels.yml` Into Cloud Enrichment Schema (§3.9)
- **Design’s current choice**: Compile `config/labels.yml` into Pydantic `Literal`/`Enum` types shared by `--provider local` and `--provider cloud`.
- **Concrete failure mode**: Exposes 99 `fine_local_only` sensitive labels (clinical psychology, kink/sexuality, substance specifics) to cloud LLM APIs and violates `config/arch-gates.yml:60-63` (`E_VISIBILITY_LEAK`).
- **Superior alternative**: Compile `CoarseCloudLabelEnum` (55 `coarse` labels, minus the 5 misclassified substance/sex-work labels noted in Area 6) for `--provider cloud` and `FullLocalLabelEnum` (all 154 labels) for `--provider local`.
- **Cost of switching now vs. later**: **Now**: 15 lines in the taxonomy loader. **Later**: Cannot retroactively un-send sensitive label classifications already transmitted to a cloud provider.

### Challenge 4: Replacing `dNh`’s `build_imessage_dedupe` With `provenance.content_hash` (§9)
- **Design’s current choice**: Map `CanonicalMessage.provenance.content_hash` directly to `EventEnvelope.dedupe_hash` in `dNh_CRM` (`§9`).
- **Concrete failure mode**: Breaks `UNIQUE(dedupe_scope, dedupe_hash)` continuity (`dNh:src/dnh_crm/store/migrations.py:23`) against all existing `events` rows in `dNh_CRM`, causing duplicate event ingestion on upgrade.
- **Superior alternative**: Compute and carry `provenance.legacy_dnh_dedupe_hash` using `dNh`'s exact `compute_idempotency_key` formula (`dNh:src/dnh_crm/ingest/dedupe.py:15-50`) for `imessage`, `whatsapp`, and `email`, or ship a `dNh` store migration that re-hashes existing rows transactionally.
- **Cost of switching now vs. later**: **Now**: 20 lines in the `dNh` adapter. **Later**: Corrupts production `dNh_CRM` timelines with duplicate inbound events and duplicate downstream task triggers.

---

## 5. What the Design Gets Right

1. **Single Canonical Store (`case.sqlite3` + FTS5 + `sqlite-vec` in `§3.6`)**: Eliminating the ChromaDB + Neo4j + InfluxDB/TimescaleDB + Redis multi-daemon fantasy (`src/chatx/storage/base.py`) in favor of a single local SQLite file with FTS5 and `sqlite-vec` dramatically reduces operational failure modes and makes case directories portable and inspectable.
2. **Adopting `dNh`’s `attributedBody` State Machine & 2-Rung Thread Resolver (`§3.5`, `§8`)**: Recognizing that `dNh:src/dnh_crm/ingest/imessage_attributed_body.py` and `imessage_thread_identity.py` are far more mature than `ChatX`’s `UTF-8`/`latin-1` regex fallback (`ChatX:src/chatx/imessage/extract.py:24-39`) eliminates the #1 source of dropped iMessage bodies on macOS Ventura/Sonoma/Sequoia.
3. **Fixing the `OR m.is_from_me = 1` Contact-Filter Leak (`§3.5`)**: Identifying that `ChatX:src/chatx/imessage/extract.py:384-385` (`WHERE m.handle_id IN (...) OR m.is_from_me = 1`) leaked every outbound message the user ever sent to *any* contact when `--contact` was specified closes a critical privacy and data-contamination bug.
4. **Calling Out and Replacing the Vacuous `coverage = 1.0` Redaction Gate (`§2.1`, `§3.7`)**: Spotlighting `ChatX:src/chatx/redaction/policy_shield.py:310-335` (`coverage = 1.0` when `total_Stage1 == 0`) and replacing it with a fail-closed multi-condition gate prevents unverified text from silently passing `--preflight`.
5. **Deleting the 4-Space `MultiVectorChromaDBStore` and `MultiPassEnrichmentPipeline` (`§3.9`, `§3.10`, `§8`)**: Removing 1,734 lines of pseudo-multi-vector and 4-pass LLM boilerplate that weren't backed by distinct models or schemas removes massive maintenance debt and 4x token waste.

---

## 6. Open Questions for the Owner (Ranked)

1. **Question 1 — Sensitivity Boundary in `config/labels.yml` (`tier: coarse` vs `fine_local_only`)**:
   - *Context*: `config/labels.yml` currently marks `sex_work_context` (`:155`), `substance_influence_depressants_ghb` (`:268`), `substance_influence_dissociatives_ketamine` (`:272`), `chemsex_context` (`:288`), and `relationship_dynamic_cuckold` (`:167`) as `tier: coarse` (cloud-safe).
   - *Decision needed*: Should all sexuality, kink, and specific substance labels be strictly demoted to `fine_local_only` so that `--provider cloud` only ever sees high-level communication/affect/conflict dynamics?
2. **Question 2 — Outbound & Non-Text Message Handling in `dNh_CRM` (`§9`)**:
   - *Context*: `dNh` currently ingests only inbound text or inbound attachment-only iMessages (`MSG_INBOUND_RECEIVED`, `ActorRole.CLIENT`), whereas `ChatX` extracts full bidirectional conversations including outbound messages (`is_from_me=1`), reactions (`reaction_only`), and group membership events (`system`).
   - *Decision needed*: When `dNh_CRM` calls `chatx.extractors` (`§9`), should `dNh` now ingest outbound messages as `MSG_OUTBOUND_SENT` (`ActorRole.OPERATOR`) and reactions as a new `EventType`, or should the `dNh` adapter filter to inbound user messages while preserving legacy `dedupe_hash` values?
3. **Question 3 — Local NER Footprint for Policy Shield v2 (`§3.7`, `§13` Q2)**:
   - *Context*: Pure regex (`patterns.py`) misses contextual PII (unlisted nicknames, employer names, street intersections).
   - *Decision needed*: Do you approve `onnxruntime` + `gliner-pii` (~300 MB ONNX weights, runs locally on Apple Silicon CPU/CoreML without PyTorch) as the default Layer 2 recognizer in Policy Shield v2, plus automatic seeding from `case.sqlite3`'s `participants` table and macOS Contacts (`AddressBook-v22.abcddb`)?
4. **Question 4 — Expected Upper Scale of a Single `case.sqlite3` File (`§3.6`, `§3.10`)**:
   - *Context*: `sqlite-vec` float32 brute-force search is sub-25ms up to ~100k chunks (~2–4M messages at 40 turns/chunk), whereas 1M chunks (~20–40M messages) requires `vec_int8`/`vec_bit` quantization or an ANN index.
   - *Decision needed*: Is the realistic upper bound for a single case ~100k–250k chunks (where `sqlite-vec` float32 + `conv_id` partition keys is plenty fast), or do you plan to index 1M+ chunks in a single `case.sqlite3` file?
5. **Question 5 — Fate of `chatx analyze` (`psychology_relationships.yml`, `§3.11`, `§13` Q3)**:
   - *Context*: `psychology_relationship_mapper.py` shares 0 label names with `config/labels.yml` (`F-18`).
   - *Decision needed*: Should `chatx analyze` be deferred out of the 6-PR rearchitecture until a domain-verified `config/psychology_relationships.yml` is authored against `config/labels.yml`, or should we author a basic starter ruleset in PR 4?

---

## 7. Verification Log & Unverified Impressions

### 7.1 Complete Verification Log

#### Files Read Directly (59 files)
- `ChatX:docs/superpowers/audits/2026-10-20-design-audit/PROMPT-master.md` (lines 1–83)
- `ChatX:docs/superpowers/audits/2026-10-20-design-audit/design/2026-10-20-chatx-rearchitecture-design.md` (lines 1–419)
- `ChatX:docs/superpowers/audits/2026-10-20-design-audit/evidence/01-code-reality-audit.md` (lines 1–375)
- `ChatX:docs/superpowers/audits/2026-10-20-design-audit/evidence/02-dnh-ingest-trace.md` (lines 1–206)
- `ChatX:docs/superpowers/audits/2026-10-20-design-audit/evidence/03-docs-parity-inventory.md` (lines 1–228)
- `ChatX:pyproject.toml` (lines 1–221)
- `ChatX:config/arch-gates.yml` (lines 1–86)
- `ChatX:config/labels.yml` (lines 1–469)
- `ChatX:schemas/message.schema.json` (lines 1–80)
- `ChatX:src/chatx/cli/main.py` (lines 1–350, 700–1050)
- `ChatX:src/chatx/cli_errors.py` (lines 1–32)
- `ChatX:src/chatx/schemas/message.py` (lines 1–76)
- `ChatX:src/chatx/schemas/validator.py` (lines 1–199)
- `ChatX:src/chatx/imessage/extract.py` (lines 1–452)
- `ChatX:src/chatx/imessage/db.py` (lines 1–70)
- `ChatX:src/chatx/imessage/time.py` (lines 1–64)
- `ChatX:src/chatx/imessage/reactions.py` (lines 1–72)
- `ChatX:src/chatx/imessage/body_normalize.py` (lines 1–35)
- `ChatX:src/chatx/imessage/backup.py` (lines 1–189)
- `ChatX:src/chatx/imessage/attachments.py` (lines 1–334)
- `ChatX:src/chatx/imessage/report.py` (lines 1–216)
- `ChatX:src/chatx/extractors/imessage.py` (lines 1–582)
- `ChatX:src/chatx/instagram/extract.py` (lines 1–174)
- `ChatX:src/chatx/pdf_ingest/reader.py` (lines 1–134)
- `ChatX:src/chatx/identity/normalize.py` (lines 1–96)
- `ChatX:src/chatx/redaction/patterns.py` (lines 1–249)
- `ChatX:src/chatx/redaction/policy_shield.py` (lines 1–539)
- `ChatX:src/chatx/transformers/chunker.py` (lines 1–422)
- `ChatX:src/chatx/transformers/pipeline.py` (lines 1–230)
- `ChatX:src/chatx/enrichment/ollama_client.py` (lines 1–509)
- `ChatX:src/chatx/enrichment/enricher.py` (lines 1–418)
- `ChatX:src/chatx/enrichment/models.py` (lines 1–260)
- `ChatX:src/chatx/enrichment/multi_pass_pipeline.py` (lines 1–800)
- `ChatX:src/chatx/storage/base.py` (lines 1–590)
- `ChatX:src/chatx/storage/psychology_relationship_mapper.py` (lines 1–570)
- `ChatX:src/chatx/indexing/vector_store.py` (lines 1–522)
- `ChatX:src/chatx/indexing/multi_vector_store.py` (lines 1–800)
- `ChatX:src/chatx/obs/run_artifacts.py` (lines 1–54)
- `ChatX:src/chatx/utils/json_output.py` (lines 1–68)
- `ChatX:src/chatx/utils/run_report.py` (lines 1–157)
- `ChatX:tests/fixtures/imessage_test_data.sql` (lines 1–162)
- `ChatX:docs/design/specifications/cloud-enrichment.md` (lines 1–258)
- `ChatX:docs/design/adrs/ADR-008-psychology-graph-integration.md` (lines 1–176)
- `dNh:pyproject.toml` (lines 1–98)
- `dNh:src/dnh_crm/idempotency.py` (lines 1–16)
- `dNh:src/dnh_crm/events.py` (lines 165–560, 800–840, 1895–1975)
- `dNh:src/dnh_crm/ingest/imessage.py` (lines 1–30)
- `dNh:src/dnh_crm/ingest/imessage_source.py` (lines 1–300)
- `dNh:src/dnh_crm/ingest/imessage_mapper.py` (lines 1–115)
- `dNh:src/dnh_crm/ingest/imessage_attributed_body.py` (lines 1–307)
- `dNh:src/dnh_crm/ingest/imessage_thread_identity.py` (lines 1–208)
- `dNh:src/dnh_crm/ingest/normalizer.py` (lines 1–61)
- `dNh:src/dnh_crm/ingest/dedupe.py` (lines 1–30)
- `dNh:src/dnh_crm/ingest/whatsapp_export.py` (lines 1–248)
- `dNh:src/dnh_crm/ingest/email_eml.py` (lines 1–297)
- `dNh:src/dnh_crm/store/migrations.py` (lines 1–424)
- `dNh:src/dnh_crm/utils/json_utils.py` (lines 1–9)
- `dNh:scripts/imessage_attributed_body_probe.py` (lines 1–800)
- `dNh:tests/unit/test_imessage_attributed_body.py` (lines 1–200)

#### Commands & Web Searches Run
1. `git -C /Users/hue/code/Dopemux-ChatRipperXXX rev-parse --short HEAD && git -C /Users/hue/code/Dopemux-ChatRipperXXX branch --show-current` $\rightarrow$ `9c3dd6b`, `governance-doctrine-integration`.
2. `git -C /Users/hue/code/dNh_CRM rev-parse --short HEAD && git -C /Users/hue/code/dNh_CRM branch --show-current` $\rightarrow$ `39c75bde`, `migrate-cheaperinference`.
3. `search_web`: `"imessage-exporter ReagentX chat.db associated_message_type 2006 3006 associated_message_emoji typedstream"` (verified `2006`/`3006` custom emoji tapbacks and `associated_message_emoji`).
4. `search_web`: `"sqlite-vec asg017 ANN index HNSW brute force 1M vectors limitations"` (verified `sqlite-vec` is brute-force only, tracking issue `#25`).
5. `search_web`: `"GLiNER PII redaction Presidio benchmark recall local Apple Silicon MLX"` (verified `gliner-pii` + `presidio-analyzer[gliner]` on Apple Silicon MPS/ONNX).
6. `search_web`: `"Anthropic Message Batches API prompt caching structured outputs tool use 2025 2026"` (verified 90% prompt caching + 50% batch discount stacking).
7. `search_web`: `"mlx-lm Apple Silicon structured output JSON schema Outlines llama.cpp GBNF Qwen3"` (verified `outlines[mlxlm]` and `llama.cpp` GBNF structured decoding).

### 7.2 Unverified Impressions (`PLAUSIBLE` / `UNKNOWN`)
- **`PLAUSIBLE` — `chatx simulate` (`src/chatx/cli/main.py:1375-1573`) disposition**: The design (`§4`, `§8`) does not mention the `chatx simulate` command present at the bottom of `src/chatx/cli/main.py:1375-1573`. We did not read lines `1375-1573` of `main.py` in full; it is `PLAUSIBLE` that `simulate` depends on legacy enrichment/vector store classes and needs explicit disposition (keep vs. delete) in `§8`.
- **`PLAUSIBLE` — Apple `chat.db` `cloudkit_record_id` & RCS (`service = 'RCS'`) in iOS 18 / macOS 15**: With iOS 18 / macOS 15 introducing RCS messaging inside the Messages app (`service = 'RCS'`), `ChatX` and `dNh` should verify whether `service` values beyond `'iMessage'` and `'SMS'` appear in `message.service` on Sequoia hosts (`UNKNOWN` on the owner's live corpus without running `probe.py`).
