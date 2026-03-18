# src/cli/prompt.py
"""
Interactive confirmation prompts for risky CLI operations.
Owns all input() calls so the rest of the CLI never touches stdin directly.
"""

CONFIRMATION_PHRASES = {
    "MUTATING": "YES, APPLY",
    "SECURITY_SENSITIVE": "YES, MODIFY IAM",
    "DESTRUCTIVE": "YES, DELETE",
}


def confirm_destructive_action(safety_level: str, result: dict | None = None) -> bool:
    """
    Prompt for explicit confirmation before a risky operation.

    Returns True if the user confirmed, False if they cancelled.
    SAFE operations always return True without prompting.
    """
    if safety_level not in ("MUTATING", "SECURITY_SENSITIVE", "DESTRUCTIVE"):
        return True

    phrase = CONFIRMATION_PHRASES.get(safety_level, "YES, CONFIRM")

    # Allow Pro policy to override the required phrase.
    if isinstance(result, dict):
        pe = result.get("pro_enforcement") or {}
        override = pe.get("required_phrase") or pe.get("confirmation_phrase")
        if isinstance(override, str) and override.strip():
            phrase = override.strip()

    print("\n" + "-" * 40)
    print("[!] CONFIRMATION REQUIRED")
    print("-" * 40)
    print(f"This is a {safety_level} operation.\n")
    print("Type EXACTLY:")
    print(f"  {phrase}")
    print("to proceed, or anything else to cancel:")

    user_input = input("> ").strip()

    # Two-step assist: accept bare "YES" as a first step, then ask again.
    if user_input == "YES" and phrase != "YES":
        print("One more step: please copy/paste the required phrase exactly:")
        print(f"  {phrase}")
        user_input = input("> ").strip()

    if user_input != phrase:
        print("Exact match required (case + punctuation).")
        print(f"Required phrase: {phrase}\n")
        return False

    return True
