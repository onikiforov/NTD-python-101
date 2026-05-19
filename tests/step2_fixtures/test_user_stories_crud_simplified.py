import json
import uuid
from pathlib import Path
from typing import Any

import allure
import pytest
import yaml

from helpers.api import API

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
    def test_list_user_stories_returns_200_and_list(self, taiga_session, cfg, created_user_story, delete_user_story):
        resp = API(cfg, taiga_session).get_user_stories_list()
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
    def test_create_user_story_returns_201_with_required_keys(self, taiga_session, cfg, delete_user_story):
        subject = f"Workshop US {uuid.uuid4().hex[:8]}"
        body = {"project": cfg.project_id, "subject": subject}

        us_resp = API(cfg, taiga_session).post_user_story(body)

        assert us_resp.status_code == 201

        data = us_resp.json()
        assert_required_keys(data)
        assert data["subject"] == subject
        assert data["project"] == cfg.project_id

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
    def test_create_user_story_parametrized_returns_201(self, taiga_session, cfg, delete_user_story, payload):
        body = {**payload, "project": cfg.project_id}

        new_us_response = API(cfg, taiga_session).post_user_story(body)
        assert new_us_response.status_code == 201

        data = new_us_response.json()
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
    def test_create_user_story_without_auth_returns_401(self, cfg):
        # Not using session here to send request without auth
        body = {"project": cfg.project_id, "subject": "No-auth story"}

        new_us_response = API(cfg, None).post_user_story(body)

        assert new_us_response.status_code == 401

        response_body = new_us_response.json()
        assert "_error_message" in response_body
        assert "Authentication credentials were not provided." in response_body["_error_message"]

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_missing_subject_returns_400(self, taiga_session, cfg):
        body = {"project": cfg.project_id}

        new_us_response = API(cfg, taiga_session).post_user_story(body)

        assert new_us_response.status_code == 400

        response_body = new_us_response.json()
        assert "subject" in response_body

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_get_user_story_detail_returns_200_with_contract(self, taiga_session, cfg, created_user_story,
                                                             delete_user_story):
        story_id = created_user_story["id"]

        resp = API(cfg, taiga_session).get_us_by_id(story_id)
        assert resp.status_code == 200

        data = resp.json()
        assert_required_keys(data)
        assert data["id"] == story_id
        assert data["subject"] == created_user_story["subject"]

        delete_user_story(story_id)

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_patch_user_story_with_current_version_returns_200(self, taiga_session, cfg, user_story):
        story_id = user_story["id"]
        new_subject = f"Updated subject {uuid.uuid4().hex[:6]}"

        detail_resp = API(cfg, taiga_session).get_us_by_id(story_id)
        assert detail_resp.status_code == 200

        current_version = detail_resp.json()["version"]

        body = {"version": current_version, "subject": new_subject}

        patch_resp = API(cfg, taiga_session).patch_us_by_id(story_id, body)
        assert patch_resp.status_code == 200

        patch_data = patch_resp.json()
        assert_required_keys(patch_data)
        assert patch_data["version"] == current_version + 1
        assert patch_data["subject"] == new_subject

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_delete_user_story_returns_204_and_confirms_404(self, taiga_session, cfg, created_user_story):
        story_id = created_user_story["id"]

        resp = API(cfg, taiga_session).delete_us_by_id(story_id)
        assert resp.status_code == 204

        confirm_resp = API(cfg, taiga_session).get_us_by_id(story_id)
        assert confirm_resp.status_code == 404
