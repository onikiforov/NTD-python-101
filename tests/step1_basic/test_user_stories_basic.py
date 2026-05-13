"""
Step-1 basic tests: GET and POST against Taiga User Stories API.

Intentional limitations (teaching moments for step-2):
- Login is performed inline in every test — no shared auth fixture.
- POST tests do NOT clean up created User Stories. Running this suite
  multiple times accumulates stories in the parent project. Use a
  throwaway project or clean up manually via the Taiga UI.
- No parametrization, no external test data.
"""

import json
import uuid

import allure
import pytest
import requests
from requests import Session, Response

from config import Config
from conftest import log_response_hook

_USER_STORY_REQUIRED_KEYS = {"id", "subject", "project"}


class TestUserStoriesBasic:
    @staticmethod
    def _login(cfg: Config) -> requests.Session:
        """Perform inline login and return a session with auth headers attached."""
        resp = requests.post(
            f"{cfg.base_url}/auth",
            json={
                "username": cfg.username,
                "password": cfg.password,
                "type": "normal",
            },
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json()["auth_token"]

        session = requests.Session()
        session.hooks["response"].append(log_response_hook)
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session

    @staticmethod
    def create_us(taiga_config: Config, session: Session) -> tuple[Response, str]:
        """Creates User Story as a pre-condition and returns it's title"""
        us_subject = f"Workshop step-1 user story {uuid.uuid4().hex[:8]}"

        resp = session.post(
            f"{taiga_config.base_url}/userstories",
            json={"project": taiga_config.project_id, "subject": us_subject},
            timeout=10,
        )
        resp.raise_for_status()

        return resp, us_subject

    @pytest.mark.smoke
    @allure.feature("User Stories")
    @allure.story("Basic")
    def test_list_user_stories_returns_200(self, taiga_config: Config) -> None:
        with allure.step("Login"):
            session = self._login(taiga_config)

        with allure.step("Create new User Story"):
            # Creates new User Story so the list is never empty
            _, us_subject = self.create_us(taiga_config, session)

        with allure.step("Fetch user stories list"):
            resp = session.get(
                f"{taiga_config.base_url}/userstories",
                params={"project": taiga_config.project_id},
                timeout=10,
            )
            resp.raise_for_status()

        with allure.step("Assert response"):
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert isinstance(data, list), (
                f"Expected list, got {type(data).__name__}: {data!r}"
            )

            assert us_subject in [item["subject"] for item in data]

    @pytest.mark.smoke
    @allure.feature("User Stories")
    @allure.story("Basic")
    def test_create_user_story_returns_201(self, taiga_config: Config) -> None:
        with allure.step("Login"):
            session = self._login(taiga_config)

        with allure.step("Create user story"):
            resp, us_subject = self.create_us(taiga_config, session)

        with allure.step("Assert response fields"):
            assert resp.status_code == 201, resp.text
            data = resp.json()
            assert _USER_STORY_REQUIRED_KEYS.issubset(set(data.keys())), (
                f"Missing keys {_USER_STORY_REQUIRED_KEYS - set(data.keys())}: {data}"
            )
            assert data["subject"] == us_subject, (
                f"Unexpected subject: {data['subject']!r}"
            )
            allure.attach(
                json.dumps(data, indent=2),
                name="Created User Story",
                attachment_type=allure.attachment_type.JSON,
            )
