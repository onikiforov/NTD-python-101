import collections.abc
import json
import logging
import logging.config
import os
import re
import time
import uuid
from pathlib import Path

import pytest
import requests

from config import Config, load_config

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


def _redact(value: object):
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
    def filter(self, record: logging.LogRecord):
        if isinstance(record.msg, str):
            record.msg = _redact_str(record.msg)
        if record.args:
            record.args = _redact(record.args)  # type: ignore[assignment]
        for key, val in record.__dict__.items():
            if key.startswith("_") or key in {"msg", "args"}:
                continue
            record.__dict__[key] = _redact(val)
        return True


def _build_logging_config(log_file: Path):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "redact_auth": {"()": RedactAuthFilter},
        },
        "formatters": {
            "console": {
                "format": "%(levelname)s %(name)s %(message)s",
            },
            "file": {
                "format": "%(asctime)s %(levelname)s %(name)s %(method)s %(url)s %(status_code)s %(elapsed_s)s %(message)s",
                "defaults": {
                    "method": "-",
                    "url": "-",
                    "status_code": "-",
                    "elapsed_s": "-",
                },
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
        "loggers": {
            "urllib3": {"level": "WARNING", "propagate": True},
            "requests": {"level": "WARNING", "propagate": True},
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        },
    }


def pytest_configure() -> None:  # noqa: ARG001
    try:
        load_config()
    except (RuntimeError, ValueError) as exc:
        pytest.exit(str(exc), returncode=1)

    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f"test-run-{int(time.time())}-{os.getpid()}.log"

    logging.config.dictConfig(_build_logging_config(log_file))
    os.chmod(log_file, 0o600)


@pytest.fixture(scope="session")
def taiga_config() -> Config:
    return load_config()


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


@pytest.fixture(scope="session")
def taiga_session(taiga_config: Config) -> requests.Session:
    resp = requests.post(
        f"{taiga_config.base_url}/auth",
        json={"username": taiga_config.username, "password": taiga_config.password, "type": "normal"},
        timeout=10,
    )
    resp.raise_for_status()
    session = requests.Session()
    session.hooks["response"].append(log_response_hook)
    session.headers["Authorization"] = f"Bearer {resp.json()['auth_token']}"
    return session


# This fixture is called explicitly
@pytest.fixture(scope="function")
def created_user_story(taiga_session: requests.Session, taiga_config: Config):
    """POST a new User Story and yield its response dict. No teardown.

    Tests are responsible for calling delete_user_story(story["id"]) to clean up.
    If a test fails before cleanup, the story leaks into the project — this is
    intentional: it shows why teardown fixtures matter.
    """
    resp = taiga_session.post(
        f"{taiga_config.base_url}/userstories",
        json={
            "project": taiga_config.project_id,
            "subject": f"Workshop US [{uuid.uuid4().hex[:8]}]",
        },
        timeout=10,
    )
    resp.raise_for_status()
    yield resp.json()


# This fixture is called explicitly
@pytest.fixture(scope="function")
def delete_user_story(taiga_session: requests.Session, taiga_config: Config):
    def delete(story_id: int) -> None:
        resp = taiga_session.delete(
            f"{taiga_config.base_url}/userstories/{story_id}",
            timeout=10,
        )
        assert resp.status_code == 204, f"Expected 204 on delete, got {resp.status_code}: {resp.text}"

    yield delete


@pytest.fixture(scope="function")
def user_story(taiga_session: requests.Session, taiga_config: Config):
    """POST a new User Story, yield its response dict, then DELETE it on teardown.

    Teardown runs even if the test fails — no leaked stories.
    Use this instead of created_user_story + delete_user_story when the test
    does not need to assert the DELETE itself.
    """
    resp = taiga_session.post(
        f"{cfg.base_url}/userstories",
        json={
            "project": taiga_config.project_id,
            "subject": f"Workshop US [{uuid.uuid4().hex[:8]}]",
        },
        timeout=10,
    )
    resp.raise_for_status()
    story = resp.json()
    yield story
    taiga_session.delete(f"{taiga_config.base_url}/userstories/{story['id']}", timeout=10)


@pytest.fixture(scope="session")
def user_story_schema() -> dict:
    path = Path(__file__).parent / "schemas" / "user_story.schema.json"
    with path.open() as fh:
        return json.load(fh)
