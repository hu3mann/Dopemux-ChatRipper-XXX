# ChatX Rearchitecture — Design

| | |
|---|---|
| Status | Draft for approval (brainstorm output; nothing built yet) |
| Date | 2026-10-20 |
| Owner | Houston (product); supervisor session (design) |
| Supersedes as statement of intent | `docs/architecture.md`, `docs/interfaces.md`, `docs/implementation.md`, `docs/operations/non-functional-requirements.md`, `docs/acceptance-criteria.md`, ADR-008 |
| Evidence base | Code-reality audit of `src/chatx` (2026-10-20), dNh_CRM ingest trace (2026-10-20), docs parity inventory (2026-10-20). Condensed in Appendix A. |

Reading guide: §3 holds the decisions already made and why. §11 lists what is deliberately left to the builder. §12 lists the few things only the owner can answer. Anything marked **UNKNOWN** is unverified and must be resolved by measurement, not assumption.

---

## 1. Intent

ChatX is a **local-first forensic chat tool for one person's own message history**. It pulls messages out of iMessage (live `chat.db` or an iPhone backup), Instagram exports, WhatsApp exports, PDF transcripts and email; turns them into a single canonical record with evidence-grade provenance; redacts them behind a privacy gate that actually blocks; and then supports search, structured enrichment, relationship/psychology analysis and reports — locally by default, with cloud models allowed only through the gate.

Two things changed since the current code was written:

1. **The code never delivered the pipeline.** Extraction is real and well tested; every later stage is stubbed, dead to the CLI, or wired with a broken hand-off (Appendix A.1). The ≥99.5 % redaction "coverage" gate is a token ratio that warns and exits 0. `--allow-cloud` guards a cloud client that does not exist.
2. **The stack is dated and duplicated.** Hardcoded `gemma2:9b`, Chroma + Neo4j, Pydantic-v1 idioms, a `claude-3-sonnet-20240229` literal. Meanwhile the sibling repo **dNh_CRM** grew its own iMessage/WhatsApp/email parsers — including a *real* `attributedBody` typedstream decoder that ChatX lacks — but has no reactions, replies, inline attachments or outbound messages, which ChatX has.

So this is a rebuild around one shared extraction core, a privacy gate that is a real gate, and a storage/model layer that matches current offerings and the owner's actual machine.

### Success looks like

- One command imports a real `chat.db` (or backup) into a case and every message has text (via typedstream when the `text` column is empty), reactions, replies, attachments with hashes, and provenance you could defend.
- dNh_CRM imports the same core package and stops carrying its own parsers.
- `--allow-cloud` cannot send anything unless the shield's measured recall on a labelled set meets the target and the run's hard-fail checks pass; the failure is an exit code, not a yellow line.
- Search, enrichment and reports run against one SQLite file per case with no services to start.
- Swapping the local model, or pointing at Claude for the cloud tier, is a config change.
- Lint, types and tests are green with the ≥90 % coverage gate computed over the **whole** package, not an omit list.

---

## 2. Goals, non-goals, anti-goals

**Goals**

- G1 Shared extraction core used by ChatX and dNh_CRM, emitting one canonical message contract.
- G2 Privacy gate with measured recall, hard-fail classes, and pseudonym round-trip; cloud tier fail-closed.
- G3 Single-file case store (SQLite + sqlite-vec + FTS5), attachments content-addressed on disk, never in the DB, never uploaded.
- G4 Provider abstraction: any OpenAI-compatible endpoint (local or cloud) and the Anthropic SDK, behind one interface; model ids are configuration.
- G5 Enrichment against the existing taxonomy (`config/labels.yml`, schema 1.2), structured outputs, provenance per record, cache.
- G6 Hybrid search (FTS5 + vectors) with citations; forensic export bundle with manifest hashes.
- G7 Analysis lane (relationships, episodes, psychology constructs) as a later, opt-in phase on the same store — no graph database.
- G8 Quality gates that are real: coverage over the whole package, contract tests, golden fixtures, measured (not promised) performance numbers.

**Non-goals (for this program)**

- An HTTP API or web UI. CLI and, later, an MCP server only.
- Multi-user, multi-tenant, or server deployment.
- Live message capture (BlueBubbles etc.) — that remains dNh_CRM's concern; the core is batch/export oriented.
- Telegram export parsing (dNh's Telegram path is the Bot API, which stays in dNh).
- Re-implementing differential-privacy summaries until a consumer exists (Appendix A.3: dead code today).

**Anti-goals (would make this a failure even if it worked)**

- Any path where un-redacted text, or any attachment, reaches a network endpoint other than a configured local one.
- A "coverage" or "privacy score" that is not a measured recall/precision against labels.
- Hardcoded model ids, endpoints, or passwords in code.
- A second copy of any parser in either repo.
- Coverage gates satisfied by excluding modules.

---

## 3. Decisions made

Each decision records the choice, the alternatives considered, and the reason. Owner-made decisions are marked **(owner)**; the rest are the designer's calls and may be overridden before approval.

### 3.1 Seam: shared extraction core **(owner)**

One Python package, `chat-extraction-core`, owns parsers and the canonical schema. ChatX and dNh_CRM both depend on it. Alternatives rejected: ChatX as sole extractor feeding dNh (dNh needs live-adjacent imports it can run itself); schema-only alignment (keeps two parser copies); ChatX consuming dNh's event store (loses reactions, backups, Instagram, PDF).

### 3.2 Layout: dedicated workspace directory **(owner)**, new repository (designer)

```
~/code/chatstack/                     # new git repo, uv workspace root
  pyproject.toml                      # [tool.uv.workspace] members = ["packages/*", "apps/*"]
  uv.lock
  packages/chat-extraction-core/      # the shared core (G1)
  apps/chatx/                         # the ChatX application
~/code/dNh_CRM/                       # stays where it is
  pyproject.toml                      # [tool.uv.sources] chat-extraction-core = { path = "../chatstack/packages/chat-extraction-core", editable = true }
~/code/Dopemux-ChatRipperXXX/         # archived: tagged, read-only reference
```

- No workspace root at `~/code` (verified absent; a root there would sit above every repo the owner has).
- **New repo rather than moving the existing clone.** The keep-list (§8) is ported file-by-file with a `Ported from Dopemux-ChatRipperXXX@<sha>` header; history stays in the old repo under tag `pre-rearchitecture-2026-10-20`. Reason: the old tree carries 192 `node_modules` files, Task Master state, MCP tooling, and a docs tree we are retiring; a clean root is cheaper than filtering. *Override if you want history carried in-tree (then `git filter-repo` on the keep-list paths is the route).*
- dNh changes land through dNh's own governance (its `AGENTS.md`/packets). This program's P1 exit criterion is "dNh can consume the core", demonstrated on a dNh branch; merging that branch is dNh's decision.

### 3.3 Toolchain

- Python `>=3.12` (dNh's floor; both current venvs are 3.12). `uv` (0.12.11 present), hatchling, `ruff`, `mypy --strict` for the core and `mypy` strict-by-default for the app, `pytest` + `pytest-cov`, `pre-commit`, `uv lock --check` in CI.
- Dependency bounds: lower **and** upper (`>=x,<next-major`) in both packages. The old repo mixed styles and declared unused packages (Appendix A.1).
- The core has **no network, no LLM, no storage dependencies**. A test asserts no socket is opened during core tests.

### 3.4 Canonical message contract v2

Single source of truth is the Pydantic model in the core; the JSON Schema is **generated** from it and committed (`schemas/chat.message.v2.schema.json`) with a test that fails if they drift. This removes the v1 problem where the Pydantic model and the hand-written schema disagreed on `required` and `additionalProperties`.

Rules adopted from the dNh side: `extra="forbid"`, frozen models, **timezone-aware UTC required** (naive datetimes rejected). Rules adopted from the ChatX side: reactions, replies, inline attachments, outbound messages, source path provenance.

| Field | Type | Notes |
|---|---|---|
| `schema_version` | `Literal["chat.message.v2"]` | |
| `msg_id` | str | Platform id when one exists (iMessage `guid`); otherwise derived `sha256(platform, conv_id, sent_at, sender.handle, text)[:32]` with `msg_id_kind` = `native` \| `derived` |
| `conv_id` | str | Platform thread id (`chat_guid`) or derived per source |
| `platform` | enum `imessage, sms, instagram, whatsapp, telegram, email, pdf_transcript, txt` | superset of both repos' enums |
| `direction` | enum `inbound, outbound, system` | `is_me` is a computed property (= `outbound`), not a stored field |
| `sender` | `Sender{handle, display_name?, pseudonym?}` | `handle` normalized (E.164 / lower-case email / platform username); `pseudonym` filled by identity stage |
| `sent_at` | datetime (aware, UTC) | `source_tz` optional string when the source implied a zone (WhatsApp exports have none — recorded as UNKNOWN, not guessed) |
| `text` | str \| None | |
| `text_source` | enum `text_column, attributed_body, caption, transcript, ocr, none` | how `text` was obtained |
| `content_kind` | enum `text, attachment_only, reaction_only, system, empty` | replaces dNh's `""`+`attachment_only` and ChatX's `None` ambiguity |
| `reply_to_msg_id` | str \| None | |
| `thread_originator_id` | str \| None | iMessage `thread_originator_guid` |
| `reactions` | list[`Reaction{from_handle, kind, emoji?, at}`] | `kind` enum `love, like, dislike, laugh, emphasize, question, emoji`, plus `removed: bool` |
| `attachments` | list[`Attachment{attachment_id, kind, filename, mime_type?, uti?, byte_size?, sha256?, storage_ref?, source_path?, missing: bool}`] | `kind` enum `image, video, audio, file, sticker, unknown` |
| `edit` | `Edit{edited_at?, unsent: bool, prior_texts: list[str]}` \| None | iMessage edits/unsends when present |
| `provenance` | `Provenance{source_kind, source_path, source_row?, source_guid?, extracted_at, extractor_version, content_hash}` | `source_kind` enum `chat_db, iphone_backup, instagram_zip, whatsapp_export, pdf, eml`; `content_hash` = sha256 over the canonical JSON **excluding** `source_meta` and `provenance` |
| `source_meta` | dict | escape hatch; never required; never hashed |

iMessage reaction codes: `associated_message_type` 2000–2005 add, 3000–3005 remove; 2006/3006 custom-emoji add/remove is **UNKNOWN** until verified on a real database (builder verification item V1).

### 3.5 Storage: SQLite per case **(owner)**

One file per case: `cases/<case>/case.sqlite3`, with `sqlite-vec` for vectors and FTS5 for text. This is the stack dNh already runs (`memory_vectors vec0(embedding float[1024])`, `chunks_fts`). Attachments live beside it, content-addressed: `cases/<case>/attachments/<sha256[:2]>/<sha256>`; the DB stores only the hash and metadata. Rejected: Postgres + pgvector (no server exists on this machine; dNh is not on Postgres; a service dependency buys nothing at single-user scale and makes forensic hand-off a dump instead of a file copy); keeping Chroma + Neo4j (two services, graph layer dead today).

Case layout:

```
cases/<case-id>/
  case.sqlite3
  attachments/<aa>/<sha256>
  exports/<run-id>/...
  logs/<run-id>.jsonl
  manifest.json          # case-level: sources, hashes, versions
```

Tables (outline; DDL is the builder's): `cases`, `sources`, `conversations`, `participants`, `messages`, `reactions`, `attachments`, `chunks`, `redactions`, `shield_evals`, `enrichments`, `embedding_spaces`, `vec_chunks` (vec0), `fts_messages`, `fts_chunks`, `relationships`, `episodes`, `runs`, `schema_migrations`. Migrations are plain SQL files with a small runner in the app (no Alembic for a single-file DB unless the builder finds a concrete need).

### 3.6 Model access: provider interface with two implementations **(owner)**

```python
class Provider(Protocol):
    def complete_structured(self, messages: list[Msg], schema: type[BaseModel], *,
                            temperature: float, seed: int | None, max_tokens: int) -> BaseModel: ...
    def embed(self, texts: list[str]) -> list[list[float]]: ...
    @property
    def identity(self) -> ProviderIdentity: ...   # kind, base_url/host, requested model, observed model if the API reports one
```

- `OpenAICompatProvider(base_url, api_key_env, model, embed_model)` — covers Ollama, LM Studio/MLX, vLLM, llama.cpp server, and any compatible cloud.
- `AnthropicProvider(model, api_key_env)` — first-class Claude for the cloud tier. Default cloud model `claude-sonnet-5-5`; `claude-opus-5-5` selectable per run.
- Structured outputs are validated against the Pydantic schema; invalid outputs are retried once then quarantined with the raw response.
- **No model id, endpoint or key in code.** Config (TOML, `~/.config/chatx/config.toml` with per-case override):

```toml
[providers.local]
kind = "openai_compat"
base_url = "http://localhost:11434/v1"
api_key_env = ""                  # none for local
model = ""                        # set at install; `chatx providers list` shows what the endpoint serves
embed_model = ""
[providers.cloud]
kind = "anthropic"
api_key_env = "ANTHROPIC_API_KEY"
model = "claude-sonnet-5-5"
[enrich]
temperature = 0.0
seed = 42
max_output_tokens = 800
context_turns = 2
```

- Every call records `ProviderIdentity` (requested vs observed model) into `runs`; observed is `UNKNOWN` when the API does not report it.

### 3.7 Policy Shield v2 — the gate

**Detection.** Microsoft Presidio (analyzer + anonymizer) as the framework, with the existing regex set ported as custom recognizers and a pluggable NER engine (spaCy by default; transformer/GLiNER engines optional). The builder picks the NER engine; the eval harness decides whether it is good enough.

**Pseudonymization.** Keep HMAC-SHA256 handles with a per-case salt file created `0600`; tokens `⟦TKN:<id8>⟧`; a reversible map stored only in the case DB so cloud outputs can be re-hydrated (token-preserving round-trip). The 32-bit truncated hash in the old `ConsistentTokenizer` is replaced by 128-bit.

**Measurement replaces the ratio.** The old metric `(total − PII tokens) / total` is removed. In its place:

- `shield/eval/` ships a labelled evaluation set: a synthetic generator (deterministic, seeded) plus an optional local-only, git-ignored file of owner-labelled real samples.
- `chatx shield eval` computes per-entity-class recall and precision and stores the report in `shield_evals` keyed by shield version + recognizer config hash.
- Targets: recall ≥ 0.995 (strict ≥ 0.999) on every entity class, on the synthetic set in CI and on the real-sample set locally. These are the old numbers with a real denominator.

**Run-time gate (fail-closed).** `--allow-cloud` proceeds only if all hold:

1. A `shield_evals` report exists for the exact shield version/config in use and meets the targets for every entity class present in the case.
2. Zero hard-fail class hits (`E_HARDFAIL_CLASS` blocks the run; it does not drop the chunk and continue).
3. A sampled second opinion: the **local** provider is asked, on a seeded random sample of redacted chunks, whether residual personal data remains; any confirmed leak blocks with `E_VISIBILITY_LEAK`.
4. No attachment is ever in a cloud payload (type-level: the cloud request model has no attachment field).

Failures are RFC-7807 problems with non-zero exit. `--strict` raises the threshold; nothing lowers it.

### 3.8 Chunking

Port `ConversationChunker` (turns 40 / stride 10, daily fallback, fixed-size). Fix the known defect that collapses every non-me participant into one `contact` (group chats keep per-sender identity). `semantic` stays unimplemented and is removed from the enum until it exists.

### 3.9 Enrichment

- Taxonomy from `config/labels.yml` (schema_version 1.2; 55 coarse / 99 fine by heuristic count — builder verifies by parse) compiled into Pydantic enums; the LLM returns structured labels validated against them.
- Confidence gate with hysteresis stays, as config (τ 0.70, τ_low 0.62, τ_high 0.78 as starting values, recorded in each run).
- Per-record provenance: provider identity, prompt hash, schema version, input content hash, shield version. Cache keyed on the same tuple.
- Enrichments are written to `enrichments` and are **queryable** — the v1 defect where enrichments never reached the index is removed by having one store.
- Cloud enrichment sends redacted chunk text with ±2 turns of redacted context, `max_output_tokens ≤ 800`, and logs every call.

### 3.10 Search, query, reports

- Embeddings via `Provider.embed`; the dimension is recorded per `embedding_spaces` row and `vec_chunks` is created per space.
- Hybrid retrieval: FTS5 (BM25) + vector, fused with reciprocal rank fusion; every hit cites `msg_id`s and `conv_id`.
- `chatx query` answers with citations using the local provider by default; cloud only through §3.7.
- Reports: `manifest.json`, `run_report.json`, `metrics.jsonl` (keep), redaction report, missing-attachments report, and a **forensic export bundle** (`exports/<run>/bundle.zip` with per-file sha256 manifest and the case manifest). PDF rendering of reports is a later nicety, not a gate.

### 3.11 Analysis lane (phase 6)

Relationship types and pattern definitions from the old `storage/base.py` and `psychology_relationship_mapper.py` are **content worth porting as data** (YAML), not as Neo4j code. They become rows in `relationships`/`episodes`, computed by rules over enrichment labels, optionally refined by the local provider. Psychology-specific embedding models (`mental-bert`) are an experiment behind an ADR and an eval, not a dependency of the app. Image enrichment and audio transcription enter here too, each behind its own ADR with a model-research gate first (Appendix A.3 shows the previous plan named seven models without choosing).

### 3.12 CLI

Typer. One RFC-7807 problem+json shape (`type, title, status, detail, instance, code`), one error-code convention (`E_<SNAKE>`), `--json` everywhere, exit 1 on any problem, exit 2 on gate refusal. Command tree:

```
chatx case      init | status | verify
chatx import    imessage [--db|--from-backup] | instagram | whatsapp | pdf | email
chatx identity  pseudonymize
chatx chunk
chatx shield    eval | redact | report
chatx enrich    [--provider local|cloud] [--allow-cloud] [--strict]
chatx index     build | status
chatx query
chatx export    bundle | report
chatx providers list | check
chatx analyze   relationships | episodes      # phase 6
chatx mcp serve                               # phase 7
```

The old `analyze`/`pipeline` stubs, the Typer group registered after `__main__`, and the `--config` flag that was accepted and ignored are not carried.

### 3.13 Observability and security

- `structlog` JSONL per run; run ids everywhere; no secrets in logs; provider identity logged per call.
- Secrets only from environment variables named in config.
- The core refuses to open sockets; the app's local provider is the only outbound path besides the explicitly configured cloud provider.
- `chat.db` is opened read-only after a WAL-safe copy (keep `imessage/db.py` behaviour).
- Encrypted iPhone backups: **out of scope for P1**; `--backup-password` is removed until decryption is implemented (it only checked presence before). Re-enters in phase 6 with a real implementation.

### 3.14 Retired outright

Chroma store, Neo4j store, `multi_vector_store.py`, `embeddings/*` (benchmark + psychology providers), `privacy/differential_privacy.py`, `enrichment/image_enricher.py` (placeholders), `constrained_dynamic_loader.py` (MCP tooling, not product), `enrichment/ollama_client.py` (replaced by providers), `cli/main.py` bodies, `utils/config.py` (Neo4j presets, default password), the entire `docs/` tree as spec (archived in the old repo; relevant intent captured here).

---

## 4. Target architecture

```
packages/chat-extraction-core/src/chat_extraction_core/
  schema/         canonical message v2 models + generated JSON Schema + version registry
  sources/
    imessage/     chat.db reader (WAL copy), backup reader (Manifest.db), reactions/replies/attachments,
                  attributedbody/  ← dNh's streamtyped parser + tests, wired
    instagram/    ZIP reader (zip-slip guard), mojibake repair
    whatsapp/     text export parser ← dNh
    pdf/          text-layer transcript parser (OCR hook, no engine)
    email/        .eml parser ← dNh
  identity/       handle normalization, HMAC pseudonymization
  fixtures/       synthetic chat.db builder, export builders, golden JSONL
  (no network, no LLM, no storage)

apps/chatx/src/chatx/
  case/           SQLite store, SQL migrations, manifest, runs
  shield/         Presidio integration, recognizers, eval harness, gate
  chunk/          chunker (ported)
  providers/      Provider protocol, openai_compat, anthropic, identity capture
  enrich/         taxonomy compile, structured enrichment, cache, quarantine
  index/          embeddings, vec0 spaces, FTS, hybrid retrieval
  query/          RAG with citations
  report/         manifests, redaction/missing-attachment reports, export bundle
  analysis/       (phase 6) relationships, episodes
  cli/            Typer app, problem+json
  mcp/            (phase 7)
```

Data flow: `sources → canonical messages (JSONL + validation + quarantine) → case.import → identity → chunk → shield.redact (+eval report) → enrich(local | cloud-through-gate) → index → query / export`. Every stage reads and writes the case DB; there are no file hand-offs between stages, which is what broke v1.

---

## 5. Contracts the builder must honour

1. **Canonical message v2** (§3.4). Breaking changes bump the version string and add a migration note; dNh pins the version.
2. **Schema generation test**: committed JSON Schema == generated schema.
3. **Problem+json**: one shape, one code convention, documented in `docs/reference/errors.md` generated from the code's error registry.
4. **Gate semantics** (§3.7): any code path to the cloud provider must pass through `shield.gate.require_cloud_ok(case, run)`; a test proves the cloud provider cannot be constructed without a gate token.
5. **Provider identity**: requested vs observed recorded separately; never collapse UNKNOWN into the requested value.
6. **Coverage**: `--cov-fail-under=90` over `chat_extraction_core` and `chatx` with no `omit` except `tests/`.
7. **No network in core**: enforced by a test fixture that fails on socket creation.

---

## 6. Phases and exit criteria

Order chosen for dependency flow; "optimal" per owner's delegation. Store comes before shield because the shield writes eval reports and redactions to the store.

| Phase | Scope | Exit criteria (all must be PASS) |
|---|---|---|
| **P0 Workspace** | `~/code/chatstack` repo, uv workspace, two empty packages, CI (ruff, mypy, pytest, lock check), pre-commit, ADR template, this document copied in | CI green; `uv sync` works from a clean clone; dNh branch resolves the path dep |
| **P1 Extraction core** | Schema v2 + generation; iMessage (chat.db, backup, typedstream via dNh parser, reactions, replies, attachments, edits), Instagram, WhatsApp (from dNh), PDF text, `.eml` (from dNh); identity; fixtures | Golden tests for every source; schema drift test; real `chat.db` smoke run documented with counts; **dNh adapter test passes on a dNh branch** (canonical → `EventEnvelope`), with dNh's existing suite green; V1 (reaction codes) resolved |
| **P2 Case store + CLI skeleton** | SQLite schema + migrations, `case init/import/status/verify`, manifest/runs/metrics, FTS5 over messages, attachments store | Import of 100k synthetic messages with measured throughput and RSS **recorded** in `docs/measurements.md`; `case verify` re-hashes attachments |
| **P3 Shield v2** | Presidio integration, ported recognizers, pseudonym round-trip, eval harness + synthetic set, `shield_evals`, gate API, hard-fail | Eval meets targets on synthetic set in CI; gate refusal paths tested (exit 2, problem+json); tokenizer 128-bit |
| **P4 Providers + enrichment** | Provider protocol, both implementations, identity capture, taxonomy compile, structured enrichment, cache, quarantine, cloud path through gate | Contract tests against recorded responses (no live model in CI); local smoke documented; a test proves cloud is unreachable without gate token; enrichments visible to `query` |
| **P5 Index, query, export** | Embedding spaces, vec0, hybrid retrieval, citations, `query`, export bundle | Retrieval tests on fixtures; bundle hash manifest verifies; measured retrieval latency recorded |
| **P6 Analysis lane** | Relationships/episodes as data + rules; psychology constructs via enrichment; image enrichment and transcription each behind ADR + eval; encrypted backups | Each sub-feature has its own ADR, eval, and opt-in flag |
| **P7 MCP + polish** | `chatx mcp serve` (local only), generated CLI/error reference, MkDocs, old repo archived | Docs generated from code; old repo tagged and README points here |

Each phase gets its own implementation plan (superpowers:writing-plans) after this design is approved.

---

## 7. Quality gates (global)

- `ruff check` + `ruff format --check`; `mypy --strict` (core) / strict config (app); `pytest --cov-fail-under=90` over whole packages; `uv lock --check`; `pip-audit` (or `uv`-native audit when available).
- Golden fixtures for every source; property tests for timestamp conversion (Apple epoch ns/µs/s heuristic bounds 2004–2100) and for handle normalization.
- Performance: no promised numbers in docs. `pytest -m perf` (opt-in) records throughput/latency/RSS into `docs/measurements.md` with machine and commit; the old targets (≥10k msg/min ingest, p95 ≤150 ms retrieval, <4 GB for 1M messages) become **tracked measurements**, promoted to gates only once met twice.
- Security tests: no-socket core; cloud unreachable without gate; salt file mode; no attachment field on cloud request models.

---

## 8. Migration from the old repository

**Keep (port with tests, minimal change)** — `imessage/time.py`, `imessage/db.py`, `imessage/backup.py` (minus password flag), `imessage/extract.py` (structure; fix `is_from_me` scope bug), `imessage/attachments.py`, `imessage/report.py`, `instagram/extract.py`, `identity/normalize.py` (+`0600`, 128-bit), `utils/json_output.py`, `cli_errors.py`, `transformers/chunker.py` (fix group-chat collapse), `tests/fixtures/*`, the 35-file iMessage test suite, `config/labels.yml`, `schemas/message.py` (as v1 reference for the v2 mapping).

**Take from dNh_CRM** — `ingest/imessage_attributed_body.py` + its 1013-line test file + probe script; `ingest/whatsapp_export.py` + tests; `ingest/email_eml.py` + tests; the dedupe-hash approach (`idempotency.py`) as the model for derived ids.

**Port with rework** — regex set → Presidio recognizers; `PolicyShield` concept → §3.7; run manifest/metrics → `runs` table; relationship types/patterns → YAML data.

**Discard** — §3.14 list, `docs/` as spec, `.taskmaster/`, `.serena/`, `context_portal/`, `node_modules/`, root scripts.

Old repo: tag `pre-rearchitecture-2026-10-20`, README banner pointing to `chatstack`, no further feature work.

---

## 9. dNh_CRM integration

- dNh adds the path dependency (§3.2) and an adapter `canonical_message → EventEnvelope(MSG_INBOUND_RECEIVED)`; mapping: `msg_id → external.source_message_id`, `conv_id → conversation_id` (`imessage:{conv_id}`), `direction → direction + actor.role`, `sent_at → occurred_at`, `content_kind == attachment_only → IMessageAttachmentOnlyPayload`, `provenance.content_hash` feeds `idempotency.dedupe_hash`.
- dNh gains, without further work: typedstream text when `text` is NULL (its own parser, finally wired), reactions and replies (may ignore), outbound messages (behind its own flag).
- dNh is **not** required to change its store, event schema, Telegram path, or BlueBubbles bridge.
- Where dNh's `conversation_contacts`/`contact_identities` tables need handles, the core's normalized `sender.handle` is the input.

---

## 10. Risks and unknowns (resolve by measurement)

| # | Item | Resolution |
|---|---|---|
| V1 | iMessage reaction codes 2006/3006 (custom emoji) and exact removal semantics | Verify on a real `chat.db` during P1; fixture it |
| V2 | dNh's typedstream parser accepts only two pinned layouts; real-world coverage unknown | P1: run the probe script over the owner's real db; count `unsupported`/`malformed`; fall back to `text` column with `text_source=none` and a report line, never silently |
| V3 | Presidio/NER recall on chat text (short, slangy, names without titles) | P3 eval on synthetic + owner-labelled real samples; choose engine by numbers |
| V4 | sqlite-vec behaviour at 1M chunks; dimension choice | P2/P5 measurements; dimension is per-space so it can change |
| V5 | macOS Full Disk Access / TCC for `chat.db` | Document; `case import` emits a clear problem (`E_DB_ACCESS_DENIED`) |
| V6 | WhatsApp export timezone is unknowable from the file | Record `source_tz=None`; offer `--assume-tz` at import; never silently UTC |
| V7 | Taxonomy counts and validity of `labels.yml` | P4: parse, validate, publish counts |
| V8 | uv workspace + dNh path dep + two lockfiles | P0: prove `uv sync` in both from clean clones; stop and report if uv semantics bite |
| V9 | Observed vs requested model identity via OpenAI-compatible endpoints | Record UNKNOWN when the endpoint does not echo the model |

---

## 11. Left to the builder

Module and table naming; exact DDL and index choices; the SQL migration runner; Presidio NLP engine selection within the eval gate; token counting method for chunks; embedding model and dimension defaults; fixture generation details; CI matrix (macOS arm64 required, Linux x86_64 nice-to-have); structlog configuration; Typer command option names beyond those listed; how `chatx providers list` discovers models; export bundle format details beyond "zip + sha256 manifest"; whether PDF report rendering uses an existing library or is dropped from P5.

---

## 12. Owner decisions still open

1. **History**: new clean repo (designer's choice, §3.2) vs carrying ChatX git history into `chatstack`.
2. **Case scoping**: one case per contact (v1 habit, `--contact` everywhere) or one case per source import with contacts as a filter. Designer's default: **case per import set, contact as a query filter** — it matches "forensic bundle" semantics and group chats.
3. **Owner-labelled shield samples**: willing to label a local, git-ignored sample of real messages so the shield's real-data recall can be measured? Without it, only the synthetic number exists and the design says so in every report.

---

## Appendix A — Current-state evidence (condensed)

### A.1 Code-reality grades (`src/chatx`, 2026-10-20)

| Area | Grade | Key evidence |
|---|---|---|
| iMessage extraction (db, backup, reactions, replies, attachments, audit) | REAL | 35-file test suite; `attributedBody` is `plistlib`→UTF-8 heuristic; `is_from_me` scope bug in `get_conversation_guids` |
| Instagram ZIP, PDF text | REAL / THIN | No OCR engine; PDF timestamps synthetic |
| extract → transform | BROKEN | `write_messages_with_validation` wraps `{"messages": …}`; `transform` expects a bare list |
| redact | REAL but ADVISORY | coverage = token ratio; warns and exits 0; hard-fail flag inverted |
| `--allow-cloud` | ADVISORY | no cloud client in `src/` |
| enrich / enrich-multi | BROKEN | enrichments never reach the index; `multi_pass_pipeline` import error |
| index / query | WIRED, UNTESTED HAND-OFF | Chroma; psychology multi-vector dead to CLI |
| graph (Neo4j), embeddings, DP summaries, image enrichment | DEAD / STUB | never reachable from CLI; placeholders |
| `analyze`, `pipeline` | STUB | print "not yet implemented" |
| Coverage gate | HOLLOW | `pyproject` omits `redaction/*`, `transformers/*`, `enrichment/*`, `indexing/*`, `schemas/validator.py`, `transcribe/*` |
| Deps | DRIFT | `yaml`, `tenacity`, `psutil`, `requests`, `fitz`, `PyPDF2`, whisper undeclared; `openai`, `anthropic`, `cohere` declared unused |
| Hardcoded | `gemma2:9b-instruct-q4_K_M` ×4, `claude-3-sonnet-20240229`, Neo4j password `"password"` |

### A.2 dNh_CRM trace (2026-10-20)

- Message = `EventEnvelope` (`dnh.crm.event.v1`, frozen, `extra=forbid`); no reactions, replies, inline attachments, or outbound iMessage ingest; tz-aware UTC enforced; ids `guid` or `rowid:N`; WhatsApp ids are content hashes.
- `ingest/imessage_attributed_body.py` (307 LOC): real `streamtyped` parser, two pinned layouts, bounded, **unwired**; tests 1013 LOC with builder fixtures pinned to observed macOS prefixes.
- `whatsapp_export.py` (248 LOC, multiline/system/media-omitted/date formats, no tz), `email_eml.py` (297 LOC), `telegram.py` (Bot API, not export). No Instagram.
- Store: SQLite `./data/dnh_crm.sqlite3`, sqlite-vec `vec0(embedding float[1024])`, FTS5. No Postgres.
- Packaging: hatchling, uv.lock, `requires-python >=3.12`, lower-bound pins, no workspace/path deps.

### A.3 Docs inventory (2026-10-20)

~60 claimed capabilities across 13 hops: 26 ABSENT, 10 UNKNOWN, the rest REAL/BROKEN/STUB/DEAD per A.1. 24 contradictions, including coverage 90 % vs 60 %, temperature ≤0.3 vs 0, retrieval p95 ≤150 ms vs <5 s, two RFC-7807 shapes, three error-code conventions, three names for the run report. Stale references: `gemma-2-9b` ×7 forms, Chroma ~25, Neo4j ~12, `all-MiniLM-L6-v2`, `mental-bert`, Stella/Cohere, seven vision models in one plan. Owner's ruling: docs are inspiration, not spec; this document is the statement of intent.

### A.4 Machine facts (2026-10-20)

`uv 0.12.11`; no `pyproject`/`uv.toml`/`uv.lock` at `~/code`; `ollama` binary at `/opt/homebrew/bin/ollama` (server not running); no `psql`/Postgres.app/brew Postgres; one docker container `postgres:16.6` (owner UNKNOWN, unrelated to dNh). ChatX venv CPython 3.12.9; dNh venv CPython 3.12.8.
