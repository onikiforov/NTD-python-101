"""
Pydantic v2 response validation.

Demonstrates:
- Positive: a valid API response is parsed and validated by a Pydantic model.
- Negative (parametrized): type-breaking mutations raise pydantic.ValidationError.
"""
from typing import Any

import allure
import pydantic
import pytest

from tests.models.pydantic.user_story_pydantic_model import UserStory

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
    def test_get_user_story_validates_with_pydantic(self, taiga_session, taiga_config, user_story):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{user_story['id']}",
            timeout=10,
        )

        assert resp.status_code == 200

        story = UserStory.model_validate(resp.json())

        assert story.id == user_story["id"]
        assert story.subject == user_story["subject"]

    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Pydantic")
    @pytest.mark.parametrize(
        "mutation,mutation_id",
        _TYPE_MUTATIONS,
        ids=[m[1] for m in _TYPE_MUTATIONS],
    )
    def test_get_user_story_invalid_type_raises_pydantic_error(self, taiga_session, taiga_config, user_story,
                                                               mutation, mutation_id):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{user_story['id']}",
            timeout=10,
        )
        assert resp.status_code == 200

        mutated: dict[str, Any] = {**resp.json(), **mutation}

        with pytest.raises(pydantic.ValidationError):
            UserStory.model_validate(mutated)
