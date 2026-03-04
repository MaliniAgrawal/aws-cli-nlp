# Phase B.1 & B.2 - Frozen Response Schema with MCP Hardening

## Overview
All interfaces (MCP, HTTP, CLI) return the **exact same structure** with no exceptions.

**Phase B.2 Hardening:**
- ✅ Stateless request handling
- ✅ No AWS credentials ever read or stored
- ✅ No command execution (generation only)
- ✅ Deterministic output for same input

## Schema Definition

```json
{
  "command": "string",
  "explanation": "string",
  "intent": "string",
  "entities": {
    "region": "string (optional)",
    "bucket": "string (optional)",
    "...": "other service-specific entities"
  },
  "validation": {
    "status": "safe|warning|dangerous|unknown",
    "reason": "string"
  },
  "meta": {
    "service": "string",
    "confidence": "high|medium|low",
    "generated_by": "rule_engine|ml_classifier",
    "version": "1.0.0"
  }
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | AWS CLI command to execute |
| `explanation` | string | Yes | Human-readable explanation |
| `intent` | string | Yes | Detected intent |
| `entities` | object | Yes | Extracted entities (can be empty {}) |
| `validation` | object | Yes | Safety validation result |
| `validation.status` | string | Yes | "safe", "warning", "dangerous", "unknown" |
| `validation.reason` | string | Yes | Explanation of validation status |
| `meta` | object | Yes | MCP metadata (Phase B.2) |
| `meta.service` | string | Yes | AWS service name |
| `meta.confidence` | string | Yes | "high", "medium", "low" |
| `meta.generated_by` | string | Yes | "rule_engine" or "ml_classifier" |
| `meta.version` | string | Yes | Schema version |

## Phase B.2 Hardening Requirements

### 1. Stateless Request Handling
- No state persisted between requests
- Registry is read-only after initialization
- Each request is independent

### 2. No AWS Credentials
- Never reads AWS credentials from environment or files
- `aws_session` parameter ignored
- No boto3 sessions created
- No AWS API calls made

### 3. No Command Execution
- Only generates commands, never executes them
- No `subprocess.run()` or `os.system()` calls in core logic
- CLI interface may execute with explicit user consent

### 4. Deterministic Output
- Same query always produces same output
- No timestamps or random values in response
- Reproducible results for testing

### 5. MCP Metadata
- Every response includes `meta` object
- Tracks service, confidence, generation method, version
- Enables client-side filtering and analytics

## Testing

Run hardening verification:
```bash
python scripts/test_hardening.py
```

Run smoke tests:
```bash
python scripts/run_smoke_tests.py
```
