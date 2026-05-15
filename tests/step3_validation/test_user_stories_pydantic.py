"""
Step-3 validation tests: Pydantic v2 response validation.

Demonstrates:
- Positive: a valid API response is parsed and validated by a Pydantic model.
- Negative (parametrized): type-breaking mutations raise pydantic.ValidationError.
"""
import json
from typing import Any

import allure
import pydantic
import pytest
import requests

from config import Config
from tests.models.user_story_pydantic_model import UserStory

# Each entry: (mutation dict, descriptive id)
_TYPE_MUTATIONS = [
    ({"id": "not-an-int"}, "id_wrong_type"),
    ({"version": [1, 2, 3]}, "version_list_instead_of_int"),
    ({"subject": 12345}, "subject_int_instead_of_str"),
]


class TestUserStoriesPydantic:
    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Pydantic")
    def test_get_user_story_validates_with_pydantic(
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

        with allure.step("Validate response with Pydantic model"):
            story = UserStory.model_validate(resp.json())

        with allure.step("Assert model fields match API response"):
            assert story.id == user_story["id"], (
                f"id mismatch: {story.id!r} != {user_story['id']!r}"
            )
            assert story.subject == user_story["subject"], (
                f"subject mismatch: {story.subject!r} != {user_story['subject']!r}"
            )
            assert isinstance(story.tags, list), (
                f"tags must be a list, got: {type(story.tags).__name__!r}"
            )

        with allure.step("Attach validated model as JSON"):
            allure.attach(
                story.model_dump_json(indent=2),
                name="Validated User Story (Pydantic)",
                attachment_type=allure.attachment_type.JSON,
            )

    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Pydantic")
    @pytest.mark.parametrize(
        "mutation,mutation_id",
        _TYPE_MUTATIONS,
        ids=[m[1] for m in _TYPE_MUTATIONS],
    )
    def test_get_user_story_invalid_type_raises_pydantic_error(
        self,
        taiga_session: requests.Session,
        taiga_config: Config,
        user_story: dict[str, Any],
        mutation: dict[str, Any],
        mutation_id: str,
    ) -> None:
        with allure.step(f"GET /userstories/{user_story['id']}"):
            resp = taiga_session.get(
                f"{taiga_config.base_url}/userstories/{user_story['id']}",
                timeout=10,
            )
            assert resp.status_code == 200, resp.text

        with allure.step(f"Apply mutation: {mutation_id}"):
            mutated: dict[str, Any] = {**resp.json(), **mutation}

        with allure.step(f"Assert Pydantic raises ValidationError for mutation {mutation_id!r}"):
            with pytest.raises(pydantic.ValidationError):
                UserStory.model_validate(mutated)
