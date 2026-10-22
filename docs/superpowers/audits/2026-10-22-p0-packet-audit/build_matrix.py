#!/usr/bin/env python3
"""Build out/cross-audit-matrix.md from out/report-*.md.  Usage: build_matrix.py [--check]"""
import re, sys, datetime
from pathlib import Path

D = Path(__file__).resolve().parent
OUT = D / "out"
PACKET = D / "inputs" / "2026-10-21-p0-workspace-packet.md"
SUMS = D / "inputs" / "SHA256SUMS"
ID_RE = re.compile(r"^(AST|ASP|ARG|GRK|DSK|KIM)-F\d{2}$")
SEV = ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]
VER = {"CONFIRMED", "PLAUSIBLE", "UNKNOWN"}


def split_cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, i = [], "", 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur += "\\|"
            i += 2
            continue
        if s[i] == "|":
            cells.append(cur.strip())
            cur = ""
        else:
            cur += s[i]
        i += 1
    cells.append(cur.strip())
    return cells


def headings():
    hs = []
    if PACKET.exists():
        for n, l in enumerate(PACKET.read_text().splitlines(), 1):
            if re.match(r"^#{2,3} ", l):
                hs.append((n, l.lstrip("# ").strip()))
    return hs


HS = headings()


def bucket(where, ev=""):
    w = where.strip().strip("`")
    m = re.search(r"packet:\s*L?(\d+)", w, re.I)
    if not m:
        # astra-pro puts prose in Where and cites `inputs/…p0-workspace-packet.md:L<n>` in Evidence;
        # fall back to the first packet-line citation there so its rows join the per-heading buckets.
        m = re.search(r"workspace-packet\.md:\s*L(\d+)", ev)
    if m:
        ln = int(m.group(1))
        cur = "packet: (before first heading)"
        for n, t in HS:
            if n <= ln:
                cur = "packet: " + t
            else:
                break
        return cur
    m = re.search(r"spec:\s*§?\s*([\d.]+)", w, re.I)
    if m:
        return "spec §" + m.group(1).rstrip(".")
    if w.lower().startswith("dnh"):
        return "dNh"
    return "other: " + (w[:40] or "(blank)")


def trunc(s, n=105):
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def parse():
    rows, errs, reports, challenges = [], [], {}, {}
    files = sorted(OUT.glob("report-*.md"))
    for f in files:
        aud = f.stem[len("report-"):]
        verdict, in_dc = "(no Packet verdict line)", False
        challenges[aud] = []
        for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
            m = re.search(r"Packet verdict:\**\s*`?(DO-NOT-APPROVE|APPROVE-WITH-CHANGES|APPROVE)\b", line)
            if m and verdict.startswith("(no"):
                verdict = m.group(1)  # strict token; deepseek writes the line bold-inline with trailing prose
            elif verdict.startswith("(no") and (m2 := re.search(r"Packet verdict:\s*(.*)", line)):
                verdict = m2.group(0).strip("*` ")[:60]  # fallback: unrecognised token, kept visible rather than dropped
            if re.match(r"^#{1,6}\s+.*Decision challenges", line, re.I):
                in_dc = True
                continue
            if in_dc and re.match(r"^#{1,6}\s", line):
                in_dc = False
            if in_dc and re.match(r"^\s*[-*]\s+", line):
                challenges[aud].append(re.sub(r"^\s*[-*]\s+", "", line).strip())
            if line.lstrip().startswith("|"):
                cells = split_cells(line)
                if cells and re.match(r"^[A-Z]{2,4}-F\d+", cells[0]):
                    if len(cells) != 7 or not ID_RE.match(cells[0]):
                        errs.append(f"{f.name}:{n}: malformed row ({len(cells)} cells / bad id): {line[:120]}")
                        continue
                    _id, sev, ver, where, fnd, ev, fix = cells
                    if sev not in SEV or ver not in VER:
                        errs.append(f"{f.name}:{n}: bad severity/verdict {sev!r}/{ver!r}")
                        continue
                    rows.append(dict(id=_id, aud=aud, sev=sev, ver=ver, where=where, ev=ev, finding=fnd, fix=fix))
        reports[aud] = verdict
    return files, rows, errs, reports, challenges


def main(argv):
    check = "--check" in argv
    files, rows, errs, reports, challenges = parse()
    ep = OUT / "_matrix-errors.txt"
    if errs:
        ep.write_text("\n".join(errs) + "\n")
    elif ep.exists():
        ep.unlink()
    if check:
        print(f"{len(files)} reports, {len(rows)} valid findings, {len(errs)} malformed rows")
        for e in errs:
            print("  " + e)
        return 0
    L = ["# Cross-audit matrix (generated; do not hand-edit)", "", "## Tally", ""]
    L += ["| Auditor | " + " | ".join(SEV) + " | Total | Packet verdict |", "|---|" + "---|" * (len(SEV) + 2)]
    for a in sorted(reports):
        mine = [r for r in rows if r["aud"] == a]
        L.append(f"| {a} | " + " | ".join(str(sum(r["sev"] == s for r in mine)) for s in SEV)
                 + f" | {len(mine)} | {reports[a].replace('|', '/')} |")
    L.append("| **all** | " + " | ".join(str(sum(r["sev"] == s for r in rows)) for s in SEV) + f" | {len(rows)} | |")
    L += ["", "## By location", ""]
    groups = {}
    for r in rows:
        groups.setdefault(bucket(r["where"], r["ev"]), []).append(r)
    for g in sorted(groups, key=lambda k: (-len({r["aud"] for r in groups[k]}), k)):
        rs = sorted(groups[g], key=lambda r: (SEV.index(r["sev"]), r["id"]))
        n = len({r["aud"] for r in rs})
        L += [f"### {g}" + ("  **convergence**" if n >= 3 else "") + f" ({len(rs)} findings, {n} auditors)", "",
              "| ID | Severity | Verdict | Where | Finding (≤105 chars) | Fix (≤105 chars) |", "|---|---|---|---|---|---|"]
        for r in rs:
            L.append(f"| {r['id']} | {r['sev']} | {r['ver']} | {r['where']} | {trunc(r['finding'])} | {trunc(r['fix'])} |")
        L.append("")
    L += ["## Decision challenges", ""]
    any_dc = False
    for a in sorted(challenges):
        for c in challenges[a]:
            L.append(f"- **{a}**: {c}")
            any_dc = True
    if not any_dc:
        L.append("(none)")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    L += ["", "---", f"Generated: {now}", "", "Input SHA256SUMS:", "", "```",
          SUMS.read_text().rstrip() if SUMS.exists() else "(missing)", "```", ""]
    (OUT / "cross-audit-matrix.md").write_text("\n".join(L))
    print(f"wrote {OUT / 'cross-audit-matrix.md'}: {len(files)} reports, {len(rows)} findings, {len(errs)} malformed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
