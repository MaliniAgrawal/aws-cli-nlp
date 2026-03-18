# src/core/executor.py
"""
Compatibility shim for src.core.execution_engine.

executor.py is the historical name. All implementation lives in
execution_engine.py. This module re-exports everything so existing
imports continue to work without change.
"""

from .execution_engine import *  # noqa: F401, F403
from .execution_engine import (
    ExecutionPolicy,
    ExecutionResult,
    execute_with_confirmation,
)

__all__ = ["ExecutionPolicy", "ExecutionResult", "execute_with_confirmation"]
