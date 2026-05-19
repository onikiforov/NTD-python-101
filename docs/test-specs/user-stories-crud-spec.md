# Test Spec: Taiga User Stories CRUD
**Project:** NTD workshop — Step-2  
**Branch:** `step-2-fixtures-data`  
**Module under test:** `POST /api/v1/userstories` and related CRUD endpoints on `https://api.taiga.io/api/v1`  
**Required Skills:** `testing-strategies`, `python-testing`, `pytest-skill`, `python-best-practices`, `superpowers:verification-before-completion`

---

## 1. Scope

### In scope
| Endpoint | Method |
|---|---|
| `/api/v1/auth` | POST (session precondition) |
| `/api/v1/userstories?project={id}` | GET list |
| `/api/v1/userstories` | POST create |
| `/api/v1/userstories/{id}` | GET detail |
| `/api/v1/userstories/{id}` | PATCH partial update |
| `/api/v1/userstories/{id}` | DELETE |

### Out of scope
- `PUT /api/v1/userstories/{id}` (full replace)
- Bulk endpoints
- Pagination header assertions
- HTTP 429 rate-limit response (documented known pitfall — reduce concurrency if encountered)
- Cross-user 403 (requires a second Taiga account not available in workshop env)
- 401 / 404 negative paths for DETAIL, PATCH, DELETE (time-boxed workshop; happy path + one key failure per group is sufficient)

---

## 2. Test Design Techniques Applied

| Technique | Applied to |
|---|---|
| Equivalence Partitioning (EP) | Auth header (valid / absent) for LIST and CREATE; PATCH version (current / stale) |
| Boundary Value Analysis (BVA) | PATCH `version`: current = server_version (at boundary); stale = server_version - 1 (just below) |
| State Transition | User story lifecycle: nonexistent → created → updated → deleted → nonexistent (confirmed via 404) |
| Risk-based depth | Full state coverage on PATCH (OCC is highest-risk) and DELETE (irreversible); lighter on LIST and DETAIL (read-only) |

---

## 3. Coverage Matrix

Every cell maps to one or more test case IDs defined in Section 5.

| Endpoint | 2xx + schema contract | 401 Unauthorized | 400 Validation / OCC |
|---|---|---|---|
| `POST /auth` | TC-AUTH-01 (session precondition) | — | — |
| `GET /userstories?project={id}` | TC-LIST-01 | TC-LIST-02 | — |
| `POST /userstories` | TC-CREATE-01, TC-CREATE-02 | TC-CREATE-03 | TC-CREATE-04 |
| `GET /userstories/{id}` | TC-DETAIL-01 | — | — |
| `PATCH /userstories/{id}` | TC-PATCH-01 | — | — |
| `DELETE /userstories/{id}` | TC-DELETE-01 | — | — |

---

## 4. Fixture Design

### 4.1 Session-scoped fixtures

**`taiga_config`** (already in `conftest.py`)  
Scope: `session`  
Returns: frozen `Config` dataclass with `base_url`, `username`, `password`, `project_id`.

**`taiga_session`** (to be added in step-2 `conftest.py`)  
Scope: `session`  
Behavior: calls `POST /auth` exactly once per pytest session, creates a `requests.Session`, attaches `Authorization: Bearer {token}` header and `log_response_hook`. All CRUD test methods use this fixture — never call `POST /auth` again inside test functions.

### 4.2 Function-scoped fixtures

**`created_user_story`**  
Scope: `function`  
Behavior: POSTs a new user story with a unique `subject` (use `uuid.uuid4().hex[:8]` suffix). Yields the full response dict.  
Teardown: none — tests that own their story call `delete_user_story` explicitly.

**`delete_user_story`**  
Scope: `function`  
Behavior: yields a callable `delete(story_id: int) -> None` that sends `DELETE /userstories/{story_id}` and asserts 204.  
Usage:
- Tests that create a story and then assert something else call `delete(story_id)` in their body as cleanup.
- `TC-DELETE-01` uses this callable as the **action under test** — assert 204, then confirm 404.

### 4.3 YAML data file

Path: `tests/data/user_stories.yaml`  
Used by: `TC-CREATE-02` (parametrized create)

Required structure:

```yaml
user_stories:
  - subject: "As a user, I want to log in so that I can access my data"
  - subject: "As an admin, I want to view reports so that I can monitor usage"
  - subject: "As a user, I want to reset my password via email"
    description: "Optional description field included"
  - subject: "Short US subject"
  - subject: "US with explicit tags"
    tags: ["workshop", "step2"]
```

Each entry is merged with `{"project": taiga_config.project_id}` at test time.  
All 3-5 payloads are valid (exercising the valid-payload equivalence partition with distinct field combinations).

---

## 5. Response Contract

All happy-path tests for individual story responses (create, detail, patch) must assert key presence:

```python
_US_OUT_KEYS = {
    "id", "ref", "subject", "project",
    "status", "version", "created_date", "modified_date",
}
```

Assertion pattern:

```python
assert set(response_data.keys()) >= _US_OUT_KEYS, (
    f"Missing keys: {_US_OUT_KEYS - set(response_data.keys())}"
)
```

`>=` (superset) is used because the API returns additional fields beyond the required set. This catches silent schema breakage without over-constraining.

List responses (`GET /userstories?project={id}`) return a JSON array — each element must contain at minimum `id`, `subject`, and `project`.

---

## 6. State Transition: User Story Lifecycle

```
[nonexistent]
     |
     | POST /userstories  (TC-CREATE-01, TC-CREATE-02)
     v
  [created]  <--- GET /userstories/{id} (TC-DETAIL-01) — state unchanged
     |
     | PATCH /userstories/{id} with current version  (TC-PATCH-01)
     v
  [updated, version = original+1]
     |
     | DELETE /userstories/{id}  (TC-DELETE-01)
     v
[nonexistent]
     |
     | GET /userstories/{id}  --> 404  (TC-DELETE-01 confirmation step)
```

---

## 7. Test Cases

### Class: `TestUserStoriesCrud`

File: `tests/step2_fixtures_data/test_user_stories_crud.py`  
Marker: `@pytest.mark.regression` on all test methods  
Allure feature: `"User Stories"` / story: `"CRUD"`

---

#### TC-AUTH-01 — Session precondition (traceability entry, not an explicit test method)

Covered implicitly by the `taiga_session` session-scoped fixture. Any fixture-level failure here aborts the entire session with a clear error before any test method runs.

**Preconditions:** Valid credentials in `.env`.  
**Steps:** `taiga_session` fixture sends `POST /auth` with `{"username": cfg.username, "password": cfg.password, "type": "normal"}`.  
**Expected:** Status 200, body contains `"auth_token"` as a non-empty string.

---

#### TC-LIST-01 — `test_list_user_stories_returns_200_and_list`

**Partition:** Auth = valid, project ID = real project owned by account.  
**Fixtures:** `taiga_session`, `taiga_config`, `created_user_story`, `delete_user_story`  
**Marker:** `@pytest.mark.regression`

**Preconditions:** At least one user story exists (ensured by `created_user_story`).

**Steps:**
1. Use `created_user_story` to guarantee the project has at least one story.
2. Send `GET {base_url}/userstories?project={project_id}` using `taiga_session`.
3. Call `delete(created_user_story["id"])` to clean up.

**Expected:**
- Status code: `200`
- Body: JSON array
- Each element contains at minimum keys: `id`, `subject`, `project`
- The created story's `id` appears in the returned list

**Assertions:**
```python
assert resp.status_code == 200
data = resp.json()
assert isinstance(data, list)
ids = [item["id"] for item in data]
assert story["id"] in ids
for item in data:
    assert {"id", "subject", "project"}.issubset(set(item.keys()))
```

---

#### TC-LIST-02 — `test_list_user_stories_without_auth_returns_401`

**Partition:** Auth = absent.  
**Fixtures:** `taiga_config`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Send `GET {base_url}/userstories?project={project_id}` with no `Authorization` header (plain `requests.get`, not `taiga_session`).

**Expected:**
- Status code: `401`
- Body: `{"detail": "Authentication credentials were not provided."}`

**Assertions:**
```python
assert resp.status_code == 401
assert resp.json()["detail"] == "Authentication credentials were not provided."
```

---

#### TC-CREATE-01 — `test_create_user_story_returns_201_with_required_keys`

**Partition:** Auth = valid, payload = minimum required (subject + project only).  
**Fixtures:** `taiga_session`, `taiga_config`, `delete_user_story`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Generate a unique subject: `f"Workshop US {uuid.uuid4().hex[:8]}"`.
2. Send `POST {base_url}/userstories` with `{"project": project_id, "subject": subject}`.
3. Capture `story_id = resp.json()["id"]`.
4. Call `delete(story_id)` to clean up.

**Expected:**
- Status code: `201`
- Body: JSON object containing all keys in `_US_OUT_KEYS`
- `data["subject"]` equals the sent subject
- `data["project"]` equals `project_id`
- `data["version"]` is an integer >= 1

**Assertions:**
```python
assert resp.status_code == 201
data = resp.json()
assert set(data.keys()) >= _US_OUT_KEYS
assert data["subject"] == subject
assert data["project"] == taiga_config.project_id
assert isinstance(data["version"], int) and data["version"] >= 1
```

---

#### TC-CREATE-02 — `test_create_user_story_parametrized_payloads`

**Technique:** Equivalence partition across 3-5 valid payload variants from YAML.  
**Partition:** Auth = valid, payload = valid variants (subject-only, with description, with tags, etc.).  
**Fixtures:** `taiga_session`, `taiga_config`, `delete_user_story`  
**Marker:** `@pytest.mark.regression`  
**Parametrize source:** `tests/data/user_stories.yaml` → key `user_stories`

**Steps (per parametrize iteration):**
1. Load payload from YAML, inject `"project": taiga_config.project_id`.
2. Send `POST {base_url}/userstories` with the full payload.
3. Capture `story_id`.
4. Call `delete(story_id)` as cleanup.

**Expected per iteration:**
- Status code: `201`
- Body contains all `_US_OUT_KEYS`
- `data["subject"]` equals the YAML `subject` value

**Implementation note:** Load the YAML in a `pytest.fixture(params=...)` or use `@pytest.mark.parametrize`. The YAML must be read once, not re-read per test.

---

#### TC-CREATE-03 — `test_create_user_story_without_auth_returns_401`

**Partition:** Auth = absent.  
**Fixtures:** `taiga_config`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Send `POST {base_url}/userstories` with no `Authorization` header and body `{"project": project_id, "subject": "No-auth story"}`.

**Expected:**
- Status code: `401`
- Body: `{"detail": "Authentication credentials were not provided."}`

---

#### TC-CREATE-04 — `test_create_user_story_missing_subject_returns_400`

**Partition:** Auth = valid, payload = invalid (required field `subject` omitted).  
**Fixtures:** `taiga_session`, `taiga_config`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Send `POST {base_url}/userstories` with `{"project": project_id}` (no `subject`).

**Expected:**
- Status code: `400`
- Body contains a `subject` key indicating the field is required (verify exact shape against actual API response at implementation time — expected: `{"subject": ["This field is required."]}` or similar)
- No cleanup needed — this test must not create a story

---

#### TC-DETAIL-01 — `test_get_user_story_detail_returns_200_with_contract`

**Partition:** Auth = valid, story ID = existing valid ID.  
**Fixtures:** `taiga_session`, `created_user_story`, `delete_user_story`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Read `story_id = created_user_story["id"]`.
2. Send `GET {base_url}/userstories/{story_id}`.
3. Call `delete(story_id)` to clean up.

**Expected:**
- Status code: `200`
- Body contains all `_US_OUT_KEYS`
- `data["id"]` equals `story_id`
- `data["subject"]` equals `created_user_story["subject"]`

---

#### TC-PATCH-01 — `test_patch_user_story_with_current_version_returns_200`

**Technique:** State transition (created → updated), BVA on version (current = at boundary).  
**Partition:** Auth = valid, version = current server version.  
**Fixtures:** `taiga_session`, `created_user_story`, `delete_user_story`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Read `story_id = created_user_story["id"]`.
2. Send `GET {base_url}/userstories/{story_id}` to retrieve the freshest version (guards against any background modification between fixture and test).
3. Extract `current_version = detail_resp.json()["version"]`.
4. Build update payload: `{"version": current_version, "subject": "Updated subject " + uuid.uuid4().hex[:6]}`.
5. Send `PATCH {base_url}/userstories/{story_id}` with the update payload.
6. Call `delete(story_id)` to clean up.

**Expected:**
- PATCH status code: `200`
- Body contains all `_US_OUT_KEYS`
- `data["version"]` equals `current_version + 1` (server increments on every successful write)
- `data["subject"]` equals the new subject sent in step 4

**OCC assertion:**
```python
assert patch_data["version"] == current_version + 1, (
    f"Expected version {current_version + 1}, got {patch_data['version']}"
)
```

---

#### TC-DELETE-01 — `test_delete_user_story_returns_204_and_confirms_404`

**Technique:** State transition (created → nonexistent), confirmed by 404 GET.  
**Partition:** Auth = valid, story ID = existing valid ID.  
**Fixtures:** `taiga_session`, `taiga_config`, `created_user_story`, `delete_user_story`  
**Marker:** `@pytest.mark.regression`

**Steps:**
1. Read `story_id = created_user_story["id"]`.
2. Call `delete(story_id)` — this is the **action under test** (inside the callable: `DELETE /userstories/{story_id}`).
3. Send `GET {base_url}/userstories/{story_id}` to confirm deletion.

**Expected:**
- DELETE response (inside callable): status `204`, body is empty
- Confirmation GET: status `404`, body `{"detail": "Not found."}`

**Assertions:**
```python
# Inside delete callable
assert delete_resp.status_code == 204
assert delete_resp.content == b""  # 204 must carry no body

# Confirmation step in test body
confirm_resp = taiga_session.get(f"{base_url}/userstories/{story_id}", timeout=10)
assert confirm_resp.status_code == 404
assert confirm_resp.json()["detail"] == "Not found."
```

---

## 8. Execution Order and Dependencies

Tests within `TestUserStoriesCrud` are independent of each other. Each uses its own `created_user_story` fixture instance. The only shared state is `taiga_session` and `taiga_config` (both session-scoped, read-only after setup).

Lifecycle ordering is enforced inside individual test bodies (e.g., TC-PATCH-01 does GET before PATCH; TC-DELETE-01 does DELETE then GET).

---

## 9. Anything Left Untested and Why

| Scenario | Reason not covered |
|---|---|
| `PUT /userstories/{id}` | Explicitly out of scope |
| Bulk endpoints | Out of scope |
| Pagination headers | Out of scope |
| HTTP 429 | Documented known pitfall — not deterministic in workshop env |
| Cross-user 403 | Requires second Taiga account not available |
| 401 / 404 on DETAIL, PATCH, DELETE | Time-boxed workshop; removed to keep discussion scope manageable |
| PATCH with `version` field missing | Lower risk than stale version; error shape not in brief |
| POST with malformed `project` | Workshop focus is CRUD lifecycle, not deep input validation |
| Concurrent PATCH race (true OCC race) | Requires parallel requests; outside step-2 scope |

---

## 10. Manual Execution Checklist

1. Confirm `.env` has `TAIGA_BASE_URL`, `TAIGA_USERNAME`, `TAIGA_PASSWORD`, `TAIGA_PROJECT_ID` set.
2. Verify `TAIGA_PROJECT_ID` is a project owned by the test account (foreign project causes 403 on writes).
3. Run: `uv run pytest tests/step2_fixtures_data/ -m regression -v 2>&1 | tee /tmp/test-run-$(date +%s).log`
4. Inspect the log for any 429 responses — if seen, re-run with reduced concurrency or add a short pause between API calls.
5. Run `allure serve allure-results` to review the report.
6. Confirm no Authorization token appears in plaintext in `logs/` (RedactAuthFilter must be active).
