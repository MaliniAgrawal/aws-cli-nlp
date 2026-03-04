# src/core/executor.py
"""
Optional AWS CLI command execution with human authorization.

Phase B.2 Guarantees:
- AI suggests (command generation)
- Human authorizes (explicit confirmation)
- Policy blocks (safety enforcement)
- Never executes without authorization
"""
import subprocess
import shlex
import json
import os
import datetime
from typing import Dict, Any, Optional, Union
"""Compatibility shim for src.core.execution_engine.

`executor.py` is deprecated in favor of `execution_engine.py`. This module
re-exports the implementation to preserve backwards compatibility for
existing imports while encouraging the new name for clarity and scale.
"""

from .execution_engine import *  # re-export everything
