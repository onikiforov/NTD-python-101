import logging
import logging.config
import time
from pathlib import Path
from typing import Any

import pytest
import requests

from config import load_config

logger = logging.getLogger(__name__)


class RedactAuthFilter(logging.Filter):
    """Redacts Authorization header values from log records before emit."""

    def filter(self, record: logging.LogRecord) -> bool:
        for value in record.__dict__.values():
            if isinstance(value, dict):
                for key in list(value.keys()):
                    if key.lower() == "authorization":
                        value[key] = "***"
        return True


def _build_logging_config(log_file: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "redact_auth": {
                "()": RedactAuthFilter,
            }
        },
        "formatters": {
            "console": {
                "format": "%(levelname)s %(name)s %(message)s",
            },
            "file": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
                "filters": ["redact_auth"],
            },
            "file": {
                "class": "logging.FileHandler",
                "level": "DEBUG",
                "formatter": "file",
                "filters": ["redact_auth"],
                "filename": str(log_file),
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    }


def pytest_configure(_config: pytest.Config) -> None:
    try:
        load_config()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=1)

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f"test-run-{int(time.time())}.log"

    logging.config.dictConfig(_build_logging_config(log_file))


def log_response_hook(
    response: requests.Response, *_args: object, **_kwargs: object
) -> None:
    logger.debug(
        "http_response",
        extra={
            "method": response.request.method,
            "url": response.request.url,
            "status_code": response.status_code,
            "elapsed_s": response.elapsed.total_seconds(),
        },
    )
