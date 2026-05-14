import json
import uuid
from pathlib import Path
from typing import Any

import allure
import pytest
import requests
import yaml

_US_OUT_KEYS = frozenset({
    "id", "ref", "subject", "project",
    "status", "version", "created_date", "modified_date",
})

def assert_required_keys(data):
    assert set(data.keys()) >= _US_OUT_KEYS, (
        f"Missing keys: {_US_OUT_KEYS - set(data.keys())}"
    )


def _load_user_stories() -> list[dict[str, Any]]:
    path = Path(__file__).parent.parent / "data" / "user_stories.yaml"
    with path.open() as fh:
        return yaml.safe_load(fh)["user_stories"]


class TestUserStoriesCrud:
    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_list_user_stories_returns_200_and_list(self, taiga_session, taiga_config, created_user_story,
                                                    delete_user_story):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories",
            params={"project": taiga_config.project_id},
            timeout=10,
        )

        assert resp.status_code == 200
        data = resp.json()
        ids = [item["id"] for item in data]
        assert created_user_story["id"] in ids
        for item in data:
            assert {"id", "subject", "project"}.issubset(set(item.keys())), (
                f"Item missing required keys: {item}"
            )

        delete_user_story(created_user_story["id"])

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_returns_201_with_required_keys(self, taiga_session, taiga_config, delete_user_story):
        subject = f"Workshop US {uuid.uuid4().hex[:8]}"

        resp = taiga_session.post(
            f"{taiga_config.base_url}/userstories",
            json={"project": taiga_config.project_id, "subject": subject},
            timeout=10,
        )

        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert_required_keys(data)
        assert data["subject"] == subject
        assert data["project"] == taiga_config.project_id
        allure.attach(
            json.dumps(data, indent=2),
            name="Created User Story",
            attachment_type=allure.attachment_type.JSON,
        )

        delete_user_story(data["id"])

    _PAYLOADS = _load_user_stories()

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    @pytest.mark.parametrize(
        "payload",
        _PAYLOADS,
        ids=[p["subject"][:40] for p in _PAYLOADS],
    )
    def test_create_user_story_parametrized_returns_201(self, taiga_session, taiga_config, delete_user_story, payload):
        body = {**payload, "project": taiga_config.project_id}

        resp = taiga_session.post(
            f"{taiga_config.base_url}/userstories",
            json=body,
            timeout=10,
        )

        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert_required_keys(data)
        assert data["subject"] == payload["subject"]
        allure.attach(
            json.dumps(data, indent=2),
            name="Created User Story",
            attachment_type=allure.attachment_type.JSON,
        )

        delete_user_story(data["id"])

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_without_auth_returns_401(self, taiga_config):
        # Not using session here to send request without auth
        resp = requests.post(
            f"{taiga_config.base_url}/userstories",
            json={"project": taiga_config.project_id, "subject": "No-auth story"},
            timeout=10,
        )

        assert resp.status_code == 401
        body = resp.json()
        assert "_error_message" in body, f"Unexpected 401 body shape: {body}"
        assert "Authentication credentials were not provided." in body["_error_message"]

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_missing_subject_returns_400(self, taiga_session, taiga_config):
        resp = taiga_session.post(
            f"{taiga_config.base_url}/userstories",
            json={"project": taiga_config.project_id},
            timeout=10,
        )

        assert resp.status_code == 400, resp.text
        body = resp.json()
        assert "subject" in body

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_get_user_story_detail_returns_200_with_contract(self, taiga_session, taiga_config, created_user_story,
                                                             delete_user_story):
        story_id = created_user_story["id"]

        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{story_id}",
            timeout=10,
        )

        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert_required_keys(data)
        assert data["id"] == story_id
        assert data["subject"] == created_user_story["subject"]

        delete_user_story(story_id)

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_patch_user_story_with_current_version_returns_200(self, taiga_session, taiga_config, user_story):
        story_id = user_story["id"]
        new_subject = f"Updated subject {uuid.uuid4().hex[:6]}"

        detail_resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{story_id}",
            timeout=10,
        )
        assert detail_resp.status_code == 200
        current_version = detail_resp.json()["version"]

        patch_resp = taiga_session.patch(
            f"{taiga_config.base_url}/userstories/{story_id}",
            json={"version": current_version, "subject": new_subject},
            timeout=10,
        )

        assert patch_resp.status_code == 200
        patch_data = patch_resp.json()
        assert_required_keys(patch_data)

        assert patch_data["version"] == current_version + 1
        assert patch_data["subject"] == new_subject

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_delete_user_story_returns_204_and_confirms_404(self, taiga_session, taiga_config, created_user_story):
        story_id = created_user_story["id"]

        resp = taiga_session.delete(
            f"{taiga_config.base_url}/userstories/{story_id}",
            timeout=10,
        )
        assert resp.status_code == 204, f"Expected 204 on delete, got {resp.status_code}: {resp.text}"

        confirm_resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{story_id}",
            timeout=10,
        )
        assert confirm_resp.status_code == 404
