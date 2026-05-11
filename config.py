import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

@dataclass(frozen=True)
class Config:
    base_url: str
    username: str
    password: str = field(repr=False)
    project_id: int


def load_config() -> Config:
    load_dotenv(override=False)

    project_id = os.environ.get("TAIGA_PROJECT_ID", None)
    if not project_id:
        raise RuntimeError("Project id cannot be empty!")
    try:
        project_id = int(project_id)
    except ValueError:
        raise RuntimeError(
            f"TAIGA_PROJECT_ID must be an integer, got: {project_id!r}"
        )

    base_url = os.environ.get("TAIGA_BASE_URL", None)
    if not base_url:
        raise RuntimeError("Base URL cannot be empty!")
    base_url = base_url.strip()

    username = os.environ.get("TAIGA_USERNAME", None)
    if not username:
        raise RuntimeError("Username cannot be empty")

    password = os.environ.get("TAIGA_PASSWORD", None)
    if not password:
        raise RuntimeError("Password cannot be empty")


    return Config(
        base_url=base_url,
        username=username,
        password=password,
        project_id=project_id,
    )
