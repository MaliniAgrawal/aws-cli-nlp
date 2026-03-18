# src/cli/policy_guard.py
"""
Org-policy enforcement gate for the CLI execution path.
Calls sys.exit(3) when a Pro policy decision is "block".
Kept separate so the exit point is easy to locate and test.
"""

import sys


def block_if_policy_denies(result: dict) -> None:
    """
    Inspect pro_enforcement in the result and exit(3) if the decision is block.
    No-ops when Pro is not enabled or the decision is allow/confirm.
    """
    pe = result.get("pro_enforcement") or {}
    if not pe.get("enabled"):
        return

    if (pe.get("decision") or "allow").lower() == "block":
        reason = pe.get("reason") or "Blocked by org policy"
        print(f"\nBLOCKED by org-policy: {reason}")
        print(
            "This block cannot be overridden."
            " Update org-policy.json to change behavior."
        )
        sys.exit(3)
