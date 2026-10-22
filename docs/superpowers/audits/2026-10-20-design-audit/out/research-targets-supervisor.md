# Research targets raised by the supervisor (snapshot of the table in `design-revision-plan.md`, 2026-10-21; RT-16–RT-18 from the chatgpt fold-in; status column and RT-19 from the owner-answer and fact-check fold-in)

19 targets: 2 answered (RT-1, RT-8), 4 partly answered (RT-4, RT-7, RT-10, RT-12), 13 open.

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
