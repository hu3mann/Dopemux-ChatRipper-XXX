#!/usr/bin/env python3
"""Rebuild out/cross-audit-matrix.md with the opus and chatgpt-web columns, convergence, tally and status.

Inputs (under out/):
  _matrix-rows.tmp.tsv        auditor, id, severity, area, citation-result, finding text, note
  cross-audit-matrix.md       existing file: theme names, codex/grok/agy placement and citation
                              results, notes (first built 2026-10-20 20:08 from codex/grok/agy)
  claim-verification-opus.md  optional: sonnet-verify's per-citation result for opus rows

Severities are as claimed by each auditor; nothing is re-graded. Idempotent: running it again
only rewrites the opus-derived parts. Usage: python3 build_matrix.py
"""
from __future__ import annotations

import collections
import pathlib
import re

OUT = pathlib.Path(__file__).resolve().parent / "out"
MATRIX = OUT / "cross-audit-matrix.md"
TSV = OUT / "_matrix-rows.tmp.tsv"
OPUS_VERIFY = OUT / "claim-verification-opus.md"
SEVS = ["INFO", "LOW", "MEDIUM", "HIGH", "BLOCKER"]
RESULTS = {"PASS", "PARTIAL", "FAIL", "UNKNOWN", "NOT_RUN"}
AUDITORS = ["codex", "grok", "agy", "opus", "chatgpt"]
MAX_TEXT = 105  # same truncation as the codex/grok/agy cells
CHATGPT_VERIFY = OUT / "claim-verification-chatgpt.md"

# Theme placement for chatgpt-web (owner-run on chatgpt.com, report-chatgpt-web.md F01-F38),
# by the supervising session (2026-10-21), one theme per finding.
CHATGPT_THEME = {
    "T01": ["F01", "F37"],
    "T02": ["F06", "F08"],
    "T03": ["F07"],
    "T04": ["F02"],
    "T05": ["F03", "F14"],
    "T06": ["F09"],
    "T07": ["F10", "F11"],
    "T08": ["F12", "F13"],
    "T09": ["F05", "F15", "F16"],
    "T10": ["F04"],
    "T11": ["F17"],
    "T12": ["F24"],
    "T13": ["F25"],
    "T14": ["F26"],
    "T15": ["F19", "F20", "F21"],
    "T16": ["F18", "F22", "F28"],
    "T17": ["F27"],
    "T18": ["F29", "F30", "F36"],
    "T19": ["F32"],
    "T20": ["F23", "F31"],
    "T21": ["F33"],
    "T22": ["F34", "F35"],
    "T23": ["F38"],
}
CHATGPT_NOTES = {
    "T01": "chatgpt F37 (no supported SQLite runtime/fix baseline for the case store) restates codex F28",
    "T07": "chatgpt F11 also covers CAS hash-then-copy and unverified existing objects (T14)",
    "T18": "chatgpt F30 (schemas resolved from checkout paths; a missing report schema validates by absence) also bears on T21",
    "T22": "chatgpt F35 says several inherited dead/advisory/real grades (Appendix A, evidence/01) overstate what was verified",
}
CHATGPT_NOTE_TAG = "chatgpt: "  # prefix that marks chatgpt notes written by this script

# Theme placement for opus, by the supervising session (2026-10-20), one theme per finding.
OPUS_THEME = {
    "T01": ["F-09"],
    "T02": ["F-01", "F-13"],
    "T03": ["F-16", "F-33"],
    "T05": ["F-14", "F-32"],
    "T06": ["F-08", "F-17", "F-34"],
    "T08": ["F-07", "F-15", "F-31"],
    "T09": ["F-04", "F-05", "F-23"],
    "T10": ["F-03", "F-06"],
    "T11": ["F-12"],
    "T13": ["F-19"],
    "T14": ["F-20"],
    "T15": ["F-02", "F-27", "F-28"],
    "T16": ["F-18", "F-25"],
    "T18": ["F-10"],
    "T19": ["F-24"],
    "T20": ["F-11", "F-26"],
    "T21": ["F-21", "F-22", "F-35"],
    "T22": ["F-30"],
    "T23": ["F-29"],
}
OPUS_NOTES = {
    "T03": "opus F-21 (the SQL fixture lacks the same columns) is placed in T21",
    "T04": "opus has no time finding of its own: see opus F-08 (`datetime.now()` fallback, T06) and F-31 (`.eml` zone silently UTC, T08)",
    "T06": "opus F-16 (no source for `Edit`, never reads `date_edited`) is placed in T03",
    "T09": "opus F-05 also covers coarse labels carrying special-category content to the cloud (T16)",
    "T15": "opus F-28 (Anthropic has no embedding model) also means cloud embedding sends every chunk (T10/T13)",
    "T20": "opus F-26 also covers `case delete`/purge (codex F26, T22)",
}
OPUS_NOTE_TAG = "opus: "  # prefix that marks notes written by this script

SPOT_START = "<!-- opus-spot-checks:start -->"
SPOT_END = "<!-- opus-spot-checks:end -->"
SPOT_BLOCK = [
    SPOT_START,
    "- Supervisor spot checks of opus (2026-10-20, by script and grep; not a substitute for the sonnet-verify pass):",
    "  - F-04 sample sizes hold. The exact one-sided 95% Clopper–Pearson bound needs n ≥ 598 labelled positives with 0 misses to claim recall ≥ 0.995 (947 with 1 miss), and n ≥ 2,995 for 0.999. Opus says \"about 600\" and \"about 3,000\".",
    "  - F-14 holds. dNh `src/dnh_crm/events.py:12-17` defines its own `MSG_OUTBOUND_*` event types, and `events.py:2008-2015` limits `IMessageAttachmentOnlyPayload` to inbound client iMessage events.",
    "  - Opus acceptance checks: reviewer-identity block present; every CONFIRMED row cites a repo path or design section; 38 of 48 research rows name a finding ID (R-08–R-11, R-17, R-22–R-24, R-30, R-44 cite scope areas only); 0 of 209 tool calls touched another auditor's output.",
    SPOT_END,
]


def cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def row(cs: list[str]) -> str:
    return "| " + " | ".join(cs) + " |"


def short(text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= MAX_TEXT:
        return text
    cut = text[: MAX_TEXT - 1].rstrip().rstrip("\\")
    if cut.count("`") % 2:
        cut += "`"
    return cut + "…"


def max_sev(found: list[str]) -> str:
    return max(found, key=SEVS.index) if found else "—"


def main() -> None:
    tsv = [line.split("\t") for line in TSV.read_text().splitlines() if line.strip()]
    assert all(len(r) == 7 for r in tsv), "TSV rows must have 7 columns"
    by_key = {(r[0], r[1]): r for r in tsv}
    opus_rows = [r for r in tsv if r[0] == "opus"]
    placed = [fid for ids in OPUS_THEME.values() for fid in ids]
    assert sorted(placed) == sorted(r[1] for r in opus_rows), "every opus finding placed exactly once"

    verify: dict[str, str] = {}
    if OPUS_VERIFY.exists():
        for line in OPUS_VERIFY.read_text().splitlines():
            if line.startswith("| F-"):
                cs = cells(line)
                if len(cs) >= 6:
                    res = cs[4].strip("* ")
                    assert res in RESULTS, (cs[0], res)
                    verify[cs[0]] = res
        missing = [r[1] for r in opus_rows if r[1] not in verify]
        assert not missing, f"claim-verification-opus.md lacks rows: {missing}"
        for r in opus_rows:
            r[4] = verify[r[1]]
        TSV.write_text("".join("\t".join(r) + "\n" for r in tsv))

    gpt_rows = [r for r in tsv if r[0] == "chatgpt"]
    placed = [fid for ids in CHATGPT_THEME.values() for fid in ids]
    assert sorted(placed) == sorted(r[1] for r in gpt_rows), "every chatgpt finding placed exactly once"
    gpt_verify: dict[str, str] = {}
    if CHATGPT_VERIFY.exists():
        for line in CHATGPT_VERIFY.read_text().splitlines():
            if re.match(r"\| F\d\d \|", line):
                cs = cells(line)
                if len(cs) >= 6:
                    res = cs[4].strip("* ")
                    assert res in RESULTS, (cs[0], res)
                    gpt_verify[cs[0]] = res
        missing = [r[1] for r in gpt_rows if r[1] not in gpt_verify]
        assert not missing, f"claim-verification-chatgpt.md lacks rows: {missing}"
    for r in gpt_rows:
        r[4] = gpt_verify.get(r[1], "NOT_RUN")
    TSV.write_text("".join("\t".join(r) + "\n" for r in tsv))

    lines = MATRIX.read_text().splitlines()
    out: list[str] = []
    themes: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("Inputs:") and "report-opus.md" not in line:
            line = line.replace(
                "`report-agy.md` (F-01–F-25), and",
                "`report-agy.md` (F-01–F-25), `report-opus.md` (F-01–F-35), and",
            ).replace(
                "(sonnet-verify's per-citation check).",
                "(sonnet-verify's per-citation check), plus `claim-verification-opus.md` (the same check for opus, when present). Citation-check entries for opus are prefixed `opus` because its IDs share agy's `F-nn` format.",
            )
        if line.startswith("Inputs:") and "report-chatgpt-web.md" not in line:
            line = line.replace(
                "`report-opus.md` (F-01–F-35), and",
                "`report-opus.md` (F-01–F-35), `report-chatgpt-web.md` (F01–F38, owner-run on chatgpt.com), and",
            )
        if line.startswith("| # | Theme |"):
            cs = cells(line)
            if "chatgpt-web" not in cs:
                cs.insert(cs.index("opus") + 1, "chatgpt-web")
            line = row(cs)
            out.append(line)
            out.append("|" + "---|" * len(cs))
            i += 2  # skip the old separator row
            continue
        if line.startswith("| opus |") and i > 0 and "Severity" not in line and not any(
            l.startswith("| chatgpt |") for l in lines
        ):
            c = collections.Counter(r[2] for r in gpt_rows)
            lines.insert(i + 1, row(["chatgpt"] + [str(c[s]) for s in ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]] + [str(len(gpt_rows))]))
        if line.startswith("| chatgpt |"):
            c = collections.Counter(r[2] for r in gpt_rows)
            line = row(["chatgpt"] + [str(c[s]) for s in ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]] + [str(len(gpt_rows))])
        if line.startswith("Status:"):
            n_ver = collections.Counter(r[4] for r in opus_rows)
            if verify:
                cite = "opus citation check done: " + ", ".join(f"{k} {n_ver[k]}" for k in ["PASS", "PARTIAL", "FAIL", "UNKNOWN", "NOT_RUN"] if n_ver[k])
            else:
                cite = "opus citation check **NOT_RUN** (sonnet-verify-opus pending)"
            line = (
                "Status: **opus column filled** (attempt 2 completed 2026-10-20 20:38 local, 35 findings); "
                f"{cite}. **chatgpt-web column filled** (owner-run on chatgpt.com, report dated 2026-10-20, {len(gpt_rows)} findings); "
                + (
                    "chatgpt citation check done: "
                    + ", ".join(f"{k} {n}" for k in ["PASS", "PARTIAL", "FAIL", "UNKNOWN", "NOT_RUN"]
                                if (n := sum(1 for r in gpt_rows if r[4] == k)))
                    if gpt_verify
                    else "chatgpt citation check **NOT_RUN** (no `claim-verification-chatgpt.md`)"
                )
                + ". Rebuild with `python3 build_matrix.py` when any input changes."
            )
        if line.startswith("| opus |") and i > 0 and "Severity" not in line:
            c = collections.Counter(r[2] for r in opus_rows)
            line = row(["opus"] + [str(c[s]) for s in ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]] + [str(len(opus_rows))])
        m = re.match(r"\| (T\d\d) \|", line)
        if m:
            cs = cells(line)
            if len(cs) == 9:  # pre-chatgpt layout: add the chatgpt-web column after opus
                cs.insert(6, "—")
            assert len(cs) == 10, (cs[0], len(cs))
            tid = cs[0]
            ids = OPUS_THEME.get(tid, [])
            cs[5] = "<br>".join(f"**{fid}** ({by_key[('opus', fid)][2]}) {short(by_key[('opus', fid)][5])}" for fid in ids) or "—"
            gids = CHATGPT_THEME.get(tid, [])
            cs[6] = "<br>".join(
                f"**{fid}** ({by_key[('chatgpt', fid)][2]}) {short(by_key[('chatgpt', fid)][5])}" for fid in gids
            ) or "—"
            cite = [e for e in cs[7].split(" · ") if e and not e.startswith(("opus ", "chatgpt "))]
            if ids and verify:
                cite += [f"opus {fid} {verify[fid]}" for fid in ids]
            elif ids:
                cite.append(f"opus NOT_RUN ({len(ids)})")
            if gids and gpt_verify:
                cite += [f"chatgpt {fid} {gpt_verify[fid]}" for fid in gids]
            elif gids:
                cite.append(f"chatgpt NOT_RUN ({len(gids)})")
            cs[7] = " · ".join(cite) or "—"
            present = [a for a, cell in zip(AUDITORS, cs[2:7]) if cell != "—"]
            sevs = re.findall(r"\((BLOCKER|HIGH|MEDIUM|LOW|INFO)\)", " ".join(cs[2:7]))
            cs[8] = f"{len(present)}/{len(AUDITORS)} · max {max_sev(sevs)}"
            notes = [
                n for n in cs[9].split("<br>")
                if n and not n.startswith((OPUS_NOTE_TAG, CHATGPT_NOTE_TAG))
            ]
            if tid in OPUS_NOTES:
                notes.append(OPUS_NOTE_TAG + OPUS_NOTES[tid])
            if tid in CHATGPT_NOTES:
                notes.append(CHATGPT_NOTE_TAG + CHATGPT_NOTES[tid])
            cs[9] = "<br>".join(notes)
            results = [
                (a, fid, by_key[(a, fid)][4])
                for a, cell in zip(AUDITORS, cs[2:7])
                for fid in re.findall(r"\*\*(F-?\d+)\*\*", cell)
            ]
            themes.append({"id": tid, "name": cs[1], "n": len(present), "max": max_sev(sevs), "results": results})
            line = row(cs)
        if line.startswith("## Strongest signals"):
            out.extend(strongest(themes))
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        if line.startswith("## Corrections and verifier observations"):
            out.append(line)
            i += 1
            body: list[str] = []
            while i < len(lines) and not lines[i].startswith("## "):
                body.append(lines[i])
                i += 1
            if SPOT_START in body:
                a, b = body.index(SPOT_START), body.index(SPOT_END)
                body = body[:a] + body[b + 1 :]
            while body and not body[-1].strip():
                body.pop()
            out.extend(body + SPOT_BLOCK + [""])
            continue
        if line.startswith("- No finding was dropped"):
            counts = collections.Counter(r[0] for r in tsv)
            line = (
                f"- No finding was dropped, merged, or re-graded. Row count check: {len(tsv)} findings placed exactly once "
                f"(codex {counts['codex']}, grok {counts['grok']}, agy {counts['agy']}, opus {counts['opus']}, "
                f"chatgpt {counts['chatgpt']}; asserted by `build_matrix.py`). "
                "Opus and chatgpt placements are the `OPUS_THEME` and `CHATGPT_THEME` tables in that script."
            )
        out.append(line)
        i += 1

    assert len(themes) == 23, len(themes)
    MATRIX.write_text("\n".join(out) + "\n")
    print(f"wrote {MATRIX} ({MATRIX.stat().st_size} bytes); opus verified rows: {len(verify)}/35")


def strongest(themes: list[dict]) -> list[str]:
    head = [
        "## Strongest signals (≥ 3 of 5 auditors, max severity ≥ HIGH, no citation FAIL)",
        "",
        "Partials are listed so the reader can judge them; the earlier 3/3 list required PARTIAL-only-on-wording, which was the supervisor's call. "
        "Opus citations count only once sonnet-verify-opus has run; chatgpt citations count only once `claim-verification-chatgpt.md` exists.",
        "",
    ]
    body: list[str] = []
    for want, label in ((5, "All five auditors"), (4, "Four of five"), (3, "Three of five")):
        hits = [
            t for t in themes
            if t["n"] == want and t["max"] in ("HIGH", "BLOCKER") and not any(r == "FAIL" for _, _, r in t["results"])
        ]
        body.append(f"**{label}** ({len(hits)})")
        body.append("")
        for t in hits:
            partial = [f"{a} {fid}" for a, fid, r in t["results"] if r == "PARTIAL"]
            extra = f" — partial: {', '.join(partial)}" if partial else ""
            body.append(f"- {t['id']} {t['name']} (max {t['max']}){extra}")
        body.append("")
    return head + body


if __name__ == "__main__":
    main()
