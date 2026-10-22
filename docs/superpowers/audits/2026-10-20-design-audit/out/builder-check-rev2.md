# Builder check of design rev 2 (2026-10-21)

Runner: Claude Code `Agent`, `model: sonnet`, `effort: medium`; transcript response models: claude-sonnet-5-5; tool calls: {'Read': 4, 'SubagentHandback': 1}. Read only the rev 2 spec (sha256 `b3152775…dcc1`). Report saved verbatim below; triage is in the README.

---

## Questions

1. **How does the shield qualify for cloud when quasi-identifier classes (location, employer, school, relationship_descriptor, unique_event, health_condition) can't plausibly reach ~600 labelled positives, and which classes are "taxonomy classes" for gate item 1?** (§3.7 run-time gate 1; §12 follow-up 3 leaves it open.)
   Why it matters: gate 1 requires every taxonomy class and every declared language to pass with no INSUFFICIENT_SUPPORT. Read literally, the cloud tier may never unlock. It's also unclear whether "taxonomy class" means the PII entity classes or the 55/99 enrichment labels. Per-language multiplies the labelling. This decides whether P4's cloud path is buildable or only scaffolding, and how much of P3/P4 gets planned as testable.

2. **Is the gate token's "final serialized request bytes at the transport layer" (RT-17) feasible with the Anthropic SDK? What is the fallback if it isn't?**
   Why it matters: the hash must survive retries, the SDK's headers, and any request-body changes, and the SDK may build bytes inside httpx. If the hook isn't feasible, the whole gate design (a §5 contract) changes. RT-17 is open, but it is a P3 dependency and not obviously left to the builder.

3. **What is the unit and procedure for "second opinion" sampling when the sample (n ≥ 3/ε ≈ 600 chunks) is drawn from a case that may have fewer chunks? Is it per run, per case, or per class?** (§3.7 gate 3.)
   Why it matters: "all of them if fewer" means a tiny case passes on a trivial sample. Does a sample drawn per run mean a fresh 600-chunk local-LLM pass on every cloud run? The cost and latency shape the P3/P4 pipeline and the cache.

4. **Is the ChatX "local-only" label policy applied at chunk level to every fine label, so that effectively only coarse labels with cloud_allowed=true can ever be enriched in the cloud? And who classifies a chunk as carrying a local-only label before cloud enrichment, given that the labels are the output of enrichment?** (§3.7 content sensitivity; §3.9.)
   Why it matters: this is circular. Local enrichment must run first to find local-only labels, and only then is the chunk cloud-eligible. The ordering and the data flow (§4) don't show a local-pass-then-cloud-pass design. It changes P4 stage structure and cache keys.

5. **How is `content_involving_minors` detected, and by what labelled evaluation?** (§3.7, §3.10, §3.11: "flagged locally and excluded from every export".)
   Why it matters: it's a hard exclusion with no detector, definition, or recall target. A heuristic vs. a taxonomy label vs. a model call changes P3 scope and the export test plan.

6. **Does the core iterate a source into canonical messages with the quarantine/disposition accounting inside the core, or does ChatX do it? Where does the "acquire into sources/ with sha256" step live?** (§3.5 acquisition and AcquisitionContext are app-side; §4 puts "acquisition via the backup API" under core `sources/imessage/`; the core has "no storage".)
   Why it matters: the module boundary is ambiguous. dNh would need acquisition (backup API, WAL-safe) from the core, but the core is also said to have no storage. It affects the API of the core package and the dNh adapter, and it is fixed early in P1.

7. **What does the dNh adapter do for platforms/rules when `msg.outbound.imported` doesn't exist yet, and who owns that dNh change on the timeline of the 30-day parallel run?** (§9 rule 4, V14.)
   Why it matters: the parallel run compares the adapter against dNh's own parsers. If outbound is skipped, the comparison is inherently partial, and the "never disagree" criterion may be vacuously or wrongly satisfied. It also affects when P1 can be called done.

8. **What default value and procedure for `--default-region` (phone normalisation) and for `--me`/the owner's handle set on iMessage?** (§3.4, §4.)
   Why it matters: direction for non-iMessage sources depends on `--me`, and phone normalisation depends on region. A wrong default silently changes handles, which feed msg_id and pseudonyms (non-reversible once ids are published).

9. **What are the exact definitions of "kill-rate floor" for mutmut and the throughput/latency numbers promoted to gates?** (§5.8, §7.) Partly left as measurements, but the mutation floor value is never given.
   Why it matters: a P3 exit criterion that says "mutation floor" with no number can't be verified. A planner needs a number, or an explicit rule for who sets it.

10. **What retention/deletion semantics apply to derived and cached cloud data after `delete-source` (cached enrichments keyed by content hash, `shield_evals`, bundles already exported, `msg_id_aliases`)?** (§3.12.)
    Why it matters: "everything derived from it" is clear for cascade tables but not for exported bundles or the audit rows the design keeps; this affects the FK/DDL plan and the purge tests.

11. **P0 exit requires "dNh CI installs a pinned wheel", but dNh changes go through dNh governance and merging is dNh's decision.** Is a dNh branch with a green CI sufficient, or must dNh merge?
    Why it matters: it can block P0/P1 exits on an external process.

## Contradictions

1. **Embedding provider vs local-only wording.** §2 G4 says "Embedding providers: local only" and §3.6 refuses non-local hosts, yet §3.6 says "A remote embedder would have to pass through the same gate". Mild: it reads as "none built in v2", but G4/anti-goals say "Sending chunk text to a cloud embedding service" is an anti-goal outright, which conflicts with the "could pass through the gate" allowance.

2. **Gate item 1 vs P3 exit.** §3.7 gate 1 requires a real-sample report "for every taxonomy class and every declared language", but §6 P3 says passing "synthetic results unlocks the local pipeline only" and the cloud tier is a "separate local gate". §1 says the recall is "per taxonomy class". It is unclear whether the local judge (gate 3) also needs the real sample ("its own recall is measured on the labelled set"). Not a hard conflict, but the P3 scope boundary is inconsistent about where real-sample work lands.

3. **Hysteresis thresholds.** §3.9: "τ 0.70, τ_low 0.62 and τ_high 0.78". A label "enters at τ_high, exits below τ_low". So what τ = 0.70 does is not defined. It is either unused or an unstated third threshold.

4. **Special-category labels vs "Every fine label is local-only".** §3.7 says every fine label is local-only and lists coarse labels with `cloud_allowed: false`. §3.9 says `cloud_allowed` defaults to false and the owner approves "label by label", and the §12 follow-up asks the owner to approve each label's value. Under the §3.7 rule, fine labels have no choice, so this is a policy-versus-per-label-approval overlap.

5. **Exit codes for refusals.** §3.12 says "Every refusal is an RFC 9457 problem with exit 3" (§3.7), but `E_SQLITE_TOO_OLD`, `E_TZ_REQUIRED`, `E_CASE_LOCKED`, and `E_PROVIDER_NOT_LOCAL` are refusals not clearly gate refusals; the table defines 3 only as "gate refused" and 1 as "error", so which code each takes is ambiguous (P0/P3 tests cite "exit 3" for `E_PROVIDER_NOT_LOCAL`, `E_VENDOR_TERMS`, `E_VISIBILITY_LEAK`).

6. **Pseudonyms: HMAC vs sequential surrogates.** §3.7 says `sender.pseudonym` is HMAC-SHA256, 128 bits, but §3.7 Chunk construction says "Pseudonyms everywhere... Chunk lines use `sender.pseudonym`" while §3.7 redaction tokens `⟦PERSON_0007⟧` are surrogates. Whether chunk lines show the HMAC pseudonym or a surrogate (and whether the HMAC value is linkable across cases or cloud calls) is not stated. §14 notes HMAC is kept for handles only.

7. **Chunking in P2, pseudonymization in P3.** §3.8 says chunk lines use pseudonyms and §4 data flow is `identity → chunk → shield`, but surrogates/map custody (§3.7) and the shield are P3 deliverables while chunking is P2 (`chatx identity` is in no phase's scope explicitly except P1 "identity").

8. **MCP phase.** §2 Non-goals say "CLI and, later, an MCP server only"; §3.12 labels MCP phase 7 and §6 P7 matches, but the §3.11 "Experiments" list and §3.13 refer to "out of scope until P6" for encrypted backups while the §8 table says P6. Consistent, so not a conflict. (Included only for completeness: none beyond the above.)

9. **Cache key vs sampling.** §3.9 cache key lists many fields, but §3.6 says the reproducibility mechanism is the cache and "a seed is only a hint"; no field covers the sampling parameters apart from `call_config_hash`. Fine, since it is included. Not a conflict.
