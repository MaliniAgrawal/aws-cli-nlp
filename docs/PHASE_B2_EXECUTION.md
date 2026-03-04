# Phase B.2 - Optional Execution with Safety Guarantees

## Goal
Enable optional execution of generated AWS CLI commands without breaking MCP safety guarantees.

**Principle:** AI suggests, Human authorizes, Policy blocks

## Architecture

### Three-Layer Safety Model

```
┌─────────────────────────────────────────┐
│  Layer 1: Command Generation (AI)      │
│  - Generates AWS CLI commands           │
│  - Provides safety classification       │
│  - Never executes                       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Layer 2: Human Authorization           │
│  - Explicit confirmation required       │
│  - Reviews command and safety info      │
│  - Decides to execute or not            │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  Layer 3: Policy Enforcement            │
│  - Checks execution policy              │
│  - Blocks if policy forbids             │
│  - Executes if allowed                  │
└─────────────────────────────────────────┘
```

## Safety Guarantees

### 1. Human Authorization Required
```python
# ❌ This will NEVER execute
execute_command(command, human_authorized=False)
# Result: blocked=True, reason="Requires explicit human authorization"

# ✅ This MAY execute (if policy allows)
execute_command(command, human_authorized=True)
```

### 2. Policy Enforcement
```python
class ExecutionPolicy:
    ALLOW_SAFE           # Auto-allow SAFE operations only
    REQUIRE_CONFIRMATION # Require confirmation for all
    BLOCK_DESTRUCTIVE    # Block DESTRUCTIVE operations
    BLOCK_ALL            # Block all execution
```

### 3. Dry-Run Mode
```python
# Simulate execution without running
execute_command(command, dry_run=True)
# Result: "[DRY RUN] Would execute: aws s3 ls"
```

### 4. Timeout Protection
```python
# Commands timeout after 30 seconds (configurable)
execute_command(command, timeout=30)
```

## Usage Examples

### Example 1: Generation Only (Default)
```python
from src.core.command_generator import generate_command_sync

# AI suggests
response = generate_command_sync("list s3 buckets")
print(response["command"])  # aws s3 ls
print(response["safety"]["level"])  # SAFE

# No execution - human must run manually
```

### Example 2: With Human Authorization
```python
from src.core.executor import execute_with_confirmation, ExecutionPolicy

# AI suggests
response = generate_command_sync("list s3 buckets")

# Human reviews and authorizes
result = execute_with_confirmation(
    generated_response=response,
    policy=ExecutionPolicy.REQUIRE_CONFIRMATION,
    dry_run=False  # Actually execute
)

print(result["execution"]["stdout"])  # Command output
```

### Example 3: Policy-Based Execution
```python
# Policy: Auto-allow SAFE operations
result = execute_with_confirmation(
    response,
    policy=ExecutionPolicy.ALLOW_SAFE
)
# SAFE operations execute automatically
# MUTATING/DESTRUCTIVE still require confirmation

# Policy: Block destructive operations
result = execute_with_confirmation(
    response,
    policy=ExecutionPolicy.BLOCK_DESTRUCTIVE
)
# DESTRUCTIVE operations are blocked
# Result: blocked=True
```

### Example 4: Dry-Run Testing
```python
# Test what would happen without executing
result = execute_with_confirmation(
    response,
    policy=ExecutionPolicy.REQUIRE_CONFIRMATION,
    dry_run=True
)

print(result["execution"]["stdout"])
# "[DRY RUN] Would execute: aws s3 ls"
```

## MCP Integration

### Two Separate Tools

**Tool 1: Generation Only (Safe)**
```python
@mcp.tool()
async def generate_aws_command_only(query: str):
    """Generate command without execution"""
    return generate_command_sync(query)
```

**Tool 2: With Optional Execution**
```python
@mcp.tool()
async def execute_aws_command(
    query: str,
    policy: str = "require_confirmation",
    dry_run: bool = False
):
    """Generate and optionally execute with human authorization"""
    response = generate_command_sync(query)
    return execute_with_confirmation(response, policy, dry_run)
```

### Claude Desktop Usage

**Safe Mode (Default):**
```
User: "List my S3 buckets"
Claude: [Calls generate_aws_command_only]
Claude: "Here's the command: aws s3 ls. Would you like me to execute it?"
User: "Yes"
Claude: [Calls execute_aws_command with human authorization]
```

**Policy-Based:**
```
User: "Delete S3 bucket old-bucket"
Claude: [Calls execute_aws_command]
Result: blocked=True (DESTRUCTIVE operation blocked by policy)
Claude: "This is a destructive operation. Policy blocks automatic execution."
```

## Execution Policies

### ALLOW_SAFE
- Auto-executes: SAFE operations
- Requires confirmation: MUTATING, SECURITY_SENSITIVE, DESTRUCTIVE
- Use case: Read-only automation

### REQUIRE_CONFIRMATION (Default)
- Requires confirmation: All operations
- Use case: Maximum safety, human-in-the-loop

### BLOCK_DESTRUCTIVE
- Auto-executes: SAFE, MUTATING
- Blocks: DESTRUCTIVE operations
- Use case: Prevent accidental deletions

### BLOCK_ALL
- Blocks: All execution
- Use case: Generation-only mode (Phase B.1)

## Response Schema

### With Execution
```json
{
  "command": "aws s3 ls",
  "explanation": "Lists all S3 buckets",
  "intent": "list_s3_buckets",
  "entities": {},
  "safety": {
    "level": "SAFE",
    "requires_confirmation": false,
    "confirmation_hint": "This is a read-only operation."
  },
  "meta": {
    "service": "s3",
    "confidence": "high",
    "generated_by": "rule_engine",
    "version": "1.0.0"
  },
  "execution": {
    "success": true,
    "stdout": "2024-01-01 12:00:00 my-bucket-1\n2024-01-01 12:00:00 my-bucket-2",
    "stderr": "",
    "exit_code": 0,
    "blocked": false,
    "reason": "Executed successfully"
  }
}
```

### Blocked by Policy
```json
{
  "command": "aws s3 rb s3://old-bucket --force",
  "safety": {
    "level": "DESTRUCTIVE",
    "requires_confirmation": true
  },
  "execution": {
    "success": false,
    "blocked": true,
    "reason": "Execution blocked by policy: DESTRUCTIVE operations not allowed"
  }
}
```

## Testing

```bash
# Test safety guarantees
python test_execution_safety.py

# Expected output:
# ✅ Human authorization required
# ✅ Policy enforcement works
# ✅ Dry-run mode available
# ✅ Never auto-executes without authorization
```

## Security Considerations

### What This Does NOT Change
- ❌ MCP server still never executes by default
- ❌ No credentials stored or accessed
- ❌ Stateless operation maintained
- ❌ No auto-execution without explicit authorization

### What This Adds
- ✅ Optional execution with human authorization
- ✅ Policy-based execution control
- ✅ Dry-run mode for testing
- ✅ Clear separation: generation vs execution

## Marketplace Positioning

### Free Tier
- Command generation only
- No execution

### Pro Tier
- Command generation
- Optional execution with policies
- Dry-run mode

### Enterprise Tier
- Custom execution policies
- Audit logging
- Team-wide policy enforcement

## Migration Path

### Phase B.1 (Current)
- Generation only
- No execution
- Maximum safety

### Phase B.2 (This)
- Optional execution
- Human authorization required
- Policy enforcement

### Phase B.3 (Future)
- Advanced policies
- Audit trails
- Compliance reporting

## Key Differentiators

**vs. Other AWS Tools:**
- ✅ AI suggests, human approves (not auto-execution)
- ✅ Policy enforcement built-in
- ✅ Safety classifications guide decisions
- ✅ Dry-run mode for testing

**For Job Interviews:**
"I built execution with three-layer safety: AI suggests, human authorizes, policy blocks. It's not automation - it's AI-assisted, human-controlled execution."

## Files Created

1. `src/core/executor.py` - Execution engine with safety guarantees
2. `src/mcp_execution_tool.py` - MCP tools for optional execution
3. `test_execution_safety.py` - Safety guarantee verification

## Summary

Phase B.2 enables **optional execution** while maintaining **all safety guarantees**:

- AI generates commands (Layer 1)
- Human authorizes execution (Layer 2)
- Policy enforces rules (Layer 3)

**Result:** AI-assisted, human-authorized, policy-controlled execution.

✅ Phase B.2 Complete
