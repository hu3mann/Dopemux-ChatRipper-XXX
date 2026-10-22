#!/usr/bin/env python3
"""Generate PROMPT-<auditor>.readonly.md for the cmd print-mode lanes (argon, deepseek, kimi).

Why this exists: `cmd -p` (v1.87.1) only permits file reads inside the cwd-rooted project and aborts the
whole run on the first denied read (see out/_attempt2-cmd-failed/smokes/). The shared per-runner wrappers
(PROMPT-<auditor>.md) carry an "## Access" section written for full-tool lanes ("reading any file in both
repositories; rg/grep; git log ..."), which would steer a print-mode auditor straight into a denial. So the
read-only variant is: PROMPT-readonly-preamble.md + wrapper with its "## Access" section replaced by the
block below. Nothing else in the wrapper is touched. Usage: make_readonly_prompts.py [--check]
"""
from __future__ import annotations

import sys
from pathlib import Path

D = Path(__file__).resolve().parent
AUDITORS = ("argon", "deepseek", "kimi")
HERE = "/Users/hue/code/Dopemux-ChatRipperXXX/docs/superpowers/audits/2026-10-22-p0-packet-audit"

READONLY_ACCESS = f"""## Access (read-only print mode — this section replaces the full-tool wording other lanes receive)

- You may read **only** files under `{HERE}/` (your working directory). The runner denies every read outside it, and a single denial ends the run with no deliverable.
- ChatX inputs: `inputs/2026-10-21-p0-workspace-packet.md`, `inputs/2026-10-20-chatx-rearchitecture-design.md` (rev 2.1), `inputs/2026-10-21-next-steps.md` — snapshot copies taken at ChatX commit `cc18536`; `inputs/SHA256SUMS` is authoritative. Do **not** open the live repository at `/Users/hue/code/Dopemux-ChatRipperXXX`.
- dNh_CRM inputs: `bundles/dnh-packaging-bundle.md` — generated digest of `pyproject.toml`, the `uv.lock` header, `.python-version`, `.github/workflows/ci.yml`, `.github/workflows/release.yml` and the other files listed in its header, taken at dNh commit `e8bbcadb`; per-file sha256 in `out/HARNESS-FACTS.md`. Do **not** open the live repository at `/Users/hue/code/dNh_CRM`. If a scope area needs a dNh file that is not in the bundle (for example `src/dnh_crm/`), mark that specific check NOT_RUN with the reason instead of guessing.
- `~/code/chatstack` does not exist (harness-verified in `out/HARNESS-FACTS.md`); P0 creates it. Treat it as absent.
- Facts you would normally measure (`git` HEADs, hashes, line counts, `uv`/Python/SQLite versions) come from `out/HARNESS-FACTS.md` only — you cannot run `git`, `rg`, `wc`, `uv` or `python3`. Cite them as harness-supplied.
- Allowed tools: `read_file`, `grep`, `glob`, `ls` inside the folder above; your runner's web search for scope area 15 (cite URLs).
- Not allowed: `write_file`, `edit_file`, `shell_command`; any read outside the folder above; anything under `~/.codex`, `~/.grok`, `~/.kimi-code`, `~/.config/opencode`, `~/.cmd`; `.env*`, `secrets/`, `auth.json`.

"""

FORBIDDEN_PHRASES = (
    "reading any file in both repositories",
    "ChatX repository (read-only): `/Users/hue/code/Dopemux-ChatRipperXXX`",
    "dNh_CRM repository (read-only): `/Users/hue/code/dNh_CRM`",
)


def replace_access(wrapper: str) -> str:
    lines = wrapper.splitlines(keepends=True)
    start = next((i for i, l in enumerate(lines) if l.startswith("## Access")), None)
    if start is None:
        raise SystemExit("wrapper has no '## Access' heading")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), None)
    if end is None:
        raise SystemExit("wrapper has no heading after '## Access'")
    return "".join(lines[:start]) + READONLY_ACCESS + "".join(lines[end:])


def build(auditor: str) -> str:
    preamble = (D / "PROMPT-readonly-preamble.md").read_text(encoding="utf-8")
    wrapper = (D / f"PROMPT-{auditor}.md").read_text(encoding="utf-8")
    out = preamble + replace_access(wrapper)
    for phrase in FORBIDDEN_PHRASES:
        if phrase in out:
            raise SystemExit(f"{auditor}: forbidden phrase survived: {phrase!r}")
    if "## Output" not in out or "=== FILE:" not in out:
        raise SystemExit(f"{auditor}: Output section or FILE markers missing after transform")
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    rc = 0
    for a in AUDITORS:
        target = D / f"PROMPT-{a}.readonly.md"
        content = build(a)
        if check:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            status = "OK" if current == content else "STALE"
            rc |= status == "STALE"
            print(f"{target.name}: {status}")
        else:
            target.write_text(content, encoding="utf-8")
            print(f"wrote {target.name} ({len(content.splitlines())} lines)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
