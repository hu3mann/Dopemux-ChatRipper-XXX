# ChatX Re-architecture, Phase P0 "Workspace" Implementation Packet

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not start until the supervisor records owner approval.

Status: DRAFT — not approved. Owner is reading design rev 2 (step S0); nothing here executes until the owner approves.
Date: 2026-10-21
Plan step: S2 of `docs/superpowers/plans/2026-10-21-next-steps.md` (draft by Sonnet, supervisor reviews).

**Goal:** Create the `~/code/chatstack` uv workspace with two empty packages and a CI that proves the installed wheel works, so P0.5 and P1 have somewhere to land.

**Architecture:** A new git repo (owner item 1) whose root is a uv workspace (`members = ["packages/*", "apps/*"]`). `packages/chat-extraction-core` (MIT) and `apps/chatx` hold only package metadata, a version, and the minimal code the failure-path stubs need. CI builds wheels, installs them in a fresh venv outside the checkout, and runs the tests there.

**Tech Stack:** Python `>=3.12`, uv (0.12.11 present locally), hatchling, ruff, `mypy --strict` (core) and a strict configuration (app), pytest + pytest-cov, pre-commit, `uv lock --check`, `pip-audit`, GitHub Actions.

**Spec:** `/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/specs/2026-10-20-chatx-rearchitecture-design.md` (rev 2, 1,261 lines).

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

> A green CI run, its URL recorded, that includes the failure-path tests (exit 3, `E_GATE_MISMATCH`, `E_SCHEMA_MISSING` stubs); `uv sync` works from a clean clone; a dNh dev branch resolves the core by both the `path` and `workspace` forms, and that branch's CI installs a pinned wheel and passes (merging it is dNh's decision, not a ChatX exit criterion); `sqlite_version` recorded and ≥ floor

## Out of scope

- P0.5 spikes (a)–(e), including anything touching the owner's `chat.db` or dNh's database.
- P1 and later: schema v2 models, parsers, fixtures, the real error registry, the CLI, the case store, the shield, providers. Nothing from the §8 keep-list is ported in P0.
- Any edit to the rev 2 spec or to `Dopemux-ChatRipperXXX` other than this packet. The old repo's tag `pre-rearchitecture-2026-10-20` and archiving (P7) are not P0.
- Any edit to `/Users/hue/code/dNh_CRM` (see Cross-repo criterion).
- Control Tower registration and TaskMaster list archival (S6 in the next-steps plan).
- Mutation testing (`mutmut`), property tests, fixture builders, perf markers, the real-sample shield evaluation. These gates apply from later phases.
- Core releases: tag `core-vX.Y.Z` cutting is the release contract (line 142); whether P0 cuts one is UNKNOWN (see Builder decisions B9).

## Acceptance checks

All State values start `NOT_RUN`. Preserve `PASS` / `FAIL` / `NOT_RUN` / `UNKNOWN` literally; never collapse `NOT_RUN` into `PASS`.

### Exit criteria (§6 P0 row, spec line 871)

The row is one cell with four semicolon-separated criteria; the first and third are split into separate rows for checking. Text is verbatim.

| ID | Criterion (verbatim) | How it will be checked | State |
|---|---|---|---|
| X1 | A green CI run, its URL recorded, that includes the failure-path tests (exit 3, `E_GATE_MISMATCH`, `E_SCHEMA_MISSING` stubs) | `gh run list -R <repo> --workflow ci.yml --limit 1 --json conclusion,url,headSha` returns `success` for the exact commit; `gh run view <id> --log` shows the three failure-path tests passed (not skipped); URL written to `docs/p0-exit-record.md` (path proposed, B12) | NOT_RUN |
| X2 | `uv sync` works from a clean clone | `git clone <remote> $SCRATCH/clean && cd $SCRATCH/clean && uv sync --all-packages --locked` exits 0, then `uv run pytest -q` exits 0. CI also runs this in a dedicated job (Task 6) | NOT_RUN |
| X3 | a dNh dev branch resolves the core by both the `path` and `workspace` forms | CROSS-REPO, needs separate authority (see section below). Check: from clean clones of dNh and chatstack, `uv lock` and `uv sync` succeed with `{ path = "../chatstack/packages/chat-extraction-core", editable = true }`, then with `{ workspace = "../chatstack" }`; `uv pip show chat-extraction-core` resolves in both | NOT_RUN |
| X4 | that branch's CI installs a pinned wheel and passes (merging it is dNh's decision, not a ChatX exit criterion) | CROSS-REPO, needs separate authority. Check: the dNh branch's CI run is green and its log shows the core installed from a wheel pinned by version and sha256 (`--require-hashes` or equivalent in the lock). Source of the wheel: UNKNOWN (B9) | NOT_RUN |
| X5 | `sqlite_version` recorded and ≥ floor | CI step prints `sqlite3.sqlite_version` and writes it to a job summary and uploaded artifact `sqlite-version.txt`; `tests/test_sqlite_floor.py` asserts the floor predicate (Task 5); the value is also written into `docs/reference/conformance.md` by the closing step. Floor: ≥ 3.51.3, or 3.50.x ≥ 3.50.7, or 3.44.x ≥ 3.44.6 (spec line 156) | NOT_RUN |

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

## Cross-repo criterion: dNh dev branch (X3, X4)

- Location: `/Users/hue/code/dNh_CRM`. Governed by dNh's own `AGENTS.md` and task packets (spec line 151). **Requires separate authority; this packet does not authorize any edit, branch creation, commit or push there.**
- Branch name: UNKNOWN — builder default (proposed): `dev/chatstack-core-resolve`. Naming only; creating it waits for dNh authority.
- What the check is (to be run by whoever holds dNh authority, after chatstack Tasks 1–7 are green):
  1. Clean clones of both repos side by side (`~/code/dNh_CRM` and `~/code/chatstack`, so the relative paths in spec lines 146–147 hold).
  2. Path form: dependency `{ path = "../chatstack/packages/chat-extraction-core", editable = true }`. Run `uv lock` then `uv sync`; import `chat_extraction_core` succeeds.
  3. Workspace form: `{ workspace = "../chatstack" }` exactly as the spec writes it (line 147). The spec cites evidence E8, and the audit's `out/external-fact-check.md` row E8 confirms it against docs.astral.sh: `workspace` may be "a path string to resolve a dependency from a different workspace"; the path points at the external workspace root and uv resolves the member named `chat-extraction-core`. Run `uv lock` then `uv sync` with the uv version pinned for the build; import succeeds. If that uv version rejects the form, stop (Stop S6).
  4. The branch's CI installs the core from a wheel pinned by version and sha256 and passes (X4).
- Prerequisite from chatstack: a built wheel with a known sha256. Source is UNKNOWN (B9).

## File structure (created by this packet)

```
/Users/hue/code/chatstack/
  pyproject.toml                  workspace root (virtual root, proposed B2); dev dependency group; ruff/mypy/pytest config
  uv.lock
  .python-version                 interpreter pin (value UNKNOWN, B1)
  .gitignore  .pre-commit-config.yaml  LICENSE (MIT, repo-level)  README.md
  .github/workflows/ci.yml        written fresh
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
- [ ] **Step 4: Commit** `docs: add design rev 2 copy, ADR template, conformance skeleton` (S7, S8, S10).

### Task 3: Package `chat-extraction-core` with schema-missing stub

**Files:**
- Create: `packages/chat-extraction-core/{pyproject.toml,LICENSE,THIRD_PARTY_NOTICES.md}`, `src/chat_extraction_core/{__init__.py,py.typed,errors.py,resources.py}`, `tests/{test_installed_not_checkout.py,test_sqlite_floor.py,test_failure_paths.py}`
- Test: the three test files above

**Interfaces:**
- Produces (proposed signatures, B4/B5):
  - `chat_extraction_core.__version__: str` (`"0.0.0"`, proposed).
  - `chat_extraction_core.errors.SchemaMissingError(Exception)` with class attribute `code = "E_SCHEMA_MISSING"` and `exit_code = 1`.
  - `chat_extraction_core.resources.read_schema(name: str) -> str` reading from the package through `importlib.resources.files("chat_extraction_core") / "schema" / name`; raises `SchemaMissingError` when absent.
  - `chat_extraction_core.sqlite_floor.meets_floor(version: str) -> bool` implementing: `>= 3.51.3`, or `3.50.x >= 3.50.7`, or `3.44.x >= 3.44.6`. Place it in `chat_extraction_core/sqlite_floor.py` (add that file to the list). Whether it belongs in the core or the app is UNKNOWN (B5); the spec says the app "refuses to open a case" (line 157), so a P1 relocation is possible.
- `pyproject.toml`: name `chat-extraction-core`, import package `chat_extraction_core` (spec lines 123, 774), hatchling build, `requires-python = ">=3.12"`, `license = "MIT"`, dependencies exactly `pydantic>=2,<3` and `phonenumbers>=8,<9` (line 160). Whether to declare them at P0 while no code imports them is UNKNOWN (B10); proposed: declare them, since `uv.lock` and `pip-audit` should exercise the real set.

- [ ] **Step 1: Write failing tests** in `tests/test_failure_paths.py`:
  - `test_read_schema_missing_raises_e_schema_missing`: `with pytest.raises(SchemaMissingError) as e: read_schema("does-not-exist.json")`; `assert e.value.code == "E_SCHEMA_MISSING"`; `assert e.value.exit_code == 1`.
  - `test_schema_missing_is_never_a_skip`: asserts the test above is not decorated with a skip marker (guards spec line 162): inspect `pytest.mark` on the function via `getattr(fn, "pytestmark", [])` and assert none named `skip`/`skipif`.
  In `tests/test_sqlite_floor.py`: parametrised `test_meets_floor` with `3.51.3 -> True`, `3.51.2 -> False`, `3.50.7 -> True`, `3.50.6 -> False`, `3.44.6 -> True`, `3.44.5 -> False`, `3.47.1 -> False` (the measured old-venv value, spec line 158), `3.53.1 -> True`; and `test_running_interpreter_meets_floor` asserting `meets_floor(sqlite3.sqlite_version)`.
  In `tests/test_installed_not_checkout.py`: `test_installed_not_checkout` asserting `"site-packages" in chat_extraction_core.__file__`, so a run against the source tree fails.
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
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Produces the jobs below. No file named `arch-gates.yml` anywhere; no workflow copied from `Dopemux-ChatRipperXXX` (S5). Action versions and runner labels: UNKNOWN, pin at build time to exact tags and record them in the commit message (B3). macOS arm64 is required, Linux x86_64 is nice to have (spec line 1084).

Jobs (matrix `os`: macOS arm64 required; Linux x86_64 optional, marked `continue-on-error: true` so a Linux failure never blocks the required result, B3):
1. `static`: `uv sync --all-packages --locked`; `ruff check`; `ruff format --check`; `mypy --strict` core; `mypy` app; `uv lock --check` (G1, G2, G4).
2. `audit`: `pip-audit` over the locked set (G5).
3. `wheel-tests` (the installed-wheel job, S4, X1, X5, G3): in order
   - `uv build --package chat-extraction-core --wheel --out-dir "$RUNNER_TEMP/dist"` and the same for `chatx`;
   - `sha256sum "$RUNNER_TEMP"/dist/*.whl` printed and uploaded as artifact (the digest feeds B9);
   - `uv venv "$RUNNER_TEMP/venv"` (fresh, outside the checkout) and `uv pip install --python "$RUNNER_TEMP/venv" "$RUNNER_TEMP"/dist/*.whl pytest pytest-cov`;
   - `mkdir "$RUNNER_TEMP/run" && cd "$RUNNER_TEMP/run"`, then run `"$RUNNER_TEMP/venv/bin/python" -m pytest "$GITHUB_WORKSPACE/packages/chat-extraction-core/tests" "$GITHUB_WORKSPACE/apps/chatx/tests" --cov=chat_extraction_core --cov=chatx --cov-branch --cov-fail-under=90 -p no:cacheprovider`, including the `installed`-marked tests; the cwd is outside the checkout and the checkout's `src/` is not on `sys.path`, which `test_installed_not_checkout` proves;
   - `"$RUNNER_TEMP/venv/bin/python" "$GITHUB_WORKSPACE/scripts/record_sqlite_version.py" | tee "$GITHUB_STEP_SUMMARY"` and upload `sqlite-version.txt` (X5).
4. `clean-clone`: `git clone "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY" "$RUNNER_TEMP/clean"` at the same SHA, `uv sync --all-packages --locked`, `uv run pytest -m "not installed"` (X2).
Triggers: `push` and `pull_request` (not specified by spec; proposed, B3).
Failure-path tests run in job 3 by name; the job also runs `pytest --collect-only -q -k "failure_paths"` and fails if fewer than the expected count is collected (guards against silent deselection). Expected count: UNKNOWN until the first local run (parametrised cases count individually); record it then (B11).

- [ ] **Step 1: Write `ci.yml`** per the jobs above with a tiny local lint (`uvx actionlint` if available, otherwise `NOT_RUN`).
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
- [ ] **Step 5: Hand off X3/X4** to whoever holds dNh authority with the Cross-repo section and the wheel digest. Leave X3, X4 `NOT_RUN` until they report evidence.

## Builder decisions (spec §11 items P0 touches; all values are `proposed`, not decided)

Spec §11 (lines 1078–1090) items P0 touches: "CI and logging: the CI matrix (macOS arm64 required, Linux x86_64 nice to have)". Naming and storage details and fixtures are P1+. Everything else below is not a §11 item but is stated UNKNOWN by the spec and needs a default.

| # | Item | Spec status | Proposed (not decided) |
|---|---|---|---|
| B1 | Interpreter and `.python-version` | spec: `>=3.12`, floor on linked SQLite; mise 3.12.13 links 3.53.1 (line 158) | proposed: mise-managed 3.12.13 if Task 1 Step 1 confirms 3.53.1 locally |
| B2 | Root `pyproject.toml` shape | not stated | proposed: virtual root (no `[project]`), dev tools in a dependency group |
| B3 | CI matrix, runners, triggers | §11: macOS arm64 required, Linux x86_64 nice to have | proposed: macOS arm64 required job; Linux x86_64 `continue-on-error: true`; runner labels and action tags UNKNOWN, pin at build time; triggers `push` and `pull_request` |
| B4 | Distribution name of the app and package versions | core `chat-extraction-core` stated; app distribution name not stated | proposed: `chatx`; both start at `0.0.0` |
| B5 | Where the floor predicate and recorder live | not stated (line 157 says the app refuses to open a case) | proposed: `chat_extraction_core/sqlite_floor.py` plus `scripts/record_sqlite_version.py`; may move in P1/P2 |
| B6 | ADR template path and sections | not stated | proposed: `docs/adr/0000-template.md`, sections Title/Status/Context/Decision/Consequences/Alternatives rejected/Evidence |
| B7 | Path of the design copy | "this document copied in" only | proposed: `docs/design/2026-10-20-chatx-rearchitecture-design.md` |
| B8 | `pip-audit` invocation and pre-commit revs | tools named, flags not | proposed: audit the exported lock (`uv export --frozen --all-packages --no-emit-workspace` piped to `pip-audit --requirement - --no-deps --disable-pip`), verify flags against the installed version first; pre-commit revs from `autoupdate` |
| B9 | Source of the pinned wheel for dNh (X4) | release contract says tags `core-vX.Y.Z` with wheel + sha256 built in CI (line 142); P0 cutting a tag is not stated | proposed: P0 CI uploads wheel and sha256 as a build artifact only; no tag or release without explicit owner authority |
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

- G-A (tension, not a contradiction): line 871 says "two empty packages" and also requires failure-path "stubs" in P0 CI. Stubs cannot pass without some code. Resolved by proposal only (Tasks 3, 4); owner/supervisor should confirm.
- G-B (inconsistency in scope of "exit 3"): the P0 row lists "exit 3, `E_GATE_MISMATCH`, `E_SCHEMA_MISSING` stubs" together, but `E_SCHEMA_MISSING` is exit 1 (line 661) and only `E_GATE_MISMATCH` is exit 3 (line 663). The tests here assert each code's own mapping.
- G-C: line 728 names `config/arch-gates.yml` as the file to rewrite, while line 871 and the brief name `arch-gates.yml` under workflows. Packet asserts neither path exists (S5).
- G-D (resolved by the audit, not a gap): the spec writes the dNh form as `{ workspace = "../chatstack" }` (line 147). uv documents this form: the `workspace` field "can also be set to a path string to resolve a dependency from a different workspace"; the path "must point to the external workspace root" and uv picks the member whose name matches the dependency (audit `out/external-fact-check.md`, E8, SUPPORTED, docs.astral.sh). The in-workspace boolean `workspace = true` is a different, same-workspace form. X3 still exercises both dNh forms against the real uv version pinned at build time (Stop S6 if the pinned uv rejects it).
- G-E: X4 needs "a pinned wheel", but the release contract (line 142) ties wheels to `core-vX.Y.Z` tags and P0 states no tag. See B9.
- G-F: the CI-URL recording location, repo remote name and visibility, runner labels, tool versions, hook revisions and the dNh branch name are not stated. All marked UNKNOWN/proposed above.

## Stop conditions (implementer stops and returns to the supervisor)

- S1: Any need to create the remote, push, tag, or make a repo public without recorded owner authority.
- S2: Any edit needed inside `/Users/hue/code/dNh_CRM`, `/Users/hue/code/Dopemux-ChatRipperXXX` (other than reading the spec for the copy), or the spec.
- S3: No locally available interpreter links SQLite at or above the floor, or CI's macOS arm64 interpreter reports below the floor.
- S4: CI cannot be made green without lowering coverage below 90, adding an `omit`, skipping a failure-path test, or weakening a gate.
- S5: A proposed default (B-list) would need a value the spec forbids or contradicts (for example a core dependency beyond `pydantic` and `phonenumbers`).
- S6: the uv version pinned for the build rejects `{ workspace = "../chatstack" }` (documented per E8, but version behaviour is checked, not assumed), or the two dNh forms cannot both resolve from clean clones.
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
