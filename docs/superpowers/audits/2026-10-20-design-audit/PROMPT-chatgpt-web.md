(Paste the text below as the first message. Attach `chatx-design-audit-pack-2026-10-20.zip`.)

---

Auditor name: **chatgpt-web**

The attached zip is your only source of truth. It contains:

- `PROMPT-master.md` — your full brief. Read it first and follow it in full: role, fifteen scope areas, two deliverables and their required structure.
- `design/2026-10-20-chatx-rearchitecture-design.md` — the design under audit.
- `evidence/01-code-reality-audit.md`, `evidence/02-dnh-ingest-trace.md`, `evidence/03-docs-parity-inventory.md` — prior automated reviews; leads, not truth.
- `bundles/source-bundle-chatx.md` and `bundles/source-bundle-dnh.md` — verbatim source files from the two repositories, each in a fenced block headed `## FILE: <path> (<n> lines)`. Cite as `chatx:<path>:<line>` / `dnh:<path>:<line>`, counting lines from the first line inside the fence. Each bundle starts with the full tracked-file inventory so you can see what exists but was not included.

Access: you cannot run code and cannot read anything outside the zip. Anything not in the bundles is **UNKNOWN** — say so rather than assume. You may browse the web for scope item 15 (ecosystem currency); cite URLs and your knowledge cutoff.

Output: produce `report-chatgpt-web.md` (Output A) and `research-targets-chatgpt-web.md` (Output B) as downloadable files if your interface supports it; otherwise print both in full, each preceded by `=== FILE: <name> ===`. Begin the report with the reviewer identity block (model, knowledge cutoff, which bundle files you actually read).

Depth: exhaustive. This is a multi-hour principal-level review, not a summary. If you hit an output limit, end with `CONTINUE` and, when asked to continue, resume exactly where you stopped without repeating.
