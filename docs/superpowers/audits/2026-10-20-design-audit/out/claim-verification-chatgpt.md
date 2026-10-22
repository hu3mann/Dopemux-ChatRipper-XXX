# Claim verification: chatgpt-web (third pass)

Runner: `sonnet-verify` | Model: Sonnet 5.5 as stated by the harness (no runtime receipt) | Date: 2026-10-21 | Tool calls: about 30
Repos at verification (read-only): ChatX `9c3dd6b` (same as bundle HEAD); dNh_CRM `39c75bde` (same as bundle HEAD). `git log --since` was not run; both HEADs equal the bundle HEADs, so no cited file changed in committed history. Uncommitted working-tree changes were not checked.
Scope: report-chatgpt-web.md section 2, rows F01 to F38. `Report §x.y` citations skipped (not evidence). Web/external claims are not fetched.

## Summary

| auditor | rows | PASS | PARTIAL | FAIL | UNKNOWN | NOT_RUN |
|---|---|---|---|---|---|---|
| chatgpt-web | 38 | 36 | 1 | 0 | 1 | 0 |

## Row verification

| ID | Sev (as claimed) | Verdict (as claimed) | Citations checked | Result | Note |
|---|---|---|---|---|---|
| F01 | BLOCKER | CONFIRMED | chatx db.py:25-43, 58-64; §3.13, §8 | PASS | Offset by 1. `shutil.copy2(db_path, temp_db_path)` then WAL then SHM copied one after another; open_ro uses `immutable=1`. §3.13 says "WAL-safe copy". |
| F02 | BLOCKER | CONFIRMED | §3.4, §10 V6; chatx time.py:27-64; chatx pdf_ingest/reader.py:60-103 | PASS | §3.4 `sent_at` datetime (aware, UTC) required. time.py infers units by magnitude; reader.py `base_ts = datetime.now(timezone.utc)`, +1 s per line. |
| F03 | BLOCKER | CONFIRMED | §9; dnh events.py:2007-2015 | PASS | §9 maps every message to `MSG_INBOUND_RECEIVED`; dNh raises "attachment-only payload is limited to inbound client iMessage events". |
| F04 | BLOCKER | CONFIRMED | §3.6-3.7, §5, contract 4; chatx policy_shield.py:226-248 | PARTIAL | §3.7 and §5.4 gate is case/run-level (`require_cloud_ok(case, run)`), no payload binding. policy_shield 226-248 only shows per-chunk redaction; it does not exhibit the authorization gap. |
| F05 | BLOCKER | CONFIRMED | §3.7, §6 P3, §10 V3, §12 q3 | PASS | P3 exit: "Eval meets targets on synthetic set in CI". Real-sample set is optional ("optional local-only" file, §12 q3 open). |
| F06 | HIGH | CONFIRMED | §3.4, §9; dnh whatsapp_export.py:165-174 | PASS | `_dedupe_key(export_filename, ts_raw, sender_display, text)` builds identity from filename, raw time, sender, text hash. §3.4 msg_id/content_hash/derived id not separated. |
| F07 | HIGH | CONFIRMED | §3.4-3.5; chatx extract.py:88-107, 227-259 | PASS | Query selects `m.service`, no edit/thread/membership columns; reaction fold falls back to `datetime.now(timezone.utc)`. |
| F08 | HIGH | CONFIRMED | chatx chunker.py:113-122, 150-168; enricher.py:290-326 | PASS | `content = f"{conv_id}:{method}:{index}:{self.run_id}"` then `[:8]` hex; source hash is IDs+time only; `sender = "ME" if msg.is_me else contact`; enricher re-parses chunk text lines. |
| F09 | HIGH | CONFIRMED | dnh imessage_attributed_body.py:168-272; dnh tests/unit/test_imessage_attributed_body.py:30-37, 59-144; §10 V2 | PASS | Two pinned layouts via `_ALLOWED_LAYOUTS`. Test at 140 uses `b"x" * 0x8000`, which `_integer` encodes with 0x81 (2 bytes), so the "four-byte" test is not four-byte. |
| F10 | HIGH | CONFIRMED | chatx report.py:76-98; extract.py:282-286, 372-389; cli/main.py:1201-1204, 1301-1308 | PASS | Report filter `m.handle_id IN (...) OR m.is_from_me = 1`; main.py 1201 uses `copy_db_for_readonly(db)` while manifest at 1304 uses `staged_db_path if from_backup else db`. |
| F11 | HIGH | CONFIRMED | chatx attachments.py:90-126, 241-269; backup.py:129-147 | PASS | `Path(attachment.filename)` candidate; `compute_file_hash` then separate `shutil.copy2`; `if not dest_path.exists()` unverified; `except ... pass`. |
| F12 | HIGH | CONFIRMED | dnh whatsapp_export.py:33-49, 93-108, 196-198 | PASS | `SYSTEM_LINE_MARKERS` include "added", "left", "joined"; `_is_system_body(message_value)` then `continue` drops the record. |
| F13 | HIGH | CONFIRMED | chatx instagram/extract.py:64-118; dnh email_eml.py:107-180, 256-283; chatx reader.py:118-133 | PASS | `ts_ms = item.get("timestamp_ms") or 0`; ig msg_id uses `idx`; email attachments keep filename/type/size only (no bytes); PDF text from `_extract_text_pages_stub`. |
| F14 | HIGH | CONFIRMED | dnh ingest_runner.py:85-118, 133-190; migrations.py:5-24; §9 | PASS | `if not 0 < lookback_rows <= 5000`; scan starts at `cursor_before - lookback_rows`; events table `UNIQUE(dedupe_scope, dedupe_hash)`. |
| F15 | HIGH | CONFIRMED | chatx patterns.py:159-197; policy_shield.py:180-205, 258-278; §3.7 | PASS | "Simplified patterns for demo"; `raise ValueError(...)` in redact_chunk_text is caught by `except Exception`, chunk skipped, `hard_fail_triggered` never set. |
| F16 | HIGH | CONFIRMED | §3.7 condition 3, §6 P3 | PASS | Condition 3: "a seeded random sample ... any confirmed leak blocks"; no sample size, estimand or sensitivity stated. |
| F17 | HIGH | CONFIRMED | §3.7; chatx normalize.py:47-95; patterns.py:200-249 | PASS | `ensure_local_salt` writes with no mode; ConsistentTokenizer generates fresh random salt per instance, hash `[:8]`, token `⟦TKN:TYPE:hash⟧` vs design `⟦TKN:<id8>⟧`. |
| F18 | HIGH | CONFIRMED | chatx labels.yml:4-13, 191-253, 403-410; §3.7-3.9 | PASS | `coarse_cloud_allowed: true`; coarse includes `substance_influence_*` and `orientation_context` ("never redacted"). Fine orientation labels at 403-410 are local-only. |
| F19 | HIGH | CONFIRMED | §3.6, §3.10 | PASS | Provider Protocol: `complete_structured(...) -> BaseModel`, `embed`, `identity`; no capability, refusal or truncation outcome. Official-source part not checked. |
| F20 | HIGH | CONFIRMED | §3.6, §3.9; chatx ollama_client.py:176-210, 263-331 | PASS | Tenacity `stop_after_attempt(3)` is transport-level; timeout 30 s, semaphore concurrency; no total deadline or spend limit. §3.6 "retried once then quarantined". |
| F21 | HIGH | CONFIRMED | §3.6, §3.9, §5 c5; chatx ollama_client.py:229-232, 361-366 | PASS | `content = f"{prompt}:{model_config.name}:{temperature}:{seed}"`; provenance `run_id="local_enrichment"`, no top_k/top_p/repeat_penalty in hash. |
| F22 | HIGH | CONFIRMED | chatx multi_pass_pipeline.py:93-145; labels.yml:8-23, 307-310; enricher.py:149-179; §3.9 | PASS | Loader reads `data.get('categories', {})`; YAML top-level key is `coarse:`. Gate compares per-record `confidence_llm` to tau_high/tau_low with no state. |
| F23 | HIGH | CONFIRMED | chatx ollama_client.py:234-261, 277-279; §3.7, §3.9-3.11 | PASS | Prompt interpolates `Message: "{request.text}"` into a single user message; only schema/JSON validation afterwards. |
| F24 | HIGH | CONFIRMED | §3.5, §4, §6 P2/P5 | PASS | Table outline only; grep finds no transaction, foreign-key, generation, repair or restore wording; DDL left to builder (§11). |
| F25 | HIGH | CONFIRMED | dnh migrations.py:181-238, 327-336, 375-380; §10 V4 | PASS | `embedding float[1024]` in `vec0`; vec0 table created only if module present; V4 says "dimension is per-space" while schema is fixed. |
| F26 | HIGH | CONFIRMED | §1, §3.4-3.5, §3.10 | PASS | §1 "evidence-grade provenance"; bundle = "per-file sha256 manifest and the case manifest"; no external attestation or acquisition-history requirement. |
| F27 | HIGH | CONFIRMED | chatx vector_store.py:170-195, 329-335; §3.10, §6 P5 | PASS | Search metadata keeps `"message_count": len(meta.get("message_ids", []))`, not the IDs; results rebuild `message_ids` from metadata that lacks them. |
| F28 | HIGH | CONFIRMED | chatx psychology_relationship_mapper.py:51-101, 343-347, 548-570; §3.11 | PASS | `GASLIGHTS ... confidence=0.93`; `final_confidence = min(1.0, base_confidence * context_multiplier + overlap_bonus)`; explanation "Gaslighting or reality distortion behavior". |
| F29 | HIGH | CONFIRMED | §3.2-3.3, §5 c1, §9, §10 V8 | PASS | §3.2 dNh `[tool.uv.sources] ... { path = "../chatstack/...", editable = true }`; V8 "two lockfiles". No immutable release contract stated. |
| F30 | HIGH | CONFIRMED | chatx pyproject.toml:121-130; schemas/validator.py:13-36; utils/run_report.py:89-95 | PASS | wheel `packages = ["src/chatx"]` only; `SCHEMA_DIR = Path(__file__).parent.parent.parent.parent / "schemas"`; `if not run_schema_path.exists(): return True`. |
| F31 | HIGH | CONFIRMED | §3.5, §3.13; chatx ollama_client.py:305-312, 385-392 | PASS | §3.13 "no secrets in logs"; code logs `response.text` and `Raw response: {message_content}` (debug). |
| F32 | HIGH | CONFIRMED | §6, §7, §10 | PASS | P3 exit is synthetic-only while gate cond. 3 needs the local provider (P4); P4 exit needs "enrichments visible to query" (P5). V3/V4 measurements sit in later phases. |
| F33 | HIGH | CONFIRMED | chatx pyproject.toml:187-207; config/arch-gates.yml:23-35, 43-48; §5, §7 | PASS | omit lists `redaction/*`, `transformers/*`, `enrichment/*`, `indexing/*`, `schemas/validator.py`; arch-gates `--dry-run \|\| true` and `\|\| true` on validation. |
| F34 | MEDIUM | CONFIRMED | §3.5, §3.12, §4, §7 | PASS | CLI tree has no resume, delete or export-portability commands; grep for "resume", "delete", "portab" returns nothing in design. |
| F35 | MEDIUM | CONFIRMED | §2, §3.12-3.14, §8, App. A; chatx cli/main.py:336-350, 780-796, 861-882 | PASS | A.1 "redact ... warns and exits 0" but main.py 336-350 has `raise typer.Exit(1)` on hardfail/coverage; 780-796 and 861-882 wire multi-vector store from CLI (A.1 "dead to CLI"). |
| F36 | MEDIUM | CONFIRMED | chatx pyproject.toml:10; dnh pyproject.toml:7; §3.3, §8 | PASS | chatx `license = {text = "MIT"}`; dNh `license = { text = "Proprietary" }`; core is to be shared by both (§3.1). |
| F37 | HIGH | CONFIRMED | §3.3, §3.5, §11; SQLite WAL docs | PASS | Design names no SQLite version or fix baseline (grep "SQLite 3." and "sqlite_version" empty). The WAL-reset fix itself is external and not checked. |
| F38 | MEDIUM | CONFIRMED | §3.3, §3.6-3.7, §3.12; Report §3.15 | UNKNOWN | Claim rests on external model/server/framework capability facts (Report §3.15, not evidence); no repo line settles it. |

## Failures and partials

- F04 (PARTIAL): design side holds (§3.7 and §5.4 describe a case/run gate, `require_cloud_ok(case, run)`, no exact-payload binding). The repo citation `policy_shield.py:226-248` is the per-chunk redaction loop and does not show any gate authorization behaviour. No FAIL rows.
- F38 (UNKNOWN): rests on external documentation only.

## Overlaps with earlier verification passes

Mechanical: chatgpt-web repo-file citations whose line ranges overlap a "Citations checked" entry in `out/claim-verification.md` (cv: codex F01-F30, grok F1-F20, agy F-01-F-25) or `out/claim-verification-opus.md` (opus: F-01-F-35). Design-section citations excluded.

| chatgpt-web ID | File and range | Overlapping rows |
|---|---|---|
| F01 | chatx db.py:25-43, 58-64 | cv codex F05; cv grok F5; cv agy F-01; opus F-09, F-11 |
| F02 | chatx pdf_ingest/reader.py:60-103 | cv codex F08; cv grok F12 |
| F03 | dnh events.py:2007-2015 | opus F-14 |
| F06 | dnh whatsapp_export.py:165-174 | opus F-13 |
| F07 | chatx extract.py:88-107 | cv codex F01; cv grok F4; cv agy F-09 |
| F07 | chatx extract.py:227-259 | cv grok F11; cv agy F-07, F-09; opus F-08 |
| F08 | chatx chunker.py:150-168 | cv grok F8, F15; cv agy F-14 |
| F09 | dnh imessage_attributed_body.py:168-272 | cv agy F-10 |
| F09 | dnh test_imessage_attributed_body.py:30-37, 59-144 | cv agy F-24; opus F-21 |
| F10 | chatx extract.py:282-286 | cv codex F07 |
| F11 | chatx attachments.py:90-126 | cv codex F07; cv agy F-08 |
| F11 | chatx attachments.py:241-269 | cv codex F14 |
| F11 | chatx backup.py:129-147 | cv codex F07 |
| F12 | dnh whatsapp_export.py:33-49, 93-108, 196-198 | cv codex F08; cv grok F12; cv agy F-04; opus F-07 |
| F13 | dnh email_eml.py:107-180 | cv agy F-19; opus F-31 |
| F13 | chatx instagram/extract.py:64-118 | cv grok F12 |
| F14 | dnh migrations.py:5-24 | cv agy F-06; opus F-01 |
| F15 | chatx patterns.py:159-197 | cv grok F8; cv agy F-16; opus F-23 |
| F15 | chatx policy_shield.py:258-278 | cv grok F8 |
| F17 | chatx normalize.py:47-95 | cv codex F11; cv grok F3, F20; cv agy F-19 |
| F17 | chatx patterns.py:200-249 | cv codex F11; cv grok F3; opus F-12 |
| F18 | chatx labels.yml:4-13 | cv grok F14, F19; cv agy F-15; opus F-05 |
| F18 | chatx labels.yml:191-253 | cv codex F17; cv agy F-18; opus F-05 |
| F20 | chatx ollama_client.py:176-210 | cv agy F-22 |
| F21 | chatx ollama_client.py:229-232 | cv agy F-22 |
| F22 | chatx labels.yml:8-23 | cv grok F10, F19; cv agy F-15, F-18; opus F-05 |
| F22 | chatx labels.yml:307-310 | cv codex F17; cv grok F1; cv agy F-18 |
| F22 | chatx enricher.py:149-179 | cv codex F18; cv grok F14; opus F-18 |
| F23 | chatx ollama_client.py:234-261 | cv agy F-22 |
| F25 | dnh migrations.py:181-238 | cv codex F13; cv grok F9; opus F-19; cv agy F-21 |
| F25 | dnh migrations.py:327-336, 375-380 | cv agy F-21; opus F-19 (375-378) |
| F27 | chatx vector_store.py:170-195, 329-335 | cv codex F19 |
| F28 | chatx psychology_relationship_mapper.py:51-101 | cv codex F20 |
| F28 | chatx psychology_relationship_mapper.py:343-347 | cv agy F-18 |
| F30 | chatx pyproject.toml:121-130 | cv codex F22 |
| F30 | chatx schemas/validator.py:13-36 | cv codex F22 |
| F33 | chatx pyproject.toml:187-207 | cv codex F25; cv grok F17; opus F-35 |
| F33 | chatx arch-gates.yml:23-35, 43-48 | cv agy F-25 |
