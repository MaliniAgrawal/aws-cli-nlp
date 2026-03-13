# AWS CLI NLP

Generate AWS CLI commands from natural language with built-in safety and governance controls.

This open-source tool converts plain English instructions into AWS CLI commands while applying DevSecOps guardrails to help prevent dangerous infrastructure changes.

---

## 🎥 Video Demo

[![AWS CLI NLP Demo](https://img.youtube.com/vi/sgyaWskNRTQ/0.jpg)](https://www.youtube.com/watch?v=sgyaWskNRTQ)

**Watch the demo to see AWS CLI NLP in action!**

**Key highlights:**
- **00:48** — Terminal Mode: Convert plain English into AWS CLI commands
- **01:30** — Safety Labels: Commands classified as SAFE, MUTATING, or DESTRUCTIVE
- **02:45** — Destructive Protection: Multi-step confirmation before deleting resources
- **04:42** — MCP Integration: Use the tool as an MCP server for AI assistants

---

## Key Features

• Natural language → AWS CLI command generation  
• DevSecOps safety classification (SAFE / MUTATING / DESTRUCTIVE)  
• Human-in-the-loop confirmation for sensitive operations  
• CI/CD validation mode with exit codes  
• MCP server integration for AI assistants (Claude Desktop)  
• Organizational policy enforcement for destructive commands  

---

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

---

## Overview

This project provides an intelligent AWS CLI command generator that:

• Parses user intent from natural language  
• Generates correct AWS CLI commands  
• Classifies safety level of operations  
• Enforces policy rules for destructive commands  
• Supports both CLI usage and MCP integration for AI tools  

It is designed as a safe interface between AI agents and cloud infrastructure commands.

---

## Safety Model

Every generated command is classified before execution.

### SAFE
Read-only operations  
**Example:** list resources

### MUTATING
Creates or modifies infrastructure  
**Example:** create bucket, update resource

### DESTRUCTIVE
Deletes resources or irreversible operations

⚠️ Destructive actions require explicit human confirmation.

🔒 Organizational policies can also block commands entirely.

---

## Quick Start

### 1. Clone repository
```bash
git clone https://github.com/MaliniAgrawal/aws-cli-nlp.git
cd aws-cli-nlp
```

### 2. Create virtual environment

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run tests
```bash
python -m pytest -q
```

---

## Using the Tool

### CLI Mode

Generate AWS CLI commands from natural language.

```bash
python aws-nlp.py "list s3 buckets"
```

**Example infrastructure command:**
```bash
python aws-nlp.py "create s3 bucket called my-data"
```

**Commands requiring confirmation:**
```bash
python aws-nlp.py "delete s3 bucket my-data" --execute
```

**Dry-run mode (preview without execution):**
```bash
python aws-nlp.py --dry-run "delete s3 bucket demo-bucket"
```

### CI/CD Mode

Validate commands safely inside automation pipelines.

```bash
python aws-nlp.py --ci "create iam user DevUser"
```

Exit codes indicate safety level for pipeline enforcement.

**Example output:**
```
[CI] safety=SECURITY_SENSITIVE decision=confirm exit_code=2
```

### MCP Server Mode

Start the MCP server for AI assistants.

```bash
python src/mcp_server.py
```

This allows AI clients such as Claude Desktop to safely generate commands without executing them automatically.

---

## Project Structure

```
aws-cli-nlp/
│
├── aws-nlp.py                CLI entry point
├── src/
│   ├── aws_nlp.py
│   ├── mcp_server.py
│   ├── parsers/
│   └── core/
│
├── docs/
├── scripts/
├── tests/
└── marketplace/
```

---

## Documentation

- **[Marketplace Integration](MARKETPLACE_README.md)** - MCP server setup and marketplace compliance
- **[Architecture & Design](docs/)** - Detailed documentation on phases, hardening, and design decisions
- **[Quick Reference](marketplace/QUICK_REFERENCE.md)** - Quick guide for common operations
- **[Permissions & Security](marketplace/PERMISSIONS.md)** - Security model and permissions

---

## Roadmap

Planned improvements:

• ✅ Impact preview / dry-run safety mode  
• Extended AWS service coverage  
• Policy engine for AI agents  
• Terraform / kubectl command governance  
• Web UI for enterprise governance workflows  

---

## Use Cases

• Safer DevOps automation  
• AI agent guardrails for cloud commands  
• Infrastructure change review  
• DevSecOps policy enforcement  
• CI/CD command validation  

---

## Contributing

Contributions and feedback are welcome.

If you find this project useful please ⭐ star the repository.

---

## License

MIT License
