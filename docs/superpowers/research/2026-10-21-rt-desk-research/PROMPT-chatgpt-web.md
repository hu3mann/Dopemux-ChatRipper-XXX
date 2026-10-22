(Paste the text below as the first message. Attach `2026-10-20-chatx-rearchitecture-design.md` — design revision 2, from `docs/superpowers/specs/`.)

---

Researcher name: **chatgpt-web-research**

You are doing current-facts desk research for a software design that is already decided. You are not auditing or redesigning it. The design is the attached file; treat it as the only description of the system. Everything you state about the outside world must come from sources you open in this session, with URLs and dates. Browsing is required. If you cannot browse, say so and stop.

Begin with an identity block: model name as your interface reports it, knowledge cutoff, whether browsing is on, today's date, and which sections of the attached design you read.

## What the design is, in two lines

A local-first macOS tool that extracts a person's own chat history (iMessage, backups, other exports) into per-case SQLite stores, redacts it through a Policy Shield before any cloud model sees it, enriches and indexes it, and answers questions with citations. The design document names open research targets in its §13; this brief covers the ones that can be settled by reading current sources rather than by measurement.

## Rules

- Primary sources first: official documentation, RFCs, the project's own repository or release notes, vendor pricing pages. Blog posts and forum threads only as leads, marked as such.
- Every factual claim carries a source row in Output B, and every source row carries the date the page states (published or updated) and the date you retrieved it. If a page has no date, write `undated`.
- Quote at most 120 characters from a source per claim, verbatim, so the quote can be found on the page later.
- Anything you did not find in a source this session is **UNKNOWN**. Do not fill gaps from memory. If you add a memory-based remark, prefix it `from memory, unverified:`.
- Stay inside each target's question. If you think a target's premise is wrong, say so in its "Residue" line and move on; do not propose changes outside the design section the target names.
- Do not recommend products you did not open the documentation for.
- Versions matter: name the version or commit of anything you describe, and the date.

## Targets, in the order the build needs them

For each target: **Design today** is what the attached design assumes (with its section); **Question** is what to settle; **Feeds** is the decision that consumes the answer.

### P1 — needed first

**RT-2 Canonical JSON: a JCS (RFC 8785) library vs the design's stated rules**
Design today: §3.4 already fixes the canonical form for hashed fields — "UTF-8, NFC-normalized strings, keys sorted, no insignificant whitespace, and no floats in hashed fields" — and calls this RFC 8785 (JCS) semantics. A sibling system (dNh_CRM) has its own `canonical_json` helper, which the design says is "checked against JCS or replaced by a JCS library"; dNh keeps its own dedupe formula (§9, §12 item 5).
Question: Is there a maintained Python implementation of RFC 8785 (name, version, release date, licence, whether it ships the RFC's test vectors)? Do the design's four rules produce the same bytes as JCS, or does JCS differ in ways that matter here — string escaping rules, key ordering by UTF-16 code units rather than code points, number formatting (the design bans floats in hashed fields; is that enough?) — and since JCS itself does not normalise Unicode, must NFC stay a documented pre-step? Is there a test-vector set that could check dNh's helper against JCS?
Feeds: whether §3.4 adopts a library or keeps a documented in-house implementation, and the conformance check for dNh's helper.

**RT-3 Generic NSAttributedString / typedstream decoders**
Design today: §3.4 decodes iMessage `attributedBody` (an Apple typedstream archive of an NSAttributedString) with its own decoders and measures decode coverage on real data before freezing the schema.
Question: What maintained decoders exist today (Python first; Rust/Swift reference implementations second — `imessage-exporter` is one known reference)? For each: licence, last release date, whether it handles the typedstream format generically or only the iMessage subset, how it reports attributes (mentions, links, attachment ranges), and known failure modes on recent macOS/iOS versions.
Feeds: build vs adopt for the decoder in §3.4; the P0.5 coverage spike's baseline.

### P2

**RT-14 macOS exposure controls for case directories**
Design today: §3.5 stores cases under `~/Library/Application Support/chatx/cases.noindex/` (mode 0700) and relies on the `.noindex` suffix to keep Spotlight out; case creation offers a Time Machine exclusion. iCloud-sync detection was raised in the audit and is not yet in the design.
Question: Current, documented behaviour of (a) the `.noindex` directory suffix for Spotlight, (b) Time Machine exclusion via `tmutil addexclusion` — fixed-path vs sticky exclusion, persistence across moves, admin requirements — and the backup-exclusion extended attribute, (c) detecting whether a folder is inside iCloud Drive or Desktop & Documents sync (paths, `brctl`, `.icloud` placeholder files, relevant xattrs), and (d) the "Optimize Mac Storage" eviction risk for files that are synced. Which of these are documented by Apple and which are only observed behaviour?
Feeds: the storage rules in §3.5 and the `case create` checks in P2.

**RT-19 Per-case encryption alongside sqlite-vec and FTS5**
Design today: §3.5 and §3.15 make encryption at rest opt-in and require FileVault (§12 item 7); the store uses FTS5 and the sqlite-vec `vec0` extension; §3.3 sets a minimum SQLite version.
Question: Does SQLCipher (current release) load runtime extensions such as sqlite-vec, and what SQLite version does it track? Which Python bindings are maintained, and what SQLite do they bundle? What is the documented performance overhead? How would the key be held on macOS (Keychain, Secure Enclave-backed keys) without the user typing a passphrase each run? Compare with an encrypted APFS volume or sparsebundle holding a plain SQLite file: what each protects against, and what breaks (backup, `verify`, portability).
Feeds: the opt-in encryption design in §3.5/§3.15.

### P3

**RT-10 (open half) Presidio V2**
Design today: §3.7 builds Policy Shield v2 on Presidio — now community-governed under the Data Privacy Stack organisation, MIT-licensed — pinned with hashes, with the v1 regex recognizers ported; §3.3's `conformance.md` records the Presidio version tested.
Question: What does Presidio's published V2 plan (`docs/presidio_V2.md` in the Presidio repository, or wherever it now lives) change — analyzer/anonymizer API, recognizer registration, NLP engine configuration, Python version floor — and what is its stated timeline and status today? Should new recognizers be written against V1 or V2 interfaces?
Feeds: the pin in §3.3 and the recognizer port in §3.7.

**RT-11 Small NER engines for short, slangy chat text**
Design today: §3.7 says the NER engine is chosen by an evaluation in P3 on a labelled real sample; the research narrows the candidates. The "OpenAI Privacy Filter" was added as a candidate during the audit.
Question: For spaCy (small and transformer pipelines), Stanza, Flair, GLiNER-family models, the OpenAI Privacy Filter, and any other current on-device option: licence, model size, CPU / Apple Silicon latency per short message if published, entity types covering person, phone, email, street address, handle/username, and any published evaluation on SMS, chat or social-media text. State clearly which numbers come from the vendor and which from third parties.
Feeds: the candidate list for the P3 eval in §3.7.

**RT-16 Local language identification for short messages**
Design today: §4 includes a language-identification step so the shield applies language-appropriate recognizers; P3's exit depends on it.
Question: For fastText `lid.176`, CLD3, `lingua`, `langid.py`, `langdetect` and any current successor: accuracy on texts under ~20 tokens if published, speed, model size, licence, maintenance status (last release), and how each reports confidence for mixed or very short input.
Feeds: the language-id component in §4 and the P3 plan.

### P4

**RT-7 (open half) Anthropic prompt caching and Message Batches for an enrichment workload**
Design today: §3.6 uses Anthropic as the cloud provider for structured enrichment of redacted chunks, with typed outcomes and a cache keyed by content.
Question: From current Anthropic documentation: prompt caching — minimum cacheable prefix, cache lifetime, pricing for cache writes and reads, which models support it, interaction with tool use and structured outputs; Message Batches — limits, turnaround, pricing, result retrieval, and whether batch requests support the same caching and structured-output features. Record the documentation dates.
Feeds: the provider configuration and cost model in §3.6.

**RT-12 (open halves) Reproducibility and structured output on local servers**
Design today: §3.6 supports OpenAI-compatible local servers; some request shapes are already recorded; reproducibility on llama.cpp's server and LM Studio, and MLX, are open.
Question: For llama.cpp `llama-server`, LM Studio's local server, and `mlx-lm`'s server: do they document a seed parameter and deterministic decoding at temperature 0; do they support JSON-schema or grammar-constrained output, and through which request field; what are the current version numbers and dates of the documentation you used.
Feeds: the provider matrix in §3.6.

**RT-17 Binding a gate token to the final request bytes**
Design today: §3.7 is the egress gate and §3.6 issues a gate token per cloud request; the provider configuration must state the account terms (`zero_data_retention = true`) before a token can be issued. The design does not yet say how the token is bound to the exact bytes the client transmits — that mechanism is what this target settles.
Question: In the current Anthropic Python SDK and the OpenAI Python SDK (and therefore OpenAI-compatible servers): what hooks exist to observe or veto the exact outgoing request body and headers before transmission — custom `httpx` clients, event hooks, transports, middleware — and at which point serialisation is final? Cite the SDK versions and the documentation or source lines.
Feeds: the gate implementation in §3.6/§3.7.

### P5

**RT-5 Local embedding models for chat text, ≤ 768 dimensions**
Design today: §3.10 indexes chunks in sqlite-vec `vec0` with a dimension cap of 768 and leaves model choice and quantization (within a rescoring rule) to the builder (§11).
Question: Current locally runnable embedding models at or under 768 dimensions suited to short conversational text: published retrieval quality (name the benchmark and note where it does not resemble chat), multilingual coverage, licence, parameter count, Apple Silicon runtimes (sentence-transformers, ONNX, MLX), context length, and whether the model publishes int8 or binary quantization guidance with rescoring.
Feeds: the builder's embedding choice in §3.10/§11.

**RT-6 Export bundle signing tool and verification UX**
Design today: §3.10 exports a zip with `MANIFEST.sha256` and `custody.json`; §11 leaves the signing tool to the builder.
Question: For minisign, OpenSSH signatures (`ssh-keygen -Y sign/verify`), Sigstore/cosign blob signing, and OpenPGP: availability on a stock Mac, detached-signature format, what a non-technical recipient must install and type to verify, key custody and rotation story, and current maintenance status.
Feeds: the export design in §3.10.

**RT-18 Evaluating citation support in answers**
Design today: §3.10 answers questions with citations and runs a "citation-support check" (does the cited span support the claim) using a local judge; §4 names the component.
Question: Current methods and metrics for claim-to-span attribution evaluation (attribution precision/recall, NLI-based judges, published benchmarks), small models that can serve as a local judge, and what agreement with human raters they report.
Feeds: the citation-support check in §3.10.

### P6

**RT-9 iOS encrypted-backup decryption libraries**
Design today: §4 includes encrypted iOS backups as a P6 source.
Question: Maintained libraries (Python first) that decrypt iOS encrypted backups: supported iOS versions as of now, licence, last release, how they handle `Manifest.db` and the keybag, and whether they can decrypt a file into memory without writing plaintext to disk.
Feeds: the P6 source plan in §4.

## Outputs

Produce two files as downloads if your interface supports it; otherwise print them in full, each preceded by `=== FILE: <name> ===`.

**Output A — `research-rt-chatgpt-web.md`.** One section per target, in the order above. Each section has exactly these parts:
1. `Answer` — at most 200 words.
2. `Evidence` — a table: Claim | Source ID (from Output B) | Quote (≤ 120 chars, verbatim) | Page date | Retrieved.
3. `Recommendation` — one of `adopt`, `adopt with change`, `reject`, `measure in P0.5` (when only measurement can settle it), followed by the design section it would change and the proposed replacement text, kept to the minimum.
4. `Confidence` — `high`, `medium` or `low`, and the single fact that would most change it.
5. `Residue` — what stays open, and anything wrong with the target's premise.

**Output B — `research-rt-sources.md`.** A flat table, one row per URL: Source ID (`S01`, `S02`, …) | URL | Title | Publisher | Page date | Retrieved | Used by (RT ids). No row without a URL you opened.

Depth: thorough, not padded. If you hit an output limit, end with `CONTINUE` and, when asked, resume exactly where you stopped without repeating.
