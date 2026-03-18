# src/pro/policy_loader.py

import json
from pathlib import Path
from typing import Optional

from .policy_schema import OrgPolicy

DEFAULT_POLICY_PATH = Path("org-policy.json")


def load_org_policy(path: Path = DEFAULT_POLICY_PATH) -> Optional[OrgPolicy]:
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        # Fail-safe: never block due to policy parsing
        return None
