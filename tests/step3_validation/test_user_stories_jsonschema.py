"""
JSON Schema validation via jsonschema library.

Demonstrates:
- Positive: a valid API response passes schema validation without raising.
- Negative (parametrized): a mutated response dict fails with ValidationError.
"""
from typing import Any

import allure
import jsonschema
import pytest

# ---------------------------------------------------------------------------
# Mutation helpers — each returns a copy of `data` with a specific defect.
# ---------------------------------------------------------------------------

def _mutate_id_wrong_type(data: dict[str, Any]) -> dict[str, Any]:
    mutated = dict(data)
    mutated["id"] = "not-an-integer"
    return mutated


def _mutate_version_wrong_type(data: dict[str, Any]) -> dict[str, Any]:
    mutated = dict(data)
    mutated["version"] = "string-instead-of-int"
    return mutated


def _mutate_subject_missing(data: dict[str, Any]) -> dict[str, Any]:
    mutated = dict(data)
    del mutated["subject"]
    return mutated


_MUTATIONS = [
    (_mutate_id_wrong_type, "id_wrong_type"),
    (_mutate_version_wrong_type, "version_wrong_type"),
    (_mutate_subject_missing, "subject_missing"),
]


class TestUserStoriesJsonSchema:
    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-JsonSchema")
    def test_get_user_story_validates_against_schema(self, taiga_session, taiga_config, user_story, user_story_schema):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{user_story['id']}",
            timeout=10,
        )

        assert resp.status_code == 200

        jsonschema.validate(instance=resp.json(), schema=user_story_schema)

    @pytest.mark.regression
    @pytest.mark.schema_validation
    @allure.feature("User Stories")
    @allure.story("Validation-JsonSchema")
    @pytest.mark.parametrize(
        "mutate_fn,mutation_id",
        _MUTATIONS,
        ids=[m[1] for m in _MUTATIONS],
    )
    def test_get_user_story_mutated_response_fails_schema(self, taiga_session, taiga_config, user_story,
                                                          user_story_schema, mutate_fn, mutation_id):
        resp = taiga_session.get(
            f"{taiga_config.base_url}/userstories/{user_story['id']}",
            timeout=10,
        )
        assert resp.status_code == 200

        mutated: dict[str, Any] = mutate_fn(resp.json())

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=mutated, schema=user_story_schema)
