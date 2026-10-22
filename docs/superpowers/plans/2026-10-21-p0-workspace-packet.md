# ChatX Re-architecture, Phase P0 "Workspace" Implementation Packet

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not start until the supervisor records owner approval.

Status: rev 2.2 — DRAFT, not approved. The owner decided the three open gaps (G-A, G-B, G-E) on 2026-10-22 and the spec is at rev 2.2; nothing here executes until the owner approves this packet.
Date: 2026-10-21 (rev 2.2: 2026-10-22, audit response)
Plan step: S2 of `docs/superpowers/plans/2026-10-21-next-steps.md` (draft by Sonnet, supervisor reviews).

**Goal:** Create the `~/code/chatstack` uv workspace with two packages that hold only metadata and the P0 failure-path stubs (G-A), a CI that proves the installed wheel works, and the `core-v0.0.1a0` pre-release dNh can pin (G-E), so P0.5 and P1 have somewhere to land.

**Architecture:** A new git repo (owner item 1) whose root is a uv workspace (`members = ["packages/*", "apps/*"]`). `packages/chat-extraction-core` (MIT) and `apps/chatx` hold only package metadata, a version, and the minimal code the failure-path stubs need. CI builds wheels, installs them in a fresh venv outside the checkout, and runs the tests there.

**Tech Stack:** Python `>=3.12`, uv (0.12.11 present locally), hatchling, ruff, `mypy --strict` (core) and a strict configuration (app), pytest + pytest-cov, pre-commit, `uv lock --check`, `pip-audit`, GitHub Actions.

**Spec:** `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md` (rev 2.2, 1,275 lines, sha256 `3f60d5123b3cb5d10b9a68cc5004bfa1084293bee17b1c026679fa80cc2cea78`; rev 2.2 changes only the §6 P0-row clause on the dNh checks, adds the §14 "Rev 2.1 → rev 2.2" block, and bumps the header Status / Revisions rows (lines 5–6) to 2.2).

## Changes in rev 2.2 (audit 2026-10-22)

Source: `docs/superpowers/audits/2026-10-22-p0-packet-audit/out/cross-audit-matrix.md` (10 BLOCKERs and ASP-F01). "Was" line numbers refer to rev 2.1.

| Finding ID(s) | Location (packet / spec) | Edit made |
|---|---|---|
| ARG-F02, AST-F01, GRK-F01, KIM-F01 | Task 3 Interfaces (was L186, L190); B4; new `test_core_version_is_0_0_1a0` | Core version `"0.0.0"` replaced by `0.0.1a0` in `__version__` and `[project] version`; one authoritative version; the installed-wheel tests assert metadata version = `__version__` = `0.0.1a0`; `release.yml` asserts tag = `core-v` + version. B4 marks the core version decided. The app keeps its own `0.0.0` |
| ARG-F01 | Task 6 job 3 (was L253) | Installed-wheel steps moved into composite action `.github/actions/wheel-tests`; venv install uses constraints from `uv export --frozen --all-packages --no-emit-workspace --no-hashes`, no `--no-deps`, so nothing floats; pytest gets `-c "$GITHUB_WORKSPACE/pyproject.toml"`. The matrix fix asked for `--require-hashes`; D4 chose version constraints without hashes, so the install is version-pinned, not hash-verified |
| ARG-F03 (also AST-F20, KIM-F06) | Task 6 Interfaces (was L257) | Top-level `permissions: contents: read` in both workflows; `contents: write` on the `release` job only; explicit `GH_TOKEN: ${{ github.token }}` on `gh` steps; no other scopes |
| ASP-F02, AST-F22 (also AST-F21, DSK-F11, KIM-F20, ARG-F17, DSK-F08, ARG-F18, DSK-F09, KIM-F13) | Task 6 job 5 (was L257); Task 7 Step 5 (was L276); G-E; B9 | `release.yml` now: (a) requires a successful `ci.yml` run for the tagged commit, (b) builds from the tagged tree, (c) runs the same composite-action tests on that exact wheel and checks tag = `core-v` + version, (d) only then writes `SHA256SUMS` and `gh release create --prerelease` with wheel, `SHA256SUMS`, notes file, (e) records sha256 and release URL. The "expected to match / may differ" digest text is removed; published bytes are the tested bytes |
| ARG-F05 (also GRK-F03, GRK-F02, DSK-F05, AST-F03 in part) | Out of scope (was L66); Scope quote (was L56); X1 (was L78) | Stale "whether P0 cuts one is UNKNOWN" replaced by the G-E statement (P0 ends by cutting `core-v0.0.1a0`); the Scope exit-criteria quote and X1 now quote spec rev 2.2 / rev 2.1 wording (`E_GATE_MISMATCH` → exit 3, `E_SCHEMA_MISSING` → exit 1) |
| ARG-F04 (also AST-F26 in part) | Downstream handoff section (was Cross-repo, L112–121); was X4 (L81) | Private-repo access is carried as the explicit OPEN OWNER DECISION B14 in the new section, to be chosen before the handoff is issued |
| ASP-F01 (spec side AST-F02) | Packet: X3/X4 rows removed (was L80–81), new X6 row, section "Downstream handoff to dNh (not a ChatX exit criterion)" with H1/H2, Task 7 Step 6 (was L277) and new completion contract, G-D, G-E, S6, B9 cross-references; spec: §6 P0 row (L871) and new §14 block "Rev 2.1 → rev 2.2" | X3/X4 become H1/H2 outside the ChatX exit criteria; the handoff is issued and recorded (X6), never carried as NOT_RUN gates. Spec §6 clause replaced as decided; spec §14 records it citing owner decision 5 and ASP-F01/AST-F02 |
| In-place, not on the scope list | Task 6 job 3 sqlite step (ARG-F06, AST-F16, GRK-F05); File structure; Task 2 commit message; header and spec reference line | `record_sqlite_version.py` output is also teed to `sqlite-version.txt` so the upload path exists; `release.yml` and the action added to the file structure; commit message says "rev 2.2 copy"; header, date and spec reference (rev 2.2, 1,275 lines, sha256) updated |
| argon decision challenge 2 (pre-approval check ARG-C01) | Downstream handoff, procedure step 3 | Spec L147 `{ workspace = "../chatstack" }` verified against uv 0.12.11 by the supervisor (`uv lock --offline`, non-member consumer): resolves, locks as an *editable* source; bare `path =` locks as a non-editable directory. Procedure step 3 now records this and keeps `editable = true` on the path form. Receipt: audit `out/arg-c01-uv-workspace-syntax.txt` |

Deferred to rev 2.3: HIGH/MEDIUM findings not on edited lines (see `cross-audit-matrix.md`). Not addressed here, among others: action pinning by commit SHA and runner labels (AST-F19, ARG-F22), `sha256sum` versus `shasum` on macOS runners (GRK-F13, ARG-F08), `uv sync --locked` and branch-CI trigger details for the dNh handoff (ARG-F04 fix text, DSK-F01, AST-F27, GRK-F08, KIM-F15), X2 command marker (GRK-F04, KIM-F02), the clean-clone job's checkout (AST-F17, GRK-F07, KIM-F05) and the recorded-SHA sequencing in Task 7 Step 3 (AST-F30, ARG-F21, GRK-F23).

## Inputs (spec line ranges actually read)

| Spec lines | Section |
|---|---|
| 120–126 | §3.1 shared extraction core seam |
| 127–151 | §3.2 layout, new repo, dNh consumption, licence |
| 152–165 | §3.3 toolchain, SQLite floor (heading `### 3.4` is at line 166) |
| 653–668 | §3.12 CLI, errors, exit codes (read to resolve exit-code mapping) |
| 722–730 | §8 keep-list tail (line 728: `config/arch-gates.yml` and `.github/workflows/*` rewritten in P0) |
| 771–833 | §4 target architecture |
| 834–862 | §5 contracts |
| 863–884 | §6 phases (P0 row quoted below) |
| 885–922 | §7 quality gates |
| 1078–1090 | §11 left to the builder |
| 1091–1122 | §12 owner decisions (1 and 13 apply) |
| 1174 | T18 row (packaging) |

Also read: `docs/superpowers/plans/2026-10-21-next-steps.md` (S2 row) and the writing-plans skill. Supervisor review (2026-10-21) added `docs/superpowers/audits/2026-10-20-design-audit/out/external-fact-check.md` row E8 (uv cross-workspace `workspace = "<path>"` form, SUPPORTED), which resolves G-D below.

## Global Constraints (verbatim from the spec)

- Python: `>=3.12` (line 154).
- SQLite floor: "the runtime must link SQLite ≥ 3.51.3, or a 3.50.x ≥ 3.50.7, or a 3.44.x ≥ 3.44.6 (the backports)" (spec line 156). Below the floor a case is refused with `E_SQLITE_TOO_OLD` (line 157). Measured 2026-10-21 (line 158): old ChatX and dNh venvs link 3.47.1 (below floor); mise's Python 3.12.13 links 3.53.1.
- Tools: `uv`, hatchling, `ruff`, `mypy --strict` for the core and a strict configuration for the app, `pytest` + `pytest-cov`, `pre-commit`, `uv lock --check` in CI (line 159).
- Core dependencies, nothing else: `pydantic>=2,<3`, `phonenumbers>=8,<9` (line 160). No network, LLM or storage dependencies in the core. App bounds are `>=x,<next-major` (line 162).
- Package data loads through `importlib.resources`, never `Path(__file__).parents[n]`; a missing schema resource is `E_SCHEMA_MISSING`, never a skip (line 162).
- Layout (lines 130–139): `~/code/chatstack/` with `pyproject.toml` (`[tool.uv.workspace] members = ["packages/*", "apps/*"]`), `uv.lock`, `packages/chat-extraction-core/` (MIT), `apps/chatx/`. No workspace root at `~/code`.
- New repo, not a history carry (owner item 1). Core is MIT-licensed and owned by DDD-Enterprises; third-party notices ship with both packages (owner item 13, line 150).
- Coverage: `--cov-fail-under=90` over `chat_extraction_core` and `chatx`, no `omit` beyond `tests/` (line 841–843).
- Exit codes (lines 657–664): 0 success; 1 other error including `E_SQLITE_TOO_OLD`, `E_SCHEMA_MISSING`; 2 usage; 3 egress refused including `E_GATE_MISMATCH`; 4 partial.

## Scope

In scope (P0 only), quoting the §6 P0 "Scope" cell (spec line 871):

> `~/code/chatstack` repo; uv workspace; two empty packages; CI (ruff, mypy, pytest, `uv lock --check`, `pip-audit`) testing the **installed wheel** in a fresh venv outside the checkout; `.github/workflows/*` rewritten, `arch-gates.yml` not carried; pre-commit; ADR template; `conformance.md` skeleton; an interpreter linking SQLite at or above the floor; this document copied in

Exit criteria, quoted from the same row:

> A green CI run, its URL recorded, that includes the failure-path tests (`E_GATE_MISMATCH` → exit 3 and `E_SCHEMA_MISSING` → exit 1, per §3.12, as stubs); `uv sync` works from a clean clone; a downstream handoff to dNh (branch resolution by both uv source forms; CI installing the pinned wheel) is issued and recorded in the P0 exit record; completing and merging it are dNh decisions, not ChatX exit criteria; `sqlite_version` recorded and ≥ floor

## Out of scope

- P0.5 spikes (a)–(e), including anything touching the owner's `chat.db` or dNh's database.
- P1 and later: schema v2 models, parsers, fixtures, the real error registry, the CLI, the case store, the shield, providers. Nothing from the §8 keep-list is ported in P0.
- Any edit to the rev 2.2 spec or to `Dopemux-ChatRipperXXX` other than this packet. The old repo's tag `pre-rearchitecture-2026-10-20` and archiving (P7) are not P0.
- Any edit to `/Users/hue/code/dNh_CRM` (see Downstream handoff to dNh).
- Control Tower registration and TaskMaster list archival (S6 in the next-steps plan).
- Mutation testing (`mutmut`), property tests, fixture builders, perf markers, the real-sample shield evaluation. These gates apply from later phases.
- Core releases other than `core-v0.0.1a0`: tag `core-vX.Y.Z` cutting is the release contract (line 142); P0 ends by cutting exactly one pre-release, `core-v0.0.1a0` (G-E, B9, Task 7 Step 5). Any later tag is not P0.
- The dNh-side checks (branch resolution, dNh CI installing the pinned wheel): see Downstream handoff to dNh. P0 issues the handoff; it does not run or wait for those checks.

## Acceptance checks

All State values start `NOT_RUN`. Preserve `PASS` / `FAIL` / `NOT_RUN` / `UNKNOWN` literally; never collapse `NOT_RUN` into `PASS`.

### Exit criteria (§6 P0 row, spec line 871)

The row is one cell with four semicolon-separated criteria, checked as X1, X2, X6 (handoff issued and recorded) and X5. Rev 2.2 removed the former rows X3 and X4: they are dNh-side checks, now H1 and H2 in Downstream handoff to dNh. Text is verbatim from spec rev 2.2.

| ID | Criterion (verbatim) | How it will be checked | State |
|---|---|---|---|
| X1 | A green CI run, its URL recorded, that includes the failure-path tests (`E_GATE_MISMATCH` → exit 3 and `E_SCHEMA_MISSING` → exit 1, per §3.12, as stubs) | `gh run list -R <repo> --workflow ci.yml --limit 1 --json conclusion,url,headSha` returns `success` for the exact commit; `gh run view <id> --log` shows the three failure-path tests passed (not skipped); URL written to `docs/p0-exit-record.md` (path proposed, B12) | NOT_RUN |
| X2 | `uv sync` works from a clean clone | `git clone <remote> $SCRATCH/clean && cd $SCRATCH/clean && uv sync --all-packages --locked` exits 0, then `uv run pytest -q` exits 0. CI also runs this in a dedicated job (Task 6) | NOT_RUN |
| X5 | `sqlite_version` recorded and ≥ floor | CI step prints `sqlite3.sqlite_version` and writes it to a job summary and uploaded artifact `sqlite-version.txt`; `tests/test_sqlite_floor.py` asserts the floor predicate (Task 5); the value is also written into `docs/reference/conformance.md` by the closing step. Floor: ≥ 3.51.3, or 3.50.x ≥ 3.50.7, or 3.44.x ≥ 3.44.6 (spec line 156) | NOT_RUN |
| X6 | a downstream handoff to dNh (branch resolution by both uv source forms; CI installing the pinned wheel) is issued and recorded in the P0 exit record; completing and merging it are dNh decisions, not ChatX exit criteria | Task 7 Step 6: `docs/p0-exit-record.md` contains a "Downstream handoff" entry with date, recipient and the inputs listed in Downstream handoff to dNh (release URL, wheel filename and sha256, both source forms). Whether dNh completes H1/H2 is not checked here and carries no State in this packet | NOT_RUN |

### Scope items (§6 P0 Scope cell, not exit criteria; each still needs evidence)

| ID | Criterion (verbatim from Scope cell) | How it will be checked | State |
|---|---|---|---|
| S1 | `~/code/chatstack` repo | `git -C /Users/hue/code/chatstack rev-parse --show-toplevel`; `git log` shows no history from `Dopemux-ChatRipperXXX` (owner item 1) | NOT_RUN |
| S2 | uv workspace | Root `pyproject.toml` contains `[tool.uv.workspace] members = ["packages/*", "apps/*"]`; `uv sync --all-packages --locked` exits 0 | NOT_RUN |
| S3 | two empty packages | `packages/chat-extraction-core/src/chat_extraction_core/__init__.py` and `apps/chatx/src/chatx/__init__.py` exist; no module beyond those listed in Tasks 3–4 | NOT_RUN |
| S4 | CI ... testing the **installed wheel** in a fresh venv outside the checkout | CI job logs show wheels built to a temp dir, a new venv under `$RUNNER_TEMP`, pytest run with cwd outside the checkout, and `test_installed_not_checkout` passing (asserts `__file__` is under site-packages) | NOT_RUN |
| S5 | `.github/workflows/*` rewritten, `arch-gates.yml` not carried | `test ! -e .github/workflows/arch-gates.yml && test ! -e config/arch-gates.yml`; `git log --diff-filter=A --name-only -- .github/workflows` shows every file authored in the new repo (no `Ported from` header on workflows) | NOT_RUN |
| S6 | pre-commit | `.pre-commit-config.yaml` exists; `uvx pre-commit run --all-files` exits 0 | NOT_RUN |
| S7 | ADR template | `docs/adr/0000-template.md` exists (path proposed, B6) | NOT_RUN |
| S8 | `conformance.md` skeleton | `docs/reference/conformance.md` (path from spec line 164) lists the seven components with version tested, date, evidence; unobserved = `UNKNOWN` | NOT_RUN |
| S9 | an interpreter linking SQLite at or above the floor | Same evidence as X5, from the interpreter that CI and the local `.python-version` select | NOT_RUN |
| S10 | this document copied in | `sha256sum` of the copy equals `sha256sum` of the source at copy time; copy path proposed in B7 | NOT_RUN |

### Global gates that apply at P0 (§7, spec lines 885–922)

| ID | Criterion (verbatim) | How it will be checked | State |
|---|---|---|---|
| G1 | `ruff check` and `ruff format --check` | `uv run ruff check .` and `uv run ruff format --check .` exit 0 locally and in CI | NOT_RUN |
| G2 | `mypy --strict` for the core and a strict configuration for the app | `uv run mypy --strict packages/chat-extraction-core/src` and `uv run mypy apps/chatx/src` (strict set in `apps/chatx/pyproject.toml`) exit 0 | NOT_RUN |
| G3 | `pytest --cov-fail-under=90` over both whole packages with no omit list, plus branch coverage | `pytest --cov=chat_extraction_core --cov=chatx --cov-branch --cov-fail-under=90` exits 0 against the installed wheels; coverage config has no `omit` other than `tests/` | NOT_RUN |
| G4 | `uv lock --check` | `uv lock --check` exits 0 locally and in CI | NOT_RUN |
| G5 | `pip-audit` | `pip-audit` over the locked dependency set exits 0 in CI (exact invocation proposed, B8) | NOT_RUN |
| G6 | dependency and model hashes pinned | `uv.lock` records sha256 for every wheel/sdist (`grep -c 'hash = "sha256:' uv.lock` greater than 0 and every `[[package]]` with a source registry has hashes). Model hashes: no model artifacts at P0, not applicable | NOT_RUN |

Not applicable at P0 (no code or data for them to test): mutation kill rate on shield and gate, fixtures, property tests, security tests other than the failure-path stubs, `pytest -m perf`, the CI-vs-local shield evaluation. Contract 9 (no-socket core, spec line 855) is not a P0 exit criterion; the import-graph and socket-guard tests are deferred to P1 unless the owner pulls them forward (B13).

## Downstream handoff to dNh (not a ChatX exit criterion)

Owner decision 5 (audit brief `PROMPT-master.md`, 2026-10-22): the dNh-side checks need separate dNh authority and are not ChatX exit criteria. ChatX's obligation is to issue the handoff and record it (X6, Task 7 Step 6). Running H1 and H2, completing the dNh branch and merging it are dNh decisions. H1 and H2 carry no State column here and are never counted as NOT_RUN gates in the P0 completion.

- Location: `/Users/hue/code/dNh_CRM`. Governed by dNh's own `AGENTS.md` and task packets (spec line 151). **Requires separate authority; this packet does not authorize any edit, branch creation, commit or push there.**
- Branch name: UNKNOWN — builder default (proposed): `dev/chatstack-core-resolve`. Naming only; creating it waits for dNh authority.
- Inputs the handoff must give dNh (all recorded in `docs/p0-exit-record.md`):
  1. The release URL: `https://github.com/DDD-Enterprises/chatstack/releases/tag/core-v0.0.1a0` (the URL form is proposed; the recorded value is whatever `release.yml` produced).
  2. The wheel filename (expected `chat_extraction_core-0.0.1a0-py3-none-any.whl`, UNKNOWN until built; take it from the release asset list) and its sha256 from `SHA256SUMS`.
  3. Both uv source forms: `{ path = "../chatstack/packages/chat-extraction-core" }` (add `editable = true` for development) and `{ workspace = "../chatstack" }` (spec lines 146–147).
  4. The chatstack commit SHA the tag points to, and the uv version used by the build.
- **OPEN OWNER DECISION: B14 repository visibility — if `DDD-Enterprises/chatstack` is private, dNh CI needs a read route (fine-grained token, or vendored wheel); choose before the handoff is issued.**

Checks for whoever holds dNh authority (verbatim from former X3 and X4, rev 2.1; only the cross-reference "see section below" now reads "see this section"):

| ID | Check | How it would be checked |
|---|---|---|
| H1 | a dNh dev branch resolves the core by both the `path` and `workspace` forms | CROSS-REPO, needs separate authority (see this section). Check: from clean clones of dNh and chatstack, `uv lock` and `uv sync` succeed with `{ path = "../chatstack/packages/chat-extraction-core", editable = true }`, then with `{ workspace = "../chatstack" }`; `uv pip show chat-extraction-core` resolves in both |
| H2 | that branch's CI installs a pinned wheel and passes (merging it is dNh's decision, not a ChatX exit criterion) | CROSS-REPO, needs separate authority. Check: the dNh branch's CI run is green and its log shows the core installed from a wheel pinned by version and sha256 (`--require-hashes` or equivalent in the lock). Source of the wheel: the `core-v0.0.1a0` pre-release assets — version and sha256 from `SHA256SUMS` (B9, decided 2026-10-22) |

Procedure behind H1 and H2 (run after chatstack Tasks 1–7 are green):

  1. Clean clones of both repos side by side (`~/code/dNh_CRM` and `~/code/chatstack`, so the relative paths in spec lines 146–147 hold).
  2. Path form: dependency `{ path = "../chatstack/packages/chat-extraction-core", editable = true }`. Run `uv lock` then `uv sync`; import `chat_extraction_core` succeeds.
  3. Workspace form: `{ workspace = "../chatstack" }` exactly as the spec writes it (line 147). The spec cites evidence E8, and the audit's `out/external-fact-check.md` row E8 confirms it against docs.astral.sh: `workspace` may be "a path string to resolve a dependency from a different workspace"; the path points at the external workspace root and uv resolves the member named `chat-extraction-core`. Run `uv lock` then `uv sync` with the uv version pinned for the build; import succeeds. If that uv version rejects the form, stop (Stop S6). Verified locally on 2026-10-22 (audit check ARG-C01, closes argon decision challenge 2; receipt `docs/superpowers/audits/2026-10-22-p0-packet-audit/out/arg-c01-uv-workspace-syntax.txt`): with uv 0.12.11 and `uv lock --offline`, a consumer that is not a workspace member resolves all three forms — `{ workspace = "../ws" }` locks as `source = { editable = … }`, bare `{ path = … }` as `{ directory = … }`, `{ path = …, editable = true }` as editable. The forms are therefore not interchangeable: keep `editable = true` on the path form (step 2) so H1 compares like with like, and expect the workspace form to install the core editable from source, not as a wheel — H2's pinned-wheel install is a third, separate configuration.
  4. The branch's CI installs the core from a wheel pinned by version and sha256 and passes (H2).
- Prerequisite from chatstack: a built wheel with a known sha256. Source: the `core-v0.0.1a0` pre-release assets (B9, decided; Task 7 Step 5), whose bytes are the ones `release.yml` tested before publishing.

## File structure (created by this packet)

```
/Users/hue/code/chatstack/
  pyproject.toml                  workspace root (virtual root, proposed B2); dev dependency group; ruff/mypy/pytest config
  uv.lock
  .python-version                 interpreter pin (value UNKNOWN, B1)
  .gitignore  .pre-commit-config.yaml  LICENSE (MIT, repo-level)  README.md
  .github/workflows/ci.yml  release.yml        written fresh
  .github/actions/wheel-tests/action.yml       installed-wheel test steps, defined once (Task 6)
  packages/chat-extraction-core/
    pyproject.toml  LICENSE  THIRD_PARTY_NOTICES.md
    src/chat_extraction_core/{__init__.py, py.typed, errors.py, resources.py, sqlite_floor.py}
    tests/{test_installed_not_checkout.py, test_sqlite_floor.py, test_failure_paths.py}
  apps/chatx/
    pyproject.toml  LICENSE  THIRD_PARTY_NOTICES.md
    src/chatx/{__init__.py, py.typed, errors.py}
    tests/{test_installed_not_checkout.py, test_failure_paths.py}
  docs/
    design/2026-10-20-chatx-rearchitecture-design.md   copy of the spec (path proposed, B7)
    adr/0000-template.md
    reference/conformance.md
    p0-exit-record.md             CI URL, sqlite_version, doc sha256 (proposed, B12)
```

Tension to resolve before Task 3 (see Gaps G-A): §6 says "two empty packages" yet also requires failure-path "stubs" in P0 CI. Stubs need some code to assert against. This packet's proposal is the smallest module that makes them real tests (Tasks 3 and 4), not skips (a skip for `E_SCHEMA_MISSING` would contradict spec line 162, "never a skip").

## Tasks

### Task 1: Repo, workspace root, interpreter, licence

**Files:**
- Create: `/Users/hue/code/chatstack/{pyproject.toml,.python-version,.gitignore,LICENSE,README.md}`

**Interfaces:**
- Produces: a workspace root every later task builds under; `[tool.uv.workspace] members = ["packages/*", "apps/*"]`; a pinned interpreter whose linked SQLite is at or above the floor.

- [ ] **Step 1: Preflight, no mutation.** Run `test ! -e /Users/hue/code/chatstack && echo absent` (it was absent when this packet was drafted). Run `uv --version` (spec records 0.12.11). Run `uv python list --only-installed` and, for each candidate interpreter, `<python> -c "import sqlite3;print(sqlite3.sqlite_version)"`. Record each pair. Expected: at least one interpreter satisfies the floor predicate (spec line 158 reports mise 3.12.13 linking 3.53.1). If none does, Stop S3.
- [ ] **Step 2: `git init -b main /Users/hue/code/chatstack`.** No remote yet. `git -C ... log` must be empty (S1).
- [ ] **Step 3: Write root `pyproject.toml`** with `[tool.uv.workspace] members = ["packages/*", "apps/*"]`, `requires-python = ">=3.12"`, a `dev` dependency group (`ruff`, `mypy`, `pytest`, `pytest-cov`, `pre-commit`, `pip-audit`), and shared `[tool.ruff]`, `[tool.pytest.ini_options]`, `[tool.coverage.run]` (`branch = true`, `source = ["chat_extraction_core", "chatx"]`, no `omit` other than `tests/`) and `[tool.coverage.report]` (`fail_under = 90`). Versions of the dev tools: UNKNOWN, take whatever `uv add` resolves and let `uv.lock` record them.
- [ ] **Step 4: Write `.python-version`** with the interpreter chosen in Step 1 (value UNKNOWN until Step 1 runs; B1). Write `.gitignore` (venvs, caches, `dist/`, `.coverage`). Write MIT `LICENSE` with holder DDD-Enterprises (spec line 150) and a short `README.md` pointing at `docs/design/`.
- [ ] **Step 5: Commit** `chore: initialise chatstack workspace root` (satisfies S1, S2 in part, S9 in part).

### Task 2: Design document, ADR template, conformance skeleton

**Files:**
- Create: `docs/design/2026-10-20-chatx-rearchitecture-design.md`, `docs/adr/0000-template.md`, `docs/reference/conformance.md`

**Interfaces:**
- Produces: `conformance.md` table with columns `Component | Version tested | Date | Evidence`, rows for exactly the seven components in spec line 164: SQLite, sqlite-vec, Presidio, the NER models, the local model server, the Anthropic API and model ids, uv. Every cell starts `UNKNOWN` (Task 5 and Task 7 fill SQLite and uv).

- [ ] **Step 1: Copy the spec byte-for-byte**: `cp /Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md /Users/hue/code/chatstack/docs/design/`. Run `shasum -a 256` on source and copy; expected: identical (S10). Record the hash in `docs/p0-exit-record.md`. Do not edit the copy.
- [ ] **Step 2: Write `docs/adr/0000-template.md`** with sections Title, Status, Context, Decision, Consequences, Alternatives rejected, Evidence. (Section list proposed, B6; the spec names no template shape.)
- [ ] **Step 3: Write `docs/reference/conformance.md`** with the table above and one sentence stating the rule from spec line 164: P0 CI writes what it observes; anything not observed stays UNKNOWN.
- [ ] **Step 4: Commit** `docs: add design rev 2.2 copy, ADR template, conformance skeleton` (S7, S8, S10).

### Task 3: Package `chat-extraction-core` with schema-missing stub

**Files:**
- Create: `packages/chat-extraction-core/{pyproject.toml,LICENSE,THIRD_PARTY_NOTICES.md}`, `src/chat_extraction_core/{__init__.py,py.typed,errors.py,resources.py}`, `tests/{test_installed_not_checkout.py,test_sqlite_floor.py,test_failure_paths.py}`
- Test: the three test files above

**Interfaces:**
- Produces (proposed signatures, B4/B5):
  - `chat_extraction_core.__version__: str = "0.0.1a0"` (decided, B4/G-E). It must equal `[project] version` in `packages/chat-extraction-core/pyproject.toml` (also `"0.0.1a0"`); `0.0.1a0` is the single authoritative core version.
  - `chat_extraction_core.errors.SchemaMissingError(Exception)` with class attribute `code = "E_SCHEMA_MISSING"` and `exit_code = 1`.
  - `chat_extraction_core.resources.read_schema(name: str) -> str` reading from the package through `importlib.resources.files("chat_extraction_core") / "schema" / name`; raises `SchemaMissingError` when absent.
  - `chat_extraction_core.sqlite_floor.meets_floor(version: str) -> bool` implementing: `>= 3.51.3`, or `3.50.x >= 3.50.7`, or `3.44.x >= 3.44.6`. Place it in `chat_extraction_core/sqlite_floor.py` (add that file to the list). Whether it belongs in the core or the app is UNKNOWN (B5); the spec says the app "refuses to open a case" (line 157), so a P1 relocation is possible.
- `pyproject.toml`: name `chat-extraction-core`, `[project] version = "0.0.1a0"` (a static string, not derived from the tag), import package `chat_extraction_core` (spec lines 123, 774), hatchling build, `requires-python = ">=3.12"`, `license = "MIT"`, dependencies exactly `pydantic>=2,<3` and `phonenumbers>=8,<9` (line 160). Whether to declare them at P0 while no code imports them is UNKNOWN (B10); proposed: declare them, since `uv.lock` and `pip-audit` should exercise the real set.

- [ ] **Step 1: Write failing tests** in `tests/test_failure_paths.py`:
  - `test_read_schema_missing_raises_e_schema_missing`: `with pytest.raises(SchemaMissingError) as e: read_schema("does-not-exist.json")`; `assert e.value.code == "E_SCHEMA_MISSING"`; `assert e.value.exit_code == 1`.
  - `test_schema_missing_is_never_a_skip`: asserts the test above is not decorated with a skip marker (guards spec line 162): inspect `pytest.mark` on the function via `getattr(fn, "pytestmark", [])` and assert none named `skip`/`skipif`.
  In `tests/test_sqlite_floor.py`: parametrised `test_meets_floor` with `3.51.3 -> True`, `3.51.2 -> False`, `3.50.7 -> True`, `3.50.6 -> False`, `3.44.6 -> True`, `3.44.5 -> False`, `3.47.1 -> False` (the measured old-venv value, spec line 158), `3.53.1 -> True`; and `test_running_interpreter_meets_floor` asserting `meets_floor(sqlite3.sqlite_version)`.
  In `tests/test_installed_not_checkout.py`: `test_installed_not_checkout` asserting `"site-packages" in chat_extraction_core.__file__`, so a run against the source tree fails. Also in that file, `test_core_version_is_0_0_1a0` (marker `installed`): `importlib.metadata.version("chat-extraction-core") == chat_extraction_core.__version__ == "0.0.1a0"`. It runs in the shared installed-wheel steps (Task 6), so `ci.yml` and `release.yml` both assert it against the built wheel's metadata.
- [ ] **Step 2: Run** `uv run --package chat-extraction-core pytest packages/chat-extraction-core/tests -q`. Expected: FAIL (ImportError / names undefined). `test_installed_not_checkout` is expected to FAIL under an editable sync; it is only meaningful in the wheel job (Task 6), so mark it with a custom marker `installed` (proposed, B11) and select it only in the wheel job.
- [ ] **Step 3: Implement** the interface above. `meets_floor` parses `major.minor.patch` and returns the boolean; one line on approach: tuple comparison per branch.
- [ ] **Step 4: Run** the same command. Expected: PASS apart from `installed`-marked tests.
- [ ] **Step 5: Commit** `feat(core): empty package with schema-missing and sqlite-floor stubs` (X1 in part, X5 in part, S3, G1–G3 in part).

### Task 4: Package `chatx` with egress-refusal stubs

**Files:**
- Create: `apps/chatx/{pyproject.toml,LICENSE,THIRD_PARTY_NOTICES.md}`, `src/chatx/{__init__.py,py.typed,errors.py}`, `tests/{test_installed_not_checkout.py,test_failure_paths.py}`

**Interfaces:**
- Consumes: `chat_extraction_core` as a workspace dependency (`[tool.uv.sources] chat-extraction-core = { workspace = true }`). This is the in-workspace form uv documents; it is distinct from the dNh `{ workspace = "../chatstack" }` form (Gap G-D).
- Produces (proposed, B4):
  - Distribution name `chatx` (UNKNOWN in spec — builder default `chatx`; spec names only the import package `chatx`, line 785 area and §4 header).
  - `chatx.errors.GateMismatchError(Exception)` with `code = "E_GATE_MISMATCH"`, `exit_code = 3`.
  - `chatx.errors.exit_code_for(code: str) -> int`, implementing only the mapping the spec states: `E_GATE_MISMATCH`, `E_VENDOR_TERMS`, `E_VISIBILITY_LEAK`, `E_PROVIDER_NOT_LOCAL`, `E_SHIELD_NOT_QUALIFIED` map to 3; `E_SQLITE_TOO_OLD`, `E_TZ_REQUIRED`, `E_CASE_LOCKED`, `E_SCHEMA_MISSING`, `E_DB_LOCKED`, `E_DB_ACCESS_DENIED` map to 1 (spec lines 661, 663, 685–687); any other code raises `KeyError`. This stays a stub: no registry, no `errors.md` generation (P2).

- [ ] **Step 1: Write failing tests** in `apps/chatx/tests/test_failure_paths.py`:
  - `test_exit_3_for_egress_refusal`: parametrised over the five exit-3 codes; `assert exit_code_for(code) == 3`.
  - `test_gate_mismatch_error_carries_code_and_exit_3`: `GateMismatchError().code == "E_GATE_MISMATCH"` and `.exit_code == 3`.
  - `test_schema_missing_maps_to_exit_1`: `exit_code_for("E_SCHEMA_MISSING") == 1` (documents that it is not exit 3, spec line 661).
  - `test_unknown_code_raises`: `pytest.raises(KeyError)` for `"E_NOT_A_CODE"`.
  Plus `test_installed_not_checkout` for `chatx` (marker `installed`).
- [ ] **Step 2: Run** `uv run --package chatx pytest apps/chatx/tests -q`. Expected: FAIL (ImportError).
- [ ] **Step 3: Implement** `chatx/errors.py` per the interface. App dependency bounds `>=x,<next-major` (line 162); at P0 the only dependency is the workspace core, so no third-party bound is needed (stated, not invented).
- [ ] **Step 4: Run** the same command. Expected: PASS apart from `installed`-marked tests.
- [ ] **Step 5: Commit** `feat(chatx): empty app package with egress-refusal exit-code stubs` (X1 in part, S3, G1–G3 in part).

### Task 5: Local gates, lock, pre-commit, sqlite_version recording

**Files:**
- Create: `.pre-commit-config.yaml`, `uv.lock`, `scripts/record_sqlite_version.py`
- Modify: `docs/reference/conformance.md` (SQLite and uv rows), `docs/p0-exit-record.md`

**Interfaces:**
- Produces: `scripts/record_sqlite_version.py`, a stdlib-only script printing one JSON line `{"python": <sys.version>, "sqlite_version": <sqlite3.sqlite_version>, "meets_floor": <bool>}` and exiting 1 when below the floor (reusing the floor predicate by import from `chat_extraction_core.sqlite_floor`). Proposed name and path (B5).

- [ ] **Step 1: Run locally** `uv lock`, then `uv lock --check` (expected exit 0, G4), `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy --strict packages/chat-extraction-core/src`, `uv run mypy apps/chatx/src`, `uv run pytest -m "not installed" --cov --cov-branch --cov-fail-under=90`. Record each exit code. Fix findings in the owning file only.
- [ ] **Step 2: Write `.pre-commit-config.yaml`** with hooks: ruff (check), ruff-format, and a local hook running `uv lock --check`. Hook repos and revs: UNKNOWN, resolve at build time with `uvx pre-commit autoupdate` and commit the pinned revs (B8). Run `uvx pre-commit run --all-files` (S6).
- [ ] **Step 3: Run `python scripts/record_sqlite_version.py`** with the interpreter from `.python-version`. Expected: `meets_floor` true. Write the observed value, today's date and the command as evidence into the SQLite row of `conformance.md`; write `uv --version` into the uv row (X5, S9 local part).
- [ ] **Step 4: Commit** `build: lock, pre-commit, sqlite_version recorder` .

### Task 6: CI workflow written fresh

**Files:**
- Create: `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/actions/wheel-tests/action.yml` (a composite action, the single definition of the installed-wheel test steps)

**Interfaces:**
- Permissions (least privilege): both workflows declare top-level `permissions: contents: read`. Only the `release` job in `release.yml` declares `permissions: contents: write`. Every step that runs `gh` sets `env: GH_TOKEN: ${{ github.token }}` explicitly. No other scopes. Open point returned to the supervisor: listing workflow runs for the release gate (job 5, step a) may also need `actions: read` on a private repository (unverified); that would be a second scope, so it is not added until the supervisor decides.
- Produces the jobs below. No file named `arch-gates.yml` anywhere; no workflow copied from `Dopemux-ChatRipperXXX` (S5). Action versions and runner labels: UNKNOWN, pin at build time to exact tags and record them in the commit message (B3). macOS arm64 is required, Linux x86_64 is nice to have (spec line 1084).

Jobs (matrix `os`: macOS arm64 required; Linux x86_64 optional, marked `continue-on-error: true` so a Linux failure never blocks the required result, B3):
1. `static`: `uv sync --all-packages --locked`; `ruff check`; `ruff format --check`; `mypy --strict` core; `mypy` app; `uv lock --check` (G1, G2, G4).
2. `audit`: `pip-audit` over the locked set (G5).
3. `wheel-tests` (the installed-wheel job, S4, X1, X5, G3): in order
   - `uv build --package chat-extraction-core --wheel --out-dir "$RUNNER_TEMP/dist"` and the same for `chatx`;
   - `sha256sum "$RUNNER_TEMP"/dist/*.whl` printed and uploaded as artifact (the digest feeds B9);
   - `uses: ./.github/actions/wheel-tests` with the wheel directory `"$RUNNER_TEMP/dist"` as input. The composite action holds the installed-wheel steps below and is also called by `release.yml` (job 5), so the two workflows cannot drift. Its steps, in order:
     1. `uv export --frozen --all-packages --no-emit-workspace --no-hashes -o "$RUNNER_TEMP/constraints.txt"` (flags verified against `uv export --help`, uv 0.12.11). The file pins every third-party package in `uv.lock` to an exact version, dev group included; assert it pins `pytest` and `pytest-cov` (`grep -E '^(pytest|pytest-cov)==' "$RUNNER_TEMP/constraints.txt"`, two matches) and fail otherwise. Whether `uv export` includes the `dev` group by default is unverified; the grep is the guard;
     2. `uv venv "$RUNNER_TEMP/venv"` (fresh, outside the checkout) and `uv pip install --python "$RUNNER_TEMP/venv" "$WHEEL_DIR"/*.whl pytest pytest-cov -c "$RUNNER_TEMP/constraints.txt"`. No `--no-deps`: the wheels' runtime dependencies (`pydantic`, `phonenumbers`) install, resolved under the constraints, so nothing floats. The constraints carry versions, not hashes (`--no-hashes`), so this install is version-pinned but not hash-verified; `uv.lock` still holds the hashes (G6);
     3. `mkdir "$RUNNER_TEMP/run" && cd "$RUNNER_TEMP/run"`, then run `"$RUNNER_TEMP/venv/bin/python" -m pytest -c "$GITHUB_WORKSPACE/pyproject.toml" "$GITHUB_WORKSPACE/packages/chat-extraction-core/tests" "$GITHUB_WORKSPACE/apps/chatx/tests" --cov=chat_extraction_core --cov=chatx --cov-branch --cov-fail-under=90 -p no:cacheprovider`, including the `installed`-marked tests. `-c` makes the root `pytest.ini_options` (the `installed` marker) apply although the cwd is outside the checkout. The cwd is outside the checkout and the checkout's `src/` is not on `sys.path`, which `test_installed_not_checkout` proves; `test_core_version_is_0_0_1a0` asserts the wheel's metadata version equals `__version__` equals `0.0.1a0`. Whether the coverage settings in the root `pyproject.toml` are read from this cwd is unverified; all flags that decide the gate (`--cov-branch`, `--cov-fail-under=90`) are passed on the command line;
     4. `"$RUNNER_TEMP/venv/bin/python" "$GITHUB_WORKSPACE/scripts/record_sqlite_version.py" | tee "$GITHUB_STEP_SUMMARY" "$RUNNER_TEMP/sqlite-version.txt"`.
   - back in `ci.yml`: upload `$RUNNER_TEMP/sqlite-version.txt` as artifact `sqlite-version.txt` (X5).
4. `clean-clone`: `git clone "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY" "$RUNNER_TEMP/clean"` at the same SHA, `uv sync --all-packages --locked`, `uv run pytest -m "not installed"` (X2).
5. `release` (in `release.yml`; G-E option b, decided; tested bytes = published bytes): runs only on pushes of tags matching `core-v*`; top-level `permissions: contents: read`, and this job alone `permissions: contents: write`. Steps, in this order, each failing the job on error:
   - (a) Gate on CI for the tagged commit: with `GH_TOKEN: ${{ github.token }}`, `gh run list -R "$GITHUB_REPOSITORY" --commit "$GITHUB_SHA" --workflow ci.yml --status success --json databaseId --jq 'length'` must print a number greater than 0; otherwise fail before building (flags verified against `gh run list --help`, gh 2.96.0; the `actions: read` question is under Permissions above);
   - (b) Build from the tagged tree: `uv build --package chat-extraction-core --wheel --out-dir "$RUNNER_TEMP/dist"`, and the same for `chatx` into the same directory (the app wheel is built only so the shared steps can run both test suites; it is never published). Record `sha256sum` of the core wheel before testing;
   - (c) Test those exact files: `uses: ./.github/actions/wheel-tests` with the wheel directory `"$RUNNER_TEMP/dist"`, the same composite action as `ci.yml` job 3, in a fresh venv outside the checkout. Then assert the release tag equals `"core-v" + version`, where version is read from the tested venv (`"$RUNNER_TEMP/venv/bin/python" -c 'import importlib.metadata as m; print(m.version("chat-extraction-core"))'`), and that the core wheel's sha256 is unchanged since (b);
   - (d) Only then: `(cd "$RUNNER_TEMP/dist" && sha256sum chat_extraction_core-*.whl > SHA256SUMS)`; build the notes file `"$RUNNER_TEMP/release/$GITHUB_REF_NAME.md"` as the committed `docs/release-notes/$GITHUB_REF_NAME.md` plus the wheel's sha256 and the release URL (`$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/releases/tag/$GITHUB_REF_NAME`); with `GH_TOKEN: ${{ github.token }}`, `gh release create "$GITHUB_REF_NAME" --prerelease --title "$GITHUB_REF_NAME" --notes-file "$RUNNER_TEMP/release/$GITHUB_REF_NAME.md" "$RUNNER_TEMP"/dist/chat_extraction_core-*.whl "$RUNNER_TEMP/dist/SHA256SUMS" "$RUNNER_TEMP/release/$GITHUB_REF_NAME.md"` (flags verified against `gh release create --help`). Uploaded: the core wheel, `SHA256SUMS` and the notes file, nothing else;
   - (e) Print the wheel sha256 and the release URL to the job summary. Task 7 Step 5 copies both into `docs/p0-exit-record.md`.
   The committed notes file cannot contain the digest, because it is written before the tag; the workflow appends it. No PyPI or other index at P0.
Triggers: `ci.yml` on `push` and `pull_request` (not specified by spec; proposed, B3); `release.yml` on tag pushes `core-v*` (decided, G-E).
Failure-path tests run in job 3 by name; the job also runs `pytest --collect-only -q -k "failure_paths"` and fails if fewer than the expected count is collected (guards against silent deselection). Expected count: UNKNOWN until the first local run (parametrised cases count individually); record it then (B11).

- [ ] **Step 1: Write `ci.yml`, `release.yml` and the composite action** per the jobs above with a tiny local lint (`uvx actionlint` if available, otherwise `NOT_RUN`).
- [ ] **Step 2: Commit** `ci: add fresh workflow testing installed wheels`.

### Task 7: Remote, first green run, recorded evidence

**Files:**
- Modify: `docs/p0-exit-record.md`, `docs/reference/conformance.md`

**Interfaces:**
- Consumes: owner authority to create the remote (Stop S1). Remote name, owner and visibility are UNKNOWN; proposed `DDD-Enterprises/chatstack`, private (B14). Spec says only "new repo" (line 130) and that DDD-Enterprises owns the core (line 150).

- [ ] **Step 1: With owner approval only**, run `gh repo create DDD-Enterprises/chatstack --private --source /Users/hue/code/chatstack --remote origin` (name and visibility proposed). Push `main`: `git -C /Users/hue/code/chatstack push -u origin main`. Do not enable branch protection or merge anything.
- [ ] **Step 2: Watch CI** in the background: `gh run watch -R DDD-Enterprises/chatstack` (exit status 8 on `gh pr checks` while pending is not a failure). Expected: all required jobs `success`.
- [ ] **Step 3: Record**: run URL, head SHA, the three failure-path test names as seen in the log, `sqlite_version` from the macOS arm64 job, the design copy sha256, and the wheel sha256 digests into `docs/p0-exit-record.md`; copy the CI-observed SQLite and uv versions into `conformance.md`. Commit and push; the CI run for that final commit must also be green and its URL is the one recorded for X1 (record the SHA so the record does not chase its own tail: the recorded URL is for the commit before the record commit, which touches docs only; note this in the file).
- [ ] **Step 4: Verify X2 from outside CI**: `git clone` to `$SCRATCH/clean`, `uv sync --all-packages --locked`, `uv run pytest -q -m "not installed"`.
- [ ] **Step 5: Pre-release tag (owner authority, Stop S1; G-E option b)**: commit `docs/release-notes/core-v0.0.1a0.md` (states: P0 pre-release, no adapter tests to run so the line-143 pre-tag step is NOT_RUN, wheel built by `release.yml` from the tagged tree and installed-wheel-tested before publication; the workflow appends the wheel sha256 and release URL). On that commit, once its CI is green: `git -C /Users/hue/code/chatstack tag -a core-v0.0.1a0 -m "core 0.0.1a0 pre-release (P0)"` then `git -C /Users/hue/code/chatstack push origin core-v0.0.1a0`. Wait for the `release` workflow; it must have passed steps (a)–(e) of Task 6 job 5 (CI green for the tagged commit, tagged-tree build, installed-wheel tests on that exact wheel, tag equals `core-v` + version, then publication). Record the release URL and the `SHA256SUMS` digest of the published wheel in `docs/p0-exit-record.md`. The published bytes are the bytes the release workflow tested. The `wheel-tests` digest from the CI run for the same SHA may differ; record it for information only, since byte-reproducible builds across runs are not a P0 gate. dNh pins the release asset's digest.
- [ ] **Step 6: Issue the downstream handoff to dNh** (X6) to whoever holds dNh authority, using Downstream handoff to dNh: the release URL, wheel filename and sha256, both uv source forms, the tagged commit SHA and the uv version. Resolve the open owner decision B14 (repository visibility and the dNh read route) first; if it is unresolved, stop (S8) rather than issue a handoff dNh cannot use. Record the handoff in `docs/p0-exit-record.md`: date, recipient and the inputs given. Do not wait for dNh, do not record H1 or H2 as `NOT_RUN` exit gates.

**Completion contract.** P0 is complete for ChatX when X1, X2, X5 and X6 are PASS, every S-row and G-row is PASS, and `docs/p0-exit-record.md` holds the CI URL, `sqlite_version`, the design copy sha256, the release URL and published wheel sha256, and the recorded handoff. H1 and H2 are dNh-side checks (owner decision 5); they are outside this calculation and their outcome never changes the P0 state. NOT_RUN stays NOT_RUN for any row that was not executed.

## Builder decisions (spec §11 items P0 touches; values are `proposed` unless marked **decided** — B4 core version and B9 were decided by the owner on 2026-10-22)

Spec §11 (lines 1078–1090) items P0 touches: "CI and logging: the CI matrix (macOS arm64 required, Linux x86_64 nice to have)". Naming and storage details and fixtures are P1+. Everything else below is not a §11 item but is stated UNKNOWN by the spec and needs a default.

| # | Item | Spec status | Proposed (not decided) |
|---|---|---|---|
| B1 | Interpreter and `.python-version` | spec: `>=3.12`, floor on linked SQLite; mise 3.12.13 links 3.53.1 (line 158) | proposed: mise-managed 3.12.13 if Task 1 Step 1 confirms 3.53.1 locally |
| B2 | Root `pyproject.toml` shape | not stated | proposed: virtual root (no `[project]`), dev tools in a dependency group |
| B3 | CI matrix, runners, triggers | §11: macOS arm64 required, Linux x86_64 nice to have | proposed: macOS arm64 required job; Linux x86_64 `continue-on-error: true`; runner labels and action tags UNKNOWN, pin at build time; triggers `push` and `pull_request` |
| B4 | Distribution name of the app and package versions | core `chat-extraction-core` stated; app distribution name not stated | proposed: `chatx`; core version **decided (owner, 2026-10-22, G-E)**: `0.0.1a0`, set as `[project] version` and `__version__` and asserted equal in the installed-wheel tests, with the release tag required to equal `core-v` + version (Task 6 job 5), so the P0 pre-release tag `core-v0.0.1a0` (B9) matches the wheel's version; the app starts at its own `0.0.0` (proposed) |
| B5 | Where the floor predicate and recorder live | not stated (line 157 says the app refuses to open a case) | proposed: `chat_extraction_core/sqlite_floor.py` plus `scripts/record_sqlite_version.py`; may move in P1/P2 |
| B6 | ADR template path and sections | not stated | proposed: `docs/adr/0000-template.md`, sections Title/Status/Context/Decision/Consequences/Alternatives rejected/Evidence |
| B7 | Path of the design copy | "this document copied in" only | proposed: `docs/design/2026-10-20-chatx-rearchitecture-design.md` |
| B8 | `pip-audit` invocation and pre-commit revs | tools named, flags not | proposed: audit the exported lock (`uv export --frozen --all-packages --no-emit-workspace` piped to `pip-audit --requirement - --no-deps --disable-pip`), verify flags against the installed version first; pre-commit revs from `autoupdate` |
| B9 | Source of the pinned wheel for dNh (H2, downstream handoff) | release contract says tags `core-vX.Y.Z` with wheel + sha256 built in CI (line 142); P0 cutting a tag is not stated | **decided (owner, 2026-10-22, G-E option b)**: after the first green run, tag `core-v0.0.1a0`; the `release` workflow, only if CI is green for the tagged commit, builds the core wheel from the clean tagged tree, runs the same installed-wheel tests as CI on that exact wheel, and only then publishes it with `SHA256SUMS` and the notes file as assets of a GitHub release marked pre-release (published bytes = tested bytes); dNh pins that version and sha256. The adapter-test step the contract requires before tagging (line 143) has nothing to run at P0 and is recorded as NOT_RUN in the release notes. Creating the tag needs owner authority (Stop S1) |
| B10 | Declare `pydantic`/`phonenumbers` at P0 | listed dependencies stated; whether empty package declares them not stated | proposed: declare them |
| B11 | Test markers and expected failure-path count | not stated | proposed: marker `installed`; count fixed from first local run |
| B12 | Where the CI URL is recorded | "its URL recorded", location not stated | proposed: `docs/p0-exit-record.md` |
| B13 | Pull forward import-graph and socket-guard tests | spec places them with the core's design (line 160) but P1 owns the code | proposed: defer to P1 |
| B14 | Remote owner, name, visibility | not stated beyond "new repo" and DDD-Enterprises ownership | proposed: `DDD-Enterprises/chatstack`, private |

## Review Focus

1. Tests run against `src/` instead of the wheel and pass falsely: pinned by `test_installed_not_checkout` in both packages and the cwd-outside-checkout step.
2. A `skipif` or `xfail` silently turns a failure-path stub green: pinned by `test_schema_missing_is_never_a_skip` and the collect-count guard in Task 6.
3. A SQLite version string on a boundary (3.51.2, 3.50.6, 3.44.5, or a 4-part version): pinned by the parametrised `test_meets_floor`; four-part strings are not covered by the spec (UNKNOWN; implementer must not guess, return it to the supervisor).
4. CI passes on macOS arm64 only because Linux is non-blocking: stated; the Linux result is recorded but excluded from X1.
5. `uv.lock` drifts after the last edit: `uv lock --check` runs in `static` and in the pre-commit hook.

## Gaps and contradictions found in the spec

- G-A (decided 2026-10-22, owner: option a): line 871 says "two empty packages" and also requires failure-path "stubs" in P0 CI. Stubs cannot pass without some code. The owner allows the minimal stubs in Tasks 3 and 4 — an `errors.py` and a resource loader in the core that raise `E_SCHEMA_MISSING`, and an app entry point that maps `E_GATE_MISMATCH` to exit 3 — and nothing beyond them in P0.
- G-B (inconsistency in scope of "exit 3"): the P0 row lists "exit 3, `E_GATE_MISMATCH`, `E_SCHEMA_MISSING` stubs" together, but `E_SCHEMA_MISSING` is exit 1 (line 661) and only `E_GATE_MISMATCH` is exit 3 (line 663). The tests here assert each code's own mapping. Decided 2026-10-22, owner: option a — §3.12 stands; the §6 P0 row was reworded to "`E_GATE_MISMATCH` → exit 3 and `E_SCHEMA_MISSING` → exit 1, per §3.12, as stubs" (spec rev 2.1, §14 entry).
- G-C: line 728 names `config/arch-gates.yml` as the file to rewrite, while line 871 and the brief name `arch-gates.yml` under workflows. Packet asserts neither path exists (S5).
- G-D (resolved by the audit, not a gap): the spec writes the dNh form as `{ workspace = "../chatstack" }` (line 147). uv documents this form: the `workspace` field "can also be set to a path string to resolve a dependency from a different workspace"; the path "must point to the external workspace root" and uv picks the member whose name matches the dependency (audit `out/external-fact-check.md`, E8, SUPPORTED, docs.astral.sh). The in-workspace boolean `workspace = true` is a different, same-workspace form. H1 (downstream handoff) still exercises both dNh forms against the real uv version pinned at build time (Stop S6 if the pinned uv rejects it).
- G-E (decided 2026-10-22, owner: option b): the dNh-side check H2 needs "a pinned wheel", and the release contract (line 142) ties wheels to `core-vX.Y.Z` tags. P0 therefore ends by cutting the pre-release tag `core-v0.0.1a0`; the wheel and `SHA256SUMS` built from that tagged tree, after the same installed-wheel tests as CI passed on that exact wheel, are the release assets dNh pins (B9, Task 6 job 5, Task 7 Step 5). The tag needs the same owner authority as the remote (Stop S1).
- G-F: the CI-URL recording location, repo remote name and visibility, runner labels, tool versions, hook revisions and the dNh branch name are not stated. All marked UNKNOWN/proposed above.

## Stop conditions (implementer stops and returns to the supervisor)

- S1: Any need to create the remote, push, tag, or make a repo public without recorded owner authority.
- S2: Any edit needed inside `/Users/hue/code/dNh_CRM`, `/Users/hue/code/Dopemux-ChatRipperXXX` (other than reading the spec for the copy), or the spec.
- S3: No locally available interpreter links SQLite at or above the floor, or CI's macOS arm64 interpreter reports below the floor.
- S4: CI cannot be made green without lowering coverage below 90, adding an `omit`, skipping a failure-path test, or weakening a gate.
- S5: A proposed default (B-list) would need a value the spec forbids or contradicts (for example a core dependency beyond `pydantic` and `phonenumbers`).
- S6 (for whoever runs H1 under dNh authority): the uv version pinned for the build rejects `{ workspace = "../chatstack" }` (documented per E8, but version behaviour is checked, not assumed), or the two dNh forms cannot both resolve from clean clones.
- S7: A third-party action, package or runner label cannot be pinned to an exact version at least two weeks old; do not use floating tags.
- S8: Any required value is UNKNOWN and no proposal above applies.
- S9: A command not listed in this packet would mutate state outside `/Users/hue/code/chatstack`.

## Rollback (undo P0 entirely)

P0 creates only a new directory and a new remote. Nothing in `Dopemux-ChatRipperXXX` or `dNh_CRM` is modified by this packet.
1. Delete the remote repository (`DDD-Enterprises/chatstack`, if created): `gh repo delete DDD-Enterprises/chatstack` (requires explicit owner confirmation; destructive). Delete any tags or releases it carries with it.
2. Delete the directory `/Users/hue/code/chatstack` in full (including `.git`, `uv.lock`, `.venv`, all docs). No other path is touched. The owner runs the deletion; agents do not delete.
3. Delete the scratch artifacts: `$SCRATCH/clean` clones and any `$RUNNER_TEMP`-equivalent local directories used for the wheel check.
4. If the dNh branch was created under separate authority, it is removed under dNh's governance, not this packet.
5. Re-check: `test ! -e /Users/hue/code/chatstack`; `gh repo view DDD-Enterprises/chatstack` returns not found.
