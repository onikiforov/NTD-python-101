"""
Step-3 validation tests: Dataclass-based response parsing.

Demonstrates:
- Positive: a valid API response is parsed into a UserStory dataclass.
- Negative (parametrized): removing any required field raises ValueError.
"""
from typing import Any

import allure
import pytest
import requests

from config import Config
from tests.models.dataclasses import UserStory

_REQUIRED_FIELDS = (
    "id",
    "ref",
    "subject",
    "project",
    "status",
    "version",
    "created_date",
    "modified_date",
)


class TestUserStoriesDataclass:
    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Dataclass")
    def test_get_user_story_parses_to_dataclass(
        self,
        taiga_session: requests.Session,
        taiga_config: Config,
        user_story: dict[str, Any],
    ) -> None:
        with allure.step(f"GET /userstories/{user_story['id']}"):
            resp = taiga_session.get(
                f"{taiga_config.base_url}/userstories/{user_story['id']}",
                timeout=10,
            )

        with allure.step("Assert HTTP 200"):
            assert resp.status_code == 200, resp.text

        with allure.step("Parse response into UserStory dataclass"):
            story = UserStory.from_dict(resp.json())

        with allure.step("Assert dataclass fields match API response"):
            assert story.id == user_story["id"], (
                f"id mismatch: {story.id!r} != {user_story['id']!r}"
            )
            assert story.subject == user_story["subject"], (
                f"subject mismatch: {story.subject!r} != {user_story['subject']!r}"
            )
            assert isinstance(story.version, int) and story.version >= 1, (
                f"version must be a positive integer, got: {story.version!r}"
            )

    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Dataclass")
    @pytest.mark.parametrize(
        "field_name",
        _REQUIRED_FIELDS,
        ids=list(_REQUIRED_FIELDS),
    )
    def test_get_user_story_missing_field_raises_valueerror(
        self,
        taiga_session: requests.Session,
        taiga_config: Config,
        user_story: dict[str, Any],
        field_name: str,
    ) -> None:
        with allure.step(f"GET /userstories/{user_story['id']}"):
            resp = taiga_session.get(
                f"{taiga_config.base_url}/userstories/{user_story['id']}",
                timeout=10,
            )
            assert resp.status_code == 200, resp.text

        with allure.step(f"Remove required field: {field_name!r}"):
            data: dict[str, Any] = dict(resp.json())
            del data[field_name]

        with allure.step(f"Assert UserStory.from_dict raises ValueError for missing {field_name!r}"):
            with pytest.raises(ValueError, match=f"Missing required field: '{field_name}'"):
                UserStory.from_dict(data)
