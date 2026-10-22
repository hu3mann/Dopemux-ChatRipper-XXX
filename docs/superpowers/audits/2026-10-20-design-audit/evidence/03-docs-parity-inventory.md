# ChatX documentation parity checklist

All paths below are relative to `/Users/hue/code/Dopemux-ChatRipperXXX`. No `docs/adr/**`, `docs/lab/**`, `docs/specifications/**`, `docs/psychology/**` or `docs/privacy*/**` directories exist. The equivalents are `docs/design/adrs/`, `docs/design/specifications/` and `docs/psychology-analysis.md`.

Abbreviations:
- **ARCH** = docs/architecture.md
- **IFC** = docs/interfaces.md
- **NFR** = docs/operations/non-functional-requirements.md
- **IMPL** = docs/implementation.md
- **ACC** = docs/acceptance-criteria.md
- **CE** = docs/design/specifications/cloud-enrichment.md
- **IMG** = docs/design/specifications/image-enrichment.md

Status codes:
- **REAL**, **BROKEN-HO** (wired but broken hand-off), **ADVISORY**, **STUB**, **DEAD** (dead to CLI), **ABSENT**: the prior audit grades.
- **UNKNOWN**: not covered by the grades.

## 1. Capability table

| Capability claimed | Strongest citation | Status | Note |
|---|---|---|---|
| **Extract** | | | |
| iMessage chat.db extraction (WAL copy, read-only) | docs/design/specifications/imessage-extractor.md:19 | REAL | |
| Reactions folded (assoc 2000–2005), stable `reply_to_msg_id` | imessage-extractor.md:23-24; ACC:11 | REAL | |
| Attachment metadata and `--copy-binaries` | imessage-extractor.md:25 | REAL | |
| iPhone backup mode (`--from-backup`, Manifest.db, password) | IFC:279 | REAL | |
| `imessage audit` / `missing_attachments.json`, exit 0 | ACC:79-87 | REAL | |
| Instagram ZIP (`--user`, `--author-only`, Zip Slip block) | docs/how-to/instagram-zip.md:5-15 | REAL | |
| PDF ingest, text layer | docs/how-to/pdf-ingestion.md:7 | REAL | |
| PDF OCR fallback (`--ocr`) | IFC:24; README:42 | ABSENT | Audit: no OCR engine |
| WhatsApp JSON/TXT extractor (`chatx whatsapp pull`) | IFC:25 | ABSENT | README:75 and IMPL:149 say "Planned" |
| Generic TXT extractor | README:76 | ABSENT | |
| attributedBody normalization, raw kept in `source_meta.raw` | docs/plans/extractor-hardening.md:78-80 | UNKNOWN | |
| Attachment SHA-256 hashing and dedupe map | docs/plans/wave2.md:11,29 | UNKNOWN | |
| Identity pseudo-IDs (HMAC, `sender_pid`) | wave2.md:10,138 | REAL | |
| iCloud download automation | docs/design/next.md:6 | ABSENT | Docs say manual only |
| **Transform / chunk** | | | |
| `chatx transform --chunk turns:40 --stride 10`, deterministic | ACC:16-22; docs/design/adrs/0002-default-chunking-strategy.md:11 | REAL | |
| Daily-window fallback for sparse periods | ADR-0002:11 | UNKNOWN | |
| extract → transform hand-off | AGENTS.md:22 | BROKEN-HO | Wrapper mismatch |
| **Redact / privacy** | | | |
| Pseudonymize (ME / CN_id6) and opaque tokens ⟦TKN:…⟧ with salt file | NFR:69-70 | REAL | |
| Regex PII redaction | ARCH:36 | REAL | Docs imply more than regex ("PII detection", IMPL:170) |
| Coverage gate ≥0.995 / ≥0.999 strict, blocks cloud | ACC:29-31; ARCH:103 | ADVISORY | Warns, exits 0 |
| `redaction_report.json` | AGENTS.md:26 | REAL | |
| Hard-fail class (CSAM) block, `E_HARDFAIL_CLASS` | NFR:72-73; ARCH:105 | ABSENT | |
| `chatx preflight cloud` | IFC:30 | ABSENT | |
| Prompt linter, `E_VISIBILITY_LEAK`, `E_ATTACHMENT_PRESENT` | NFR:67 | ABSENT | Only in config/arch-gates.yml:49-68 |
| Differential privacy (ε=1.0, δ=1e-6, `--enable-dp`) | IFC:239-265 | DEAD | |
| **Enrich-local** | | | |
| `enrich messages\|units --backend local` (gemma, τ gate, hysteresis) | IFC:32-36; ACC:41-48 | BROKEN-HO | Enrichments do not reach the index |
| Multi-pass 4-pass enrichment (`enrich-multi`) | IMPL:225-230, 267 | BROKEN-HO | Import error |
| Message and CU enrichment schemas with provenance/shield/merge | CE:38-231 | UNKNOWN | JSON-schema validation is REAL generally |
| Cache keyed (model_id, sha, prompt_hash, source_hash, schema_v), ≥80% hit | NFR:121 | UNKNOWN | |
| **Enrich-cloud** | | | |
| `--backend cloud\|hybrid`, `--allow-cloud`, ±2 turns, ≤800 tokens | CE:25-27 | ADVISORY | No cloud client exists |
| Token-preserving cloud reconstruction | ADR-008:54-64 | ABSENT | |
| `--qps`, `--concurrency`, `--batch` | NFR:124 | ABSENT | |
| **Index / search** | | | |
| `chatx index --store chroma --collection chatx_<contact>` | IFC:41 | UNKNOWN | Index command not graded; indexing wrapper is DEAD |
| `chatx index update` (metadata merge, no re-embedding) | IFC:281-320 | ABSENT | |
| Multi-vector psychology-aware search | IMPL:242-245 | DEAD | |
| **Query / report** | | | |
| `chatx query` with citations | ACC:33-39; IFC:55 | UNKNOWN | Not graded |
| `simulate`, `reply` | IFC:56-57 | ABSENT | |
| HTTP `/v1/query\|simulate\|reply` (loopback, 60s, `X-Request-Id`) | IFC:152-224; ACC:50-57 | ABSENT | IMPL:377 agrees |
| `chatx analyze`, `chatx pipeline` | README:46; ADR-008:96 | STUB | |
| `timeline show`, `factors analyze`, `tokens inspect`, `backfill` | IFC:60-62, 48 | ABSENT | |
| **Graph / relationships** | | | |
| Neo4j temporal graph (12 relationship types, 6 patterns) | docs/psychology-analysis.md:42-56 | DEAD | |
| `label build`, `issues build`, `episodes detect`, `issues graph build` | IFC:44-47 | ABSENT | |
| Hybrid Chroma+Neo4j forensic query engine | ADR-008:66-74 | ABSENT | |
| **Psychology** | | | |
| mental-bert psychology embeddings | psychology-analysis.md:27-35 | DEAD | |
| `PsychologyLabelMapper` (470+ labels to relationships) | ADR-008:31-41 | ABSENT | psychology-analysis.md:169 says "In Development" |
| labels.yml two-tier taxonomy | config/labels.yml:8-14 | UNKNOWN | Config file exists; code use not graded |
| **Image / audio** | | | |
| Image pipeline (OCR, YOLOv8, Florence-2, pHash, CLIP, Qwen2.5-VL psych) | IMG:28-58 | STUB | Hardcoded placeholders |
| `image_enrichment.jsonl` sidecar and schema | IMG:60 | UNKNOWN | |
| Local transcription (`--transcribe-audio local`, faster-whisper) | ADR-0017:9; docs/how-to/transcription-local.md:6 | STUB | |
| **Storage** | | | |
| `./out/` tree: raw, messages, chunks, redacted, enriched, indexed, reports, cache | ARCH:86-96 | UNKNOWN | Differs from artifacts named elsewhere |
| Quarantine `out/quarantine/messages_bad.jsonl` | docs/extractor_readiness.md:26 | REAL | |
| `BaseVectorStore` / `BaseLLMClient` / `BaseExtractor` extension points | ARCH:146-161 | UNKNOWN | |
| **CLI / MCP** | | | |
| RFC-7807 `--error-format json\|text` | docs/design/adrs/0018-cli-error-model-rfc7807.md:38 | REAL | |
| `chatx ingest` / `reindex` deprecated aliases | IFC:66-69 | ABSENT | |
| `chatx export run`, `--self-test`, `--dry-run` | NFR:151,111 | ABSENT | |
| MCP servers and `scripts/mcp/*` | AGENTS.md:50-58 | UNKNOWN | Tooling, not product |
| **Ops / observability** | | | |
| `manifest.json`, `run_report.json`, `metrics.jsonl` | AGENTS.md:25; wave2.md:108-109 | REAL | |
| Per-record provenance/shield fields | NFR:85-86 | UNKNOWN | |
| Structured JSONL logs, rotation, cloud-call logging | ARCH:125-128; NFR:89 | UNKNOWN | |
| Token ledger, cost tracking | ARCH:134; test-strategy.md:34 | ABSENT | |
| Perf smoke (`CHATX_RUN_PERF=1 pytest -m perf`) | docs/development/developer-guide.md:43 | UNKNOWN | |
| CI arch-gates (config/arch-gates.yml) | arch-gates.yml:1-86 | UNKNOWN | Uses `chatx validate`, `chatx metrics summarize` (ABSENT); several steps end `\|\| true` (:43,47,76) |

## 2. Contractual numbers and hard constraints

| Promise | Citation | Status |
|---|---|---|
| Redaction coverage ≥0.995 (0.999 strict) | ACC:30; NFR:24; IFC:273; CE:26 | ADVISORY |
| Block cloud below threshold | NFR:170 | ADVISORY |
| Test coverage ≥90% new code | AGENTS.md:20,36; NFR:130 | UNKNOWN (process gate) |
| Test coverage ≥60% repo-wide | extractor_readiness.md:41; IMPL:463; IMG:135 | UNKNOWN |
| Model: gemma-2-9b-q4_K_M, temp ≤0.3, no streaming, fixed seed | NFR:9; IFC:10 | UNKNOWN |
| Model temp=0 | NFR:29; IMPL:222 | UNKNOWN |
| τ=0.7, τ_low=0.62, τ_high=0.78 | IFC:271; NFR:11 | UNKNOWN |
| Chunking turns:40 stride:10, daily fallback | ADR-0002:11 | REAL |
| Context ±2 turns, `max_output_tokens` ≤800 | NFR:34 | ABSENT (no cloud) |
| Extraction ≥5k msg/min | ARCH:167; test-strategy.md:38 | UNKNOWN |
| Ingest and transform ≥10k msg/min; chunk ≥50k/min | NFR:19-20 | UNKNOWN |
| Redaction preflight 100k msgs ≤120s | NFR:25 | UNKNOWN |
| Local enrich ≥25 msg/s, p95 ≤250 ms | NFR:29 | UNKNOWN |
| Cloud batch of 100 ≤90s | NFR:35 | ABSENT |
| Index 50k msgs ≤90s | NFR:39 | UNKNOWN |
| Retrieval p95 ≤150 ms | NFR:40 | UNKNOWN |
| Query <5s over 100k messages | ARCH:169 | UNKNOWN |
| Memory <4GB for 1M messages; peak RSS ≤75% | ARCH:170; NFR:45 | UNKNOWN |
| Checkpoint every ≤10k messages | NFR:44 | ABSENT |
| Cache hit ≥0.80 | NFR:103 | UNKNOWN |
| Index metadata update 25k upserts/min | IFC:320 | ABSENT |
| HTTP request ≤60s | IFC:158 | ABSENT |
| STT: ≥1.5x realtime CPU, ≤2s per 30s clip, ≤2GB RSS | ADR-0017:16-20 | STUB |
| Image: pHash Hamming ≤6, screenshot OCR ≥80% tokens | IMG:140-143 | STUB |
| Image VLM temp 0.1, top_p 0.9 | IMG:98 | STUB |
| DP defaults ε=1.0, δ=1e-6 | ARCH:110 | DEAD |
| Schema valid 100%, invalid quarantined | NFR:177 | REAL |
| Error format RFC-7807, exit code 1 | ADR-0018:11 | REAL |
| Schema versions: `schema_v` "1.0.0" in CE:65; labels.yml `schema_version: 1.2` (labels.yml:8); image `schema_v:"1"` (IMG:83) | | UNKNOWN |
| Manual QA sample 1–2% | NFR:183; CE:237 | ABSENT |
| Attachments never uploaded | ARCH:119; AGENTS.md:46 | REAL (no cloud client exists, so vacuously) |
| Python 3.11+ | AGENTS.md:19; contributing.md:5 | UNKNOWN |
| Support macOS (Apple Silicon and Intel) and Linux x86_64 | NFR:142 | UNKNOWN |

## 3. Stale references (specific models, libraries, services, versions)

| Reference | Citation(s) | Count |
|---|---|---|
| `gemma-2-9b-q4_K_M` / `gemma-2-9b` | IFC:10,33,36; NFR:9; IMPL:221 | 5 |
| `gemma2:9b` | docs/design/next.md:13 | 1 |
| `gemma:2-9b-q4_K_M` (invalid Ollama tag form) | developer-guide.md:8 | 1 |
| "gemma2 by default" | docs/research/image-enrichment.md:53 | 1 |
| Ollama | ARCH:155; IMPL:220; implementation-plan.md:173 | ~5 |
| Cloud providers (`openai`, `anthropic`; no model id) | CE:69,190 | 2 |
| "Sonnet or Opus", PluggedIn router | docs/development/repo-prompt.md:33 | 1 |
| ChromaDB / Chroma | ARCH:28,36,159; IMPL (many); IFC:41,305; implementation-plan.md | ~25 |
| Neo4j | IMPL:49,347; ADR-008; psychology-analysis.md; docs/DEV_DOCS_CRAWL.yml:28 | ~12 |
| `all-MiniLM-L6-v2` | IMPL:237 | 1 |
| `mental/mental-bert-base-uncased` | IMPL:348; psychology-analysis.md:30; ADR-008:13 | 3 |
| Stella-1.5B-v5, Cohere v3.0 | docs/SESSION_SUMMARY.md:38,81 | 2 |
| `nomic-embed-text` | research/image-enrichment.md:54 | 1 |
| Qwen2.5-VL 7B, LLaVA-NeXT, InternVL 2.5 | IMG:90-96; research/*.md | ~8 |
| Florence-2 (OpenVINO/ONNX), YOLOv8-s/v9, SAM, OpenCLIP, Tesseract, pillow-heif | IMG:36-52 | 1 each |
| faster-whisper (CTranslate2), whisper.cpp, whisperx; env `CHATX_STT_*` | ADR-0017; ADR-0003:14; transcription-local.md | ~6 |
| OCRmyPDF, PyMuPDF/pypdfium2 | wave2.md:123 | 1 |
| pgvector, Weaviate | ARCH:160 | 1 |
| Pydantic >=2.5, typer >=0.9, chromadb >=0.4, sqlalchemy >=2.0, ollama >=0.3, sentence-transformers >=2.2.2, torch >=2.0 | IMPL:469-489 | 7 |
| Typer + Rich | IMPL:42; implementation-plan.md | 3 |
| FastAPI | repo-prompt.md:7 | 1 |
| Python 3.11 | AGENTS.md:19; arch-gates.yml:17; contributing.md:5; developer-guide.md:6 | 4 |
| Repo URL `hue/Dopemux-ChatRipperXX` (two X; the repo has three) | README:20,139 | 2 |
| Uppercase file names: ARCHITECTURE.md, INTERFACES.md, NON_FUNCTIONAL.md, ACCEPTANCE_CRITERIA.md, CLOUD_ENRICHMENT.md, IMESSAGE_SPEC.md, TEST_STRATEGY.md, NEXT.md, `SCHEMAS/` | NFR:189-193; imessage-extractor.md:9; developer-guide.md:52 | ~10 |
| ADR path `docs/adr/` (ADRs actually live in `docs/design/adrs/`) | ADR-0001:11 | 1 |
| `docs/ADR-0017-transcription-engine.md` | wave2.md:70 | 1 |
| ADR-0016 (PDF) cited; file absent | wave2.md:17 | 1 |
| "ADR-001" and "ADR-003 (Privacy Shield)" cited; files absent (ADR-0003 is transcription) | ADR-008:7,171 | 2 |
| MkDocs and GitHub Pages deploy | README:84-86,125 | 2 |
| Commitizen / semantic release | docs/reference/changelog.md:4 | 1 |

## 4. Contradictions

| Topic | Side A | Side B |
|---|---|---|
| Missing-attachments file name | `missing_attachments.json`: AGENTS.md:27, ACC:85, ARCH:138 | `missing_attachments_report.json`: developer-guide.md:31 |
| Message output path | `out/messages.jsonl`: ACC:20, IFC:28 | `out/messages_<contact>.json`: iphone-backup.md:22; `out/instagram_messages.json`: instagram-zip.md:18; `out/raw/*.json`: developer-guide.md:45 |
| Run summary and metrics files | `run_summary.json`: ARCH:139; `out/metrics/*.jsonl`: NFR:105 | `run_report.json`: AGENTS.md:25; `out/metrics.jsonl`: iphone-backup.md:24 |
| Transcript field | `source_meta.transcript`: ACC:76; ADR-0003:16 | `source_meta.transcripts[]`: imessage-extractor.md:27 |
| Transcription engine | ADR-0003: mock/whisper, Accepted | ADR-0017: faster-whisper, "Proposed"; how-to presents it as the default |
| Local-model temperature | ≤0.3: NFR:9 | =0: NFR:29; IMPL:222 |
| Test coverage gate | ≥90%: AGENTS.md:20 ("required gates") | ≥60%: extractor_readiness.md:41; IMG:135 |
| Extraction throughput | ≥5k msg/min: ARCH:167 | ≥10k msg/min: NFR:19 |
| Query latency | p95 ≤150 ms: NFR:40 | <5s: ARCH:169; ADR-008:138 |
| `certainty` / `directness` type | float: IFC:95 | `{"val":0.0}`: IFC:133 |
| `inferred_meaning` limit | ≤25 words: IFC:99 | ≤200 chars: IFC:134; CE:109 |
| "RFC-7807" error shape | `type,title,status,detail,instance,code`: ADR-0018:28; IFC:335 | `error,code,detail,hint`: IFC:161,229 |
| Error code naming | `MISSING_DB`: ADR-0018:19 | `E_MISSING_DB`, `E_INVALID_INPUT`: implementation-plan.md:18; `MISSING_MANIFEST_DB`: extractor-hardening.md:69; `E_*`: NFR:160 |
| CLI error model status | Accepted: ADR-0018:3 | "Missing" for PR-X5: extractor_readiness.md:35 |
| WhatsApp | canonical `chatx whatsapp pull`: IFC:25; NFR:19 MUST parse | Planned: README:75; IMPL:149 |
| HTTP API | specified with 60s SLA: IFC:152; ACC:50 | Not yet implemented: IMPL:377 |
| Differential privacy | production ready: SESSION_SUMMARY.md:116; IMPL:322 | Phase 3 "completion": implementation-plan.md:117-125 |
| PDF OCR | complete: README:42 | "needs OCR integration": IMPL:357; "when configured": pdf-ingestion.md:15 |
| `enrich` / `index` invocation | `enrich messages --contact`; `index --store chroma --collection`: IFC:32,41 | `enrich --input`; `index --contact`: IMPL:262-263 |
| Label counts | 53 coarse / 100+ fine / 470+ constructs: psychology-analysis.md:18-19; ADR-008:15 | labels.yml: 55 coarse, 99 fine leaves (my count) |
| Pseudonym token form | `⟦TKN:<id8>⟧`: CE:240 | `⟦TKN:PERSON_A⟧`: ADR-008:60; psychology-analysis.md:127 |
| Psychology/Neo4j status | "Foundation complete": psychology-analysis.md:163-166; IMPL:346-350 | Hybrid query, mapper "PLANNED": IMPL:370-373 |
| Chunk default | ADR-0002:7 notes earlier docs said turns:20 | Now consistently 40; no live conflict found |
| Hash/doc layout | ARCH:86-96 tree (raw/, messages/, chunks/…) | Not used by any how-to |

## 5. Pure planning / wish-list docs

| Doc | Reason |
|---|---|
| docs/design/adrs/ADR-008-psychology-graph-integration.md | Names classes and a `chatx graph` command that do not exist (CLI "Phase 3"); a 7–10 week timeline |
| docs/psychology-analysis.md | Illustrative `hybrid_engine` code only |
| docs/design/specifications/image-enrichment.md | Status "Proposed"; the planned modules are only in a PR list |
| docs/research/image-enrichment.md, docs/research/image-psychology-model-research-plan.md | Research plan, pending Exa; no decision |
| docs/implementation-plan.md | Phased sprint plan with unchecked boxes |
| docs/plans/wave2.md | PR queue; PR-10 to PR-20 are partly delivered |
| docs/plans/extractor-hardening.md | Codex prompt and PR list, mostly delivered |
| docs/design/adrs/0004-acquisition-ux-imessage-icloud-usb.md | Proposed; the `--from-backup` it calls "future" now exists |
| docs/design/adrs/0017-transcription-engine-faster-whisper.md | Proposed; SLAs are targets |
| docs/design/next.md | Open-questions log |
| docs/SESSION_SUMMARY.md | Agent session handoff note |
| docs/dopemux-mvp-research.md | Unrelated Dopemux agent-orchestrator plan; no ChatX content |
| docs/reference/workflow/taskmaster-integration.md | Copy of the TaskMaster guide; tooling only |
| docs/agent-workflows.md, docs/repo-prompt-xml.md, docs/development/repo-prompt.md, docs/DEV_DOCS_CRAWL.yml, docs/reference/commands/index.md | Contributor/agent tooling, not product |
| docs/policy/pr.md | Empty file (0 lines) |

## NOT VERIFIED

- I did not read `docs/reference/workflow/taskmaster-integration.md` or `docs/dopemux-mvp-research.md` beyond headings and the first ~3 KB. I read `docs/research/image-psychology-model-research-plan.md` only to about line 60 of 81.
- I read `config/labels.yml` only at its head, its tail and the section boundaries. The coarse (55) and fine (99) counts are from `awk` indentation heuristics, not a parse.
- I did not verify whether `schemas/*.json` files named in the docs exist, because the scope excluded `src/` and I did not check `schemas/` itself.
- Statuses marked UNKNOWN are not covered by the audit grades. These include `index` and `query` as CLI commands, attachment hashing, attributedBody normalization, the cache, provenance fields and perf smoke. I applied ABSENT only where the grade rule clearly covers the item.
- I cannot confirm whether `config/arch-gates.yml` runs anywhere. It sits in `config/`, not `.github/workflows/`.
- I did not check whether `docs/policy/pr.md` is intentionally empty.
- I did not verify whether README links such as `CLAUDE.md` and `LICENSE` resolve.
