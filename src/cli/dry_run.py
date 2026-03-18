# src/cli/dry_run.py
"""
Dry-run terminal presentation and execute-hint helper.
No I/O side-effects other than print(); no sys.exit().
"""

from src.core.cli_formatter import Colors, _get_color

IMPACT_DESCRIPTIONS = {
    "delete_s3_bucket": [
        "This will permanently delete the S3 bucket",
        "All objects in the bucket will be removed",
        "This action cannot be undone",
    ],
    "terminate_instance": [
        "This will terminate the specified instance(s)",
        "Data on instance stores will be lost",
        "This action cannot be undone",
    ],
    "delete_iam": [
        "This will modify IAM permissions",
        "Changes may affect access control",
        "Review security implications carefully",
    ],
    "create_iam_user": [
        "Creates a new IAM user",
        "User initially has no permissions",
        "Policies can be attached later",
    ],
}


def get_impact_preview(command: str, intent: str) -> list:
    command_lower = command.lower()
    intent_lower = intent.lower()

    if "delete" in intent_lower and "s3" in command_lower:
        return IMPACT_DESCRIPTIONS.get("delete_s3_bucket", [])
    if "terminate" in command_lower or "terminate" in intent_lower:
        return IMPACT_DESCRIPTIONS.get("terminate_instance", [])
    if "iam" in command_lower and (
        "delete" in command_lower or "remove" in command_lower
    ):
        return IMPACT_DESCRIPTIONS.get("delete_iam", [])
    if "iam" in command_lower and "create" in intent_lower and "user" in intent_lower:
        return IMPACT_DESCRIPTIONS.get("create_iam_user", [])
    return []


def print_dry_run(result: dict, no_color: bool = False) -> None:
    """Print dry-run output: command, safety level, impact preview."""
    command = result.get("command", "")
    intent = result.get("intent", "")
    safety_level = result.get("safety", {}).get("level", "UNKNOWN")

    bold = _get_color(Colors.BOLD, no_color)
    cyan = _get_color(Colors.CYAN, no_color)
    reset = _get_color(Colors.RESET, no_color)

    if safety_level == "SAFE":
        safety_color = _get_color(Colors.GREEN, no_color)
    elif safety_level == "MUTATING":
        safety_color = _get_color(Colors.YELLOW, no_color)
    elif safety_level in ("DESTRUCTIVE", "SECURITY_SENSITIVE"):
        safety_color = _get_color(Colors.RED, no_color)
    else:
        safety_color = _get_color(Colors.GRAY, no_color)

    print(f"{bold}Command:{reset}")
    print(f"  {cyan}{command}{reset}")
    print(f"\n{bold}Safety:{reset}")
    print(f"  {safety_color}{safety_level}{reset}")

    if safety_level in ("DESTRUCTIVE", "SECURITY_SENSITIVE", "MUTATING"):
        items = get_impact_preview(command, intent)
        if items:
            print(f"\n{bold}Impact Preview:{reset}")
            for item in items:
                print(f"  • {item}")

    print(f"\n{bold}Status:{reset}")
    print("  DRY RUN – command not executed")


def print_execute_hint(query: str) -> None:
    print("\nTo execute this command, rerun with --execute:")
    print(f'  python aws-nlp.py "{query}" --execute')
