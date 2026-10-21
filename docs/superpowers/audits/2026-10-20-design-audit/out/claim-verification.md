# claim-verification
Runner: sonnet-verify | Model: Sonnet 5.5 (claude-sonnet-5-5 as stated in system prompt; no runtime receipt) | Date: 2026-10-20 | Tool calls: ~35 (limit 300)

Conventions: ChatX = /Users/hue/code/Dopemux-ChatRipperXXX (HEAD 9c3dd6b); dNh = /Users/hue/code/dNh_CRM. Citations to external URLs and to Grok's own "§15" (its ecosystem-currency deep dive, not a design section) were not fetched, so any claim resting only on them is UNKNOWN. Where a row mixes verified repo/design lines with an unfetched URL, Result reflects the repo/design lines and the note says so.

## Summary

| Auditor | Rows | PASS | PARTIAL | FAIL | UNKNOWN | NOT_RUN |
|---|---|---|---|---|---|---|
| codex | 30 | 26 | 0 | 0 | 4 | 0 |
| grok | 20 | 17 | 1 | 0 | 2 | 0 |
| agy | 25 | 17 | 8 | 0 | 0 | 0 |
| total | 75 | 60 | 9 | 0 | 6 | 0 |

## codex (F01-F30)

| ID | Sev | Verdict | Citations checked | Result | Note |
|---|---|---|---|---|---|
| F01 | HIGH | CONFIRMED | §3.4; ChatX extract.py:88-108 | PASS | SELECT lists only 12 columns ("m.associated_message_type"); §3.4 line 123 source_meta "never required". |
| F02 | HIGH | CONFIRMED | §3.4 msg_id, content_hash, sender, attachments | PASS | Line 108 derived id hashes `text`; line 122 hash excludes only source_meta/provenance. |
| F03 | HIGH | CONFIRMED | §3.4, V6; dNh whatsapp_export.py:177-193 | PASS | `return parsed.replace(tzinfo=UTC)` at 192 vs design "never silently UTC" (V6). |
| F04 | HIGH | CONFIRMED | §9; dNh normalizer.py:26-47; dedupe.py:15-25 | PASS | normalizer hardcodes `Direction.INBOUND`; dedupe hash formula at 15-24 differs from §9 content_hash. |
| F05 | HIGH | CONFIRMED | §3.13; ChatX db.py:25-43 | PASS | `shutil.copy2` of db, then wal, then shm sequentially; §3.13 "WAL-safe copy". |
| F06 | HIGH | CONFIRMED | §8, V1-V2; dNh imessage_attributed_body.py:69-80; ChatX reactions.py:33-37 | PASS | Two pinned layouts in `_ALLOWED_LAYOUTS`; "3000 <= type <= 3999: return custom". |
| F07 | HIGH | CONFIRMED | ChatX extract.py:283-286; attachments.py:97-124; backup.py:129-147; §8 | PASS | Caller passes (attachments, out_dir, dedupe_map) without backup_dir though param exists (attachments.py:220). |
| F08 | HIGH | CONFIRMED | dNh whatsapp_export.py:33-49,105-108,196-198; ChatX pdf_ingest/reader.py:68-102; §8 | PASS | `any(marker in normalized ...)` with "added"/"left"; reader.py `platform="imessage"`, `base_ts = now`. |
| F09 | BLOCKER | CONFIRMED | §3.7, §6 P3, §12.3 | PASS | Line 190 targets on "synthetic set in CI"; P3 exit "synthetic set"; §12.3 owner labels open. |
| F10 | BLOCKER | CONFIRMED | §3.6-3.7, §5.4; Ollama URL | PASS | §5.4 gate token only at construction. Ollama docs URL not fetched (UNKNOWN part). |
| F11 | HIGH | CONFIRMED | §3.7; normalize.py:47-64; patterns.py:227-234 | PASS | §3.7 `<id8>` vs "128-bit"; patterns.py `hexdigest()[:8]`; normalize `mac[:32]`; salt written without chmod. |
| F12 | HIGH | CONFIRMED | §3.5, §6 P2, §7 | PASS | No transaction/writer/recovery language in cited sections; DDL "is the builder's" (line 142). |
| F13 | HIGH | CONFIRMED | §6 P2/P5, V4; dNh migrations.py:197-237 | PASS | P2 exit "100k synthetic"; `vec0(... embedding float[1024]`. Million-chunk behaviour itself not testable by reading. |
| F14 | HIGH | CONFIRMED | §3.5, §3.10; attachments.py:246-269 | PASS | `shutil.copy2(source_path, dest_path)` direct to final path, no temp+rename; §3.10 "zip + sha256 manifest". |
| F15 | HIGH | CONFIRMED | §3.6; Anthropic embeddings URL | UNKNOWN | §3.6 protocol has `embed()` and AnthropicProvider (lines 150,156); provider capability claim needs external doc. |
| F16 | HIGH | CONFIRMED | §3.6-3.9; structured-outputs URL | PASS | Only "retried once then quarantined" (157); no timeout/usage semantics. URL not fetched. |
| F17 | HIGH | CONFIRMED | labels.yml:191-238,248-285,307-425; §3.9 | PASS | Coarse section includes substance/kink/orientation labels (e.g. `kink_context`, `orientation_context`). |
| F18 | MEDIUM | CONFIRMED | enricher.py:164-176; §3.9 | PASS | Per-item threshold compare, no state; §3.9 cache key tuple at line 209. |
| F19 | HIGH | CONFIRMED | §3.10; vector_store.py:170-181,329-335 | PASS | Metadata holds message_count not ids at 176; result ids read from metadata at 334. |
| F20 | HIGH | CONFIRMED | §3.11; psychology_relationship_mapper.py:67-94 | PASS | Set-intersection rule matching, fixed base confidence + overlap bonus. |
| F21 | HIGH | CONFIRMED | §3.2, §5.1, V8 | PASS | Line 85 `path = ..., editable = true`; §5.1 "dNh pins the version" (version string only). |
| F22 | MEDIUM | CONFIRMED | pyproject.toml:121-130; validator.py:14-36; §3.3-3.4 | PASS | Wheel packages only `src/chatx`; SCHEMA_DIR = `Path(__file__).parent x4 / "schemas"`. |
| F23 | HIGH | CONFIRMED | §3.7-3.10, §4, §6 | PASS | §3.7 item 3 needs local provider; providers land in P4 after P3; no phase lists chunking. |
| F24 | HIGH | CONFIRMED | §3.5, §3.13, §7 | PASS | No threat-model or file-permission section beyond salt 0600 (line 184). |
| F25 | HIGH | CONFIRMED | pyproject.toml:187-206; test_db_copy.py:38-50; dNh test_imessage_real_source_ingest.py:13-41 | PASS | omit list lists redaction/*, enrichment/*; test writes `"fake db"`; dNh test builds minimal 5-table schema. |
| F26 | MEDIUM | CONFIRMED | §3.12, §6-7 | PASS | CLI tree has no resume/delete/repair commands. |
| F27 | MEDIUM | CONFIRMED | §2, §3.12; docs/interfaces.md:48-62,281-298; NFR.md:44,111,142 | PASS | Old docs list `backfill`, `simulate`, `reply`, `index update`; NFR:44 "1M-message corpus". |
| F28 | HIGH | CONFIRMED | §3.3, §3.5; sqlite.org URL | UNKNOWN | Design states no SQLite minimum version (§3.3 lines 93-97); WAL-reset bug claim is external. |
| F29 | MEDIUM | CONFIRMED | §3.7; Presidio FAQ; OpenAI Privacy Filter | UNKNOWN | §3.7 line 182 names Presidio; stewardship/model-comparison claims external. |
| F30 | LOW | CONFIRMED | §3.12; RFC 9457 URL | UNKNOWN | §3.12 line 226 says "RFC-7807"; supersession by 9457 is external. |

## grok (F1-F20)

| ID | Sev | Verdict | Citations checked | Result | Note |
|---|---|---|---|---|---|
| F1 | BLOCKER | CONFIRMED | §1 bullet 3; §3.7; policy_shield.py:138-157; labels.yml:307-308 | PASS | `(total_tokens - pii_tokens) / total_tokens`; labels "NEVER leave device"; §1 line 30 "measured recall". |
| F2 | BLOCKER | CONFIRMED for fetched docs | §3.6 toml; §15 docs | UNKNOWN | Design lines 156,170,172 show `claude-sonnet-5-5` and shared `temperature = 0.0`; API behaviour is external. |
| F3 | HIGH | CONFIRMED | §3.7; patterns.py:230-234; normalize.py:19-64 | PASS | `hexdigest()[:8]`; salt path list, ensure_local_salt has no chmod; §3.7 map "only in the case DB". |
| F4 | HIGH | CONFIRMED | extract.py:88-108,184-190; imessage_test_data.sql:5-19; §3.4, §9; imessage_source.py:109-124,57-58 | PARTIAL | Live SELECT omits forensic columns, but fixture 5-19 does include `date_edited` and `balloon_bundle_id`. |
| F5 | HIGH | CONFIRMED | db.py:12-64; §3.13; SQLite docs | PASS | `mode=ro&immutable=1` at 59; TemporaryDirectory copy of full chat.db. SQLite docs not fetched. |
| F6 | HIGH | CONFIRMED | extract.py:181; time.py:16-17; imessage_mapper.py:10-11,38-58 | PASS | `to_iso_utc(date) or datetime.now(...)`; time.py LOWER 1999 vs mapper MIN 2004 vs §7 line 327 2004-2100; mapper raises. |
| F7 | HIGH | CONFIRMED gap | §3.6, §3.13, §6 P7; §2 anti-goal | PASS | Anti-goal line 60 "other than a configured local one"; base_url is config (line 163); P7 "local only". |
| F8 | HIGH | CONFIRMED | §3.7-3.8; chunker.py:166-174; policy_shield.py:181-183,265-269; patterns.py:162-176 | PASS | chunker `{contact}: {msg.text}`; shield raises on hard-fail; patterns say "Simplified patterns for demo". |
| F9 | HIGH | Design CONFIRMED; scale PLAUSIBLE | §3.5, G3, §3.10; migrations.py:197-211; §15 | PASS | `embedding float[1024]`; G3 "single-file" vs attachments dir; no key/signature on manifest (line 218). Scale notes external. |
| F10 | HIGH | CONFIRMED | §6 P1/P3/P6; §3.11; storage/base.py:211-285; labels.yml:18-20,320-323 | PASS | base.py:254 `GASLIGHTS`; labels:20 "NOT a clinical assessment"; §6 P6 lists encrypted backups. |
| F11 | MEDIUM | Code and design CONFIRMED | reactions.py:7-14,36-37,62-72; extract.py:130-148,229; §3.4 V1; §8 | PASS | Map has 2000-2005 only; 3000-3999 -> "custom"; no `p:`/`bp:` handling at 229. |
| F12 | MEDIUM | CONFIRMED | whatsapp_export.py:33-49,105-107,196-198; instagram/extract.py:70-118; reader.py:68-102 | PASS | Markers incl. "added"; instagram reads content/photos/videos/audio_files/reactions; PDF `platform="imessage"`. |
| F13 | MEDIUM | CONFIRMED gap | §3.4; idempotency.py:10-16; dedupe.py:15-24 | PASS | dNh canonical_json helper exists; §3.4 hash has no canonicalization rules; pseudonym filled later (line 112). |
| F14 | MEDIUM | CONFIRMED | enricher.py:164-176; main.py:375-376; labels.yml:10-13; §3.9 | PASS | tau/tau_low/tau_high options; `fine_cloud_allowed: false` at 12 not in §3.9. |
| F15 | MEDIUM | CONFIRMED gap | §3.8, §3.10; chunker.py:156-178 | PASS | `range(0, n, turns_per_chunk - stride)` overlap; §3.10 line 216 RRF with no k/depth. |
| F16 | MEDIUM | PLAUSIBLE; UNKNOWN | §3.2; uv --version; §15 | UNKNOWN | §3.2 line 85 uses `path = ".../chat-extraction-core"`; Astral doc currency and uv session output not checkable. |
| F17 | MEDIUM | CONFIRMED | pyproject.toml:193-218; imessage_test_data.sql:135-158; §7-8 | PASS | omit list 198-207; fixture lines 139-140 are `X'62706c6973743030...` (bplist00); `raise NotImplementedError` exclusion at 216. |
| F18 | LOW | CONFIRMED | §4; dNh pyproject.toml:19; ChatX httpx | PASS | dNh `httpx>=0.28`; ChatX pyproject:45 `httpx>=0.27,<0.28`; §4 line 289 "no file hand-offs" beside JSONL step. |
| F19 | INFO | CONFIRMED | labels.yml:8,18-20; session count | PASS | `schema_version: 1.2`; parsed counts coarse 55, fine_local_only 99 leaf labels (12 groups). |
| F20 | INFO | CONFIRMED | normalize.py:47-54; extractors/imessage.py:276-314; body_normalize.py:12-31 | PASS | `mac[:32]` "128-bit"; PRAGMA table_info probe + `balloon_bundle_id`; plistlib/utf-8 heuristic. |

## agy (F-01 to F-25)

| ID | Sev | Verdict | Citations checked | Result | Note |
|---|---|---|---|---|---|
| F-01 | BLOCKER | CONFIRMED | ChatX db.py:12-60; dNh probe.py:288-311; §3.5, §8 | PASS | `file:{db_path}?mode=ro&immutable=1` (59); probe uses `source_connection.backup(target)` + `quick_check`. |
| F-02 | BLOCKER | CONFIRMED | §3.4, §3.12, §9 | PASS | Line 122 excludes only source_meta/provenance, so reactions/attachments.missing/pseudonym are in the hash. |
| F-03 | BLOCKER | CONFIRMED | §3.4; dNh whatsapp_export.py:180-187 | PASS | Line 108 derives id from (platform, conv_id, sent_at, handle, text); WhatsApp formats are minute-resolution (`%H:%M`). |
| F-04 | BLOCKER | CONFIRMED | whatsapp_export.py:24-49,105-108,196-198; §3.5, §8 | PASS | `WHATSAPP_PREFIX_RE` needs ` - ` separator (no bracketed iOS form); substring markers "added","left","joined". §3.5 not relevant. |
| F-05 | BLOCKER | CONFIRMED | events.py:172-182,519-560; normalizer.py:28-41; §9 | PASS | Channel enum lacks instagram/pdf/txt; `EventPayload.text min_length=1`; normalizer fixes INBOUND/CLIENT. |
| F-06 | BLOCKER | CONFIRMED | dedupe.py:15-24; migrations.py:23; §9 | PASS | `UNIQUE(dedupe_scope, dedupe_hash)`; §9 line 349 "content_hash feeds idempotency.dedupe_hash". |
| F-07 | BLOCKER | CONFIRMED | extract.py:229,257; imessage_test_data.sql:82-90 | PASS | `target_guid in messages_by_guid` with no prefix strip; fixture uses bare 'msg-004'. "0% on real chat.db" is extrapolation not checkable. |
| F-08 | BLOCKER | CONFIRMED | attachments.py:90-126 | PASS | No `expanduser` anywhere in file; paths joined as `attachments_dir / attachment.filename`. "fails all" is runtime. |
| F-09 | HIGH | CONFIRMED | extract.py:88-108,237; imessage_test_data.sql:144-149 | PARTIAL | 88-108 and fixture table at 144 support; line 237 is a `datetime.now` fallback, reply logic is at 176-177. Real-schema fact external. |
| F-10 | HIGH | CONFIRMED | dNh imessage_attributed_body.py:229-243; probe.py:45,604-625 | PASS | Only `if not text.strip()` guards (240); `'￼'.strip()` is non-empty (run). Probe lines show placeholder handling, context only. |
| F-11 | HIGH | CONFIRMED | instagram/extract.py:21-38,157; §4, §8 | PARTIAL | Code has zip-slip check only, no mojibake repair or size limits. But §4 line 267 lists mojibake repair as target, not as existing in extract.py. |
| F-12 | BLOCKER | CONFIRMED | §3.6, §3.7, §3.12; policy_shield.py:130-169 | PARTIAL | §3.7 line 184 "reversible map stored only in the case DB" supports; policy_shield 130-169 (replace/coverage) is unrelated; §3.6, §3.12 unrelated. |
| F-13 | HIGH | CONFIRMED | §3.7; policy_shield.py:310-335 | PASS | Line 196 "seeded random sample" with no n; code lines are preflight, tangential. Statistical bound is external math. |
| F-14 | HIGH | CONFIRMED | chunker.py:124-198; §3.9 | PASS | chunker:166 `contact` in line text; §3.9 line 211 "±2 turns of redacted context". |
| F-15 | BLOCKER | CONFIRMED | labels.yml:3-12; arch-gates.yml:60-65; §3.9 | PASS | labels lines 4-5 coarse vs fine_local_only; §3.9 line 207 compiles whole file. No `privacy_tier` key exists; section names used. |
| F-16 | MEDIUM | CONFIRMED | patterns.py:159-197; labels.yml:373-389,425-427 | PASS | `illegal_drugs`/`explicit_violence` regexes vs `substances_specifics`, `crime_threat`, `violence_detail`. |
| F-17 | HIGH | CONFIRMED | §3.6, §3.10, §5; sqlite-vec #25; §11 | PARTIAL | §3.10 has no 1M figure; "p95 ≤150 ms" is in §7 line 328 as tracked measurement, not §11. sqlite-vec issue unfetched. |
| F-18 | HIGH | CONFIRMED | psychology_relationship_mapper.py:129-546; labels.yml:1-469; §3.11, §8 | PASS | Parsed: 123 mapper source_labels, 0 present in the 55 coarse + 99 fine ids; e.g. `gaslighting_pattern` at mapper:343. |
| F-19 | HIGH | CONFIRMED | dNh email_eml.py:110-165; ChatX normalize.py:1-96; §3.5, §3.12 | PASS | No To/Cc/In-Reply-To read; `direction=Direction.INBOUND` (154); normalize.py manual digit parsing, no phonenumbers. |
| F-20 | MEDIUM | CONFIRMED | dNh imessage_thread_identity.py:85; probe.py:435-453 | PASS | `MIN(chat_id) AS chat_id` at 85; probe `COUNT(DISTINCT chat_id) AS identity_count`. |
| F-21 | HIGH | CONFIRMED | §3.6, §6, §7; dNh migrations.py:1-424 | PARTIAL | Storage is §3.5, not §3.6; claim "no schema migration table" is contradicted: line 142 lists `schema_migrations`. No PRAGMAs/watermarks mention is true. |
| F-22 | MEDIUM | CONFIRMED | §3.9; ollama_client.py:194-260 | PASS | §3.9 mentions no cache_control/batch/cost cap/injection handling; ollama_client lines are generic client setup. |
| F-23 | MEDIUM | CONFIRMED | backup.py:55-93; main.py:992-998; §3.5 | PARTIAL | `--backup-password` exists (main.py:992). backup.py:62 is blank; the "not supported yet" string was not found (rg). EXIF claim not located. |
| F-24 | MEDIUM | CONFIRMED | imessage_test_data.sql:1-162; dNh test_imessage_attributed_body.py:1-200; §11 | PARTIAL | Fixture has no `p:0/`, thread_originator, `~/Library` (rg 0 hits); blobs are bplist. But §8 line 337 does take the 1013-line dNh test file; §11 is not the place. |
| F-25 | MEDIUM | CONFIRMED | pyproject.toml:31-76; arch-gates.yml:24-76; §7, §12 | PARTIAL | arch-gates.yml:25,43 use `chatx redact --input` / `enrich messages`. But pymilvus/qdrant/pinecone/weaviate/spacy are absent from pyproject (rg); torch/chromadb are optional extras, not default deps. |

## Failures and partials

No FAIL rows. PARTIAL rows:

- Grok F4: fixture 5-19 is cited as omitting forensic columns but defines `date_edited` and `balloon_bundle_id`; the live SELECT (88-108) does omit them.
- AGY F-09: extract.py:237 does not concern replies (reply handling is 176-177); 88-108 and fixture 144-149 do pass; the real-chat.db column claim is external.
- AGY F-11: extract.py has no mojibake repair or entry-size limits, but §4/§8 do not claim the existing file has them (§4 line 267 describes the target layout).
- AGY F-12: only §3.7 line 184 supports; policy_shield.py:130-169, §3.6, §3.12 do not bear on where the token map is stored.
- AGY F-17: cited §3.10 contains no 1M-chunk figure; the <150 ms p95 target sits in §7 line 328 as a tracked measurement, and §11 does not contain it. sqlite-vec issue not fetched.
- AGY F-21: DDL/storage prose is in §3.5 not §3.6; "no schema migration table" is contradicted by design line 142 (`schema_migrations`).
- AGY F-23: no "Encrypted backups are not supported yet" text at backup.py:62 or anywhere in backup.py; `--backup-password` flag does exist; EXIF-stripping claim not located.
- AGY F-24: §11 does not omit the dNh test suite; §8 line 337 includes "its 1013-line test file". Fixture-gap sub-claims pass.
- AGY F-25: the listed heavy packages (pymilvus, qdrant-client, pinecone, weaviate-client, spacy) are not in pyproject.toml; transformers/torch/chromadb are optional extras, not default dependencies. arch-gates.yml sub-claim passes.

UNKNOWN rows (external only): Codex F15, F28, F29, F30; Grok F2, F16.

Other observation outside the finding rows (not scored): AGY threat-table item A2 says db.py:25 uses `mkdtemp` with 0755; db.py:25 uses `TemporaryDirectory`.

## Cross-auditor citation overlaps

Repo files (same file, overlapping lines):
- ChatX src/chatx/imessage/db.py: Codex F05 (25-43), Grok F5 (12-64), AGY F-01 (12-60).
- ChatX src/chatx/imessage/extract.py 88-108: Codex F01, Grok F4 (88-108,184-190), AGY F-09.
- extract.py:229: Grok F11 (130-148,229), AGY F-07 (229,257).
- ChatX imessage/reactions.py: Codex F06 (33-37), Grok F11 (36-37).
- ChatX imessage/attachments.py: Codex F07 (97-124), AGY F-08 (90-126).
- dNh ingest/whatsapp_export.py 33-49,105-108,196-198: Codex F08, Grok F12 (105-107), AGY F-04 (24-49,105-108,196-198); Codex F03 (177-193) with AGY F-03 (180-187).
- ChatX pdf_ingest/reader.py: Codex F08 (68-102), Grok F12 (68-102).
- dNh ingest/dedupe.py: Codex F04 (15-25), Grok F13 (15-24), AGY F-06 (15-24).
- dNh ingest/normalizer.py: Codex F04 (26-47), AGY F-05 (28-41).
- dNh store/migrations.py: Codex F13 (197-237), Grok F9 (197-211), AGY F-21 (1-424).
- ChatX pyproject.toml: Codex F25 (187-206) with Grok F17 (193-218).
- ChatX tests/fixtures/imessage_test_data.sql: Grok F4 (5-19), Grok F17 (135-158), AGY F-07 (82-90), AGY F-09 (144-149), AGY F-24 (1-162); pairs F17/F-09 (144-149) and F-24 with each.
- ChatX identity/normalize.py: Codex F11 (47-64), Grok F3 (19-64), Grok F20 (47-54), AGY F-19 (1-96).
- ChatX redaction/patterns.py: Codex F11 (227-234), Grok F3 (230-234), Grok F8 (162-176), AGY F-16 (159-197) (Grok F8 with AGY F-16 at 162-176).
- ChatX redaction/policy_shield.py: Grok F1 (138-157) with AGY F-12 (130-169).
- ChatX transformers/chunker.py: Grok F8 (166-174), Grok F15 (156-178), AGY F-14 (124-198).
- ChatX config/labels.yml: Codex F17 (307-425) with Grok F1 (307-308), Grok F10 (320-323), AGY F-16 (373-389,425-427); Grok F10 (18-20) with Grok F19 (18-20); Grok F14 (10-13) with AGY F-15 (3-12); AGY F-18 (1-469) spans all.
- ChatX enrichment/enricher.py:164-176: Codex F18, Grok F14.

Design sections cited by two or more auditors (section-level only):
- §3.4: Codex F01, F02, F03; Grok F4, F13; AGY F-02, F-03.
- §3.5: Codex F12, F14, F24; Grok F9; AGY F-04, F-23.
- §3.6: Codex F10, F15, F16; Grok F2, F7; AGY F-12, F-17, F-21.
- §3.7: Codex F09, F10, F11, F29; Grok F1, F3, F8; AGY F-12, F-13.
- §3.9: Codex F17, F18; Grok F14; AGY F-14, F-15, F-22.
- §3.10: Codex F14, F19; Grok F9, F15; AGY F-17.
- §3.11: Codex F20; Grok F10; AGY F-18.
- §3.13: Codex F05, F24; Grok F5, F7.
- §3.2: Codex F21; Grok F16.
- §8: Codex F06, F07, F08; Grok F4, F11, F17; AGY F-04, F-11, F-18.
- §9: Codex F04; Grok F4; AGY F-02, F-05, F-06.
