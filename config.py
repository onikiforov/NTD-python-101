import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    base_url: str
    username: str
    password: str
    project_id: int


def load_config() -> Config:
    load_dotenv(override=False)

    missing: list[str] = [
        var
        for var in ("TAIGA_USERNAME", "TAIGA_PASSWORD", "TAIGA_PROJECT_ID")
        if not os.environ.get(var, "").strip()
    ]
    if missing:
        raise RuntimeError(
            f"Missing or blank required env vars: {', '.join(missing)}. "
            "Check your .env file."
        )

    return Config(
        base_url=os.environ.get("TAIGA_BASE_URL", "https://api.taiga.io/api/v1").rstrip("/"),
        username=os.environ["TAIGA_USERNAME"].strip(),
        password=os.environ["TAIGA_PASSWORD"].strip(),
        project_id=int(os.environ["TAIGA_PROJECT_ID"].strip()),
    )
