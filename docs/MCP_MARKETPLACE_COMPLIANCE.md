# MCP Marketplace Compliance - CRITICAL

## Required Behavior for Marketplace Approval

### MCP Server MUST:

1. **Never Execute Commands**
   - Generation only
   - No subprocess calls
   - No AWS API calls

2. **Always Include Execution Metadata**
   ```json
   "execution": {
     "allowed": false,
     "mode": "manual"
   }
   ```

3. **Refuse All Execution Requests**
   - Even if user says "delete now"
   - Even if user says "execute this"
   - Always respond with manual mode

## Why This Matters

**Marketplace Review Will Reject If:**
- MCP executes any commands
- Missing execution metadata
- Execution mode is not "manual"
- Any auto-execution capability

**This Passes Review:**
- Clear separation: generation vs execution
- Explicit manual mode
- Safety classifications included
- Human must copy/paste to execute

## Implementation

### MCP Server (src/mcp_server.py)
```python
@mcp.tool()
async def generate_aws_cli(query: str):
    result = await generate_command(query)
    
    # CRITICAL: Always include this
    result["execution"] = {
        "allowed": False,
        "mode": "manual",
        "note": "MCP server never executes commands."
    }
    
    return result
```

### Response Example
```json
{
  "command": "aws s3 rb s3://production --force",
  "explanation": "Deletes S3 bucket",
  "intent": "delete_s3_bucket",
  "safety": {
    "level": "DESTRUCTIVE",
    "requires_confirmation": true,
    "confirmation_hint": "Review carefully before running."
  },
  "execution": {
    "allowed": false,
    "mode": "manual",
    "note": "MCP server never executes commands. Copy and run manually."
  }
}
```

## Where Execution IS Available

### CLI with --execute Flag
```bash
aws-nlp "list s3 buckets" --execute
# Requires human confirmation for destructive ops
```

### Interactive CLI
```bash
python src/mcp_server.py --mode cli
# User explicitly confirms execution
```

## Where Execution is NOT Available

### MCP Server (Claude Desktop)
- ❌ Never executes
- ✅ Always manual mode
- ✅ User must copy/paste command

### HTTP API
- ❌ Never executes
- ✅ Generation only
- ✅ Returns command string

## Testing Compliance

```bash
# Verify MCP compliance
python test_mcp_compliance.py

# Expected output:
# ✅ MCP never executes commands
# ✅ Execution mode is 'manual'
# ✅ Safety classification present
# 🎉 MCP MARKETPLACE COMPLIANCE: PASS
```

## Marketplace Positioning

### Product Description
"AWS CLI Generator provides AI-assisted command generation with built-in safety awareness. The MCP server generates commands only - users must execute manually in their terminal. This ensures human oversight for all AWS operations."

### Key Selling Points
- ✅ AI suggests, human executes
- ✅ Safety classifications guide decisions
- ✅ Never auto-executes (marketplace compliant)
- ✅ Clear separation of concerns

### Security Statement
"This tool never executes AWS commands automatically. The MCP server operates in generation-only mode, requiring users to manually copy and execute commands in their terminal. This design ensures human oversight and prevents unintended AWS operations."

## Compliance Checklist

- [x] MCP server never executes commands
- [x] All responses include execution metadata
- [x] execution.allowed = false (always)
- [x] execution.mode = "manual" (always)
- [x] Safety classifications included
- [x] Documentation clearly states manual mode
- [x] Tests verify compliance
- [x] No execution tools in MCP server

## Common Mistakes to Avoid

### ❌ DON'T DO THIS:
```python
# Bad: Conditional execution
if user_confirmed:
    execute_command()  # FAILS REVIEW

# Bad: Optional execution parameter
@mcp.tool()
async def generate_aws_cli(query: str, execute: bool = False):
    if execute:  # FAILS REVIEW
        run_command()
```

### ✅ DO THIS:
```python
# Good: Always manual mode
@mcp.tool()
async def generate_aws_cli(query: str):
    result = generate_command_sync(query)
    result["execution"] = {
        "allowed": False,
        "mode": "manual"
    }
    return result
```

## Verification

Run these tests before marketplace submission:

```bash
# 1. MCP compliance
python test_mcp_compliance.py

# 2. Phase B.2 completion
python test_phase_b2_completion.py

# 3. Safety guarantees
python test_execution_safety.py
```

All must pass for marketplace approval.

## Summary

**MCP Server Behavior:**
- Generates commands ✅
- Provides safety info ✅
- Never executes ❌
- Always manual mode ✅

**CLI Behavior:**
- Generates commands ✅
- Optionally executes with --execute flag ✅
- Requires confirmation for destructive ops ✅
- Human authorization required ✅

**Result:**
- Marketplace compliant ✅
- Safe for users ✅
- Clear boundaries ✅
- Human oversight maintained ✅

---

**CRITICAL: Do not modify MCP server to add execution capability.**
**This will fail marketplace review.**
