# NTD — API Testing Workshop

## 1. Workshop Overview

**Audience:** QA engineers new to API testing with Python.

**Goal:** Walk through four progressive steps that build a pytest suite against the public Taiga.io REST API, introducing fixtures, data-driven tests, schema validation, and Allure reporting.

---

## 2. Prerequisites

- A **Taiga.io account** you own (register free at taiga.io).
- **One project pre-created** in the Taiga web UI. Copy its numeric ID into `.env` as `TAIGA_PROJECT_ID`. Tests use this project as the parent for all User Story CRUD operations — they never create a new project automatically.

  **How to find your project ID:**
  1. Open your project in the Taiga web UI — the URL looks like `https://taiga.io/project/my-project-slug/`.
  2. Copy the slug (the `my-project-slug` part).
  3. Run:
     ```bash
     curl -s https://api.taiga.io/api/v1/projects/by_slug?slug=my-project-slug | python3 -m json.tool | grep -m 1 '"id"'
     ```
  4. The `"id"` value is your project ID. Put it in `.env` as `TAIGA_PROJECT_ID=<number>`.
- **`uv`** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
- **Allure CLI** installed (see [Allure docs](https://allurereport.org/docs/install/)).

---

## 3. Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env: fill in TAIGA_USERNAME, TAIGA_PASSWORD, TAIGA_PROJECT_ID

# Install Allure CLI (macOS example)
brew install allure
```

---

## 4. Run Commands

```bash
# Run smoke tests only
uv run pytest -m smoke -v

# Run regression tests only
uv run pytest -m regression -v

# Run schema validation tests only
uv run pytest -m schema_validation -v

# Run all tests
uv run pytest -v

# Serve Allure report
uv run allure serve allure-results
```

> **Note:** On `main` (step-0), pytest collects **0 tests** by design. The infrastructure is in place; tests are added in subsequent branches.

---

## 5. Branch Tour

| Branch                 | What's new                                                    | Look at first                                          |
|------------------------|---------------------------------------------------------------|--------------------------------------------------------|
| `main` (step-0)        | Project scaffold, logging, env handling                       | `conftest.py`, `pyproject.toml`, `config.py`           |
| `step-1-basic-tests`   | Naive GET/POST, inline login, hardcoded data, deliberate leak | `tests/step1_basic/test_user_stories_basic.py`         |
| `step-2-fixtures-data` | Session auth fixture, YAML data, full CRUD with teardown      | `conftest.py` (fixtures), `tests/step2_fixtures/`      |
| `step-3-validation`    | jsonschema + dataclass + pydantic validation                  | `tests/step3_validation/`, `schemas/`, `tests/models/` |

---

## 6. Pitfalls

- **Rate limits:** Taiga.io enforces request rate limits. If tests start returning 429, add a short delay or reduce parallelism.
- **OCC — Optimistic Concurrency Control:** `PATCH` requests to `/userstories/{id}` require a `version` field matching the current server-side version. Always fetch the resource first and pass back its `version`.
- **`TAIGA_PROJECT_ID` must belong to your account:** The ID must be a project you own or are a member of. Using someone else's project ID will cause 403 errors on write operations.
- **Auth token is session-scoped (step-2+):** The `auth_token` fixture posts to `/auth` exactly once per pytest session. All tests in a session share the same token. Do not call `/auth` again inside individual test functions.
