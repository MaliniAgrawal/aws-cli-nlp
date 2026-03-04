#!/usr/bin/env python3
"""
Local, append-only history recorder and reader for AWS NLP CLI.
Phase C.1 (FINAL)
"""

import json
import os
import datetime
from typing import Dict, Any, List, Optional

HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".aws-nlp")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.jsonl")


def record_history(entry: Dict[str, Any]) -> None:
    """Append a JSON-line record to the local history file."""
    try:
        os.makedirs(HISTORY_DIR, exist_ok=True)
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            **entry,
        }
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # History must never break core execution
        pass


def read_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Read history entries (most recent last)."""
    if not os.path.exists(HISTORY_FILE):
        return []

    entries: List[Dict[str, Any]] = []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []

    if limit:
        return entries[-limit:]
    return entries
