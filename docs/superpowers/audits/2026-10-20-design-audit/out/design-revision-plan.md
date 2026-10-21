# Design revision plan — from the cross-audit matrix to design v2

Status: draft, supervisor-authored, 2026-10-20 20:25 local; opus fold-in 2026-10-21 01:49 PDT; chatgpt fold-in 2026-10-21 02:32 PDT; owner answers and external fact check folded in 2026-10-21 (sections *Owner decisions* and *External facts checked* near the end). **Applied to the design as revision 2 on 2026-10-21** (owner instruction "apply"): `docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md`, first applied as sha256 `b315277541bae28540611ae6193a92b653f7b0198df91224e8287ed5b101dcc1`. After the builder check (`builder-check-rev2.md`) was triaged into it, the current file is sha256 `96ef71cf674c5c5d51d4134dca2596dbb9e77831fec2027066fd5eb414703527`. Its §14 maps every theme and finding to the sections changed, and has one row for the builder check.
Inputs: `cross-audit-matrix.md` (23 themes, 148 findings from codex/grok/agy/opus/chatgpt-web), `claim-verification.md`, `claim-verification-opus.md`, `claim-verification-chatgpt.md`. Opus findings F-01–F-35 and chatgpt-web findings F01–F38 are folded in; every addition or change they caused is marked *(opus F-xx)* or *(chatgpt Fxx)*.
Target: `design/2026-10-20-chatx-rearchitecture-design.md` → revision 2 of the same file, with a change log that cites finding IDs per edit.

Legend: **(decided)** = designer's call, owner may override before approval · **(owner)** = needs the owner · **RT-n** = research target to carry into the consolidated research list · claims marked *verify* are the designer's belief, not checked evidence (none remain after the 2026-10-21 fact check) · **E-n** = row in `external-fact-check.md`.

---

## T01 Acquisition & WAL safety — codex F05, F28 · grok F5 · agy F-01 · opus F-09 · chatgpt F01, F37

Problem: the design keeps `imessage/db.py` and calls it "WAL-safe". The code copies `chat.db`, `-wal`, `-shm` sequentially with `shutil.copy2` (not a snapshot) and then opens the copy with `immutable=1`, which makes SQLite ignore the copied WAL — recent messages are silently dropped. The copy lives in a `TemporaryDirectory` under `/tmp`.

Change (decided), §3.13 and §4 `sources/imessage/`:
- Acquire with the **SQLite online backup API** (`sqlite3.Connection.backup`, stdlib) from a `mode=ro` connection on the live db into `cases/<case>/sources/<source-id>/chat.sqlite3`. The backup API produces a self-contained database (WAL contents included), so the snapshot is opened `mode=ro` without `immutable=1`.
- Run `PRAGMA quick_check` on the snapshot; record source file sizes, mtimes, sha256 of db/wal/shm as seen at acquisition, `sqlite3.sqlite_version`, and the quick_check result in `sources`. The snapshot **is** the evidence copy: content-addressed in the case manifest, never in `/tmp`, dir mode 0700.
- If the backup API cannot complete (locked db, Full Disk Access denied) → `E_DB_LOCKED` / `E_DB_ACCESS_DENIED`, non-zero exit, no fallback to raw file copy. Same path for iPhone backups: `Manifest.db` is acquired the same way.
- Keep `imessage/db.py` only as the *location* of this logic; its current body is replaced (update §8 keep-list wording).
- **SQLite floor** *(decided 2026-10-21; was RT-1)*: sqlite.org documents a WAL-reset bug that can corrupt a WAL database when two connections write or checkpoint at the same moment. It is present in 3.7.0 through 3.51.2 and fixed in 3.51.3 (2026-03-13), with backports in 3.44.6 and 3.50.7 (**E4**; the supervisor re-read sqlite.org/wal.html). The runtime must link SQLite ≥ 3.51.3, or a 3.50.x ≥ 3.50.7, or a 3.44.x ≥ 3.44.6. Every run records `sqlite3.sqlite_version`. On this Mac (2026-10-21) the ChatX and dNh venvs link 3.47.1, which is below the floor, and mise's Python 3.12.13 links 3.53.1. So the new repo's interpreter is chosen by the SQLite it links, and P0 checks it.
- *(opus F-09)* A fixture test writes rows into a WAL database without checkpointing, snapshots it through the backup API, and asserts the un-checkpointed rows are present. Whether the retired `immutable=1` copy loses them is opus's PLAUSIBLE claim; the test settles it, and the change does not depend on it.
- *(chatgpt F01)* Covered by the backup-API acquisition above. Added: the snapshot is checked with the full `PRAGMA integrity_check` instead of `quick_check`, and `sources` records the snapshot's row counts and `MAX(ROWID)` for `message`, `chat` and `attachment`, so a later re-acquisition can show what changed. The live db keeps changing while Messages runs, so the check is of the snapshot itself.
- *(chatgpt F37)* Same question as the SQLite floor above, now answered. Added: P0 records the SQLite library ChatX actually links (`sqlite3.sqlite_version`, not the Python version) on the owner's machine and in CI. The floor is written into §3.5 with T12's concurrency rules, and a runtime below it refuses to open a case (`E_SQLITE_TOO_OLD`).

## T02 Message identity & content hash — codex F02 · grok F13 · agy F-02, F-03 · opus F-01, F-13 · chatgpt F06, F08

Problem: derived `msg_id` = `sha256(platform, conv_id, sent_at, sender.handle, text)[:32]` collides when the same text is sent twice in the same minute (WhatsApp timestamps are minute-resolution). `content_hash` covers everything but `source_meta`/`provenance`, so `sender.pseudonym` (filled later), `reactions` (arrive later), and `attachments[].missing` all change the "content" hash. No canonical JSON form is defined.

Change (decided), §3.4:
- Canonical form: UTF-8, NFC-normalized strings, keys sorted, no insignificant whitespace, floats forbidden in hashed fields (RFC 8785 / JCS semantics; dNh's `canonical_json` helper is the reference implementation — **RT-2** confirm it matches JCS or adopt a JCS library).
- Derived `msg_id` adds an **occurrence index** *(changed per chatgpt F06; owner-approved 2026-10-21)*: `sha256(platform, conv_id, sent_at, sender.handle, text, occurrence)[:32]`, where `occurrence` counts earlier messages in the same source with the same `(platform, conv_id, sent_at, sender.handle, text)`, in source order (0 for the first). Identical messages in the same minute no longer collide, and re-importing the same file reproduces the same ids. The earlier draft hashed `source_id` and the row index, which broke the re-export contract below: a different file changes `source_id`, and one inserted line shifts every later row. The row index is kept as `provenance.source_row` (where a message was seen), not as identity.
- Two hashes: `content_hash` over the **immutable message core** — `platform, conv_id, msg_id, direction, sent_at, sender.handle, text, text_source, content_kind, reply_to_msg_id, thread_originator_id, sorted attachments[].sha256` — and `record_hash` over the full record. `sender.pseudonym`, `reactions`, `edit`, `attachments[].missing/storage_ref/source_path`, `source_meta`, `provenance` are **never** in `content_hash`.
- Reactions remain embedded in the canonical record for transport but are stored as their own rows (`reactions` table keyed by target `msg_id`), so a late-arriving reaction never rewrites a message row.
- *(opus F-01, F-13)* Covered by the two-hash split and the occurrence index above. Id stability is written into §3.4 as a contract: re-importing the same source reproduces every id, and a later, longer export of the same chat keeps the ids of the messages it shares with the earlier one, except where messages in the same minute were deleted between exports (documented limit; test: two overlapping WhatsApp exports). Opus's extra suggestion, a source-file fingerprint inside `msg_id`, is **not adopted** (decided): it would change every id on re-export and break that contract. dNh's side of F-01 is settled by owner item 5: dNh keeps its own dedupe formula (T05).
- *(chatgpt F06)* The design names five things v1 ran together: **message identity** (`msg_id`); **source observation** (new `message_observations(msg_id, source_id, source_row, record_hash)`, so one message seen in two overlapping exports is one message row with two observations); **revision** (`record_hash`); **content** (`content_hash`); **raw evidence integrity** (the acquired file's sha256 in `sources`, T01). When a later schema version changes an id formula, `msg_id_aliases(old_id, new_id, schema_version)` keeps old citations resolvable; ids are never rewritten in place.
- *(chatgpt F08)* Chunk ids: `chunk_id = sha256(chunker config hash, ordered (msg_id, record_hash) list)[:32]`, the same on every run and different when any member message changes. This replaces the kept chunker's run-dependent 8-hex-digit ids. The enricher receives structured `(msg_id, sender.pseudonym, text)` rows and never re-parses chunk text into messages, so a multi-line message stays one message and group-chat speakers stay distinct (T09 already moves chunk lines to per-sender pseudonyms).

## T03 Schema fidelity & forensic columns — codex F01 · grok F4, F20 · agy F-09 · opus F-16, F-33 · chatgpt F07

Problem: the design says `source_meta` is "never required"; the live `SELECT` reads 12 columns; replies are taken from `associated_message_guid` (that column is for reactions); `date_edited`, `date_retracted`, `balloon_bundle_id`, `item_type`, `group_action_type`, multi-chat membership and historical participant membership are not captured.

Change (decided), §3.4 and §4:
- Add a **column manifest** to the design (new table in §3.4): columns the iMessage reader must select when present — `message`: `ROWID, guid, text, attributedBody, handle_id, date, date_read, date_delivered, is_from_me, is_read, is_sent, is_delivered, is_audio_message, item_type, group_action_type, group_title, associated_message_guid, associated_message_type, associated_message_emoji, thread_originator_guid, thread_originator_part, reply_to_guid, balloon_bundle_id, date_edited, date_retracted, cache_has_attachments, error, service, account, destination_caller_id, expressive_send_style_id`; `chat`: `ROWID, guid, chat_identifier, display_name, service_name, group_id, style, is_archived`; joins `chat_message_join`, `chat_handle_join`, `message_attachment_join`; `attachment`: `ROWID, guid, filename, uti, mime_type, transfer_name, total_bytes, is_sticker, hide_attachment, created_date`; `handle`: `ROWID, id, service, country`.
- **Schema probe at open** (`PRAGMA table_info`): record which columns exist per source (macOS versions differ); absent columns → `None` + listed in `sources.schema_probe`. Never fail on an absent optional column; never silently skip a listed one.
- `source_meta` becomes **required for iMessage** and carries every selected column that has no canonical field, verbatim. The "escape hatch" wording goes; it is the forensic raw layer.
- Replies: `reply_to_msg_id` ← `thread_originator_guid` (+ `thread_originator_part`); `associated_message_guid` is reactions only (see T06).
- Edits/unsends: `edit.edited_at ← date_edited`, `edit.unsent ← date_retracted IS NOT NULL`; prior texts from the typedstream edit history when decodable, else `[]` with `source_meta.edit_history_undecoded = true`.
- Group events: `item_type != 0` → `content_kind = system`, new field `system_event{kind, group_action_type, group_title, affected_handles}`.
- Multi-chat: messages joined to >1 chat are emitted once with `conv_id` = the lowest `chat.ROWID` (deterministic) and `source_meta.chat_ids` = all; the store keeps a `message_conversations` join table; the import report counts multi-chat messages (agy F-20).
- Participants: `chat_handle_join` is snapshotted into `participants(conv_id, handle, observed_at_import)`; historical membership changes are **not** recoverable from `chat.db` — stated as a known limitation.
- *(opus F-16)* Covered by the column manifest and the `edit` mapping above. The plist keys inside `message_summary_info` per macOS version are opus research target R-03; the P1 probe reads them before the decoder is ported.
- *(opus F-33)* Enum values without an importer are removed (decided): `platform` loses `telegram` and `txt`, and `text_source` loses `ocr`. Each comes back with the phase that ships its importer. This removes the v1 pattern of claimed-but-absent capability.
- *(chatgpt F07)* Added to the column manifest: `payload_data` and `message_summary_info`. With `attributedBody` they are kept as raw blobs in `message_blobs(msg_id, column, sha256, bytes)`, so an app message or edit history that cannot be decoded today can be decoded later from the case without re-acquiring the source. A message with a `balloon_bundle_id` and no decoder gets a new `content_kind` value, `unsupported`, and is counted in the import report; the dNh adapter skips it with a count (T05). Unknown `item_type` / `group_action_type` values → `system_event.kind = unknown` with the raw codes kept. `participants` rows carry `membership = snapshot_at_import`; earlier membership is recorded as unknown, not as absent.

## T04 Time & timezone — codex F03 · grok F6 · chatgpt F02

Problem: §3.4 requires aware UTC unconditionally; dNh's WhatsApp parser does `replace(tzinfo=UTC)`; the old PDF reader uses `now()`; Apple-epoch heuristic bounds differ (1999 vs 2004 vs 2004–2100 in §7).

Change (decided), §3.4, §7, §10 V6:
- `sent_at` stays required and aware. New field `time_source` enum `platform_utc, assumed_tz, explicit_tz` and `source_tz` (IANA name or `None`).
- Sources without zone (WhatsApp exports, PDF transcripts) **require** `--assume-tz <IANA>` at import; without it the import refuses with `E_TZ_REQUIRED`. No default, no silent UTC.
- Unparseable timestamps → the row is **quarantined** with reason `unparseable_timestamp`; never `now()`, never inherited.
- One Apple-epoch converter in the core: epoch 2001-01-01; `0` means unset → `None`; ns/µs/s heuristic bounds **2001–2100**; property-tested; §7 text updated to match.
- *(chatgpt F02)* Every message also keeps `sent_at_raw` (the source value verbatim: Apple integer, export string, header) and `time_precision` (`ns`, `s`, `minute`, `day`). `--assume-tz` makes the zone an assumption on record (`time_source = assumed_tz`), not a fact, and reports say so. Messages with equal `sent_at` keep source order through `provenance.source_row` (T02). Quarantined rows keep `sent_at_raw`, so a later parser fix can re-import them.

## T05 dNh integration — codex F04 · grok F18 · agy F-05, F-06 · opus F-14, F-32 · chatgpt F03, F14

Problem: the §9 adapter crashes on platforms dNh's `Channel` enum lacks, on `reaction_only/empty/system` rows (`EventPayload.text min_length=1`), hardcodes `INBOUND`; replacing dNh's dedupe hash with `content_hash` would re-ingest every historical message; §4 says both "JSONL" and "no file hand-offs"; pin styles would collide.

Change (decided), §9 and §4:
- The adapter is **total**: every `(platform, direction, content_kind)` triple has a disposition — mapped, or skipped-with-count in the adapter report *(opus F-14)*. dNh's branch adds `Channel` members for `instagram` and `pdf_transcript` if it wants them; until then those platforms are skipped, not crashed. `reaction_only/empty/system` → skipped (recorded) in v1 of the adapter. `attachment_only` → `IMessageAttachmentOnlyPayload` for **inbound iMessage only**, because dNh limits that payload to inbound client iMessage events (`events.py:2008-2015`); other attachment-only messages are skipped-with-count. Empty `text` is never sent (dNh `EventPayload.text` has `min_length=1`).
- Direction *(changed per opus F-14)*: inbound → `MSG_INBOUND_RECEIVED`; outbound history → a dNh **outbound** event type, never `MSG_INBOUND_RECEIVED`. Owner item 8 (2026-10-21): imported history gets a **new dNh event type**, e.g. `msg.outbound.imported`, added to dNh's `EventType` (`events.py:12-17`) by a small dNh schema change. `msg.outbound.manual` is not reused, because dNh's opportunity, action, RAG and CRM-intel services consume it, and years of imported history must not look like fresh sends. Until that dNh change ships, outbound messages are skipped-with-count. The adapter never hardcodes a direction. §9's statement that dNh's event schema does not change is removed: either it changes or outbound is not emitted.
- **Dedupe compatibility (owner-visible)**: dNh keeps `build_imessage_dedupe` for iMessage rows; the core exposes the inputs it needs (`guid`, `rowid`) via `provenance.source_guid/source_row`. `content_hash` is stored **in addition** on dNh's side, not instead. No historical row changes its `dedupe_hash`. The owner confirmed this (item 5, 2026-10-21).
- §4 data flow: the core yields an iterator of canonical messages; `chatx case import` consumes it directly; JSONL is written only for `--emit-jsonl` and for dNh's adapter tests. The "no file hand-offs" sentence applies between chatx stages.
- Pins: the core has **no** `httpx` or other network dependency, so the `httpx` conflict cannot arise; the core pins `pydantic>=2.x,<3` and `phonenumbers>=8,<9` only; the app may use upper bounds freely because dNh does not install the app.
- *(opus F-32)* §9 gains the deletion step the "no second copy of any parser" anti-goal implies: once the adapter is live and the replay test passes, dNh removes its chat.db parsers (`ingest/imessage_source.py`, `ingest/imessage_mapper.py`). BlueBubbles live capture stays, because it is outside ChatX's scope. Cut-over (owner item 9, 2026-10-21): the adapter and dNh's parsers run side by side on real ingest for 30 days with their outputs compared, and dNh's parsers are deleted only if the two never disagree. A disagreement is fixed and restarts the 30 days *(decided)*.
- *(chatgpt F03)* Covered by the total adapter above. Added: the disposition list is a table in §9, one row per `(platform, direction, content_kind)` triple, and the adapter test builds every triple from the enums, so a new enum value (for example `unsupported`, T03) fails the test until it has a row.
- *(chatgpt F14)* Wiring the decoder does not fix history. Backfill is a separate one-time migration: the adapter replays the whole snapshot, not only dNh's bounded lookback window, and rows dNh already holds dedupe as before (`UNIQUE(dedupe_scope, dedupe_hash)`). Rows dNh stored with no text that now decode cannot be corrected by re-sending, because the dedupe key is unchanged and dNh's log is append-only; the owner chose to leave them and count them (item 12, 2026-10-21): the adapter reports how many stored events lack text that now decodes, and no correction event type is added. The P0.5 replay spike (T19 c) reports new, duplicate and would-correct counts before anything is sent.

## T06 iMessage decoding — codex F06 · grok F11 · agy F-07, F-10, F-20 · opus F-08, F-17, F-34 · chatgpt F09

Problem: reaction targets are looked up without stripping `p:<n>/` / `bp:` prefixes (0 % linkage on real dbs); 3000–3999 all map to "custom"; sticker type 1000 absent; dNh's typedstream parser accepts two pinned layouts; a decoded body consisting only of U+FFFC is treated as text; multi-chat ambiguity hidden by `MIN(chat_id)`.

Change (decided), §3.4, §4, §10 V1/V2:
- Reaction parsing: strip `p:<part>/` and `bp:` from `associated_message_guid`; keep `Reaction.target_part`. Codes 2000–2005 add / 3000–3005 remove by kind; 2006/3006 → `kind=emoji` with `emoji ← associated_message_emoji` (V1 still verifies on a real db); 1000 → sticker attachment, not a reaction; any other code → `kind=unknown` with the raw code in `source_meta`. Never "custom" by range.
- Typedstream: dNh's parser is the first decoder; the core adds a **generic typedstream walker** as the second strategy (**RT-3**: NSAttributedString typedstream grammar / existing open-source decoders to evaluate); only then `text_source=none` with a report line. Decoded text that is empty after removing U+FFFC and whitespace → `text=None`, `content_kind=attachment_only` (or `empty` if no attachment).
- `chatx import imessage --probe` ships in P1: layout coverage, `unsupported/malformed` counts, multi-chat counts, reaction linkage rate — the V2 measurement, run on the owner's real db before the schema is frozen (see T19).
- *(opus F-08, F-17)* Covered above (reaction prefixes and codes, the `unknown` kind, no `now()`) and in T03 (replies from `thread_originator_guid`). Added: a property test that any interleaving of add and remove events for one target folds to the same final state and history (T21).
- *(opus F-34)* The adopted dNh decoder keeps its bounds (`MAX_INPUT_BYTES = 256 * 1024`, `MAX_OUTPUT_BYTES = 64 * 1024`) and its fail-closed statuses. The status is stored with the message as `text_source` evidence, not discarded.
- *(chatgpt F09)* §3.4 and §10 state the decoding guarantee as partial: text is decoded where a strategy succeeds; otherwise the blob is kept (`message_blobs`, T03) with its status. Recovery is measured on the owner's real blobs by the P0.5 probe, not claimed from fixtures. dNh's `test_decodes_four_byte_little_endian_length` encodes its `0x8000` length in the 2-byte `0x81` form (`dnh:tests/unit/test_imessage_attributed_body.py:140-144`); the ported test is fixed to exercise the 4-byte form.

## T07 Attachments & path containment — codex F07 · agy F-08, F-23 · chatgpt F10, F11

Problem: no `expanduser()` on `~/Library/Messages/Attachments/...` (every live lookup fails); backup context dropped at the caller; no containment check; copy goes straight to the final path.

Change (decided), §4 `sources/imessage/`, §3.5:
- Resolve: `expanduser()` → `resolve()` → **containment check** against the allowed roots (`~/Library/Messages/Attachments`, the backup dir, or `--attachments-root`); outside → `missing=true, missing_reason=outside_root`. Reasons enum: `not_found, outside_root, unreadable, hidden, not_in_backup`.
- Backup mode passes `backup_dir` through the whole call chain (the parameter exists; the caller drops it).
- CAS write: stream to `attachments/.tmp/<uuid>` while hashing, `fsync`, atomic rename to `<aa>/<sha256>`; verify the hash after rename (T14).
- Bytes are stored **exactly**; EXIF is never stripped from the stored object. Thumbnails/derivatives are never exported.
- `--backup-password` removal stands (the PARTIAL note on agy F-23 does not change the decision).
- *(chatgpt F10)* One `AcquisitionContext` (source id, live or backup, roots, `backup_dir`, `Manifest.db` snapshot, contact scope) is resolved once at import start, stored in `sources`, and passed to extraction, attachment resolution and the missing-attachments report, so they cannot disagree. A contact-scoped import selects the chats whose participants include the contact (group chats included and flagged), then every message in those chats in both directions. The v1 filter `OR m.is_from_me = 1`, which pulled the owner's messages from every chat, is removed.
- *(chatgpt F11)* Added to the CAS write: source paths pass the containment check before they are opened; when `<aa>/<sha256>` already exists its bytes are re-hashed before the new temp file is discarded, and a mismatch replaces the stored object and is logged as corruption. A crash leaves only files in `attachments/.tmp/`, which `case verify` reports and the next run sweeps.

## T08 Other importers — codex F08 · grok F12 · agy F-04, F-11, F-19 · opus F-07, F-15, F-31 · chatgpt F12, F13

Problem: dNh's WhatsApp parser drops any message containing "added"/"left"/"joined" and does not parse iOS bracketed exports; PDF rows get `platform=imessage` and `now()` timestamps; email drops To/Cc/In-Reply-To/References and hardcodes INBOUND; phone normalization is hand-rolled; §4/§8 imply Instagram mojibake repair already exists.

Change (decided), §4 `sources/*`, §8:
- WhatsApp: support Android (`DD/MM/YYYY, HH:MM - Name: text`) and iOS bracketed (`[DD/MM/YYYY, HH:MM:SS] Name: text`) forms; `--date-order dmy|mdy` explicit; system lines detected **structurally** (no `Name:` prefix), never by substring; `<Media omitted>`, `This message was deleted`, `‎image omitted` → `content_kind` `attachment_only`/`system` with `source_meta.wa_marker`. Golden exports for both OS forms and ≥2 locales.
- Instagram: mojibake repair (latin-1 → UTF-8 re-decode, the documented Instagram export quirk) is **P1 work**, named as such in §8 ("port with rework"), with limits: max uncompressed bytes, max entries, compression-ratio bound.
- PDF: `platform=pdf_transcript`; timestamps only from parsed lines; lines with no timestamp → quarantined (T04); direction from `--me <name>`.
- Email: capture `Message-ID, In-Reply-To, References, From, To, Cc, Bcc, Date`; `reply_to_msg_id ← In-Reply-To`; `conv_id` from the `References` chain root; direction from `--me <address>...`.
- Handles: `phonenumbers` with `--default-region`; E.164 output; unparseable → raw handle + `handle_kind=raw`.
- *(opus F-07, F-15)* Covered above (structural system-line detection, both OS forms, explicit date order, golden exports; Instagram latin-1 re-decode). Added: the re-decode runs only when it round-trips cleanly, and the golden fixture includes emoji and accented names, because mojibake names evade the PERSON recognizer (T09).
- *(opus F-31)* `.eml`: a missing or `-0000` zone gives `source_tz=None` and the T04 unknown-zone rule, never silent UTC. Ids come from the normalised `Message-ID` header, falling back to a hash of normalised headers plus body, so the same mail saved twice dedupes (dNh `email_eml.py:107-115, 203-213` uses the file hash today).
- *(chatgpt F12)* Covered by structural system-line detection above. Added: every input line or record ends in exactly one disposition (message, continuation of the previous message, system event, quarantined with reason), and the import report sums to the input count (T22).
- *(chatgpt F13)* Each importer gets a fidelity table in §4: what it reads, what it keeps raw in `source_meta`, and what it cannot recover. Every message carries a source locator in `provenance` (line number for WhatsApp, JSON pointer for Instagram, `Message-ID` plus file for email, page and line for PDF), and the original export file is acquired into the case with its sha256, like `chat.db` (T01).

## T09 Policy Shield — codex F09 · grok F1, F8 · agy F-13, F-14, F-16 · opus F-04, F-05, F-23 · chatgpt F05, F15, F16

Problem: entity recall is presented as de-identification; quasi-identifiers are unnamed; the synthetic set qualifies the cloud gate; the second-opinion "sample" has no size; hard-fail is a naïve regex list that collides with the taxonomy; chunk lines carry the raw `contact` handle before redaction.

Change (decided), §3.7, §3.8, §12.3:
- **What the gate claims**: per-class recall on named classes, including quasi-identifier classes (`location, date_of_birth, employer, school, relationship_descriptor, unique_event, financial_account, health_condition`). Every report states: "recall measured on classes {…}; de-identification is not claimed."
- **Eligibility**: synthetic results qualify CI only. The cloud gate requires a passing **real-sample** evaluation (owner-labelled, git-ignored). The owner will label a full real sample (§12.3, answered 2026-10-21: about 600 examples per entity class present). Until it passes, the cloud tier is unavailable, and the design says this plainly.
- **Statistics**: per class, the Clopper-Pearson 95 % lower bound on recall must meet the target. With zero misses that needs ≈600 labelled positives per class for 0.995 (≈3000 for 0.999). Classes below the support floor → `INSUFFICIENT_SUPPORT`, which blocks the cloud tier.
- **Second opinion**: sample size from the rule of three, `n ≥ 3/ε` for residual leak rate ε (config, default 0.005 → n ≥ 600 chunks, or every chunk if fewer); zero confirmed leaks required.
- **Hard-fail = taxonomy, not regex**: the `HardFailDetector` regexes are retired. A chunk is `cloud_eligible=false` if the local classifier assigns any label in the local-only tier (T16). It is not dropped; it is enriched locally only.
- **Chunk construction**: identity runs before chunking (already in the flow) and chunk lines use `sender.pseudonym` only; `meta.contact` is a pseudonym; the ±2-turn context comes from the redacted store; the cloud request model has a `redacted_text` field and nothing else textual (type-level, as for attachments).
- *(opus F-04)* Covered by the statistics bullet above. Made explicit: the class set is fixed by the taxonomy before evaluation, not by what the detector finds in the case, so a class the detector never fires on still needs labelled support or reads `INSUFFICIENT_SUPPORT`.
- *(opus F-05)* The cloud gate checks content sensitivity as well as identifiers: special-category coarse labels (sexual, substance, health, orientation) become local-only (T16), and a chunk carrying one is `cloud_eligible=false` whatever its PII recall.
- *(opus F-23)* The hard-fail classes are listed in `config/labels.yml` with written definitions the owner approves. Policy chosen 2026-10-21 (owner item 10): **special categories stay local**. Every fine label is local-only. Coarse labels about sexuality, health, substances, crime or violence, and anything involving minors are `cloud_allowed: false`. Content involving minors is flagged locally and excluded from every export, including `--include-analysis` bundles. The wording of each definition is written in P3 and returns to the owner for approval. A hit excludes the chunk (as above), is logged locally by id only, and never appears in exports or cloud requests.
- *(chatgpt F05)* Covered by the eligibility and statistics bullets above. Added: required classes come from the taxonomy (opus F-04), and required **languages** are declared per case by the owner. Recall is reported per class and language; a chunk whose detected language is not declared is `cloud_eligible=false` (local language identification, **RT-16**). A missing real-sample evaluation keeps the cloud tier off; P3 can exit on synthetic results for the local pipeline only (T19).
- *(chatgpt F15)* The shield fails closed per run. An exception or an unclassifiable chunk inside the shield makes that chunk `cloud_eligible=false` and sets the run's `shield_status = degraded`; a degraded run cannot get a gate token (T10), so its cloud stage stops while the local pipeline continues (see *Not changed on purpose*). The chunk id and exception class are kept locally. v1 did the opposite: `redact_chunks` caught the exception and dropped the chunk, and the hard-fail flag was set only when blocking was off.
- *(chatgpt F16)* The second-opinion bullet gains its estimand: the residual leak rate per chunk among chunks the primary shield passed. Chunks are drawn by simple random sampling without replacement, seed recorded. The second-opinion model's own recall is measured on the labelled set first and must meet the same class floors; if it does not, its zero-leak result is not evidence and the class reads `INSUFFICIENT_SUPPORT`.

## T10 Cloud egress gate & bypass — codex F10 · grok F7 · agy F-15 · opus F-03, F-06 · chatgpt F04

Problem: the gate token is checked at provider construction, not per request; a "local" provider is whatever `base_url` says; the P7 MCP host may itself be a cloud client; the whole taxonomy (99 local-only fine labels) is compiled into the enum sent to the cloud.

Change (decided), §3.6, §3.7, §3.12, §5.4:
- **Per-request binding**: `GateToken(case_id, run_id, payload_hash, shield_version, issued_at, ttl)`; `CloudProvider.complete_structured` requires a token whose `payload_hash` equals the hash of the exact request body; mismatch or expiry → `E_GATE_MISMATCH`. Test: a forged/foreign token cannot send.
- **Locality is computed, not declared** *(changed per opus F-03)*: a provider is `local` only if its host resolves to loopback or it is a Unix socket. A LAN address (RFC 1918/ULA) is another machine, so it counts as `cloud` unless the owner lists that host in `[providers.local].allow_lan_hosts`; the run records the resolved address and the rule that admitted it. `chatx providers check` prints the classification; `[providers.local]` pointing at any other host is `E_PROVIDER_NOT_LOCAL`.
- **MCP boundary**: `chatx mcp serve` returns redacted/pseudonymized views only; raw text requires `--expose-raw` with a printed warning; the design states that the MCP host is a cloud boundary.
- **Two compiled enums**: `CoarseCloudLabels` (labels with `cloud_allowed: true`, T16) and `FineLocalLabels`; the cloud request/response models are typed with the cloud enum only. `fine_cloud_allowed: false` in `labels.yml` is honoured by construction.
- *(opus F-06)* Covered by the MCP-boundary bullet above (redacted views only). Added: `--expose-raw` counts as cloud egress of raw text, because the MCP client's model is usually cloud-hosted. It needs a per-session confirmation and is recorded as such in `runs`.
- *(owner item 11b, 2026-10-21)* Cloud processing of other people's messages is allowed only for redacted chunks, only after the real-sample gate passes (T09), and only under vendor terms with zero data retention and no training. `[providers.cloud]` must declare `zero_data_retention = true` and `training = false`. These are the owner's statement of the account terms, which the tool cannot check, and each run records them. Without both, no gate token is issued (`E_VENDOR_TERMS`, *decided*).
- *(chatgpt F04)* The token also binds `operation` (enrich or second opinion) and `destination` (resolved host and model id). The hash is taken over the serialized bytes at the transport layer, after the SDK has built the request (a custom HTTP-client hook, **RT-17**), and is re-checked on every retry, so any later change to the request fails closed with `E_GATE_MISMATCH`. Local trust is the computed locality rule above. sonnet-verify marked this finding PARTIAL (the cited code does not show the gap); the design gap stands either way.

## T11 Pseudonym tokens, salt & map custody — codex F11 · grok F3 · agy F-12 · opus F-12 · chatgpt F17

Problem: `⟦TKN:<id8>⟧` vs "128-bit"; salt file written without `chmod`, global rather than per case; the reversible map sits in the same DB as raw messages; export does not say what it omits.

Change (decided), §3.7, §3.10:
- Tokens *(changed per opus F-12)*: typed per-case sequential surrogates such as `⟦PERSON_0007⟧` and `⟦PHONE_0003⟧`, allocated in first-seen order in the pseudonym map (single writer under the case lock, T12). Redacted text carries no hash material, collisions cannot happen, and the type helps the model during enrichment. HMAC-128 stays only for `sender.pseudonym` handle ids. The round-trip test covers allocation, reuse and re-hydration.
- Salt: **per case**, `cases/<case>/secrets/salt` created with `O_CREAT|O_EXCL`, mode 0600, dir 0700; no global salt; `chatx identity rotate` re-derives and invalidates cloud-derived caches (documented).
- Map custody: the reversible map lives in `cases/<case>/secrets/pseudonyms.sqlite3`, not in `case.sqlite3`. **Export bundles never include `secrets/`**; `--include-pseudonym-map` is an explicit flag with a warning. The threat the separation addresses is bundle hand-off, not a local root attacker (T20 says so). The owner confirmed this layout (item 6, 2026-10-21).
- *(chatgpt F17)* The token grammar is written into §3.7 as an exact pattern, `⟦[A-Z_]+_[0-9]{4,}⟧`, and `⟦`/`⟧` in source text are escaped at import, so message content cannot forge a surrogate. Re-hydration is local only, takes the case lock, and is recorded in `runs`; a surrogate in model output that is not in the map is left as is and flagged, never resolved. The HMAC key for `sender.pseudonym` is the per-case salt, so creation, rotation and loss are documented once for both.

## T12 Storage invariants — codex F12 · agy F-21 · chatgpt F24

Change (decided), §3.5:
- Single writer: `cases/<case>/.lock` (exclusive `flock`); a second `chatx` on the same case → `E_CASE_LOCKED`.
- PRAGMAs: `journal_mode=WAL`, `synchronous=NORMAL` (`FULL` for the import commit), `foreign_keys=ON`, `busy_timeout=5000`.
- Every stage opens a `runs` row first and closes it last; batches are transactions; a crashed run leaves `status=running`, which `case verify` reports and `case resume` picks up from the run's watermark (`last_source_row`).
- FK policy: `messages → reactions/message_attachments/chunks/enrichments` `ON DELETE CASCADE`; `sources → messages` `RESTRICT` (a source is removed only through `case delete-source`, which is explicit).
- `schema_migrations(version, applied_at, checksum)`, forward-only SQL files; `case verify` compares applied checksums with shipped files.
- *(chatgpt F24)* Invariants `case verify` checks: every message has at least one observation (T02); every chunk's `msg_ids` exist with a matching `record_hash`; FTS row count equals message count; each embedding space has one vector per chunk (T13). A source stays `status=partial` until its last import batch commits, then becomes `complete`. Messages, sources and attachments are the evidence; chunks, FTS, embeddings and enrichments are derived and disposable, and `case repair` rebuilds them from the evidence tables. `chatx case backup` uses the SQLite backup API (T01).

## T13 Scale & vector index — codex F13 · grok F9 · agy F-17 · opus F-19 · chatgpt F25

Problem: sqlite-vec `vec0` is a brute-force scan; 1M × float32[1024] ≈ 4 GB per query; the P2 exit measures 100k messages, not millions of chunks; G3 says "single-file" while attachments are a directory.

Change (decided), §2 G3, §3.10, §6 P5, §10 V4:
- G3 reads "single-directory case (one SQLite file + content-addressed attachments)".
- Default query plan is **filter-then-KNN**: FTS5/metadata/time-window candidates first, vector scoring over the candidate set only; a full-table KNN is an explicit `--exhaustive` option.
- Embedding default: a small-dimension local model (≤768) and `vec0` `int8` quantization where the model tolerates it (**RT-4**: sqlite-vec quantized types and the current scan cost; **RT-5**: local embedding model shortlist by dimension/quality).
- P5 exit measures retrieval at **1M synthetic chunks**, not 100k, and records it; if the tracked target fails twice the ADR candidates are a file-based ANN index beside the DB (usearch/hnswlib) — listed, not chosen.
- *(opus F-19)* sqlite-vec is pre-v1 (**E9**: latest release v0.1.9, 2026-03-31; `vec0` KNN is an exact scan, and the ANN index proposed in issue #25 has not shipped): pin the exact version, record it and the `vec0` table definition in `schema_migrations`, and fail loudly if the extension is missing. There is no silent FTS-only fallback; `--no-vector` is the explicit way to run without it. Quantized vectors are rescored with float vectors for the final top-k. Opus's size figure (1M chunks × 1024 float32 ≈ 4.1 GB) is why the default is a ≤768-dimension model with int8 storage.
- *(chatgpt F25)* Each embedding space (`model, revision, dimension, quantization, distance`) is a row in `embedding_spaces` with its own `vec0` table. Changing the model creates a new space and re-embeds; vectors from two spaces are never mixed, and an old space is dropped only explicitly. dNh's fixed `float[1024]` table belongs to dNh and is not shared, because ChatX does not write dNh's vectors. Capacity is the P5 1M-chunk measurement above.

## T14 CAS, export & manifest custody — codex F14 (+ grok F9, F10 points) · opus F-20 · chatgpt F26

Change (decided), §3.5, §3.10:
- CAS writes are temp-file + `fsync` + atomic rename + post-write hash verification (T07).
- `manifest.json` lists every file with sha256, size, tool version, schema version; the bundle carries `MANIFEST.sha256` and an optional detached signature via `--sign` (**RT-6**: signing tool — minisign / `ssh-keygen -Y sign` / age — and verification UX).
- `custody.json` in every bundle: OS user, host, start/end timestamps, run ids, source hashes.
- *(opus F-20)* `custody.json` also records the source device and OS version, the tool version and git commit, and the operator. An RFC 3161 timestamp is optional and owner-chosen, because it sends the manifest hash to a timestamp authority (a hash only, but still network egress).
- *(chatgpt F26)* The forensic claim is narrowed in §2 and §3.10: a verified bundle shows its files are the ones the tool wrote at export, if the manifest hash or signature is trusted. It does not show the source was complete or the device data authentic. The bundle includes the `sources` rows (hashes at acquisition, T01) as acquisition history, and `chatx case import-bundle` verifies the manifest before opening anything. Docs use "forensic" only with this qualification. Intended use (owner item 11a, 2026-10-21): bundles are for the owner's own records.

## T15 Provider protocol & operation — codex F15, F16 · grok F2 · agy F-22 · opus F-02, F-27, F-28 · chatgpt F19, F20, F21

Problem: one protocol with `embed()` and a shared `temperature/seed` cannot be honoured by both Anthropic (no embedding model and no `seed` parameter, confirmed 2026-10-21 by **E1** and **E2a**) and an OpenAI-compatible server; no timeouts, retry budget, usage, cost cap, prompt caching, batch mode, or injection handling.

Change (decided), §3.6, §3.9:
- Split the protocol: `ChatProvider.complete_structured(...)` and `EmbeddingProvider.embed(...)`. `AnthropicProvider` implements chat only.
- **Embeddings are local-only by design** (embedding raw text in the cloud is egress). Cloud embedding is added to the anti-goals.
- Sampling parameters are **capability-gated per provider and model**, not universal *(changed per opus F-02)*: a provider sends `temperature`, `seed` or `top_p` only where its capability record says the model accepts them. Confirmed 2026-10-21 from the Sonnet 5.5 and Opus 5.5 migration guides (**E2b**, **E2c**; the supervisor re-read both pages). Both models return HTTP 400 for a non-default `temperature`, `top_p` or `top_k`; the Python SDK v1.0+ no longer defines these and raises `TypeError` if they are passed. Both also return 400 for `tool_choice` of type `any` or `tool`, with or without thinking. So the Anthropic provider sends no sampling parameters. It gets structured output from `output_config.format` or a `strict: true` tool with `tool_choice: auto`, and the prompt says when to answer. `runs` stores what was actually sent, with `None` for anything omitted.
- **Thinking and output budget** *(decided from **E2d**)*: thinking is on by default on both models and counts toward `max_tokens`, which caps thinking and answer together. Opus 5.5 cannot turn thinking off (`disabled` returns 400). Sonnet 5.5 turns off up-front thinking with `thinking: {"type": "between_tools"}`, which is accepted only at `low`, `medium` and `high` effort. The design's `max_output_tokens = 800` (§3.6 config line 174, and line 211) is removed. The provider sets `effort` and a `max_tokens` sized for thinking plus the enrichment answer, and a `max_tokens` stop is the `truncated` outcome (chatgpt F19), never a parse error.
- Operation contract: connect/read timeouts; retries with exponential backoff on 429/5xx/timeouts under a per-run retry budget; `usage` tokens per call; `--max-cost-usd` with a price table in config (never in code); Anthropic prompt caching on the static prefix (system + taxonomy); optional batch mode (`--batch`) for cloud enrichment; observed model from the response's `model` field.
- Prompt-injection posture: chunk text is data, delimited and labelled as such in the prompt; outputs are schema-validated; the model has no tools during enrichment.
- *(opus F-27)* `chatx providers check` probes each endpoint's structured-output mode (`json_schema`, `grammar` or `none`) and records it in `ProviderIdentity`. Every provider validates output against the schema and retries within the budget; there is no silent fallback to unconstrained JSON. Reports never claim bit-reproducibility: the cache (T16) is the reproducibility mechanism, and a seed is only a hint. **E3** (2026-10-21): vLLM, Ollama, the llama.cpp server and LM Studio all offer schema-constrained output, each with a different request shape. vLLM documents no reproducibility by default, and only on the same hardware and version. Ollama's docs only say temperature 0 gives more consistent results. **RT-12** narrows to probing the server the owner chooses.
- *(opus F-28)* Covered by the protocol split above (`AnthropicProvider` implements `ChatProvider` only; embeddings are local by design). Added: a remote embedder would be a cloud path through the same gate, and none is built in v2.
- *(chatgpt F19)* `complete_structured` returns a typed outcome: `ok`, `refused` (with the stop reason), `truncated` (output limit hit), `invalid` (schema errors after the retry budget) or `unavailable`. Each is stored per item in `enrichments` with no labels and counted in the run report; a refusal is never retried as if it were bad JSON. An unavailable `EmbeddingProvider` fails the index stage with an error code; there is no fallback model.
- *(chatgpt F20)* Added to the operation contract: a per-run deadline (`--deadline`), bounded concurrency (config), and cost checked before each send (estimated input tokens × price) as well as after (reported usage). Ctrl-C finishes in-flight items, records the watermark, and leaves the run resumable (`case resume`, T12).
- *(chatgpt F21)* Each call stores `call_config_hash`, a hash of exactly what was sent (model id, sampling parameters actually sent, output limit, structured-output mode, system-prompt hash, taxonomy hash, preprocessing version), plus the model id from the response. The T16 cache key includes `call_config_hash`.

## T16 Taxonomy, labels, enrichment & psychology validity — codex F17, F18, F20 · grok F14, F19 · agy F-18 · opus F-18, F-25 · chatgpt F18, F22, F28

Problem: "coarse" is treated as cloud-safe but contains substance/kink/orientation labels; "hysteresis" is a stateless three-band split; the cache key omits recognizer/taxonomy/prompt hashes; the psychology mapper's 123 `source_labels` have **0** matches in `labels.yml` (verified by script); pattern rules assert no validity or direction.

Change (decided), §3.9, §3.11, §8:
- `labels.yml` → schema 1.3 with an explicit per-label `cloud_allowed: bool`, default `false`; substances, sexuality/orientation, health, legal exposure are `false` whatever their tier. Owner item 10 (2026-10-21) adds crime or violence and anything involving minors (T09). `CoarseCloudLabels` is compiled from `cloud_allowed: true` only (T10).
- Hysteresis is **stateful** per `(conv_id, label)` in time order: enter at `τ_high`, exit below `τ_low`, hold between; state stored with the enrichment.
- Cache key: `(provider identity, model, prompt template hash, taxonomy version, schema version, shield version, recognizer config hash, input content hash, context hash)`.
- The old mapper's rules are ported as **documentation** (`docs/analysis/legacy-patterns.md`), not as data: a new construct map from the current taxonomy is built in P6 with its own eval, ADR and basis citations; outputs are "indicators with supporting message citations", carry the "not a clinical assessment" disclaimer, and claim no direction or cause.
- An owner-labelled **enrichment gold set** is a prerequisite for tuning any threshold (§12 item 4; the owner agreed to label it, 2026-10-21).
- *(opus F-18)* `confidence_llm` is self-reported and is never read as a probability. Thresholds are tuned on the enrichment gold set (owner item 4) with a reliability curve; until that set exists every label carries `calibrated: false` and the cloud tier stays off. **RT-13**.
- *(opus F-25)* No analysis-lane label name asserts intent or a diagnosis. Names describe observable text patterns; `GASLIGHTS`, `MANIPULATES`, `CODEPENDS_ON` and `AROUSAL_MANIPULATION` are renamed in P6. Each analysis label needs inter-rater agreement between two human raters on the gold set before it ships. Its records are typed `model_inference` with provenance and are exported only with `--include-analysis` (T19). **RT-15**.
- *(chatgpt F18)* Covered by `cloud_allowed` defaulting to `false` and the special-category rule (opus F-05). Added: the owner approves `cloud_allowed` label by label; the policy is set by owner item 10 (special categories stay local, T09). Cloud requests carry an opaque request id instead of `msg_id`/`conv_id`, and chunk lines use times relative to the chunk start instead of calendar dates, so a request is harder to link back to a person; the mapping stays local.
- *(chatgpt F22)* The v1 loader reads `data.get('categories', {})` while `labels.yml` has top-level `coarse` and `fine_local`, so it loads no labels (sonnet-verify PASS). It is replaced by a compiler that validates `labels.yml` 1.3 against a JSON Schema, with a test that every YAML label appears in the compiled enums. The enrichment schema allows `none_apply` and per-label abstention. Hysteresis and calibration are covered above.
- *(chatgpt F28)* Covered by opus F-25 and the mapper-as-documentation change. Added: every analysis indicator names the actor (pseudonym), cites the messages that support it, records the counter-evidence searched for (messages in the same window that do not fit), and may abstain. A review state (`unreviewed`, `accepted`, `rejected`) is stored and exported with the indicator.

## T17 Retrieval & citations — codex F19 · grok F15 · chatgpt F27

Change (decided), §3.10:
- RRF with explicit `k` (default 60) and per-retriever depth `N` (config); fusion happens at **message** level: chunk hits expand to their `msg_ids`, duplicates across stride overlap collapse; citations are `(msg_id, conv_id, sent_at, span)`; chunks store `msg_ids`, not a count.
- Derivative invalidation: chunks, embeddings and enrichments carry the `content_hash` of their inputs; `case verify` flags stale derivatives; a changed source invalidates by hash.
- *(chatgpt F27)* `span` is defined as character offsets into the message's stored `text` at a stated `record_hash`; a citation whose `record_hash` no longer matches is reported stale. Filters (time, contact, label) apply to every retriever before fusion. P5 adds a local retrieval gold set (owner-written queries with relevant `msg_id`s) and measures recall@k. A cited answer passes only if each cited span supports its claim, checked by a local judge model and spot-checked by the owner (**RT-18**).

## T18 Packaging & uv workspace — codex F21, F22 · grok F16 · opus F-10 · chatgpt F29, F30, F36

Change (decided), §3.2, §3.3:
- dNh consumes a **built wheel pinned by version and hash** (from a git tag / local index), not an editable path dependency; the editable path dep is for a dNh development branch only. "dNh pins the version" now means bytes, not a string.
- Package data via `importlib.resources`; no `Path(__file__).parents[n]`. The core's dependency set is listed in the design (pydantic, phonenumbers) and a test asserts its import graph contains no network/LLM/storage modules.
- **uv syntax** *(answered 2026-10-21 by **E8**; was RT-8)*: from outside the core's workspace, dNh's development branch can use `{ path = "<core dir>", editable = true }`, a plain path dependency that does not apply the other workspace's lock or sources, or `{ workspace = "<workspace root>" }`, which resolves the member by name. Release builds use the pinned wheel above. P0 proves both from clean clones.
- *(opus F-10)* Covered by the built-wheel bullet above: dNh CI installs a pinned version, never the editable path.
- *(chatgpt F29)* Release contract: core releases are git tags `core-vX.Y.Z` with a wheel and its sha256 built in CI from a clean tree; dNh's lock records that hash. Before tagging, the core's CI runs dNh's adapter tests against the new wheel.
- *(chatgpt F30)* A missing schema resource is an error (`E_SCHEMA_MISSING`), never a skip; v1's validator returns `True` when the schema file is absent. CI installs the built wheel into a fresh venv outside the checkout and runs the CLI smoke tests there.
- *(chatgpt F36)* Model artifacts are pinned by repository, revision and file sha256, alongside the dependency hashes; third-party notices ship with both packages. Licence and ownership (owner item 13, 2026-10-21): the core is MIT-licensed, like ChatX, and owned by the owner (DDD-Enterprises). Proprietary dNh may depend on it.

## T19 Phase sequencing — codex F23 · grok F10 · opus F-24 · chatgpt F32

Change (decided), §6:
- Provider protocol + `OpenAICompatProvider` move to **P3** (the shield's second opinion and local-only classification need a local model); `AnthropicProvider` + enrichment stay P4. Chunking is assigned to P2 explicitly.
- P3's synthetic target gates **the cloud tier**, not the program: a miss leaves the local pipeline fully usable and the cloud tier disabled with a stated reason.
- Schema v2 is `chat.message.v2-draft` until the P1 real-db probe (T06) has run; freezing happens after the probe, not before.
- Analysis-lane outputs live in `analysis_*` tables with a disclaimer column and are exported only with `--include-analysis`.
- Encrypted backups (P6) gain **RT-9**: iOS backup keybag/AES-256 decryption libraries and their maintenance status.
- *(opus F-24)* **P0.5 spikes** (decided) run before the P1 build, each with an exit number: (a) typedstream decode coverage on the owner's real `chat.db` through the structure-only probe; (b) Presidio and GLiNER recall on about 300 owner-labelled messages; (c) a dNh dedupe-continuity replay on a copy of dNh's db. A spike result can reorder or cut later phases; spikes ship no code. Spike (b) uses the first ~300 messages of the owner's labelled real sample (owner item 3, answered yes).
- *(chatgpt F32)* Each phase's exit is rewritten so that phase's own outputs can satisfy it; an exit that needs a later phase's component moves to that phase. P0.5 gains two spikes: (d) structured output from the chosen local model at the target throughput, which feeds P3; (e) `vec0` scan timing at 100k and 1M synthetic chunks, which feeds the T13 ADR before P5 is planned in detail.

## T20 Threat model & local exposure — codex F24 (+ grok F5, agy threat-table A2) · opus F-11, F-26 · chatgpt F23, F31

Change (decided), new §3.15:
- Assets: raw messages, attachments, pseudonym map + salt, cloud key, exports. Adversaries: another local user/process, a lost laptop, a malicious export/ZIP/PDF, a malicious or cloud-backed MCP client, prompt injection via message content, a misconfigured provider URL.
- Controls: case dir 0700 / files 0600; nothing under `/tmp`; FileVault required at case creation (checked with `fdesetup status`; owner item 7) unless `--allow-unencrypted-disk` is passed, which the case records; input limits (ZIP bytes/entries/ratio, PDF pages, db size); parameterized SQL only; no `pickle`/`eval`; schema-validated model outputs; MCP returns redacted only; computed provider locality; logs carry ids and hashes, never text.
- Out of scope: root on the machine, memory forensics, a compromised OS.
- *(opus F-11)* Local-exposure controls added. The default case root is `~/Library/Application Support/chatx/cases.noindex/` (0700; the `.noindex` suffix keeps Spotlight out). Roots inside iCloud-synced folders (Desktop & Documents, iCloud Drive) are refused. Case creation offers a Time Machine exclusion. Temp copies live in a 0700 `tmp/` under the case root and are swept at start. Typer runs with `pretty_exceptions_show_locals=False`. Models are provisioned ahead of time and runs set `HF_HUB_OFFLINE=1`. The no-socket test covers the app's import and shield paths as well as the core. Encryption at rest (owner item 7, 2026-10-21): FileVault is required as above. Per-case encryption is an opt-in flag (`chatx case create --encrypt`). It is off by default because SQLCipher has not been shown to work with sqlite-vec and FTS5 (**RT-19**). **RT-14**.
- *(opus F-26)* §2 gains an **intended use** section that names the people in the data (the owner, and third parties who did not consent) and what the tool may be used for. Each cloud run records the vendor terms in force (retention and zero-data-retention status, as stated by the owner). `chatx case purge` deletes a case and its secrets, keeping one audit line outside the case. Owner item 11 (2026-10-21): the data is the owner's own conversations, kept as a personal archive. Cloud processing of other people's messages is allowed only after the gates and under zero-retention, no-training terms (T10).
- *(chatgpt F23)* Covered by the prompt-injection posture (T15). Added: an adversarial test set of chunks containing instructions, fake JSON and fake surrogate tokens, whose labels must match the clean-text baseline. Output fields are enums plus citations to request lines; a citation to a line not in the request is rejected.
- *(chatgpt F31)* §3.15 lists every place message content can land, with a rule for each: case db and its WAL, FTS shadow tables, `secrets/`, attachments, case `tmp/`, quarantine files (moved into the case, 0700), logs, crash output, model caches, exports, the dNh adapter's JSONL, and shell history (names typed as `--contact`; the CLI also accepts a contact from a file or a prompt). Diagnostics use an allowlist of fields (ids, counts, codes, hashes); anything else is dropped.

## T21 Tests, fixtures & coverage — codex F25 · grok F17 · agy F-24 · opus F-21, F-22, F-35 · chatgpt F33

Change (decided), §7, §8:
- Fixtures must include real-shape artifacts: typedstream `attributedBody` blobs (dNh's observed prefixes plus sanitized captures from the owner's db via the probe), `p:0/`/`bp:` reaction guids, `thread_originator_guid`, `~/Library` paths, multi-chat joins, `date_edited`/`date_retracted`, group events, sticker type 1000, WhatsApp Android + iOS exports, Instagram with mojibake, `.eml` with `References`.
- The old bplist-based fixtures are legacy regression tests, not goldens, and are deleted at the end of P1.
- Coverage: no `omit` at all; `--cov-fail-under=90` over both packages (already in §5.6; §7 wording aligned).
- *(opus F-21)* Fixture databases are generated from per-macOS-version schema snapshots (DDL only, captured by the probe; no rows from the owner's data), so goldens cannot pass against a schema that does not exist. Property tests cover the reaction and edit folds (T06).
- *(opus F-22)* Shield and gate modules get branch coverage plus mutation testing (`mutmut`) with a kill-rate floor, and a type-level test that cloud request models have no attachment field. Line coverage stays the gate everywhere else.
- *(opus F-35)* Covered: §5.6 already brings `redaction/*` and the other omitted packages under coverage.
- *(chatgpt F33)* The P0 exit needs a green CI run on the new repo (run URL recorded) that tests the installed wheel (T18) and includes the failure paths (exit 3, `E_GATE_MISMATCH`, `E_SCHEMA_MISSING`). The real-data shield evaluation cannot run in CI because it uses the owner's data; it is a separate local gate, and the docs say CI shows only the synthetic one.

## T22 Operations, intent regression & CI gates — codex F26, F27 · agy F-25 · opus F-30 · chatgpt F34, F35

Change (decided), §3.12, §6 P0, new §8 disposition table:
- CLI gains `chatx case resume | repair | delete-source`, `chatx import … --resume`, `chatx index build --incremental`.
- Disposition of old requirements: `backfill` → `import --resume`; `index update` → `index build --incremental`; `simulate`, `reply` → dropped (no consumer, reason stated); NFR "1M-message corpus" → tracked measurement at P5 (T13).
- P0 scope explicitly includes **rewriting** `.github/workflows/*` and `config/arch-gates.yml`; the old gate file is not carried.
- *(opus F-30)* Gate refusal moves from exit 2, which is Click/Typer's usage-error code, to exit 3 (decided). The exit-code table is documented in `docs/reference/errors.md` next to the RFC 9457 problem types. **E7** (2026-10-21) confirms Click's `UsageError.exit_code` is 2; that Typer inherits it is inferred.
- *(chatgpt F34)* §3.12 gains a behaviour table. Exit codes: 0 success, 1 error, 2 usage (Click), 3 gate refused, 4 partial (counts printed and recorded). Per command it states what a partial or interrupted run leaves (watermark, `status=partial`) and what `delete-source` and `case purge` remove and keep. Every input record ends in exactly one disposition, and the report's counts sum to the input count (asserted). A case directory is self-contained, with paths stored relative to the case root, so it can be moved.
- *(chatgpt F35)* Appendix A.1 corrections: `redact` warns and exits 0 by default, but exits 1 under `--preflight` when the preflight fails on hard-fail or low coverage (`main.py:337-350`); the multi-vector store is reachable from `index` and `query` through `--store multi` or `--multi-vector` (`main.py:737-739, 781, 825-826, 862`), so it is not "dead to CLI". The disposition table above is extended to every old command and every documented feature in Appendix A, one row each: kept, ported, deferred to a named phase, or dropped with a reason.

## T23 Ecosystem currency — codex F29, F30 · opus F-29 · chatgpt F38

Change (decided), §3.12, §3.7:
- "RFC 7807" → "RFC 9457 (Problem Details; obsoletes 7807)" everywhere. **E6**: RFC 9457's abstract says it obsoletes RFC 7807.
- Presidio stays the **candidate** framework; the P3 eval compares it against at least one alternative NER route (GLiNER / spaCy-only); **RT-10**: Presidio stewardship and release cadence; **RT-11**: current small-NER options for chat text.
- *(opus F-29)* Opus reported that Presidio is now stewarded by Data Privacy Stack and moving to a community-owned V2. **E5** (2026-10-21) confirms the move: Presidio is now an independent, community-governed project under the `data-privacy-stack` org, still MIT, with images on ghcr.io. The transition document does not mention V1 or V2. The install guide links "Migrating from V1 to V2" to `docs/presidio_V2.md`, which was not read, so the V2 question stays in **RT-10**. Pin the version with hashes for the P3 eval. OpenAI Privacy Filter, an open-weight PII detection and redaction model that runs locally (**E5**), joins the **RT-11** candidates.
- *(chatgpt F38)* `docs/reference/conformance.md` lists each external component (SQLite, sqlite-vec, Presidio, the NER models, the local model server, the Anthropic API and model ids, uv) with the version tested, the date, and the evidence (a link or a test). `chatx providers check` and P0 CI write what they observe; anything not observed stays UNKNOWN.

---

## Research targets raised by this plan (to merge with the auditors' lists)

| RT | Topic | Raised by | Status 2026-10-21 |
|---|---|---|---|
| RT-1 | SQLite minimum version for WAL/backup-API correctness | T01 (codex F28) | **Answered** by E4: floor written into T01 |
| RT-2 | Canonical JSON: JCS (RFC 8785) vs dNh `canonical_json` | T02 | Open |
| RT-3 | Generic NSAttributedString typedstream decoders | T06 | Open |
| RT-4 | sqlite-vec quantized vector types and scan cost at 1M rows | T13 | Partly: `vec0` is an exact scan, pre-v1, v0.1.9 (E9). Quantized types and scan cost stay open (P0.5 spike e) |
| RT-5 | Local embedding models by dimension/quality for chat text | T13 | Open |
| RT-6 | Bundle signing tool and verification UX | T14 | Open |
| RT-7 | Anthropic API: embeddings availability, seed/determinism, structured outputs, prompt caching, Batch API — current docs; per-model sampling and forced `tool_choice` constraints (opus F-02) | T15 | Mostly answered by E1 and E2a–E2d (T15). Open: prompt caching and Batch API for this workload |
| RT-8 | uv workspace/path-dependency syntax, current docs | T18 | **Answered** by E8: syntax written into T18 |
| RT-9 | iOS encrypted backup decryption libraries | T19 | Open |
| RT-10 | Presidio stewardship and release cadence; V1→V2 migration (opus F-29) | T23 | Partly: stewardship confirmed (E5). Open: what V2 changes (`docs/presidio_V2.md` not read) |
| RT-11 | Small NER engines for short, slangy chat text | T23 | Open. OpenAI Privacy Filter added as a candidate (E5) |
| RT-12 | Structured-output support across local servers (Ollama, llama.cpp, vLLM, LM Studio, MLX) | T15 (opus F-27) | Partly: request shapes per server and vLLM reproducibility (E3). Open: llama.cpp and LM Studio reproducibility, MLX |
| RT-13 | Confidence calibration for LLM labels on small gold sets (reliability curves, ECE) | T16 (opus F-18) | Open |
| RT-14 | macOS exposure controls: `.noindex`, Time Machine exclusion, detecting iCloud-synced folders | T20 (opus F-11) | Open |
| RT-15 | Inter-rater agreement protocol for relationship and analysis labels | T16 (opus F-25) | Open |
| RT-16 | Local language identification for short chat messages | T09 (chatgpt F05) | Open |
| RT-17 | Binding a gate token to the final request bytes: transport hooks in the Anthropic and OpenAI-compatible clients | T10 (chatgpt F04) | Open |
| RT-18 | Evaluating citation support in answers (claim-to-span attribution, local judge models) | T17 (chatgpt F27) | Open |
| RT-19 | Per-case encryption with SQLCipher (or an encrypted sparsebundle) alongside sqlite-vec and FTS5: compatibility, speed, key handling | T20 (owner item 7) | Open |

## Owner decisions (answered 2026-10-21)

Asked in this session with the multiple-choice tool; the answers below are the owner's words (option labels), with the option's description as shown. Items 1–3 are the design's §12 items; 4–13 were raised by this plan. They replace the open-items list that stood here.

| # | Question | Answer | What the plan does with it |
|---|---|---|---|
| 1 | New repo, or carry ChatX's git history (§3.2)? | New clean repo | New `chatstack` repo; ChatX is tagged `pre-rearchitecture-2026-10-20` and archived read-only; kept files carry a "ported from <sha>" header. |
| 2 | What is a case? | Case per import set | A case holds one or more source imports; contact is a query filter; a message lives in exactly one case. |
| 3 | Label a real sample for the shield? | Yes, full sample | About 600 labelled examples per entity class present; with zero misses the 95 % lower bound on recall reaches 0.995 (T09). P0.5 spike (b) uses the first ~300 (T19). |
| 4 | Label an enrichment gold set? | Yes | Label thresholds are tuned and calibrated on it (T16, RT-13). Until it exists, labels stay `calibrated: false` and cloud enrichment stays off. |
| 5 | dNh dedupe formula | dNh keeps its formula | dNh's append-only log is unchanged. The core exposes `content_hash` and source ids, and dNh's adapter maps them into its existing dedupe inputs (T05). |
| 6 | Where the pseudonym map lives | Separate secrets file | `cases/<case>/secrets/pseudonyms.sqlite3`, mode 0600, left out of bundles unless `--include-pseudonym-map` is passed, which warns first (T11). |
| 7 | Encryption at rest per case | Opt-in, require FileVault | Case creation refuses without FileVault unless overridden. Per-case encryption is an opt-in flag, not the default, until SQLCipher is shown to work with sqlite-vec (T20, new RT-19). |
| 8 | dNh event type for imported outbound history | New imported type | For example `msg.outbound.imported`, which needs a small dNh schema change. `msg.outbound.manual` is not reused, because dNh services consume it (T05). |
| 9 | When dNh deletes its chat.db parsers | After 30-day parallel run | Both paths run on real ingest for 30 days. dNh's parsers are deleted only if the outputs never disagree (T05). |
| 10 | Hard-fail list and `cloud_allowed` policy | Special categories stay local | Every fine label is local-only. Coarse labels about sexuality, health, substances, crime or violence, and anything involving minors are `cloud_allowed: false`. Content involving minors is flagged locally and excluded from every export (T09, T16). |
| 11a | Whose data is this tool for? | My own conversations | A personal archive and analysis of chats the owner took part in. Forensic bundles are for the owner's own records (T14, T20). |
| 11b | May redacted chunks of other people's messages go to a cloud model? | After gates, zero retention | Only after the shield passes on the owner's labelled real samples, and only under vendor terms with zero data retention and no training (T10, `E_VENDOR_TERMS`). |
| 12 | dNh events stored without text that now decodes | Leave them and count | The adapter reports the count. dNh's log is untouched (T05). |
| 13 | Licence of `chat-extraction-core` | MIT | Same licence as ChatX. Owned by the owner (DDD-Enterprises); proprietary dNh may depend on it (T18). |
| — | Derived `msg_id` with an occurrence index (chatgpt F06) | Approve occurrence index | `sha256(platform, conv_id, sent_at, sender.handle, text, occurrence)[:32]` stands (T02). |
| — | Model selected for the ChatGPT web audit | GPT-6 Pro | Recorded in the README run table as the owner's report. The ChatGPT session called itself "GPT-6 Astra Pro". There is no runtime receipt. |

Still with the owner, later: approval of the written hard-fail definitions in `config/labels.yml` (P3, item 10), and the vendor-terms statement in `[providers.cloud]` before any cloud run (item 11b).

## External facts checked (2026-10-21)

Source: `external-fact-check.md`, written by a Sonnet fact-checker (`model: sonnet`, `effort: medium`; see the README run table) from vendor and project pages fetched 2026-10-21. The verifier files keep their literal UNKNOWN verdicts, because those record what could be checked from the repos. The rows below settle the external part of these rows: codex F15, F28, F29, F30; grok F2, F16; opus F-02, F-27 (partly), F-29 (partly), F-30. chatgpt F38 stays UNKNOWN, and its remedy (`conformance.md`) is adopted in T23. The cross-audit matrix is unchanged.

| E | Auditor rows | Checker's verdict (verbatim) | What it means for those rows | Supervisor re-check | Plan change |
|---|---|---|---|---|---|
| E1 | codex F15, opus F-28 | SUPPORTED | Anthropic offers no embedding model and names Voyage AI as one provider. | — | None. Embeddings stay local (T15). |
| E2a | grok F2, opus F-02 | CONTRADICTED (no `seed` exists) | The claim checked was "a `seed` exists", so the rows' "no seed" holds. | The checker read 100,000 of 142,661 characters of the API reference. Neither migration guide mentions a seed (grep of both saved pages). | T15 |
| E2b | grok F2, opus F-02 | CONTRADICTED for "accepted or ignored": both models reject with HTTP 400 | The rows' "rejected with 400" holds. | Re-read the Sonnet 5.5 and Opus 5.5 migration guides: holds. | T15 |
| E2c | opus F-02 | CONTRADICTED (both models return 400, with or without thinking) | The claim checked was "forced `tool_choice` is supported", so the row's "rejected" holds. | Re-read both guides: holds. | T15 |
| E2d | opus F-02 | SUPPORTED (thinking on by default; shares `max_tokens`) | Holds. | Re-read both guides: holds. | T15 thinking and output budget |
| E3 | opus F-27 | PARTLY_SUPPORTED | Request shapes differ per server. vLLM is not reproducible by default. For Ollama, non-reproducibility is NOT_FOUND in vendor docs. llama.cpp and LM Studio reproducibility were not checked. | — | T15, RT-12 |
| E4 | codex F28 | SUPPORTED | Affects 3.7.0–3.51.2; fixed in 3.51.3; backports in 3.44.6 and 3.50.7. | Re-read sqlite.org/wal.html: holds. | T01 SQLite floor |
| E5 | codex F29, opus F-29 | PARTLY_SUPPORTED | The stewardship move holds. A V1→V2 migration is not established by the transition doc. | — | T23, RT-10, RT-11 |
| E6 | codex F30 | SUPPORTED | RFC 9457 obsoletes RFC 7807. | — | T23 |
| E7 | opus F-30 | SUPPORTED | Click's usage errors exit 2; for Typer this is inferred. | — | T22 |
| E8 | grok F16 | SUPPORTED | Both path and `workspace = "<root>"` sources are valid from outside a workspace. | — | T18 |
| E9 | agy F-17 | SUPPORTED | `vec0` is an exact scan; sqlite-vec is pre-v1, latest v0.1.9. | — | T13 |

## Not changed on purpose

- SQLite per case, no services (§3.5) — every auditor's scale concern is addressed by query plan, quantization and measurement, not by reintroducing a server.
- Presidio as the starting framework (§3.7) — kept as candidate, decided by the P3 eval.
- New repo rather than history carry (§3.2) — unchanged; the owner confirmed it 2026-10-21 (item 1).
- HMAC-128 handle pseudonyms (`sender.pseudonym`) — kept; only redaction tokens switch to surrogates (T11, opus F-12).
- `msg_id` without a source-file fingerprint — opus F-13's suggestion declined, because it breaks id stability across re-exports (T02).
- Stopping the whole run when the shield fails (chatgpt F15's wording) — not adopted: the cloud stage stops and the local pipeline continues, because nothing leaves the machine on the local path (T09, T19).
- External attestation for bundles (chatgpt F26) — stays optional (RFC 3161 timestamp, owner-chosen, T14); the forensic claim is narrowed instead.

## Outside this plan (recorded for the owner, not ChatX work)

- dNh's venv links SQLite 3.47.1 (checked 2026-10-21), which is inside the WAL-reset range (E4). dNh's source does not set `journal_mode` (grep of `src/`, 2026-10-21), so it probably runs in the default rollback-journal mode, where that bug does not apply. The database file was not opened to confirm this, because `data/` is outside this audit's read scope.
