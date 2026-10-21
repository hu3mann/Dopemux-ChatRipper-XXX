All six sections are below. Everything was read from source and nothing was executed. dNh is at `/Users/hue/code/dNh_CRM`. Citations are `repo:path:line`. Line numbers for `events.py` are taken from my grep output and read-ranges, so treat them as ±2.

## 1. dNh canonical message / event model

dNh has no standalone "ChatMessage" class. An inbound message is an `EventEnvelope` of type `MSG_INBOUND_RECEIVED` with a text payload.

**`EventEnvelope`** (`dNh:src/dnh_crm/events.py:1902-1962+`, frozen, `extra=forbid`):

| Field | Type | Required / default |
|---|---|---|
| `schema_version` | `Literal["dnh.crm.event.v1"]` | default |
| `event_id` | str, min 1 | required |
| `event_type` | `EventType` | required |
| `occurred_at` | datetime | required |
| `conversation_id` | str, min 1 | required |
| `interaction_id`, `agent_session_id` | str \| None | optional |
| `channel` | `Channel` | required |
| `direction` | `Direction` | required |
| `actor` | `EventActor` | required |
| `sender_handle`, `recipient_handle` | str \| None | optional |
| `idempotency` | `EventIdempotency` | required |
| `external` | `EventExternal` | required |
| `tooling` | `EventTooling` \| None | optional |
| `security` | `EventSecurity` \| None | optional |
| `payload` | union of about 40 payload models | required |

- **`EventActor`** (`events.py:470`): `role` (`ActorRole` enum), `handle` (str, min 1).
- **`EventIdempotency`** (`events.py:477`): `dedupe_scope`, `dedupe_hash`.
- **`EventExternal`** (`events.py:484`, `extra=allow`): `source_message_id`, `source_thread_id`.
- **`EventSecurity`** (`events.py:500`): `contains_sensitive_facts` (bool, default False), `provenance` (str \| None), `verification_state` (default `NOT_REQUIRED`).
- **`EventPayload`** (`events.py:519`, `extra=allow`): `text` (str, min length 1).
- **`IMessageAttachmentOnlyPayload`** (`events.py:525`): `text` is `""`, `attachment_only` is `True`, `attachment_count` is int ≥1.
- **`TelegramEventPayload`** (`events.py:533`): `conversation_id`, `telegram_update_id`, `telegram_chat_id`, `telegram_thread_id`, `telegram_message_id`, `date_unix` (all required), `from_id`, `from_username`, `text`, `caption` (optional), `is_edited` (bool, default False).
- **Enums:** `Channel` (`events.py:172`) has IMESSAGE, TELEGRAM, SMS, WHATSAPP, EMAIL, EMAIL_PROTON, EMAIL_GMAIL, TELEGRAM_OPS, SYSTEM. `Direction` (`events.py:184`) is INBOUND / OUTBOUND / INTERNAL. `ActorRole` (`events.py:190`) is CLIENT / OPERATOR / SYSTEM.

**Pre-envelope iMessage record, `IMessageRawRecord`** (`dNh:src/dnh_crm/ingest/imessage.py:11-24`, frozen, `extra=forbid`). All five fields are required: `message_id`, `thread_id`, `sender_handle` (all str, min 1), `text` (str), `sent_at` (datetime).

**Id formation**
- **iMessage message id:** the chat.db `guid` if non-empty, else `rowid:{rowid}` (`dNh:src/dnh_crm/ingest/imessage_mapper.py:17`).
- **iMessage event id:** `evt-imessage-{message_id}` (`dNh:src/dnh_crm/ingest/normalizer.py:~38`).
- **iMessage conversation id:** `imessage:{thread_id}` (`normalizer.py:~40`).
- **iMessage thread id:** `chat_guid` if known, else `chat:{chat_id}` (`imessage_mapper.py:~70-90`).
- **iMessage handle:** `handle.id` from chat.db (`imessage_source.py:~125`). There is no separate contact id on the event.
- **WhatsApp export event id:** `evt-whatsapp-export-{dedupe_hash}` (`dNh:src/dnh_crm/ingest/whatsapp_export.py:~118`).
- **WhatsApp source message id:** the same dedupe hash, a sha256 over channel, filename, sender display, text hash and raw ts (`whatsapp_export.py:~165`).
- **WhatsApp thread id:** `whatsapp_export:{filename}` (`whatsapp_export.py:~112`).
- **WhatsApp handle:** `+E164` if the sender looks like a phone number, else the slug `whatsapp_export:{name}` (`whatsapp_export.py:~195-235`).
- **Contacts:** `contact_identities` (handle, handle_type, contact_id) and `conversation_contacts` map handles and conversations to contacts (`dNh:src/dnh_crm/store/migrations.py:53-75`).
- **Dedupe hash:** `compute_dedupe_hash` is sha256 of a canonical payload (`dNh:src/dnh_crm/idempotency.py:14-16`).
- **iMessage dedupe:** the hash covers channel, message id, thread id, handle, ISO `sent_at` and text (`dNh:src/dnh_crm/ingest/dedupe.py:12-24`).

**Timestamps**
- Every ingested timestamp is a tz-aware UTC datetime. `IMessageRawRecord` rejects naive values and converts with `astimezone(UTC)` (`imessage.py:18-24`).
- The chat.db date is converted by trying Apple-epoch and Unix-epoch divisors and accepting the first result between 2004 and 2100 (`imessage_mapper.py:35-60`).
- WhatsApp export times are parsed with `strptime` and then forced to UTC with `replace(tzinfo=UTC)`. No source timezone is applied (`whatsapp_export.py:~175-192`).
- Email times go through `parsedate_to_datetime` and then `astimezone(UTC)` (`email_eml.py:~203-213`).

**Attachments**
- iMessage attachments travel as a list of `{attachment_id, storage_ref}` in the raw dict (`imessage_mapper.py:30-35`).
- The envelope carries only `attachment_count` (`events.py:525`).
- Separate events, `MediaAttachmentRecordedPayload` (`events.py:806-827`), carry the detail. Its fields are `attachment_id`, `conversation_id`, `source_event_id`, `source_channel`, `media_kind` (IMAGE / VIDEO / AUDIO / FILE / UNKNOWN), `mime_type`, `byte_size`, `sha256_content_hash`, `original_filename`, `storage_ref`, `perceptual_hash` and `created_at`.

**Reactions, replies, edits, unsends**
- **Reactions and tapbacks:** no model. `rg -i "tapback|associated_message_guid|reaction"` over `dNh:src` found no ingest-model matches.
- **Reply-to:** none on the message model. Only `RecommendationSourceRef` and operator reply events exist.
- **Edits:** only Telegram. `is_edited` is a field (`events.py:~546`), `edited_message` is read in `ingest/telegram.py:66-69`, and the edit flag is part of the dedupe key (`ingest/dedupe.py:28-30`).
- **Unsends:** nothing in the iMessage model. The WhatsApp parser treats "this message was deleted" as a system line and drops it (`whatsapp_export.py:~42`).

**Provenance**
- `EventExternal` holds the source message and thread ids. `EventSecurity.provenance` is a free-form string.
- Email provenance is the `Message-ID` header, or `synthetic:{filehash}` / `file:{filehash}` (`email_eml.py:~111-113`).
- No source file path or raw blob is carried on the envelope.

## 2. ChatX canonical message model

Source: `ChatX:src/chatx/schemas/message.py`.

| Model | Field | Type | Required / default |
|---|---|---|---|
| `CanonicalMessage` (`:43`) | `msg_id` | str | required |
| | `conv_id` | str | required |
| | `platform` | `Literal["imessage","instagram","whatsapp","txt"]` | required |
| | `timestamp` | datetime | required (docstring says UTC; no validator) |
| | `sender` | str | required |
| | `sender_id` | str | required |
| | `is_me` | bool | required |
| | `text` | str \| None | default None |
| | `reply_to_msg_id` | str \| None | default None |
| | `reactions` | list[Reaction] | default [] |
| | `attachments` | list[Attachment] | default [] |
| | `source_ref` | SourceRef | required |
| | `source_meta` | dict[str, Any] | default {} |
| `Reaction` (`:9`) | `from_` (alias `from`) | str | required |
| | `kind` | str | required |
| | `ts` | datetime | required |
| `Attachment` (`:19`) | `type` | `Literal[image, video, audio, file, unknown]` | required |
| | `filename` | str | required |
| | `abs_path`, `mime_type`, `uti`, `transfer_name` | str \| None | default None |
| | `source_meta` | dict | default {}, `exclude=True` |
| `SourceRef` (`:36`) | `guid` | str \| None | default None |
| | `path` | str | required |

**Mismatches with `ChatX:schemas/message.schema.json`**
- **`text` required:** the schema's `required` list includes `text`, `reactions` and `attachments`. In Pydantic all three have defaults, so they are optional on input.
- **Extra keys:** the schema sets `additionalProperties:false` on the message, reaction, attachment and source_ref objects. Pydantic uses its default `extra`, which ignores unknown keys.
- **`Attachment.source_meta`:** excluded from dump in Pydantic and absent from the schema (`message.py:31-33`). That part is consistent.
- **`source_meta`:** the schema allows it at the top level but does not require it. Pydantic gives it a default.
- **Timestamps:** the schema has `format: date-time`. Pydantic does not require a timezone-aware value.
- **Enums:** the platform and attachment-type enums match.

## 3. Alignment table

| Concept | ChatX | dNh | Compatible? |
|---|---|---|---|
| Message id | `msg_id` (str) | `external.source_message_id` (and `event_id` = prefix + id) | rename |
| Conversation / thread id | `conv_id` | `conversation_id` (`imessage:{thread}`) and `external.source_thread_id` | rename; dNh has two |
| Platform / source | `platform`: imessage, instagram, whatsapp, txt | `channel`: IMESSAGE, TELEGRAM, SMS, WHATSAPP, EMAIL, EMAIL_PROTON, EMAIL_GMAIL, TELEGRAM_OPS, SYSTEM | rename + value conflict; instagram and txt missing in dNh, others missing in ChatX |
| Sender display | `sender` | none; only `actor.handle` / `sender_handle` | missing in dNh |
| Sender id | `sender_id` ('me' or normalized handle) | `actor.handle` | rename |
| Direction | `is_me` (bool) | `direction` (INBOUND / OUTBOUND / INTERNAL) + `actor.role` | type conflict |
| Timestamp | `timestamp` (datetime, UTC by docstring) | `occurred_at` (datetime, forced UTC) | rename |
| Text / body | `text` (str \| None) | `payload.text` (min length 1, or `""` plus `attachment_only`) | rename + nullability conflict |
| Attachments | `attachments[]` (type, filename, abs_path, mime_type, uti, transfer_name) | separate `MediaAttachmentRecordedPayload` events; envelope carries only a count | type conflict (inline vs separate event); no `abs_path` or `uti` in dNh |
| Reactions | `reactions[]` (from, kind, ts) | none | missing in dNh |
| Reply-to | `reply_to_msg_id` | none | missing in dNh |
| Edited / unsent | none | Telegram `is_edited` only | missing in ChatX |
| Provenance / hash | `source_ref{guid, path}`, `source_meta` | `idempotency{scope, hash}`, `external`, `security.provenance` | different shape; no `source_ref.path` in dNh; no content-hash field in ChatX |

**Hard conflicts**
- **Direction:** ChatX models a user-sent flag (`is_me`). dNh's iMessage path only ingests `is_from_me = 0` (`imessage_source.py:~60`, `read_latest_inbound` query), so there is no outbound iMessage ingest model.
- **Empty text:** dNh requires non-empty text or an attachment-only marker. ChatX allows `None`.
- **Id derivation:** dNh WhatsApp ids are derived from a hash, not a platform id. dNh iMessage ids are `guid` or `rowid:N`. ChatX `msg_id` is "rowid or GUID".
- **Envelope strictness:** dNh `extra=forbid` and frozen versus ChatX default.
- **Timezone enforcement:** dNh enforces tz-aware UTC. ChatX does not.
- **Attachment shape:** ChatX inline versus dNh separate events.
- **Provenance fields:** the two sides share none.
- **Platform enums:** the two enums do not overlap cleanly.

## 4. Packaging and dependency style

| | ChatX | dNh |
|---|---|---|
| Name | `chatx` 0.1.0 (`ChatX:pyproject.toml:6-7`) | `dnh-crm` 0.1.0-alpha.1 (`dNh:pyproject.toml:2-3`) |
| requires-python | `>=3.11` (`:11`) | `>=3.12` (`:5`) |
| Build backend | hatchling (`:1-3`) | hatchling |
| Dependency bounds | mixed: some `>=x,<y` (e.g. `pydantic>=2.8,<3`, `httpx>=0.27,<0.28`), others lower-bound only | lower-bound only (e.g. `pydantic>=2.10`) |
| Extras | llm, local-llm, embeddings, gpu-optimize, wave3, dev | dev, telegram, calendar, gmail, retrieval (`:34-60`) |
| Dev groups | extra only | `[dependency-groups] dev` plus the extra; `[tool.uv] default-groups=["dev"]` |
| Lock / tooling | `uv.lock`; venv prompt "chatx", uv 0.12.11 | `uv.lock`; venv prompt "dnh-crm", uv 0.11.7 |
| `.venv` interpreter | CPython 3.12.9 | CPython 3.12.8 |
| Workspace, path or git deps | none found in `pyproject.toml` (UNKNOWN for git deps hidden in the lock) | none found; grep for `workspace` or `[tool.uv.sources]` matched nothing in either file |

The ChatX `[project.scripts]` section exists, but I did not read its entries. The same applies to the optional `.venv-dopetask` in dNh.

## 5. Parser reality in dNh

**`imessage_attributed_body.py`** (307 lines): a real typedstream parser, not a heuristic.
- It checks the exact header `\x04\x0bstreamtyped\x81\xe8\x03` (`:33`).
- It runs a bounded, non-recursive state machine and does not use `NSUnarchiver` (`:1-17`).
- It validates the root class chain against a pinned layout table (`:68-81`).
- It then validates the string class chain and reads the inline UTF-8 payload (`:176-190`).
- Back-references are never resolved. Only two layouts are accepted.
- Any deviation returns an `unsupported` or `malformed` result instead of falling back.
- Limits are 256 KB in and 64 KB out (`:29-30`).
- The docstring says the module "is intentionally unwired" (`:16-17`).
- A repo-wide `rg` finds it referenced only by `dNh:tests/unit/test_imessage_attributed_body.py` and `dNh:scripts/imessage_attributed_body_probe.py`. It is not imported by `ingest_runner.py` or `imessage_source.py`.
- Tests are in `dNh:tests/unit/test_imessage_attributed_body.py` (1013 lines).
  - Fixtures are hand-built bytes from a builder (`_archive`, `:60-90`).
  - Real-snapshot prefix constants pin the builder against observed macOS bytes (`:95-113`).
  - Full real blobs: UNKNOWN. I did not inspect the rest of the test file or the probe script.

**Other parsers** (no `instagram_export.py` or `telegram_export.py` exists; see NOT VERIFIED)

| Module | LOC | Quirks handled | Tests |
|---|---|---|---|
| `ingest/whatsapp_export.py` | 248 | Multiline continuation (`:90-105`); system-line markers (`:30-49`); `<media omitted>` placeholder (`:26-29`); 2- and 4-digit years, 24h and AM/PM, ISO dates (`:178-189`); CRLF normalization. No timezone handling. | `dNh:tests/unit/test_whatsapp_export_ingest_unit.py` (216), `dNh:tests/integration/test_whatsapp_export_ingest.py` (218) |
| `ingest/email_eml.py` | 297 | Multipart walk, text/plain plus text/html stripped to text, charset fallback with `errors="replace"`, attachment metadata, synthetic id when `Message-ID` is missing | `dNh:tests/unit/test_email_eml_ingest_unit.py` (309), `dNh:tests/integration/test_email_eml_ingest.py` (243) |
| `ingest/telegram.py` | 322 | Not an export parser. It handles Bot API updates (`message` / `edited_message`) and operator-command classification (`:60-85`). | `dNh:tests/unit/test_telegram_ingest.py` (222) plus several integration files |
| Instagram | none | `rg -i instagram` found no files or modules in dNh `src` | none |

Neither the email nor the Telegram module addresses Instagram-style mojibake repair. A grep for `latin` / `mojibake` in `src` found nothing.

**iMessage chat.db reading:** dNh reads chat.db directly. It opens `sqlite3.connect(f"file:{chat_db_path}?mode=ro", uri=True)` (`dNh:src/dnh_crm/ingest/imessage_source.py:140`) and queries the `message`, `handle` and `chat` tables. `ingest_runner.py:12-21,56-60` imports and uses these readers. The default path is `~/Library/Messages/chat.db` (`dNh:src/dnh_crm/config.py:28`). It also has a BlueBubbles live bridge (`dNh:src/dnh_crm/integrations/imessage_bluebubbles*.py`). The direct reader selects only the `text` column and does not decode `attributedBody` (`imessage_source.py:~110-120`).

## 6. dNh persistence for messages

- **Store:** a SQLite file, default `./data/dnh_crm.sqlite3` (`dNh:src/dnh_crm/config.py:24`).
- **Connection code:** `event_repo.py:202-207,4061-4062`.
- **Migrations:** all in one Python module, `dNh:src/dnh_crm/store/migrations.py`, with no separate migration files. It also creates `projections`, `projector_state`, `ingest_source_cursors`, `ingest_source_row_links` and `ingest_source_runs`.
- **Events table** (`migrations.py:5-27`): `events` has columns `id`, `event_id` (unique), `event_type`, `occurred_at`, `conversation_id`, `channel`, `direction`, `actor_role`, `actor_handle`, `dedupe_scope`, `dedupe_hash`, `source_message_id`, `source_thread_id`, `payload_text` and `envelope_json`. It has `UNIQUE(dedupe_scope, dedupe_hash)` and a replay index on `(conversation_id, occurred_at, id)` (`:30-33`).
- **Vector and text search:** the same SQLite file holds `memory_chunks`, a sqlite-vec `memory_vectors vec0(embedding float[1024])` table (`:198-203`) and an FTS5 `chunks_fts` table (`:206`).
- **Optional dependencies:** `sqlite-vec` and `qdrant-client` are in the `retrieval` extra (`dNh:pyproject.toml:56-59`).
- **Qdrant usage:** UNKNOWN. I did not trace it.
- **Event-log JSONL store:** none found.

## NOT VERIFIED

- Instagram: there is no `instagram_export.py`, `telegram_export.py` or `normalize.py` in dNh. The closest are `ingest/normalizer.py` and `ingest/telegram.py`. A repo-wide `find -ipath '*instagram*'` returned nothing.
- Whether any dNh code path (outside tests and the probe script) calls the `attributedBody` decoder. The only matches are the tests and the probe.
- Whether the real-blob fixtures exist beyond the prefix constants in the `attributedBody` test.
- Exact line numbers where I wrote `~`.
- Whether the BlueBubbles normalizer maps reactions or edits (only an event-type token check at `imessage_bluebubbles_normalizer.py:285` was seen).
- Qdrant use in dNh.
- The ChatX `[project.scripts]` entries, and ChatX's Instagram and iMessage extractors (outside this brief).
- Hidden path or git sources in either `uv.lock`.
- The ChatX Pydantic-versus-JSON-Schema comparison is by reading only; I ran no validation.
