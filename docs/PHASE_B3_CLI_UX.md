# Phase B.3 - CLI UX Polish

## Overview
MCP gets JSON, CLI gets human-friendly text. Same engine underneath.

## CLI Command: `aws-nlp`

### Basic Usage
```bash
aws-nlp "list s3 buckets"
```

### Flags

| Flag | Description | Output |
|------|-------------|--------|
| (none) | Default human-friendly output | Formatted text with colors |
| `--json` | JSON output for scripting/MCP | Raw JSON response |
| `--no-color` | Disable colored output | Plain text without ANSI codes |
| `--explain-only` | Show explanation only | Intent and explanation, no command |

## Output Formats

### 1. Default (Human-Friendly)

**Command:**
```bash
aws-nlp "delete s3 bucket old-bucket"
```

**Output:**
```
Command:
  aws s3 rb s3://old-bucket --force

Safety:
  ⚠ DESTRUCTIVE – requires confirmation

Explanation:
  Permanently deletes the bucket and all objects.

Tip:
  Review carefully before running in production.
```

### 2. JSON Format (`--json`)

**Command:**
```bash
aws-nlp --json "delete s3 bucket old-bucket"
```

**Output:**
```json
{
  "command": "aws s3 rb s3://old-bucket --force",
  "explanation": "Permanently deletes the bucket and all objects.",
  "intent": "delete_s3_bucket",
  "entities": {
    "bucket": "old-bucket"
  },
  "validation": {
    "status": "dangerous",
    "reason": "Destructive operation"
  },
  "meta": {
    "service": "s3",
    "confidence": "high",
    "generated_by": "rule_engine",
    "version": "1.0.0"
  }
}
```

### 3. No Color (`--no-color`)

**Command:**
```bash
aws-nlp --no-color "list s3 buckets"
```

**Output:**
```
Command:
  aws s3 ls

Safety:
  ✓ SAFE – Read-only operation

Explanation:
  Lists all S3 buckets in your account.

Tip:
  This is a read-only operation.
```

### 4. Explain Only (`--explain-only`)

**Command:**
```bash
aws-nlp --explain-only "create ec2 instance"
```

**Output:**
```
Intent: create_ec2_instance
Service: ec2
Explanation:
  Creates a new EC2 instance with specified configuration.
```

## Safety Indicators

| Status | Color | Icon | Meaning |
|--------|-------|------|---------|
| `safe` | Green | ✓ | Read-only or low-risk operation |
| `warning` | Yellow | ⚠ | Modifies resources but reversible |
| `dangerous` | Red | ⚠ | Destructive operation |
| `unknown` | Gray | ? | Cannot determine safety |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Unknown intent |
| 2 | Dangerous operation detected |

## Examples

### Safe Operation
```bash
$ aws-nlp "list lambda functions in us-west-1"

Command:
  aws lambda list-functions --region us-west-1

Safety:
  ✓ SAFE – Read-only operation

Explanation:
  Lists Lambda functions in us-west-1.

Tip:
  This is a read-only operation.
```

### Warning Operation
```bash
$ aws-nlp "create s3 bucket my-bucket"

Command:
  aws s3 mb s3://my-bucket

Safety:
  ⚠ WARNING – Verify parameters before execution

Explanation:
  Creates S3 bucket 'my-bucket'.

Tip:
  Verify parameters before execution.
```

### Dangerous Operation
```bash
$ aws-nlp "terminate ec2 instance i-1234567890abcdef0"

Command:
  aws ec2 terminate-instances --instance-ids i-1234567890abcdef0

Safety:
  ⚠ DESTRUCTIVE – requires confirmation

Explanation:
  Terminates EC2 instance(s) i-1234567890abcdef0.

Tip:
  Review carefully before running in production.
```

## Interactive Mode

Run without arguments for interactive mode:
```bash
python src/mcp_server.py --mode cli
```

Interactive commands:
- `<query>` - Generate AWS CLI command
- `json <query>` - Output in JSON format
- `explain <query>` - Show explanation only
- `exit` or `quit` - Exit the program

## Integration

### MCP Server
MCP always receives JSON format (no formatting applied):
```python
@mcp.tool()
async def generate_aws_cli(query: str):
    result = await generate_command(query)
    return result  # Returns JSON
```

### HTTP API
HTTP API returns JSON by default:
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "list s3 buckets"}'
```

### CLI
CLI uses human-friendly format by default:
```bash
aws-nlp "list s3 buckets"
```

## Environment Variables

| Variable | Effect |
|----------|--------|
| `NO_COLOR` | Disables colored output (same as `--no-color`) |

## Testing

Run CLI UX tests:
```bash
python scripts/test_cli_ux.py
```

This tests all output formats and color codes.
