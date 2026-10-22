Permission smokes run 2026-10-22 (~14:55–15:12 UTC; attempt 2 itself ran 11:28Z) after attempt 2 failed with stopReason=permission_denied on the first read_file.
All on google/gemini-4-argon, -t, --output-format json, tiny prompt ("read file X, reply with its first line"), --max-turns 4-6.
  a  cwd=scratch, --permission-mode plan, --add-dir <audit dir>                 -> permission_denied (exit 9)
  b  cwd=scratch, --permission-mode default, --tools-enable read_file, --add-dir -> permission_denied; runner: "read_file — not withheld by this run"
  c  cwd=scratch, --permission-mode plan, --tools-enable read_file, --add-dir    -> permission_denied (exit 9)
  d  cwd=<audit dir>, --permission-mode plan (no --add-dir)                      -> end_turn, 2x tool_result, correct first lines (exit 0)
Conclusion: cmd -p (v1.87.1) only permits file reads inside the cwd-rooted project; --add-dir does not widen that headlessly.
Attempt 2 ran from out/, so the first read ($D/PROMPT-master.md) was outside the project and denied. Fix: run from $D.
