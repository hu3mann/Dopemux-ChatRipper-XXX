# dNh_CRM packaging bundle (generated, read-only digest)

## header

```
date: 2026-10-22T11:04:39Z
repo: /Users/hue/code/dNh_CRM
HEAD: e8bbcadb19f0f72e80f708e1c1073a3cb5aa45b1
last commit: e8bbcadb 2026-10-21 14:03:16 -0700 restore: rebuild .claude/WORKTREE_MCP_SETUP.md from HEAD + dopemux MCP block (blob 0821d485 verified)
branch: migrate-cheaperinference
```

## top-level listing (ls -la, names only)

```
.
..
.agents
.claude
.control-tower
.dopemux
.dopetask-pin
.env.example
.envrc
.envrc.dopemux-mcp
.envrc.dopemux-mcp.example
.envrc.dopemux-mcp.notes
.gemini
.git
.github
.gitignore
.implementer_state.json
.mcp.json
.pre-commit-config.yaml
.python-version
.venv
.vibe
AGENT_SOP.md
AGENTS.md
ARCHITECTURE.md
artifacts
audit
CHANGELOG.md
CLAUDE.md
CODEX.md
configs
data
dist
docker-compose.yml
docs
dopetask_bundle.yaml
GEMINI.md
implementer-specialist
implementer-specialist.skill
justfile
legacy
LICENSE
llm-plans
Makefile
Masterplan_v3_tightening_review_and_clean_revision.md
ops
out
pr_body.md
PROJECT_INIT_REPORT.md
PROJECT_INSTRUCTIONS.md
project_source_missing_bundle
project_source_missing_bundle.zip
proof
pyproject.toml
README.md
repo_system_docs.zip
run_implementor.sh
schemas
scripts
src
task-packets
tests
tools
uv.lock
workspace
```

## pyproject.toml

```
[project]
name = "dnh-crm"
version = "0.1.0-alpha.1"
description = "Local-first multi-channel CRM orchestration system"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "Proprietary" }
authors = [
  { name = "Hue" }
]
dependencies = [
  "typer>=0.16",
  "rich>=14.0",
  "pydantic>=2.10",
  "pydantic-settings>=2.14.2",
  "python-dotenv>=1.0",
  "sqlalchemy>=2.0",
  "aiosqlite>=0.20",
  "httpx>=0.28",
  "orjson>=3.10",
  "structlog>=25.0",
  "pyyaml>=6.0",
  "tenacity>=9.0",
  "jsonschema>=4.26.0",
]

[dependency-groups]
dev = [
  "pytest>=9.0.3",
  "pytest-cov>=6.0",
  "pytest-asyncio>=0.25",
  "ruff>=0.11",
  "mypy>=1.15",
  "pre-commit>=4.2",
]

[project.optional-dependencies]
dev = [
  "pytest>=9.0.3",
  "pytest-cov>=6.0",
  "pytest-asyncio>=0.25",
  "ruff>=0.11",
  "mypy>=1.15",
  "pre-commit>=4.2",
]
telegram = [
  "python-telegram-bot>=22.0",
]
calendar = [
  "caldav>=1.4",
]
gmail = [
  "google-api-python-client>=2.165",
  "google-auth>=2.38",
]
retrieval = [
  "qdrant-client>=1.13",
  "sqlite-vec>=0.1.6",
]

[project.scripts]
dnh-crm = "dnh_crm.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
default-groups = ["dev"]

[tool.ruff]
line-length = 100
target-version = "py312"
extend-exclude = ["legacy", "implementer-specialist"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "ASYNC", "N"]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-q --strict-markers --strict-config"
pythonpath = ["src"]
testpaths = ["tests"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_ignores = true
warn_return_any = true
warn_redundant_casts = true

[tool.coverage.run]
branch = true
source = ["src/dnh_crm"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## .python-version

```
3.12
```

## .github/workflows/ci.yml

```
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Set up Python
        run: uv python install 3.12

      - name: Sync dependencies
        run: uv sync --all-extras

      - name: Fatal lint
        run: uv run ruff check --select E9,F63,F7,F82 .

      - name: Compile source
        run: uv run python -m compileall -q src

      - name: Validate command-deck project pack
        run: uv run python tools/command_deck/chatgpt_project_pack.py validate --manifest docs/command-deck/chatgpt_project_sources.v2.json --max-sources 40

      - name: Control-plane smoke tests
        run: uv run pytest tests/integration/test_telegram_topics.py

      - name: Full test suite
        run: uv run pytest tests/

      - name: Build
        run: uv build
```

## .github/workflows/release.yml

```
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v7

      - name: Install uv
        uses: astral-sh/setup-uv@v7

      - name: Set up Python
        run: uv python install 3.12

      - name: Sync dependencies
        run: uv sync --all-extras

      - name: Release check
        run: ./scripts/release_check.sh

      - name: Build proof bundle
        run: ./scripts/export_proof_bundle.sh

      - name: Publish GitHub release
        uses: softprops/action-gh-release@v3
        with:
          files: |
            dist/*
            proof/*.zip
            CHANGELOG.md
```

## uv.lock (first 30 lines)

```
version = 1
revision = 3
requires-python = ">=3.12"
resolution-markers = [
    "python_full_version < '3.13'",
    "python_full_version == '3.13.*'",
    "python_full_version >= '3.14'",
]

[[package]]
name = "aiosqlite"
version = "0.22.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/4e/8a/64761f4005f17809769d23e518d915db74e6310474e733e3593cfc854ef1/aiosqlite-0.22.1.tar.gz", hash = "sha256:043e0bd78d32888c0a9ca90fc788b38796843360c855a7262a532813133a0650", size = 14821, upload-time = "2025-12-23T19:25:43.997Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/00/b7/e3bf5133d697a08128598c8d0abc5e16377b51465a33756de24fa7dee953/aiosqlite-0.22.1-py3-none-any.whl", hash = "sha256:21c002eb13823fad740196c5a2e9d8e62f6243bd9e7e4a1f87fb5e44ecb4fceb", size = 17405, upload-time = "2025-12-23T19:25:42.139Z" },
]

[[package]]
name = "annotated-doc"
version = "0.0.4"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/57/ba/046ceea27344560984e26a590f90bc7f4a75b06701f653222458922b558c/annotated_doc-0.0.4.tar.gz", hash = "sha256:fbcda96e87e9c92ad167c2e53839e57503ecfda18804ea28102353485033faa4", size = 7288, upload-time = "2025-11-10T22:07:42.062Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/1e/d3/26bf1008eb3d2daa8ef4cacc7f3bfdc11818d111f7e2d0201bc6e3b49d45/annotated_doc-0.0.4-py3-none-any.whl", hash = "sha256:571ac1dc6991c450b25a9c2d84a3705e2ae7a53467b5d111c24fa8baabbed320", size = 5303, upload-time = "2025-11-10T22:07:40.673Z" },
]

[[package]]
name = "annotated-types"
version = "0.7.0"
```

## uv.lock package count

```
[[package]] entries: 100
```

## uv.lock matches for chatx|chat-extraction|chat_extraction

```
(none)
```

## pyproject.toml [tool.uv] / [tool.uv.sources] lines

```
68:[tool.uv]
```

## tool versions (owner machine, default python3)

```
uv: uv 0.12.11 (4b53f66b7 2026-09-08 aarch64-apple-darwin)
python3 / sqlite3 (owner machine, default python3): 3.12.13 3.53.1
```
