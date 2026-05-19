import logging
import pytest
import requests

from config import load_config, Config

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def cfg() -> Config:  # noqa: ARG001
    try:
        return load_config()
    except (RuntimeError, ValueError) as exc:
        pytest.exit(str(exc), returncode=1)


@pytest.fixture(scope="session", autouse=True)
def logger_settings() -> None:
    # Set urllib3 logging level and disable child loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").propagate = False

    # Set requests logging level and disable child loggers
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("requests").propagate = False


@pytest.fixture(scope="session")
def taiga_config():
    return load_config()


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
