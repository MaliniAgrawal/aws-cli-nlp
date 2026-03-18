#!/usr/bin/env python3
"""
Thin compatibility shim — delegates to `src.aws_nlp:main`.

Prefer the installed entry point or `python -m src.aws_nlp` over this file.
This shim exists only for contributors who run from the repo root without
installing the package first.
"""

from src.aws_nlp import main

if __name__ == "__main__":
    main()
