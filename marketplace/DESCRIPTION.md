# AWS CLI Safety Assistant - Marketplace Description

## Title
AWS CLI Safety Assistant - Natural Language AWS CLI Generator

## Tagline
Generate AWS CLI commands from natural language with safety classification and human-controlled execution.

## Category
Developer Tools / AWS Utilities

## Description

### Overview
AWS CLI Safety Assistant translates plain English into AWS CLI commands. It is designed for developers and AI-assisted workflows with explicit safety boundaries.

### What It Does
- Generates AWS CLI command suggestions from natural language.
- Classifies command risk as SAFE, MUTATING, SECURITY_SENSITIVE, or DESTRUCTIVE.
- Provides CLI, CI JSON output, and MCP integration.

### Execution Model
- MCP mode: generation only, never executes commands.
- CLI mode: execution is optional and requires explicit `--execute`.
- Risky CLI actions require confirmation before execution.

### Supported AWS Services
S3, EC2, Lambda, DynamoDB, IAM, RDS, SQS, SNS, CloudFormation, CloudWatch, ECR, EKS, Secrets Manager, and SSM.

### Integration Options
- MCP server (stdio): `python -m src.mcp_server`
- CLI: `python aws-nlp.py "list s3 buckets"`
- CI mode: `python aws-nlp.py --ci "list s3 buckets"`

### Requirements
- Python 3.11+
- AWS CLI v2 installed for users who intend to run generated commands
- `aws configure` completed for users who intend to run generated commands

### What This Tool Does NOT Do
- MCP does not execute AWS commands.
- The tool does not auto-approve destructive operations.
- The tool does not store AWS credentials.

### Note
This product generates commands and safety metadata. Any real AWS resource action only happens when a user runs the generated command with their own AWS CLI and credentials.
