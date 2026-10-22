#!/usr/bin/env python3
"""Split a `cmd -p --output-format json` NDJSON stream into the final text, a usage receipt,
and the inline deliverables (`=== FILE: <name> ===` ... `=== END ===`).

Usage: extract_deliverables.py <auditor> <out_dir>
Reads   <out_dir>/<auditor>.stdout.md      (NDJSON exactly as redirected by the wrapper)
Writes  <out_dir>/<auditor>.final.md       (finalText from the result line, or recovered text events)
        <out_dir>/<auditor>.usage.txt      (usage, stop reason, session id — one JSON line)
        <out_dir>/report-<auditor>.md and <out_dir>/preapproval-<auditor>.md
        — never overwrites an existing deliverable; writes <name>.fromstdout.md instead.
Exit:   0 both deliverables written; 4 one or both missing; 3 no result line and no text events.
"""
import json
import pathlib
import re
import sys

BLOCK = re.compile(r"^=== FILE: (\S+) ===\n(.*?)(?=^=== FILE: |^=== END ===|\Z)", re.S | re.M)


def collect_text(obj, acc):
    """Fallback only: gather full (non-delta) text blocks nested anywhere in an event."""
    if isinstance(obj, dict):
        if obj.get("type") == "text" and isinstance(obj.get("text"), str):
            if not acc or acc[-1] != obj["text"]:
                acc.append(obj["text"])
        for v in obj.values():
            collect_text(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_text(v, acc)


def main() -> int:
    auditor, out = sys.argv[1], pathlib.Path(sys.argv[2])
    src = out / f"{auditor}.stdout.md"
    final, usage, meta, texts = None, None, {}, []
    for raw in src.read_text(errors="replace").splitlines():
        raw = raw.strip()
        if not raw.startswith("{"):
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            final = ev.get("finalText")
            usage = ev.get("usage")
            meta = {k: ev.get(k) for k in ("subtype", "sessionId", "stopReason", "durationMs")}
        else:
            collect_text(ev, texts)
    if final is None and texts:
        final = "\n".join(texts)
        meta["recovered"] = "concatenated text events (no result line)"
    (out / f"{auditor}.usage.txt").write_text(json.dumps({"usage": usage, **meta}) + "\n")
    if final is None:
        (out / f"{auditor}.final.md").write_text("NO RESULT LINE AND NO TEXT EVENTS\n")
        print(f"{auditor}: no final text")
        return 3
    (out / f"{auditor}.final.md").write_text(final if final.endswith("\n") else final + "\n")

    allowed = {f"report-{auditor}.md", f"preapproval-{auditor}.md"}
    found = {}
    for m in BLOCK.finditer(final):
        name, body = m.group(1), m.group(2)
        if name in allowed:
            found[name] = body
        else:
            print(f"{auditor}: ignoring unexpected file block {name!r}")
    for name, body in found.items():
        dest = out / name
        if dest.exists():
            dest = out / f"{name}.fromstdout.md"
            print(f"{auditor}: {name} already exists; writing {dest.name} instead")
        dest.write_text(body.rstrip("\n") + "\n")
        print(f"{auditor}: wrote {dest.name} ({len(body)} chars)")
    missing = allowed - set(found)
    if missing:
        print(f"{auditor}: MISSING {sorted(missing)}")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
