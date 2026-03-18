# src/mcp_server.py
import argparse
import asyncio
import os
import sys

USE_HAIKU = bool(os.getenv("USE_HAIKU", "false").lower() in ["true", "1", "yes"])

from fastmcp import FastMCP  # noqa: E402

from src.core.cli_formatter import format_mcp_response  # noqa: E402
from src.core.command_generator import (  # noqa: E402
    generate_command,
    list_supported_services,
)
from src.core.logging_utils import setup_logger  # noqa: E402
from src.core.registry import registry  # noqa: E402
from src.core.telemetry import telemetry_log_event  # noqa: E402

logger = setup_logger("aws-cli-generator-phase-a")

registry.autodiscover()

mcp = FastMCP("aws-cli-generator")


@mcp.tool()
async def generate_aws_cli(query: str):
    """
    Generate AWS CLI command from natural language query.

    This tool NEVER executes commands. It only generates command strings
    for human review and manual execution.

    Returns a stable JSON payload (see docs/MCP_CONTRACT.md):
      - command: the AWS CLI string to copy and run
      - intent: detected operation
      - service: AWS service name
      - safety.level: SAFE | MUTATING | SECURITY_SENSITIVE | DESTRUCTIVE
      - safety.requires_confirmation: bool
      - execution.allowed: always False
      - execution.mode: always "manual"
    """
    result = await generate_command(query)

    # Execution block is unconditional — allowed is always False in MCP.
    result["execution"] = {"allowed": False, "mode": "manual"}

    formatted = format_mcp_response(result)

    telemetry_log_event(
        "response.emitted",
        {
            "result_summary": {
                "intent": result["intent"],
                "safety_level": result["safety"].get("level"),
                "execution_mode": "manual",
                "format": "mcp",
            }
        },
    )

    return formatted


@mcp.tool()
async def health_check():
    return {"status": "ok", "model": "haiku" if USE_HAIKU else "local-transformer"}


@mcp.tool()
async def list_supported_services_mcp():
    return list_supported_services()


async def run_stdio():
    logger.info("Starting MCP stdio server")
    await mcp.run_stdio_async()


def main():
    parser = argparse.ArgumentParser(
        description="AWS CLI Assistant MCP server (stdio only)"
    )
    parser.add_argument(
        "--mode",
        default="mcp",
        help="Compatibility flag. Only 'mcp' is supported in Free v1.",
    )
    parser.add_argument(
        "--http", action="store_true", help="Deprecated and unsupported in Free v1."
    )
    args = parser.parse_args()

    if args.http or str(args.mode).lower() != "mcp":
        print(
            "[!] Free v1 supports MCP stdio mode only. Use: python -m src.mcp_server",
            file=sys.stderr,
        )
        sys.exit(2)

    print("[MCP] Starting MCP stdio server...", file=sys.stderr)
    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()

__all__ = ["generate_aws_cli", "list_supported_services_mcp", "health_check"]
