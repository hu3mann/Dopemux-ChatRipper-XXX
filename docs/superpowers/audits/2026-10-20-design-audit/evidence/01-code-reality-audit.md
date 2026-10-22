# ChatX implementation audit (read-only, nothing run)

Paths are under `/Users/hue/code/Dopemux-ChatRipperXXX`. I read the code, but I did not execute it or any test. Anything marked "likely" is from reading, not running.

## Headline findings

1. **Only extraction is wired end to end.** `imessage pull`, `instagram pull` and `imessage pdf` work. `transform`, `redact`, `enrich`, `index` and `query` each have real code behind them. The hand-offs between stages are broken or unenforced.
2. **Extract output cannot be fed to `transform`.**
   - `write_messages_with_validation` writes `{"messages":[...],"total_count":..,"schema_version":"1.0"}` (`utils/json_output.py:~60`).
   - `transform` does `json.load` and `CanonicalMessage(**m) for m in data` (`cli/main.py:159-166`). Iterating that dict yields key strings, so it raises `TypeError`.
   - It only works if the user unwraps the list by hand or supplies JSONL.
3. **`chatx enrich-multi` cannot run.** `enrichment/multi_pass_pipeline.py:14-15` imports `OllamaClient` and `PrivacyGate`.
   - `ollama_client.py` only defines `ProductionOllamaClient`.
   - `PrivacyGate` lives in `indexing/multi_vector_store.py:99`, not in `policy_shield.py`.
   - The import happens at `cli/main.py:605`, before the `try`, so it ends in an ImportError traceback.
   - The module also uses `.generate()` on a client that has no such method, and it needs `yaml`, which is not a declared dependency.
4. **The ≥99.5% "redaction coverage" gate is not a recall measure, and it is never enforced.** Details in section 5.
5. **`--allow-cloud` gates nothing real.** There is no cloud code anywhere in `src/`. Details in section 5.
6. **The `attributedBody` parser is not a real typedstream parser.** Details in sections 1 and 8.
7. **Scope leak when extracting a contact.** `imessage/extract.py:385` has `OR m.is_from_me = 1` in `get_conversation_guids`.
   - That selects every chat in which the user ever sent a message, not only chats with the target handle.
   - Messages from other contacts and group chats are exported under one `--contact` run.
8. **The coverage gate excludes the core pipeline.** `pyproject.toml` has `--cov-fail-under=90`, but `[tool.coverage.run] omit` removes `redaction/*`, `transformers/*`, `enrichment/*`, `indexing/*`, `schemas/validator.py` and `transcribe/local_whisper.py`.

## 1. Package map

Grades: REAL = substantive logic, THIN = skeleton or placeholder, STUB = TODO-only, DEAD = unreferenced from the CLI path. "CLI-live" means reachable from `chatx.cli.main`.

### Top level and CLI

| Module | LOC | Responsibility and key symbols | Grade |
|---|---|---|---|
| `__init__.py` | 20 | Exports `CanonicalMessage`, `EnrichmentMessage`; `__version__` is 0.1.0 | REAL |
| `cli/main.py` | 1573 | Typer app, 11 commands; see section 2 | REAL, with 3 stubs |
| `cli/__init__.py` | 5 | Re-exports `cli` | REAL |
| `cli_errors.py` | 32 | RFC7807 `emit_problem`, `redact_path` | REAL, CLI-live |
| `constrained_dynamic_loader.py` | 488 | MCP server loader (Claude-tooling concern, nothing to do with chat analysis) | REAL but DEAD to product |

### iMessage

| Module | LOC | Responsibility and key symbols | Grade |
|---|---|---|---|
| `imessage/extract.py` | 452 | `extract_messages`; 4-pass handling of reactions, replies and attachments; `resolve_contact_handles`; `get_conversation_guids` (scope bug) | REAL |
| `imessage/time.py` | 64 | `to_iso_utc`: Apple epoch, magnitude heuristic for s/µs/ns, bounds 1999–2100 | REAL |
| `imessage/reactions.py` | 71 | Reaction map 2000–2005, "custom" 3000–3999, `is_reply` | REAL, mapping questionable (below) |
| `imessage/body_normalize.py` | 35 | `normalize_attributed_body`: tries `plistlib`, else UTF-8 decode with errors ignored, then strips non-printables | THIN, effectively a heuristic |
| `imessage/db.py` | 70 | `copy_db_for_readonly` copies db plus WAL/SHM; `open_ro` uses `mode=ro&immutable=1` | REAL |
| `imessage/backup.py` | 189 | MobileSync handling: `Manifest.db` fileID lookup, `stage_sms_db`, encryption flag via plist | REAL for unencrypted only |
| `imessage/attachments.py` | 334 | Metadata, copy, dedupe by sha256, thumbnails, backup path resolution | REAL |
| `imessage/transcribe.py` | 259 | `transcribe_local`: faster-whisper, then openai-whisper "base", then mock; stats | REAL |
| `imessage/report.py` | 216 | Missing/evicted attachments report | REAL |
| `extractors/{__init__,base,imessage}.py` | 9+169+582 | Second, parallel iMessage extractor (`IMessageExtractor`, `BaseExtractor`, `detect_platform`) | DEAD to the CLI; used only by tests |

- **`attributedBody`:** `plistlib` will not parse real typedstream blobs (`streamtyped`). A grep for `typedstream`, `streamtyped` and `NSString` in `src/` finds nothing. Real blobs will likely come out as text with class names mixed in.
- **`attributedBody` tests:** they only test `b"Hello <b>world</b>"` and a synthetic plist (`tests/imessage/test_body_normalize.py`, `tests/imessage/test_text_decoding.py`).
- **Reaction codes:** the common documentation of `chat.db` puts 3000–3005 as tapback removals, not "custom emoji". Treat that mapping as suspect until checked against a real db.

### Other extractors

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `instagram/extract.py` | 174 | ZIP stream reader with zip-slip guard, participant and author filters, `msg_id=ig:{thread}:{ts}:{idx}`. No latin-1/UTF-8 mojibake repair for Instagram's known encoding quirk. | REAL |
| `pdf_ingest/reader.py` | 134 | `fitz`, then `PyPDF2`, then empty. Parses `Name: msg` lines. | THIN |
| `transcribe/local_whisper.py` | 72 | `faster_whisper.WhisperModel`, default model `small`, int8 | REAL |

- **PDF details:**
  - Timestamps are synthetic (`now()` plus 1 s per line).
  - Platform is hardcoded `"imessage"`.
  - OCR does nothing outside test injection: when `--ocr` is set and no text is found, pages stay empty unless `ocr_text_override` is passed.
- **Dependencies:** `fitz`, `PyPDF2` and the whisper packages are undeclared.

### Media, identity and observability

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `media/{exif,hash,sniff,thumbnail,__init__}.py` | 35, 18, 69, 21, 7 | Pillow EXIF (`pillow_heif` optional), sha256 stream, magic-number sniff with HEIF brands, 256 px JPEG thumbnail | REAL, small |
| `identity/normalize.py` | 96 | `pseudonymize`: HMAC-SHA256 truncated to 128 bits; local salt file; `normalize_sender` | REAL |
| `obs/run_artifacts.py` | 54 | `write_manifest`, which hashes the db | REAL |
| `utils/run_report.py` | 157 | Run report plus metrics JSONL | REAL |
| `utils/json_output.py` | 68 | Validate with Pydantic then JSON Schema; quarantine bad rows | REAL |
| `utils/logging.py` | 69 | `setup_logging` | REAL |
| `utils/config.py` | 342 | Pydantic-settings `Config`, Neo4j pool presets, "stella/cohere/legacy" providers, default Neo4j password `"password"` | REAL but DEAD (CLI never reads it; `--config` is ignored, TODO at `main.py:53`) |

### Schemas

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `schemas/message.py` | 76 | `CanonicalMessage`, `Reaction` (alias `from`), `Attachment`, `SourceRef` | REAL |
| `schemas/enrichment.py` | 79 | `EnrichmentMessage` | REAL, but a duplicate of `enrichment/models.py::MessageEnrichment` |
| `schemas/redaction.py` | 66 | Pydantic `RedactionReport`, `PrivacyPolicy` | DEAD in practice; `policy_shield.py` defines its own dataclasses with the same names |
| `schemas/validator.py` | 199 | Loads `<repo>/schemas/*.schema.json` via `Path(__file__).parents[3]/"schemas"`; `validate_data`, `quarantine_invalid_data`, `validate_pipeline_data` | REAL |

- **Schema path:** the validator resolves schemas relative to the source tree. That breaks for an installed wheel, because the hatch wheel includes only `src/chatx`.

### Transform and redaction

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `transformers/chunker.py` | 421 | `ConversationChunker`: turns (window 40, stride 10), daily, fixed (4000 chars). Text is `[YYYY-MM-DD HH:MM] ME|<contact>: text`. | REAL |
| `transformers/pipeline.py` | 230 | Normalize, chunk, validate and quarantine, save JSON/JSONL | REAL |
| `redaction/patterns.py` | 248 | Regex PII, tiny name list, hard-fail regexes, `ConsistentTokenizer` | REAL but shallow |
| `redaction/policy_shield.py` | 539 | `PolicyShield.redact_chunks`, `preflight_cloud_check`, DP summaries | REAL, flawed (section 5) |
| `privacy/differential_privacy.py` | 460 | Laplace/Gaussian count, sum, histogram, mean | REAL; only reachable from `policy_shield`, never from the CLI |

- **Chunker limits:** every non-"me" speaker is collapsed to the single `contact` string, so group chats are lost. `semantic` is declared in `ChunkMethod` but not implemented. `stride >= turns` makes the `range` step zero or negative.

### Enrichment

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `enrichment/ollama_client.py` | 509 | `ProductionOllamaClient`: httpx async `/api/chat` with `format=<json schema>`, tenacity retry, health monitor. Sets `OLLAMA_*` env vars in the client's own process (no effect on a running server). | REAL |
| `enrichment/enricher.py` | 418 | `MessageEnricher`: parses chunk text back into messages by regex, batches to Ollama, confidence gate, quarantine | REAL, fragile |
| `enrichment/models.py` | 260 | Pydantic models for enrichment, using pydantic v1 `@validator`/`@root_validator`/`class Config` | REAL, dated |
| `enrichment/multi_pass_pipeline.py` | 888 | 4-pass labeling against `config/labels.yml` | REAL code, BROKEN imports |
| `enrichment/image_enricher.py` | 187 | Returns hardcoded placeholder objects (`person` 0.85) and hardcoded psych labels; no model | STUB; tests assert the placeholders |
| `enrichment/llm_client.py` | 29 | `enrich_messages` returns `[]` with a TODO | STUB; exported by `enrichment/__init__.py` |

- **Fragile parsing:** `enricher._parse_chunk_text_to_messages` pairs lines to `message_ids[i]` by line index, so multi-line messages misalign.
- **Prompt bug:** `ollama_client.py:~244` builds `Sender: {"ME" if request.text else request.contact}`, which is "ME" whenever the text is non-empty.
- **Validator bug (likely):** `EnrichmentResponse.validate_result_xor_error` is a v1-style validator that reads `values.get('error')` while validating `error`. That looks wrong under Pydantic v2. No test covers it.

### Indexing

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `indexing/vector_store.py` | 522 | `ChromaDBVectorStore` (`PersistentClient`, telemetry off, SentenceTransformer embedding function) | REAL, CLI-live |
| `indexing/multi_vector_store.py` | 844 | `MultiVectorChromaDBStore`: four spaces; `custom_temporal` and `custom_structural` are placeholders mapped to `None` models; defines `PrivacyGate` | REAL partly, CLI-live |
| `indexing/pipeline.py` | 436 | `IndexingPipeline` wrapper | DEAD (no CLI or test callers) |
| `indexing/__init__.py` | 0 | Empty | n/a |

### Storage and embeddings

| Module | LOC | Responsibility | Grade |
|---|---|---|---|
| `storage/base.py` | 589 | Graph node/relationship dataclasses, `BaseGraphStore`, 47 `RelationshipTypes`, `PatternTypes` | REAL, DEAD to the CLI |
| `storage/graph.py` | 766 | `Neo4jGraphStore` | REAL, DEAD to the CLI (tests only) |
| `storage/psychology_relationship_mapper.py` | 569 | Label-to-relationship rule table | REAL data, DEAD to the CLI |
| `embeddings/{__init__,base,hardware,psychology,benchmarking}.py` | 25, 123, 175, 338, 626 | Provider ABC, GPU/MPS detection, mental-bert provider, benchmarks | REAL, DEAD to the CLI; `benchmarking.py:91` has a TODO |

- **Embeddings:** nothing in the CLI path imports `chatx.embeddings`. `psychology.py` loads `mental/mental-bert-base-uncased`, `nlpaueb/legal-bert-base-uncased` and `sentence-transformers/all-MiniLM-L6-v2`.
- **Storage:** nothing in the CLI path imports `chatx.storage` either.

TODO/NotImplemented hits are few: `cli/main.py:53, 93, 577, 859, 1344`, `enrichment/llm_client.py:28` and `embeddings/benchmarking.py:91`. Most of the weakness is wiring and quality, not explicit stubs.

## 2. CLI surface (`cli/main.py`)

Entry point: `chatx = chatx.cli.main:cli` (`pyproject.toml`).

Global options (callback, lines 35-55): `-v/--verbose` (count), `-q/--quiet`, `-c/--config` (accepted and ignored), `--version`.

| Command | Key options | What it calls | Status |
|---|---|---|---|
| `extract` (58) | `source`, `-o`, `-p`, `--dry-run`, `--error-format` | Prints "Extraction not yet implemented" | STUB |
| `transform` (98) | `input_file`, `-o`, `--format json\|jsonl`, `--chunk turns\|daily\|fixed`, `--contact`, `--turns`, `--stride`, `--char-limit`, `--validate` | `TransformationPipeline.transform` | WIRED, but the input contract mismatches extract output |
| `redact` (222) | `--salt-file`, `--threshold 0.995`, `--strict`, `--pseudonymize`, `--detect-names`, `--report`, `--preflight` | `PolicyShield.redact_chunks`, `save_redaction_report`, `preflight_cloud_check` | WIRED; threshold check is advisory (section 5) |
| `enrich` (365) | `--backend local\|cloud\|hybrid`, `--model gemma2:9b-instruct-q4_K_M`, `--tau`, `--tau-low`, `--tau-high`, `--max-concurrent`, `--timeout`, `--allow-cloud`. `--batch-size` is declared but never used. | `MessageEnricher` with `ProductionOllamaClient` | WIRED, local only |
| `analyze` (564) | `--type` | Prints "Analysis not yet implemented" | STUB |
| `enrich-multi` (581) | `--contact` (required), `--model`, `--taxonomy`, `--privacy-tier`, `--ollama-url` | `MultiPassEnrichmentPipeline` | BROKEN (import errors) |
| `index` (733) | `--contact`, `--store chroma\|multi`, `--collection`, `--multi-vector`, `--batch-size`, `--overwrite` | `ChromaDBVectorStore` or `MultiVectorChromaDBStore.index_chunks` | WIRED; `--overwrite` is never passed to the store |
| `query` (820) | `--contact`, `--k`, `--multi-vector`, `--psychology-weight`, `--temporal-weight`, `--since`, `--until`, `--labels-any/all/not`, `--privacy-tier`, `--insights` | `store.search` or `search_multi_vector` | WIRED; `labels-all` and `labels-not` are ignored (TODO line 859) |
| `pipeline` (1318) | `source`, `output_dir`, `--skip-*`, `--provider` | Prints "Pipeline not yet implemented" | STUB |
| `imessage pull` (974) | `--contact`, `--db`, `--from-backup`, `--backup-password`, `--out`, `--include-attachments`, `--copy-binaries`, `--thumbnails`, `--transcribe-audio local\|off`, `--report-missing`, `--error-format` | `imessage.extract_messages`, `stage_sms_db`, `write_messages_with_validation`, run report, metrics, manifest | WIRED end to end |
| `imessage audit` (1470) | `--db`, `--out`, `--contact` | `generate_missing_attachments_report` | WIRED |
| `imessage pdf` (1538) | `--pdf`, `--me`, `--ocr` | `extract_messages_from_pdf` | WIRED, thin |
| `instagram pull` (1361) | `--zip`, `--user`, `--author-only`, `--out`, `--error-format` | `extract_messages_from_zip` | WIRED |

Defects in the CLI file:
- **Late registration:** `if __name__ == "__main__": cli()` sits at line 1353, and the `instagram` Typer group, `imessage audit` and `imessage pdf` are registered after it. Running `python -m chatx.cli.main` will not register them. The installed `chatx` script imports the whole module, so it is unaffected.
- **Backup report bug:** in `imessage pull --from-backup`, `--report-missing` opens `db` (the default `~/Library/Messages/chat.db`), not the staged backup db (`main.py:1201`).
- **Encrypted backups:** `--backup-password` is only checked for presence. There is no decryption, so encrypted backups cannot be read (`backup.py: ensure_backup_accessible`).
- **Error handling:** `--error-format json` is honoured only on some commands. `audit` always emits a problem document for a missing db.

## 3. Pipeline reality

| Hop | Boundary format | Connected in code? |
|---|---|---|
| Extract to file | `CanonicalMessage` (Pydantic v2) dumped with `by_alias`, validated against `schemas/message.schema.json`, wrapped as `{messages,total_count,schema_version}` | Yes, with quarantine to `quarantine/messages_bad.jsonl` |
| File to `transform` | Expects a bare list or JSONL of `CanonicalMessage` dicts | Broken for the default wrapper (finding 2) |
| Transform to chunks | `ConversationChunk.to_dict()` (plain dicts), validated against `chunk.schema.json`; provenance `schema_v 0.1.0` | Yes. `meta.contact` is the raw `--contact` and is not redacted later. |
| Chunks to `redact` | Raw dicts; only `chunk["text"]` is touched | Yes. A chunk that raises (including a hard-fail) is dropped from the output and listed in `visibility_leaks`. A chunk with no text is passed through unchanged. |
| Redacted chunks to `enrich` | Dicts; the CLI checks for `provenance.redaction` in the first 5 chunks | Yes, but it only warns if redaction metadata is missing. Nothing blocks unredacted input. |
| `enrich` output | `enrichment/models.py::MessageEnrichment` as JSONL, validated by `enrichment_message.schema.json`. `schemas/enrichment.py::EnrichmentMessage` is a duplicate definition. | Yes. Requires a running Ollama and `tenacity`. |
| Enrichments to `index` | `index` reads chunks, not enrichments. `IndexingPipeline.update_chunk_enrichments` exists but nothing calls it. | **Not connected.** Enrichment output does not flow into the index in code. |
| Index to `query` | Chroma; embedding model downloaded from Hugging Face on first use | Yes. `index` does not check redaction or privacy tier. |
| Graph storage (Neo4j) and relationship mapper | None | Docs only. No CLI or pipeline code calls it. |
| Image enrichment | `image_enrichment.schema.json`, `enrichment/image_enricher.py` | Placeholder only. Not in the CLI. |
| DP summaries | `PolicyShield.generate_privacy_safe_summary` | Not called by any command. |

The `meta.labels_coarse` and `meta.labels_fine_local` fields exist in chunks but are only filled by `enrich-multi`, which is broken.

## 4. Dependencies, pins and hardcoded models

Python: `requires-python >=3.11`, ruff and mypy target 3.11, classifiers list 3.11 and 3.12. The repo's own interpreter here is 3.12.13.

### Runtime pins (`pyproject.toml`)
- **Core:**
  - `pydantic>=2.8,<3`, `pydantic-settings>=2.4,<3`
  - `click>=8.1`, `rich>=13`, `typer>=0.9`
  - `sqlalchemy>=2` (unused in `src/`), `python-dateutil>=2.8`, `pathvalidate>=3`, `jsonschema>=4`, `Pillow>=10`
  - `httpx>=0.27,<0.28`, `aiosqlite>=0.20,<0.21` (unused), `structlog>=24.4,<25` (unused)
  - `watchdog>=4,<5` (unused), `blake3>=0.4,<0.5` (unused), `numpy>=1.26,<3`
- **`llm` extra:** `openai>=1.0`, `anthropic>=0.8`, `chromadb>=0.4`. Neither the openai nor the anthropic SDK is imported anywhere in `src/`.
- **`local-llm` extra:** `ollama>=0.1`. The code talks to Ollama over raw httpx, so this SDK is unused.
- **`embeddings` extra:** `neo4j>=5.23,<6`, `sentence-transformers>=3.2.1,<4`, `transformers>=4.44.2,<5`, `torch>=2.4.1,<2.6`, `cohere>=5.5,<6` (unused), `accelerate>=1.2.1,<2`
- **`gpu-optimize` extra:** `bitsandbytes>=0.43.3,<0.44`
- **`wave3` extra:** the legacy bundle, which adds `scikit-learn` (unused) and `tenacity>=8.2`.
- **`dev` extra:** `pytest>=8.3,<9`, `pytest-cov`, `pytest-asyncio>=0.23,<1`, `coverage[toml]>=7.6,<8`, `testcontainers[neo4j]>=4.7,<5`, `ruff>=0.6.9,<1`, `mypy>=1.11,<2`, `pre-commit`, `mkdocs-material`, `pillow-heif>=0.14`, type stubs.

### Imported but undeclared
- `yaml` (PyYAML, `multi_pass_pipeline.py`)
- `tenacity` (in `ollama_client.py`, imported with a silent no-op fallback; declared only in the `wave3` extra, so a plain install loses retries)
- `psutil` (`embeddings/hardware.py`)
- `requests` (`constrained_dynamic_loader.py`)
- `fitz` and `PyPDF2` (PDF)
- `whisper` (openai-whisper) and `faster_whisper`

### Hardcoded models, endpoints and engines
- **Ollama:** `gemma2:9b-instruct-q4_K_M` appears at `cli/main.py:372, 586`, `ollama_client.py:52, 103` and `multi_pass_pipeline.py:33, 682`. The default URL is `http://localhost:11434`, using `/api/chat` and `/api/tags`.
- **Ollama decoding:** temperature 0, seed 42, `top_k` 1, `top_p` 0.1, `num_predict` 800, context 8192.
- **Cloud model string:** `claude-3-sonnet-20240229` (`multi_pass_pipeline.py:34`). It is a dated model id, and nothing calls it.
- **Embeddings:**
  - `all-MiniLM-L6-v2` (single-vector Chroma default and `embeddings/base.py`)
  - `all-mpnet-base-v2` (psychological space in `multi_vector_store.py`)
  - `mental/mental-bert-base-uncased`, `nlpaueb/legal-bert-base-uncased`, `sentence-transformers/all-MiniLM-L6-v2` (`embeddings/psychology.py`)
  - config presets name "stella", "cohere", "legacy" (`utils/config.py`)
- **Vector store:** ChromaDB `PersistentClient` at `./.chroma_db` and `./.chroma_multi_db`, cosine distance, telemetry off.
- **Whisper:** faster-whisper `small`/int8/CPU/beam 5 (`local_whisper.py`), and openai-whisper `base` (`transcribe.py:92`).
- **Graph:** Neo4j `bolt://localhost:7687`, default password `"password"` (`utils/config.py:176, 341`).
- **No OCR engine, EXIF reader beyond Pillow, or object-detector model is wired.** `image_enricher.py` is a stub.

### Dated or inconsistent patterns
- Pydantic v1 decorators and `class Config` in `enrichment/models.py:98-252` and `utils/config.py:184`. They still import under v2 but are deprecated and the validator logic is suspect.
- `.dict()` and `.json()` calls: `enricher.py:193, 391`, `extractors/base.py:110, 118`, `utils/config.py:287`.
- `datetime.utcnow()` in `privacy/differential_privacy.py` (6 places), `storage/base.py:200, 206` and `policy_shield.py:513`.
- `gemma2` default and `claude-3-sonnet-20240229` are old model ids.
- Pins are tight and old: `httpx <0.28`, `structlog <25`, `torch <2.6`, `watchdog <5`, `blake3 <0.5`.
- `typer` and `click` are both listed, but only `typer` is used.
- `typing.Optional/List/Dict` is used widely alongside `X | None`.
- Dependencies are mismatched between the extras. Several declared packages are unused, and several used packages are undeclared.

## 5. Privacy and security core

**`redaction/patterns.py` (regex only, no NER).**
- Regexes cover email, US and international phone, SSN, credit card (Luhn-checked), IP (range-checked), URL, street address, 5-digit ZIP, coordinates, and a few chat phrases ("my name is…", "call me…", birthday).
- Name detection is a hardcoded set of about 30 English names. It records the first occurrence of a repeated word as the position, so spans are wrong for repeats.
- The ZIP regex matches any 5-digit number.
- Overlap removal keeps the higher-confidence match.
- Hard-fail classes are about 6 demo-grade regexes (the code comment says "simplified patterns for demo").

**`ConsistentTokenizer`.**
- Tokens are `⟦TKN:TYPE:<sha256(text:type:salt)[:8]>⟧`, a plain salted hash with only 32 bits.
- With `--salt-file`, the salt is a hex string created on first use, written without a permission change.
- Without `--salt-file`, a fresh random salt is generated per run, so pseudonyms are not stable across runs.
- The DP RNG seed is derived from the first 8 bytes of that salt, which makes the noise reproducible from the salt.

**`identity/normalize.py` (cleaner).**
- Uses HMAC-SHA256 with a 32-byte random key from `$CHATX_SALT_FILE`, `~/.config/chatx/salt.key` or `~/.chatx_salt`. It creates the file if absent, with no chmod 600.
- `source_meta.sender_pid` is added at extraction, but `sender` and `sender_id` stay raw. The Instagram comment says "pseudonymized in PR-13", so that is deferred.
- The raw handle is therefore in `messages_*.json` and in chunk text before redaction.

**Coverage metric (`policy_shield._calculate_coverage`, lines 138-158).**
- It computes `(total_tokens − pii_tokens) / total_tokens`, the share of tokens that were not detected as PII.
- It does not compare against a ground truth, so it says nothing about how much real PII was caught. A chunk full of undetected PII scores 1.0.
- The overall figure is a plain mean of per-chunk scores.
- Short chunks with many PII spans drop below the threshold. Large ordinary chunks pass trivially.

**Enforcement of the 99.5% gate.**
- `redact_chunk_text` only logs a warning when coverage is below the threshold (line 193-194).
- The `redact` CLI prints a yellow warning and still writes the output and exits 0 (`main.py:298-303`).
- The only exit-1 path is `--preflight` with a failure (`main.py:348-350`).
- Nothing downstream (`enrich`, `index`, `query`) calls `preflight_cloud_check` or reads the `threshold_met` flag.
- `strict` raises the threshold to 0.999 but is equally advisory.

**Hard-fail handling.** With `block_hard_fail=True`, `redact_chunk_text` raises. `redact_chunks` catches it, drops the chunk, and adds it to `visibility_leaks`. The `hardfail_triggered` flag is only set when `block_hard_fail=False`, which is the opposite of what the report field suggests.

**`--allow-cloud`.**
- `enrich` rejects `cloud` or `hybrid` without the flag, then (with the flag) prints "not yet implemented" and forces `backend = "local"` (`main.py:407-413`).
- There is no cloud client in `src/`.
- `utils/config.py: allow_cloud` is never read.
- The `--privacy-tier` option in `enrich-multi` and `query` is a label filter only.
- `multi_vector_store.PrivacyGate` and `policy_shield.preflight_cloud_check` define "cloud-safe" label logic, but nothing connects either to a network call.
- What actually keeps data local today is that no remote LLM code exists. The one network call outside localhost is the Hugging Face model download by sentence-transformers or Chroma.

**`privacy/differential_privacy.py`.**
- Implements Laplace and Gaussian mechanisms for count, sum, histogram and mean with `numpy.random.Generator(PCG64)`, which is not a secure RNG.
- The budget tracker only sums epsilon per query id and never refuses a query once a budget is exhausted.
- `aggregate_statistics_with_dp` splits epsilon evenly across queries.
- It is only reachable through `PolicyShield.generate_privacy_safe_summary` and `aggregate_statistics_with_dp`, and nothing calls either (the CLI never does).

## 6. Tests

`tests/` has 68 `.py` files, about 10.3k lines.

Mapping of tests to modules:
- **iMessage:** `tests/imessage/*` (about 35 files), `tests/integration/test_imessage_extraction.py`, `tests/fixtures/*` (synthetic `imessage_test_data.sql`, `Attachments/audio.m4a`, `photo.jpg`, a tiny HEIC generator, Instagram builders). Good coverage of time, reactions, replies, backup mode, attachments, dedupe, thumbnails, transcription (mocked), missing report and audit CLI.
- **Instagram:** `tests/instagram/*` (ZIP and golden schema).
- **PDF:** `tests/imessage/test_pdf_ingest.py`, with injected text only.
- **Media:** `tests/media/*` (14 lines each).
- **Identity:** `tests/identity/test_normalize.py`.
- **Observability and CLI errors:** `tests/obs`, `tests/utils`, `tests/cli/test_error_model.py`, `tests/validate/test_quarantine_exit.py`, `tests/unit/test_run_report_metrics.py`.
- **Redaction and DP:** `tests/unit/redaction/test_policy_shield.py` (397 lines), `tests/unit/privacy/test_differential_privacy.py` (536), `tests/test_differential_privacy.py` (247, partly duplicate). These test internal functions, not recall on labelled PII.
- **Storage and embeddings:** `tests/unit/storage/*` (Neo4j with mocks, mapper) and `tests/unit/embeddings/*`. These test modules the CLI never reaches.
- **Parallel extractor:** `tests/unit/test_extractors.py`, `tests/imessage/test_text_decoding.py`.
- **Image enrichment:** `tests/image_enrich/*` (placeholders).
- **Perf:** `tests/perf/test_extract_perf.py` (skipped unless `CHATX_RUN_PERF=1`).

Modules with no direct tests:
- `transformers/chunker.py` and `transformers/pipeline.py`
- `enrichment/enricher.py` and `enrichment/ollama_client.py`
- `enrichment/multi_pass_pipeline.py`
- `enrichment/llm_client.py`
- `indexing/vector_store.py`, `indexing/multi_vector_store.py`, `indexing/pipeline.py`
- `transcribe/local_whisper.py` (only an 18-line check in `tests/imessage/test_transcribe_local.py`)
- `media/thumbnail.py` (covered indirectly)
- `cli/main.py` for `transform`, `redact`, `enrich`, `index`, `query`

Test files that are empty or do not test the product:
- `tests/test_policy_shield.py` is 0 lines.
- `tests/unit/hooks/*` (4 files, about 950 lines) import from `.claude/hooks` by `sys.path` and test Claude Code hook scripts. This is tooling, not product.
- `tests/unit/mcp/test_constrained_loader.py` (755 lines) tests `constrained_dynamic_loader.py`, which is also tooling.

Skips and xfails: only `tests/unit/mcp/test_constrained_loader.py:671` (skip if no servers) and the perf gate. No `xfail`.

Config (`pyproject.toml`): `testpaths=["tests"]`, strict markers, `--cov=src/chatx`, `--cov-fail-under=90`. Excluded from coverage via `omit` are `redaction/*`, `transformers/*`, `enrichment/*`, `indexing/*`, `schemas/validator.py`, `transcribe/local_whisper.py` and `__main__.py`. The 90% figure is therefore computed over the extraction side plus the unused storage and embeddings modules.

## 7. Root-level oddities

Tooling debris, not product:
- `test_integration.py` is a script (imports `src.chatx...`, prints emoji status) for the multi-vector store. It is outside `testpaths`, so pytest does not collect it.
- `QUICK_VERIFICATION.py` is the same kind of script, for DP and PolicyShield.
- `test_zen.json` and `test_taskmaster.json` are two lines each of sample hook-event payloads for the Claude Code hooks.
- `patch.diff` is a 15-line diff to `PROJECT_INSTRUCTIONS.md` that renames a `gap` shell alias to `gclip`. It is unrelated to the code.
- `CLAUDE.md.backup` (170 lines) is the older copy of `CLAUDE.md` (299 lines). `AGENTS.md` (82) and `llms.md`/`llm-context.md` are agent context files.
- `node_modules/` has 9 tracked files (dotenv only), left over from a Node tool.
- `.serena/` (tracked: `project.yml` plus 3 memory notes) and `context_portal/` (tracked: alembic files; `context.db` is untracked) are MCP-tool state.
- `.taskmaster/` (7 tracked files) holds the Task Master tasks and PRDs.
- `.claude/` has 192 tracked files: agents, hooks, MCP config, workflows. It is the largest area of the repo.
- `awesome-claude-code/` and `claude-platform-evolution/` are untracked directories.
- `htmlcov/`, `site/`, `.coverage` and `.env` are gitignored, so they are untracked.
- `scripts/` holds MCP and git-hook helpers.
- Git history has 151 commits. Recent ones are about governance docs, MCP optimization and hooks, not chat analysis.

Product-adjacent but not code: `config/labels.yml` (469 lines, the taxonomy), `config/arch-gates.yml`, and `docs/` (48 files). `docs/` claims more than the code does; I did not audit it line by line.

## 8. Reusable assets (my judgment)

**Keep or port (domain logic with tests):**
- `imessage/time.py`: Apple epoch conversion with unit inference. Small and tested, but re-verify the ns/µs heuristic against real data.
- `imessage/db.py`: the safe read-only copy of the db plus WAL/SHM.
- `imessage/backup.py`: the `Manifest.db` fileID to hashed-path logic and the staging. Unencrypted only. The new design must decide how to handle encrypted backups.
- `imessage/extract.py`: the structure of "fold reactions into parents, resolve replies by guid, then attachments". Fix the `is_from_me` scope bug first, and re-derive the reaction type codes.
- `imessage/attachments.py`, `media/*`, `imessage/report.py`: attachment metadata, dedupe, thumbnails, missing-file report. These have solid tests.
- `instagram/extract.py`: the zip-slip guard and the streaming read. Add the mojibake repair.
- `schemas/message.py` plus `schemas/message.schema.json` and `schemas/chunk.schema.json`: the canonical-message contract, with a single source of truth to be chosen between Pydantic and JSON Schema.
- `identity/normalize.py`: HMAC pseudonymization (add file permissions).
- `utils/json_output.py` and `cli_errors.py`: quarantine plus RFC7807 error pattern.
- `transformers/chunker.py`: the three chunking strategies, after adding tests and fixing group-chat collapse.
- Test fixtures (`tests/fixtures/*`, `imessage_test_data.sql`) and the 35-file iMessage suite.
- `config/labels.yml` (the taxonomy) and `schemas/*.json`.

**Port with real rework:**
- Regex patterns in `redaction/patterns.py`: the regexes are a starting point, but need a proper recall evaluation set, NER or an equivalent, and a coverage metric that measures what it claims.
- `PolicyShield` structure (policy object, report, preflight): keep the idea, but make the threshold a hard gate that downstream stages enforce.
- `differential_privacy.py`: the Laplace/Gaussian mechanisms are standard; add budget enforcement and a secure RNG if it is going to be used at all.
- `ollama_client.py`: the retry, semaphore and schema-constrained `format` call pattern. Replace the model name, fix the prompt bug, and use `ollama`'s current structured-output API.

**Replaceable scaffolding / discard:**
- `cli/main.py` command bodies (about 1570 lines of repeated load/print code); the `extract`, `analyze` and `pipeline` stubs; the late-registration layout.
- `enrichment/llm_client.py`, `enrichment/image_enricher.py` (placeholders), `multi_pass_pipeline.py` (broken imports; the taxonomy and pass design may inform a rewrite).
- `enrichment/models.py` (pydantic v1 style) and the duplicate `schemas/enrichment.py`.
- `extractors/*` (the second iMessage extractor), `indexing/pipeline.py`, `utils/config.py`.
- `storage/*`, `embeddings/*` and `constrained_dynamic_loader.py`: large, tested, unreachable from the CLI, and the Neo4j and benchmarking layers are well beyond what the pipeline needs today. The relationship-type tables in `storage/base.py` and the mapper rules are content worth reading, not code worth keeping as is.
- `.claude/`, `.serena/`, `.taskmaster/`, `context_portal/`, `node_modules/`, `patch.diff`, `test_*.json`, root scripts.

**Unverified:** the real behaviour of `attributedBody` on genuine messages, the correct tapback codes, the model-validation logic in `EnrichmentResponse`, and whether anything in `docs/` matches the code. All of these need a run against real data or a real model.
