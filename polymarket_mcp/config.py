"""Configuration for MewCP Polymarket MCP Server."""

import logging
import os

SERVER_VERSION = "v1.0.0"
BREAKING_CHANGES: list[dict] = []

POLYMARKET_API_BASE = "https://api.polymarket.us"  # authenticated
POLYMARKET_PUBLIC_API_BASE = "https://gateway.polymarket.us"  # public

CONNECT_TIMEOUT = 5    # TCP connection — fixed across all servers
READ_TIMEOUT = 30      # all endpoints are synchronous REST calls; 30s covers slow list/order responses


def configure_logging() -> None:
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    try:
        from pythonjsonlogger.json import JsonFormatter
        handler = logging.StreamHandler()
        handler.setFormatter(
            JsonFormatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")
        )
    except ImportError:
        handler = logging.StreamHandler()
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)
