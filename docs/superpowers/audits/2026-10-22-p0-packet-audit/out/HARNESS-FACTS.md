# HARNESS-FACTS — precomputed by the supervisor harness with deterministic local tools, 2026-10-22T11:27:18Z

Auditors running under `cmd` print mode cannot execute shell commands. The values below were computed by the harness, not by the auditor; cite them as **harness-supplied (not independently verified)**.

## Repositories
- ChatX: `/Users/hue/code/Dopemux-ChatRipperXXX` — branch `governance-doctrine-integration`, HEAD `cc185366aca4b8912993b1400405c6eaebacfe6b` (cc18536 2026-10-22T03:30:33-07:00); tracked files modified in the working tree: 11. Audit inputs are the snapshot copies under `inputs/`, not the working tree.
- dNh_CRM: `/Users/hue/code/dNh_CRM` — branch `migrate-cheaperinference`, HEAD `e8bbcadb19f0f72e80f708e1c1073a3cb5aa45b1` (e8bbcadb 2026-10-21T14:03:16-07:00); tracked files modified: 0.
- `~/code/chatstack` exists: no

## Audit inputs and bundles (sha256, line count)
- `inputs/2026-10-20-chatx-rearchitecture-design.md`: sha256 `605278090866f493184cf1d019cc030d934bb64d9e9b04ad7100a2eaadf54076`, 1269 lines
- `inputs/2026-10-21-next-steps.md`: sha256 `f5b20b0a711c1b27b86fbfe3f6275ad32cec1584ad4b461b28c19a607559baaa`, 79 lines
- `inputs/2026-10-21-p0-workspace-packet.md`: sha256 `38d0f84d5606c4cd62d360bf435ff04d0f7e1845e90d37c8f3c8ad5a6e7302dd`, 336 lines
- `inputs/SHA256SUMS`: sha256 `89675133d3a9a29a74944efc4ce4cbbb6e3eb086391faaec327a447489addb4a`, 3 lines
- `bundles/dnh-packaging-bundle.md`: sha256 `3aa591d989153b642a024485feaac6b7d73bdc3f3b131a4de76453bc4a75de37`, 338 lines

## dNh_CRM files named by the brief (working tree at the HEAD above)
- `pyproject.toml`: sha256 `fd16616008b0bdaf95ea617a4ae4a1af02e76ca1807dfa27e1b203a588d9db7d`, 98 lines
- `uv.lock`: sha256 `5855f815e00843187cd01a248f02ef705fc707a72778a9b386f5b52744a6a955`, 2076 lines
- `.python-version`: sha256 `7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d`, 1 lines
- `.github/workflows/ci.yml`: sha256 `62359ee3c27331f2f1cf7659168a90baf2030b76dfdf929ffac46382b3dc3f58`, 41 lines
- `.github/workflows/release.yml`: sha256 `4ef133489dadbd63f37c7226c970b193c9822ceae0af617953e505b797867cce`, 37 lines

## Toolchain on the audit host
- uv: uv 0.12.11 (4b53f66b7 2026-09-08 aarch64-apple-darwin)
- python3: Python 3.12.13; sqlite3 library via python: 3.53.1
- macOS: 27.0.1
