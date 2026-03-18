# src/core/telemetry.py
import time

from loguru import logger


def telemetry_log_event(event_name: str, details: dict):
    payload = {
        "timestamp": int(time.time() * 1000),
        "event": event_name,
        "details": details,
    }
    # log as JSON (loguru will serialize)
    logger.info(payload)
