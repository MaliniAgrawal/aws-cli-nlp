#!/usr/bin/env python3
# src/aws_nlp.py
"""
AWS NLP CLI - Human-friendly command-line interface
Usage:
  aws-nlp "list s3 buckets"
  aws-nlp --json "list s3 buckets"
  aws-nlp --no-color "list s3 buckets"
  aws-nlp --explain-only "list s3 buckets"
"""
import sys
import argparse
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.command_generator import generate_command_sync
from src.core.cli_formatter import format_human, format_json, format_explain_only, format_agent
from src.core.registry import registry

# Impact descriptions for common operations
IMPACT_DESCRIPTIONS = {
    "delete_s3_bucket": [
        "This will permanently delete the S3 bucket",
        "All objects in the bucket will be removed",
        "This action cannot be undone"
    ],
    "terminate_instance": [
        "This will terminate the specified instance(s)",
        "Data on instance stores will be lost",
        "This action cannot be undone"
    ],
    "delete_iam": [
        "This will modify IAM permissions",
        "Changes may affect access control",
        "Review security implications carefully"
    ],
    "create_iam_user": [
        "Creates a new IAM user",
        "User initially has no permissions",
        "Policies can be attached later"
    ]
}

def _get_impact_preview(command: str, intent: str) -> list:
    """Get impact preview based on command and intent."""
    command_lower = command.lower()
    intent_lower = intent.lower()
    
    # Match against known patterns
    if "delete" in intent_lower and "s3" in command_lower:
        return IMPACT_DESCRIPTIONS.get("delete_s3_bucket", [])
    elif "terminate" in command_lower or "terminate" in intent_lower:
        return IMPACT_DESCRIPTIONS.get("terminate_instance", [])
    elif "iam" in command_lower and ("delete" in command_lower or "remove" in command_lower):
        return IMPACT_DESCRIPTIONS.get("delete_iam", [])
    elif "iam" in command_lower and "create" in intent_lower and "user" in intent_lower:
        return IMPACT_DESCRIPTIONS.get("create_iam_user", [])
    
    return []

def _print_execute_hint(query: str) -> None:
    print("\nTo execute this command, rerun with --execute:")
    print(f'  python aws-nlp.py "{query}" --execute')

def confirm_destructive_action(safety_level: str, result: dict | None = None) -> bool:
    """
    Prompt user for explicit confirmation for risky operations.

    - SAFE: no prompt required
    - MUTATING: optional phrase
    - SECURITY_SENSITIVE: phrase required
    - DESTRUCTIVE: phrase required

    If Pro policy provides a phrase override, use it.
    """
    # Only prompt for risky ops
    if safety_level not in ("MUTATING", "SECURITY_SENSITIVE", "DESTRUCTIVE"):
        return True

    # Default phrases (Free baseline)
    default_phrases = {
        "MUTATING": "YES, APPLY",
        "SECURITY_SENSITIVE": "YES, MODIFY IAM",
        "DESTRUCTIVE": "YES, DELETE",
    }

    # Optional Pro override (future-ready)
    phrase = default_phrases.get(safety_level, "YES, CONFIRM")

    # If you later add something like result["pro_enforcement"]["required_phrase"], prefer it
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

    # 2-step assist: allow "YES" as a first step when the required phrase is longer.
    # Still requires exact phrase before proceeding.
    if user_input == "YES" and phrase != "YES":
        print("One more step: please copy/paste the required phrase exactly:")
        print(f"  {phrase}")
        user_input = input("> ").strip()

    if user_input != phrase:
        print("Exact match required (case + punctuation).")
        print(f"Required phrase: {phrase}\n")
        return False

    return True

def _pro_block_if_needed(result: dict) -> None:
    pe = result.get("pro_enforcement") or {}
    if not pe.get("enabled"):
        return

    decision = (pe.get("decision") or "allow").lower()
    if decision == "block":
        reason = pe.get("reason") or "Blocked by org policy"
        print(f"\nBLOCKED by org-policy: {reason}")
        print("This block cannot be overridden. Update org-policy.json to change behavior.")
        sys.exit(3)  # policy block

def ci_exit_code(result: dict, fail_on_confirm: bool = True) -> int:
    """
    CI mode exit codes:
      0 = allowed
      2 = requires confirmation / approval
      3 = blocked by policy
      4 = unsupported/unknown intent
      5 = internal error
    """
    try:
        intent = (result.get("intent") or "").lower()
        safety = result.get("safety") or {}
        level = (safety.get("level") or "UNKNOWN").upper()

        # Unsupported / unknown intent
        if intent in ("unknown", "unsupported_intent", "") or level == "UNKNOWN":
            return 4

        # Prefer Pro enforcement if present
        pe = result.get("pro_enforcement") or {}
        if pe.get("enabled"):
            decision = (pe.get("decision") or "allow").lower()
            if decision == "block":
                return 3
            if decision == "confirm" and fail_on_confirm:
                return 2

        # Fallback to safety when Pro not enabled
        if fail_on_confirm and level in ("MUTATING", "DESTRUCTIVE", "SECURITY_SENSITIVE"):
            return 2

        return 0

    except Exception:
        return 5

def main():
    parser = argparse.ArgumentParser(
        prog="aws-nlp",
        description="Generate AWS CLI commands from natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aws-nlp "list s3 buckets"
  aws-nlp --json "delete s3 bucket old-bucket"
  aws-nlp --no-color "create ec2 instance"
  aws-nlp --explain-only "list lambda functions"
        """
    )
    
    parser.add_argument(
        "query",
        nargs='?',
        help="Natural language query for AWS operation (omit when using --history)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (for scripting/MCP)"
    )

    parser.add_argument(
        "--format",
        choices=["human", "json", "agent", "explain"],
        default=None,
        help="Output format: human (default), json, agent (IDE-friendly), explain"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    parser.add_argument(
        "--explain-only",
        action="store_true",
        help="Show explanation only, no command"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the generated command (requires confirmation for destructive ops)"
    )
    
    parser.add_argument(
        "--policy",
        choices=["allow_safe", "require_confirmation", "block_destructive", "block_all"],
        default="require_confirmation",
        help="Execution policy (default: require_confirmation)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running the command"
    )

    parser.add_argument(
        "--history",
        action="store_true",
        help="Show local command history (CLI only)"
    )

    parser.add_argument(
        "--last",
        type=int,
        default=None,
        help="Limit history entries (used with --history)"
    )

    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy the generated command to clipboard"
    )

    parser.add_argument(
        "--copy-verbose",
        action="store_true",
        help="When used with --copy, prints clipboard status message (stderr in --json mode)."
    )

    parser.add_argument(
        "--history-service",
        type=str,
        default=None,
        help="Filter history by service (used with 'history')"
    )

    parser.add_argument(
        "--history-safety",
        type=str,
        default=None,
        help="Filter history by safety level (SAFE/MUTATING/DESTRUCTIVE/SECURITY_SENSITIVE) (used with 'history')"
    )

    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Never prompt; output only (no execution)."
    )

    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI/CD mode: non-interactive, never executes, prints JSON and exits with policy-based code"
    )
    parser.add_argument(
        "--allow-confirm",
        action="store_true",
        help="In --ci mode, allow confirmation-required actions (exit 0 instead of 2)"
    )
    
    args = parser.parse_args()

    # Backward compatible flags -> format
    if args.format is None:
        if args.explain_only:
            args.format = "explain"
        elif getattr(args, "json", False):
            args.format = "json"
        else:
            args.format = "human"

    # Never prompt in machine-friendly modes
    if args.format in ("json", "agent", "explain"):
        args.no_prompt = True

    # Safety: agent mode is output-only; block --execute in agent mode
    if args.format == "agent" and getattr(args, "execute", False):
        print("[!] --format agent is output-only and does not support --execute.", file=sys.stderr)
        sys.exit(2)

    if not args.query and not args.history:
        parser.print_help()
        sys.exit(2)

    # Short-circuit: handle history display (do not generate commands or record history)
    is_history_query = bool(args.query and args.query.strip().lower() == "history")
    if args.history or is_history_query:
        try:
            from src.core.history import read_history

            entries = read_history(limit=args.last or 20)
            if not entries:
                print("No command history found.")
                return

            # Apply filters if provided
            svc = args.history_service.lower() if args.history_service else None
            lvl = args.history_safety.upper() if args.history_safety else None

            filtered = []
            for e in entries:
                if svc and (e.get("service") or "").lower() != svc:
                    continue
                # Support both legacy flat 'safety_level' and nested 'safety': {"level": ...}
                safety_val = (e.get("safety") or {}).get("level") if isinstance(e.get("safety"), dict) else e.get("safety_level", "")
                if lvl and (safety_val or "").upper() != lvl:
                    continue
                filtered.append(e)

            entries = filtered

            if not entries:
                print("No command history found.")
                return

            print("\nCommand History (most recent last)\n")
            for e in entries:
                ts = e.get("timestamp", "?")
                query = e.get("query", "")
                intent = e.get("intent", "")
                service = e.get("service", "")
                safety = e.get("safety_level", "")
                allowed = e.get("execution_allowed", False)
                mode = e.get("mode") or e.get("execution_mode") or "manual"

                print(f"[{ts}]")
                print(f"  Query   : {query}")
                print(f"  Intent  : {intent}")
                print(f"  Service : {service}")
                if safety:
                    print(f"  Safety  : {safety}")
                print(f"  Allowed : {allowed} ({mode})")
                print("-" * 50)
            return
        except Exception:
            print("Failed to read history.")
            return

    # Initialize registry
    if not registry.services:
        registry.autodiscover()
    
    # Generate command
    result = generate_command_sync(args.query)

    # ---------------------------
    # CI/CD Mode (strict by default)
    # ---------------------------
    if args.ci:
        # Always output machine-readable JSON
        print(json.dumps(result, indent=2))

        # strict by default: confirm => exit 2
        fail_on_confirm = not args.allow_confirm

        pe = result.get("pro_enforcement") or {}
        decision = (pe.get("decision") or "allow").lower()
        reason = pe.get("reason") or ""
        safety_level = ((result.get("safety") or {}).get("level") or "UNKNOWN").upper()

        code = ci_exit_code(result, fail_on_confirm=fail_on_confirm)

        # Human-readable summary to stderr (doesn't pollute JSON stdout)
        print(
            f"[CI] safety={safety_level} decision={decision} exit_code={code}"
            + (f" reason={reason}" if reason else ""),
            file=sys.stderr
        )

        sys.exit(code)

    # Agent format: strict JSON only (no prompt, no execute)
    if args.format == "agent":
        from src.core.cli_formatter import format_agent
        out = format_agent(result)

        # Clipboard copy still allowed, but stay silent by default
        if args.copy and not args.explain_only:
            from src.core.clipboard import copy_to_clipboard
            ok, msg = copy_to_clipboard(result.get("command", ""))
            if args.copy_verbose:
                print(msg, file=sys.stderr)

        print(out)
        return

    # Clipboard copy (Phase C.2)
    if args.copy and not args.explain_only:
        try:
            from src.core.clipboard import copy_to_clipboard
            ok, msg = copy_to_clipboard(result.get("command", ""))

            # FIX 1: Always print to stderr for JSON/agent format
            if args.format in ("json", "agent"):
                print(msg, file=sys.stderr)
            elif args.copy_verbose:
                print(msg)
        except Exception:
            if args.format in ("json", "agent"):
                print("\n[!] Clipboard copy failed (internal error).", file=sys.stderr)
            elif args.copy_verbose:
                print("\n[!] Clipboard copy failed (internal error).")

    # Record history for CLI usage only (Phase C.1)
    # Do not record when explain-only requested
    if not args.explain_only:
        try:
            from src.core.history import record_history

            record_history({
                "query": args.query,
                "command": result.get("command"),
                "intent": result.get("intent"),
                "service": result.get("meta", {}).get("service"),
                "safety_level": result.get("safety", {}).get("level"),
                "execution_allowed": False,
                "mode": "manual",
                "source": "cli",
            })
        except Exception:
            # History recording must never break CLI
            pass
    
    # DRY RUN MODE: Show command + impact preview, no execution, no prompt
    if args.dry_run:
        from src.core.cli_formatter import Colors, _get_color
        
        command = result.get("command", "")
        intent = result.get("intent", "")
        safety_level = result.get("safety", {}).get("level", "UNKNOWN")
        
        # Color setup
        bold = _get_color(Colors.BOLD, args.no_color)
        cyan = _get_color(Colors.CYAN, args.no_color)
        reset = _get_color(Colors.RESET, args.no_color)
        
        # Safety level colors
        if safety_level == "SAFE":
            safety_color = _get_color(Colors.GREEN, args.no_color)
        elif safety_level == "MUTATING":
            safety_color = _get_color(Colors.YELLOW, args.no_color)
        elif safety_level in ("DESTRUCTIVE", "SECURITY_SENSITIVE"):
            safety_color = _get_color(Colors.RED, args.no_color)
        else:
            safety_color = _get_color(Colors.GRAY, args.no_color)
        
        print(f"{bold}Command:{reset}")
        print(f"  {cyan}{command}{reset}")
        print(f"\n{bold}Safety:{reset}")
        print(f"  {safety_color}{safety_level}{reset}")
        
        # Impact Preview for destructive operations
        if safety_level in ("DESTRUCTIVE", "SECURITY_SENSITIVE", "MUTATING"):
            impact_items = _get_impact_preview(command, intent)
            if impact_items:
                print(f"\n{bold}Impact Preview:{reset}")
                for item in impact_items:
                    print(f"  • {item}")
        
        print(f"\n{bold}Status:{reset}")
        print("  DRY RUN – command not executed")
        return
    
    # Handle execution if requested
    if args.execute:
        from src.core.executor import execute_with_confirmation, ExecutionPolicy

        _pro_block_if_needed(result)
        
        # Map policy string to enum
        policy_map = {
            "allow_safe": ExecutionPolicy.ALLOW_SAFE,
            "require_confirmation": ExecutionPolicy.REQUIRE_CONFIRMATION,
            "block_destructive": ExecutionPolicy.BLOCK_DESTRUCTIVE,
            "block_all": ExecutionPolicy.BLOCK_ALL
        }
        execution_policy = policy_map[args.policy]

        # Respect --no-prompt: block interactive execution in scripted/non-interactive use
        if args.no_prompt:
            print("\n[!] --no-prompt blocks interactive execution. Run without --no-prompt or remove --execute.")
            sys.exit(2)

        # Check if confirmation needed
        safety_level = result.get("safety", {}).get("level", "UNKNOWN")
        
        # Display the generated command first (human mode only)
        if args.format in (None, "human"):
            print(format_human(result, args.no_color))
        
        # Phase B.3.2: Explicit confirmation for destructive/mutating/security-sensitive operations
        confirmed = confirm_destructive_action(safety_level, result)
        if not confirmed:
            print("\n[x] Operation cancelled by user.")
            sys.exit(1)
        
        # Execute with policy
        result = execute_with_confirmation(
            generated_response=result,
            policy=execution_policy,
            dry_run=False
        )
        
        # Show execution result
        if args.format == "json":
            print(format_json(result))
            return
        elif args.format == "agent":
            print(format_agent(result))
            return
        else:
            print(format_human(result, args.no_color))
            print("\n" + "="*70)
            print("EXECUTION RESULT")
            print("="*70)
            exec_result = result.get("execution", {})
            if exec_result.get("blocked"):
                print(f"[BLOCKED] {exec_result.get('reason')}")
            elif exec_result.get("success"):
                print(f"[OK] {exec_result.get('reason')}")
                if exec_result.get("stdout"):
                    print(f"\nOutput:\n{exec_result.get('stdout')}")
            else:
                print(f"[FAILED] {exec_result.get('reason')}")
                if exec_result.get("stderr"):
                    print(f"\nError:\n{exec_result.get('stderr')}")
    else:
        # Format output based on flags (no execution)
        if args.format == "json":
            print(format_json(result))
            return
        elif args.format == "agent":
            print(format_agent(result))
            return
        elif args.explain_only or args.format == "explain":
            print(format_explain_only(result, args.no_color))
        else:
            print(format_human(result, args.no_color))
            
            # Optional interactive prompt only in human mode
            if not args.no_prompt:
                # If we're not in an interactive terminal (pytest/CI), don't prompt.
                if not sys.stdin.isatty():
                    _print_execute_hint(args.query)
                    return

                execute_prompt = input("\n\nExecute this command? (y/n): ").strip().lower()
                if execute_prompt in ["y", "yes"]:
                    _print_execute_hint(args.query)
                else:
                    print("\nCommand not executed.")
            else:
                return
