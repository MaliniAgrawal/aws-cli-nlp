# AWS CLI NLP

Generate AWS CLI commands from plain English with built-in safety checks.

```bash
python aws-nlp.py "create iam user DevUser"
```

```
Command:
  aws iam create-user --user-name DevUser

Safety:
  [!] SECURITY_SENSITIVE - Review before applying.

Explanation:
  Creates a new IAM user named 'DevUser'.

Tip:
  Review permissions and least-privilege impact before execution.
```

---

## 🎥 Video Demo

[![AWS CLI NLP Demo](https://img.youtube.com/vi/sgyaWskNRTQ/0.jpg)](https://www.youtube.com/watch?v=sgyaWskNRTQ)

- **00:48** — Terminal Mode: plain English → AWS CLI command
- **01:30** — Safety Labels: SAFE, MUTATING, DESTRUCTIVE
- **02:45** — Destructive Protection: multi-step confirmation
- **04:42** — MCP Integration: AI assistant usage

---

## What it does

- Translates natural language into AWS CLI commands
- Classifies every command as `SAFE`, `MUTATING`, `SECURITY_SENSITIVE`, or `DESTRUCTIVE`
- Requires explicit confirmation before any risky action runs
- Previews commands without execution (`--dry-run`)
- Returns machine-readable JSON for automation and AI agents
- Runs as an MCP server for Claude Desktop and other AI assistants

---

## Safety model

| Level | Meaning | Confirmation required |
|---|---|---|
| `SAFE` | Read-only (list, describe, get) | No |
| `MUTATING` | Creates or modifies resources | Yes — type `YES, APPLY` |
| `SECURITY_SENSITIVE` | IAM, security groups, policies | Yes — type `YES, MODIFY IAM` |
| `DESTRUCTIVE` | Deletes or terminates resources | Yes — type `YES, DELETE` |

MCP mode **never executes commands**. CLI mode only executes when you pass `--execute`.

---

## Install

### Prerequisites

- Python 3.10+
- Git

AWS CLI and `aws configure` are only needed if you plan to use `--execute`.

### Linux / macOS

```bash
git clone https://github.com/MaliniAgrawal/aws-cli-nlp.git
cd aws-cli-nlp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
git clone https://github.com/MaliniAgrawal/aws-cli-nlp.git
cd aws-cli-nlp
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> If PowerShell blocks the activation script, run this once:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Verify the install

```bash
python aws-nlp.py "list s3 buckets"
```

You should see a generated command and a `SAFE` safety label. No AWS credentials are needed for generation.

### Install as a package (optional)

```bash
pip install -e .
aws-nlp "list s3 buckets"   # entry point available after editable install
```

### Dev dependencies

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

---

## Usage

### Generate a command (no execution)

```bash
python aws-nlp.py "list s3 buckets"
python aws-nlp.py "create s3 bucket called my-data"
python aws-nlp.py "describe ec2 instances in us-east-1"
```

**Windows (PowerShell):**
```powershell
python aws-nlp.py "list s3 buckets"
python aws-nlp.py "create iam user DevUser"
```

### Preview without executing (dry-run)

Shows the command, safety level, and impact summary. Nothing runs.

```bash
python aws-nlp.py --dry-run "delete s3 bucket demo-bucket"
```

**Windows:**
```powershell
python aws-nlp.py --dry-run "delete s3 bucket demo-bucket"
```

### Execute a command

Requires `--execute`. Risky operations prompt for an exact confirmation phrase.

```bash
python aws-nlp.py "delete s3 bucket old-logs" --execute
```

```
[!] CONFIRMATION REQUIRED
This is a DESTRUCTIVE operation.

Type EXACTLY:
  YES, DELETE
to proceed, or anything else to cancel:
```

### Output formats

```bash
python aws-nlp.py --json "list lambda functions"          # machine-readable JSON
python aws-nlp.py --explain-only "create s3 bucket test" # explanation only, no command
python aws-nlp.py --format agent "list ec2 instances"    # compact JSON for AI agents
python aws-nlp.py --no-color "list s3 buckets"           # plain text, no ANSI codes
```

### Copy to clipboard

```bash
python aws-nlp.py --copy "list s3 buckets"
python aws-nlp.py --copy --copy-verbose "list s3 buckets"  # prints clipboard status
```

### Command history

```bash
python aws-nlp.py --history                          # last 20 entries
python aws-nlp.py --history --last 5                 # last 5 entries
python aws-nlp.py --history --history-service s3     # filter by service
python aws-nlp.py --history --history-safety DESTRUCTIVE  # filter by safety level
```

---

## CI/CD mode

`--ci` is non-interactive, never executes, and exits with a code your pipeline can act on.

```bash
python aws-nlp.py --ci "create iam user DevUser"
```

Stdout receives the full JSON result. Stderr receives a one-line summary:

```
[CI] safety=SECURITY_SENSITIVE decision=allow exit_code=2
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Allowed — safe to proceed |
| `1` | Cancelled by user |
| `2` | Requires human confirmation |
| `3` | Blocked by org policy |
| `4` | Unsupported or unknown intent |
| `5` | Internal error |

### Pipeline examples

**Bash — block on anything that needs confirmation:**
```bash
python aws-nlp.py --ci "delete s3 bucket old-logs"
if [ $? -ne 0 ]; then
  echo "Command requires review. Halting pipeline."
  exit 1
fi
```

**PowerShell — same check:**
```powershell
python aws-nlp.py --ci "delete s3 bucket old-logs"
if ($LASTEXITCODE -ne 0) {
  Write-Error "Command requires review. Halting pipeline."
  exit 1
}
```

**Allow confirmation-required actions (exit 0 instead of 2):**
```bash
python aws-nlp.py --ci --allow-confirm "create s3 bucket staging-data"
```

**Capture JSON output for downstream processing:**
```bash
result=$(python aws-nlp.py --ci "list ec2 instances")
echo "$result" | jq '.safety.level'
```

---

## MCP server

The MCP server exposes command generation to AI assistants. It **never executes commands**.

### Start the server

```bash
python src/mcp_server.py
```

```
[MCP] Starting MCP stdio server...
```

### Configure Claude Desktop

Edit `claude_desktop_config.json` (usually at `~/.config/claude/` on Linux/macOS or `%APPDATA%\Claude\` on Windows):

**Linux / macOS:**
```json
{
  "mcpServers": {
    "aws-cli-nlp": {
      "command": "python",
      "args": ["/home/<your-user>/aws-cli-nlp/src/mcp_server.py"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "aws-cli-nlp": {
      "command": "python",
      "args": ["C:\\Users\\<your-user>\\aws-cli-nlp\\src\\mcp_server.py"]
    }
  }
}
```

Replace `<your-user>` with your actual username.

### Available MCP tools

| Tool | What it does |
|---|---|
| `generate_aws_cli` | Generate an AWS CLI command from natural language |
| `list_supported_services_mcp` | List all supported AWS services |
| `health_check` | Confirm the server is running |

---

## Supported AWS services

S3, EC2, IAM, Lambda, DynamoDB, RDS, CloudFormation, SNS, SQS, ECR, EKS, CloudWatch, SSM, Secrets Manager

---

## Project structure

```
aws-cli-nlp/
├── aws-nlp.py              # CLI entry point
├── pyproject.toml          # Packaging and tool config
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Dev/test dependencies
├── src/
│   ├── aws_nlp.py          # CLI implementation
│   ├── mcp_server.py       # MCP server (never executes)
│   ├── core/               # Generator, validator, formatter, registry
│   └── parsers/            # Per-service parsers
├── docs/                   # Architecture and design notes
├── marketplace/            # Marketplace and integration docs
├── scripts/                # Helper scripts
└── tests/                  # Unit and integration tests
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'fastmcp'`**

Your virtual environment is not active, or dependencies were not installed.

```bash
# Linux / macOS
source venv/bin/activate
pip install -r requirements.txt

# Windows
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

**`python: command not found` on Windows**

Try `python3` or use the full path. If Python is not installed, download it from [python.org](https://www.python.org/downloads/) and check "Add Python to PATH" during setup.

---

**PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled`**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

**`Intent not recognized` or no command generated**

Check which services are registered:

```bash
python -c "from src.core.registry import registry; registry.autodiscover(); print(registry.list_services())"
```

---

**History file not found**

The history file is created on first use at `~/.aws_nlp_history.jsonl`.

```bash
# Linux / macOS
ls -la ~/.aws_nlp_history.jsonl

# Windows
dir $env:USERPROFILE\.aws_nlp_history.jsonl
```

---

**MCP server not connecting to Claude Desktop**

1. Confirm the server starts without errors: `python src/mcp_server.py`
2. Check the path in `claude_desktop_config.json` is absolute and correct
3. Restart Claude Desktop after editing the config

---

## Documentation

- [Marketplace Integration](MARKETPLACE_README.md) — MCP server setup and marketplace compliance
- [Architecture & Design](docs/) — Phase notes and design decisions
- [Quick Reference](marketplace/QUICK_REFERENCE.md) — Common operations at a glance
- [Permissions & Security](marketplace/PERMISSIONS.md) — Security model and credential handling

---

## Roadmap

- ✅ Dry-run / impact preview mode
- Extended AWS service coverage
- Policy engine for AI agents
- Terraform / kubectl command governance
- Web UI for enterprise governance workflows

---

## Contributing

Contributions and feedback are welcome. If you find this project useful, please ⭐ star the repository.

---

## License

MIT License
