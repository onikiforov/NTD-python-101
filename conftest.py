import collections.abc
import json
import logging
import re
import time
import uuid
from pathlib import Path

import allure
import pytest
import requests

from config import Config, load_config

logger = logging.getLogger(__name__)


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    try:
        load_config()
    except (RuntimeError, ValueError) as exc:
        pytest.exit(str(exc), returncode=1)


@pytest.fixture(scope="session")
def taiga_config() -> Config:
    return load_config()


@pytest.fixture(scope="session", autouse=True)
def logger_settings() -> None:
    # Set urllib3 logging level and disable child loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").propagate = False

    # Set requests logging level and disable child loggers
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("requests").propagate = False


def log_response_hook(
    response: requests.Response, *_args: object, **_kwargs: object
) -> None:
    request_headers = response.request.headers

    if "Authorization" in request_headers.keys():
        request_headers.pop("Authorization")

    request_data = {
        "method": response.request.method,
        "url": response.request.url,
        "headers": request_headers,
        "body": response.request.body
    }

    logger.debug("http_request: " + str(request_data))

    response_data = {
        "status_code": response.status_code,
        "elapsed_s": round(response.elapsed.total_seconds(), 3),
        "headers": response.headers
    }

    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        body = response.text

    response_data["body"] = body

    logger.debug("http_response: " + str(response_data))


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
        f"{taiga_config.base_url}/userstories",
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
