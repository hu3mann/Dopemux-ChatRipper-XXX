# ChatX rearchitecture design — audit report (grok)

## 0. Reviewer identity

| Item | Value |
|---|---|
| Auditor | grok |
| Model | Grok 4.7, as this session is identified. No runtime receipt of model id or effort: both UNKNOWN. |
| Runner | Grok Build on macOS, zsh. |
| Knowledge cutoff | Not stated on the session card. I will not invent a date. Section 15 uses pages fetched on 2026-10-20. Unfetched claims stay PLAUSIBLE or UNKNOWN. |
| Subject | Design SHA-256 `c481b18880dae379ff2b39bfdeb0bd2d9e4a81956ee84deda4aae1cc8bd9f2a7` (34,277 bytes). `docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md` is byte-identical. |
| ChatX | `/Users/hue/code/Dopemux-ChatRipperXXX`, branch `governance-doctrine-integration`, HEAD `9c3dd6b01197a1205fc12c6b5bde6ba7cba258f9`, dirty worktree. Audited as on disk. |
| dNh | `/Users/hue/code/dNh_CRM`, branch `migrate-cheaperinference`, HEAD `39c75bdec38d0fb4853d914056669615c1c1e1b6`, dirty worktree. |
| Independence | This session did not implement the design. No subagents. The packet-audit JSON from the independent-audit skill is omitted because the brief defines Output A and Output B for a design draft, not a proof bundle. |
| Time | One read-only session on 2026-10-20. Wall clock was not instrumented. |
| Method | Design, evidence notes, and cited source ranges. `git rev-parse`/`status`, `wc`, `shasum`, `uv --version` (`0.12.11`, 2026-09-08, aarch64), a read-only count of `config/labels.yml`, web search for item 15. No tests, no installs, no writes outside this directory, no `.env` or secrets. No fixture `*.db`, so `sqlite3 .schema` was not run; the SQL fixture was read. |

Evidence notes 01–03 are leads. A line citation means this session read that line.

## 1. Executive summary

1. §3.7 replaces today's token-ratio with per-class entity recall. That is a real fix for `policy_shield._calculate_coverage`, and it still does not de-identify a chat. Dates, places, relationships, and style survive a perfect Presidio score. The §1 success line overclaims the gate.
2. The gate's denominator is "every entity class present in the case." Detecting that a class is present is the original problem. A synthetic set written beside the recognizers, plus a P3 exit of "eval meets targets," rewards an easy generator.
3. The second opinion has no `n`, no confidence level, and an LLM as the oracle. Zero hits in an unspecified sample bound nothing. Keep it as a spot check or publish `3/n`.
4. §3.7 writes both `⟦TKN:<id8>⟧` and "128-bit." `identity/normalize.py:54` is already `mac[:32]`. `patterns.py:233` is the 32-bit tokenizer. A reversible map inside `case.sqlite3` makes the case directory the secret, and the zip manifest does not exclude it.
5. §3.6 cannot be implemented as written against Anthropic's docs fetched on 2026-10-20. Anthropic publishes no embedding model. Models after Opus 4.6 reject `temperature` other than `1.0`. The sample config sends `temperature = 0.0` to `claude-sonnet-5-5`. `seed = 42` is not a portable promise.
6. `claude-sonnet-5-5` and `claude-opus-5-5` match the public id shape on the fetch date. They remain config, and they will move.
7. v2 has no column-to-field map. The live SELECT (`extract.py:88-108`) omits read/delivered/edited/retracted times, thread originator, balloon id, item and group-action types, attachment-cache flag, expressive style, and account. `platform` is the literal `"imessage"` (`extract.py:186`). `msg_id` is `msg_{rowid}` (`extract.py:184`) while §8 says to port the tests with minimal change.
8. Prior text lives in `message_summary_info`, not in a string column, and public notes disagree by OS on `date_retracted`. Tapback targets use `p:<part>/<guid>` and `bp:<guid>`; `extract.py:229` does exact guid match. `reactions.py:36-37` treats 3000–3999 as custom adds. §3.4's removal range is the correction only if it beats the keep-list.
9. Keeping `imessage/db.py` keeps a snapshot that drops the WAL: the copy includes `-wal` (`db.py:32-41`) and the open uses `immutable=1` (`db.py:59`). Failed dates become `datetime.now` (`extract.py:181`).
10. dNh has the typedstream parser worth porting and the iMessage product path worth leaving. Two layouts, unwired, 64 KB cap, back-references unresolved. The reader selects `text`, opens the live file `mode=ro`, and marks `is_from_me != 0` as `not_inbound` (`imessage_source.py:57-58`). §9's adapter losses have no table.
11. `[providers.local]` is local only by label. Nothing requires loopback. Phase 7's MCP server returns case text to whatever host called the tool.
12. dNh's vec0 is `float[1024]` (`migrations.py:198-202`). The author's own 1M-vector note says float KNN misses a 100 ms line. G3's "single file" is a directory. An in-zip sha256 manifest does not authenticate itself.
13. A missed recall target should be a passing P3 outcome (cloud stays off). Schema v2 should freeze after a real-db spike, not in the same phase as the first probe. Inferred labels such as `GASLIGHTS` (`storage/base.py:254`) need a store and an export path of their own.
14. Encrypted backups bundled into the psychology phase couple an extraction feature to an ethics feature.
15. Keep the demolition list: token-ratio, JSON hand-offs, Chroma, Neo4j, hardcoded model ids, fake backup decrypt, coverage `omit`. The approval blockers are the gate's meaning, the provider contract, and the chat.db map.

## 2. Findings

| ID | Sev. | Area | Finding | Evidence | Verdict | Change | Cost of ignoring |
|---|---|---|---|---|---|---|---|
| F1 | BLOCKER | 3, 14 | Entity recall is treated as de-identification. Quasi-identifiers are unnamed. The class denominator follows the case. | §1 bullet 3; §3.7; `policy_shield.py:138-157`; `labels.yml:307-308` | CONFIRMED | Measure the labelled class list. Print residual risk on every cloud run. Hold the generator out from recognizer tuning. | Cloud ships on a high score for the wrong question. |
| F2 | BLOCKER | 5, 15 | `embed()` plus a shared `temperature` cannot bind Anthropic and an OpenAI-compatible server. | §3.6; sample toml `temperature = 0.0`, `claude-sonnet-5-5`; §15 docs | CONFIRMED for fetched docs | Split `Embedder` from chat. Per-backend temperature. Remote embedders are a separate gated host. | First Anthropic call returns 400, or text goes to Voyage with no rule. |
| F3 | HIGH | 3, 11 | `id8` fights 128-bit. The map sits in the case DB. Export omits no secret. Salt today is global and mode-unspecified. | §3.7; `patterns.py:230-234`; `normalize.py:19-64` | CONFIRMED | 128-bit ids, per-case salt `0600`, export profile without map, salt, or raw `source_meta`. | Colliding tokens merge two people. A copied case rehydrates the cloud. |
| F4 | HIGH | 1, 2 | No source map. Live SELECT and the fixture omit the forensic columns. Adapter losses are "may ignore." | `extract.py:88-108,184-190`; `imessage_test_data.sql:5-19`; §3.4, §9; `imessage_source.py:109-124,57-58` | CONFIRMED | Normative column-to-field table, OS column, loss behavior. Same for `EventEnvelope`. | Ported `extract.py` is called v2. Edits, groups, SMS/RCS disappear. |
| F5 | HIGH | 2, 4 | Immutable open ignores the copied WAL. Temp dirs hold a full `chat.db`. | `db.py:12-64`; §3.13; SQLite URI docs in §15 | CONFIRMED code; WAL behavior CONFIRMED from SQLite docs | Backup API, or copy then recover without `immutable`, into mode `0700`. | Newest committed messages missing, run looks complete. |
| F6 | HIGH | 1, 2 | Unparseable dates become now. §7 bounds (2004–2100) differ from `time.py` (1999–2100). dNh raises. | `extract.py:181`; `time.py:16-17`; `imessage_mapper.py:10-11,38-58` | CONFIRMED | Quarantine the row. One bounds policy. | Import time is labelled `sent_at`. |
| F7 | HIGH | 5, 10, 11 | Cloud bypass by base URL, and by an MCP host that is itself a cloud client. | §3.6, §3.13, §6 P7; §2 anti-goal | CONFIRMED gap | Loopback allowlist for unredacted paths. P7 returns redacted projections only. | Shield skipped by a URL edit or by Claude Desktop. |
| F8 | HIGH | 3 | Unbounded LLM sample. Hard-fail undefined. Chunk text is redacted after raw handles are written into the line and `meta.contact`. | §3.7–3.8; `chunker.py:166-174`; `policy_shield.py:181-183,265-269`; `patterns.py:162-176` | CONFIRMED | Set `n` and the `3/n` sentence, or demote the check. Owner-defined hard-fail, no spans in logs. Redact messages before chunking. | A short sample "passes." Contact names ride in the clear. |
| F9 | HIGH | 4 | Million-row `float[1024]`, a directory called one file, unsigned manifest. | §3.5, G3, §3.10; `migrations.py:197-211`; §15 scale notes | Design CONFIRMED. Scale PLAUSIBLE from the author's benchmark | Measure before a dimension default. Case root outside iCloud folders. Separate the manifest hash from the zip. | RSS blow-up, a bundle that cannot be shown to be original, synced copies of the corpus. |
| F10 | HIGH | 8, 10 | P3 fails unless the synthetic target is met. Schema freezes with the first probe. Clinical labels share the forensic store. Decrypt sits in P6. | §6 P1/P3/P6; §3.11; `storage/base.py:211-285`; `labels.yml:18-20,320-323` | CONFIRMED | Pre-P1 spike. "Cloud stays off" is a pass. Hypothesis table excluded from the default bundle. Decrypt in its own phase. | Theater eval, wrong frozen fields, "GASLIGHTS" exported as a fact. |
| F11 | MEDIUM | 1, 2 | 3000–3999 mapped as custom adds. No guid-prefix parser. Sticker type 1000 absent. §8 ports the caller anyway. | `reactions.py:7-14,36-37,62-72`; `extract.py:130-148,229`; §3.4 V1; §15 readers | Code and design CONFIRMED. Wire format PLAUSIBLE | §3.4 wins. Parse `p:`, `bp:`, bare guid. Probe 2006/3006. Separate sticker rows from sticker files. | Removals import as adds. Real tapbacks fail to attach. |
| F12 | MEDIUM | 1, 2 | WhatsApp drops system and delete lines; marker `added` is a substring. Instagram reads four payload kinds. PDF is `platform=imessage` with `now()+1s` stamps. | `whatsapp_export.py:33-49,105-107,196-198`; `instagram/extract.py:70-118`; `pdf_ingest/reader.py:68-102` | CONFIRMED | Anchored system markers to `content_kind=system`. Instagram keep/drop list. PDF platform `pdf_transcript`, null time unless printed. | Group history vanishes. A PDF looks like iMessage from today. |
| F13 | MEDIUM | 1 | `content_hash` and derived ids lack a canonical form. `pseudonym` is inside the hashed object and is filled later. `text` inside the derived id changes the id on edit. | §3.4; `idempotency.py:10-16`; `dedupe.py:15-24` | CONFIRMED gap; dNh helper CONFIRMED | Copy dNh's canonical-JSON rules into the core. Exclude post-hoc fields. | Two runs of one message disagree. |
| F14 | MEDIUM | 6 | "Hysteresis" is a static three-band split. No label gold set. `fine_cloud_allowed: false` is not in §3.9. Cache key omits recognizer hash and temperature handling. | `enricher.py:164-176`; `main.py:375-376`; `labels.yml:10-13`; §3.9 | CONFIRMED | Rename or add state. Bind cloud prompts to `cloud_policy`. Label a set before τ is a gate. | Fine sexual labels can enter a cloud prompt. τ is copied as science. |
| F15 | MEDIUM | 7 | RRF has no `k`, no depth, no `msg_id` collapse across stride-10 overlap. A citation may be 40 turns. | §3.8, §3.10; `chunker.py:156-178` | CONFIRMED gap; overlap CONFIRMED | Fix parameters. Collapse to message ids. Judged set is a P5 exit. | The model treats five copies of one message as corroboration. |
| F16 | MEDIUM | 9 | §3.2 points `path` at the member. Current Astral docs use `workspace = "<workspace root>"` for a cross-workspace source. Installed uv is 0.12.11 (2026-09-08); the doc page is dated 2026-10-20. | §3.2; this session's `uv --version`; §15 | PLAUSIBLE stale snippet. UNKNOWN on 0.12.11 | P0 runs both forms. Keep hatchling as a stated choice; both repos use it today. | dNh CI fails, or locks a path that moves. |
| F17 | MEDIUM | 12 | New coverage scope is right. Old fixtures as goldens will freeze bplist bodies, `msg_{rowid}`, and the 3000–3999 map. Today's omit list is the pipeline. | `pyproject.toml:193-218`; `imessage_test_data.sql:135-158`; §7–8 | CONFIRMED | New v2 goldens. Old tests are characterization tests until updated. Drop the `NotImplementedError` coverage exclusion. | CI goes green on the behavior v2 retires. |
| F18 | LOW | 4, 9 | §4 says both "JSONL then import" and "no file hand-offs." Core upper bounds will fight dNh's lower-only pins if the core grows a shared library. | §4; `dNh pyproject.toml:19` (`httpx>=0.28`). ChatX `httpx<0.28` is from evidence 01, not re-read this session | CONFIRMED for the two sentences and dNh's pin | JSONL is extractor output only. Core stays free of httpx, as §3.3 says. | A second JSONL bus recreates the v1 wrapper bug. |
| F19 | INFO | 6 | Coarse 55 and fine 99 are true under a parse. `schema_version: 1.2`. Severity "is not a clinical assessment." | `labels.yml:8,18-20`; this session's count | CONFIRMED | Publish counts in P4 (V7). Promote that sentence into the P6 contract. | Low if V7 runs. |
| F20 | INFO | 2 | 128-bit HMAC already exists. The dead extractor probes columns and selects `balloon_bundle_id`; its body decoder is still the plist heuristic. | `normalize.py:47-54`; `extractors/imessage.py:276-314`; `body_normalize.py:12-31` | CONFIRMED | Port the column probe. Leave the dead decoder. | Rebuilding a token that exists, and losing the one balloon-id select. |

## 3. Per-area deep dives

### 3.1 Canonical schema v2

v2 correctly takes ChatX's reactions, replies, attachments, outbound, and source path (`schemas/message.py:43-70`) and dNh's `extra=forbid`, frozen models, and aware UTC. It is not yet implementable: each field needs a source rule.

The live query reads `ROWID`, `guid`, `text`, `attributedBody`, `is_from_me`, `service`, `date`, `handle_id`, handle id, chat guid, `associated_message_guid`, `associated_message_type` (`extract.py:88-108`). The fixture matches that world and adds `date_edited`, `cache_has_attachments`, `balloon_bundle_id` (`imessage_test_data.sql:5-19`).

| Source fact | v2 home | On disk |
|---|---|---|
| `handle_id`, `is_from_me` | `sender.handle`, `direction` | Selected. Outbound becomes `"Me"` (`extract.py:152-154`). Account is unread. `direction=system` has no tie to `item_type`. |
| `date` | `sent_at` | Selected. Failure becomes now (F6). |
| `date_read`, `date_delivered` | Absent | Unselected. Cannot be rebuilt from `text`. |
| `date_edited`, `date_retracted`, prior text | `edit.*` | Unselected. Prior text is a `message_summary_info` blob. Secondary sources disagree on whether Sequoia uses `date_retracted` (§15). Empty list vs null changes `content_hash`. |
| Associated guid/type | reactions, `reply_to_msg_id` | Selected. Match is raw equality (`extract.py:229`). `is_reply` is type 0 plus a guid (`reactions.py:72`), which the fixture uses (`imessage_test_data.sql:81-83`). |
| `thread_originator_guid` | Named in §3.4 | Unselected. |
| `balloon_bundle_id`, `payload_data` | Absent | Dead extractor selects the balloon (`extractors/imessage.py:314`). Link previews and locations need it. |
| `item_type`, `group_action_type` | `content_kind=system` only | Unselected. Participant changes need actor, action, target. |
| `service`, `account` | `platform` includes `sms` | `service` goes to `source_meta` (`extract.py:201`); platform is hardcoded (`:186`). RCS is a value a 2026 forensics note names (§15). |
| Stickers, audio, location | kind enums only | No rule for associated type 1000 (PLAUSIBLE from a public reader). `is_audio_message` unread. |
| Instagram | `platform=instagram` | Reads `content`, photos, videos, audio, reactions (`instagram/extract.py:70-96`). Shares, gifs, files, calls unread. `source_meta` stores key names (`:118`). Mojibake is promised in §4 and absent in this reader. |
| WhatsApp | V6 for timezone | System lines, including deletes, are dropped (`whatsapp_export.py:33-49,196-198`). Times are forced to UTC (`:192`). |

Ids in the wild: ChatX `msg_{rowid}` (`extract.py:184`); dNh guid or `rowid:{n}` (`imessage_mapper.py:17`); Instagram `ig:{thread}:{ts}:{idx}` (`instagram/extract.py:103`); WhatsApp a content hash. v2's `sha256(...)[:32]` is 128 bits and includes `text`, so an edit mints a new id and identical texts at the same timestamp collide. `tests/imessage/` holds 30 Python files (this session's count; the design's "35" was not reproduced).

`content_hash` excludes `source_meta` and `provenance` and does not specify key order, Unicode, or null-vs-omit. `sender.pseudonym` is filled later and would sit inside the hash. dNh already canonicalizes JSON (`idempotency.py:10-16`) over a fixed field list (`dedupe.py:15-24`).

Versioning is a literal plus "a migration note" (§5). `schema_migrations` is SQL. The generated-schema test is worth keeping; it fixes the v1 required-field drift. It does not version stored rows.

§9 maps a handful of fields and says reactions and replies "may ignore." Also unmapped: `text_source`, edits, attachment hash, source path. Evidence 02's dNh `Direction` and `Channel` enums have no `system`, Instagram, or PDF. "Lossless" needs a loss table and one fixture per kind. This session confirmed the inbound classifier; the full enum list is evidence 02's, spot-checked only where cited.

### 3.2 Extraction correctness

| Concern | Start from | Still missing |
|---|---|---|
| typedstream | dNh `decode_imessage_attributed_body` | Two layouts (`imessage_attributed_body.py:69-80`), header check (`:26`), unwired (`:14-16`), 256 KB/64 KB (`:23-24`), back-references refused (`:33-37`). ChatX tries `bplist00` then UTF-8 (`body_normalize.py:12-31`). V2's probe is the right next step. The 1013-line test file was not re-read. |
| Apple epoch | dNh raises; ChatX documents magnitudes | ChatX bounds 1999–2100 and the caller substitutes now. dNh takes the first in-range candidate across Apple and Unix divisors (`imessage_mapper.py:41-56`), so two divisors can both "succeed." |
| WAL | Neither | F5 vs dNh's live `mode=ro` (`imessage_source.py:140`), which can see the WAL and can fail under Messages' lock. |
| Manifest.db | ChatX `backup.py` | Password string is checked (`backup.py:178-188`); nothing decrypts. Design §3.13 is right to remove the flag. FileID lookup is two SQL shapes and `xx/fileID` (`:113-131`). |
| Attachment bytes | ChatX | `sha256_stream` (`media/hash.py:9`), HEIC maps (`attachments.py:19-20`, `media/sniff.py:63-65`), optional `pillow_heif` (`media/exif.py:8-11`). dNh stores the attachment id as the storage ref (`imessage_mapper.py:30-34`). The backup path walker was not re-read past Manifest lookup. |
| Reactions and outbound | ChatX structure | dNh appends `not_inbound` (`imessage_source.py:57-58`) and the latest-row query requires non-empty `text` (`:119-121`). ChatX scope bug: `handle_id IN (...) OR is_from_me = 1` (`extract.py:384-386`). Design names it. |
| Participants | Neither | Chunker collapse is F8. v2's `participants` table has no `chat_handle_join` rule. |
| Email | dNh `email_eml.py` (297 lines) | MIME walk not re-read. P1 needs a golden multipart, missing Message-ID, and odd charset. |
| PDF | ChatX reader, defects unnamed | `platform="imessage"`, timestamps `now()` plus one second (`pdf_ingest/reader.py:68-102`). |

### 3.3 Policy Shield v2

Presidio is a reasonable framework on the docs fetched 2026-10-20: analyzer, anonymizer, custom recognizers, and a documented `GLiNERRecognizer` sample using `urchade/gliner_multi_pii-v1`. spaCy as the default will miss bare names on short turns. The design already lets the eval pick the engine (V3). That split is right. The metric is the problem.

The synthetic-plus-gitignored-real shape is right if the generator is frozen before recognizer tuning, the class list is closed (R19), and names and handles are in the set. Locales are unspecified; the current hard-fail block is a few English keyword regexes (`patterns.py:163-176`). 0.995 on PERSON may be unreachable. Missing it, with cloud left disabled, should be a passing P3 (F10). §12.3's "say synthetic-only" must stay.

Gate holes, in the design's own order:

1. Version-pinned eval reports are right. "Classes present in the case" lets a run with no detected phones skip the phone target. A laptop failure on real text must not be washed out by a synthetic CI pass.
2. "Block the run" corrects today's code: `block_hard_fail` raises (`policy_shield.py:182-183`), the loop swallows it, drops the chunk, and leaves `hardfail_triggered` false (`:265-269`). The class list is still the demo set unless replaced. Do not log the matching span.
3. With a perfect oracle and zero finds, a 95% upper bound is about `3/n`. `n=600` is about 0.5%; `n=3000` is about 0.1%. The local model is not that oracle. The check can stay as a spot check.
4. No attachment field on the cloud type is necessary. Filenames, OCR, EXIF, paths, and `meta.contact` are still text (`chunker.py:166-174`).

HMAC-SHA256 with a per-case salt is sound for minting tokens. `normalize.py` already truncates to 128 bits and writes a 32-byte key with the process umask, including `~/.chatx_salt` (`:19-64`). §8's "add 128-bit" is done. §8 does not say "retire the global salt"; §3.7 does. The reversible map is a codebook: HMAC stops guessing only for an attacker who lacks the file. Export, Time Machine, and iCloud copies of the sqlite file rehydrate everything. Cloud requests must exclude the map. Paraphrases that drop tokens break "token-preserving" round-trip; the design has no echo check.

Redact per message, render the chunk from redacted text, then scan the chunk for spans the joiner created.

### 3.4 Storage

SQLite, FTS5, in-process vectors, and content-addressed files match a single user and match dNh. Rejecting Postgres is sound.

sqlite-vec's author reported, for v0.1.0, sub-100 ms KNN around 100k vectors at dimensions at or below 1024, and at 1M no float dimension he tried met 100 ms. A later DiskANN pull request on that project shows a 1M flat query around 590 ms on an M4 and a long build. He says not to treat the numbers as gospel. They are enough to refuse an implied "several million chunks" default at `float[1024]`. One million float32×1024 vectors are about 4 GiB before SQLite overhead. Partition keys want hundreds of rows per key (vec0 docs). V4 is the right status. P5 should record dimension, N, RSS, and p95 on this Mac.

DDL still open: message primary key; guid uniqueness on re-import; reactions as rows or JSON; whether FTS indexes raw text, redacted text, or both; tombstones for retracts; WAL and `busy_timeout` when import and query or MCP overlap.

G3 says one file. The layout is a directory. Restore is a tree copy after a checkpoint. CAS paths are right; add mode `0700`/`0600`, symlink refusal, and "HEIC stays original bytes so the hash stays the source hash." A zip plus an internal sha256 list detects corruption. It becomes custody only with operator, tool version, source-db hash, and a manifest anchor outside the zip. `obs/run_artifacts.py` already hashes the input db (grep at `:44-46`). Reserve "forensic" for that provenance. Default the case root under Application Support, not the cwd.

### 3.5 Providers

Config-held model ids, plus requested and observed identity stored separately, match real failures (`gemma2:9b-instruct-q4_K_M`, `claude-3-sonnet-20240229`). V9 is right. UNKNOWN must stay UNKNOWN when a local server echoes the requested name while serving other weights.

OpenAI-compatible `format=json` and Anthropic `output_config.format` are different contracts. Fetched Anthropic docs describe grammar-constrained JSON, a first-call compile, and a grammar cache. The protocol returns a `BaseModel` only: no usage, no timeout, no 429-vs-400 split. One retry then quarantine (§3.6) stores a second copy of model output. Cap quarantine and keep it out of exports.

`temperature=0.0` and `seed=42` read as a promise. Record accepted, ignored, or rejected per parameter, and put that flag in the cache key.

Embeddings stay on a local OpenAI-compatible server unless a separate host passes the same gate. Voyage, named by Anthropic's embeddings page, is another cloud processor. Apple-silicon serving is correctly left as "whatever `providers list` shows." P5 RSS must include the model server. Appendix A.4's Ollama path was not re-checked.

### 3.6 Enrichment and taxonomy

`labels.yml` is real: schema 1.2, 55 coarse leaves, 99 fine leaves, `fine_cloud_allowed: false`, severity "not a clinical assessment" (`labels.yml:8-20,307-323`). Bind the cloud prompt to that policy. The fine set includes sexual practice and sex-trade detail.

`ConfidenceGate` compares one number to three thresholds (`enricher.py:167-176`). There is no previous decision. Keeping 0.70/0.62/0.78 as recorded starting values is fair. Calling it hysteresis will send a later reader looking for state.

The cache tuple in §3.9 needs recognizer-config hash, the temperature-handling flag, and observed model id. V7 counts keys. P4's exit is "visible to query." A few hundred owner-labelled chunks are the minimum before τ is more than a knob. Until then the UI says unverified.

Enum-only cloud output with `extra=forbid` limits prompt injection. A free-text rationale reopens it. Enrich message ids; the current enricher re-parses display lines (evidence 01; that function was not re-read). Input tokens are uncapped; a 40-turn chunk plus the taxonomy dwarfs `max_output_tokens=800`.

### 3.7 Search and query

BM25 plus vectors plus RRF is a sound default once `k`, depth, and filters (`conv_id`, time, platform) exist. Stride 10 inside a window of 40 repeats `msg_id`s (`chunker.py:156-178`). Collapse to message ids before fusion so repetition is not corroboration. Cite the messages actually quoted. A top-k fixture does not test that. Run the user's question through the redactor before a cloud query; the question is a new document.

### 3.8 Analysis lane

SQLite rows from rules, without Neo4j, match the evidence that `storage/graph.py` is dead to the CLI. The names are the asset and they are not neutral: `SEXUAL_ESCALATES`, `CONSENT_VIOLATES`, `GASLIGHTS`, `MANIPULATES`, `NEGOTIATES_SERVICE` (`storage/base.py:224-285`). Store them as hypotheses with rule id and supporting `msg_id`s, local-only, off by default, out of the default bundle. The category comment on service negotiation is part of the meaning; a YAML port should keep it or drop the type. `mental-bert` behind an ADR is the right strength; a Hugging Face download is a supply-chain event (evidence 01; `embeddings/psychology.py` not re-opened). Image and audio stay behind their own ADRs. Encrypted backups are extraction work, not this lane.

### 3.9 Workspace and packaging

A new repo matches the debris evidence 01 describes. Python `>=3.12` matches dNh (`pyproject.toml:5`) and raises ChatX from `>=3.11` (`pyproject.toml:11`). Hatchling is what both packages use (`dNh pyproject.toml:64-66`). uv's current `uv init` template defaults apps to `uv_build`; staying on hatchling should be a written choice.

The §3.2 snippet uses `path` to the member with `editable=true`. Astral's workspaces page says a cross-workspace source is `workspace="<root>"` so uv picks the member by name. Ordinary path sources still exist. Two lockfiles are normal. P0 has to try the written snippet on uv 0.12.11, from a second checkout, and record which form resolves (F16, V8). Upper bounds are cheap only while the core stays free of httpx and the LLM stack (§3.3).

CI gates named in §7 are the right set once one audit command is chosen. The no-socket test enforces the core rule. It does not stop Presidio or spaCy from downloading weights on first use. Pin those hashes.

`~/code` having no `pyproject` is an Appendix A.4 claim this session did not re-stat. UNKNOWN, and cheap to re-check.

### 3.10 Phase plan

Store before shield is justified. The missing early phase is a spike that publishes, before goldens exist: typedstream status counts (V2); reaction histogram including prefixes (V1); whether `date_retracted` is non-zero here; a local note on `message_summary_info`; service counts. P1 currently freezes the schema in the same exit as "V1 resolved."

P0 is appropriately thin. P2's 100k measurement is real and should include a killed-process `case verify`. P3 should treat "targets missed, exit 2" as success. P4's recorded responses are right; add fixtures for invalid JSON, refusal, 429, and temperature rejected. P5 needs the judged set and the vec0 page. P6 should not hold decrypt. P7's generated docs are right; MCP needs F7.

"Smoke run documented with counts" needs the count list: messages, empty text, decoded, unsupported, reactions attached, reactions orphaned, attachments missing.

### 3.11 Threat model

§3.13 covers env secrets, no sockets in the core, and a read-only `chat.db`. Unaddressed:

| Threat | Exposure | Mitigation |
|---|---|---|
| Same-user local attacker | Plaintext sqlite plus the map | Write down that the case directory is the trust boundary. Mode `0700`. |
| Other local users | Umask on salt and temp | `0600` salt, `0700` temp, refuse a group-readable case. |
| "Local" base URL | F7 | Loopback allowlist. |
| MCP host | P7 | Redacted tools, or a local host only. |
| Provider retention | Grammar cache up to 24h is in the fetched structured-output/strict-tool docs. Default body retention was not fully read | Read the current retention page before `--allow-cloud` exists. Record the account setting. |
| Voyage or any other embedder | Unnamed if `embed()` is "just the provider" | New host, same gate. |
| Logs | "No secrets" allows message bodies and hard-fail spans | Log ids and counts. |
| Crash reports | Exception strings can capture bytes | Class name only, as today's raise roughly does. |
| Temp `chat.db` | `TemporaryDirectory` (`db.py:25-29`) deletes on clean exit | `0700`, `finally`, parent outside the cwd. |
| Swap | Ordinary files | FileVault as an owner-confirmed assumption. |
| Spotlight, iCloud, Time Machine | Relative `cases/` follows cwd | Default root under Application Support. Time Machine is an owner opt-in, documented. Spotlight's behavior on sqlite: UNKNOWN until tested. |
| Quarantine | Raw model output | Sensitive, size-capped, out of the export. |
| Embedding inversion | Vectors of raw text | Embed redacted text only. |
| Downloaded weights and sqlite-vec | Native code in the process that holds text. dNh pins `sqlite-vec>=0.1.6` with no upper bound (`pyproject.toml:58`) | Lockfile, hash pin, one failing audit command. Telemetry of Presidio, spaCy, Typer: UNKNOWN until their current docs are read. |
| Prompt injection via tools | Message text instructing a tool-using model | No tools on the P4 cloud schema. |

### 3.12 Testing

`imessage_test_data.sql` teaches the old extractor and certifies the wrong body decoder: `bplist00` blobs (`:139-140`), bare-guid tapbacks (`:86-90`), type-0 replies (`:81-83`), no removal, no `p:0/` prefix, no group action. dNh's synthetic typedstream bytes are the better pattern (evidence 02's description of prefix constants; test body not re-read).

Property tests in §7 need an oracle: seconds, microseconds, and nanoseconds in 2004–2030 round-trip; `0` and `None` quarantine; out-of-band values quarantine; a handle table for E.164 and email. Align bounds with F6.

Contract fixtures should include invalid JSON, schema failure, refusal, 429, and a rejected temperature. One test must keep an observed model id that differs from the request.

Real blobs stay gitignored. The probe prints counts and format classes. CI uses synthetic `streamtyped` only.

The 90% gate is real only with an empty omit list. Today's omit drops redaction, transformers, enrichment, indexing, the validator, and local whisper (`pyproject.toml:196-207`). `exclude_lines` also skips `NotImplementedError` (`:209-218`). Line coverage will not catch the WAL bug or the guid prefix. Those need their own tests. Evidence 01 says the chunker and enricher lack direct tests; that claim was not re-audited file by file.

### 3.13 Omissions

A user of this tool also needs, and the design does not specify: an absolute case root; re-import rules; merging a phone and an email into one person; merging two Macs that share guids; how to destroy a case including WAL, logs, temp, and salt (APFS erase is best-effort); what happens when the salt is lost and the map remains; redaction of outbound text that quotes the other person; RCS; link-preview URLs as data and as PII; locales beyond US-shaped patterns; an input-token cap; which `embedding_spaces` row a query uses; empty-index and dimension-mismatch behavior; and a sentence that the archive contains other people's words, so the export is a disclosure. PDF already shows how `sent_at` becomes extract time (`pdf_ingest/reader.py:68-102`).

### 3.14 Intent reconciliation

The owner's ruling stands: old docs are inspiration. Silent cuts are how the next session resurrects them. Add to §2's non-goals, each of which evidence 03 marks ABSENT or DEAD and §2 does not name:

- HTTP `/v1/query|simulate|reply`, and CLI twins of `simulate` and `reply`. §2 already bars an HTTP API.
- `timeline`, `factors`, `tokens inspect`, `backfill`. The shield replaces a separate `preflight cloud`.
- Differential privacy. Already a non-goal. Keep it.
- The *capabilities* behind Chroma, Neo4j, multi-vector psychology search, and default `mental-bert`, not only the libraries. §3.14 retires the code.
- WhatsApp JSON. The design takes dNh's text export. Old IFC said JSON/TXT must parse.
- Generic TXT, iCloud download automation, and a shipped PDF OCR engine. §4's "hook, no engine" should also be a non-goal.
- Numeric SLAs (10k msg/min, p95 150 ms, <4 GB, cache-hit 0.80, QPS flags, checkpoint-every-10k) until measured twice. §7 implies this; §2 does not say it.
- The error shape `error, code, detail, hint`. §3.12 picks RFC-7807 plus `E_<SNAKE>` and exit 2 for the gate. Exit 2 is a change from ADR-0018's exit 1 and should be labelled a change.

Kept, and the evidence undermines the claim as carried forward:

- 90% coverage, which today omits the pipeline (F17).
- 0.995/0.999, which today gate a ratio that exits 0 (F1). The numbers can stay. The implication "safe for cloud" cannot.
- τ 0.70/0.62/0.78 and the word hysteresis (F14).
- Relationship types as portable facts (F10). Port the YAML as hypotheses.
- `⟦TKN:<id8>⟧`, which is the old docs' token and fights 128-bit (F3).
- Turns 40 / stride 10. The code does this and collapses senders. The design fixes the collapse and keeps the overlap (F15).
- "Attachments never uploaded," true today because no cloud client exists (evidence 03). The new client makes it a test, and filenames remain text (F8).

Resolved contradictions worth one winner-table so they are not re-litigated: temperature (design picks 0.0, which then hits F2); coverage floor (90 on the whole package); query latency (no SLA); run-report filenames (`manifest.json`, `run_report.json`, `metrics.jsonl`).

### 3.15 Ecosystem currency

Fetched 2026-10-20.

**Model ids.** Official model-id docs describe `claude-{name}-{major}-{minor}` from the 4.6 generation on. System-card index and catalogs fetched the same day list `claude-sonnet-5-5` and `claude-opus-5-5`. The design's examples match that shape. Confidence high for the fetch date; confirm with one authenticated call before locking a default. `providers list` on localhost will not enumerate Anthropic ids.

**Temperature and structured output.** Fetched API text: models after Opus 4.6 reject `temperature` other than `1.0`; historical 0.0 was documented as not fully deterministic. Structured outputs use `output_config.format` on a stated model list, with first-request grammar compile. Prefill is unsupported on several recent models. Confidence high on those sentences; re-check the exact model.

**Embeddings.** Official page: Anthropic does not offer an embedding model and documents Voyage (Voyage 4 family, several dimensions including 1024) as a separate API. Confidence high. Secondary price blogs were not copied.

**Presidio.** Still the framework, with a GLiNER sample. Confidence high that the sample exists; low that any named model hits 0.995 on chat names. V3 stays a measurement.

**sqlite-vec.** vec0 docs cover metadata columns and partition-key limits. Scale evidence is the author's 2024 post and DiskANN PR #278. A 2026 article claiming millisecond search over a billion vectors was rejected as uncorroborated. Confidence medium that 1M float vectors are a problem; low on any millisecond figure.

**uv.** Fetched workspaces docs describe `workspace="<external root>"` and ordinary path dependencies. Installed binary is 0.12.11, built 2026-09-08. Match to the 2026-10-20 wording: UNKNOWN (F16).

**iMessage.** No Apple schema was fetched. A forensics field guide, `imessage-chatdb`, the Rust `imessage-database` crate, and an unsend note agree on nanoseconds since 2001-01-01 (older rows in seconds), tapback adds 2000–2005, removals 3000–3005, emoji often 2006/3006, guid prefixes, and `message_summary_info` for edits. They disagree on `date_retracted` by OS. Confidence medium. Extend V1's "count a real db" posture to unsends.

**Local servers.** Ollama, LM Studio/MLX, vLLM, and llama.cpp remain the right family. Nothing was benchmarked here.

**Already retired correctly.** `claude-3-sonnet-20240229`, default `all-MiniLM-L6-v2`, Chroma, Neo4j. Nothing fetched makes SQLite plus FTS a superseded single-user choice.

## 4. Decision challenges

**DC1. Shared core (owner).** Keep it. The parsers have already split: typedstream in one repo, reactions in the other. The corollary to drop is "one core means one lossless envelope." A silent lossy adapter hides edits from dNh. Growing dNh's frozen event schema for every v2 field is a dNh migration. Settle it with a loss table and a fixture.

**DC2. Separate repo and path dependency (owner).** Keep the repo. Challenge the syntax and the coupling. A relative editable path means every dNh checkout needs `chatstack` beside it, and a core break lands immediately. A tagged wheel adds a release step and lets dNh lag. P0 on a clean second checkout, plus one intentional breaking field, settles it. If the path form fails on uv 0.12.11, try `workspace="../chatstack"` before a third invention.

**DC3. SQLite + sqlite-vec + FTS5 (owner).** Keep SQLite and FTS5. Challenge vec0 as a same-phase default at 1024-d and "several million" rows. Wrong toward vec0: RSS and a later migration. Wrong toward FTS-first: semantic search slips a phase, keyword search still ships. Settle with the P5 page on this Mac at 100k and 1M, one small dimension and one 1024-d model.

**DC4. Two implementations, one interface (owner).** Keep config-held ids and OpenAI-compatible local chat. Challenge `embed` and `temperature` on the Anthropic class. One protocol 400s or grows a hidden Voyage dependency. Two protocols are more code and a clearer gate. Settle with one recorded Anthropic structured-output response under the temperature policy you actually send, and a host allowlist for embeddings.

**DC5. Docs are inspiration (owner).** Keep. Add the §3.14 non-goals so evidence 03 is not rebuilt as HTTP, Neo4j, and DP. No further evidence is needed.

**DC6. Case layout (owner).** Keep the directory and CAS files. Challenge the words "single-file," the missing salt and map locations, and a cwd-relative root. One sqlite file would put attachments back into BLOBs, which you already rejected. Settle with a P2 restore drill and a default root that is not an iCloud path.

**DC7. Keep `db.py` behavior (designer, §3.13).** Do not keep it as written. `immutable=1` drops WAL frames (F5). The cost of keeping it is a successful run that missed messages. The cost of the backup API is a small rewrite and a test with an uncheckpointed frame. That test settles it.

## 5. What the design gets right

- The diagnosis matches the code: extraction is real; coverage is a token ratio (`policy_shield.py:138-157`); `--allow-cloud` forces local (`cli/main.py:411-413`).
- One case database removes the `{"messages": ...}` versus bare-list break.
- dNh's typedstream parser replaces the plist heuristic, and V2 refuses to treat two layouts as complete.
- The `is_from_me OR` scope bug and the group-sender collapse are named.
- 3000–3005 as removals corrects `reactions.py` if §3.4 wins. Leaving 2006/3006 UNKNOWN is the right posture and should be copied for unsends.
- V6 refuses to guess WhatsApp zones, against dNh's `replace(tzinfo=UTC)`.
- Attachments are hashed files, not BLOBs and not upload fields.
- Model ids leave the source. Requested and observed identity stay distinct.
- Coverage is defined on the whole package. The current omit list shows why.
- Encrypted backups stay out until decryption exists. Today's flag checks a password string (`backup.py:185-188`).
- Perf numbers become measurements instead of conflicting SLAs.
- Chroma, Neo4j, differential privacy, and image-enricher placeholders are retired as code.
- The core's no-network rule has a test.
- Telegram and BlueBubbles stay in dNh. The core stays batch and export oriented.
- §12.3 forces shield reports to say whether real labels exist.
- `labels.yml` is kept as data, including the non-clinical sentence P6 should promote.

## 6. Open questions for the owner

1. **Cloud, given F1.** If entity recall is the only shield measurement, is cloud enrichment still a goal, or does cloud stay disabled until you accept the residual risk in writing? That keeps or deletes P4's Anthropic path.
2. **Case grain.** "One case per import set" still means either one directory for the whole archive or one directory per import. Search, salt, and the bundle follow the choice.
3. **Real shield labels.** Confirm that synthetic-only reports are acceptable for any later cloud use. §12.3 already requires the report to say so.
4. **Git history.** Clean repo versus carried history. Decide before P0 creates the remote. It does not change the schema.
5. **Where inferred psychology may go.** "Nowhere by default" keeps P6 tables out of `export bundle`. Including them changes what §1's forensic bundle is, and the UI has to say so.
6. **FileVault and Time Machine.** Is disk encryption the assumed control, and do backups include cases? That picks the P2 root and backup story.
7. **Anthropic retention.** Ordinary retention or a zero-data-retention arrangement? The grammar-cache note means the current retention page still has to be read. P4 waits on the answer.

## 7. Verification log

**Read in full:** the design; evidence 01, 02, and 03. Specs copy compared by hash.

**ChatX ranges read:** `imessage/extract.py` (query, ids, scope); `time.py`; `db.py`; `reactions.py`; `body_normalize.py`; `backup.py`; `schemas/message.py`; `identity/normalize.py`; `redaction/patterns.py` (hard-fail, tokenizer); `redaction/policy_shield.py` (coverage through the chunk loop); `transformers/chunker.py` (turns); `instagram/extract.py`; `pdf_ingest/reader.py`; `cli/main.py` (cloud flag, τ); `enrichment/enricher.py` (gate); `storage/base.py` (relationship constants through the service-negotiation category); `config/labels.yml` (head, fine section, and a full count); `pyproject.toml` (Python floor and coverage); `tests/fixtures/imessage_test_data.sql`; `extractors/imessage.py` (column probe). Grep-level: `media/sniff.py`, `media/hash.py`, `media/exif.py`, HEIC maps in `attachments.py`, db hash in `obs/run_artifacts.py`.

**dNh ranges read:** `imessage_attributed_body.py` through the payload walk; `imessage_mapper.py`; `imessage_source.py` (classifier, latest query, scan, attachment helper start); `whatsapp_export.py` (markers, flush, system check); `dedupe.py`; `idempotency.py`; `migrations.py` vector and FTS DDL; `pyproject.toml` head and retrieval extra.

**Commands:** `wc -l` on the four inputs; `git rev-parse`, branch, and status in both repos; `shasum -a 256` on both design copies; `uv --version`; Python count of label leaves; `find` for fixture databases (none) and `tests/imessage/*.py` (30); `wc -l` on the dNh parsers. No pytest. Web search only for item 15.

**Pages used:** Claude model-id docs, system-card index, structured outputs, messages/completions temperature text, strict-tool retention note, embeddings page; Presidio entity list and GLiNER sample; sqlite-vec vec0 docs, Alex Garcia's v0.1.0 post, sqlite-vec PR #278; Astral uv workspaces and dependency docs; SQLite URI docs and the Midnight Commander note that `immutable=1` skips an uncheckpointed WAL; secondary iMessage notes (`macforensics.app` chat.db article, `imessage-chatdb` README, Rust `imessage-database` docs, `imessage-unsent` Sequoia note). A sqlite-vec "billion vectors" article was retrieved and rejected.

**UNKNOWN:** training cutoff; whether uv 0.12.11 accepts either source form; default Anthropic body retention; `date_retracted` on the owner's Mac; real typedstream coverage; whether `~/code` has a `pyproject.toml`; Ollama's presence; `email_eml.py` MIME behavior; the rest of `attachments.py`; the enricher's line parser; the 1013-line typedstream tests; Spotlight on a sqlite case; telemetry of current Presidio, spaCy, Typer, and sqlite-vec; dNh's Qdrant use; the ChatX `httpx` pin line (taken from evidence 01).

**Unverified impressions**

- A global salt plus a reversible map will show up the first time two cases are diffed, because the same handle mints the same token.
- Removing unimplemented `semantic` chunking is the right cut even if a demo later asks for the word.
- "Evidence-grade" in §1 will be quoted at the author the first time a bundle is handed to someone else. An integrity manifest will not satisfy that reader.
- Porting relationship names without the sex-work category comment (`storage/base.py` around the `NEGOTIATES_SERVICE` block) strips the only scope hint. Keep the note or drop the types.
