#!/usr/bin/env python3
"""Extract '=== FILE: name ===' blocks from auditor output into out/.
Usage: extract_reports.py [--force] <auditor>...   (auditor: astra argon grok deepseek kimi astra-pro | all)"""
import re, sys
from pathlib import Path

D = Path(__file__).resolve().parent
OUT = D / "out"
KNOWN = ["astra", "argon", "grok", "deepseek", "kimi"]
FILE_RE = re.compile(r"^=== FILE: (?P<name>[A-Za-z0-9._-]+) ===$")
NAME_RE = re.compile(r"^(?P<kind>report|preapproval)-(?P<aud>[a-z-]+)\.md$")
IDENT = ["Model:", "Runner:", "Knowledge cutoff:", "Files opened:"]


def blocks(text):
    cur, buf, res = None, [], []
    for line in text.splitlines():
        m = FILE_RE.match(line)
        if m or line.strip() == "=== END ===":
            if cur is not None:
                res.append((cur, buf))
            cur, buf = (m.group("name") if m else None), []
            continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        res.append((cur, buf))
    return res


def main(argv):
    force = "--force" in argv
    auds = [a for a in argv if a != "--force"]
    if not auds:
        print(__doc__)
        return 64
    if "all" in auds:
        auds = KNOWN
    rc = 0
    for a in auds:
        src = OUT / f"{a}.last-message.md"
        if not src.exists():
            src = OUT / f"{a}.stdout.md"
        if not src.exists():
            print(f"[{a}] no output file found in {OUT}")
            rc = 2
            continue
        found = []
        for name, lines in blocks(src.read_text(errors="replace")):
            m = NAME_RE.match(name)
            if not m or m.group("aud") != a:
                print(f"[{a}] REFUSED block name {name!r} (must be report-{a}.md or preapproval-{a}.md)")
                continue
            dest = OUT / name
            body = "\n".join(lines).strip("\n") + "\n"
            if dest.exists() and not force:
                print(f"[{a}] REFUSED to overwrite {dest} (use --force)")
                found.append(name)
                continue
            dest.write_text(body)
            found.append(name)
            print(f"{dest}  lines={body.count(chr(10))}  words={len(body.split())}")
            if m.group("kind") == "report":
                for key in IDENT + ["Packet verdict:"]:
                    if key not in body:
                        print(f"  WARN: {name} missing '{key}'")
        expected = [f"report-{a}.md", f"preapproval-{a}.md"]
        missing = [e for e in expected if e not in found]
        if missing:
            print(f"[{a}] MISSING {missing}; found {found or 'nothing'}")
            rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
