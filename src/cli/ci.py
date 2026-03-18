# src/cli/ci.py
"""
CI mode exit-code contract.

  0  allowed          SAFE, no confirmation needed
  2  requires review  MUTATING / DESTRUCTIVE / SECURITY_SENSITIVE
  3  blocked          org policy decision == block
  4  unknown intent   unrecognised or unsupported input
  5  internal error   exception inside ci_exit_code
"""


def ci_exit_code(result: dict, fail_on_confirm: bool = True) -> int:
    try:
        intent = (result.get("intent") or "").lower()
        safety = result.get("safety") or {}
        level = (safety.get("level") or "UNKNOWN").upper()

        if intent in ("unknown", "unsupported_intent", "") or level == "UNKNOWN":
            return 4

        pe = result.get("pro_enforcement") or {}
        if pe.get("enabled"):
            decision = (pe.get("decision") or "allow").lower()
            if decision == "block":
                return 3
            if decision == "confirm" and fail_on_confirm:
                return 2

        if fail_on_confirm and level in (
            "MUTATING",
            "DESTRUCTIVE",
            "SECURITY_SENSITIVE",
        ):
            return 2

        return 0

    except Exception:
        return 5
