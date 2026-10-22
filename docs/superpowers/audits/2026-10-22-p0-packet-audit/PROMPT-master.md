# ChatX P0 "Workspace" Packet — External Audit Brief

Date: 2026-10-22 · Pack version: 1 · The packet's author is **not** available to you.

## Your role

You are an independent, principal-level reviewer with deep experience in: Python packaging (uv workspaces, PEP 517/518/621/440/735, wheels, lockfiles), GitHub Actions and supply-chain hygiene, release engineering, SQLite deployment on macOS and Linux, and running engineering plans that other agents execute. You are auditing an **implementation packet** (a task-by-task plan that a builder agent will execute) against the **design document it implements** and against **one real downstream repository** (dNh_CRM) that must consume the result.

You produce two deliverables: **(A) an audit report** with findings, and **(B) a pre-approval checklist** — the concrete checks the owner should run or decide before approving the packet or before Task 1 starts. Depth is the point. Read the packet line by line; read the spec sections it cites; read the dNh files it makes claims about.

## Inputs

| Item | Where |
|---|---|
| Packet under audit | `inputs/2026-10-21-p0-workspace-packet.md` (336 lines; copy of `docs/superpowers/plans/…` at ChatX commit `cc18536`) |
| Design it implements | `inputs/2026-10-20-chatx-rearchitecture-design.md` — **rev 2.1**, 1,269 lines, sha256 `605278090866f493184cf1d019cc030d934bb64d9e9b04ad7100a2eaadf54076`. P0 is defined by §6 (phase table, line ~871); the release contract is §3.2 (lines ~142–143); exit codes are §3.12; builder decisions are §11; rev 2 → 2.1 changes are the last block of §14 |
| The plan the packet is step S2 of | `inputs/2026-10-21-next-steps.md` |
| dNh_CRM packaging digest | `bundles/dnh-packaging-bundle.md` (`pyproject.toml`, `.python-version`, CI and release workflows, lockfile header) — generated, treat as a lead and verify against the repository if you can reach it |
| Prior audit of the design | `docs/superpowers/audits/2026-10-20-design-audit/out/` in the ChatX repo — `cross-audit-matrix.md`, `design-revision-plan.md`, `builder-check-rev2.md` (context only; do not re-audit the design) |
| Repositories | see **Access** in your wrapper prompt |

`~/code/chatstack` — the repository P0 creates — does not exist yet. Nothing is built. You are auditing the plan, not an implementation.

## Owner decisions already made (audit them; do not silently override them)

1. New repository `~/code/chatstack`, uv workspace, two packages `packages/chat-extraction-core` (MIT) and `apps/chatx`; dNh_CRM stays where it is and consumes the core first by `path`/`workspace` source, later by a pinned wheel (spec §3.2, owner items 1–2).
2. **G-A** (2026-10-22): the two packages may hold exactly the failure-path stubs the packet lists (Tasks 3–4) and nothing more. "Two empty packages" in spec §6 is read with that allowance.
3. **G-B** (2026-10-22): spec §3.12 stands — `E_GATE_MISMATCH` → exit 3, `E_SCHEMA_MISSING` → exit 1. The §6 P0 row was reworded in rev 2.1.
4. **G-E** (2026-10-22): P0 ends by tagging `core-v0.0.1a0`; a `release` workflow builds the core wheel from the tagged tree and publishes it with `SHA256SUMS` as a GitHub pre-release; dNh pins that version and digest. The core's starting version is therefore `0.0.1a0`. The adapter-test step the release contract wants before a tag has nothing to run at P0 and is recorded NOT_RUN.
5. The packet is DRAFT. Nothing executes until the owner approves it. Pushing, creating the remote, and tagging need owner authority (packet Stop S1). dNh-side checks (packet X3, X4) need separate dNh authority and are not ChatX exit criteria.

You may challenge any of these. Label such items **DECISION CHALLENGE**, give the argument, the cost of being wrong either way, and what evidence would settle it.

## Ground rules

- **Evidence over fluency.** Every finding cites its location: `packet:L<line>` or `packet:<section>`, `spec:§x.y` or `spec:L<line>`, `dnh:<path>:<line>`, `bundle:<section>`. Findings without a citation go in a separate "unverified impressions" list.
- **Verdicts:** `CONFIRMED` (you read the text/code and it is so), `PLAUSIBLE` (reasoned, not verified), `UNKNOWN` (could not check). Never upgrade PLAUSIBLE to CONFIRMED by repetition.
- **Never invent** uv/pip/GitHub Actions flags, action versions, PEP numbers, SQLite version numbers, model ids, or tool behaviours. When you rely on a tool behaviour, state your confidence and exactly what the builder must verify before depending on it.
- **Severity is about the packet's fitness to execute**, not about the design. BLOCKER = a builder following the packet as written would produce a wrong, unsafe, or unverifiable result, or would need authority the packet does not grant. HIGH = a task or exit criterion cannot be completed or measured as written. MEDIUM = ambiguity that two builders would resolve differently. LOW = wording, ordering, cost. INFO = note.
- **Do not modify any file** in either repository. Write only to the output location in your wrapper prompt.
- **State your knowledge cutoff** and flag anywhere the packet may rely on tool behaviour that has changed since (uv, GitHub Actions, PyPI) — as PLAUSIBLE unless you verified it.
- You are auditing, not rewriting. Propose each change as a finding with a concrete fix, not as a replacement packet.

## Scope — audit every item, in depth

1. **Workspace semantics.** `[tool.uv.workspace] members`, the `path` vs `workspace` source forms dNh is asked to try (X3), `uv lock --check`, `uv sync` from a clean clone, lockfile ownership. Does the packet's structure actually produce what spec §3.2 and §6 require?
2. **Package metadata.** Names, versions (`0.0.1a0` core, `0.0.0` app), PEP 440 pre-release handling by `uv` and `pip` when pinning by exact version, build backend, Python floor vs dNh's `.python-version`, license files, `[project]` completeness for a wheel that will be published as a release asset.
3. **Failure-path stubs and exit codes.** Tasks 3–4 against spec §3.12 and decision G-B: are the stubs minimal, are the tests asserting the right codes, is there any path by which "stubs" grow into product code inside P0?
4. **CI design (`ci.yml`).** Fresh venv outside the checkout, testing the *installed wheel* rather than the source tree, ruff/mypy/pytest/`uv lock --check`/`pip-audit` on near-empty packages (does `pip-audit` behave on an empty dependency set?), OS matrix (macOS arm64 is required for `sqlite_version`), action pinning (tag vs commit SHA), `permissions:` least privilege, caching, uv version pinning, timeouts. Does every step feed an exit criterion?
5. **Release contract (`release.yml`, decision G-E).** Trigger on `core-v*`, `uv build --package`, `SHA256SUMS`, `gh release create --prerelease` with the notes file, permissions needed (`contents: write`), what happens if the tag is pushed before CI is green, whether the wheel's version string will match the tag, reproducibility expectations between the CI wheel digest and the release asset digest (the packet says they are "expected to match" and makes non-matching non-fatal — is that sound?).
6. **Cross-repo (X3, X4).** Read dNh's `pyproject.toml`, `uv.lock`, `.python-version`, `.github/workflows/ci.yml`. Can dNh resolve the core by both `path` and `workspace` forms as the packet claims, given dNh is *not* a member of the chatstack workspace? What does adding a path dependency do to dNh's lockfile and CI? How exactly would dNh's CI "install a pinned wheel" from a GitHub pre-release asset (auth, URL form, hash pinning syntax for uv and for pip)? Is the separate-authority boundary respected?
7. **SQLite floor.** How the packet measures "an interpreter linking SQLite at or above the floor" (spec §3.3/§7 floor; packet exit record): uv-managed Python vs system Python vs Homebrew on macOS, Linux runner images, `sqlite3.sqlite_version` vs `sqlite_version_info`; whether the measurement is taken in the same interpreter that runs the tests.
8. **Scaffolding criteria.** Pre-commit config, ADR template, `conformance.md` skeleton, the design copy and its sha256 (S10): is each one measurable, and does the packet say where the evidence lands?
9. **Exit-criteria measurability.** For every X/S/G row: is there a named artefact or command whose output decides PASS/FAIL, and is NOT_RUN preserved (never collapsed into PASS)? Does `docs/p0-exit-record.md` capture everything the spec's §6 row asks for (CI URL, `sqlite_version`, digests)?
10. **Authority and stop conditions.** Remote creation, visibility, tag push, dNh branch work: does every action that needs owner or dNh authority sit behind a stop? Any step that could silently widen scope (e.g. creating files outside the two packages, adding dependencies)?
11. **Task ordering and delegation.** Dependencies between Tasks 1–7, what can run in parallel, which tasks suit a cheaper builder model and which need the supervisor; are the estimates and call/retry budgets stated; is the "subagent-driven" execution instruction compatible with the stop conditions?
12. **Open gaps G-C and G-F.** G-C: which `arch-gates` file spec L728 means and whether "not carried" is actionable. G-F: where the CI URL is recorded, the remote name, visibility. Propose a resolution for each with the evidence that supports it.
13. **Security and supply chain.** Secrets in workflows (none should be needed except `GITHUB_TOKEN` for the release), network reach of CI steps, pinned action SHAs, `pip-audit` data source, `.gitignore` for venvs/dist, whether anything in P0 could touch owner data (it must not).
14. **Packet ↔ spec consistency after rev 2.1.** Does the packet contradict §3.2, §3.12, §6, §11 or §14 anywhere? Did the rev 2.1 edits (§6 P0 row, §14 block) introduce a contradiction elsewhere in the spec? Is anything in the packet's "Builder decisions" table still marked proposed that the spec actually decides?
15. **Current best practice as of your cutoff.** uv workspace and `uv build` behaviour, PEP 735 dependency groups vs extras, GitHub release asset pinning, Trusted Publishing (not used here — should it be?), SBOM/attestation for the wheel. Each item: confidence, and exactly what the builder must verify.

## Output A — `report-<auditor>.md`

In this order, nothing else:

1. **Reviewer identity block** — four lines: `Model:` (as you know it), `Runner:`, `Knowledge cutoff:`, `Files opened:` (every file you actually read, as paths).
2. **Packet verdict** — one line: `Packet verdict: APPROVE | APPROVE-WITH-CHANGES | DO-NOT-APPROVE`, then one sentence why.
3. **Findings table** — exactly these seven columns, one row per finding, no line breaks inside cells, escape any `|` inside a cell as `\|`:

   `| ID | Severity | Verdict | Where | Finding | Evidence | Fix |`

   - `ID`: `<PREFIX>-F01`, `<PREFIX>-F02`, … (your prefix is in your wrapper prompt).
   - `Severity`: `BLOCKER` / `HIGH` / `MEDIUM` / `LOW` / `INFO`.
   - `Verdict`: `CONFIRMED` / `PLAUSIBLE` / `UNKNOWN`.
   - `Where`: the primary citation in the forms above (`packet:L123`, `spec:§3.12`, `dnh:pyproject.toml:14`).
   - `Finding`: what is wrong or missing, in one or two sentences.
   - `Evidence`: what you read that shows it (quote ≤ 20 words if useful).
   - `Fix`: the concrete change to the packet (or spec), one sentence.

   Aim for completeness over count; 15–40 rows is typical. Put the scope-area number in the Finding text as `[S4]` etc.
4. **Decision challenges** — `DECISION CHALLENGE` items as a bullet list (argument, cost of being wrong either way, what would settle it). "None" if none.
5. **Unverified impressions** — bullet list of things you suspect but could not cite. "None" if none.

## Output B — `preapproval-<auditor>.md`

A single table the owner can work through before approving:

`| ID | Check | How to verify | Blocking? |`

- `ID`: `<PREFIX>-C01`, … ; `Check`: one sentence; `How to verify`: a command, a file to open, or a question to answer, concrete enough to run; `Blocking?`: `yes` if approval should wait for it, `no` otherwise.
- After the table, a short section **What I could not check** (tools, repos or facts you lacked).

## Delivery

Your wrapper prompt names the output directory and files. Whether or not you can write files, your **final message must end** with both deliverables printed in full, each preceded by a line `=== FILE: <filename> ===`, and the whole block closed with a line `=== END ===`. Print nothing after `=== END ===`.
