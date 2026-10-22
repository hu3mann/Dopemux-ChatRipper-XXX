# Cross-audit matrix (generated; do not hand-edit)

## Tally

| Auditor | BLOCKER | HIGH | MEDIUM | LOW | INFO | Total | Packet verdict |
|---|---|---|---|---|---|---|---|
| argon | 5 | 9 | 9 | 2 | 0 | 25 | DO-NOT-APPROVE |
| astra | 2 | 20 | 15 | 0 | 3 | 40 | DO-NOT-APPROVE |
| astra-pro | 1 | 14 | 16 | 1 | 4 | 36 | DO-NOT-APPROVE |
| deepseek | 0 | 2 | 12 | 6 | 4 | 24 | APPROVE-WITH-CHANGES |
| grok | 1 | 12 | 12 | 5 | 2 | 32 | DO-NOT-APPROVE |
| kimi | 1 | 6 | 10 | 9 | 4 | 30 | DO-NOT-APPROVE |
| **all** | 10 | 63 | 74 | 23 | 17 | 187 | |

## By location

### packet: (before first heading)  **convergence** (8 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F24 | MEDIUM | CONFIRMED | Acceptance ledger; G-F; approval recording | **[S9, S10, S12] The ledger and write authority need one concrete contract.** The packet defines 21 X/S/… | Name one authoritative exit record containing every criterion, state, command/result, evidence link, and… |
| AST-F35 | MEDIUM | CONFIRMED | packet:L3 | [S10,S11] Delegation is requested without task ownership, dependency edges or bounded call/retry budgets. | Record Task 1 before 2/3, core interface before 4, 2–4 before 5, and 5 before 6/7; assign bounded packag… |
| DSK-F13 | MEDIUM | CONFIRMED | packet:L3,L149 | [S11] No per-task estimate, model assignment, or call/retry budget is stated (scope 11), and the subagen… | Add a budget line per task and state stop conditions bind subagents. |
| GRK-F25 | MEDIUM | CONFIRMED | packet:L3 | [S10] [S11] The header requires subagent-driven execution of every task, including Task 7's push and tag… | Add a one-line budget per task. Mark Task 6 and Task 7 supervisor-only. Tell subagents they stop at S1 a… |
| ARG-F24 | LOW | CONFIRMED | packet:L3 | [S10][S11] The packet header (`packet:L3`) instructs agentic workers to `Use superpowers:subagent-driven… | Add a delegation table mapping Tasks 1–6 (local repo/code/CI authoring, sequential dependencies `T1 -> T… |
| ASP-F31 | LOW | CONFIRMED | Execution handoff and delegation | **[S10, S11] The ordered tasks are usable, but parallel execution has no shared-file ownership or bounde… | Default to serial integration or name one integrator for shared files and commits. Delegate independent … |
| GRK-F30 | LOW | CONFIRMED | packet:L7 | [S14] The packet is step S2 of next-steps, which still says the design is rev 2 at 1,261 lines and that … | One packet line: S2's input is rev 2.1, and the next-steps freeze does not revert that block. |
| KIM-F25 | LOW | CONFIRMED | packet:L3 | [S11] The packet mandates subagent-driven execution but never says the nine Stop conditions must be prop… | Add one line: every task delegation must embed the full Stop-conditions list verbatim, and any stop retu… |

### packet: Cross-repo criterion: dNh dev branch (X3, X4)  **convergence** (9 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F14 | HIGH | PLAUSIBLE | packet:L119 | [S1][S6] Criterion X3 (`packet:L80`, `L119`) and `spec:L147` require dNh to resolve `chat-extraction-cor… | Move a non-mutating smoke test of `uv` (`0.12.11`) workspace/path syntax in `$SCRATCH` into Task 1 Step … |
| ASP-F18 | HIGH | CONFIRMED | Private release consumption by dNh | **[S6, S10, S13, S15] The separately authorised X4 work needs a cross-repository credential plan.** The … | Put a least-privilege source-repository read mechanism in the dNh handoff, such as an appropriately scop… |
| ASP-F19 | HIGH | CONFIRMED | dNh source-to-wheel transition | **[S1, S6] The consumer transition is described as an outcome rather than an executable change.** The bu… | Prepare a separate-authority handoff specifying the dependency entry, removal/replacement of development… |
| AST-F25 | HIGH | CONFIRMED | packet:L118–120 | [S1,S6] The dNh handoff does not specify the transition from editable source experiments to a wheel-lock… | Give dNh's authorized owner exact manifest surfaces, separate path/workspace experiments, and a final wh… |
| AST-F28 | HIGH | CONFIRMED | packet:L117 | [S6,S10] The clean-clone instruction names the existing primary repository paths. | Use a unique authorized scratch parent with sibling dNh_CRM/chatstack clones at recorded SHAs, preserve … |
| DSK-F14 | MEDIUM | PLAUSIBLE | packet:L119 | [S1] The `workspace = "../chatstack"` cross-workspace form is confirmed (docs.astral.sh), but the packet… | Specify the expected dNh lock delta and verify only chat-extraction-core plus its deps enter dNh's lock. |
| KIM-F15 | MEDIUM | CONFIRMED | packet:L116 | [S6] X3 and X4 require two different dNh pyproject states on one branch — a path/workspace source for X3… | State that X3 is verified locally (never pushed to CI) and X4 is a follow-up commit switching the source… |
| GRK-F31 | INFO | CONFIRMED | packet:L114 | [S6] [S10] The separate-authority boundary is real: the packet forbids edits to dNh, and X3/X4 stay NOT_… | Keep X3 and X4 at NOT_RUN in the ChatX exit record until dNh evidence arrives. Do not mark P0 all-PASS w… |
| GRK-F32 | INFO | CONFIRMED | packet:L119 | [S1] [S15] These checks match current docs and are not defects. Workspace globs match spec §3.2. One roo… | Name the group `dev`. Re-check `uv export --help` and `uv sync --help` on 0.12.11 for `--all-packages`, … |

### packet: Exit criteria (§6 P0 row, spec line 871)  **convergence** (19 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F04 | BLOCKER | CONFIRMED | packet:L81 | [S6][S9] Exit criterion X4 requires a dNh dev branch's CI to install the `core-v0.0.1a0` wheel from `DDD… | Specify in the Cross-repo section (`packet:L113-121`) how dNh's CI authenticates to private `DDD-Enterpr… |
| ASP-F01 | HIGH | CONFIRMED | X3/X4; Task 7; completion contract | **[S9, S10, S14] The governing exclusion of X3/X4 has not reached the operative acceptance text.** The b… | Record the brief’s existing owner decision as an explicit override in the packet and exit record. Keep X… |
| ASP-F10 | HIGH | CONFIRMED | X2; Tasks 3–5; installed marker | **[S1, S3, S4] Several local acceptance commands include tests that are expected to fail in an editable … | Register the marker and use an explicit `-m "not installed"` selection consistently for workspace runs. … |
| ASP-F11 | HIGH | CONFIRMED | X1; Tasks 3–4; B11; Task 7 evidence | **[S3, S4, S9] The test proof has no fixed identity or outcome contract.** The prescribed cases imply te… | Name the required node IDs and parameter cases, with an explicit expected manifest. Retain execution res… |
| ASP-F14 | HIGH | CONFIRMED | X5; Task 6 SQLite artifact | **[S7, S9] The requested SQLite evidence file is never created by the shown recipe.** The recorder is pi… | Write the recorder output to a named artifact path and append the same output to the summary. Upload tha… |
| ASP-F21 | HIGH | CONFIRMED | X4 version/hash enforcement | **[S5, S6, S13, S15] “Version + SHA256” lacks a selected enforcement recipe and trusted expected-hash lo… | In the separate dNh handoff, choose a concrete installation path and persist the approved expected wheel… |
| ASP-F22 | HIGH | CONFIRMED | X1; Task 7 exit-record commits | **[S5, S9] The evidence record confuses the tested commit with the commit containing its evidence.** X1 … | Name the tested source SHA, release tag SHA, and evidence-document SHA separately. Use a durable externa… |
| AST-F08 | HIGH | CONFIRMED | packet:L79 | [S3,S4,S9] Local acceptance commands select tests deliberately designed to fail under editable installat… | Register installed and explicitly exclude it in every editable/local command while explicitly including … |
| AST-F27 | HIGH | CONFIRMED | packet:L81 | [S6,S9] A green existing dNh workflow does not by itself prove a frozen, hashed wheel installation. | Define the authorized PR/trigger, consumer uv pin, immutable dNh lock and wheel URL/hash representation,… |
| DSK-F01 | HIGH | CONFIRMED | packet:L81 | [S6] X4 says dNh CI will "install a pinned wheel" from the core-v0.0.1a0 pre-release assets but specifie… | Specify an authenticated `gh release download` + explicit sha256 check in dNh CI, and drop the "or equiv… |
| GRK-F02 | HIGH | CONFIRMED | packet:L78 | [S9] [S14] X1 and the scope quote claim to be verbatim from spec L871, but they still use the pre-2.1 se… | Replace the scope-section quote and the X1 criterion cell with the current spec L871 exit sentence. |
| GRK-F04 | HIGH | CONFIRMED | packet:L79 | [S9] X2's command is `uv run pytest -q` with no marker filter. `test_installed_not_checkout` requires `s… | Change X2 to `uv run pytest -q -m "not installed"`. Keep the installed-wheel proof on S4 and the wheel j… |
| GRK-F08 | HIGH | CONFIRMED | packet:L80 | [S1] [S6] X3 and X4 are one dNh branch, but a `path` or `workspace = "../chatstack"` source is absent on… | Split the work: path and workspace forms are local experiments and must be reverted before push. The CI … |
| KIM-F02 | HIGH | CONFIRMED | packet:L79 | [S9] X2's check runs `uv run pytest -q` from a clean clone, where installs are editable and the `install… | Change X2's command to `uv run pytest -q -m "not installed"` to match the two other clean-clone checks. |
| ARG-F15 | MEDIUM | CONFIRMED | packet:L81 | [S2][S6] Because `0.0.1a0` is a PEP 440 pre-release (`a0`), pinning or resolving `chat-extraction-core` … | Specify the exact `pyproject.toml` snippet for X4: `chat-extraction-core == 0.0.1a0` in `dependencies` p… |
| ASP-F23 | MEDIUM | CONFIRMED | Task 6 clean-clone job | **[S4, S9] “At the same SHA” is not implemented by the shown clone command.** The command clones the rep… | Specify authenticated checkout into a unique temporary directory, define whether a PR check uses its hea… |
| GRK-F19 | MEDIUM | CONFIRMED | packet:L80 | [S6] [S7] X3 and X4 never print dNh's `sqlite3.sqlite_version`. dNh `.python-version` is `3.12` (floatin… | The dNh check records `sqlite3.sqlite_version` from the interpreter that imports the core. Below floor i… |
| KIM-F19 | LOW | CONFIRMED | packet:L78 | [S9] X1's `gh run list ... --limit 1` returns the newest run of the workflow, which may be a later push,… | Add `--commit <sha>` to the `gh run list` invocation in X1. |
| KIM-F29 | INFO | PLAUSIBLE | packet:L81 | [S2][S15] dNh pinning `chat-extraction-core==0.0.1a0`: both pip and uv allow a pre-release when the requ… | Builder verifies with `uv pip install --dry-run "chat-extraction-core==0.0.1a0"` (or pip equivalent) onc… |

### packet: Task 1: Repo, workspace root, interpreter, licence  **convergence** (13 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F13 | HIGH | CONFIRMED | packet:L159 | [S7] Task 1 Step 1 (`packet:L159`) selects a local interpreter via `uv python list --only-installed` and… | Explicitly specify the Python/SQLite provisioning step in `ci.yml` and `release.yml` (e.g., pinning `ast… |
| GRK-F12 | HIGH | CONFIRMED | packet:L161 | [S1] [S2] Task 1 puts `requires-python = ">=3.12"` on the root, and B2 says the root has no `[project]`.… | Keep the root as `[tool.uv.workspace]` plus `[dependency-groups] dev` only. Put `requires-python = ">=3.… |
| ASP-F15 | MEDIUM | CONFIRMED | Interpreter selection; B1/B3; S9 | **[S7] The reported mise interpreter is not a provisioned CI interpreter contract.** A Python version st… | Specify the interpreter provider and selection procedure. Record `sys.executable`, Python version, archi… |
| ASP-F29 | MEDIUM | CONFIRMED | Tool resolution; hook updates; stop S7 | **[S4, S12, S13] “Whatever resolves” and automatic hook updates conflict with the age/pinning stop unles… | Select and record eligible versions before acceptance runs, execute tools from the controlled environmen… |
| AST-F04 | MEDIUM | CONFIRMED | packet:L161 | [S1,S2,S15] The root metadata instructions mix a projectless root with an unplaced requires-python field. | Choose an explicit valid root TOML shape, keep >=3.12 in both member projects if the root stays projectl… |
| AST-F33 | MEDIUM | CONFIRMED | packet:L161 | [S4,S10,S13] Unrestricted dependency selection and autoupdate conflict with Stop S7's two-week rule. | Define a dated dependency-selection policy covering transitive/build/test/hook tools, and distinguish ve… |
| AST-F36 | MEDIUM | CONFIRMED | packet:L159–162 | [S10,S11] Filesystem authority outside chatstack is not fully scoped for normal tool operation and scrat… | Make an existing destination a hard stop, name permitted disposable scratch/cache roots and provisioning… |
| GRK-F24 | MEDIUM | CONFIRMED | packet:L159 | [S7] Task 1 discovers interpreters only with `uv python list --only-installed`. The spec's known-good ru… | Also measure the mise interpreter if it is installed. Write the exact patch into `.python-version`. CI u… |
| KIM-F08 | MEDIUM | PLAUSIBLE | packet:L161 | [S1][S2] Task 1 Step 3 writes `requires-python = ">=3.12"` into the root pyproject while B2 makes the ro… | Drop the key at the root and declare `requires-python = ">=3.12"` in each member; Task 3 states it, Task… |
| DSK-F15 | LOW | PLAUSIBLE | packet:L161 | [S1] The root virtual pyproject carries a bare `requires-python = ">=3.12"` but a virtual root has no `[… | Remove root-level requires-python; rely on member-level requires-python and `.python-version`. |
| ASP-F34 | INFO | CONFIRMED | Development groups and prerelease selection | **[S1, S2, S15] The proposed development-group and alpha-version choices are compatible with current pac… | Retain development groups and the accepted core alpha version. Use an explicit consumer requirement or s… |
| AST-F39 | INFO | CONFIRMED | packet:L161 | [S2,S15] Dependency groups and an alpha release are sound choices; neither requires switching to PyPI. | Retain the dev group and exact 0.0.1a0 wheel pin, verify resolver policy with the chosen uv/pip versions… |
| KIM-F28 | INFO | CONFIRMED | packet:L159 | [S7] Harness-supplied toolchain facts corroborate spec L158: the owner machine's `python3` is 3.12.13 li… | None; Task 1 Step 1 measures it again anyway. |

### packet: Task 3: Package `chat-extraction-core` with schema-missing stub  **convergence** (20 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F02 | BLOCKER | CONFIRMED | packet:L186 | [S2][S14] Task 3 specifies `chat_extraction_core.__version__: str ("0.0.0", proposed)`, directly contrad… | Update Task 3 (`packet:L186` and `packet:L190`) to set `version = "0.0.1a0"` in `packages/chat-extractio… |
| AST-F01 | BLOCKER | CONFIRMED | packet:L186 | [S2,S5,S14] The executable core interface still starts at 0.0.0, contradicting the approved release vers… | Set one authoritative version to 0.0.1a0 and require wheel METADATA, installed distribution version, mod… |
| GRK-F01 | BLOCKER | CONFIRMED | packet:L186 | [S2] [S5] [S14] The only version Task 3 tells the builder to write is `__version__ = "0.0.0"`, while B4 … | Set `[project].version` and `__version__` to `0.0.1a0` from one assignment, mark that part of B4 decided… |
| KIM-F01 | BLOCKER | CONFIRMED | packet:L186 | [S2][S5] The core's version is never set to the decided `0.0.1a0`: Task 3 proposes `__version__` of `"0.… | In Task 3 set `[project] version = "0.0.1a0"` and `__version__ = "0.0.1a0"`; add a release-job step asse… |
| ARG-F07 | HIGH | CONFIRMED | packet:L181 | [S3][S8] The File structure (`packet:L134`) and Task 3 Interfaces (`packet:L189`) include `sqlite_floor.… | Reconcile the File structure block (`packet:L125-145`) and the per-task `Files:` lists (`packet:L181`, `… |
| ARG-F10 | HIGH | CONFIRMED | packet:L188 | [S2][S3] Task 3 (`packet:L188`) implements `read_schema(name: str) -> str` via `importlib.resources.file… | Specify in Task 3 that `read_schema` must catch `FileNotFoundError` (and check `.is_file()`) on the `Tra… |
| ARG-F11 | HIGH | CONFIRMED | packet:L196 | [S4] In Task 3 (`packet:L196`) and Task 4 (`packet:L219`), `test_installed_not_checkout` asserts `"site-… | Specify in Task 1 Step 3 that `[tool.pytest.ini_options]` in root `pyproject.toml` must NOT put `--cov` … |
| ASP-F03 | HIGH | CONFIRMED | Task 3 version; B4; G-E | **[S2, S5] Core version instructions disagree.** Task 3 specifies `core.__version__ = "0.0.0"`, while B4… | Set the core distribution and import versions consistently to `0.0.1a0`. Add an acceptance assertion com… |
| ASP-F05 | HIGH | CONFIRMED | Build-system requirements; CI and release builds | **[S2, S5, S15] Build dependencies have no reproducible installation contract.** The packet names Hatchl… | Specify backend versions and a supported mechanism for constraining and verifying their dependency closu… |
| AST-F11 | HIGH | CONFIRMED | packet:L194 | [S3,S4,S9] The anti-skip guard does not prove the required failure paths executed successfully. | Define mandatory node IDs and expected parameter cases in advance, then reject skipped, xfailed, missing… |
| KIM-F03 | HIGH | CONFIRMED | packet:L199 | [S3][S4] Task 3 Step 4 and Task 4 Step 4 say to run "the same command" as Steps 2 and expect "PASS apart… | Add `-m "not installed"` to both Step 2/4 commands and register the `installed` marker in the root pytes… |
| ARG-F16 | MEDIUM | CONFIRMED | packet:L198 | [S3][S7] Task 3 Step 3 (`packet:L198`) specifies implementing `meets_floor(version: str) -> bool` via `t… | Specify in Task 3 that `meets_floor` must strictly validate a 3-part integer version (`^\d+\.\d+\.\d+$`)… |
| ARG-F19 | MEDIUM | CONFIRMED | packet:L181 | [S2][S8] Both packages include `LICENSE` and `THIRD_PARTY_NOTICES.md` (`packet:L181`, `L205`; `spec:L150… | Specify the P0 content of `THIRD_PARTY_NOTICES.md` for both packages (listing `pydantic` and `phonenumbe… |
| AST-F06 | MEDIUM | CONFIRMED | packet:L181–190 | [S2,S8] Creating LICENSE, THIRD_PARTY_NOTICES.md and py.typed does not establish that both wheels ship t… | Define compatible licence metadata and inclusion rules for both packages, and assert the required files … |
| AST-F14 | MEDIUM | CONFIRMED | packet:L196 | [S4,S9] The installed-origin assertion is weaker than the wheel provenance claim. | Assert resolved module locations under that venv's actual installation directories and outside the check… |
| DSK-F04 | MEDIUM | CONFIRMED | packet:L186 | [S2] Task 3 sets core `__version__ = "0.0.0"` but B4/G-E decide the core starts at 0.0.1a0; wheel metada… | Set `__version__ = "0.0.1a0"` and derive it from pyproject `version`. |
| DSK-F12 | MEDIUM | PLAUSIBLE | packet:L189,L205 | [S2] hatchling does not auto-include LICENSE or THIRD_PARTY_NOTICES.md in the wheel, yet the packet clai… | Add hatchling include config so LICENSE and THIRD_PARTY_NOTICES.md land in each wheel. |
| GRK-F18 | MEDIUM | CONFIRMED | packet:L192 | [S3] [S8] `read_schema` is specified to return the resource or raise. The only test is the missing path.… | Ship one tiny schema via `importlib.resources` and a test that reads it, or state that P0 always raises … |
| GRK-F21 | MEDIUM | CONFIRMED | packet:L190 | [S2] [S15] The core metadata sets `license = "MIT"` and tells the builder to write `LICENSE` and `THIRD_… | Add the hatchling include or `license-files` the pinned hatchling accepts. The wheel job fails if `unzip… |
| KIM-F10 | MEDIUM | CONFIRMED | packet:L181 | [S3][S12] `sqlite_floor.py` appears in the file tree and the Task 3 interface but is missing from Task 3… | Add `sqlite_floor.py` to Task 3's Files list and record explicitly (packet G-A or owner note) that the f… |

### packet: Task 4: Package `chatx` with egress-refusal stubs  **convergence** (9 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F20 | MEDIUM | CONFIRMED | packet:L212 | [S3][S14] Task 4 (`packet:L212`) defines `chatx.errors.exit_code_for(code: str) -> int` mapping 5 codes … | Either restrict `chatx/errors.py` to `E_GATE_MISMATCH` (exit 3) and `E_SCHEMA_MISSING` (exit 1) to stric… |
| ASP-F07 | MEDIUM | CONFIRMED | Task 4 app metadata | **[S2, S6, S15] The source override is more explicit than the published dependency contract.** The packe… | Specify the app’s project dependency, approved version bound, Python requirement, build backend, and pac… |
| AST-F05 | MEDIUM | CONFIRMED | packet:L205–221 | [S1,S2] The app's wheel metadata contract is incomplete, particularly its published requirement on the c… | Specify the app name/version, Hatchling backend, Python floor and bounded core requirement, then inspect… |
| AST-F10 | MEDIUM | CONFIRMED | packet:L211–218 | [S3,S14] The tests prove integer mappings and exception attributes, not operating-system exit status. | State explicitly whether mapping-only stubs satisfy G-A or require a test-only subprocess harness for ex… |
| DSK-F03 | MEDIUM | CONFIRMED | packet:L207 | [S2] Task 4 declares the core only via `[tool.uv.sources] workspace = true` but never adds chat-extracti… | Add `chat-extraction-core==0.0.1a0` (exact, pre-release-safe) to app `[project].dependencies`. |
| KIM-F09 | MEDIUM | CONFIRMED | packet:L209 | [S2] Task 4 never enumerates the app's pyproject contents — no `version`, no `requires-python`, no licen… | Mirror Task 3: state `version = "0.0.0"`, `requires-python = ">=3.12"`, `license` and hatchling backend … |
| DSK-F18 | LOW | CONFIRMED | packet:L211 | [S3] The exit-3 "failure path" is asserted as an attribute (`GateMismatchError.exit_code == 3`), not an … | Record in p0-exit-record.md that exit 3 is asserted at the attribute level, with the real CLI exit defer… |
| GRK-F28 | LOW | CONFIRMED | packet:L208 | [S2] Task 4 says chatx consumes the core via `[tool.uv.sources]` and does not say to list `chat-extracti… | State both tables, `license = "MIT"` for the app, version `0.0.0`, and that approval adopts the distribu… |
| KIM-F26 | LOW | PLAUSIBLE | packet:L208 | [S1][S15] When uv builds the chatx wheel, the `{ workspace = true }` core dependency is expected to be r… | Builder inspects the built chatx wheel's METADATA in Task 6 and records what uv emitted; if it is not an… |

### packet: Task 6: CI workflow written fresh  **convergence** (44 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F01 | BLOCKER | CONFIRMED | packet:L253 | [S4] The `wheel-tests` job installs the built wheels with `uv pip install` alongside only `pytest` and `… | Pass `-c "$GITHUB_WORKSPACE/pyproject.toml"` to `pytest` in `wheel-tests`, and export pinned hashes from… |
| ARG-F03 | BLOCKER | CONFIRMED | packet:L257 | [S5][S13] Neither `ci.yml` nor `release.yml` specifies a `permissions:` block; `release.yml` runs `gh re… | Declare `permissions: contents: read` at the top level of `ci.yml` and `permissions: contents: write` on… |
| ASP-F02 | BLOCKER | CONFIRMED | Task 6 release job; Task 7 G-E handoff | **[S4, S5, S13] Published bytes are not bound to tested bytes.** CI builds and tests wheels, but the tag… | Preserve the tagged-tree build required by G-E. Before publication, install and test that exact release … |
| ARG-F06 | HIGH | CONFIRMED | packet:L255 | [S7][S9] In Task 6 job 3 (`wheel-tests`), `"$RUNNER_TEMP/venv/bin/python" "$GITHUB_WORKSPACE/scripts/rec… | Change the step to `tee "$RUNNER_TEMP/sqlite-version.txt" >> "$GITHUB_STEP_SUMMARY"` and upload `$RUNNER… |
| ARG-F08 | HIGH | CONFIRMED | packet:L252 | [S4][S5] Task 6 job 3 (`wheel-tests`) uses `sha256sum "$RUNNER_TEMP"/dist/*.whl` (`packet:L252`) and `re… | Standardise on `(cd dist && shasum -a 256 *.whl > SHA256SUMS)` in both `wheel-tests` and `release.yml` s… |
| ASP-F17 | HIGH | CONFIRMED | Release workflow authentication | **[S5, S13, S15] Release creation lacks an explicit credential and permission contract.** The recipe inv… | Define `GH_TOKEN` from the workflow token for the release step and grant `contents: write` only where ne… |
| AST-F12 | HIGH | CONFIRMED | packet:L253 | [S4,S13] Wheel tests install a freshly resolved dependency set rather than the audited locked set. | Install a hash-checked export of the selected lock into the external venv, install verified local wheels… |
| AST-F13 | HIGH | CONFIRMED | packet:L251–257 | [S2,S5,S13,S15] The build toolchain is outside the packet's demonstrated hash-pinning contract. | Pin and verify the build requirements used in CI and release, select flags supported by the chosen uv ve… |
| AST-F16 | HIGH | CONFIRMED | packet:L255 | [S4,S7,S9] The SQLite upload artifact is never created by the stated command. | Write one named SQLite evidence file, append its contents to the summary, upload that exact path with mi… |
| AST-F17 | HIGH | CONFIRMED | packet:L256 | [S1,S4,S9] The clean-clone recipe does not implement its same-SHA, isolated-checkout claim. | Specify an authenticated checkout into a fresh scratch directory, select and assert the exact event comm… |
| AST-F19 | HIGH | CONFIRMED | packet:L245 | [S4,S13] Exact action tags are treated as immutable pins. | Pin every action and reusable third-party workflow to a verified full commit SHA, retain its human-reada… |
| AST-F20 | HIGH | CONFIRMED | packet:L257 | [S4,S5,S13] Workflow token permissions and gh authentication are unspecified. | Set contents: read by default, grant contents: write only to the gated publishing job, bind GH_TOKEN the… |
| AST-F21 | HIGH | CONFIRMED | packet:L257–258 | [S5,S10] A matching tag immediately enables publication without an enforced green-CI dependency. | Make publication fail closed until all required checks for the dereferenced tag commit succeed, and reta… |
| AST-F23 | HIGH | CONFIRMED | packet:L257 | [S2,S5] The broad core-v* trigger has no tag-to-package identity validation. | Reject malformed or mismatched tags, require the approved P0 tag and notes file, assert a clean checkout… |
| DSK-F02 | HIGH | PLAUSIBLE | packet:L247 | [S4] CI's green run and X5 depend on the GitHub macOS runner's Python linking SQLite >= 3.51.3, which is… | Add a CI step to install/verify a known floor-compliant CPython (python-build-standalone 3.12.x linking … |
| GRK-F05 | HIGH | CONFIRMED | packet:L255 | [S7] [S9] The wheel job pipes `record_sqlite_version.py` into `$GITHUB_STEP_SUMMARY` and then says to up… | Write the JSON to `$RUNNER_TEMP/sqlite-version.txt`, upload that path, and append the same bytes to the … |
| GRK-F06 | HIGH | CONFIRMED | packet:L247 | [S4] [S7] [S13] [S15] The job list never checks out the repo, never installs uv, never selects `.python-… | Specify `actions/checkout` and `astral-sh/setup-uv` by commit SHA, `version: "0.12.11"`, `permissions: c… |
| GRK-F07 | HIGH | CONFIRMED | packet:L256 | [S4] [S9] [S13] The clean-clone command is a raw `git clone` of `$GITHUB_SERVER_URL/$GITHUB_REPOSITORY` … | Use `actions/checkout` with `ref: ${{ github.sha }}` and a second `path`. Do not invent a token-in-URL c… |
| GRK-F13 | HIGH | PLAUSIBLE | packet:L252 | [S4] [S5] The required macOS job and the release job call `sha256sum`. macOS ships `shasum`, not `sha256… | Use `shasum -a 256` in both workflows. |
| KIM-F05 | HIGH | CONFIRMED | packet:L256 | [S4] The `clean-clone` job runs `git clone "$GITHUB_SERVER_URL/$GITHUB_REPOSITORY"` with no credentials;… | Use `gh repo clone "$GITHUB_REPOSITORY"` with `env: GH_TOKEN: ${{ github.token }}`, or an `x-access-toke… |
| KIM-F06 | HIGH | CONFIRMED | packet:L257 | [S4][S5][S13] Neither workflow gets a `permissions:` block and the `gh release create` step gets no `GH_… | Add `permissions: contents: read` to ci.yml, `permissions: contents: write` to release.yml, and `env: GH… |
| KIM-F07 | HIGH | CONFIRMED | packet:L253 | [S7] The `wheel-tests` job — the one that records `sqlite_version` for X5/S9 — never pins an interpreter… | Pin uv (`setup-uv` with an exact version) and add `uv python install 3.12 && uv python pin 3.12` (or set… |
| ARG-F17 | MEDIUM | CONFIRMED | packet:L257 | [S5] In `release.yml` (`packet:L257`), the workflow triggers on `core-v*` tags and builds `chat-extracti… | Add a step in `release.yml` before `uv build` that asserts ` GITHUB_REF_NAME == "core-v$(python3 -c 'imp… |
| ARG-F22 | MEDIUM | CONFIRMED | packet:L245 | [S4][S13] Task 6 (`packet:L245`, `B3` at `packet:L287`) says `Action versions and runner labels: UNKNOWN… | Require pinning all GitHub Actions in `ci.yml` and `release.yml` to full 40-char commit SHAs (with the v… |
| ARG-F23 | MEDIUM | CONFIRMED | packet:L259 | [S3][S4] Task 6 (`packet:L259`) guards against silent deselection of failure-path tests by running `pyte… | Extend `test_schema_missing_is_never_a_skip` to forbid `xfail` in `pytestmark` as well, and in `ci.yml` … |
| ASP-F28 | MEDIUM | CONFIRMED | Action pinning policy | **[S4, S13, S15] Exact action tags are not immutable references.** The packet’s “exact tags” language ca… | Use a supported action dependency lock mechanism or verified full upstream commit SHAs, with readable re… |
| ASP-F30 | MEDIUM | CONFIRMED | Tag-triggered release gate | **[S5] Correct manual sequencing is not enforced by the workflow.** Task 7 correctly waits for green CI … | Make the release job verify the required successful CI result for the tagged SHA and validate the tag ag… |
| ASP-F32 | MEDIUM | CONFIRMED | CI operational bounds and result reporting | **[S4, S13] Job bounds and environment reuse policy remain unspecified.** The workflow recipe does not c… | Specify job timeouts and expected package/GitHub network access. Choose no cache or a scoped dependency-… |
| AST-F24 | MEDIUM | CONFIRMED | packet:L257–276 | [S5,S9,S15] Release custody omits a consumer-verifiable manifest layout and a partial-publication policy. | Define manifest-relative filenames, download and verify the published wheel against the expected digest,… |
| AST-F37 | MEDIUM | CONFIRMED | packet:L245–261 | [S4,S7,S13] Runner qualification and CI operational controls remain incomplete. | Specify the approved runner/uv/Python setup, assert arm64 and the SQLite floor in the test interpreter, … |
| DSK-F06 | MEDIUM | CONFIRMED | packet:L245,B3 | [S4] Action pinning is specified as "exact tags", not commit SHAs; supply-chain best practice (and the b… | Pin each action to a full commit SHA and record the SHA. |
| DSK-F07 | MEDIUM | CONFIRMED | packet:L247 | [S13] No least-privilege `permissions:` block is specified; ci.yml needs `contents: read` and release.ym… | Add `permissions: contents: read` to ci.yml and `contents: write` to release.yml. |
| DSK-F08 | MEDIUM | CONFIRMED | packet:L257 | [S5] release.yml names the release from `$GITHUB_REF_NAME` (core-v0.0.1a0) but never validates that the … | Add a release.yml step asserting the wheel version equals the tag minus the `core-v` prefix. |
| GRK-F14 | MEDIUM | CONFIRMED | packet:L257 | [S5] [S15] `release.yml` has no runner and no `permissions: contents: write`. GitHub documents that new … | Use `ubuntu-24.04`, contents:write on the release job only, `--wheel --no-sources`, and an assertion tha… |
| GRK-F15 | MEDIUM | PLAUSIBLE | packet:L253 | [S4] `uv pip install` of both wheels plus pytest, with no `--no-index`, can ask PyPI for `chat-extractio… | Install the core wheel, then the app wheel with `--no-index --find-links`, then install pytest from the … |
| GRK-F20 | MEDIUM | CONFIRMED | packet:L245 | [S4] [S11] [S13] [S15] S7 bans floating tags and wants pins "at least two weeks old", but B3 pins "exact… | Pin checkout, setup-uv, and uv `0.12.11` by commit SHA or an immutable uv version. Call the actionlint b… |
| KIM-F12 | MEDIUM | PLAUSIBLE | packet:L254 | [S4] The wheel job invokes pytest with test paths inside `$GITHUB_WORKSPACE`, so pytest's rootdir become… | Specify the root pytest config in Task 1 (register marker `installed`, no `pythonpath`, no coverage addo… |
| DSK-F20 | LOW | CONFIRMED | packet:L247 | [S4] ci.yml specifies no job `timeout-minutes` and no uv/cache pinning; defaults (6h timeout, no explici… | Set `timeout-minutes` and enable setup-uv caching. |
| KIM-F20 | LOW | CONFIRMED | packet:L257 | [S5] release.yml has no guard that ci.yml was green on the tagged SHA; the manual ordering in Task 7 Ste… | Add a step that queries check-runs for the tagged SHA (`gh api`) and fails the release unless ci.yml suc… |
| KIM-F22 | LOW | PLAUSIBLE | packet:L261 | [S4] `uvx actionlint` assumes a working PyPI distribution of actionlint, which is a Go tool; availabilit… | Name the fallback explicitly (e.g. `brew install actionlint` or download the pinned release binary) or a… |
| ASP-F35 | INFO | CONFIRMED | Trusted Publishing applicability | **[S5, S15] PyPI Trusted Publishing is not required by this release destination.** It authenticates publ… | Record it as outside the current destination’s requirements. Revisit Trusted Publishing if PyPI distribu… |
| AST-F38 | INFO | CONFIRMED | packet:L257 | [S5,S13,S15] Release hashes are not independent provenance; current immutability/attestation options des… | Record whether immutable draft-then-publish releases, build provenance and SBOMs are enabled or deferred… |
| DSK-F23 | INFO | PLAUSIBLE | packet:L257 | [S13] Trusted Publishing (no PyPI) is correctly not used, but the published wheel has no SBOM/SLSA prove… | Optionally add provenance attestation to release assets. |
| KIM-F30 | INFO | PLAUSIBLE | packet:L257 | [S15] Supply-chain upgrades the packet could note for later phases without changing P0: GitHub artifact … | Optional: add a one-line note to Task 6 that attestation/SBOM are deferred candidates; verify dependency… |

### packet: Task 7: Remote, first green run, recorded evidence  **convergence** (11 findings, 6 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| AST-F22 | BLOCKER | CONFIRMED | packet:L276 | [S5,S9] The packet permits publishing bytes that have never passed the installed-wheel tests. | Keep G-E's tagged-tree rebuild but run the required installed-wheel checks on that exact release artifac… |
| AST-F26 | HIGH | CONFIRMED | packet:L270–272 | [S6,S10,S13] The proposed private release is not reachable by dNh's workflow token by default, and no al… | Resolve private-asset access under separate dNh authority using a scoped credential or approved artifact… |
| AST-F30 | HIGH | CONFIRMED | packet:L274 | [S9,S12] X1's recorded run cannot simultaneously be the final-commit run and its predecessor as instruct… | Define tested_sha, record_commit_sha, immutable run ID/attempt/URL and release_tag_sha separately, selec… |
| ARG-F18 | MEDIUM | CONFIRMED | packet:L276 | [S5] Task 7 Step 5 (`packet:L276`) states that `wheel-tests` wheel sha256 and `release.yml` wheel sha256… | Set `SOURCE_DATE_EPOCH: ${{ github.event.head_commit.timestamp }}` (or `git log -1 --format=%ct`) in bot… |
| ARG-F21 | MEDIUM | CONFIRMED | packet:L274 | [S9] Task 7 Step 3 (`packet:L274`) records the CI run URL in `docs/p0-exit-record.md` for commit $N$, th… | Sequence Task 7 cleanly: (1) commit `docs/release-notes/core-v0.0.1a0.md` before tagging, (2) push and w… |
| DSK-F09 | MEDIUM | PLAUSIBLE | packet:L276 | [S5] Task 7 Step 5 says CI and release wheel digests are "expected to match", but Python wheels are not … | State the release asset SHA256SUMS is authoritative and CI's digest is advisory; optionally set SOURCE_D… |
| DSK-F11 | MEDIUM | CONFIRMED | packet:L276 | [S5] Nothing enforces that the tag is pushed only after ci.yml is green; tag pushes bypass branch protec… | Add a release.yml guard (or environment protection) requiring green CI for the tagged commit. |
| GRK-F23 | MEDIUM | CONFIRMED | packet:L274 | [S9] [S12] X1 says `gh run list` succeeds "for the exact commit", while Task 7 Step 3 stores the URL of … | X1 names both SHAs and requires both runs green. Approving the packet adopts `docs/p0-exit-record.md` on… |
| KIM-F13 | MEDIUM | PLAUSIBLE | packet:L276 | [S5] "They are expected to match" (wheel-tests digest vs release-asset digest) is likely false: wheel zi… | Drop "expected to match", or set `SOURCE_DATE_EPOCH` in both build jobs and make reproducibility an expl… |
| KIM-F17 | MEDIUM | CONFIRMED | packet:L277 | [S9] The final resting place for the acceptance rows' State values is unnamed: X3/X4 stay NOT_RUN "until… | Name the sink per row: e.g. the packet's acceptance table holds final X/S/G states, p0-exit-record.md ho… |
| ASP-F36 | INFO | UNKNOWN | Optional SBOM and artifact attestation | **[S5, S13, S15] Stronger provenance is useful but its availability is unverified and it is not an accep… | Explicitly defer these optional additions or confirm repository-plan eligibility and define their subjec… |

### packet: Builder decisions (spec §11 items P0 touches; values are `proposed` unless marked **decided** — B4 core version and B9 were decided by the owner on 2026-10-22)  **convergence** (8 findings, 5 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F09 | HIGH | CONFIRMED | packet:L292 | [S4][S13] B8 (`packet:L292`) proposes running `pip-audit` via `uv export --frozen --all-packages --no-em… | Specify `uv export --frozen --all-packages --no-dev --no-emit-workspace --no-hashes -o "$RUNNER_TEMP/req… |
| GRK-F09 | HIGH | CONFIRMED | packet:L294 | [S6] [S13] B14 proposes a private repo. GitHub's release-asset API serves public resources without auth;… | Choose public, or name a fine-grained credential in dNh with contents:read on chatstack and download wit… |
| GRK-F11 | HIGH | PLAUSIBLE | packet:L292 | [S4] [S13] [S15] B8's flags exist in current pip-audit help: `--requirement`, `--no-deps`, and `--disabl… | On the pinned pip-audit, if import still needs pip, install pip in that job before the audit. Keep "veri… |
| KIM-F04 | HIGH | CONFIRMED | packet:L298 | [S6][S13] B14 proposes a private remote, but X4's mechanism — dNh's CI installing the wheel from the `co… | Decide visibility before approval; if private, specify a dNh-side secret (PAT or GitHub App token) and a… |
| AST-F18 | MEDIUM | CONFIRMED | packet:L292 | [S4,S13,S15] G5 lacks a retained audit input, package-count invariant and explicit collection/network-fa… | Save the export and audit report, record service/tool versions and included groups, assert expected pack… |
| DSK-F10 | MEDIUM | PLAUSIBLE | packet:L292 | [S4] B8's `uv export --frozen --all-packages --no-emit-workspace` hits a documented uv bug where `--all-… | Verify on uv 0.12.11 and fall back to `--no-emit-project` or a filtered export. |
| KIM-F21 | LOW | PLAUSIBLE | packet:L292 | [S4][S15] B8's `pip-audit --requirement -` stdin form may not be accepted (pip-audit's `-r` expects a pa… | Keep the hedge; smoke the exact pipeline once locally before Task 6 and adjust to a temp file if stdin f… |
| DSK-F22 | INFO | CONFIRMED | packet:L296 | [S12] G-F remains partially open: remote name DDD-Enterprises/chatstack and private visibility are propo… | Get explicit owner confirmation of name/visibility in the pre-approval checklist. |

### packet: Gaps and contradictions found in the spec  **convergence** (7 findings, 5 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| GRK-F10 | HIGH | CONFIRMED | packet:L310 | [S3] [S10] [S14] G-A and spec §14 allow an `errors.py`, a schema loader, and an app map of `E_GATE_MISMA… | Amend the §14 parenthetical so it names `sqlite_floor.py` and the §3.12 map, or delete them from P0. Say… |
| AST-F29 | MEDIUM | CONFIRMED | packet:L312 | [S12,S14] G-C remains an unresolved rewrite-versus-absence contract, with an inaccurate workflow-path pr… | Record a canonical decision that fresh ci.yml replaces the legacy gates and both old filenames stay abse… |
| ARG-F25 | LOW | CONFIRMED | packet:L312 | [S8][S12] Gap G-C (`packet:L312`) notes `spec:L728` names `config/arch-gates.yml` while `spec:L871` name… | Add a single sign-off line at the top of the Builder decisions table (`packet:L280`) stating that owner … |
| GRK-F26 | LOW | CONFIRMED | packet:L312 | [S12] G-C says spec L871 puts `arch-gates.yml` under workflows. L871 names the file with no directory. T… | Correct the G-C sentence. Also require `git ls-files` to show no path containing `arch-gates`. Do not po… |
| AST-F40 | INFO | CONFIRMED | packet:L313 | [S1,S6,S15] The external-workspace source form is documented and should not be rejected merely because d… | Retain both X3 experiments under dNh authority, record the actual consumer uv version and each lock/orig… |
| DSK-F21 | INFO | CONFIRMED | packet:L312,S5 | [S12] G-C is resolved by S5 asserting both `config/arch-gates.yml` and `.github/workflows/arch-gates.yml… | Cite the exact source path in S5. |
| KIM-F27 | INFO | CONFIRMED | packet:L313 | [S1][S6][S15] The cross-workspace form dNh is asked to try is documented by uv independently of the prio… | None; keep Stop S6. |

### packet: Scope items (§6 P0 Scope cell, not exit criteria; each still needs evidence)  **convergence** (6 findings, 5 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F25 | MEDIUM | CONFIRMED | S10; Task 2 design copy | **[S8, S14] Copy-time equality does not bind the copy to the approved input.** Hashing the current sourc… | Compare both source and copy against the approved design hash in the supplied manifest. Stop on mismatch… |
| ASP-F27 | MEDIUM | CONFIRMED | S5; G-C; fresh architecture configuration | **[S8, S12, S14] G-C does not yet resolve whether a fresh architecture configuration exists.** S5 requir… | Record one explicit G-C interpretation and align the scaffold and acceptance check: either a newly autho… |
| AST-F32 | MEDIUM | CONFIRMED | packet:L88–108 | [S8,S9] Evidence collection is incomplete for the full acceptance matrix. | Create the exit record with every X1–X5, S1–S10 and G1–G6 row mapped to command, SHA, artifact, result a… |
| GRK-F22 | MEDIUM | CONFIRMED | packet:L98 | [S8] [S10] S10 says the copy's hash equals the source at copy time and does not pin `60527809…`. A later… | Put the audited sha256 in S10 and stop on mismatch. Create `docs/p0-exit-record.md` in Task 2 Step 1. |
| DSK-F17 | LOW | CONFIRMED | packet:L97,L173 | [S8] S10's check text says `sha256sum` while Task 2 Step 1 uses `shasum -a 256`; the macOS host has `sha… | Use `shasum -a 256` consistently on the macOS host. |
| KIM-F23 | LOW | CONFIRMED | packet:L92 | [S8] S5's `test ! -e .github/workflows/arch-gates.yml` checks are vacuous in a repository created by `gi… | Reword S5 so the git-log authorship check is primary and the `test ! -e` checks are listed as belt-and-b… |

### packet: Task 5: Local gates, lock, pre-commit, sqlite_version recording  **convergence** (6 findings, 4 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F12 | HIGH | CONFIRMED | packet:L234 | [S1][S4] Task 5 Step 1 runs `uv run mypy --strict packages/chat-extraction-core/src` and `uv run mypy ap… | Add `uv sync --all-packages --locked` to Task 5 Step 1 immediately after `uv lock --check` and before ru… |
| AST-F15 | HIGH | CONFIRMED | packet:L232–236 | [S7,S9] Local SQLite evidence is not bound to the interpreter that can import the core and run the tests. | Run the recorder through the same explicit environment interpreter as pytest locally and in CI, recordin… |
| AST-F34 | MEDIUM | CONFIRMED | packet:L235 | [S4,S8] Pre-commit's pinned root dependency is bypassed and its bootstrap is underspecified. | Provide valid initial hook definitions, invoke the locked pre-commit tool, verify approved immutable rev… |
| KIM-F11 | MEDIUM | CONFIRMED | packet:L236 | [S7] Task 5 Step 3 runs bare `python scripts/record_sqlite_version.py`, but the script imports `chat_ext… | Change the command to `uv run python scripts/record_sqlite_version.py`. |
| KIM-F16 | MEDIUM | CONFIRMED | packet:L235 | [S10][S13] Pre-commit hook revs are sourced from `uvx pre-commit autoupdate`, which floats to the newest… | Pin hook revs by hand, record each rev's release date in the commit message, and drop autoupdate from th… |
| GRK-F27 | LOW | CONFIRMED | packet:L235 | [S8] [S13] Pre-commit revisions come from `uvx pre-commit autoupdate`, which tracks latest, against S7's… | Pin hook revs that are two weeks old. Run ruff and `uv lock --check` as local hooks that call the projec… |

### packet: File structure (created by this packet)  **convergence** (4 findings, 3 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F09 | HIGH | PLAUSIBLE | Combined installed-wheel pytest invocation | **[S4, S15] Duplicate bare test-module names can prevent collection.** Both packages contain `test_failu… | Specify `--import-mode=importlib` or another demonstrated collision-free arrangement. Collect both direc… |
| AST-F07 | HIGH | CONFIRMED | packet:L135–139 | [S4,S9] Both test directories contain identical module basenames without a defined collision-free import… | Require --import-mode=importlib consistently for combined collection and execution, and verify both pack… |
| ASP-F06 | MEDIUM | CONFIRMED | Task 1; B2 | **[S1, S2, S15] The root Python constraint is assigned to an undefined metadata location.** Task 1 reque… | Keep the chosen virtual-root design and put `requires-python = ">=3.12"` in each member’s `[project]`. S… |
| DSK-F16 | LOW | CONFIRMED | packet:L140 | [S5] `docs/release-notes/` is used by Task 7 Step 5 but absent from the file-structure listing (docs/ sh… | Add `docs/release-notes/` to the structure listing. |

### packet: Global Constraints (verbatim from the spec)  **convergence** (3 findings, 3 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F08 | MEDIUM | CONFIRMED | Package payload; licenses and notices | **[S2, S8, S15] Source-tree scaffolding does not prove the required wheel contents.** The packet require… | Define and inspect the expected payload of each wheel, including license/notice material, `py.typed`, an… |
| GRK-F29 | LOW | CONFIRMED | packet:L41 | [S14] Several line cites are off by about one. App bounds are spec L161; packet L41 cites L162, and L162… | Correct those citations to L161, L149, L144, and L852–854. |
| KIM-F18 | LOW | CONFIRMED | packet:L45 | [S14] The coverage global-constraint cites "(line 841–843)", which is §5 contracts 3–4 (id stability, pr… | Correct the citation to spec lines 852–854 / 888. |

### packet: Global gates that apply at P0 (§7, spec lines 885–922)  **convergence** (7 findings, 3 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F04 | HIGH | CONFIRMED | Task 6 fresh-venv installation | **[S1, S4, S13] The wheel-test environment escapes the dependency lock.** Installing the two wheel paths… | Install the selected, fully pinned and hashed third-party closure into the fresh venv, then install the … |
| ASP-F13 | HIGH | CONFIRMED | G3; coverage acceptance | **[S4, S9, S15] The command does not independently enforce 90% line coverage.** With branch measurement … | Retain branch measurement and the existing aggregate threshold, and add an explicit statement-coverage c… |
| AST-F09 | HIGH | CONFIRMED | packet:L104 | [S4,S9] The app's strict mypy configuration is not selected by its root-level command. | Pass --config-file apps/chatx/pyproject.toml or place the strict app configuration in the selected root … |
| ASP-F12 | MEDIUM | PLAUSIBLE | G2; root invocation; app mypy settings | **[S4, S15] Strict checking of the app is not guaranteed by the shown command.** Core is checked with `-… | Use explicit `--strict` for both commands, or explicitly select a configuration that provides the requir… |
| ASP-F16 | MEDIUM | CONFIRMED | G5; B8 audit invocation | **[S4, S13, S15] Audit completeness and evidence remain undefined.** B8 still asks the builder to valida… | Resolve the invocation against pinned tools, export to a retained file, and verify its expected package … |
| GRK-F16 | MEDIUM | CONFIRMED | packet:L105 | [S8] [S14] §7 says "no omit list". §5 L853 says "no omit beyond `tests/`". The revision plan T21 said "n… | Do not set `omit`. Point coverage `source` at the two import packages. Correct the citation to L852–854 … |
| GRK-F17 | MEDIUM | CONFIRMED | packet:L110 | [S3] [S14] Spec §3.3 requires two tests, an import-graph test and a socket guard, as the enforcement of … | Add those two tests in P0. They do not add product modules. Name them in the G-A allowance so S5 does no… |

### packet: Out of scope  **convergence** (3 findings, 3 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ARG-F05 | BLOCKER | CONFIRMED | packet:L66 | [S14] Out-of-scope bullet 7 (`packet:L66`) states `whether P0 cuts one [a core-vX.Y.Z tag] is UNKNOWN (s… | Remove the stale `UNKNOWN` claim at `packet:L66` and update `packet:L55` and `packet:L78` to quote `spec… |
| GRK-F03 | HIGH | CONFIRMED | packet:L66 | [S5] [S10] [S14] Cutting the tag is out of scope and "UNKNOWN" (L66), required by Task 7 and §14, and st… | Delete the UNKNOWN sentence. State that §14 waives the L144 adapter run for `core-v0.0.1a0` only, that t… |
| ASP-F33 | INFO | CONFIRMED | Minimal failure stubs and proof boundary | **[S3, S10, S14] The authorised stub scope is coherent, but its proof must be named accurately.** Except… | Retain the approved stubs and report their assertions as stub-level evidence. Do not expand P0 into a re… |

### packet: Scope  **convergence** (3 findings, 3 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F26 | MEDIUM | CONFIRMED | Scope quotes; G-A/G-B/G-E propagation | **[S3, S5, S14] Several operative paragraphs predate the accepted decisions.** The purported verbatim sc… | Replace stale text with the existing decisions: the exact authorised stubs, gate mismatch exit 3, schema… |
| AST-F03 | MEDIUM | CONFIRMED | packet:L56–78 | [S5,S14] Several operative sections retain superseded decisions. | Refresh the quoted exit rows, scope exclusions and resolved-gap prose from rev 2.1 and mark B4's core ve… |
| DSK-F05 | MEDIUM | CONFIRMED | packet:L56,L78 | [S14] X1 and the Scope exit quote carry the stale rev-2 wording "exit 3, E_GATE_MISMATCH, E_SCHEMA_MISSI… | Update both quotes to the rev 2.1 wording. |

### packet: Task 2: Design document, ADR template, conformance skeleton (2 findings, 2 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| AST-F31 | HIGH | CONFIRMED | packet:L173 | [S8,S9,S14] The design-copy check accepts a moving source instead of the approved snapshot. | Bind the copy to that approved revision/hash, fail on any source drift, and require an explicit new appr… |
| KIM-F24 | LOW | CONFIRMED | packet:L173 | [S8][S14] Task 2 copies the live spec and only verifies copy equals source at copy time; nothing pins th… | Add an assertion that the source hash equals the recorded rev 2.1 sha256 before copying; FAIL (stop) on … |

### dNh (1 findings, 1 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| DSK-F24 | INFO | CONFIRMED | dnh:pyproject.toml:112 | [S15] dNh duplicates its dev deps in both `[dependency-groups]` and `[project.optional-dependencies]` (l… | Use a single dependency-group in chatstack; do not copy the duplication. |

### other: spec:L728 (1 findings, 1 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| KIM-F14 | MEDIUM | CONFIRMED | spec:L728 | [S12][S14] G-C residual: spec L728 says `config/arch-gates.yml` and `.github/workflows/*` "are rewritten… | Next spec rev: reword L728 to "`.github/workflows/*` rewritten in P0; `config/arch-gates.yml` not carrie… |

### other: spec:L869–871 (1 findings, 1 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| AST-F02 | HIGH | CONFIRMED | spec:L869–871 | [S9,S10,S14] The frozen spec still makes X3/X4 mandatory P0 exits, whereas this audit brief explicitly e… | Record the owner's newer exclusion in the canonical phase contract and distinguish ChatX completion from… |

### packet: Inputs (spec line ranges actually read) (1 findings, 1 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| ASP-F20 | MEDIUM | UNKNOWN | X3 external-workspace proof | **[S1, S6, S15] The external-workspace syntax is documented today, but acceptance on uv 0.12.11 is unver… | After separate authority, exercise each source form independently with uv `0.12.11`, fresh consumer envi… |

### packet: Review Focus (1 findings, 1 auditors)

| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |
|---|---|---|---|---|---|
| DSK-F19 | LOW | CONFIRMED | packet:L304 | [S7] `meets_floor` parses 3-part versions only; 4-part strings (e.g. 3.51.3.x) are unhandled and the par… | Have `meets_floor` define or reject 4-part strings and add a test. |

## Decision challenges

- **argon**: **DECISION CHALLENGE 1 (G-E / Spec §3.2 vs B14 Private Repo Visibility for Cross-Repo Wheel Consumption in X4):**
- **argon**: *Argument:* Owner decision G-E (`PROMPT-master.md:L29`, `spec:L1201`) requires `release.yml` to publish the `core-v0.0.1a0` wheel to GitHub Releases on `chatstack` and requires dNh's CI (X4) to install that pinned wheel by version and sha256. Simultaneously, `packet:L298` (B14) proposes creating `DDD-Enterprises/chatstack` as a **private** GitHub repository. When `dNh_CRM` runs its GitHub Actions workflow (`bundle:.github/workflows/ci.yml`), its default `GITHUB_TOKEN` is scoped strictly to `dNh_CRM` and cannot download release assets from a private sibling repository (`DDD-Enterprises/chatstack`). Furthermore, `uv` downloading a direct wheel URL from a private GitHub release asset (`https://github.com/DDD-Enterprises/chatstack/releases/download/...`) requires either a cross-repo fine-grained PAT configured in dNh's GitHub Secrets (`UV_EXTRA_INDEX_URL` / basic auth or `gh release download` pre-step) or `DDD-Enterprises/chatstack` being public (since `chat-extraction-core` is MIT-licensed and contains zero owner data or secrets), or committing the wheel into a local directory/find-links on the dNh test branch.
- **argon**: *Cost of being wrong either way:* If `DDD-Enterprises/chatstack` is created private and no cross-repo token/vendoring mechanism is specified, X4 will fail in dNh CI with HTTP 404/401 on the release URL, blocking P0 exit or forcing ad-hoc secret creation in dNh_CRM (which violates Stop S2 / separate governance). Conversely, making `DDD-Enterprises/chatstack` public exposes the architecture design doc (`docs/design/2026-10-20-chatx-rearchitecture-design.md`) if copied into the repo per S10.
- **argon**: *What evidence would settle it:* An owner decision before Task 7 starts choosing between: (a) keeping `DDD-Enterprises/chatstack` private and having the dNh dev branch download the release asset via a pre-existing org token or commit the `core-v0.0.1a0` wheel + `SHA256SUMS` into a temporary `vendor/` dir on the dNh dev branch for `--find-links`, or (b) configuring a scoped read-only deploy key / PAT in dNh_CRM under dNh authority.
- **argon**: **DECISION CHALLENGE 2 (Spec §3.2 / X3 `{ workspace = "../chatstack" }` Cross-Workspace Source Syntax):**
- **argon**: *Argument:* Spec §3.2 (`spec:L147`) and packet X3 (`packet:L80`, `L119`) assert that `dNh_CRM` (which is **not** a member of `/Users/hue/code/chatstack/pyproject.toml`'s `[tool.uv.workspace] members`) can declare `chat-extraction-core = { workspace = "../chatstack" }` in `[tool.uv.sources]`, citing internal audit row E8. In `uv`'s documented workspace model (through early 2026), `[tool.uv.sources]` accepts `workspace = true` (a boolean, valid only for packages inside the same workspace) and `path = "../chatstack/packages/chat-extraction-core"` for relative path dependencies across workspaces. While `uv` between March 2026 and `0.12.11` (September 2026) may have added `workspace = "<path>"` as E8 claims, the packet itself acknowledges uncertainty by adding Stop S6 (`packet:L324`: "the uv version pinned for the build rejects `{ workspace = "../chatstack" }`").
- **argon**: *Cost of being wrong either way:* If `uv 0.12.11` rejects `workspace = "../chatstack"` (expecting a boolean), waiting until X3 (after Task 7) to discover this means P0 completes all 7 tasks and cuts a release tag only to fail its exit criterion X3 on a spec syntax error. If `uv 0.12.11` supports it, the cost of checking it in Task 1 Step 1 is 10 seconds.
- **argon**: *What evidence would settle it:* Running a 2-directory scratch test with `uv 0.12.11` during Pre-Approval (Check `ARG-C01` in Output B) before approving the packet.
- **astra**: **DECISION CHALLENGE — decision 5, downstream exit exclusion (AST-F02).** The latest owner instruction excludes X3/X4 from ChatX exit criteria, so this audit honors that boundary. However, the frozen spec still requires their PASS. Approving local P0 without a separately named downstream status risks representing installation compatibility as proven; retaining them as implicit blockers would make ChatX wait on authority it does not hold. Settle this with an owner-recorded canonical amendment defining local P0 completion and downstream integration pending, with X3/X4 remaining NOT_RUN until evidenced.
- **astra**: **DECISION CHALLENGE — proposed B14 private distribution, not an already-decided visibility change (AST-F26).** Private GitHub assets require a consumer access route beyond assuming dNh's repository token can read chatstack. Keeping privacy without that route leaves X4 unusable; making the repository public merely to avoid authentication would expose material without authority. Settle this with the owner's visibility decision and a separately authorized dNh download/credential or artifact-delivery design; do not silently change visibility.
- **grok**: **DECISION CHALLENGE — G-E, tag `core-v0.0.1a0` now.** Argument: spec L144 still says the core's CI runs dNh's adapter tests before a tag. §14 waives that step for this tag only and does not change L144. dNh's tree has no adapter, so the waived step is an honest NOT_RUN, not a hidden PASS. Cost of tagging now: the tag is immutable, the wheel is a stub with pydantic and phonenumbers and no parsers, and a later real consumer must not reuse `0.0.1a0`. Cost of not tagging: X4 has no bytes to pin, and the §6 exit row cannot pass. What settles it: the owner writes, in the packet, that this tag is a packaging pin only, that dNh must not merge the branch, and that the first tag any adapter imports will be a new version after those tests are PASS. GRK-F03 is the packet edit either way.

---
Generated: 2026-10-22T18:42:32Z

Input SHA256SUMS:

```
605278090866f493184cf1d019cc030d934bb64d9e9b04ad7100a2eaadf54076  2026-10-20-chatx-rearchitecture-design.md
f5b20b0a711c1b27b86fbfe3f6275ad32cec1584ad4b461b28c19a607559baaa  2026-10-21-next-steps.md
38d0f84d5606c4cd62d360bf435ff04d0f7e1845e90d37c8f3c8ad5a6e7302dd  2026-10-21-p0-workspace-packet.md
```
