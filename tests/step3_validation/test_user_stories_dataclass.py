"""
Dataclass-based response parsing.

Demonstrates:
- Positive: a valid API response is parsed into a UserStory dataclass.
- Negative (parametrized): removing any required field raises ValueError.
"""
import allure
import pytest

from tests.models.dataclasses.user_story_dataclass import UserStory

_REQUIRED_FIELDS = (
    "id",
    "ref"
)


class TestUserStoriesDataclass:
    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Dataclass")
    def test_get_user_story_parses_to_dataclass(self, taiga_session, taiga_config, user_story):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{user_story['id']}",
            timeout=10,
        )

        assert resp.status_code == 200

        story = UserStory(**resp.json())

        assert story.id == user_story["id"]
        assert story.subject == user_story["subject"]
        assert story.version >= 1

    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-Dataclass")
    @pytest.mark.parametrize(
        "field_name",
        _REQUIRED_FIELDS,
        ids=list(_REQUIRED_FIELDS),
    )
    def test_get_user_story_missing_field_raises_value_error(self, taiga_session, taiga_config, user_story, field_name):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{user_story['id']}",
            timeout=10,
        )
        assert resp.status_code == 200

        data = dict(resp.json())
        del data[field_name]

        with pytest.raises(ValueError, match=f"Missing required field: '{field_name}'"):
            UserStory.from_dict(data)
