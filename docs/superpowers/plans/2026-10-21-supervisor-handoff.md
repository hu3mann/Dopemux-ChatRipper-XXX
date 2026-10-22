# Supervisor handoff — ChatX re-architecture, 2026-10-21 (end of session)

Written by the Fable 5.1 supervisor session that followed design rev 2. Read this,
then `2026-10-21-next-steps.md`. Owner decisions are in §4; nothing here authorises
executing them.

## 1. Repo state at handoff

| Repo | Branch | HEAD | Upstream | Notes |
|---|---|---|---|---|
| `Dopemux-ChatRipperXXX` | `governance-doctrine-integration` | `3fb80e6` | origin, **ahead 1 (unpushed)** | `3fb80e6` adds the four docs in §2; `e3e59ed` (pushed) holds design rev 2 and the audit. Tracked edits to `.gitignore` and `AGENTS.md` pre-date this session. `node_modules/*` deletions in `git status` are build residue, not work. |
| `dNh_CRM` | `migrate-cheaperinference` | `e8bbcadb` | origin, in sync | `721cb585` recovered 9 instruction/config files lost with the 2026-10-21 checkout deletion; `e8bbcadb` rebuilt `.claude/WORKTREE_MCP_SETUP.md` from HEAD plus the dopemux MCP block (blob `0821d485` verified). Per-file recovery table: `/Users/hue/code/dNh_CRM.restore-review-20261021/README.md` (plain folder, not a repo; delete when satisfied). |

Time Machine has **no destination configured** (`tmutil destinationinfo` → none). Nothing
outside git is backed up. Fix before P0.5 touches real data.

## 2. Artifacts (paths under `docs/superpowers/` unless stated)

| Artifact | State | Purpose |
|---|---|---|
| `specs/2026-10-20-chatx-rearchitecture-design.md` | rev 2, 1,261 lines, sha256 `96ef71cf…3527` | The design. Single source of truth. Edits only as owner-approved changes with a §14 change-log entry. |
| `audits/2026-10-20-design-audit/` | complete | Multi-model audit. `out/research-targets-supervisor.md` is the RT status source; `out/external-fact-check.md` holds E-rows (E8 = uv cross-workspace `workspace = "<path>"` form, SUPPORTED). |
| `plans/2026-10-21-next-steps.md` | proposal | Sequence S0–S6. Owner chose options c, d (research prompt + P0 packet) this session. |
| `research/2026-10-21-rt-desk-research/README.md`, `PROMPT-chatgpt-web.md` | drafted, **NOT RUN** | 14 RT targets for ChatGPT web (Astra Pro). Outputs → `out/research-rt-chatgpt-web.md`, `out/research-rt-sources.md`; then sonnet-verify → `out/claim-verification-research.md`. |
| `plans/2026-10-21-p0-workspace-packet.md` | draft, not executable | 7 tasks, exit criteria X1–X5, gaps G-A…G-F, stops S1–S9, builder proposals B1–B9. Blocked on §4 items 3–4. |
| `~/Downloads/chatx-rt-desk-research-inputs-20261021.zip` | built | Flat copy of spec, prompt, README, RT status, `MANIFEST.sha256`, `README-INPUTS.txt` for the ChatGPT session. |

## 3. Delegation record (cost-first policy)

| Subtask | Requested model / effort | Observed | Outcome |
|---|---|---|---|
| Draft research prompt | sonnet / medium (Agent) | UNKNOWN (no runtime receipt) | Four "Design today" lines contradicted the spec (RT-2, RT-10, RT-14, RT-17). Fixed by supervisor. |
| Draft P0 packet | sonnet / medium (Agent) | UNKNOWN | Claimed E8 unread and treated the spec's `{ workspace = "../chatstack" }` as doubtful; the audit had already verified it. G-D, S6, X3, Inputs fixed by supervisor. |
| Review, synthesis, commits | this session (Fable 5.1) | self | — |

Lesson: Sonnet drafts of spec-grounded documents were sound in structure and wrong in
exactly the lines that restate the spec. Keep a line-level check of every "the design
says" sentence with the supervisor; do not delegate that check to the drafter.

## 4. Owner decisions pending, in order

1. **Push** `3fb80e6` (`git -C ~/code/Dopemux-ChatRipperXXX push`). Ask-gated.
2. **Run the research prompt** (S1): attach the design from the zip, paste the prompt
   from its `---` line, save the two outputs into `research/2026-10-21-rt-desk-research/out/`.
3. **Rule on packet gaps G-A, G-B, G-E** (§5 has the options and a recommendation).
4. **Authority for P0 execution**: create `~/code/chatstack` and remote
   `DDD-Enterprises/chatstack` (packet stop S1); any dNh dev branch for X3/X4 is under
   dNh's own governance (packet stop S2).
5. **Backups**: configure a Time Machine destination (or equivalent) — see §1.

## 5. The three packet gaps, with a recommendation (supervisor opinion, not authority)

**G-A — "two empty packages" vs failure-path stubs in CI.** The §6 P0 row (spec line 871)
says the packages are empty and also that the first green CI run includes failure-path
tests for `E_GATE_MISMATCH` and `E_SCHEMA_MISSING`. An empty package cannot emit an
error code, so one of the two must give.
Options: (a) allow minimal stubs — an `errors.py` and a resource loader in the core that
raise `E_SCHEMA_MISSING` when the schema resource is absent, and an app entry point
that maps `E_GATE_MISMATCH` to exit 3 (packet Tasks 3–4, ≈ 60 lines total); (b) keep the
packages truly empty and move the failure-path tests to P1.
Recommendation: (a). The point of the P0 row is that the CI gate shape (installed-wheel
tests, failure paths asserted by exit code) exists before any real code does; (b)
defers exactly the check the row exists to establish.

**G-B — exit-code wording.** The P0 row groups "exit 3, `E_GATE_MISMATCH`,
`E_SCHEMA_MISSING` stubs", which reads as if both codes exit 3. §3.12 (lines 661–663)
says `E_SCHEMA_MISSING` → exit 1 and `E_GATE_MISMATCH` → exit 3.
Options: (a) tests assert §3.12's mapping (1 and 3 respectively) and the §6 row is
reworded in a §14 change-log entry; (b) change §3.12 so schema-missing is exit 3.
Recommendation: (a). Exit 3 means "data was stopped from leaving the machine"; a
missing packaged schema is a build defect, not a refused egress. The packet already
asserts the §3.12 mapping; only the row's wording needs the owner's one-line edit.

**G-E — where X4's "pinned wheel" comes from.** X4 says a dNh dev branch's CI installs
the core from a wheel pinned by version and sha256. The release contract (line 142) ties
wheels to `core-vX.Y.Z` tags built in CI from a clean tree, and P0 cuts no tag.
Options: (a) B9 as proposed — P0 CI uploads the wheel and its sha256 as a workflow
artifact, dNh pins that digest (dNh's CI then needs a cross-repo artifact download and
a token); (b) cut a pre-release tag `core-v0.0.1a0` (or similar) at the end of P0 so a
release asset with a URL and sha256 exists, exercising the real release path with an
empty adapter-test step; (c) drop X4 from P0 and satisfy it in P1 with the first real
release.
Recommendation: (b), with (c) as fallback if the owner does not want a tag before P1.
(b) tests the contract that matters — dNh pinning bytes, not a string — while it is
still cheap, and avoids inventing an artifact-download path that the release contract
never uses. Tagging needs the same authority as creating the remote (§4 item 4).

## 6. Next supervisor's first moves

1. `git -C ~/code/Dopemux-ChatRipperXXX status -sb` — confirm pushed or still ahead 1.
2. If `research/2026-10-21-rt-desk-research/out/research-rt-*.md` exist, dispatch
   sonnet-verify per the research README (Agent, `model: sonnet`, may fetch URLs; one
   row per evidence row; PASS/FAIL/UNKNOWN counts per RT).
3. Apply only `adopt` / `adopt with change` recommendations whose evidence rows all
   PASS, one spec change each, each with a §14 entry and owner approval.
4. With rulings on G-A/G-B/G-E, convert the packet's affected B-values from `proposed`
   to `decided`, then dispatch Sonnet to execute Tasks 1–7 under stops S1–S9; the
   supervisor verifies X1–X5 evidence itself (CI URL, clean-clone sync, sqlite floor).
5. S3 disk headroom (next-steps plan) before P0.5.

## 7. Validation states at handoff

| Check | State |
|---|---|
| Prompt "Design today" lines vs spec rev 2 | PASS (line-level, supervisor) |
| Packet spec claims vs spec rev 2 | PASS after G-D fix; G-A, G-B, G-E OPEN (owner) |
| Research prompt run | NOT_RUN |
| P0 packet execution | NOT_RUN |
| Push of `3fb80e6` | NOT_RUN |
| dNh restore commits on origin | PASS (`origin/migrate-cheaperinference` contains `e8bbcadb`) |

## 8. Hazards for whoever continues

- The prompt and packet cite spec **line numbers** (142–147, 154–162, 657–664, 728,
  841–843, 871, 885–922). Any spec edit shifts them; re-check references after each §14 change.
- `rm` is deny-listed in agent shells; stage files under the session scratchpad instead.
- Delegated drafts are not evidence. Worker claims about what the spec or audit says
  were wrong twice today; read the source line before relying on them.
