# Changelog

All notable changes to this project will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) — see [docs/VERSIONING.md](docs/VERSIONING.md).

---

## [0.1.0] — 2025-07-10

First tagged release. Establishes the core CLI, safety model, MCP server, CI pipeline, and test suite.

### Added

**Core command generation**
- Natural language → AWS CLI command translation via regex-based NLP with ML fallback
- 14 supported services: S3, EC2, IAM, Lambda, DynamoDB, RDS, CloudFormation, SNS, SQS, ECR, EKS, CloudWatch, SSM, Secrets Manager
- Per-service parsers under `src/parsers/` with a self-registering `registry`

**Safety model**
- Four safety levels: `SAFE`, `MUTATING`, `SECURITY_SENSITIVE`, `DESTRUCTIVE`
- Exact confirmation phrases required before any risky operation runs (`YES, APPLY` / `YES, MODIFY IAM` / `YES, DELETE`)
- `--dry-run` flag: previews command and impact summary without executing

**CLI flags**
- `--execute` — opt-in execution gate; nothing runs without it
- `--dry-run` — preview mode, no execution
- `--json` — machine-readable JSON output
- `--explain-only` — explanation only, no command printed
- `--format agent` — compact JSON for AI agent consumption
- `--no-color` — plain text output, no ANSI codes
- `--copy` / `--copy-verbose` — copy generated command to clipboard
- `--history` / `--last N` / `--history-service` / `--history-safety` — command history with filters
- `--ci` — non-interactive CI/CD mode with structured exit codes and JSON stdout

**CI/CD mode** (`--ci`)
- Exit codes: 0 (safe), 2 (requires confirmation), 3 (policy blocked), 4 (unknown intent), 5 (internal error)
- JSON to stdout, one-line summary to stderr
- `--allow-confirm` flag to treat exit 2 as exit 0 in pipelines

**MCP server** (`src/mcp_server.py`)
- stdio MCP server for Claude Desktop and other AI assistants
- Never executes commands — always returns `execution.allowed=false, mode="manual"`
- Tools: `generate_aws_cli`, `list_supported_services_mcp`, `health_check`

**Output formats**
- `format_human()`, `format_json()`, `format_agent()`, `format_explain_only()`, `format_mcp_response()` in `src/core/cli_formatter.py`
- Frozen response schema via `build_standard_response()` in `src/core/response_schema.py`

**Packaging and install**
- `pyproject.toml` with `[build-system]`, `[project]`, entry point `aws-nlp = "src.aws_nlp:main"`
- `pip install -e .` and `pip install -e ".[dev]"` both work cleanly
- `aws-nlp.py` thin shim for direct script invocation
- `requirements.txt` (runtime only) and `requirements-dev.txt` (chains runtime + dev tools)

**Testing**
- 75 unit tests across `tests/unit/`
- Contract tests for NL→command generation and JSON output shape
- CI exit-code tests: pure unit tests for all exit codes + integration tests driving `main()` with `--ci`
- MCP compliance tests: `execution.allowed` always false, required response fields present

**CI pipeline** (`.github/workflows/ci.yml`)
- `test` job: matrix across Python 3.10, 3.11, 3.12
- `lint` job: black, isort, flake8 (all clean)
- `package` job: `pip install -e ".[dev]"` + entry point smoke tests

**Code quality**
- `src/aws_nlp.py` refactored into thin orchestrator + `src/cli/` modules: `ci.py`, `dry_run.py`, `policy_guard.py`, `prompt.py`
- `conftest.py` at repo root as single `sys.path` injection point
- `setup.cfg` for flake8 config (`max-line-length=88`, `extend-ignore=E203`)
- All linters clean: black, isort, flake8

### Notes

- AWS credentials are not required for command generation or MCP mode
- `--execute` requires `aws configure` to be set up
- History file is created on first use at `~/.aws_nlp_history.jsonl`

[0.1.0]: https://github.com/MaliniAgrawal/aws-cli-nlp/releases/tag/v0.1.0
