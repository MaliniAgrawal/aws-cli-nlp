"""
Root conftest.py — makes the project root the import base for all tests.
With `pip install -e .` this file is redundant but kept as a fallback for
contributors who run pytest without installing the package first.
"""

import sys
from pathlib import Path

# Insert project root (the directory that contains `src/`) so that
# `from src.foo import bar` works in every test without per-file path hacks.
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
