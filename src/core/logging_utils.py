import os
import sys
from pathlib import Path
from loguru import logger


def setup_logger(app_name: str):
    """
    Safe, cross-platform log directory:
    - Windows: %LOCALAPPDATA%\<app_name>\telemetry\telemetry.log
    - Linux/macOS: ~/.local/share/<app_name>/telemetry/telemetry.log
    Also mirrors logs to stderr (so Claude logs show them).
    """

    if os.name == "nt":
        base_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    else:
        base_dir = Path.home() / ".local" / "share"

    log_dir = base_dir / app_name / "telemetry"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "telemetry.log"

    # Remove default handler(s) to avoid duplicates
    logger.remove()

    # 1) File logging (structured JSON)
    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="30 days",
        serialize=True,
        level="INFO",
    )

    # 2) Console logging (shows in Claude MCP logs) - MUST use stderr for MCP stdio
    logger.add(
        sys.stderr,
        level="INFO",
    )

    logger.info(f"Logging initialized. File={log_file}")
    return logger
