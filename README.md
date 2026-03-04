# MCP Phase A

Minimal README for the Phase A deliverable of the MCP AWS CLI Generator project.

## Overview

This folder contains the Phase-A implementation and supporting scripts for the MCP (AWS CLI generator) prototype. Key components:

- `src/` : core code, parsers for AWS services, config and utilities.
- `scripts/` : helper scripts and tests.
- `docs/` : documentation and design notes.

## Quick start

1. Create and activate a virtual environment (Windows example):

```powershell
python -m venv venv-phase-a
venv-phase-a\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run tests:

```powershell
python -m pytest -q
```

## Notes

- The `phase-a/.gitignore` file is already provided to exclude virtualenvs, AWS keys, logs, and temporary files.
- Parsers live in `src/parsers/<service>/` and typically include `__init__.py`, `manifest.json`, and `parser.py`.

## Next steps

- Initialize a Git repository and make an initial commit when ready.
