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
