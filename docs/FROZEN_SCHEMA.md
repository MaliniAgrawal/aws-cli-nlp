# Phase B.1 - Frozen Response Schema

## Overview
All interfaces (MCP, HTTP, CLI) return the **exact same structure** with no exceptions.

## Schema Definition

```json
{
  "command": "string",
  "explanation": "string",
  "intent": "string",
  "entities": {
    "region": "string (optional)",
    "bucket": "string (optional)",
    "table": "string (optional)",
    "function": "string (optional)",
    "user": "string (optional)",
    "...": "other service-specific entities"
  },
  "validation": {
    "status": "safe|warning|dangerous|unknown",
    "reason": "string"
  }
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | AWS CLI command to execute |
| `explanation` | string | Yes | Human-readable explanation of what the command does |
| `intent` | string | Yes | Detected intent (e.g., "list_s3_buckets", "create_dynamodb_table") |
| `entities` | object | Yes | Extracted entities from the query (can be empty {}) |
| `validation` | object | Yes | Safety validation result |
| `validation.status` | string | Yes | One of: "safe", "warning", "dangerous", "unknown" |
| `validation.reason` | string | Yes | Explanation of the validation status |

## Examples

### Example 1: List S3 Buckets
**Query:** "list s3 buckets"

**Response:**
```json
{
  "command": "aws s3 ls",
  "explanation": "Lists all S3 buckets in your account.",
  "intent": "list_s3_buckets",
  "entities": {},
  "validation": {
    "status": "safe",
    "reason": "Read-only operation"
  }
}
```

### Example 2: Create S3 Bucket with Region
**Query:** "create an S3 bucket named my-bucket in us-west-1"

**Response:**
```json
{
  "command": "aws s3 mb s3://my-bucket --region us-west-1",
  "explanation": "Creates S3 bucket 'my-bucket' in region us-west-1.",
  "intent": "create_s3_bucket",
  "entities": {
    "bucket": "my-bucket",
    "region": "us-west-1"
  },
  "validation": {
    "status": "safe",
    "reason": "Create operation with valid parameters"
  }
}
```

### Example 3: List EC2 Instances
**Query:** "list ec2 instances in us-west-1"

**Response:**
```json
{
  "command": "aws ec2 describe-instances --region us-west-1",
  "explanation": "Describes EC2 instances in us-west-1.",
  "intent": "list_ec2_instances",
  "entities": {
    "region": "us-west-1"
  },
  "validation": {
    "status": "safe",
    "reason": "Read-only operation"
  }

**Response:**
  "command": "echo 'Unsupported intent'",
  "explanation": "Intent not supported",
    "status": "unknown",
    "reason": "unsupported_intent"
  }
}
```

## Implementation

### Core Module
- **Location:** `src/core/response_schema.py`
- **Function:** `build_standard_response(command, explanation, intent, entities, validation)`

### Usage in All Interfaces

#### MCP Server (`src/mcp_server.py`)
```python
@mcp.tool()
async def generate_aws_cli(query: str):
    result = await generate_command(query)
    return result  # Returns frozen schema
```

#### HTTP API (`src/http_adapter.py`)
```python
@app.post("/generate")
async def generate(req: GenerateRequest):
    result = generate_command_sync(req.query)
    return result  # Returns frozen schema
```

#### CLI Interface (`src/cli_interface.py`)
```python
result = generate_command_sync(query)
print(f"Command: {result['command']}")
print(f"Intent: {result['intent']}")
# ... uses all fields from frozen schema
```

## Validation Status Values

| Status | Meaning | Example |
|--------|---------|---------|
| `safe` | Read-only or low-risk operation | list, describe, get |
| `warning` | Modifies resources but reversible | create, update, put |
| `dangerous` | Destructive operation | delete, terminate, remove |
| `unknown` | Cannot determine safety | Unsupported intent or validation error |

## Guarantees

1. **Structure Consistency:** All interfaces return identical JSON structure
2. **Field Presence:** All 5 top-level fields always present
3. **Type Safety:** Field types never change
4. **No Nulls:** Empty values use empty strings "" or empty objects {}
5. **Backward Compatible:** Future additions only, never removals

## Testing

Run smoke tests to verify schema consistency:
```bash
python scripts/run_smoke_tests.py
```

All responses should match the frozen schema structure.
