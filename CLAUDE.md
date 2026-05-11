# NTD — Claude Code Project Guide

## Tech Stack

- Python 3.12
- `requests` for HTTP
- `pytest` 8.3+ with `allure-pytest`, `pytest-dotenv`
- `pydantic` v2 for model validation
- `jsonschema` for JSON Schema validation
- `pyyaml` for data-driven YAML fixtures
- Package manager: `uv`
- System under test: Taiga public API (`https://api.taiga.io/api/v1`)

## Build & Run Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest -v 2>&1 | tee /tmp/test-run-$(date +%s).log

# Run by marker
uv run pytest -m smoke -v
uv run pytest -m regression -v
uv run pytest -m schema_validation -v

# Serve Allure report
allure serve allure-results
```

> On `main` (step-0), pytest collects 0 tests by design.

## Branch Map

| Branch | Purpose |
|---|---|
| `main` (step-0) | Infrastructure only: `conftest.py`, `config.py`, logging, env validation. Zero tests collected. |
| `step-1-basic-tests` | Naive GET/POST tests with inline login and hardcoded data. Deliberately leaks Authorization header to demonstrate the problem. |
| `step-2-fixtures-data` | Session-scoped auth fixture, YAML-driven test data, full CRUD lifecycle with teardown. |
| `step-3-validation` | jsonschema + dataclass + pydantic response validation. Adds `schemas/` and `tests/models/`. |

## Architecture

- `config.py` — `load_config()` reads `.env` via `python-dotenv`, validates required vars, returns a frozen `Config` dataclass. Single source of truth for env values.
- `conftest.py` — `pytest_configure` calls `load_config()` (fail-fast on bad env), sets up `dictConfig` logging with timestamped file handler and `RedactAuthFilter`. Exports `log_response_hook` for use as a `requests` response hook.
- `tests/__init__.py` — empty, marks `tests/` as a package.
- `logs/` and `allure-results/` — tracked via `.gitkeep`; actual contents are gitignored.

## Known Pitfalls

- **Rate limits:** Taiga.io throttles requests. If 429s appear, reduce concurrency.
- **OCC (Optimistic Concurrency Control):** `PATCH /userstories/{id}` requires `version` to match the current server version. Always read before patching.
- **Step-1 deliberate leak:** `step-1-basic-tests` logs Authorization in plaintext intentionally — it is the anti-pattern being taught. `RedactAuthFilter` in `conftest.py` is the solution shown in subsequent steps.
- **Authorization redaction:** `RedactAuthFilter` inspects `record.__dict__` for any `dict` value whose key matches `authorization` (case-insensitive) and replaces the value with `***`. Applied to both console and file handlers.
- **`TAIGA_PROJECT_ID` must be a real project in the `.env` account.** Using a foreign project causes 403 on writes.
- **Auth token is session-scoped (step-2+):** One `POST /auth` per pytest session. Never call it again inside individual test functions.
- **`load_config()` raises `RuntimeError`** on missing/blank vars — `pytest_configure` converts this to `pytest.exit()` with returncode 1. Do not swallow this exception.
- **No bare `except:`** anywhere — always name the exact exception type.

## Conventions

- Stdlib-first: prefer `logging.config.dictConfig` over third-party logging libraries.
- Structured logging: use `logger.debug("event_name", extra={...})` — never f-string interpolation in the message string.
- Retries on external calls: warn and retry, then re-raise the last exception with context.
- Functional style preferred; OOP only for `logging.Filter` subclasses and connectors to external systems.
- All imports at top of every file.

## Required Skills (for implementer agents)

- `python-best-practices`
- `python-testing`
- `pytest-skill`
- `testing-strategies`
- `superpowers:verification-before-completion`

## Required Agents

| Task | Agent |
|---|---|
| Writing or editing any test file | `python-test-engineer` |
| Reviewing API test suites | `api-test-reviewer` |
| Security review of auth/input handling | `security-auditor` |
| Codebase research (multi-step) | `codebase-intel` |
