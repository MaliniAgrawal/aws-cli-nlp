#!/usr/bin/env python3
# src/aws_nlp.py
"""
AWS NLP CLI — thin orchestrator.

Presentation  → src/cli/dry_run.py, src/core/cli_formatter.py
Confirmation  → src/cli/prompt.py
CI exit codes → src/cli/ci.py
Policy guard  → src/cli/policy_guard.py
Generation    → src/core/command_generator.py
Execution     → src/core/executor.py
History       → src/core/history.py
Clipboard     → src/core/clipboard.py
"""

import argparse
import json
import sys

from src.cli.ci import ci_exit_code
from src.cli.dry_run import print_dry_run, print_execute_hint
from src.cli.policy_guard import block_if_policy_denies
from src.cli.prompt import confirm_destructive_action
from src.core.cli_formatter import (
    format_agent,
    format_explain_only,
    format_human,
    format_json,
)
from src.core.command_generator import generate_command_sync
from src.core.registry import registry


def _handle_history(args) -> None:
    from src.core.history import read_history

    entries = read_history(limit=args.last or 20)
    if not entries:
        print("No command history found.")
        return

    svc = args.history_service.lower() if args.history_service else None
    lvl = args.history_safety.upper() if args.history_safety else None

    filtered = []
    for e in entries:
        if svc and (e.get("service") or "").lower() != svc:
            continue
        safety_val = (
            (e.get("safety") or {}).get("level")
            if isinstance(e.get("safety"), dict)
            else e.get("safety_level", "")
        )
        if lvl and (safety_val or "").upper() != lvl:
            continue
        filtered.append(e)

    if not filtered:
        print("No command history found.")
        return

    print("\nCommand History (most recent last)\n")
    for e in filtered:
        print(f"[{e.get('timestamp', '?')}]")
        print(f"  Query   : {e.get('query', '')}")
        print(f"  Intent  : {e.get('intent', '')}")
        print(f"  Service : {e.get('service', '')}")
        if e.get("safety_level"):
            print(f"  Safety  : {e.get('safety_level')}")
        mode = e.get("mode") or e.get("execution_mode") or "manual"
        print(f"  Allowed : {e.get('execution_allowed', False)} ({mode})")
        print("-" * 50)


def _record_history(args, result: dict) -> None:
    try:
        from src.core.history import record_history

        record_history(
            {
                "query": args.query,
                "command": result.get("command"),
                "intent": result.get("intent"),
                "service": result.get("meta", {}).get("service"),
                "safety_level": result.get("safety", {}).get("level"),
                "execution_allowed": False,
                "mode": "manual",
                "source": "cli",
            }
        )
    except Exception:
        pass


def _handle_clipboard(args, result: dict) -> None:
    if not args.copy or args.explain_only:
        return
    try:
        from src.core.clipboard import copy_to_clipboard

        ok, msg = copy_to_clipboard(result.get("command", ""))
        if args.format in ("json", "agent"):
            print(msg, file=sys.stderr)
        elif args.copy_verbose:
            print(msg)
    except Exception:
        if args.format in ("json", "agent"):
            print("\n[!] Clipboard copy failed (internal error).", file=sys.stderr)
        elif args.copy_verbose:
            print("\n[!] Clipboard copy failed (internal error).")


def _handle_execution(args, result: dict) -> None:
    from src.core.executor import ExecutionPolicy, execute_with_confirmation

    block_if_policy_denies(result)

    policy_map = {
        "allow_safe": ExecutionPolicy.ALLOW_SAFE,
        "require_confirmation": ExecutionPolicy.REQUIRE_CONFIRMATION,
        "block_destructive": ExecutionPolicy.BLOCK_DESTRUCTIVE,
        "block_all": ExecutionPolicy.BLOCK_ALL,
    }
    execution_policy = policy_map[args.policy]

    if args.no_prompt:
        print(
            "\n[!] --no-prompt blocks interactive execution."
            " Run without --no-prompt or remove --execute."
        )
        sys.exit(2)

    safety_level = result.get("safety", {}).get("level", "UNKNOWN")

    if args.format in (None, "human"):
        print(format_human(result, args.no_color))

    if not confirm_destructive_action(safety_level, result):
        print("\n[x] Operation cancelled by user.")
        sys.exit(1)

    result = execute_with_confirmation(
        generated_response=result, policy=execution_policy, dry_run=False
    )

    if args.format == "json":
        print(format_json(result))
        return
    if args.format == "agent":
        print(format_agent(result))
        return

    print(format_human(result, args.no_color))
    print("\n" + "=" * 70)
    print("EXECUTION RESULT")
    print("=" * 70)
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


def _build_parser() -> argparse.ArgumentParser:
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
        """,
    )
    parser.add_argument(
        "query", nargs="?", help="Natural language query (omit when using --history)"
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--format", choices=["human", "json", "agent", "explain"], default=None
    )
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--explain-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--policy",
        choices=[
            "allow_safe",
            "require_confirmation",
            "block_destructive",
            "block_all",
        ],
        default="require_confirmation",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--last", type=int, default=None)
    parser.add_argument("--copy", action="store_true")
    parser.add_argument("--copy-verbose", action="store_true")
    parser.add_argument("--history-service", type=str, default=None)
    parser.add_argument("--history-safety", type=str, default=None)
    parser.add_argument("--no-prompt", action="store_true")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI/CD mode: non-interactive, never executes, "
        "exits with policy-based code",
    )
    parser.add_argument(
        "--allow-confirm",
        action="store_true",
        help="In --ci mode, exit 0 instead of 2 for confirm-required ops",
    )
    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    # Resolve output format
    if args.format is None:
        if args.explain_only:
            args.format = "explain"
        elif getattr(args, "json", False):
            args.format = "json"
        else:
            args.format = "human"

    if args.format in ("json", "agent", "explain"):
        args.no_prompt = True

    if args.format == "agent" and getattr(args, "execute", False):
        print(
            "[!] --format agent is output-only and does not support --execute.",
            file=sys.stderr,
        )
        sys.exit(2)

    if not args.query and not args.history:
        parser.print_help()
        sys.exit(2)

    # History display — short-circuits before generation
    is_history_query = bool(args.query and args.query.strip().lower() == "history")
    if args.history or is_history_query:
        try:
            _handle_history(args)
        except Exception:
            print("Failed to read history.")
        return

    # Ensure registry is ready
    if not registry.services:
        registry.autodiscover()

    result = generate_command_sync(args.query)

    # CI mode — emit JSON + stderr summary, then exit
    if args.ci:
        print(json.dumps(result, indent=2))
        fail_on_confirm = not args.allow_confirm
        pe = result.get("pro_enforcement") or {}
        decision = (pe.get("decision") or "allow").lower()
        reason = pe.get("reason") or ""
        safety_level = ((result.get("safety") or {}).get("level") or "UNKNOWN").upper()
        code = ci_exit_code(result, fail_on_confirm=fail_on_confirm)
        print(
            f"[CI] safety={safety_level} decision={decision} exit_code={code}"
            + (f" reason={reason}" if reason else ""),
            file=sys.stderr,
        )
        sys.exit(code)

    # Agent format — JSON only, no prompts
    if args.format == "agent":
        _handle_clipboard(args, result)
        print(format_agent(result))
        return

    _handle_clipboard(args, result)

    if not args.explain_only:
        _record_history(args, result)

    # Dry-run — show preview, no execution
    if args.dry_run:
        print_dry_run(result, args.no_color)
        return

    # Execution path
    if args.execute:
        _handle_execution(args, result)
        return

    # Display-only path
    if args.format == "json":
        print(format_json(result))
        return
    if args.format == "agent":
        print(format_agent(result))
        return
    if args.explain_only or args.format == "explain":
        print(format_explain_only(result, args.no_color))
        return

    print(format_human(result, args.no_color))

    if not args.no_prompt:
        if not sys.stdin.isatty():
            print_execute_hint(args.query)
            return
        execute_prompt = input("\n\nExecute this command? (y/n): ").strip().lower()
        if execute_prompt in ["y", "yes"]:
            print_execute_hint(args.query)
        else:
            print("\nCommand not executed.")
