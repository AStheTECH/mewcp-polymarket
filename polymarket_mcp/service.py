"""Upstream API client for MewCP Polymarket MCP Server."""

import base64
import binascii
import logging
import time
from typing import Any

import requests
from fastmcp_credentials import get_credentials
from nacl.signing import SigningKey

from .config import (
    CONNECT_TIMEOUT,
    POLYMARKET_API_BASE,
    POLYMARKET_PUBLIC_API_BASE,
    READ_TIMEOUT,
)

logger = logging.getLogger("polymarket-mcp.service")


def _get_credential(field: str) -> str:
    cred = get_credentials()
    value = cred.fields.get(field) if cred.fields else None
    if not value:
        raise ValueError(f"Missing {field} credential")
    return value


def _signing_key(secret_key: str) -> SigningKey:
    try:
        key = base64.b64decode(secret_key)
    except (binascii.Error, ValueError):
        raise ValueError("Invalid secret_key credential: not valid base64") from None
    if len(key) == 64:
        key = key[:32]
    if len(key) != 32:
        raise ValueError("Invalid secret_key credential: expected a 32- or 64-byte Ed25519 key")
    return SigningKey(key)


def _auth_headers(method: str, path: str) -> dict[str, str]:
    key_id = _get_credential("key_id")
    signer = _signing_key(_get_credential("secret_key"))
    timestamp = str(int(time.time() * 1000))
    message = f"{timestamp}{method.upper()}{path}"
    signature = base64.b64encode(signer.sign(message.encode()).signature).decode()
    return {
        "X-PM-Access-Key": key_id,
        "X-PM-Timestamp": timestamp,
        "X-PM-Signature": signature,
        "Content-Type": "application/json",
    }


def _param_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    if not params:
        return None
    cleaned: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            cleaned[key] = [_param_value(v) for v in value if v is not None]
        else:
            cleaned[key] = _param_value(value)
    return cleaned or None


def _parse_retry_after(header: str | None) -> int | None:
    if not header:
        return None
    try:
        return int(header)
    except ValueError:
        return None


def api_request(
    method: str,
    endpoint: str,
    body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: tuple[int, int] | None = None,
    authenticated: bool = False,
) -> tuple[dict[str, Any], int, int | None]:
    if timeout is None:
        timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)
    if authenticated:
        url = f"{POLYMARKET_API_BASE}{endpoint}"
        headers = _auth_headers(method, endpoint)
    else:
        url = f"{POLYMARKET_PUBLIC_API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}
    resp = requests.request(method=method, url=url, headers=headers,
                            json=body, params=_clean_params(params), timeout=timeout)
    try:
        data = resp.json()
    except Exception:
        data = {"error": resp.text or "Empty response body"}
    return data, resp.status_code, _parse_retry_after(resp.headers.get("Retry-After"))
