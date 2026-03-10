# AWS CLI NLP

Generate AWS CLI commands from natural language with built-in safety controls.

**Key Features:**
- CLI + MCP server support  
- DevSecOps safety classification  
- CI/CD friendly exit codes  
- Human-in-the-loop execution  
- Policy enforcement for destructive commands  

## Architecture

```
User
  ↓
Natural Language
  ↓
aws-cli-nlp
  ↓
Safety Engine
  ↓
Generated AWS CLI
```

## Overview

This project provides an intelligent AWS CLI command generator that uses natural language processing to:
- Parse user intent and generate secure AWS CLI commands
- Validate commands before execution
- Enforce organizational policies
- Support both CLI and Model Context Protocol (MCP) integration

**Key Components:**
- `src/` : core code, parsers for AWS services, config and utilities
- `scripts/` : helper scripts and tests
- `docs/` : documentation and design notes
- `marketplace/` : MCP server packaging and compliance

## Quick start

1. Create and activate a virtual environment:

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run tests:

```bash
python -m pytest -q
```

## Using the Tool

**As CLI:**
```bash
python src/aws_nlp.py "create an S3 bucket called my-data"
```

**As MCP Server:**
```bash
python src/mcp_server.py
```

## Notes

- The `.gitignore` file is already provided to exclude virtualenvs, AWS keys, logs, and temporary files.
- Parsers live in `src/parsers/<service>/` and typically include `__init__.py`, `manifest.json`, and `parser.py`.
- Policy enforcement is configured in `src/pro/` for enterprise deployments.

## Documentation

- **[Marketplace Integration](MARKETPLACE_README.md)** - MCP server setup and marketplace compliance
- **[Architecture & Design](docs/)** - Detailed documentation on phases, hardening, and design decisions
- **[MCP Compliance](docs/MCP_MARKETPLACE_COMPLIANCE.md)** - Compliance requirements and validation
- **[Quick Reference](marketplace/QUICK_REFERENCE.md)** - Quick guide for common operations
- **[Permissions & Security](marketplace/PERMISSIONS.md)** - Security model and permissions
