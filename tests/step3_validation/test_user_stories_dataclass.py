"""
Step-3 validation tests: Dataclass-based response parsing.

Demonstrates:
- Positive: a valid API response is parsed into a UserStory dataclass.
- Negative (parametrized): removing any required field raises ValueError.
"""
import allure
import pytest

from tests.models.user_story_dataclass import UserStory

_REQUIRED_FIELDS = (
    "id",
    "ref",
    "subject",
    "project",
    "status",
    "version",
    "created_date",
    "modified_date",
    "owner",
    "backlog_order",
    "sprint_order",
    "kanban_order",
    "is_blocked",
    "is_closed",
    "is_voter",
    "is_watcher",
    "client_requirement",
    "team_requirement",
    "total_comments",
    "total_watchers",
    "total_voters",
    "total_attachments",
    "blocked_note",
    "blocked_note_html",
    "comment",
    "due_date_reason",
    "due_date_status",
    "tags",
    "watchers",
    "tasks",
    "assigned_users",
    "points",
    "owner_extra_info",
    "project_extra_info",
    "status_extra_info",
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

        story = UserStory.from_dict(resp.json())

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
