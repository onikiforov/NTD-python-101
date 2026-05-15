import collections.abc
import logging
import re
from pathlib import Path

import pytest
import requests

from config import load_config

logger = logging.getLogger(__name__)

_SENSITIVE_KEYS = frozenset({
    "authorization", "cookie", "set-cookie", "proxy-authorization",
    "x-auth-token", "x-api-key", "x-csrf-token",
    "password", "auth_token", "refresh_token", "client_secret",
})
_AUTH_RE = re.compile(r"(authorization\s*[:=]\s*)(\S+)", re.IGNORECASE)
_BEARER_RE = re.compile(r"(Bearer\s+)([a-z0-9._\-]+)", re.IGNORECASE)


def _redact_str(s: str) -> str:
    s = _AUTH_RE.sub(r"\1***", s)
    s = _BEARER_RE.sub(r"\1***", s)
    return s


def _redact(value: object) -> object:
    if isinstance(value, str):
        return _redact_str(value)
    if isinstance(value, bytes):
        return _redact_str(value.decode("utf-8", errors="replace")).encode()
    if isinstance(value, collections.abc.Mapping):
        return {
            k: "***" if str(k).lower() in _SENSITIVE_KEYS else _redact(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        redacted = [_redact(v) for v in value]
        return type(value)(redacted)
    return value


class RedactAuthFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _redact_str(record.msg)
        if record.args:
            record.args = _redact(record.args)  # type: ignore[assignment]
        for key, val in list(record.__dict__.items()):
            if key.startswith("_") or key in {"msg", "args"}:
                continue
            record.__dict__[key] = _redact(val)
        return True


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    try:
        load_config()
    except (RuntimeError, ValueError) as exc:
        pytest.exit(str(exc), returncode=1)

    Path("logs").mkdir(exist_ok=True)

    redact = RedactAuthFilter()
    for handler in logging.root.handlers:
        handler.addFilter(redact)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def log_response_hook(
    response: requests.Response, *_args: object, **_kwargs: object
) -> None:
    logger.debug(
        "http_response",
        extra={
            "method": response.request.method,
            "url": response.request.url,
            "status_code": response.status_code,
            "elapsed_s": round(response.elapsed.total_seconds(), 3),
        },
    )
