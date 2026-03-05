# AWS CLI Safety Assistant (Free Edition)

**AI-assisted AWS CLI generation with enforced human confirmation, safety classification, and non-executing MCP integration.**

---

## Overview

AWS CLI Safety Assistant transforms natural language into AWS CLI commands with built-in safety guardrails. This Free Edition provides local CLI execution with mandatory human-in-the-loop confirmation for all risky operations.

## Install (Free v1)

Prerequisites: Python 3.8+, AWS CLI v2, `aws configure` completed.

Install (GitHub release distribution):

```bash
git clone <https://github.com/MaliniAgrawal/aws-cli-nlp.git>
cd aws-cli-nlp
```

Run:

```bash
python aws-nlp.py "list s3 buckets"
python aws-nlp.py --ci "list s3 buckets"
python -m src.mcp_server
```

Safety: MCP never executes; CLI requires `--execute` plus confirmation.

## Delivery Reality

Marketplace typically expects AMI, container, or SaaS delivery rather than a pure CLI zip. For Free v1, GitHub releases are the distribution channel. The Marketplace listing is best reserved for Pro, packaged as container/AMI/SaaS with org policy enforcement and enterprise controls.

### What Makes This Safe

✅ **Never executes via MCP** - MCP integration is read-only (suggestion mode only)  
✅ **Human-in-the-loop confirmations** - Exact phrase matching for destructive operations  
✅ **Safety classification** - Every command labeled: SAFE / MUTATING / SECURITY_SENSITIVE / DESTRUCTIVE  
✅ **Local audit trail** - Complete command history with timestamps  
✅ **CI/CD validation** - Deterministic exit codes for pipeline integration  
✅ **IDE/Agent compatible** - Clean JSON output for AWS Q, GitHub Copilot, and other AI assistants  
✅ **Clear separation** - Suggest vs execute modes are explicitly separated

---

## Key Features

### 1. Safety Classification System

Every generated command is automatically classified:

- **SAFE** - Read-only operations (list, describe, get)
- **MUTATING** - Creates or modifies resources (create, update, put)
- **SECURITY_SENSITIVE** - IAM, security groups, policies
- **DESTRUCTIVE** - Deletes or terminates resources (delete, terminate)

### 2. Mandatory Confirmation for Risky Operations

Destructive and security-sensitive operations require exact phrase confirmation:

```bash
$ aws-nlp "delete s3 bucket old-data" --execute

[!] CONFIRMATION REQUIRED
This is a DESTRUCTIVE operation.

Type EXACTLY:
  YES, DELETE
to proceed, or anything else to cancel:
```

### 3. MCP Server Integration (Non-Executing)

Safe integration with Model Context Protocol (MCP) clients:

- Provides command suggestions only
- Never executes commands automatically
- Returns structured JSON for AI assistants
- Compatible with Claude Desktop, AWS Q, and other MCP clients

### 4. Local Command History & Audit Trail

Track all generated commands with full context:

```bash
$ aws-nlp --history

[2024-01-15 10:23:45]
  Query   : list s3 buckets in us-east-1
  Intent  : list_s3_buckets
  Service : s3
  Safety  : SAFE
  Allowed : True (manual)
```

### 5. CI/CD Integration

Deterministic exit codes for pipeline validation:

- `0` - Command allowed
- `2` - Requires human confirmation
- `3` - Blocked by policy
- `4` - Unsupported/unknown intent
- `5` - Internal error

```bash
$ aws-nlp "delete production database" --ci
# Exit code 2: requires confirmation
```

---

## Installation

### Prerequisites

- Python 3.8+
- AWS CLI installed and configured
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone <https://github.com/MaliniAgrawal/aws-cli-nlp.git>
cd aws-cli-nlp

# Create virtual environment
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Basic Command Generation

```bash
# Generate command (no execution)
python src/aws_nlp.py "list s3 buckets"

# JSON output for scripting
python src/aws_nlp.py "list ec2 instances" --json

# Explanation only
python src/aws_nlp.py "create s3 bucket my-data" --explain-only
```

### Safe Execution with Confirmation

```bash
# Execute with confirmation prompt
python src/aws_nlp.py "delete s3 bucket old-data" --execute

# Dry-run mode (simulate without executing)
python src/aws_nlp.py "terminate ec2 instance i-123456" --execute --dry-run
```

### Clipboard Integration

```bash
# Copy command to clipboard
python src/aws_nlp.py "list lambda functions" --copy

# Verbose clipboard feedback
python src/aws_nlp.py "describe ec2 instances" --copy --copy-verbose
```

### History & Audit

```bash
# View command history
python src/aws_nlp.py --history

# Filter by service
python src/aws_nlp.py --history --history-service s3

# Filter by safety level
python src/aws_nlp.py --history --history-safety DESTRUCTIVE
```

### CI/CD Mode

```bash
# Non-interactive validation
python src/aws_nlp.py "list s3 buckets" --ci
echo $?  # Check exit code

# Allow confirmation-required actions in CI
python src/aws_nlp.py "create s3 bucket test" --ci --allow-confirm
```

---

## MCP Server Usage

### Start MCP Server

```bash
python src/mcp_server.py
```

### MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop):

**Linux/macOS:**
```json
{
  "mcpServers": {
    "aws-cli-assistant": {
      "command": "python",
      "args": ["/home/user/aws-cli-nlp/src/mcp_server.py"],
      "env": {}
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "aws-cli-assistant": {
      "command": "python",
      "args": ["C:\\Users\\user\\aws-cli-nlp\\src\\mcp_server.py"],
      "env": {}
    }
  }
}
```

> Replace `/home/user` (Linux/macOS) or `C:\Users\user` (Windows) with your actual home directory.

### Available MCP Tools

1. **generate_aws_command** - Generate AWS CLI command from natural language
2. **validate_aws_command** - Validate command safety and syntax
3. **get_command_history** - Retrieve local command history

**Important**: MCP server never executes commands. It only provides suggestions.

---

## Supported AWS Services

### Core Services (v1)
- **S3** - Buckets, objects, lifecycle
- **EC2** - Instances, security groups, key pairs
- **IAM** - Users, roles, policies
- **Lambda** - Functions, invocations
- **DynamoDB** - Tables, items
- **RDS** - Database instances
- **CloudFormation** - Stacks, templates
- **SNS** - Topics, subscriptions
- **SQS** - Queues, messages
- **ECR** - Repositories, images
- **EKS** - Clusters
- **CloudWatch** - Logs, alarms, metrics
- **SSM** - Parameter Store
- **Secrets Manager** - Secrets

### Extensibility

Add new services using the template generator:

```bash
python scripts/add_service_template.py --name <service> --intents <intent1> <intent2>
```

---

## Safety Guarantees

### What This Tool Does

✅ Generates AWS CLI commands from natural language  
✅ Classifies every command by safety level  
✅ Requires explicit confirmation for risky operations  
✅ Maintains local audit trail  
✅ Provides MCP integration for AI assistants (suggestion mode only)  
✅ Validates commands before execution  
✅ Supports CI/CD pipeline integration

### What This Tool Does NOT Do

❌ Execute commands without human confirmation  
❌ Execute commands via MCP (MCP is suggestion-only)  
❌ Bypass safety classifications  
❌ Store AWS credentials  
❌ Send data to external services (fully local)  
❌ Auto-approve destructive operations

---

## Architecture

```
aws-cli-nlp/
├── src/
│   ├── core/                     # Core functionality
│   │   ├── command_generator.py  # Generation logic
│   │   ├── registry.py           # Service autodiscovery
│   │   ├── nlp_utils.py          # Intent classification
│   │   ├── aws_validator.py      # Safety classification
│   │   └── history.py            # Audit trail
│   ├── parsers/                  # Service-specific parsers
│   ├── aws_nlp.py                # CLI interface
│   └── mcp_server.py             # MCP server (non-executing)
├── scripts/                      # Helper scripts and tests
├── marketplace/                  # Marketplace packaging
├── docs/                         # Documentation
└── tests/                        # Test suite
```

---

## Testing

```bash
# Run all tests
python -m pytest -q

# Test specific module
python -m pytest tests/test_command_generator.py -v

# Test with coverage
python -m pytest --cov=src tests/
```

---

## Configuration

### Settings (src/config/settings.py)

```python
SETTINGS = {
    "use_ml": False,              # Enable ML-based intent classification
    "model_size": "small",        # ML model size (small/large)
    "log_level": "INFO",          # Logging verbosity
    "history_enabled": True,      # Enable command history
    "max_history_entries": 1000   # History retention limit
}
```

### Execution Policies

- **allow_safe** - Auto-execute SAFE operations only
- **require_confirmation** - Prompt for all non-SAFE operations (default)
- **block_destructive** - Block DESTRUCTIVE operations entirely
- **block_all** - Block all execution (suggestion mode only)

---

## Troubleshooting

### Command Not Recognized

```bash
# Check service registration
python -c "from src.core.registry import registry; registry.autodiscover(); print(registry.list_services())"
```

### History Not Recording

```bash
# Verify history file
ls -la ~/.aws_nlp_history.jsonl  # Linux/Mac
dir %USERPROFILE%\.aws_nlp_history.jsonl  # Windows
```

### MCP Connection Issues

```bash
# Test MCP server directly
python src/mcp_server.py
# Should output: MCP server listening on stdio
```

---

## Roadmap

### Planned Features (Pro Edition)
- Organization-wide policy enforcement
- Remote execution with approval workflows
- Multi-account support
- Advanced ML intent classification
- Custom safety rules
- Team collaboration features

---

## License

This Free Edition is provided as-is for local CLI usage and MCP integration.

---

## Support

- **Documentation**: See `docs/` folder
- **Issues**: Report via GitHub Issues
- **Community**: Join our discussions

---

## Compliance Statement

**This product provides AI-assisted AWS CLI generation with enforced human confirmation, safety classification, and non-executing MCP integration.**

- All command execution requires explicit human approval
- MCP integration is read-only (suggestion mode only)
- No credentials are stored or transmitted
- All processing is performed locally
- Complete audit trail maintained locally

---

## Version

**v1.0.0 - Free Edition**

Built for AWS Marketplace - Safe, Local, Human-Controlled
