# AWS CLI Safety Assistant - Permissions Statement

## Security and Permissions Declaration

### Scope
This product is primarily a command-generation assistant.

- MCP path: generation only, no execution.
- CLI path: optional execution when user explicitly passes `--execute`.

### What It Does
- Parses natural-language AWS requests.
- Generates AWS CLI command text.
- Classifies safety level for each generated command.
- Logs local history and telemetry files for local auditing.

### What It Does NOT Do
- MCP does not execute commands.
- CLI does not execute unless `--execute` is explicitly requested.
- The tool does not auto-approve destructive or security-sensitive actions.
- The tool does not store AWS credentials.

### Credential Handling
- The tool does not persist credentials.
- Users manage credentials with standard AWS CLI configuration.

### AWS API Interaction
- Command generation and MCP response paths do not require AWS API calls.
- Optional validation/license paths in the codebase may use AWS SDK clients when explicitly enabled or configured.

### User Responsibility
Users are responsible for:
1. Reviewing generated commands.
2. Executing commands intentionally in their own terminal.
3. Managing AWS credentials and permissions in their own AWS account.

### Summary
This product enforces a clear boundary: AI suggests, human decides. MCP remains suggestion-only; CLI execution is explicit and user-controlled.
