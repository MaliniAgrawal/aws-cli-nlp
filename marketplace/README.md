# AWS CLI Safety Assistant Marketplace Docs

Canonical listing content is in `../MARKETPLACE_README.md`.

This folder contains supporting submission docs:
- `marketplace/DESCRIPTION.md`
- `marketplace/PERMISSIONS.md`
- `marketplace/QUICK_REFERENCE.md`
- `marketplace/demo.py`

Free v1 delivery:
- Distributed via GitHub release/source archive.
- Not packaged as AMI/container/SaaS.

Safety boundary:
- MCP server is generation-only and never executes commands.
- CLI can execute only when user explicitly passes `--execute`.
- Risky CLI operations require confirmation phrases.
