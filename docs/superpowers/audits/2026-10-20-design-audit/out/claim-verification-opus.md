# claim-verification-opus

Runner: sonnet-verify (second pass, auditor `opus`) | Model: Sonnet 5.5 (claude-sonnet-5-5 per system prompt; no runtime receipt) | Date: 2026-10-21 | Tool calls: ~17 (resumed run, cap 200). File could not be written by the subagent (Write rejected by harness); supervisor to save to out/claim-verification-opus.md.

Conventions: ChatX = /Users/hue/code/Dopemux-ChatRipperXXX (HEAD 9c3dd6b); dNh = /Users/hue/code/dNh_CRM. Design = design/2026-10-20-chatx-rearchitecture-design.md. External URLs not fetched; a claim resting only on them is UNKNOWN. Where a row mixes verified repo/design lines with external facts, Result reflects the repo/design lines and the note says so.

## Summary

| auditor | rows | PASS | PARTIAL | FAIL | UNKNOWN | NOT_RUN |
|---|---|---|---|---|---|---|
| opus | 35 | 28 | 3 | 0 | 4 | 0 |

## Row results

| ID | Sev (as claimed) | Verdict (as claimed) | Citations checked | Result | Note |
|---|---|---|---|---|---|
| F-01 | BLOCKER | CONFIRMED | design L349, L122; dNh dedupe.py:11-25; migrations.py:5-23 | PASS | L349 "`provenance.content_hash` feeds `idempotency.dedupe_hash`"; dNh hashes channel/ids/sender/sent_at/text; `UNIQUE(dedupe_scope, dedupe_hash)`. |
| F-02 | HIGH | CONFIRMED (API facts); PLAUSIBLE | design L144-179; claude-api skill; Messages API URL | UNKNOWN | Design shows `temperature, seed, max_tokens` params, `seed = 42`, default `claude-sonnet-5-5`. Rejection/no-seed API behaviour is external; not checked. |
| F-03 | HIGH | CONFIRMED (design text) | design L155-160, L245-251, L61 | PASS | "covers Ollama… and any compatible cloud"; L61 offset 1 (anti-goal is L60); L251 "local provider is the only outbound path". |
| F-04 | HIGH | CONFIRMED | design L186-195, L382; Presidio quote | PASS | L193 "meets the targets for every entity class present in the case"; L382 real samples optional. Presidio quote external, not needed for design claim. |
| F-05 | HIGH | CONFIRMED (labels/policy); PLAUSIBLE | labels.yml:10-12,155,192-241,242,284; design L211 | PASS | `coarse_cloud_allowed: true`; sex_work_context (L155), chemsex (L242), kink (L284) sit under `coarse:`; L211 "±2 turns of redacted context". |
| F-06 | HIGH | CONFIRMED (design text) | design §3.12 L224-241, §6 P7 L318 | PASS | Command tree has `chatx mcp serve # phase 7`; P7 row "(local only)". |
| F-07 | HIGH | CONFIRMED (code); PLAUSIBLE | dNh whatsapp_export.py:24-27,33-48,96-116,127-128,177-192,196-198; design L338 | PASS | `any(marker in normalized …)`; `if ": " not in rest: … continue`; `%m/%d/%y` only; `.replace(tzinfo=UTC)`; ValueError at L128. |
| F-08 | HIGH | CONFIRMED (code); PLAUSIBLE | reactions.py:35-36,55-56; extract.py:145,226-246; fixtures | PASS | `if 3000 <= … <= 3999: return "custom"`; raw `target_guid in messages_by_guid`; `datetime.now(timezone.utc)` fallback; fixture has no `p:`/`bp:`. |
| F-09 | HIGH | CONFIRMED (code); PLAUSIBLE | db.py:12-41,46-63; design L249 | PASS | Three sequential `shutil.copy2`; `?mode=ro&immutable=1`. Immutable+WAL semantics is external. |
| F-10 | HIGH | CONFIRMED | design L76-90, L295, L311; dNh ci.yml:10-23 | PASS | Design: `{ path = "../chatstack/…", editable = true }`; CI: single `actions/checkout`, `uv sync --all-extras`. |
| F-11 | HIGH | CONFIRMED (design/code); PLAUSIBLE | design L127-140, L245-251; db.py:25; cli/main.py:13-26 | PASS | Relative `cases/<case>/`; `TemporaryDirectory(prefix="chatx_imessage_")`; `typer.Typer(name=…, add_completion=False)` no `pretty_exceptions_show_locals`. |
| F-12 | MEDIUM | CONFIRMED | design L184; patterns.py:227-236 | PASS | L184 "tokens `⟦TKN:<id8>⟧`… replaced by 128-bit"; code `sha256(f"{text}:{pii_type}:{salt}")[:8]`. Note: salt is concatenated, so "unkeyed" is loose. |
| F-13 | MEDIUM | CONFIRMED (design/dNh); PLAUSIBLE | design L108; dNh whatsapp_export.py:165-174 | PASS | L108 `sha256(platform, conv_id, sent_at, sender.handle, text)[:32]`; dNh key uses `ts_raw`, `export_filename`. |
| F-14 | MEDIUM | CONFIRMED | dNh events.py:12-17,519-530,2007-2016; design L349-351 | PASS | `text: str = Field(min_length=1)`; "attachment-only payload is limited to inbound client iMessage events"; L349 maps to `MSG_INBOUND_RECEIVED`. |
| F-15 | MEDIUM | CONFIRMED (absence); PLAUSIBLE | instagram/extract.py:155-157; rg mojibake/latin-1 | PASS | `json.load(io.TextIOWrapper(f, encoding="utf-8"))` with no repair; rg in ChatX src/tests and dNh: 0 hits. |
| F-16 | MEDIUM | CONFIRMED | design L121, L335; extract.py grep; extractors/imessage.py:106-178 | PASS | 0 hits for date_edited/date_retracted/message_summary_info in imessage/extract.py; `_decode_message_summary_info` at extractors/imessage.py:105. |
| F-17 | MEDIUM | CONFIRMED (code); PLAUSIBLE | extract.py:176-177; reactions.py is_reply; design L116-117 | PASS | `return associated_message_type == 0 and has_associated_guid`; design reply_to at L117 (offset 1), no derivation rule. |
| F-18 | MEDIUM | CONFIRMED | enricher.py:29-43,164-176; design L207 | PASS | `elif confidence >= tau: high` else low; tau 0.7, tau_low 0.62, tau_high 0.78; `confidence_llm`. |
| F-19 | MEDIUM | CONFIRMED | dNh migrations.py:198-202,375-378; design L329, L363; sqlite-vec README | PASS | `has_vec0 = … pragma_module_list() WHERE name='vec0'`, `if has_vec0:`; 1M×1024×4 ≈ 4.1 GB; design target "<4 GB for 1M messages". README external. |
| F-20 | MEDIUM | CONFIRMED | design L218, L46 | PASS | "bundle.zip with per-file sha256 manifest"; no signature/timestamp in design (rg signed/signature: 0 hits). |
| F-21 | MEDIUM | CONFIRMED | fixtures sql:5-19,67-70,106-109; dNh test_imessage_attributed_body.py:94-113; probe.py:29 | PARTIAL | message table lacks thread_originator_guid/date_retracted/item_type; no `p:`/`bp:`. But fixture has a `message_summary_info` table (sql:144-157) and `date_edited`. |
| F-22 | MEDIUM | CONFIRMED | design L300, L326 | PASS | L300 "`--cov-fail-under=90` over `chat_extraction_core` and `chatx`"; L326 pytest cov line coverage; no branch/mutation. |
| F-23 | MEDIUM | CONFIRMED | design L192-195; patterns.py:160-200 | PASS | L195 "Zero hard-fail class hits … blocks the run" (offset 2-3); no class enumeration; HardFailDetector regex dict (violence, drugs, csam). |
| F-24 | MEDIUM | CONFIRMED | design L305-318, §10 | PASS | P0→P1→P2→P3 order; no spike phase before store/CLI. |
| F-25 | MEDIUM | CONFIRMED | storage/base.py:254-267,393-440; design L220-222 | PASS | `GASLIGHTS`, `MANIPULATES`, `CODEPENDS_ON` (254-267); `AROUSAL_MANIPULATION` at L402. |
| F-26 | MEDIUM | CONFIRMED (absence) | design §2, §3.7, §3.12 | PASS | rg for consent/retention/purge/delete in design: 0 hits. |
| F-27 | MEDIUM | PLAUSIBLE | design L153-154 | UNKNOWN | Claim is about external server behaviour; design lines do not discuss structured-output support. |
| F-28 | MEDIUM | CONFIRMED | design L147-150, L214; embeddings URL | PARTIAL | Design: `Provider.embed` and `AnthropicProvider implements Provider`; L214 "Embeddings via `Provider.embed`". "Anthropic has no embedding model" is external, unchecked. |
| F-29 | MEDIUM | CONFIRMED | design L182; presidio URL | UNKNOWN | L182 "Microsoft Presidio (analyzer + anonymizer)" verified; ownership transition is external. |
| F-30 | LOW | PLAUSIBLE | design L226 | UNKNOWN | L226 "exit 1 on any problem, exit 2 on gate refusal" verified; Click/Typer exit-2 collision is external. |
| F-31 | LOW | CONFIRMED | dNh email_eml.py:107-115,203-213 | PARTIAL | Naive tz `.replace(tzinfo=UTC)` confirmed (L210-211). `synthetic:{file_hash}` is hash of file bytes, so byte-identical re-save dedupes; duplicates only if bytes differ. |
| F-32 | LOW | CONFIRMED | design L64 (actual L63), §9; dNh imessage_source.py:116-120 | PASS | L63 "A second copy of any parser in either repo."; imessage_source.py reads `FROM message … WHERE m.is_from_me = 0`; imessage_mapper.py exists. |
| F-33 | LOW | CONFIRMED | design L110, L115, L55 (cited L57), §3.12 | PASS | L110 enum has `telegram`, `txt`; L115 `ocr`; L55 "Telegram export parsing" non-goal; import tree has no txt. |
| F-34 | INFO | CONFIRMED | dNh imessage_attributed_body.py:1-75,23-24 | PASS | `MAX_INPUT_BYTES = 256 * 1024`, `MAX_OUTPUT_BYTES = 64 * 1024`; "Fail-closed decoder"; rg in src: only itself. |
| F-35 | INFO | CONFIRMED | pyproject.toml:193,198-207 | PASS | omit list has `redaction/*`, `transformers/*`, `enrichment/*`, `indexing/*`. |

## Failures and partials

- F-21 (PARTIAL): finding says fixture lacks `message_summary_info`; tests/fixtures/imessage_test_data.sql:142-157 creates a `message_summary_info` table with `date_edited`. The message-table columns thread_originator_guid, date_retracted, item_type, group_action_type, date_read/delivered are indeed absent, and no `p:`/`bp:` GUIDs.
- F-28 (PARTIAL): design lines (Provider.embed, AnthropicProvider) verified; the "Anthropic offers no embedding model" fact is external and unchecked.
- F-31 (PARTIAL): tz-to-UTC fallback verified; the "same mail saved twice" duplicate claim is only true when file bytes differ (`file_hash = sha256(file_bytes)`).
- UNKNOWN (external-only): F-02 (Messages API behaviour), F-27 (OpenAI-compatible server behaviour), F-29 (Presidio ownership), F-30 (Click exit 2).
- Offsets noted, not failures: F-03 (L61 vs L60), F-17 (L116-117 vs L117), F-23 (L192 vs L194-195), F-32 (L64 vs L63), F-33 (L57 vs L55).

## Overlaps with the first verification pass

Mechanical: opus repo-file citations whose line ranges overlap a "Citations checked" entry in out/claim-verification.md. Design section citations excluded (different line/section forms). Other-row IDs are prefixed by auditor (codex F01-F30, grok F1-F20, agy F-01..F-25).

- F-01 db? no. F-01 dedupe.py:11-25 overlaps codex F04 (dedupe.py:15-25), grok F13 (15-24), agy F-06 (15-24); F-01 migrations.py:5-23 overlaps agy F-06 (migrations.py:23).
- F-05 labels.yml:10-12 overlaps codex F15 (3-12), grok F14 (10-13); labels.yml:192-241 overlaps codex F17 (191-238); labels.yml:284 overlaps codex F17 (248-285).
- F-07 whatsapp_export.py ranges overlap codex F03 (177-193), codex F08 (33-49,105-108,196-198), grok F12 (33-49,105-107,196-198), agy F-03 (180-187), agy F-04 (24-49,105-108,196-198).
- F-08 reactions.py:35-36 overlaps codex F06 (33-37), grok F11 (36-37); extract.py:145 overlaps grok F11 (130-148); extract.py:226-246 overlaps grok F11 (229), agy F-07 (229,257), agy F-09 (237).
- F-09 db.py:12-41,46-63 overlaps codex F05 (25-43), grok F5 (12-64), agy F-01 (12-60).
- F-11 db.py:25 overlaps codex F05 (25-43), grok F5 (12-64), agy F-01 (12-60).
- F-12 patterns.py:227-236 overlaps codex F11 (227-234), grok F3 (230-234).
- F-14 events.py:519-530 overlaps agy F-05 (519-560).
- F-15 instagram/extract.py:155-157 overlaps agy F-11 (21-38,157).
- F-17 reactions.py is_reply (62-72) overlaps grok F11 (62-72).
- F-18 enricher.py:164-176 overlaps codex F18, grok F14 (164-176).
- F-19 migrations.py:198-202 overlaps grok F9 (197-211), codex F13 (197-237).
- F-21 imessage_test_data.sql:5-19 overlaps grok F4 (5-19), agy F-24 (1-162); test_imessage_attributed_body.py:94-113 overlaps agy F-24 (1-200).
- F-23 patterns.py:160-200 overlaps agy F-16 (159-197), grok F8 (162-176).
- F-31 email_eml.py:107-115 overlaps agy F-19 (110-165).
- F-32 imessage_source.py:116-120 overlaps grok F4 (109-124).
- F-34 imessage_attributed_body.py:1-75 overlaps grok F6 (69-80).
- F-35 pyproject.toml:193,198-207 overlaps codex F25 (187-206), grok F17 (193-218).
