# ChatX Rearchitecture — Design

| | |
|---|---|
| Status | **Revision 2.1.** Rev 2 applied the audited revision plan, as the owner instructed on 2026-10-21 ("apply"); a builder check of rev 2 followed and its points are settled in this text and listed in §14. Rev 2.1 (2026-10-22) records three owner decisions from the P0 packet's gaps (§14, last block) and rewords one P0 exit criterion; nothing else changed. Next step: build P0 from `docs/superpowers/plans/2026-10-21-p0-workspace-packet.md`. Nothing is built yet. |
| Revisions | Rev 1, 2026-10-20: the brainstorm output, sha256 `c481b18880dae379ff2b39bfdeb0bd2d9e4a81956ee84deda4aae1cc8bd9f2a7`. It is kept unchanged at `docs/superpowers/audits/2026-10-20-design-audit/design/`. Rev 2, 2026-10-21: this file. Every change is listed in §14 with the finding IDs behind it. Rev 2.1, 2026-10-22: the P0 exit-criteria wording in §6 and the three decisions in §14's last block; no other text touched. |
| Owner | Houston (product); supervisor session (design) |
| Supersedes as statement of intent | Rev 1 of this file, `docs/architecture.md`, `docs/interfaces.md`, `docs/implementation.md`, `docs/operations/non-functional-requirements.md`, `docs/acceptance-criteria.md`, ADR-008 |
| Evidence base | **Rev 1's evidence:** a code-reality audit of `src/chatx`, a dNh_CRM ingest trace and a docs parity inventory (all 2026-10-20). **Design audit of rev 1:** five independent auditors (codex, grok, agy, opus, chatgpt-web) produced 148 findings. Their citations were checked line by line: 124 PASS, 13 PARTIAL, 11 UNKNOWN, 0 FAIL. An external fact check (E1–E9) followed, and the findings were grouped into a 23-theme cross-audit matrix. All of it is in `docs/superpowers/audits/2026-10-20-design-audit/`. Condensed in Appendix A. |

Reading guide: §3 holds the decisions and why; §3.15 is the threat model. §11 lists what is left to the builder. §12 records the owner's answers and the few follow-ups that remain. §13 lists the research targets, and §14 is the change log from rev 1.

Notation:
- **Findings** are written as auditor plus ID: `codex F05`, `grok F5`, `agy F-01`, `opus F-09`, `chatgpt F01`.
- **Themes** `T01`–`T23` are the cross-audit matrix rows.
- **`E1`–`E9`** are rows of `external-fact-check.md`.
- **`RT-n`** are research targets.
- **"Owner item n"** refers to §12.
- **UNKNOWN** means unverified; it must be settled by measurement, not assumption.
- **(decided)** marks a designer's call the owner may override.

---

## 1. Intent

ChatX is a **local-first tool for the owner's own message history**: a personal archive and analysis of conversations the owner took part in (owner item 11a).
- It pulls messages out of iMessage (a live `chat.db` or an iPhone backup), Instagram exports, WhatsApp exports, PDF transcripts and email.
- It turns them into one canonical record with evidence-grade provenance.
- It redacts them behind a privacy gate that actually blocks.
- It then supports search, structured enrichment, relationship analysis and reports. These run locally by default; cloud models are allowed only through the gate.

Two things changed since the current code was written:

1. **The code never delivered the pipeline.** Extraction is real and well tested. Every later stage is stubbed, never called by the CLI, or wired with a broken hand-off (Appendix A.1). The ≥99.5 % redaction "coverage" gate is a token ratio. By default it only warns and exits 0; only `--preflight` can block. `--allow-cloud` guards a cloud client that does not exist.
2. **The stack is dated and duplicated.** It hardcodes `gemma2:9b`, uses Chroma and Neo4j, keeps Pydantic-v1 idioms and has a `claude-3-sonnet-20240229` literal. Meanwhile the sibling repo **dNh_CRM** grew its own iMessage, WhatsApp and email parsers. Those include a *real* `attributedBody` typedstream decoder that ChatX lacks. But dNh has no reactions, replies, inline attachments or outbound messages, which ChatX has.

So this is a rebuild around three things: one shared extraction core, a privacy gate that is a real gate, and a storage and model layer that matches current offerings and the owner's actual machine.

**What "forensic" means here** *(narrowed in rev 2, chatgpt F26)*. The bundle and source checks prove less than the word usually implies:
- A verified export bundle shows that its files are the ones the tool wrote at export, provided the manifest hash or signature is trusted.
- The `sources` records show what was acquired and when, with hashes.
- Neither shows that a source was complete, or that the device data was authentic.
- The docs use "forensic" only with this qualification. Bundles are for the owner's own records.

### Success looks like

- **Import.** One command imports a real `chat.db` (or backup) into a case. Every message carries its text, reactions, replies, attachments with hashes, and provenance you could defend:
  - Text comes from the `text` column, or from the typedstream decoders when that column is empty.
  - Where text cannot be decoded, the raw blob and its decode status are kept.
- **dNh.** dNh_CRM imports the same core package. After a 30-day parallel run with no disagreements, it deletes its own chat.db parsers.
- **Cloud gate.** `--allow-cloud` sends nothing unless all of these hold:
  - the shield's measured recall meets the target, as a 95 % lower bound of 0.995 for every entity class (§3.7), on the owner's labelled real sample;
  - the chunk carries no local-only label;
  - the vendor terms are declared as zero retention and no training;
  - the request matches its gate token byte for byte.
  A failure is an exit code, not a yellow line.
- **No services.** Search, enrichment and reports run against one case directory — one SQLite database plus content-addressed attachments — with no services to start.
- **Configuration only.** Swapping the local model, or pointing the cloud tier at Claude, is a configuration change, and the tool probes each model's capabilities instead of assuming them.
- **Gates.** Lint, types and tests are green. The ≥90 % coverage gate is computed over **both whole packages**, not an omit list, and the shield and gate code also carry branch coverage and a mutation-testing floor.

---

## 2. Goals, non-goals, anti-goals

**Goals**

- G1 Shared extraction core used by ChatX and dNh_CRM, emitting one canonical message contract with stable ids.
- G2 Privacy gate with measured recall on owner-labelled real samples, a content-sensitivity policy, hard-fail classes and pseudonym round-trip. The cloud tier fails closed.
- G3 **Single-directory case**: one SQLite database (with sqlite-vec and FTS5) plus content-addressed attachments beside it. Attachments are never in the database and never uploaded.
- G4 Provider abstraction with two protocols:
  - **Chat providers:** any OpenAI-compatible endpoint, and the Anthropic SDK.
  - **Embedding providers:** local only.
  Model ids are configuration, and capabilities are probed, not assumed.
- G5 Enrichment against the taxonomy (`config/labels.yml`, schema 1.3, per-label `cloud_allowed`). It uses structured outputs, typed outcomes, per-record provenance and a cache, with thresholds calibrated on an owner-labelled gold set.
- G6 Hybrid search with message-level citations, and an export bundle with a hash manifest, a custody record and an optional signature.
- G7 Analysis lane (relationships, episodes, observable-pattern indicators) as a later, opt-in phase on the same store, with no graph database.
- G8 Quality gates that are real: whole-package coverage, contract tests, golden fixtures from real schema snapshots, and measured (not promised) performance numbers.

### 2.1 Intended use *(new in rev 2: opus F-26; owner items 11a, 11b)*

- **Whose data:** the owner's own conversations. The data also contains third parties who never consented to analysis. Every rule below exists for their sake as much as the owner's.
- **What for:** a personal archive and the owner's own analysis. Bundles are for the owner's own records. ChatX is not a service for processing other people's exports. It is not a tool for certifying evidence to third parties (§1).
- **Cloud:** only redacted chunks may leave the machine, and only under all of these conditions:
  - after the real-sample gate passes;
  - never with a special-category label (§3.7);
  - only under vendor terms the owner declares as zero data retention and no training (`E_VENDOR_TERMS` otherwise).
- **Deletion:**
  - `chatx case delete-source` removes one source and everything derived from it.
  - `chatx case purge` deletes a case and its secrets. It keeps one audit line outside the case, recording that the purge happened.
- **Analysis outputs** are model inferences about patterns in text. They are not findings about people (§3.11).

**Non-goals (for this program)**

- An HTTP API or web UI. CLI and, later, an MCP server only.
- Multi-user, multi-tenant, or server deployment.
- Live message capture (BlueBubbles etc.). That remains dNh_CRM's concern; the core is batch and export oriented.
- Telegram export parsing. dNh's Telegram path is the Bot API, which stays in dNh.
- Differential-privacy summaries, until a consumer exists (dead code today, Appendix A.1).
- `reply`/`simulate` (generating messages) and any outbound action (§8 disposition table).
- Bit-reproducible model output. No backend guarantees it (opus F-27, E3). The cache is the reproducibility mechanism.
- Proving source completeness or device authenticity (§1).

**Anti-goals (would make this a failure even if it worked)**

- Any path where un-redacted text, or any attachment, reaches a provider that the locality check (§3.6) does not classify as local. This includes an MCP client (§3.12).
- Sending chunk text to a cloud embedding service.
- Any chunk carrying a special-category or other local-only label reaching a cloud model.
- A "coverage" or "privacy score" that is not a measured recall/precision against labels.
- Hardcoded model ids, endpoints, or passwords in code.
- A second copy of any parser in either repo once the 30-day parallel run (§9) ends.
- Coverage gates satisfied by excluding modules.
- Fabricated data: a timestamp set to "now", a time zone assumed silently, or placeholder text standing in for an undecoded body.

---

## 3. Decisions made

Each decision records the choice, the alternatives considered, and the reason. Owner-made decisions are marked **(owner)**. The owner's 2026-10-21 answers are cited by item number (§12). The rest are the designer's calls.

### 3.1 Seam: shared extraction core **(owner)**

One Python package, `chat-extraction-core`, owns the parsers and the canonical schema. ChatX and dNh_CRM both depend on it. Alternatives rejected:
- **ChatX as sole extractor feeding dNh:** dNh needs imports it can run itself.
- **Schema-only alignment:** keeps two copies of every parser.
- **ChatX consuming dNh's event store:** loses reactions, backups, Instagram and PDF.

### 3.2 Layout: dedicated workspace directory **(owner)**, new repository **(owner, item 1)**

```
~/code/chatstack/                     # new git repo, uv workspace root
  pyproject.toml                      # [tool.uv.workspace] members = ["packages/*", "apps/*"]
  uv.lock
  packages/chat-extraction-core/      # the shared core (G1), MIT
  apps/chatx/                         # the ChatX application
~/code/dNh_CRM/                       # stays where it is
  pyproject.toml                      # release: chat-extraction-core pinned to a tagged wheel by version and sha256
~/code/Dopemux-ChatRipperXXX/         # archived: tagged, read-only reference
```

- **No workspace root at `~/code`.** It was verified absent; a root there would sit above every repo the owner has.
- **New repo, not a history carry.** The owner confirmed this on 2026-10-21. The keep-list (§8) is ported file by file, each with a `Ported from Dopemux-ChatRipperXXX@<sha>` header. History stays in the old repo under the tag `pre-rearchitecture-2026-10-20`.
- **How dNh consumes the core** *(rev 2: opus F-10, codex F21, chatgpt F29, E8)*:
  - **Release builds** depend on a **built wheel pinned by version and sha256**. "dNh pins the version" means bytes, not a string.
  - **Release contract:** core releases are git tags `core-vX.Y.Z`. The wheel and its sha256 are built in CI from a clean tree, and dNh's lock records that hash. Before tagging, the core's CI runs dNh's adapter tests against the new wheel.
  - **Development branches** may use either form; uv documents both (E8):
    - `{ path = "../chatstack/packages/chat-extraction-core", editable = true }` is a plain path dependency. It does not apply the other workspace's lock or sources.
    - `{ workspace = "../chatstack" }` resolves the member by name.
  - P0 proves both forms from clean clones.
- **Licence and ownership** *(owner item 13)*: the core is MIT-licensed, like ChatX, and owned by the owner (DDD-Enterprises). Proprietary dNh may depend on it. Third-party notices ship with both packages.
- **dNh changes** go through dNh's own governance (its `AGENTS.md` and task packets). This program demonstrates them on a dNh branch; merging is dNh's decision.

### 3.3 Toolchain

- **Python and SQLite.** Python `>=3.12`, dNh's floor. The interpreter is chosen by the **SQLite library it links** *(rev 2: codex F28, chatgpt F37, E4)*:
  - **Why:** sqlite.org documents a WAL-reset bug. It can corrupt a WAL database when two connections write or checkpoint at the same moment. It affects 3.7.0 through 3.51.2 and is fixed in 3.51.3.
  - **Floor:** the runtime must link SQLite ≥ 3.51.3, or a 3.50.x ≥ 3.50.7, or a 3.44.x ≥ 3.44.6 (the backports).
  - **Enforcement:** every run records `sqlite3.sqlite_version`. A runtime below the floor refuses to open a case with `E_SQLITE_TOO_OLD`.
  - **Measured 2026-10-21:** the old ChatX and dNh venvs link 3.47.1, which is below the floor. mise's Python 3.12.13 links 3.53.1.
- **Tools:** `uv` (0.12.11 present), hatchling, `ruff`, `mypy --strict` for the core and a strict configuration for the app, `pytest` + `pytest-cov`, `pre-commit`, and `uv lock --check` in CI.
- **The core's dependencies are listed:** `pydantic>=2,<3` and `phonenumbers>=8,<9`, nothing else *(rev 2: grok F18, codex F22)*. The core has **no network, no LLM and no storage dependencies**. Two tests enforce this: an import-graph test asserts it, and a socket guard fails any core test that opens a socket.
- **App dependency bounds** are lower and upper (`>=x,<next-major`). dNh never installs the app, so these cannot conflict with dNh's pins.
- **Package data** is loaded through `importlib.resources`; there is no `Path(__file__).parents[n]`. A missing schema resource is an error (`E_SCHEMA_MISSING`), never a skip (chatgpt F30).
- **Model artifacts** (NER, embedding and judge models) are pinned by repository, revision and file sha256, alongside the dependency hashes, and provisioned ahead of time. Runs set `HF_HUB_OFFLINE=1` (chatgpt F36, opus F-11).
- **`docs/reference/conformance.md`** *(chatgpt F38)* lists each external component with the version tested, the date and the evidence (a link or a test). The components are SQLite, sqlite-vec, Presidio, the NER models, the local model server, the Anthropic API and model ids, and uv. `chatx providers check` and P0 CI write what they observe; anything not observed stays UNKNOWN.

### 3.4 Canonical message contract v2

**Source of truth.** The Pydantic model in the core is the single source of truth. The JSON Schema is **generated** from it and committed (`schemas/chat.message.v2.schema.json`), and a test fails if the two drift. The version string is `chat.message.v2-draft` until the P0.5 real-database probe has run (§6). It is frozen as `chat.message.v2` after that, not before *(rev 2: grok F10)*.

**Rules.** From the dNh side: `extra="forbid"`, frozen models, and timezone-aware UTC `sent_at`, with how the zone was obtained recorded (`time_source`). From the ChatX side: reactions, replies, inline attachments, outbound messages and source path provenance.

**Canonical form and hashes** *(rev 2: codex F02, grok F13, agy F-02, opus F-01)*.
- **Canonical JSON:** UTF-8, NFC-normalized strings, keys sorted, no insignificant whitespace, and no floats in hashed fields. This is RFC 8785 (JCS) semantics. dNh's `canonical_json` helper is checked against JCS or replaced by a JCS library (RT-2).
- **`content_hash`** is a sha256 over the **immutable message core**: `platform, conv_id, msg_id, direction, sent_at, sender.handle, text, text_source, content_kind, reply_to_msg_id, thread_originator_id`, and the sorted `attachments[].sha256`.
- **Never in `content_hash`:** `sender.pseudonym`, `reactions`, `edit`, `attachments[].missing/missing_reason/storage_ref/source_path`, `source_meta` and `provenance`. They arrive later or describe where the message was seen.
- **`record_hash`** is a sha256 over the whole canonical record except `provenance`. It changes when anything about the message changes, including late reactions or edits.
- **Why `provenance` is excluded** *(decided)*: `provenance` holds `extracted_at`, and re-importing must not change `record_hash`.

**Five things v1 ran together** *(chatgpt F06)*:
1. **Message identity**: `msg_id`.
2. **Source observation**: `message_observations(msg_id, source_id, source_row, record_hash)`. One message seen in two overlapping exports is one message row with two observations.
3. **Revision**: `record_hash`.
4. **Content**: `content_hash`.
5. **Raw evidence integrity**: the acquired file's sha256 in `sources` (§3.5).

**Id stability contract** *(chatgpt F06, opus F-13; the `msg_id` formula was confirmed by the owner on 2026-10-21)*.
- **Native ids:** the platform id where one exists (iMessage `guid`).
- **Derived ids:** `sha256(platform, conv_id, sent_at, sender.handle, text, occurrence)[:32]`. `occurrence` counts earlier messages in the same source with the same `(platform, conv_id, sent_at, sender.handle, text)`, in source order, starting at 0. Identical messages sent in the same minute no longer collide.
- **What is guaranteed:**
  - Re-importing the same source reproduces every id.
  - A later, longer export of the same chat keeps the ids of the messages it shares with the earlier one. The documented limit: messages in the same minute deleted between the two exports. The test uses two overlapping WhatsApp exports.
  - The row index is stored as `provenance.source_row`, where the message was seen. It is never part of the identity.
- **When a later schema version changes an id formula,** `msg_id_aliases(old_id, new_id, schema_version)` keeps old citations resolvable. Ids are never rewritten in place.
- **Declined (decided):** a source-file fingerprint inside `msg_id` (opus F-13's suggestion). It would change every id on re-export.

**Fields**

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `Literal["chat.message.v2-draft"]`, then `"chat.message.v2"` | frozen after the P0.5 probe |
| `msg_id` | str | per the id stability contract above |
| `msg_id_kind` | enum `native, derived` | |
| `conv_id` | str | platform thread id (`chat_guid`) or derived per source; multi-chat rule below |
| `platform` | enum `imessage, sms, instagram, whatsapp, email, pdf_transcript` | `telegram` and `txt` removed until an importer ships them (opus F-33) |
| `direction` | enum `inbound, outbound, system` | `is_me` is a computed property (= `outbound`), not a stored field |
| `sender` | `Sender{handle, handle_kind, display_name?, pseudonym?}` | `handle_kind` enum `e164, email, username, display_name, raw`; phones normalized with `phonenumbers` and the case's `default_region` (§3.5); unparseable → raw handle, `handle_kind=raw`; `pseudonym` is the HMAC join key and is never placed in model input (§3.7) |
| `sent_at` | datetime (aware, UTC) | required |
| `sent_at_raw` | str | the source value verbatim (Apple integer, export string, header) (chatgpt F02) |
| `time_precision` | enum `ns, s, minute, day` | |
| `time_source` | enum `platform_utc, assumed_tz, explicit_tz` | `assumed_tz` is an assumption on record, and reports say so |
| `source_tz` | IANA name \| None | |
| `text` | str \| None | |
| `text_source` | enum `text_column, attributed_body, caption, transcript, none` | `ocr` removed (no OCR engine, opus F-33) |
| `text_decode_status` | enum `decoded, unsupported, malformed, not_attempted` | the decoder's status, kept as evidence (opus F-34) |
| `content_kind` | enum `text, attachment_only, reaction_only, system, empty, unsupported` | `unsupported` = an app message (`balloon_bundle_id`) with no decoder (chatgpt F07) |
| `system_event` | `SystemEvent{kind, group_action_type, group_title, affected_handles}` \| None | unknown codes → `kind=unknown` with raw codes kept |
| `reply_to_msg_id` | str \| None | from `thread_originator_guid` (+ `reply_to_part` from `thread_originator_part`) |
| `reply_to_part` | int \| None | |
| `thread_originator_id` | str \| None | |
| `reactions` | list[`Reaction{from_handle, kind, emoji?, target_part?, removed, at, raw_code}`] | `kind` enum `love, like, dislike, laugh, emphasize, question, emoji, unknown` |
| `attachments` | list[`Attachment{attachment_id, kind, filename, mime_type?, uti?, byte_size?, sha256?, storage_ref?, source_path?, missing, missing_reason?}`] | `kind` enum `image, video, audio, file, sticker, unknown`; `missing_reason` enum `not_found, outside_root, unreadable, hidden, not_in_backup` |
| `edit` | `Edit{edited_at?, unsent, prior_texts}` \| None | iMessage edits and unsends |
| `provenance` | `Provenance{source_kind, source_id, source_path, source_row, source_locator, source_guid?, extracted_at, extractor_version, content_hash, record_hash}` | `source_kind` enum `chat_db, iphone_backup, instagram_zip, whatsapp_export, pdf, eml`; `source_locator` per importer (§4) |
| `source_meta` | dict | **required for iMessage**: every selected column that has no canonical field, verbatim. It is the forensic raw layer, not an optional extra |

**iMessage column manifest** *(rev 2: codex F01, grok F4, agy F-09, chatgpt F07)*. The reader selects these columns when they are present.

| Table | Columns |
|---|---|
| `message` | `ROWID, guid, text, attributedBody, payload_data, message_summary_info, handle_id, date, date_read, date_delivered, is_from_me, is_read, is_sent, is_delivered, is_audio_message, item_type, group_action_type, group_title, associated_message_guid, associated_message_type, associated_message_emoji, thread_originator_guid, thread_originator_part, reply_to_guid, balloon_bundle_id, date_edited, date_retracted, cache_has_attachments, error, service, account, destination_caller_id, expressive_send_style_id` |
| `chat` | `ROWID, guid, chat_identifier, display_name, service_name, group_id, style, is_archived` |
| `attachment` | `ROWID, guid, filename, uti, mime_type, transfer_name, total_bytes, is_sticker, hide_attachment, created_date` |
| `handle` | `ROWID, id, service, country` |
| joins | `chat_message_join`, `chat_handle_join`, `message_attachment_join` |

- **Schema probe at open.** `PRAGMA table_info` records which manifest columns exist in each source (macOS versions differ) in `sources.schema_probe`.
  - An absent column becomes `None`, and the probe lists it.
  - An absent optional column never fails the import.
  - A manifest column is never skipped silently.
- **Raw blobs.** `attributedBody`, `payload_data` and `message_summary_info` are kept in `message_blobs(msg_id, column, sha256, bytes)`. An app message or an edit history that cannot be decoded today can then be decoded later from the case, without re-acquiring the source.

**iMessage mapping rules** *(rev 2: T03, T06)*:
- **Replies.** `reply_to_msg_id` comes from `thread_originator_guid`. `associated_message_guid` is used for reactions only.
- **Reactions.**
  - Strip `p:<part>/` and `bp:` from `associated_message_guid` and keep the part as `Reaction.target_part`. Without this, reactions cannot link to their targets in real databases (agy F-07).
  - Codes 2000–2005 add a reaction by kind, and 3000–3005 remove it.
  - Codes 2006/3006 are `kind=emoji`, with `emoji` taken from `associated_message_emoji` (V1 still verifies this on a real database).
  - Any other code is `kind=unknown`, with the raw code kept. Nothing is mapped to "custom" by range.
  - Reactions travel inside the canonical record but are stored as their own rows, keyed by target `msg_id`, so a late reaction never rewrites a message row.
- **Stickers.** Code 1000 is a sticker attachment, not a reaction.
- **Edits and unsends.**
  - `edit.edited_at` comes from `date_edited`, and `edit.unsent` is set when `date_retracted IS NOT NULL`.
  - Prior texts come from the typedstream edit history when it decodes. Otherwise `prior_texts` is `[]` and `source_meta.edit_history_undecoded` is true.
  - The plist keys inside `message_summary_info` per macOS version are read by the probe before the decoder is ported (opus F-16).
- **Group events.** A message with `item_type != 0` gets `content_kind = system` and a `system_event`.
- **Multi-chat.** A message joined to more than one chat is emitted once:
  - its `conv_id` is the lowest `chat.ROWID`, so the choice is deterministic;
  - `source_meta.chat_ids` lists every chat, and the store keeps a `message_conversations` join table;
  - the import report counts multi-chat messages (agy F-20).
- **Participants.** `chat_handle_join` is snapshotted into `participants(conv_id, handle, membership = snapshot_at_import)`. Earlier membership is recorded as unknown, not as absent; `chat.db` does not keep membership history (stated limitation).

**Decoding guarantee: partial** *(rev 2: codex F06, agy F-10, opus F-34, chatgpt F09)*. Text is decoded where one of these strategies succeeds, tried in order:
1. dNh's bounded, fail-closed typedstream decoder (`MAX_INPUT_BYTES = 256 * 1024`, `MAX_OUTPUT_BYTES = 64 * 1024`).
2. A generic typedstream walker (RT-3).
3. Otherwise `text_source = none`. The blob is kept and its status recorded.
Text that is empty once U+FFFC (the inline-attachment marker) and whitespace are removed becomes `text = None`, with `content_kind = attachment_only` (or `empty` when there is no attachment). No placeholder text is ever written. Recovery is measured on the owner's real blobs by the P0.5 probe, not claimed from fixtures.

**Time rules** *(rev 2: codex F03, grok F6, chatgpt F02)*:
- **One Apple-epoch converter** in the core:
  - epoch 2001-01-01;
  - `0` means unset and becomes `None`;
  - units (ns, µs or s) are inferred within the bounds **2001–2100**;
  - it is property-tested.
- **Sources with no time zone** (WhatsApp exports, PDF transcripts) **require** `--assume-tz <IANA>` at import. Without it the import refuses with `E_TZ_REQUIRED`; there is no default and no silent UTC.
- **An unparseable timestamp** quarantines the row (reason `unparseable_timestamp`), keeping `sent_at_raw` so a later parser fix can re-import it. A timestamp is never set to "now" or inherited.
- **Messages with equal `sent_at`** keep their source order through `provenance.source_row`.

### 3.5 Storage: SQLite per case **(owner)**; case per import set **(owner, item 2)**

**What a case is.** A case holds one or more source imports. Contact is a query filter, not a case boundary, and a message lives in exactly one case.

**Case settings** *(decided, builder check)*, fixed at `chatx case create`:
- `default_region` for phone numbers. It is required, with no implicit default, because it shapes `sender.handle` and so `msg_id`. Changing it later re-normalizes handles and records `msg_id_aliases`.
- `owner_handles`: the owner's phone numbers, emails, usernames and display names. Sources that do not mark direction themselves (WhatsApp, PDF, email) take it from these; `--me` adds to them for one import.
- `languages`: the languages the shield is evaluated for (default `en`, §3.7).

Rejected for storage:
- **Postgres + pgvector:** no server exists on this machine, dNh is not on Postgres, and a service buys nothing at single-user scale.
- **Keeping Chroma + Neo4j:** two services, and the graph layer is dead today.

**Case root** *(rev 2: opus F-11, owner item 7)*:
- **Default location:** `~/Library/Application Support/chatx/cases.noindex/`, mode 0700. The `.noindex` suffix keeps Spotlight out.
- **Refused locations:** roots inside iCloud-synced folders (Desktop & Documents, iCloud Drive).
- **Time Machine:** case creation offers an exclusion.
- **FileVault:** required at case creation, checked with `fdesetup status`. `--allow-unencrypted-disk` overrides it, and the case records the override.
- **Per-case encryption:** opt-in (`chatx case create --encrypt`). It is off by default because SQLCipher has not yet been shown to work with sqlite-vec and FTS5 (RT-19).

```
cases.noindex/<case-id>/
  case.sqlite3                 # evidence, derived and operational tables (below)
  sources/<source-id>/         # acquired evidence copies: chat.db snapshot, Manifest.db snapshot, export files
  attachments/<aa>/<sha256>    # content-addressed bytes, stored exactly (EXIF never stripped)
  attachments/.tmp/            # in-flight CAS writes; reported by `case verify`, swept at start
  secrets/                     # 0700: salt and pseudonyms.sqlite3 (0600); never in a bundle by default
  tmp/                         # 0700 scratch; swept at start; nothing goes to /tmp
  exports/<run-id>/
  logs/<run-id>.jsonl
  manifest.json
  .lock
```

**Acquisition** *(rev 2: codex F05, grok F5, agy F-01, opus F-09, chatgpt F01)*. This replaces rev 1's "WAL-safe copy" and its `immutable=1` open.
- **Who does it** *(decided, builder check)*. The core implements acquisition and writes only to the path the caller passes. Its "no storage" rule means no database or persistence layer of its own. The app chooses the path and records the result in `sources`.
- **Snapshot.** The live database is opened `mode=ro`. The **SQLite online backup API** (`sqlite3.Connection.backup`) copies it into `sources/<source-id>/chat.sqlite3`. The backup API produces a self-contained database, including WAL contents, which is then opened `mode=ro`.
- **Check.** The snapshot is checked with the full `PRAGMA integrity_check`.
- **What `sources` records for each acquisition:**
  - the source file sizes, mtimes, and sha256 of `chat.db`, `-wal` and `-shm` as seen;
  - the snapshot's sha256 and `sqlite_version`;
  - the integrity result;
  - row counts and `MAX(ROWID)` for `message`, `chat` and `attachment`, so a later re-acquisition can show what changed.
- **Failure.** If the backup cannot complete (a locked database, or Full Disk Access denied), the import exits with `E_DB_LOCKED` or `E_DB_ACCESS_DENIED`. There is no fallback to copying raw files.
- **Same path for others.** iPhone backups acquire `Manifest.db` the same way. Export files (Instagram ZIP, WhatsApp text, PDF, `.eml`) are copied into `sources/` with their sha256.
- **The snapshot is the evidence copy.**
- **Fixture test.** A fixture test writes rows into a WAL database without checkpointing, snapshots it, and asserts the rows are present.

**Acquisition context** *(chatgpt F10)*. One `AcquisitionContext` is resolved once at import start and stored in `sources`. It holds:
- the source id;
- live or backup;
- the allowed attachment roots and `backup_dir`;
- the `Manifest.db` snapshot;
- the contact scope.
It is passed to extraction, attachment resolution and the missing-attachments report, so they cannot disagree.

A contact-scoped import selects the chats whose participants include the contact (group chats included and flagged), then every message in those chats, in both directions. The v1 filter `OR m.is_from_me = 1`, which pulled the owner's messages from every chat, is retired.

**Tables** *(DDL is the builder's; rev 2 adds the evidence/derived split, chatgpt F24)*:
- **Evidence:**
  - `cases`, `sources`, `conversations`, `message_conversations`, `participants`;
  - `messages`, `message_observations`, `msg_id_aliases`, `message_blobs`;
  - `reactions`, `attachments`, `message_attachments`, `quarantine`.
- **Derived (disposable; `chatx case repair` rebuilds them from the evidence):**
  - `chunks`, `redactions`, `shield_evals`, `enrichments`;
  - `embedding_spaces`, plus one `vec0` table per space;
  - `fts_messages`, `fts_chunks`, and `analysis_*`.
- **Operational:** `runs`, `schema_migrations`.

**Invariants and concurrency** *(rev 2: codex F12, agy F-21, chatgpt F24)*:
- **Single writer.** `cases/<case>/.lock` takes an exclusive `flock`; a second `chatx` process on the same case gets `E_CASE_LOCKED`. Pseudonym allocation (§3.7) relies on this lock.
- **PRAGMAs:** `journal_mode=WAL`, `synchronous=NORMAL` (`FULL` for the import commit), `foreign_keys=ON`, `busy_timeout=5000`, and `secure_delete=ON`, so deleted content is overwritten rather than left in free pages.
- **Runs and transactions.** Every stage opens a `runs` row first and closes it last; batches are transactions.
- **Crashes.** A crashed run leaves `status=running`, which `case verify` reports. `case resume` restarts from the run's watermark (`last_source_row`).
- **Source status.** A source stays `status=partial` until its last import batch commits, then becomes `complete`.
- **Foreign-key policy:**
  - `messages` → `reactions`/`message_attachments`/`chunks`/`enrichments` is `ON DELETE CASCADE`.
  - `sources` → `messages` is `RESTRICT`. A source is removed only through `case delete-source`.
- **Migrations.** `schema_migrations(version, applied_at, checksum)` holds forward-only SQL files, run by a small runner in the app; there is no Alembic. `case verify` compares the applied checksums with the shipped files.
- **What `case verify` checks:**
  - every message has at least one observation;
  - every chunk's `msg_ids` exist with a matching `record_hash`;
  - the FTS row count equals the message count;
  - each embedding space has one vector per chunk;
  - attachment bytes re-hash to their names;
  - no stale `.tmp` files remain;
  - no run is left `running`.
- **Backup.** `chatx case backup` uses the SQLite backup API.

**Content-addressed attachment writes** *(rev 2: codex F07, F14, agy F-08, chatgpt F11)*:
- **Resolving a path:** `expanduser()`, then `resolve()`, then a **containment check** against the allowed roots (`~/Library/Messages/Attachments`, the backup directory, or `--attachments-root`). A path outside them gives `missing=true, missing_reason=outside_root`.
- **Backup mode** passes `backup_dir` through the whole call chain.
- **Writing:**
  1. Stream to `attachments/.tmp/<uuid>` while hashing.
  2. `fsync`.
  3. Atomic rename to `<aa>/<sha256>`.
  4. Verify the hash after the rename.
- **An existing object** is re-hashed before the new temp file is discarded. A mismatch replaces the stored object and is logged as corruption.
- **Bytes are stored exactly.** EXIF is never stripped from the stored object, and thumbnails or other derivatives are never exported.

### 3.6 Model access: chat and embedding providers **(owner: "both behind one interface")**

The owner's decision still holds: one place in the code talks to models, and both an OpenAI-compatible endpoint and the Anthropic SDK sit behind it. Rev 2 splits that place into two protocols (codex F15, grok F2, opus F-28), because chat and embeddings have different providers and different privacy rules:

```python
class ChatProvider(Protocol):
    def complete_structured(self, request: StructuredRequest, *, gate: GateToken | None) -> Outcome: ...
    @property
    def capabilities(self) -> Capabilities: ...   # structured-output mode, accepted sampling parameters, thinking modes, limits
    @property
    def identity(self) -> ProviderIdentity: ...   # kind, resolved host, locality verdict, requested model, observed model

class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def space(self) -> EmbeddingSpace: ...        # model, revision, dimension, quantization, distance
```

- **Implementations.** `OpenAICompatProvider` implements both protocols; it covers Ollama, LM Studio/MLX, vLLM and the llama.cpp server. `AnthropicProvider` implements `ChatProvider` only: Anthropic offers no embedding model (E1).
- **Embeddings are local only** *(decided)*. Embedding chunk text in the cloud would be egress. An `EmbeddingProvider` whose host is not local is refused. A remote embedder would contradict the anti-goal (§2); adding one needs a revised design, not configuration *(clarified, builder check)*.
- **Locality is computed, not declared** *(opus F-03)*:
  - A provider is `local` only if its host resolves to loopback, or it is a Unix socket.
  - A LAN address (RFC 1918/ULA) is another machine, so it counts as `cloud`. The exception is a host the owner lists in `allow_lan_hosts`.
  - The run records the resolved address and the rule that admitted it.
  - `chatx providers check` prints the verdict. A local-role provider that resolves elsewhere fails with `E_PROVIDER_NOT_LOCAL`.
- **Outcome is typed** *(chatgpt F19)*. Each call returns one of:
  - `ok`;
  - `refused`, with the stop reason;
  - `truncated`, when the output limit was hit;
  - `invalid`, schema errors after the retry budget;
  - `unavailable`.
  Each outcome is stored per item and counted in the run report. A refusal is never retried as if it were bad JSON. An unavailable `EmbeddingProvider` fails the index stage with an error code; there is no fallback model.
- **Sampling parameters are capability-gated per provider and model** *(opus F-02, grok F2)*. A provider sends `temperature`, `top_p` or `seed` only where its capabilities say the model accepts them. `runs` stores exactly what was sent, with `None` for anything omitted.
- **Anthropic specifics**, confirmed on 2026-10-21 from the Sonnet 5.5 and Opus 5.5 migration guides (E2a–E2d; the supervisor re-read both pages):
  - The Messages API has **no `seed`**.
  - Both models return HTTP 400 for a non-default `temperature`, `top_p` or `top_k`.
  - Both return 400 for `tool_choice` of type `any` or `tool`, with or without thinking.
  - So the Anthropic provider sends no sampling parameters. It gets structured output from `output_config.format`, or from a `strict: true` tool with `tool_choice: auto`, and the prompt says when to answer.
- **Thinking and output budget** (E2d):
  - Thinking is on by default on both models, and it counts toward `max_tokens`, which caps thinking and answer together.
  - Opus 5.5 cannot turn thinking off.
  - Sonnet 5.5 can, with `thinking: {"type": "between_tools"}`, but only at `low`, `medium` and `high` effort.
  - Rev 1's 800-token output cap is removed. The provider sets `effort` and a `max_tokens` sized for thinking plus the answer. Stopping at `max_tokens` is the `truncated` outcome, never a parse error.
- **Structured output on OpenAI-compatible servers** *(opus F-27, E3)*. vLLM, Ollama, the llama.cpp server and LM Studio all offer schema-constrained output, each with a different request shape.
  - `chatx providers check` probes the mode (`json_schema`, `grammar` or `none`) and records it in `capabilities`.
  - Every provider validates output against the schema and retries within the budget. There is no silent fallback to unconstrained JSON.
  - Reports never claim bit-reproducibility: vLLM documents none by default. The cache (§3.9) is the reproducibility mechanism, and a seed is only a hint.
- **Operation contract** *(codex F16, agy F-22, chatgpt F20)*:
  - **Time limits:** connect and read timeouts, plus a per-run deadline (`--deadline`).
  - **Retries:** exponential backoff on 429, 5xx and timeouts, under a per-run retry budget.
  - **Throughput:** bounded concurrency, set in config.
  - **Cost:** `usage` is recorded per call. A cost cap (`--max-cost-usd`, with a price table in config, never in code) is checked before each send against the estimated input and after it against reported usage.
  - **Anthropic extras:** prompt caching on the static prefix (system prompt and taxonomy), and an optional batch mode (`--batch`) for cloud enrichment (RT-7).
  - **Observed model:** taken from the response's `model` field.
  - **Interrupts:** Ctrl-C finishes the items in flight, records the watermark and leaves the run resumable.
- **Call identity** *(chatgpt F21)*. Each call stores `call_config_hash`, a hash of exactly what was sent:
  - the model id and the sampling parameters actually sent;
  - the output limit and the structured-output mode;
  - the system-prompt hash, the taxonomy hash and the preprocessing version.
  It also stores the model id from the response. `ProviderIdentity` keeps the requested and observed model separately. An endpoint that does not echo the model is recorded as UNKNOWN, never filled in from the request.
- **Prompt-injection posture** *(chatgpt F23)*. Chunk text is data, delimited and labelled as such in the prompt. The model has no tools during enrichment. Output fields are enums plus citations to request lines, and a citation to a line that is not in the request is rejected.
- **No model id, endpoint or key in code.** Configuration lives in `~/.config/chatx/config.toml`, with per-case overrides:

```toml
[providers.local]                  # role: local chat (shield second opinion, local enrichment, query)
kind = "openai_compat"
base_url = "http://localhost:11434/v1"
api_key_env = ""
model = ""                         # set at install; `chatx providers list` shows what the endpoint serves
allow_lan_hosts = []               # LAN hosts the owner explicitly treats as local

[providers.local.sampling]         # sent only where `chatx providers check` reports the model accepts it
temperature = 0.0

[providers.embedding]              # local only; a non-local host is refused
kind = "openai_compat"
base_url = "http://localhost:11434/v1"
model = ""

[providers.cloud]
kind = "anthropic"
api_key_env = "ANTHROPIC_API_KEY"
model = "claude-sonnet-5-5"        # claude-opus-5-5 selectable per run
effort = "medium"
max_tokens = 16000                 # starting value for thinking + answer; P4 sizes it from measured use
zero_data_retention = true         # the owner's statement of the account terms; both lines are required for a gate token
training = false

[enrich]
context_turns = 2
concurrency = 4
max_cost_usd = 0                   # 0 = cloud spend disabled
```

### 3.7 Policy Shield v2 — the gate

**What the shield claims** *(grok F1)*. It claims per-class recall on named classes, and nothing more. Every report states: "recall measured on classes {…}; de-identification is not claimed."

**Classes** *(opus F-04, chatgpt F05)*. The class set is the shield's **entity-class list** (`config/shield_classes.yml`), fixed before evaluation *(clarified, builder check)*. It is not the enrichment taxonomy (`labels.yml`), and it does not depend on what the detector happens to find in a case. It covers:
- **Direct identifiers:** person names, phone numbers, emails, street addresses, handles, account numbers, government ids.
- **Quasi-identifier classes:** `location, date_of_birth, employer, school, relationship_descriptor, unique_event, financial_account, health_condition`.

The owner declares each case's languages (`languages`, default `en`, §3.5). Language is identified locally (RT-16), and a chunk in an undeclared language is not cloud-eligible.

**Detection.** The framework is Presidio, the candidate since rev 1. It is now community-governed under the Data Privacy Stack organisation and still MIT-licensed (E5); it is pinned with hashes, and what V2 changes is RT-10. The v1 regex set is ported as custom recognizers. The NER engine is chosen by the P3 evaluation from spaCy, GLiNER and OpenAI Privacy Filter, an open-weight local PII model (E5, RT-11).

**Pseudonymization** *(codex F11, grok F3, agy F-12, opus F-12, chatgpt F17)*.
- **Sender pseudonyms.** `sender.pseudonym` is HMAC-SHA256 truncated to 128 bits, keyed by the per-case salt.
- **Redaction tokens are typed per-case sequential surrogates,** `⟦PERSON_0007⟧`, `⟦PHONE_0003⟧`:
  - They are allocated in first-seen order under the case lock.
  - Redacted text carries no hash material, so collisions cannot happen, and the type helps the model during enrichment.
- **Token grammar:** exactly `⟦[A-Z_]+_[0-9]{4,}⟧`. `⟦` and `⟧` in source text are escaped at import, so message content cannot forge a surrogate.
- **Salt.** It is per case, created with `O_CREAT|O_EXCL` at `secrets/salt`, mode 0600, in a 0700 directory. There is no global salt. `chatx identity rotate` re-derives the pseudonyms and invalidates caches derived from cloud calls.
- **The reversible map** lives in `secrets/pseudonyms.sqlite3`, not in `case.sqlite3` (owner item 6).
  - **Export bundles never include `secrets/`** unless `--include-pseudonym-map` is passed, which warns first.
  - The separation protects bundle hand-off, not against a local root attacker (§3.15).
- **Re-hydration** is local only, takes the case lock and is recorded in `runs`. A surrogate in model output that is not in the map is left as it is and flagged; it is never resolved.

**Measurement** *(codex F09, grok F1, agy F-13, opus F-04)*:
- **Two evaluation sets.**
  - A deterministic synthetic set. It runs in CI and qualifies CI only.
  - The owner's labelled **real sample**, local and git-ignored. The owner will label a full sample: about 600 examples per entity class (owner item 3).
- **`chatx shield eval`** computes recall and precision per class and language. It stores them in `shield_evals`, keyed by shield version and recognizer config hash.
- **Target.** Per class, the one-sided 95 % Clopper–Pearson lower bound on recall must be ≥ 0.995, or ≥ 0.999 with `--strict`.
  - With zero misses, 0.995 needs n ≥ 598 labelled positives, and 947 with one miss.
  - 0.999 needs n ≥ 2,995.
- **Short of support.** A class below that support reads `INSUFFICIENT_SUPPORT`, which keeps the cloud tier off.
- **Strict, by owner decision** (item 14). Every class must reach the 0.995 bound on real labelled data. There is no tiering by class type, no synthetic substitute and no per-case exclusion of a class. A class the owner's data rarely contains — passport numbers, employers, schools — may never reach 598 positives, and then the cloud tier stays locked. That is the intended outcome, not a defect.

**Content sensitivity: local-only labels** *(opus F-05, F-23, chatgpt F18; owner item 10: "special categories stay local")*:
- **Every fine label is local-only.**
- **These coarse labels have `cloud_allowed: false`:**
  - sexuality and sexual orientation;
  - health;
  - substances;
  - crime or violence;
  - anything involving minors.
- **A chunk carrying any local-only label** is `cloud_eligible = false`. It is enriched locally only, whatever its PII recall.
- **Order** *(decided, builder check)*. The labels come from enrichment, so every chunk first goes through the **local pass** (§3.9): shield detection plus local enrichment with the full taxonomy. Only chunks the local pass leaves `cloud_eligible` can reach the cloud pass.
- **Content involving minors** is flagged locally and excluded from every export, including `--include-analysis` bundles.
  - **How it is detected** *(decided, builder check)*: two local signals, either of which flags the chunk — the coarse label `minors_involved` from the local pass, and a high-recall lexical check for ages and school-age terms.
  - **Definition:** approved with the hard-fail definitions (§12 follow-up 1).
  - **Measurement:** its recall is measured on the gold set and reported. The exclusion applies whatever the measured recall.
- **Hard-fail classes come from the taxonomy, not regexes:**
  - The v1 `HardFailDetector` regexes are retired; they collided with labels the taxonomy allows.
  - The classes and their written definitions are listed in `config/labels.yml`. P3 writes the definitions, and the owner approves them.
  - A hit excludes the chunk from cloud processing. It is logged locally by id only and never appears in exports or cloud requests.

**Chunk construction for the cloud** *(grok F8, agy F-14, chatgpt F18)*:
- **Surrogates everywhere** *(clarified, builder check)*. Text sent to any model names people only by surrogates from the same map as the redaction tokens. One person is one `⟦PERSON_nnnn⟧`, whether they are the sender or mentioned in the text. `sender.pseudonym` (the HMAC value) is an internal join key for the case and for exports; it is never placed in model input. The ±2-turn context is rendered the same way.
- **Nothing linkable.** Cloud requests carry an opaque request id instead of `msg_id`/`conv_id`, and lines carry times relative to the chunk start instead of calendar dates. The mapping stays local.
- **Enforced by types.** The cloud request model's only text field is `redacted_text`, and it has no attachment or id field.

**Run-time gate (fail-closed).** A cloud request gets a gate token only if all of these hold:
1. **Real-sample evaluation.** A real-sample `shield_evals` report exists for the exact shield version and config. It meets the target for every class on the entity-class list and every declared language, with no `INSUFFICIENT_SUPPORT`.
2. **Eligible chunk.** The chunk is `cloud_eligible`: no local-only label, no hard-fail hit, and a declared language.
3. **Second opinion passes** *(agy F-13, chatgpt F16)*.
   - **What it estimates:** the residual leak rate per chunk, among the chunks the primary shield passed.
   - **How** *(decided, builder check)*: per cloud run, over the chunks that run would send. The local judge model reviews a simple random sample of them, drawn without replacement with the seed recorded.
   - **Sample size:** n ≥ 3/ε chunks; ε is configurable, default 0.005, so 600 chunks. When a run would send fewer, every one of them is checked — an exhaustive check, not a small sample.
   - **Reuse:** verdicts are cached by `(chunk_id, judge call_config_hash)`, so a later run samples only among chunks not yet checked.
   - **Pass:** zero confirmed leaks are required. A confirmed leak blocks with `E_VISIBILITY_LEAK`.
   - **The judge is checked first:** its own recall is measured on the labelled set. If it misses the class floors, its result is not evidence, and the class reads `INSUFFICIENT_SUPPORT`.
4. **The run's shield status is `ok`** *(chatgpt F15)*. Any exception, or any chunk the shield cannot classify, makes that chunk ineligible and sets `shield_status = degraded`. A degraded run gets no token (`E_SHIELD_NOT_QUALIFIED`, also used when item 1 fails), so its cloud stage stops while the local pipeline continues. The chunk id and exception class are kept locally.
5. **Vendor terms declared** *(owner item 11b)*. `[providers.cloud]` declares `zero_data_retention = true` and `training = false`. These are the owner's statement of the account terms, which the tool cannot check, and each run records them. Without both, the error is `E_VENDOR_TERMS`.
6. **Real cloud destination.** The destination is classified `cloud` by the locality check, and its resolved host and model id are recorded.

**Gate token** *(codex F10, grok F7, chatgpt F04)*:
- **Contents:** `GateToken(case_id, run_id, operation, destination, payload_hash, shield_version, issued_at, ttl)`. `operation` is enrichment or second opinion. `destination` is the resolved host and model id.
- **What `payload_hash` covers:** the final serialized request bytes at the transport layer, after the SDK has built the request.
- **How** *(decided, builder check)*. Both SDKs take a caller-supplied `httpx` client, and the check runs in that client's request hook on the final body bytes; this is to be confirmed (RT-17).
  - **Fallback:** if the hook cannot see the final bytes, ChatX serializes the request body itself and sends it with its own `httpx` call to the same endpoint. The hashed bytes are then the sent bytes by construction.
- **Checked every time.** The hash is re-checked on every retry. Any later change to the request, an expired token or a foreign token fails closed with `E_GATE_MISMATCH`.
- **Tests:** a forged, expired or foreign token cannot send.

**Exit codes.** Every refusal to let data leave the machine is an RFC 9457 problem with exit 3; §3.12 lists the codes. `--strict` raises the threshold; nothing lowers it.

### 3.8 Chunking

- **Ported:** `ConversationChunker`, with windows of 40 turns, stride 10, a daily fallback and a fixed-size mode. It is built in P2.
- **Fixed:**
  - Group chats keep per-sender identity; v1 collapsed every non-owner participant into one `contact`.
  - Lines sent to any model use surrogates (§3.7).
- **Chunk ids are deterministic** *(chatgpt F08)*: `chunk_id = sha256(chunker config hash, ordered (msg_id, record_hash) list)[:32]`.
  - They are the same on every run, and change when any member message changes.
  - This replaces v1's run-dependent 8-hex-digit ids.
- **Chunks store their members.** Each chunk stores its ordered `(msg_id, record_hash)` members.
- **Structured input to the enricher.** It receives structured `(msg_id, sender, text)` rows and never re-parses chunk text, so a multi-line message stays one message.
- **Rendering per consumer** *(decided, builder check)*. A chunk stores its membership only, not rendered text.
  - **Local consumers** (local enrichment, the local index) render the raw text, which never leaves the machine.
  - **Cloud requests and MCP views** render it with surrogates at request time, which needs the P3 shield.
  - So chunking ships in P2 without depending on P3.
- **`semantic`** is removed from the enum until it exists.

### 3.9 Enrichment

- **Taxonomy** *(codex F17, agy F-15, F-18, chatgpt F22)*:
  - **Schema 1.3:** `config/labels.yml` moves to schema 1.3, with a per-label `cloud_allowed: bool` that defaults to `false`. The content policy is §3.7's. Fine labels are always local-only, and the compiler rejects `cloud_allowed: true` on one. The owner approves `cloud_allowed` for coarse labels only, label by label *(clarified, builder check)*.
  - **Compiler:** a compiler validates the file against a JSON Schema. It produces two enums, `CoarseCloudLabels` (labels with `cloud_allowed: true`) and `FineLocalLabels`.
  - **Typed by construction:** cloud request and response models are typed with the cloud enum only, so local-only labels cannot reach the cloud.
  - **Test:** every YAML label appears in a compiled enum.
  - **Why:** the v1 loader read a `categories` key that does not exist, so it loaded no labels. The counts — 55 coarse and 99 fine leaves — are confirmed by a parse (grok F19).
- **Output schema.** Labels come from the enum. The schema allows `none_apply` and per-label abstention, and each label cites lines of the request.
- **Confidence** *(codex F18, grok F14, opus F-18)*:
  - **Not a probability:** `confidence_llm` is self-reported and is never read as a probability.
  - **Calibration:** thresholds are calibrated on the owner-labelled **enrichment gold set** (owner item 4: yes) with a reliability curve (RT-13). Until that set exists, every label carries `calibrated: false` and cloud enrichment stays off.
  - **Hysteresis is stateful:** it is tracked per `(conv_id, label)` in time order. A label enters at τ_high (0.78), exits below τ_low (0.62) and holds in between, and the state is stored with the enrichment.
  - **τ (0.70) is the cloud-escalation threshold** *(clarified, builder check)*: a cloud-eligible chunk goes to the cloud pass only when its local pass abstained, or gave some label a calibrated confidence below τ.
  - All three are starting values, recorded in each run.
- **Provenance and cache key:**
  - **Key fields:** `(provider identity, call_config_hash, prompt template hash, taxonomy version, schema version, shield version, recognizer config hash, input content hash, context hash)`.
  - **Per-row record:** every enrichment row records the same fields plus its typed outcome.
- **One store.** Enrichments are written to `enrichments` in the same store, and they join to their messages. This removes the v1 defect where enrichments never reached the index.
- **Two passes** *(decided, builder check)*:
  - The **local pass** runs on every chunk: shield detection and local enrichment with the full taxonomy, on raw text that never leaves the machine. Its labels decide `cloud_eligible` (§3.7).
  - The **cloud pass** is optional. It runs only on eligible chunks that meet the escalation rule above, using the cloud enum only.
- **Cloud enrichment** sends surrogate-rendered chunk text with ±2 turns of context rendered the same way, under the gate (§3.7) and the operation contract (§3.6), and logs every call.

### 3.10 Search, query, reports

- **Embedding spaces** *(chatgpt F25, opus F-19)*. Each space — model, revision, dimension, quantization, distance — is a row in `embedding_spaces`, with its own `vec0` table.
  - **Changing spaces:** changing the model creates a new space and re-embeds. Two spaces are never mixed, and an old space is dropped only explicitly.
  - **Defaults:** a local model of 768 dimensions or fewer (RT-5), with `int8` vectors where the model tolerates them. The final top-k is rescored with float vectors.
- **sqlite-vec** is pre-v1 (v0.1.9), and `vec0` KNN is an exact scan (E9).
  - **Pinned:** it is pinned to an exact version, and the version and the `vec0` table definition are recorded in `schema_migrations`.
  - **Missing extension:** if it is missing, indexing fails loudly. There is no silent FTS-only fallback; `--no-vector` is the explicit way to run without vectors.
- **Query plan** *(codex F13, grok F9, agy F-17)*: filter, then KNN. FTS5, metadata and time-window filters produce candidates, and only those are scored by vector. A full-table KNN needs `--exhaustive`.
- **Fusion** *(codex F19, grok F15, chatgpt F27)*:
  - **RRF parameters:** reciprocal rank fusion with `k = 60` and a per-retriever depth `N`, both in config.
  - **Filters first:** filters (time, contact, label) apply to every retriever before fusion.
  - **Message-level fusion:** chunk hits expand to their `msg_ids`, and duplicates from the stride overlap collapse.
- **Citations:**
  - **Form:** `(msg_id, conv_id, sent_at, span)`, where `span` is a pair of character offsets into the message's stored `text` at a stated `record_hash`.
  - **Staleness:** a citation whose `record_hash` no longer matches is reported stale.
  - **Derived data:** derived rows carry the `content_hash` of their inputs, and `case verify` flags stale ones.
- **`chatx query`** answers with citations, using the local provider by default; the cloud is reachable only through §3.7.
  - **Citation support:** an answer passes only if each cited span supports its claim. A local judge model checks this, and the owner spot-checks it (RT-18).
  - **Evaluation:** P5 adds a local retrieval gold set (owner-written queries with their relevant `msg_id`s) and measures recall@k.
- **Reports kept from rev 1:** `manifest.json`, `run_report.json`, `metrics.jsonl`, the redaction report and the missing-attachments report.
- **Export bundle** *(codex F14, opus F-20, chatgpt F26)*:
  - **Contents:** `exports/<run>/bundle.zip`.
  - **Manifest:** `MANIFEST.sha256` lists every file with its sha256, size, tool version and schema version.
  - **Custody record:** `custody.json` holds:
    - the OS user and host;
    - the source device and its OS version;
    - the tool version and git commit, and the operator;
    - the start and end times and the run ids;
    - the `sources` rows with their acquisition hashes.
  - **Signature:** an optional detached signature via `--sign` (tool choice is RT-6).
  - **Timestamp:** an optional RFC 3161 timestamp, owner-chosen, because it sends the manifest hash to a timestamp authority. That is a hash only, but it is still network egress.
  - **Excluded by default:** `secrets/` (unless `--include-pseudonym-map`) and analysis records (unless `--include-analysis`).
  - **Never included:** content involving minors.
  - **Reading a bundle back:** `chatx case import-bundle` verifies the manifest before opening anything.

### 3.11 Analysis lane (phase 6)

- **Old rules become documentation, not data** *(agy F-18, codex F20)*. The v1 relationship types and pattern rules (`storage/base.py`, `psychology_relationship_mapper.py`) are ported as `docs/analysis/legacy-patterns.md`. None of the mapper's 123 `source_labels` exists in `labels.yml`.
- **A new construct map** is built in P6 from the current taxonomy, with its own ADR, evaluation and basis citations.
- **Indicators** *(opus F-25, chatgpt F28)*:
  - **Names:** they describe observable text patterns. No name asserts intent or a diagnosis: `GASLIGHTS`, `MANIPULATES`, `CODEPENDS_ON` and `AROUSAL_MANIPULATION` are renamed.
  - **What each indicator carries:**
    - the actor (a pseudonym);
    - the messages that support it, cited;
    - the counter-evidence searched for — messages in the same window that do not fit;
    - its abstentions;
    - a review state (`unreviewed`, `accepted`, `rejected`).
  - **Records:** they are typed `model_inference`, with provenance and the fixed disclaimer "not a clinical assessment". They make no claim of direction or cause.
- **Agreement before shipping.** Each analysis label needs inter-rater agreement between two human raters on the gold set (RT-15).
- **Storage and export.** Outputs live in `analysis_*` tables and are exported only with `--include-analysis`. Content involving minors is never exported.
- **Experiments**, each behind an ADR with a model-research gate first:
  - psychology-specific embedding models (`mental-bert`);
  - image enrichment;
  - audio transcription;
  - encrypted iPhone backups (RT-9).

### 3.12 CLI

- **Errors.** Typer, with `pretty_exceptions_show_locals=False`. Errors follow **one RFC 9457** problem+json shape (`type, title, status, detail, instance, code`; RFC 9457 obsoletes 7807, E6), with one error-code convention, `E_<SNAKE>`. `--json` works everywhere.
- **Exit codes** *(opus F-30, chatgpt F34)*:

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | any other error (an RFC 9457 problem is printed), including `E_SQLITE_TOO_OLD`, `E_TZ_REQUIRED`, `E_CASE_LOCKED`, `E_DB_*` and `E_SCHEMA_MISSING` |
| 2 | usage error. Click's `UsageError.exit_code` is 2 (E7); Typer inherits it (inferred) |
| 3 | egress refused — data was stopped from leaving the machine: `E_GATE_MISMATCH`, `E_VENDOR_TERMS`, `E_VISIBILITY_LEAK`, `E_PROVIDER_NOT_LOCAL`, `E_SHIELD_NOT_QUALIFIED` (§3.7) |
| 4 | partial: some records ended in quarantine or a skip. The counts are printed and recorded |

- **Command tree.** The contact can also come from `--contact-file` or a prompt, so names do not land in shell history (chatgpt F31).

```
chatx case       create [--encrypt] | status | verify | repair | resume | backup | delete-source | purge | import-bundle
chatx import     imessage [--db PATH | --from-backup DIR] [--contact ... | --contact-file F] [--probe] [--resume]
                 instagram | whatsapp --assume-tz TZ --date-order dmy/mdy | pdf --assume-tz TZ --me NAME | email --me ADDR
chatx identity   pseudonymize | rotate
chatx chunk
chatx shield     eval | redact | report
chatx enrich     [--provider local/cloud] [--allow-cloud] [--strict] [--deadline] [--max-cost-usd] [--batch]
chatx index      build [--incremental] [--no-vector] | status
chatx query      [--exhaustive]
chatx export     bundle [--sign] [--include-pseudonym-map] [--include-analysis] | report
chatx providers  list | check
chatx analyze    relationships | episodes                     # phase 6
chatx mcp serve  [--expose-raw]                               # phase 7
```

- **Error codes defined by this design:**
  - `E_DB_LOCKED`, `E_DB_ACCESS_DENIED`, `E_SQLITE_TOO_OLD`, `E_CASE_LOCKED`;
  - `E_TZ_REQUIRED`, `E_SCHEMA_MISSING`;
  - `E_PROVIDER_NOT_LOCAL`, `E_GATE_MISMATCH`, `E_VENDOR_TERMS`, `E_VISIBILITY_LEAK`, `E_SHIELD_NOT_QUALIFIED`.
  - `E_HARDFAIL_CLASS` is a per-chunk reason code in the shield report, not a run error.
  - The registry generates `docs/reference/errors.md`.
- **Behaviour contract** *(codex F26, chatgpt F34)*:
  - **Partial or interrupted runs:** each command states what one leaves behind (a watermark, `status=partial`) and how `case resume` continues it.
  - **`delete-source`** removes the source, its messages and everything derived from them by cascade *(decided, builder check)*. It also:
    - drops cache entries no longer referenced, and the source's `msg_id_aliases`;
    - runs `VACUUM` and a WAL checkpoint with truncation, so no content stays in free pages (`secure_delete` is on, §3.5).
    It keeps the `runs` audit rows, which hold counts, not content.
  - **Bundles already exported** live outside the case and are not recalled. The case records each export path, and `case purge` lists them so the owner can delete them.
  - **`case purge`** removes the case directory, including `secrets/`. It keeps one audit line outside the case.
  - **Dispositions:** every input record ends in exactly one disposition — imported, continuation of the previous message, system event, skipped with a reason, or quarantined with a reason. The report's counts are asserted to sum to the input count.
  - **Portability:** a case directory is self-contained, with paths stored relative to the case root, so it can be moved.
- **MCP** *(opus F-06, grok F7)*:
  - **Redacted views only.** `chatx mcp serve` returns redacted views with surrogates for people only (§3.7, §3.8), because the MCP client's model is usually cloud-hosted.
  - **`--expose-raw`** counts as cloud egress of raw text. It needs a per-session confirmation, and `runs` records it.
- **Not carried from v1:** the `extract`, `analyze` and `pipeline` stubs; the Typer group registered after `__main__`; the `--config` flag that was accepted and ignored. The full disposition is in §8.

### 3.13 Observability and security

- **Logs.** `structlog` JSONL per run, with run ids everywhere and provider identity per call. Diagnostics use an **allowlist of fields** — ids, counts, codes, hashes. Anything else, including message text, handles and contact names, is dropped (chatgpt F31).
- **Secrets** come only from environment variables named in config.
- **Offline by default.** Models are provisioned ahead of time and `HF_HUB_OFFLINE=1` is set. The no-socket test covers the core, and also the app's import, identity and shield stages (opus F-11). The only outbound paths are the local provider and the explicitly configured, gated cloud provider.
- **SQLite version.** Every run records `sqlite_version` (§3.3).
- **Acquisition** is specified in §3.5.
- **Encrypted iPhone backups** are **out of scope until P6**. `--backup-password` is removed until decryption is implemented; v1 only checked that a password was given.

### 3.14 Retired outright

- **Stores:** the Chroma store, the Neo4j store, and `multi_vector_store.py`. The latter is reachable today through `index --store multi` and `--multi-vector` (Appendix A.1); it is retired, not merely dead.
- **Unused code:** `embeddings/*` (benchmark and psychology providers), `privacy/differential_privacy.py`, `enrichment/image_enricher.py` (placeholders), `constrained_dynamic_loader.py` (MCP tooling, not product), `enrichment/ollama_client.py` (replaced by providers), the `cli/main.py` command bodies, and `utils/config.py` (Neo4j presets, default password).
- **Retired behaviours:**
  - the sequential `chat.db`/`-wal`/`-shm` copy with `immutable=1`;
  - the plistlib/UTF-8 heuristic in `body_normalize.py`, and the `[ATTRIBUTED_BODY_CONTENT]` placeholder;
  - the `datetime.now()` fallbacks;
  - the 3000–3999 "custom" reaction mapping;
  - the `OR m.is_from_me = 1` contact filter;
  - the `HardFailDetector` regexes;
  - the hash-based `ConsistentTokenizer` tokens;
  - the run-dependent chunk ids;
  - the `categories` taxonomy loader.
- **Tests and CI:** the old bplist fixtures, at the end of P1. `config/arch-gates.yml` and `.github/workflows/*` are rewritten in P0, not carried.
- **Docs:** the entire `docs/` tree as specification. It is archived in the old repo, and the relevant intent is captured here.

### 3.15 Threat model *(new in rev 2: codex F24, opus F-11, F-26, chatgpt F23, F31)*

**Assets.** Raw messages and attachments; the pseudonym map and salt; the cloud API key; export bundles.

**Adversaries considered:**
- another local user or process;
- a lost or stolen laptop;
- a malicious export, ZIP, PDF or `.eml`;
- a malicious or cloud-backed MCP client;
- prompt injection through message content;
- a misconfigured provider URL;
- sync and backup services copying case data off the machine.

**Out of scope.** Root on the machine, memory forensics, a compromised OS.

**Controls:**
- **File system.** Case directories are 0700 and files 0600. Nothing is written to `/tmp`. FileVault is required (§3.5), and per-case encryption is opt-in.
- **Input limits** cover ZIP bytes, entries and compression ratio, PDF pages and database size. SQL is parameterized only, and there is no `pickle` or `eval`.
- **Model output** is schema-validated. An adversarial test set of chunks containing instructions, fake JSON and fake surrogate tokens must produce the same labels as the clean-text baseline.
- **Egress.** Provider locality is computed (§3.6), MCP serves redacted views only, and the gate token binds the exact request (§3.7).

**Where message content can land, and the rule for each place:**

| Place | Rule |
|---|---|
| `case.sqlite3` and its WAL, FTS shadow tables | inside the 0700 case root; deleted by `case purge` |
| `secrets/` | 0700/0600; excluded from bundles by default |
| `attachments/`, `sources/` | inside the case root; bytes exact |
| case `tmp/`, `attachments/.tmp/` | inside the case root; swept at start; reported by `case verify` |
| quarantine records | stored in the case, never in loose files |
| logs | field allowlist only (ids, counts, codes, hashes) |
| crash output | `pretty_exceptions_show_locals=False`; no locals printed |
| model caches | pinned artifacts only; no message content written to them |
| exports | §3.10 rules; secrets and analysis opt-in; content involving minors never |
| dNh adapter JSONL (`--emit-jsonl`) | written into the case `tmp/`, deleted after the adapter run |
| shell history | contacts may be given via `--contact-file` or a prompt |
| Spotlight, iCloud, Time Machine | `.noindex` root, iCloud-synced roots refused, Time Machine exclusion offered |

---

## 4. Target architecture

```
packages/chat-extraction-core/src/chat_extraction_core/
  schema/       canonical message v2 models, generated JSON Schema, canonical JSON + content/record hashes, version registry
  time/         Apple-epoch converter (2001–2100 bounds), export-time grammars, --assume-tz handling
  sources/
    imessage/   acquisition via the backup API, schema probe + column manifest, reader,
                reaction / reply / edit / system-event folds, multi-chat rule,
                attributedbody/ (dNh's bounded decoder first, generic typedstream walker second),
                attachment resolver (expanduser, resolve, containment)
    backup/     iPhone Manifest.db acquisition and fileID resolution (unencrypted until P6)
    instagram/  ZIP reader (zip-slip guard, byte/entry/ratio limits), latin-1 mojibake repair
    whatsapp/   Android + iOS export grammars, structural system lines, explicit date order
    pdf/        text-layer transcript parser (no OCR)
    email/      .eml parser (Message-ID, In-Reply-To, References, From/To/Cc/Bcc, Date)
  identity/     phonenumbers-based handle normalization, HMAC pseudonyms
  fixtures/     chat.db builders from per-macOS schema snapshots, export builders, golden JSONL
  (no network, no LLM, no database of its own; writes only to paths the caller gives; dependencies: pydantic, phonenumbers)

apps/chatx/src/chatx/
  case/         store, SQL migrations, acquisition orchestration, CAS, verify / repair / resume / backup / purge
  shield/       Presidio integration, recognizers, language id, surrogates + map custody, eval harness, gate + tokens
  chunk/        chunker (deterministic ids)
  providers/    ChatProvider, EmbeddingProvider, openai_compat, anthropic, capabilities probe, locality check
  enrich/       taxonomy compiler, structured enrichment, typed outcomes, cache, calibration, hysteresis
  index/        embedding spaces, vec0 tables, FTS, filter-then-KNN, RRF fusion
  query/        answers with citations, citation-support check
  report/       manifests, run / redaction / missing-attachment reports, export bundle + custody, import-bundle
  analysis/     (phase 6) construct map, indicators
  cli/          Typer app, RFC 9457 problems, exit codes
  mcp/          (phase 7) redacted views
```

**Data flow:**

`core acquire + iterate → case import (probe, map, quarantine) → identity → chunk (membership) → local pass (shield detection + local enrichment) → cloud pass (eligible chunks only, surrogate rendering, through the gate) → index → query / export`

- **Within ChatX.** Every stage reads and writes the case database. There are no file hand-offs between stages, which is what broke v1.
- **From the core** *(decided, builder check)*. The core yields canonical messages and disposition records (quarantined or skipped, each with a reason), so ChatX and dNh get the same accounting. `chatx import` consumes them directly.
- **JSONL** is written only for `--emit-jsonl` and the dNh adapter tests (§9, chatgpt F03).

**Importer fidelity** *(chatgpt F13, codex F08, grok F12, agy F-04, F-11, F-19, opus F-07, F-15, F-31)*. Each original export file is acquired into `sources/` with its sha256, like `chat.db`.

| Source | Reads | Keeps raw in `source_meta` | Cannot recover | `source_locator` |
|---|---|---|---|---|
| iMessage `chat.db` | the §3.4 column manifest | every manifest column without a canonical field; blobs in `message_blobs` | membership history; messages Messages already purged | `ROWID` |
| iPhone backup | the same, via `Manifest.db` fileIDs | the same | encrypted backups (until P6) | `ROWID` + fileID |
| Instagram ZIP | messages JSON (sender, `timestamp_ms`, content, media, reactions, shares) | unknown keys verbatim | handles (display names only); edits | JSON pointer |
| WhatsApp text export | Android and iOS bracketed line grammars; `--date-order dmy/mdy` explicit | the raw line and markers (`<Media omitted>`, deleted-message lines) as `source_meta.wa_marker` | time zone (`--assume-tz` required); seconds on Android; handles (display names only); reactions; replies | line number |
| PDF transcript | text layer only; `platform=pdf_transcript` | the raw line | attachments; time zone (`--assume-tz` required); lines without a timestamp are quarantined | page + line |
| Email `.eml` | `Message-ID, In-Reply-To, References, From, To, Cc, Bcc, Date`; `reply_to_msg_id` ← `In-Reply-To`; `conv_id` ← root of the `References` chain; direction from `--me` | all headers | a missing or `-0000` zone → `source_tz=None` and the §3.4 time rules | `Message-ID` + file |

**WhatsApp rules.**
- **System lines** are detected **structurally**: a line with no `Name:` prefix is a system line. Substring matching is never used, because v1 dropped ordinary messages containing words like "added" or "left".
- **Continuations.** Lines before the first header and continuation lines are kept, not discarded.

**Instagram rules.**
- **Mojibake.** The latin-1→UTF-8 re-decode runs only when it round-trips cleanly. The golden fixture includes emoji and accented names, because mojibake names evade the PERSON recognizer.
- **Email ids.** These come from the normalized `Message-ID` header, falling back to a hash of normalized headers plus body, so the same mail saved twice dedupes.

---

## 5. Contracts the builder must honour

1. **Canonical message v2.**
   - The version is `chat.message.v2-draft` until the P0.5 probe, then frozen.
   - A breaking change bumps the version string, adds a migration note and records the affected ids in `msg_id_aliases`.
   - dNh pins the core wheel by version and sha256.
2. **Schema generation test.** The committed JSON Schema equals the generated schema. Schemas load through `importlib.resources`; a missing one is `E_SCHEMA_MISSING`.
3. **Id stability.** Re-importing a source reproduces every `msg_id` and `chunk_id`. An overlapping later export keeps shared ids, within the §3.4 limit. Tests cover both.
4. **Problems and exit codes.**
   - Errors use one RFC 9457 shape and one code convention.
   - Exit codes are 0–4 (§3.12).
   - `docs/reference/errors.md` is generated from the code's error registry.
5. **Gate semantics.**
   - Every call to a cloud provider takes a gate token bound to the exact serialized request.
   - Tests prove that a missing, forged, expired, foreign or mismatched token cannot send.
   - Cloud request types have no attachment, `msg_id` or `conv_id` fields.
6. **Provider identity.** Requested and observed models are recorded separately, with `call_config_hash` per call. UNKNOWN is never replaced by the requested value.
7. **dNh adapter totality.** The adapter test enumerates every `(platform, direction, content_kind)` triple from the enums and asserts that exactly one disposition rule matches it (§9). A new enum value fails the test until it has a rule.
8. **Coverage.**
   - `--cov-fail-under=90` on lines over `chat_extraction_core` and `chatx`, with no `omit` beyond `tests/`.
   - Branch coverage and a mutation-testing (`mutmut`) kill rate of at least 80 % on `shield/` and the gate. The floor is raised as it is met and never lowered *(decided, builder check)*.
9. **No network.**
   - The core never opens a socket.
   - The app's import, identity and shield stages never open a socket.
   - Model artifacts load offline.
10. **SQLite floor.** A case never opens under SQLite below the floor (§3.3).

---

## 6. Phases and exit criteria

The order follows two rules, both new in rev 2:
- **Risk first** *(opus F-24)*: the P0.5 spikes test the unknowns that decide feasibility before anything is built on them.
- **Each phase's exit uses only that phase's outputs** *(codex F23, chatgpt F32)*.

| Phase | Scope | Exit criteria (all must be PASS) |
|---|---|---|
| **P0 Workspace** | `~/code/chatstack` repo; uv workspace; two empty packages; CI (ruff, mypy, pytest, `uv lock --check`, `pip-audit`) testing the **installed wheel** in a fresh venv outside the checkout; `.github/workflows/*` rewritten, `arch-gates.yml` not carried; pre-commit; ADR template; `conformance.md` skeleton; an interpreter linking SQLite at or above the floor; this document copied in | A green CI run, its URL recorded, that includes the failure-path tests (`E_GATE_MISMATCH` → exit 3 and `E_SCHEMA_MISSING` → exit 1, per §3.12, as stubs); `uv sync` works from a clean clone; a dNh dev branch resolves the core by both the `path` and `workspace` forms, and that branch's CI installs a pinned wheel and passes (merging it is dNh's decision, not a ChatX exit criterion); `sqlite_version` recorded and ≥ floor |
| **P0.5 Spikes** (no shipped code) | (a) the structure-only probe on the owner's real `chat.db`: schema-probe result, typedstream decode coverage, reaction-prefix linkage, multi-chat counts, 2006/3006 codes; (b) Presidio + spaCy, GLiNER and OpenAI Privacy Filter recall on the first ~300 owner-labelled messages; (c) dNh dedupe-continuity replay on a copy of dNh's database: new, duplicate and would-correct counts; (d) the chosen local model's structured output at target throughput; (e) `vec0` scan timing at 100k and 1M synthetic chunks | Each spike's numbers recorded in `docs/measurements.md`. A result may reorder or cut later phases. The schema stays `v2-draft` until (a) has run |
| **P1 Extraction core** | Schema v2 (frozen after P0.5 a); acquisition; iMessage (manifest, folds, decoders, attachments); unencrypted backups; Instagram (mojibake, limits); WhatsApp; PDF; email; identity; fixtures from schema snapshots; `chatx import imessage --probe` | Golden tests per source, with the real-shape fixtures of §7; schema drift test; WAL snapshot test; reaction-fold property test; id-stability tests; a real `chat.db` smoke run documented with counts; the dNh adapter test passes on a dNh branch with dNh's suite green; V1 resolved; old bplist fixtures and tests that pin retired behaviour deleted |
| **P2 Case store, chunking, CLI skeleton** | Store, migrations, invariants, lock, CAS; `case create/status/verify/repair/resume/backup/delete-source/purge`; manifest, `runs`, metrics; FTS5 over messages; chunking (§3.8) | Import of 100k synthetic messages with throughput and RSS **recorded** in `docs/measurements.md`; `case verify` checks every §3.5 invariant and re-hashes attachments; a crash-and-resume test; deterministic chunk ids test |
| **P3 Shield v2 and local provider** | Presidio integration, ported recognizers, NER engine chosen by the eval, language id, surrogates and map custody, eval harness (synthetic and real), `shield_evals`, gate and tokens, taxonomy-based hard-fail with definitions drafted for the owner; `ChatProvider` + `OpenAICompatProvider`, capability probe, locality check, second-opinion judge | Synthetic eval in CI; refusal-path tests (exit 3, `E_GATE_MISMATCH`, `E_VENDOR_TERMS`, `E_PROVIDER_NOT_LOCAL`, `E_VISIBILITY_LEAK`); token-grammar and escaping tests; mutation kill rate ≥ 80 % on shield and gate; once the owner's labels exist, the real-sample evaluation — including the second-opinion judge's recall on the same sample — is run and recorded. Passing P3 on synthetic results unlocks the **local** pipeline only. The cloud tier unlocks when the real-sample evaluation passes; that is a separate local gate, recorded and reported as such |
| **P4 Enrichment and cloud provider** | `labels.yml` 1.3 and its compiler; structured enrichment with typed outcomes; cache; stateful hysteresis; calibration on the gold set; `AnthropicProvider`; the operation contract; the cloud path through the gate | Contract tests against recorded responses (no live model in CI); an owner-run live smoke of the request shape against the configured cloud model; the adversarial prompt-injection set passes; every enrichment row joins to its messages and appears in the run report |
| **P5 Index, query, export** | Embedding spaces, `vec0`, filter-then-KNN, RRF, citations, `query`, citation-support check, retrieval gold set; export bundle with custody; `import-bundle` | Recall@k on the gold set recorded; retrieval latency at **1M synthetic chunks** recorded; a bundle verifies and round-trips through `import-bundle`; stale-citation detection test. If the latency target fails twice, an ADR chooses between file-based ANN candidates (usearch, hnswlib) |
| **P6 Analysis lane and extras** | Construct map and indicators; image enrichment; audio transcription; encrypted backups | Each sub-feature has its own ADR, evaluation and opt-in flag; analysis labels have inter-rater agreement before shipping |
| **P7 MCP and polish** | `chatx mcp serve` (redacted views; `--expose-raw` recorded as egress); generated CLI and error reference; MkDocs; old repo archived | Docs generated from code; an MCP egress test; old repo tagged, and its README points here |

Each phase gets its own implementation plan (superpowers:writing-plans).

---

## 7. Quality gates (global)

- **Static checks:** `ruff check` and `ruff format --check`; `mypy --strict` for the core and a strict configuration for the app.
- **Coverage:** `pytest --cov-fail-under=90` over both whole packages with no omit list, plus branch coverage and a `mutmut` kill rate of at least 80 % on shield and gate code (opus F-22, F-35).
- **Supply chain:** `uv lock --check` and `pip-audit`; dependency and model hashes pinned.
- **Fixtures:**
  - **Generated, not copied.** Fixture databases are generated from per-macOS-version **schema snapshots** (DDL only, captured by the probe; no rows from the owner's data), so goldens cannot pass against a schema that does not exist (opus F-21).
  - **Real-shape artifacts.** Fixtures include:
    - typedstream `attributedBody` blobs (dNh's observed prefixes plus sanitized probe captures);
    - `p:0/` and `bp:` reaction guids;
    - `thread_originator_guid`, `~/Library` paths and multi-chat joins;
    - `date_edited`/`date_retracted`, group events and sticker type 1000;
    - WhatsApp Android and iOS exports in at least two locales;
    - Instagram with mojibake;
    - `.eml` with `References`.
  - **Legacy tests.** The old bplist fixtures, and tests that pin retired behaviour, are deleted at the end of P1 (grok F17).
  - **Decoder test.** dNh's `test_decodes_four_byte_little_endian_length` actually encodes its `0x8000` length in the two-byte form. The ported test is fixed to exercise the four-byte form (chatgpt F09).
- **Property tests:**
  - the Apple-epoch converter (bounds 2001–2100, `0` → `None`);
  - handle normalization;
  - reaction and edit fold algebra (any interleaving of adds and removes reaches the same state and history);
  - the WhatsApp grammars;
  - id stability across overlapping exports.
- **Security tests:**
  - the no-socket core and offline app stages;
  - a cloud send without a valid token fails;
  - modes on the salt and secrets;
  - no attachment or id field on cloud request models;
  - token escaping;
  - the adversarial injection set;
  - a log-allowlist test, which greps a fixture run's logs for fixture text.
- **Performance.** Numbers are measurements, not promises. `pytest -m perf` (opt-in) records throughput, latency and RSS into `docs/measurements.md`, with the machine and commit.
  - The old targets become tracked measurements, promoted to gates only once met twice: ≥10k msg/min ingest, p95 ≤150 ms retrieval, <4 GB for 1M messages, and a cache hit rate ≥80 %.
  - P5 measures at 1M chunks.
- **CI vs local.** CI shows the synthetic shield evaluation only. The real-sample evaluation uses the owner's data, so it is a separate local gate, recorded per run. The docs say so (chatgpt F33).

---

## 8. Migration from the old repository

**Keep (minimal change):**
- `imessage/report.py`.
- `identity/normalize.py`: the HMAC scheme, now with a per-case salt and mode 0600.
- `utils/json_output.py` (quarantine) and `cli_errors.py` (→ RFC 9457).
- `config/labels.yml` (→ schema 1.3).
- `schemas/message.py`, as the v1 reference for the v2 mapping.

**Port with rework:**
- `imessage/db.py`: only its location is kept. The body is replaced by backup-API acquisition.
- `imessage/backup.py`: the `Manifest.db` logic stays, acquired the same way. The password flag is removed.
- `imessage/extract.py`: the structure stays. The column manifest, contact filter and folds are rewritten.
- `imessage/reactions.py`: the code map is rewritten.
- `imessage/time.py`: bounds become 2001–2100, `0` becomes `None`, and there is no `now()`.
- `imessage/attachments.py`: adds `expanduser`, containment, `backup_dir` threading and CAS.
- `instagram/extract.py`: adds mojibake repair and limits.
- `transformers/chunker.py`: adds deterministic ids and per-sender pseudonyms.
- The regex set becomes Presidio recognizers, and the `PolicyShield` concept becomes §3.7.
- The run manifest and metrics become `runs`.
- The relationship types and patterns become `docs/analysis/legacy-patterns.md`.

**Take from dNh_CRM:**
- `ingest/imessage_attributed_body.py`, its 1013-line test file (with the four-byte test fixed) and the probe script.
- `ingest/whatsapp_export.py`, rewritten: both grammars, structural system lines, date order, no silent UTC.
- `ingest/email_eml.py`, extended: recipient headers, direction, zone rule, header-based ids.
- `idempotency.py`'s canonical JSON, as the starting point for RT-2.

**Tests:**
- The 35-file iMessage suite is ported where it tests behaviour that is kept.
- Tests that pin retired behaviour are deleted with the old fixtures at the end of P1: bplist bodies, `msg_{rowid}` ids and the 3000–3999 "custom" map.

**Discard.** The §3.14 list; `docs/` as specification; `.taskmaster/`, `.serena/`, `context_portal/`, `node_modules/`; the root scripts.

**Disposition of every old command and documented feature** *(codex F27, chatgpt F35)*:

| Old command or feature | Disposition |
|---|---|
| `imessage pull` | ported → `chatx import imessage` |
| `imessage pull --from-backup` | ported → `chatx import imessage --from-backup` (unencrypted; encrypted backups P6) |
| `--backup-password` | removed until P6 implements decryption |
| `imessage audit` (missing attachments) | ported → the import's missing-attachments report and `chatx case verify` |
| `imessage pdf` | ported → `chatx import pdf` (`platform=pdf_transcript`, `--assume-tz`) |
| `instagram pull` | ported with rework → `chatx import instagram` |
| `transform` | ported → `chatx chunk` |
| `redact` (+ `--preflight`) | reworked → `chatx shield redact` + the gate (§3.7) |
| `enrich` | reworked → `chatx enrich` |
| `enrich-multi` | dropped *(decided)*: it fails to import in v1; its passes fold into one structured enrichment (§3.9) |
| `index` (`--store chroma/multi`, `--multi-vector`) | reworked → `chatx index build`; Chroma and the multi-vector store retired |
| `query` | reworked → `chatx query` |
| `extract` (stub) | dropped → replaced by `chatx import` |
| `pipeline` (stub) | dropped *(decided)*: stages stay separate commands |
| `analyze` (stub) | → `chatx analyze`, P6 |
| `backfill` | → `chatx import … --resume` |
| `index update` | → `chatx index build --incremental` |
| `simulate`, `reply` | dropped: no consumer; generating or sending messages is out of scope |
| `timeline show` | → time filters on `chatx query` (P5) |
| `factors analyze` | → analysis lane (P6) |
| `tokens inspect` / token ledger | dropped *(decided)*: replaced by per-call usage in `runs` |
| HTTP API `/v1/query`, `/v1/simulate`, `/v1/reply` | dropped (non-goal) |
| Neo4j graph, psychology multi-vector search, `mental-bert` | retired; the analysis lane is P6 |
| differential-privacy summaries | dropped (non-goal) |
| image enrichment | P6, behind an ADR |
| voice-note transcription | P6, behind an ADR |
| PDF OCR fallback | dropped: text layer only; `ocr` removed from `text_source` |
| WhatsApp import | P1, text exports (Android and iOS) |
| generic TXT importer | dropped until an importer exists; `txt` removed from `platform` |
| iCloud attachment download | non-goal; reported as `missing_reason` |
| "1M-message corpus" NFR | tracked measurement at P5 |
| cache hit ≥80 % NFR | tracked measurement from P4 |

**Old repo.** It is tagged `pre-rearchitecture-2026-10-20`, its README gets a banner pointing to `chatstack`, and it gets no further feature work.

---

## 9. dNh_CRM integration

**Dependency.** Release builds pin the core wheel by version and sha256. Development branches may use the `path` or `workspace` form (§3.2, E8).

**Adapter** `canonical_message → dNh EventEnvelope` *(codex F04, agy F-05, opus F-14, chatgpt F03)*. It is **total**: every `(platform, direction, content_kind)` triple matches exactly one rule below. The adapter test expands the rules over the enums to prove it. Skips are counted in the adapter report, never silent.

| Rule | Matches | Disposition |
|---|---|---|
| 1 | `imessage` or `sms`, `inbound`, `text` | `MSG_INBOUND_RECEIVED`, `EventPayload(text)`, channel from platform |
| 2 | `imessage`, `inbound`, `attachment_only` | `MSG_INBOUND_RECEIVED`, `IMessageAttachmentOnlyPayload` (dNh allows this payload only for inbound client iMessage, `events.py:2008-2015`) |
| 3 | `whatsapp` or `email`, `inbound`, `text` | `MSG_INBOUND_RECEIVED` with dNh's `WHATSAPP` or `EMAIL` channel |
| 4 | any platform, `outbound`, `text` | the new dNh type `msg.outbound.imported` (owner item 8) once dNh ships it; until then skipped with a count |
| 5 | `instagram` or `pdf_transcript`, any direction or kind | skipped with a count, until dNh adds `Channel` members for them |
| 6 | `content_kind` in `reaction_only, system, empty, unsupported` | skipped with a count |
| 7 | `attachment_only` other than rule 2 | skipped with a count |
| 8 | `direction = system` | skipped with a count |

Rules are applied in order, and the first match wins. The totality test checks that each triple reaches exactly one rule.

**Fields:**
- `msg_id` → `external.source_message_id`.
- `conv_id` → `conversation_id` (`imessage:{conv_id}`).
- `sent_at` → `occurred_at`, which is aware, as dNh requires.
- Empty `text` is never sent; dNh's `EventPayload.text` has `min_length=1`.

**Dedupe** *(owner item 5)*:
- dNh keeps its own `build_imessage_dedupe` formula. The core supplies its inputs (`guid`, `rowid`) through `provenance.source_guid` and `provenance.source_row`.
- `content_hash` is stored **in addition**, not instead. No historical row changes its `dedupe_hash`.

**Outbound history** *(owner item 8)*:
- A small dNh schema change adds a dedicated event type, for example `msg.outbound.imported`.
- `msg.outbound.manual` is not reused, because dNh's opportunity, action, RAG and CRM-intel services consume it, and years of imported history must not look like fresh sends.

**Backfill** *(chatgpt F14, owner item 12)*:
- It is a separate one-time migration. The adapter replays the whole snapshot, not only dNh's lookback window, and rows dNh already holds dedupe as before.
- dNh events stored without text that now decode are **left as they are and counted**; no correction event is added. The P0.5 replay spike (c) reports the new, duplicate and would-correct counts before anything is sent.

**Cut-over** *(opus F-32, owner item 9)*:
- The adapter and dNh's own chat.db parsers run side by side on real ingest for **30 days**, with their outputs compared.
- dNh deletes its parsers (`ingest/imessage_source.py`, `ingest/imessage_mapper.py`) only if the two never disagree. A disagreement is fixed and restarts the 30 days *(decided)*.
- **What is compared** *(decided, builder check)*: the messages both paths ingest, which are the inbound iMessage rows dNh's own reader takes (`is_from_me = 0`, with text).
  - A **disagreement** is a message present in one and missing from the other, or one with a different text, sender or time.
  - Rows only the adapter produces (text decoded from blobs, outbound, reactions) are reported as **additions**, not disagreements.
- **The outbound event type** is a dNh change on dNh's schedule. It is not a P1 exit criterion; until it ships, outbound is skipped with a count.
- BlueBubbles live capture stays in dNh.

**What dNh gains:**
- typedstream text where the `text` column is empty, through its own decoder, finally wired;
- reactions and replies, which it may ignore;
- outbound history, once the new event type exists.
dNh is not required to change its store, its Telegram path or its BlueBubbles bridge.

**Handles.** Where dNh's `conversation_contacts`/`contact_identities` tables need handles, the core's normalized `sender.handle` is the input.

**Aside.** dNh's own venv links SQLite 3.47.1, which is inside the WAL-reset range (§3.3). dNh's source never sets `journal_mode`, so it probably runs in rollback-journal mode, where that bug does not apply. This is unverified; it belongs to dNh, not this program.

---

## 10. Risks and unknowns (resolve by measurement)

| # | Item | Status in rev 2 |
|---|---|---|
| V1 | iMessage reaction codes 2006/3006 (custom emoji) and exact removal semantics | Open. P0.5 (a) counts them on the real database; P1 fixtures them |
| V2 | Typedstream coverage of the owner's real blobs | Open. P0.5 (a) measures it; the guarantee is stated as partial (§3.4); blobs are always kept |
| V3 | PII recall on chat text (short, slangy, names without titles) | Open. P0.5 (b), then the P3 eval, choose between Presidio + spaCy, GLiNER and OpenAI Privacy Filter |
| V4 | sqlite-vec at 1M chunks | Partly answered: exact scan, pre-v1, v0.1.9 (E9). P0.5 (e) and P5 measure; ADR candidates if the target fails twice |
| V5 | macOS Full Disk Access / TCC for `chat.db` | `E_DB_ACCESS_DENIED`, documented |
| V6 | WhatsApp export time zone | Resolved by design: `--assume-tz` required, `time_source = assumed_tz` |
| V7 | Taxonomy counts and validity | Counts confirmed by parse (55 coarse, 99 fine). Validity is enforced by the 1.3 compiler |
| V8 | uv workspace with dNh's dependency from outside it | Answered (E8); P0 proves both forms |
| V9 | Observed vs requested model | Anthropic responses carry `model`. OpenAI-compatible endpoints that do not echo it are recorded UNKNOWN |
| V10 | SQLite runtime floor | Answered (E4). The interpreter is chosen by the SQLite it links; the old venvs (3.47.1) are below the floor |
| V11 | Per-case encryption with sqlite-vec and FTS5 | Open (RT-19). Opt-in only until shown |
| V12 | Anthropic request surface changes | Facts as of 2026-10-21 (E2). The capability probe and `conformance.md` catch drift |
| V13 | What Presidio V2 changes | Open (RT-10). Pinned version for the P3 eval |
| V14 | dNh's new outbound event type lands through dNh governance | Outbound is skipped with a count until it ships |
| V15 | Labelling effort: about 600 positives per class, a gold set, and a retrieval gold set | Owner committed to the shield sample and the gold set, and chose the strict gate (item 14). Rare classes keep the cloud tier locked until they reach 598 real positives (§3.7) |

---

## 11. Left to the builder

- **Naming and storage details:** module and table naming; exact DDL and indexes; the SQL migration runner.
- **Shield:** the NER engine, within the P3 eval; the token-counting method for chunks.
- **Embeddings:** the embedding model and dimension, within ≤768; the quantization type, within the rescoring rule.
- **Fixtures:** fixture generation details.
- **CI and logging:** the CI matrix (macOS arm64 required, Linux x86_64 nice to have); the structlog configuration.
- **CLI:** option names beyond those listed; how `chatx providers list` discovers models.
- **Export bundle:** the signing tool (RT-6); its format beyond "zip + `MANIFEST.sha256` + `custody.json`"; whether report PDF rendering uses an existing library or is dropped from P5.
- **The dNh adapter:** whether its rules live as data or code, provided the totality test holds.

---

## 12. Owner decisions (answered 2026-10-21)

These were asked in this session with the multiple-choice tool. Answers are the owner's option labels. Items 1–3 were rev 1's open items; 4–13 came from the audit; 14 came from the builder check of rev 2.

| # | Question | Answer | Where it lands |
|---|---|---|---|
| 1 | New repo, or carry ChatX's git history? | New clean repo | §3.2 |
| 2 | What is a case? | Case per import set | §3.5 |
| 3 | Label a real sample for the shield? | Yes, full sample (about 600 per entity class) | §3.7, §6 P0.5 (b) |
| 4 | Label an enrichment gold set? | Yes | §3.9 |
| 5 | dNh dedupe formula | dNh keeps its formula | §9 |
| 6 | Where the pseudonym map lives | Separate secrets file | §3.5, §3.7 |
| 7 | Encryption at rest per case | Opt-in, require FileVault | §3.5, §3.15 |
| 8 | dNh event type for imported outbound history | New imported type | §9 |
| 9 | When dNh deletes its chat.db parsers | After 30-day parallel run | §9 |
| 10 | Hard-fail list and `cloud_allowed` policy | Special categories stay local | §3.7, §3.9 |
| 11a | Whose data is this tool for? | My own conversations | §1, §2.1 |
| 11b | May redacted chunks of other people's messages go to a cloud model? | After gates, zero retention | §2.1, §3.6, §3.7 |
| 12 | dNh events stored without text that now decodes | Leave them and count | §9 |
| 13 | Licence of `chat-extraction-core` | MIT | §3.2 |
| 14 | How strict the cloud gate is per class | Strict: every class at 99.5% on real data | §3.7 |
| — | Derived `msg_id` with an occurrence index | Approve occurrence index | §3.4 |
| — | Model selected for the ChatGPT web audit | GPT-6 Pro | audit README (the session called itself "GPT-6 Astra Pro"; no runtime receipt) |

**Follow-ups that remain with the owner:**
1. **P3:** approve the written hard-fail definitions (including `minors_involved`) and each coarse label's `cloud_allowed` value in `config/labels.yml` 1.3.
2. **Before the first cloud run:** state the account's terms in `[providers.cloud]` (`zero_data_retention`, `training`).
3. **Rare classes (§3.7):** settled by item 14 (strict). There is no per-case exclusion of a class; a class short of 598 real positives keeps the cloud tier locked.
4. **P6:** analysis labels need a **second human rater** for inter-rater agreement (§3.11). Without one, analysis labels do not ship.

---

## 13. Research targets

These are the research targets this design raises, with their status as of 2026-10-21. The auditors' own 239 targets are in `docs/superpowers/audits/2026-10-20-design-audit/out/research-targets-*.md` and have not been de-duplicated.

| RT | Topic | Status |
|---|---|---|
| RT-1 | SQLite minimum version for WAL/backup-API correctness | Answered (E4): §3.3 floor |
| RT-2 | Canonical JSON: JCS (RFC 8785) vs dNh `canonical_json` | Open |
| RT-3 | Generic NSAttributedString typedstream decoders | Open |
| RT-4 | sqlite-vec quantized vector types and scan cost at 1M rows | Partly: exact scan, pre-v1 (E9); quantized types and cost open (P0.5 e) |
| RT-5 | Local embedding models by dimension and quality for chat text | Open |
| RT-6 | Bundle signing tool and verification UX | Open |
| RT-7 | Anthropic API for this workload | Mostly answered (E1, E2a–E2d); open: prompt caching and Batch API |
| RT-8 | uv path/workspace dependency syntax | Answered (E8): §3.2 |
| RT-9 | iOS encrypted-backup decryption libraries | Open (P6) |
| RT-10 | Presidio stewardship and what V2 changes | Partly: stewardship confirmed (E5); V2 open |
| RT-11 | Small NER engines for short, slangy chat text | Open; OpenAI Privacy Filter added as a candidate (E5) |
| RT-12 | Structured-output support across local servers | Partly (E3); open: llama.cpp and LM Studio reproducibility, MLX |
| RT-13 | Confidence calibration on small gold sets | Open |
| RT-14 | macOS exposure controls (`.noindex`, Time Machine, iCloud-synced folders) | Open |
| RT-15 | Inter-rater agreement protocol for analysis labels | Open |
| RT-16 | Local language identification for short chat messages | Open |
| RT-17 | Binding a gate token to the final request bytes (transport hooks) | Open |
| RT-18 | Evaluating citation support in answers | Open |
| RT-19 | Per-case encryption alongside sqlite-vec and FTS5 | Open |

---

## 14. Change log: rev 1 → rev 2

Each row is one theme of the cross-audit matrix (`docs/superpowers/audits/2026-10-20-design-audit/out/cross-audit-matrix.md`). Findings are listed by auditor, as the matrix places them. The full reasoning for each change, finding by finding, is in `out/design-revision-plan.md` under the same theme. This table is generated from the matrix by the build script, so every one of the 148 findings appears exactly once.

| Theme | Sections | What changed | Findings | Owner items | Facts / research |
|---|---|---|---|---|---|
| T01 Acquisition & WAL safety | §3.3, §3.5, §7 | Acquisition via the SQLite backup API and `integrity_check` replaces the sequential copy opened with `immutable=1`; the acquisition record lands in `sources`; SQLite floor ≥ 3.51.3 (`E_SQLITE_TOO_OLD`); WAL snapshot fixture test. | codex F05, F28 · grok F5 · agy F-01 · opus F-09 · chatgpt F01, F37 | — | E4; RT-1 |
| T02 Message identity & content hash | §3.4, §3.8, §5 | Canonical JSON (JCS); `content_hash` over the immutable core plus `record_hash`; derived `msg_id` with an occurrence index; id stability contract; five identity concepts; `msg_id_aliases`; deterministic chunk ids. | codex F02 · grok F13 · agy F-02, F-03 · opus F-01, F-13 · chatgpt F06, F08 | msg_id confirmation | RT-2 |
| T03 Schema fidelity & forensic columns | §3.4, §4 | iMessage column manifest and schema probe; `source_meta` required for iMessage; `message_blobs`; replies from `thread_originator_guid`; edits and unsends; `system_event`; multi-chat rule; participant snapshot; `unsupported` content kind; `telegram`, `txt`, `ocr` enum values removed. | codex F01 · grok F4, F20 · agy F-09 · opus F-16, F-33 · chatgpt F07 | — | — |
| T04 Time & timezone | §3.4, §4, §7 | `sent_at_raw`, `time_precision`, `time_source`, `source_tz`; `--assume-tz` required (`E_TZ_REQUIRED`); unparseable timestamps quarantined; one Apple-epoch converter with 2001–2100 bounds. | codex F03 · grok F6 · chatgpt F02 | — | — |
| T05 dNh integration, dedupe & envelope mapping | §4, §5, §9 | Total adapter with a rule table and totality test; outbound history to a new dNh event type; dNh keeps its dedupe formula; backfill counts instead of corrections; 30-day parallel run before dNh deletes its parsers; core has no network dependencies; JSONL only via `--emit-jsonl`. | codex F04 · grok F18 · agy F-05, F-06 · opus F-14, F-32 · chatgpt F03, F14 | 5, 8, 9, 12 | — |
| T06 iMessage decoding — attributedBody, reactions, replies, edits, multi-chat | §3.4, §6, §7 | Reaction prefix stripping and code map (`unknown` kind, no range mapping); stickers as attachments; decoder strategies with a partial guarantee, the U+FFFC rule and `text_decode_status`; `--probe`; P0.5 spike (a); four-byte decoder test fixed. | codex F06 · grok F11 · agy F-07, F-10, F-20 · opus F-08, F-17, F-34 · chatgpt F09 | — | RT-3 |
| T07 Attachments & path containment | §3.5, §4 | `AcquisitionContext`; contact scope through chat participants (old `is_from_me` filter retired); `expanduser`/`resolve`/containment with `missing_reason`; `backup_dir` threaded through; content-addressed write procedure. | codex F07 · agy F-08, F-23 · chatgpt F10, F11 | — | — |
| T08 Other importers — WhatsApp, Instagram, PDF, email | §4 | Importer fidelity table with source locators; WhatsApp Android and iOS grammars with structural system lines and explicit date order; Instagram mojibake repair; PDF as `pdf_transcript` without fabricated times; email recipient headers and header-based ids; `phonenumbers` handles; dispositions sum to input counts. | codex F08 · grok F12 · agy F-04, F-11, F-19 · opus F-07, F-15, F-31 · chatgpt F12, F13 | — | — |
| T09 Policy Shield — evaluation statistics, hard-fail, chunk leakage | §3.7, §3.8 | Shield claims per-class recall only; class set fixed by the shield's entity-class list, including quasi-identifiers; declared languages; real-sample eligibility; Clopper–Pearson bounds and `INSUFFICIENT_SUPPORT`; second-opinion estimand, sample size and judge recall; hard-fail from the taxonomy; special categories local; degraded runs; cloud chunk construction. | codex F09 · grok F1, F8 · agy F-13, F-14, F-16 · opus F-04, F-05, F-23 · chatgpt F05, F15, F16 | 3, 10 | RT-16 |
| T10 Cloud egress gate & bypass routes | §3.6, §3.7, §3.12, §5 | Gate token per request, bound to the final bytes, operation and destination; locality computed (`E_PROVIDER_NOT_LOCAL`); vendor terms required (`E_VENDOR_TERMS`); MCP serves redacted views and `--expose-raw` counts as egress; two compiled label enums. | codex F10 · grok F7 · agy F-15 · opus F-03, F-06 · chatgpt F04 | 11b | RT-17 |
| T11 Pseudonym tokens, salt & map custody | §3.5, §3.7 | Typed sequential surrogate tokens with an exact grammar and escaping; per-case salt; map in `secrets/pseudonyms.sqlite3`; bundles exclude secrets by default; re-hydration local, locked and recorded. | codex F11 · grok F3 · agy F-12 · opus F-12 · chatgpt F17 | 6 | — |
| T12 Storage invariants, DDL & migrations | §3.5 | Single-writer lock, PRAGMAs, runs and watermarks, source status, foreign-key policy, migration checksums, `case verify` invariants, evidence/derived split with `case repair`, `case backup`. | codex F12 · agy F-21 · chatgpt F24 | — | — |
| T13 Scale & vector index | §2, §3.10, §6 | Single-directory case (G3); filter-then-KNN with `--exhaustive`; ≤768-dimension int8 vectors with float rescoring; embedding spaces; sqlite-vec pinned and failing loudly; P5 measured at 1M chunks with an ANN ADR fallback. | codex F13 · grok F9 · agy F-17 · opus F-19 · chatgpt F25 | — | E9; RT-4, RT-5 |
| T14 CAS, export & manifest custody | §1, §3.10 | Bundle with `MANIFEST.sha256`, `custody.json`, optional signature and optional RFC 3161 timestamp; forensic claim narrowed; `import-bundle`; exclusions (secrets, analysis, content involving minors). | codex F14 · opus F-20 · chatgpt F26 | 11a | RT-6 |
| T15 Provider protocol & operation | §3.6 | `ChatProvider`/`EmbeddingProvider` split with local-only embeddings; capability-gated sampling; Anthropic request facts; thinking counts toward `max_tokens` and the 800-token cap is removed; structured-output probe; typed outcomes; operation contract; `call_config_hash`; prompt-injection posture; config example rewritten. | codex F15, F16 · grok F2 · agy F-22 · opus F-02, F-27, F-28 · chatgpt F19, F20, F21 | — | E1, E2a, E2b, E2c, E2d, E3; RT-7, RT-12 |
| T16 Taxonomy, labels, enrichment & psychology validity | §3.9, §3.11 | `labels.yml` 1.3 with per-label `cloud_allowed`; compiler and two enums; calibration on the gold set; stateful hysteresis; cache key; abstention; analysis lane rebuilt as documented legacy rules plus observable-pattern indicators with inter-rater agreement and review state. | codex F17, F18, F20 · grok F14, F19 · agy F-18 · opus F-18, F-25 · chatgpt F18, F22, F28 | 4, 10 | RT-13, RT-15 |
| T17 Retrieval, citations & RRF | §3.10 | RRF with explicit `k` and depth; message-level fusion with filters first; span citations at a `record_hash` with stale detection; derived-row invalidation; retrieval gold set and recall@k; citation-support check. | codex F19 · grok F15 · chatgpt F27 | — | RT-18 |
| T18 Packaging & uv workspace | §3.2, §3.3 | dNh pins a built wheel by version and sha256; release contract; both uv development forms; `importlib.resources` and `E_SCHEMA_MISSING`; listed core dependencies; model artifact pins; MIT licence. | codex F21, F22 · grok F16 · opus F-10 · chatgpt F29, F30, F36 | 13 | E8; RT-8 |
| T19 Phase sequencing & prerequisites | §6 | P0.5 spikes (a)–(e); provider protocol moves to P3 and chunking to P2; each phase's exit uses its own outputs; the cloud tier unlocks only on the real-sample evaluation; schema stays draft until the probe; analysis outputs opt-in. | codex F23 · grok F10 · opus F-24 · chatgpt F32 | 3 | RT-9 |
| T20 Threat model & local exposure | §2.1, §3.5, §3.13, §3.15 | Threat model and intended-use section; `.noindex` case root, iCloud refusal, Time Machine exclusion, FileVault required, per-case encryption opt-in; log field allowlist; offline models; content-landing table; adversarial test set; `case purge`. | codex F24 · opus F-11, F-26 · chatgpt F23, F31 | 7, 11a, 11b | RT-14, RT-19 |
| T21 Tests, fixtures & coverage | §5, §7, §8 | Fixtures from schema snapshots and the real-shape fixture list; legacy fixtures deleted after P1; no-omit coverage plus branch and mutation floors on shield and gate; CI tests the installed wheel; real-sample evaluation is a local gate. | codex F25 · grok F17 · agy F-24 · opus F-21, F-22, F-35 · chatgpt F33 | — | — |
| T22 Operations, intent regression & CI gates | §3.12, §6, §8, App. A | CLI additions; exit codes 0–4 with gate refusal at 3; behaviour contract; disposition table for every old command and feature; workflows rewritten; Appendix A.1 corrections. | codex F26, F27 · agy F-25 · opus F-30 · chatgpt F34, F35 | — | E7 |
| T23 Ecosystem currency (external docs) | §3.3, §3.7, §3.12 | RFC 9457 replaces RFC 7807; Presidio stewardship noted and the version pinned; OpenAI Privacy Filter added as a candidate; `conformance.md`. | codex F29, F30 · opus F-29 · chatgpt F38 | — | E5, E6; RT-10, RT-11 |
| — | Header, §1, §2.1, §3.2, §3.5, §12 | Owner decisions not tied to a finding: new clean repo; case per import set; the tool is for the owner's own conversations. §12 records every answer. The ChatGPT run's model is recorded as owner-reported in A.5. | — | 1, 2, 11a, msg_id confirmation, ChatGPT model confirmation | — |
| — | App. A.4, A.5 | SQLite link versions added; audit summary of rev 1 added. | — | — | E4 |
| — | §1, §3.5, §3.7, §3.8, §3.9, §3.12, §4, §5, §6, §9, §10, §12 | Builder check of rev 2 (`out/builder-check-rev2.md`): 11 questions and 9 possible contradictions. Seven contradictions were resolved; two were not conflicts. Ten questions were settled as designer's calls, marked *(decided, builder check)* or *(clarified, builder check)*. One was answered by the owner: item 14, a strict gate. | — | 14 | RT-17 |

**Declined or not changed on purpose:**

- **SQLite per case, no services** (§3.5). The scale concerns are handled by the query plan, quantization and measurement, not by bringing back a server.
- **Presidio as the starting framework** (§3.7). It stays a candidate, decided by the P3 evaluation.
- **New repo rather than history carry** (§3.2). The owner confirmed this (item 1).
- **HMAC-128 handle pseudonyms** (`sender.pseudonym`) are kept. Only redaction tokens switch to surrogates (opus F-12).
- **A source-file fingerprint inside `msg_id`** (opus F-13) is declined. It would break id stability across re-exports.
- **Stopping the whole run when the shield fails** (chatgpt F15's wording) is declined. The cloud stage stops and the local pipeline continues, because nothing leaves the machine on the local path.
- **External attestation for bundles** (chatgpt F26) stays optional (RFC 3161, owner-chosen). The forensic claim is narrowed instead.
- **Splitting P1 into P1a/P1b** (opus F-24's suggestion) is not adopted. The P0.5 spikes take the risk out of P1 first, and the plans written per phase may still split it.

### Rev 2 → rev 2.1 (2026-10-22): owner decisions from the P0 packet

The P0 packet (`docs/superpowers/plans/2026-10-21-p0-workspace-packet.md`) found three gaps in rev 2 that it could not resolve on its own authority. The owner decided them on 2026-10-22. Only the first changes spec text; the other two are recorded here so the spec and the packet say the same thing.

- **G-B — exit code for `E_SCHEMA_MISSING` (§3.12 vs §6).** §3.12 maps `E_SCHEMA_MISSING` to exit 1 and only `E_GATE_MISMATCH` to exit 3; the §6 P0 row read as if both were exit 3. Decision: §3.12 stands. The P0 row now reads "`E_GATE_MISMATCH` → exit 3 and `E_SCHEMA_MISSING` → exit 1, per §3.12, as stubs".
- **G-A — "two empty packages" vs failure-path stubs (§6, P0 row).** The stubs need a little code to run. Decision: the packages may hold exactly the stubs the P0 packet lists (Tasks 3 and 4: an `errors.py` and a resource loader in the core raising `E_SCHEMA_MISSING`; an app entry point mapping `E_GATE_MISMATCH` to exit 3) and nothing beyond them. "Two empty packages" in the P0 row is read with that allowance; the wording is left as is.
- **G-E — the pinned wheel dNh's CI installs (§6 P0 exit criterion vs the release contract, §3.2).** The release contract ties wheels to `core-vX.Y.Z` tags and P0 named no tag. Decision: P0 ends by tagging `core-v0.0.1a0`; a `release` workflow builds the core wheel from the tagged tree and publishes it with `SHA256SUMS` as a GitHub pre-release; dNh pins that version and digest. The adapter-test step the contract requires before a tag has nothing to run at P0 and is recorded as NOT_RUN in the release notes. The core package therefore starts at version `0.0.1a0` (packet decision B4).

---

## Appendix A — Current-state evidence (condensed)

### A.1 Code-reality grades (`src/chatx`, 2026-10-20; two rows corrected in rev 2)

| Area | Grade | Key evidence |
|---|---|---|
| iMessage extraction (db, backup, reactions, replies, attachments, audit) | REAL | 35-file test suite; `attributedBody` is a `plistlib`→UTF-8 heuristic; `is_from_me` scope bug in `get_conversation_guids` |
| Instagram ZIP, PDF text | REAL / THIN | No OCR engine; PDF timestamps synthetic |
| extract → transform | BROKEN | `write_messages_with_validation` wraps `{"messages": …}`; `transform` expects a bare list |
| redact | REAL but ADVISORY | coverage = token ratio. By default it warns and exits 0. It exits 1 only under `--preflight`, when the preflight fails on hard-fail or low coverage (`cli/main.py:337-350`; corrected in rev 2, chatgpt F35). Hard-fail flag inverted |
| `--allow-cloud` | ADVISORY | no cloud client in `src/` |
| enrich / enrich-multi | BROKEN | enrichments never reach the index; `multi_pass_pipeline` import error; taxonomy loader reads a key that does not exist |
| index / query | WIRED, UNTESTED HAND-OFF | Chroma. The psychology multi-vector store **is** reachable through `--store multi` and `--multi-vector` (`cli/main.py:737-739, 781, 825-826, 862`). Rev 1 said "dead to CLI"; corrected per chatgpt F35 |
| graph (Neo4j), embeddings providers, DP summaries, image enrichment | DEAD / STUB | never reachable from CLI; placeholders |
| `analyze`, `pipeline` | STUB | print "not yet implemented" |
| Coverage gate | HOLLOW | `pyproject` omits `redaction/*`, `transformers/*`, `enrichment/*`, `indexing/*`, `schemas/validator.py`, `transcribe/*` |
| Deps | DRIFT | `yaml`, `tenacity`, `psutil`, `requests`, `fitz`, `PyPDF2`, whisper undeclared; `openai`, `anthropic`, `cohere` declared unused |
| Hardcoded values | HARDCODED | `gemma2:9b-instruct-q4_K_M` ×4, `claude-3-sonnet-20240229`, Neo4j password `"password"` |

### A.2 dNh_CRM trace (2026-10-20)

- **Message model.** A message is an `EventEnvelope` (`dnh.crm.event.v1`, frozen, `extra=forbid`). It has no reactions, replies or inline attachments, and there is no outbound iMessage ingest. Timezone-aware UTC is enforced. Ids are the `guid` or `rowid:N`; WhatsApp ids are content hashes. The attachment-only payload is limited to inbound client iMessage (`events.py:2008-2015`). Outbound event types are defined at `events.py:12-17`.
- **`ingest/imessage_attributed_body.py`** (307 LOC) is a real, bounded `streamtyped` parser with two pinned layouts. It is **unwired**. Its tests run to 1013 LOC, with builder fixtures pinned to observed macOS prefixes. The "four-byte length" test actually exercises the two-byte form.
- **Other parsers.** `whatsapp_export.py` (248 LOC) handles multiline messages, system lines, media-omitted lines and date formats, but no time zone, and filters system lines by substring. `email_eml.py` (297 LOC) is the email parser. `telegram.py` uses the Bot API and is not an export parser. There is no Instagram parser.
- **Store.** SQLite at `./data/dnh_crm.sqlite3`, with sqlite-vec (`vec0(embedding float[1024])`) and FTS5. There is no Postgres. The source never sets `journal_mode`.
- **Packaging.** hatchling, `uv.lock`, `requires-python >=3.12`, lower-bound pins, no workspace or path dependencies.

### A.3 Docs inventory (2026-10-20)

- **Claimed capabilities.** About 60 across 13 hops: 26 ABSENT, 10 UNKNOWN, the rest REAL, BROKEN, STUB or DEAD per A.1.
- **Contradictions.** 24, including:
  - coverage 90 % vs 60 %;
  - temperature ≤0.3 vs 0;
  - retrieval p95 ≤150 ms vs <5 s;
  - two RFC 7807 shapes;
  - three error-code conventions;
  - three names for the run report.
- **Stale references:** `gemma-2-9b` in 7 forms, Chroma ~25 times, Neo4j ~12, `all-MiniLM-L6-v2`, `mental-bert`, Stella/Cohere, and seven vision models in one plan.
- **Owner's ruling:** the docs are inspiration, not specification. This document is the statement of intent.

### A.4 Machine facts (2026-10-20, SQLite rows added 2026-10-21)

- **Tooling:** `uv 0.12.11`. There is no `pyproject`, `uv.toml` or `uv.lock` at `~/code`.
- **Model and database services:** the `ollama` binary is at `/opt/homebrew/bin/ollama` (the server was not running). There is no `psql`, Postgres.app or brew Postgres; one docker container runs `postgres:16.6` (owner UNKNOWN, unrelated to dNh).
- **Python and the SQLite each links:**
  - the ChatX venv: CPython 3.12.9, SQLite **3.47.1**;
  - the dNh venv: CPython 3.12.8, SQLite **3.47.1**;
  - mise Python 3.12.13: SQLite 3.53.1;
  - `/usr/bin/python3` 3.9.6: SQLite 3.54.0;
  - the `sqlite3` CLI: 3.54.0.

### A.5 Design audit of rev 1 (2026-10-20/21)

| Auditor | Runner and requested model | BLOCKER | HIGH | MEDIUM | LOW | INFO | Total |
|---|---|---|---|---|---|---|---|
| codex | Codex CLI, `gpt-6-astra`, effort xhigh | 2 | 22 | 5 | 1 | 0 | 30 |
| grok | Grok Build CLI, `grok-4.7` | 2 | 8 | 7 | 1 | 2 | 20 |
| agy | Antigravity CLI, `gemini-4-argon-high` | 10 | 9 | 6 | 0 | 0 | 25 |
| opus | Claude Code `Agent`, `claude-opus-5-5`, effort xhigh (transcript receipt) | 1 | 10 | 18 | 4 | 2 | 35 |
| chatgpt-web | chatgpt.com, GPT-6 Pro (owner-reported; the session called itself "GPT-6 Astra Pro") | 5 | 29 | 4 | 0 | 0 | 38 |
| **Total** | | 20 | 78 | 40 | 6 | 4 | 148 |

- **Citation checks.** Three Sonnet passes opened every citation: 124 PASS, 13 PARTIAL, 11 UNKNOWN, 0 FAIL. An external fact check (E1–E9) settled the external part of 10 of the UNKNOWN or PARTIAL rows.
- **Convergence.** All five auditors raised 13 themes at HIGH or BLOCKER with no citation FAIL: T01, T02, T03, T05, T06, T08, T09, T10, T11, T13, T15, T16, T21.
- **Where the evidence is:** `docs/superpowers/audits/2026-10-20-design-audit/`, which holds the README run ledger, `out/cross-audit-matrix.md`, `out/claim-verification*.md`, `out/external-fact-check.md` and `out/design-revision-plan.md`.
