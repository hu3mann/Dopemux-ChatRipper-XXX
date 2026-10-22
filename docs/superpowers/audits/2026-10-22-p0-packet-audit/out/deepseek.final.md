I've read the brief, the harness facts, the packet, the rev 2.1 design, next-steps, SHA256SUMS, and the dNh bundle, plus verified three external facts (uv cross-workspace `workspace` source, `uv export --no-emit-workspace`, uv.lock hash semantics) against docs.astral.sh and GitHub issues. Here are the two deliverables.

=== FILE: report-deepseek.md ===
# ChatX P0 "Workspace" Packet — Audit Report (deepseek)

**Reviewer identity block**
- Model: deepseek (audit lane name per wrapper prompt; concrete model id not independently verifiable — no runtime receipt).
- Runner: cmd, print mode (read-only; no write_file/shell_command/git/uv/python available).
- Knowledge cutoff: 2025 (approximate; post-cutoff tool behaviours — uv 0.12.11, SQLite 3.51.3, GitHub Actions — are flagged PLAUSIBLE unless corroborated by the cited web sources).
- Files opened: /Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit/PROMPT-master.md, .../out/HARNESS-FACTS.md, .../inputs/2026-10-21-p0-workspace-packet.md, .../inputs/2026-10-21-next-steps.md, .../inputs/2026-10-20-chatx-rearchitecture-design.md, .../inputs/SHA256SUMS, .../bundles/dnh-packaging-bundle.md. All dNh evidence is from the bundle snapshot at dNh HEAD e8bbcadb; ChatX evidence is from the inputs/ snapshots at cc18536.

**Packet verdict: APPROVE-WITH-CHANGES** — the packet faithfully encodes G-A/G-B/G-E, the exit criteria and the authority stops, but it carries one stale rev-2 quote, a core-version contradiction, and two unproven mechanisms (X4 wheel-pinning/auth, and a floor-compliant CI interpreter) that must be closed before Task 1.

**Findings table**

| ID | Severity | Verdict | Where | Finding | Evidence | Fix |
| --- | --- | --- | --- | --- | --- | --- |
| DSK-F01 | HIGH | CONFIRMED | packet:L81 | [S6] X4 says dNh CI will "install a pinned wheel" from the core-v0.0.1a0 pre-release assets but specifies no mechanism: (a) how dNh's CI authenticates to a private repo's release asset, and (b) how the sha256 is enforced, since uv.lock hashes registry distributions but not URL/path sources. | "core installed from a wheel pinned by version and sha256 (--require-hashes or equivalent in the lock)"; dnh ci.yml has no download step. | Specify an authenticated `gh release download` + explicit sha256 check in dNh CI, and drop the "or equivalent in the lock" claim. |
| DSK-F02 | HIGH | PLAUSIBLE | packet:L247 | [S4] CI's green run and X5 depend on the GitHub macOS runner's Python linking SQLite >= 3.51.3, which is unverified and plausibly false (3.51.3 is recent); the packet preflights only local interpreters (Task 1 Step 1) and Stop S3 fires with no CI remediation path. | "macOS arm64 required"; S3 "CI's macOS arm64 interpreter reports below the floor"; owner machine links 3.53.1 (harness). | Add a CI step to install/verify a known floor-compliant CPython (python-build-standalone 3.12.x linking >= 3.51.3) and record which build. |
| DSK-F03 | MEDIUM | CONFIRMED | packet:L207 | [S2] Task 4 declares the core only via `[tool.uv.sources] workspace = true` but never adds chat-extraction-core to the app's `[project].dependencies`, so the workspace relationship is unexercised; and any `>=0.0.1` bound would exclude the 0.0.1a0 pre-release (PEP 440 sorts pre-releases first). | "Consumes: chat_extraction_core as a workspace dependency ([tool.uv.sources]...)" with no dependencies line. | Add `chat-extraction-core==0.0.1a0` (exact, pre-release-safe) to app `[project].dependencies`. |
| DSK-F04 | MEDIUM | CONFIRMED | packet:L186 | [S2] Task 3 sets core `__version__ = "0.0.0"` but B4/G-E decide the core starts at 0.0.1a0; wheel metadata (0.0.1a0) would contradict the runtime attribute. | "__version__: str ("0.0.0", proposed)" vs B4 "the core starts at 0.0.1a0". | Set `__version__ = "0.0.1a0"` and derive it from pyproject `version`. |
| DSK-F05 | MEDIUM | CONFIRMED | packet:L56,L78 | [S14] X1 and the Scope exit quote carry the stale rev-2 wording "exit 3, E_GATE_MISMATCH, E_SCHEMA_MISSING stubs", implying both are exit 3, contradicting rev 2.1's reworded §6 and the packet's own G-B note. | spec L871 reads "E_GATE_MISMATCH → exit 3 and E_SCHEMA_MISSING → exit 1, per §3.12, as stubs". | Update both quotes to the rev 2.1 wording. |
| DSK-F06 | MEDIUM | CONFIRMED | packet:L245,B3 | [S4] Action pinning is specified as "exact tags", not commit SHAs; supply-chain best practice (and the brief's tag-vs-SHA question) wants full-SHA pinning; dNh's own workflows use floating `@v7`/`@v3`. | "pin at build time to exact tags and record them in the commit message". | Pin each action to a full commit SHA and record the SHA. |
| DSK-F07 | MEDIUM | CONFIRMED | packet:L247 | [S13] No least-privilege `permissions:` block is specified; ci.yml needs `contents: read` and release.yml needs `contents: write` for `gh release create` (only noted in prose, not in the workflow spec). | Task 6 lists jobs with no `permissions:` key. | Add `permissions: contents: read` to ci.yml and `contents: write` to release.yml. |
| DSK-F08 | MEDIUM | CONFIRMED | packet:L257 | [S5] release.yml names the release from `$GITHUB_REF_NAME` (core-v0.0.1a0) but never validates that the built wheel version (0.0.1a0) matches the tag suffix; a mismatched tag/version would publish silently. | "gh release create "$GITHUB_REF_NAME" --prerelease". | Add a release.yml step asserting the wheel version equals the tag minus the `core-v` prefix. |
| DSK-F09 | MEDIUM | PLAUSIBLE | packet:L276 | [S5] Task 7 Step 5 says CI and release wheel digests are "expected to match", but Python wheels are not byte-reproducible without SOURCE_DATE_EPOCH, so they will likely differ; non-fatal is correct, the wording misleads. | "they are expected to match; if they differ ... byte-reproducible wheel builds are not a P0 gate". | State the release asset SHA256SUMS is authoritative and CI's digest is advisory; optionally set SOURCE_DATE_EPOCH. |
| DSK-F10 | MEDIUM | PLAUSIBLE | packet:L292 | [S4] B8's `uv export --frozen --all-packages --no-emit-workspace` hits a documented uv bug where `--all-packages` ignores `--no-emit-workspace` (emits `-e .`), which pip-audit may reject. | astral-sh/uv issue #18070 (title: "uv export ignores --no-emit-workspace if --all-packages is passed"). | Verify on uv 0.12.11 and fall back to `--no-emit-project` or a filtered export. |
| DSK-F11 | MEDIUM | CONFIRMED | packet:L276 | [S5] Nothing enforces that the tag is pushed only after ci.yml is green; tag pushes bypass branch protection, so a red-CI tag still publishes a wheel. | Task 7 Step 5 "once its CI is green: tag" is procedural only. | Add a release.yml guard (or environment protection) requiring green CI for the tagged commit. |
| DSK-F12 | MEDIUM | PLAUSIBLE | packet:L189,L205 | [S2] hatchling does not auto-include LICENSE or THIRD_PARTY_NOTICES.md in the wheel, yet the packet claims notices "ship with both packages"; no `[tool.hatch.build]` include/license-files config is specified. | owner item 13 "third-party notices ship with both packages"; no hatch build config in Tasks 3-4. | Add hatchling include config so LICENSE and THIRD_PARTY_NOTICES.md land in each wheel. |
| DSK-F13 | MEDIUM | CONFIRMED | packet:L3,L149 | [S11] No per-task estimate, model assignment, or call/retry budget is stated (scope 11), and the subagent-driven-development instruction does not explicitly bind subagents to stops S1-S9, which require owner/supervisor authority a subagent cannot grant. | "Use superpowers:subagent-driven-development ... implement this plan task-by-task". | Add a budget line per task and state stop conditions bind subagents. |
| DSK-F14 | MEDIUM | PLAUSIBLE | packet:L119 | [S1] The `workspace = "../chatstack"` cross-workspace form is confirmed (docs.astral.sh), but the packet doesn't state the expected dNh lockfile delta or guard against uv silently pulling other chatstack members into dNh's resolution. | "uv resolves the member named chat-extraction-core". | Specify the expected dNh lock delta and verify only chat-extraction-core plus its deps enter dNh's lock. |
| DSK-F15 | LOW | PLAUSIBLE | packet:L161 | [S1] The root virtual pyproject carries a bare `requires-python = ">=3.12"` but a virtual root has no `[project]`; PEP 621 puts requires-python under `[project]`, so the key is misplaced. | root pyproject listed with "requires-python = ">=3.12"" and no `[project]`. | Remove root-level requires-python; rely on member-level requires-python and `.python-version`. |
| DSK-F16 | LOW | CONFIRMED | packet:L140 | [S5] `docs/release-notes/` is used by Task 7 Step 5 but absent from the file-structure listing (docs/ shows design/adr/reference/p0-exit-record only). | file structure lines 140-144. | Add `docs/release-notes/` to the structure listing. |
| DSK-F17 | LOW | CONFIRMED | packet:L97,L173 | [S8] S10's check text says `sha256sum` while Task 2 Step 1 uses `shasum -a 256`; the macOS host has `shasum`, not `sha256sum` by default. | "sha256sum of the copy" vs "shasum -a 256". | Use `shasum -a 256` consistently on the macOS host. |
| DSK-F18 | LOW | CONFIRMED | packet:L211 | [S3] The exit-3 "failure path" is asserted as an attribute (`GateMismatchError.exit_code == 3`), not an actual process exit; G-A's "app entry point mapping E_GATE_MISMATCH to exit 3" implies an entry point that does not exist at P0. | "assert e.value.exit_code == 3". | Record in p0-exit-record.md that exit 3 is asserted at the attribute level, with the real CLI exit deferred to P1. |
| DSK-F19 | LOW | CONFIRMED | packet:L304 | [S7] `meets_floor` parses 3-part versions only; 4-part strings (e.g. 3.51.3.x) are unhandled and the parametrized tests cover only 3-part cases (acknowledged in Review Focus 3). | "four-part strings are not covered by the spec (UNKNOWN...)". | Have `meets_floor` define or reject 4-part strings and add a test. |
| DSK-F20 | LOW | CONFIRMED | packet:L247 | [S4] ci.yml specifies no job `timeout-minutes` and no uv/cache pinning; defaults (6h timeout, no explicit cache) are weaker than best practice. | jobs listed with steps only. | Set `timeout-minutes` and enable setup-uv caching. |
| DSK-F21 | INFO | CONFIRMED | packet:L312,S5 | [S12] G-C is resolved by S5 asserting both `config/arch-gates.yml` and `.github/workflows/arch-gates.yml` absent, but the packet should name spec L728's actual source path (config/arch-gates.yml) as the "not carried" artifact. | spec L728 "config/arch-gates.yml ... rewritten in P0, not carried". | Cite the exact source path in S5. |
| DSK-F22 | INFO | CONFIRMED | packet:L296 | [S12] G-F remains partially open: remote name DDD-Enterprises/chatstack and private visibility are proposed, not decided; owner must confirm before Task 7 (gated behind S1). | "Remote owner, name and visibility are UNKNOWN; proposed DDD-Enterprises/chatstack, private". | Get explicit owner confirmation of name/visibility in the pre-approval checklist. |
| DSK-F23 | INFO | PLAUSIBLE | packet:L257 | [S13] Trusted Publishing (no PyPI) is correctly not used, but the published wheel has no SBOM/SLSA provenance or `--attestations` on the release. | "No PyPI or other index at P0". | Optionally add provenance attestation to release assets. |
| DSK-F24 | INFO | CONFIRMED | dnh:pyproject.toml:112 | [S15] dNh duplicates its dev deps in both `[dependency-groups]` and `[project.optional-dependencies]` (legacy); the chatstack root should use only `[dependency-groups]` (PEP 735). | bundle shows identical dev lists in both tables. | Use a single dependency-group in chatstack; do not copy the duplication. |

**Decision challenges**

- **G-E (tag at P0 with adapter-test NOT_RUN).** The packet ends P0 by tagging `core-v0.0.1a0` while the release-contract precondition (spec L143: "Before tagging, the core's CI runs dNh's adapter tests against the new wheel") is recorded NOT_RUN. For: the 0.0.1a0 wheel is empty (only stubs), so there is no adapter surface and NOT_RUN is honest. Against: it establishes that tags can be cut without adapter proof, and dNh will pin a wheel whose adapter is unverified. Cost of being wrong: low today (no functional risk), but the contract's teeth are blunted. Settle it: confirm the 0.0.1a0 wheel contains no adapter-relevant code and record that explicitly in the release notes.
- **B14 private visibility vs public.** An MIT core published as a private repo's release asset forces authenticated downloads in dNh's CI (DSK-F01). For: private matches "new clean repo" caution. Against: public would make X4's asset download trivial and is consistent with MIT intent. Cost of being wrong: private adds auth friction to every consumer; public exposes only a stub wheel (harmless). Settle it: owner states whether non-dNh consumers are anticipated.
- **Core version 0.0.1a0 (pre-release) vs 0.0.1.** A pre-release forces exact-pin discipline everywhere (DSK-F03) and `--pre`-style handling. For: signals alpha status. Against: `>=0.0.1` bounds silently exclude it, a trap for dNh and the app. Cost of being wrong: mis-pinning breaks installs silently; a final 0.0.1 avoids the trap but loses the alpha signal. Settle it: owner confirms the alpha semantics are worth the pinning friction, or the first tag uses 0.0.1.

**Unverified impressions**

- The GitHub macOS arm64 runner's Python may link SQLite below 3.51.3 (could not run it; DSK-F02).
- uv 0.12.11's `--no-emit-workspace` behaviour with `--all-packages` may differ from the reported issue #18070 (DSK-F10).
- uv.lock's ability to hash a URL/GitHub-release source wheel by sha256 is unconfirmed (issue #16818 shows path-based wheels lack hashes; URL sources untested here).
- Whether `uv pip show chat-extraction-core` reports the workspace-resolved package as the packet expects.
- dNh `uv.lock` revision 3 compatibility with adding a workspace source under uv 0.12.11.

=== FILE: preapproval-deepseek.md ===
# Pre-approval checklist — ChatX P0 packet (deepseek)

| ID | Check | How to verify | Blocking? |
| --- | --- | --- | --- |
| DSK-C01 | Resolve the core version contradiction (`__version__` 0.0.0 vs 0.0.1a0). | Read packet L186 vs B4; confirm `__version__ = "0.0.1a0"` in Task 3. | yes |
| DSK-C02 | Update X1/S4 exit-criteria text to the rev 2.1 wording. | Diff packet L56/L78 against spec L871; the arrow wording must match. | yes |
| DSK-C03 | Decide the X4 wheel-pinning mechanism and dNh CI auth. | Write the dNh CI download+hash step, or confirm the owner accepts the NOT_RUN hand-off as-is. | yes |
| DSK-C04 | Verify a floor-compliant interpreter exists on the CI macOS runner. | Run `python -c "import sqlite3;print(sqlite3.sqlite_version)"` on macos-14/15 arm64. | yes |
| DSK-C05 | Confirm the app declares `chat-extraction-core==0.0.1a0` in `[project].dependencies`. | Read apps/chatx/pyproject.toml after Task 4. | yes |
| DSK-C06 | Confirm remote name and visibility (B14). | Owner states DDD-Enterprises/chatstack, private or public. | yes |
| DSK-C07 | Confirm actions pinned to commit SHA, not tags. | `grep uses:` in both workflows; each should be a full SHA. | yes |
| DSK-C08 | Add least-privilege `permissions:` blocks. | Read ci.yml (contents: read) and release.yml (contents: write). | yes |
| DSK-C09 | Add a release tag/version match assertion. | Read release.yml for a step comparing wheel version to tag suffix. | no |
| DSK-C10 | Fix the "expected to match" reproducibility wording and decide SOURCE_DATE_EPOCH. | Read Task 7 Step 5 text; confirm release SHA256SUMS is authoritative. | no |
| DSK-C11 | Verify `uv export --no-emit-workspace` on uv 0.12.11. | Run `uv export --frozen --all-packages --no-emit-workspace`. | yes |
| DSK-C12 | Confirm LICENSE and THIRD_PARTY_NOTICES.md ship in the wheel. | `uv build --package chat-extraction-core` then `unzip -l` the wheel. | yes |
| DSK-C13 | Add per-task estimates/budget and bind subagents to stops S1-S9. | Read the packet Tasks for budget lines and a subagent-stop clause. | no |
| DSK-C14 | Confirm the `workspace = "../chatstack"` dNh lock delta contains only the core and its deps. | Run `uv lock` on the dNh branch and inspect the `uv.lock` diff. | yes |
| DSK-C15 | Remove root-level `requires-python` from the virtual root pyproject. | Read the root pyproject.toml; it should have no stray PEP 621 key. | no |
| DSK-C16 | Decide 4-part SQLite version handling in `meets_floor`. | Read sqlite_floor.py and its test for a 4-part case. | no |
| DSK-C17 | Add a tag-before-green guard to release.yml. | Read release.yml for a CI-green precondition on the tagged commit. | no |
| DSK-C18 | Confirm the attribute-level exit-3 stub is acceptable for P0. | Owner confirms stub-level exit assertion is fine; real CLI exit is P1. | no |

**What I could not check**

- Live dNh repo files not in the bundle (e.g. `src/dnh_crm/`, `scripts/release_check.sh`) — all dNh evidence is from `bundles/dnh-packaging-bundle.md`.
- I could not run `git`, `uv`, `python3`, `wc` or `shasum` (print-mode runner); every hash, line count, HEAD and version above is harness-supplied from `out/HARNESS-FACTS.md`, not my own measurement.
- GitHub runner SQLite versions and uv 0.12.11 flag behaviours beyond the cited docs.astral.sh and GitHub issues.
- The prior design-audit files (`cross-audit-matrix.md`, `design-revision-plan.md`, `builder-check-rev2.md`) referenced in the brief, which live outside this folder and were not needed to re-audit the design.

=== END ===
