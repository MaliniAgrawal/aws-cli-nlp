# AWS CLI Safety Assistant - Quick Reference

## Elevator Pitch
Natural-language AWS CLI generator with safety classification and human-controlled execution.

## What It Does
- Generates AWS CLI commands from plain English.
- Labels safety as SAFE, MUTATING, SECURITY_SENSITIVE, or DESTRUCTIVE.
- Supports MCP and CLI workflows.

## Execution Boundary
- MCP: never executes commands.
- CLI: executes only with explicit `--execute`.
- Risky operations require confirmation.

## Example Commands
```bash
python aws-nlp.py "list s3 buckets"
python aws-nlp.py --ci "list s3 buckets"
python -m src.mcp_server
```

## Security Notes
- No credential storage.
- No auto-execution from MCP.
- Human approval required for risky CLI execution.

## References
- `MARKETPLACE_README.md`
- `marketplace/DESCRIPTION.md`
- `marketplace/PERMISSIONS.md`
