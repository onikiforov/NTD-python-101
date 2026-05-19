"""
Step-2 CRUD tests for Taiga User Stories API.

Demonstrates session-scoped auth fixture, function-scoped lifecycle fixtures,
YAML-driven parametrization, and OCC (Optimistic Concurrency Control) on PATCH.
"""
import json
import uuid
from pathlib import Path
from collections.abc import Callable
from typing import Any

import allure
import pytest
import requests
import yaml

from config import Config
from helpers.api import API

_US_OUT_KEYS = frozenset({
    "id", "ref", "subject", "project",
    "status", "version", "created_date", "modified_date",
})


def _load_user_stories() -> list[dict[str, Any]]:
    path = Path(__file__).parent.parent / "data" / "user_stories.yaml"
    with path.open() as fh:
        return yaml.safe_load(fh)["user_stories"]


class TestUserStoriesCrud:
    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_list_user_stories_returns_200_and_list(
        self,
        taiga_session: requests.Session,
        cfg: Config,
        created_user_story: dict[str, Any],
        delete_user_story: Callable[[int], None],
    ) -> None:
        story = created_user_story

        with allure.step("Fetch user stories list"):
            resp = API(cfg, taiga_session).get_user_stories_list()

        with allure.step("Assert 200 and list structure"):
            assert resp.status_code == 200

            data = resp.json()
            assert isinstance(data, list), f"Expected list, got {type(data).__name__}"

            ids = [item["id"] for item in data]
            assert story["id"] in ids, f"Created story {story['id']} not found in list"

            for item in data:
                assert {"id", "subject", "project"}.issubset(set(item.keys())), (
                    f"Item missing required keys: {item}"
                )

        with allure.step("Clean up created story"):
            delete_user_story(story["id"])

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_returns_201_with_required_keys(
        self,
        taiga_session: requests.Session,
        cfg: Config,
        delete_user_story: Callable[[int], None],
    ) -> None:
        subject = f"Workshop US {uuid.uuid4().hex[:8]}"
        body = {"project": cfg.project_id, "subject": subject}

        with allure.step("POST new user story with minimal payload"):
            us_resp = API(cfg, taiga_session).post_user_story(body)

        with allure.step("Assert 201 and response contract"):
            assert us_resp.status_code == 201

            data: dict[str, Any] = us_resp.json()
            assert set(data.keys()) >= _US_OUT_KEYS, (
                f"Missing keys: {_US_OUT_KEYS - set(data.keys())}"
            )
            assert data["subject"] == subject, f"Subject mismatch: {data['subject']!r}"
            assert data["project"] == cfg.project_id, f"Project mismatch: {data['project']!r}"
            assert isinstance(data["version"], int) and data["version"] >= 1, (
                f"Unexpected version: {data['version']!r}"
            )

            allure.attach(
                json.dumps(data, indent=2),
                name="Created User Story",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Clean up created story"):
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
    def test_create_user_story_parametrized_returns_201(
        self,
        taiga_session: requests.Session,
        cfg: Config,
        delete_user_story: Callable[[int], None],
        payload: dict[str, Any],
    ) -> None:
        body = {**payload, "project": cfg.project_id}

        with allure.step(f"POST user story: {payload['subject']!r}"):
            new_us_response = API(cfg, taiga_session).post_user_story(body)

        with allure.step("Assert 201 and response contract"):
            assert new_us_response.status_code == 201

            data: dict[str, Any] = new_us_response.json()
            assert set(data.keys()) >= _US_OUT_KEYS, (
                f"Missing keys: {_US_OUT_KEYS - set(data.keys())}"
            )
            assert data["subject"] == payload["subject"], (
                f"Subject mismatch: {data['subject']!r} != {payload['subject']!r}"
            )

            allure.attach(
                json.dumps(data, indent=2),
                name="Created User Story",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Clean up created story"):
            delete_user_story(data["id"])

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_without_auth_returns_401(
        self,
        cfg: Config,
    ) -> None:
        body = {"project": cfg.project_id, "subject": "No-auth story"}

        with allure.step("POST user story without auth header"):
            new_us_response = API(cfg, None).post_user_story(body)

        with allure.step("Assert 401 and error message"):
            assert new_us_response.status_code == 401

            response_body: dict[str, Any] = new_us_response.json()
            assert "_error_message" in response_body, f"Unexpected 401 body shape: {response_body}"
            assert "Authentication credentials were not provided." in response_body["_error_message"], (
                f"Unexpected _error_message: {response_body['_error_message']!r}"
            )

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_create_user_story_missing_subject_returns_400(
        self,
        taiga_session: requests.Session,
        cfg: Config,
    ) -> None:
        body = {"project": cfg.project_id}

        with allure.step("POST user story without required subject field"):
            new_us_response = API(cfg, taiga_session).post_user_story(body)

        with allure.step("Assert 400 and subject error key"):
            assert new_us_response.status_code == 400

            response_body: dict[str, Any] = new_us_response.json()
            assert "subject" in response_body, (
                f"Expected 'subject' key in error body, got: {response_body}"
            )

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_get_user_story_detail_returns_200_with_contract(
        self,
        taiga_session: requests.Session,
        cfg: Config,
        created_user_story: dict[str, Any],
        delete_user_story: Callable[[int], None],
    ) -> None:
        story = created_user_story
        story_id = story["id"]

        with allure.step(f"GET user story detail for id={story_id}"):
            resp = API(cfg, taiga_session).get_us_by_id(story_id)

        with allure.step("Assert 200 and full contract"):
            assert resp.status_code == 200

            data: dict[str, Any] = resp.json()
            assert set(data.keys()) >= _US_OUT_KEYS, (
                f"Missing keys: {_US_OUT_KEYS - set(data.keys())}"
            )
            assert data["id"] == story_id, f"ID mismatch: {data['id']} != {story_id}"
            assert data["subject"] == story["subject"], (
                f"Subject mismatch: {data['subject']!r} != {story['subject']!r}"
            )

        with allure.step("Clean up created story"):
            delete_user_story(story_id)

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_patch_user_story_with_current_version_returns_200(
        self,
        taiga_session: requests.Session,
        cfg: Config,
        created_user_story: dict[str, Any],
        delete_user_story: Callable[[int], None],
    ) -> None:
        story_id = created_user_story["id"]
        new_subject = f"Updated subject {uuid.uuid4().hex[:6]}"

        with allure.step("Fetch current version for OCC"):
            detail_resp = API(cfg, taiga_session).get_us_by_id(story_id)
            assert detail_resp.status_code == 200, detail_resp.text

            current_version: int = detail_resp.json()["version"]

        with allure.step(f"PATCH user story with version={current_version}"):
            body = {"version": current_version, "subject": new_subject}

            patch_resp = API(cfg, taiga_session).patch_us_by_id(story_id, body)

        with allure.step("Assert 200 and OCC version increment"):
            assert patch_resp.status_code == 200

            patch_data: dict[str, Any] = patch_resp.json()
            assert set(patch_data.keys()) >= _US_OUT_KEYS, (
                f"Missing keys: {_US_OUT_KEYS - set(patch_data.keys())}"
            )
            assert patch_data["version"] == current_version + 1, (
                f"Expected version {current_version + 1}, got {patch_data['version']}"
            )
            assert patch_data["subject"] == new_subject, (
                f"Subject not updated: {patch_data['subject']!r}"
            )

        with allure.step("Clean up patched story"):
            delete_user_story(story_id)

    @pytest.mark.regression
    @allure.feature("User Stories")
    @allure.story("CRUD")
    def test_delete_user_story_returns_204_and_confirms_404(
        self,
        taiga_session: requests.Session,
        cfg: Config,
        created_user_story: dict[str, Any],
    ) -> None:
        story_id = created_user_story["id"]

        with allure.step(f"DELETE user story id={story_id}"):
            resp = API(cfg, taiga_session).delete_us_by_id(story_id)

        with allure.step("Assert 204"):
            assert resp.status_code == 204

        with allure.step("Confirm story no longer exists via GET -> 404"):
            confirm_resp = API(cfg, taiga_session).get_us_by_id(story_id)
            assert confirm_resp.status_code == 404
