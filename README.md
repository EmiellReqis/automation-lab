# automation-lab
*Status: Work in progress — learning project*

A mini framework for automating API tests (pytest) using the FastAPI application as an example.

## What's inside
- FastAPI sample app (system-under-test)
- pytest-based API tests
- configuration via env vars

## Requirements
- Python: 3.12.x
- pip + venv

## Quickstart
### Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```
```md
Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install dependencies
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
### Optional (UI only — Playwright):
```
pip install -r requirements-ui.txt
```
Note: Playwright also requires installing browser binaries.
```
python -m playwright install chromium

and/or: python -m playwright install-deps
```
### Run UI tests
```
pytest -m ui -q
```
### Artifacts (on failure / xfail)
UI test artifacts are saved under:

- pytest-logs/ui/

What you’ll find there:

- ui-*.png — screenshot captured on test failure / xfail
- trace-*.zip — Playwright trace recorded on test failure / xfail

### Open Playwright trace
```
python -m playwright show-trace .pytest-logs/ui/trace-<...>.zip
```

### Run the FastAPI app (SUT)
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
### Run tests
Run from repo root

In a new terminal (with the same venv activated):
```
pytest -q
pytest -m api -q
pytest -m unit -q
pytest -m smoke -q
pytest -m integration -q
pytest -m "api and smoke" -q
pytest -m "api and integration" -q
```
Note: UI tests are skipped unless Playwright dependencies are installed.
If tests require a running app on a non-default address/port, set BASE_URL:
```
BASE_URL=http://127.0.0.1:8000 pytest -q
```

## Project structure
```text
automation-lab/
├─ .pytest-logs/                    # Test run artifacts (logs/screenshots/traces)
│  |─ sut                           # SUT (FastAPI) process logs per run
│     └─   sut-*.log                # Uvicorn stdout/stderr captured to file
│  └─ ui                            # UI artifacts (Playwright)
│     |─   trace.zip                # Playwright trace recorded on fail/xfail
│     └─   ui-*.png                 # Screenshot captured on fail/xfail
├─ app/                             # FastAPI sample service (system under test)
│  └─ main.py                       # FastAPI app entrypoint (FastAPI() instance)
├─ tests/                           # pytest test suite
│  └─ api                           # API tests (requests-based)
│     └─   test_health.py           # example API test(s)
│  └─ ui                            # UI tests (Playwright)
|     |─   conftest.py              # Playwright UI fixtures
│     └─   test_ui_smoke.py         # ui test(s)
│  └─ unit                          # Unit tests (fast feedback)
│     └─   test_unit_placeholder.py # placeholder for unit test(s)
|  |─ api_client.py                 # Wrapper for API calls (requests) used in tests
|  |─ config.py                     # Test config (BASE_URL, timeouts, env parsing)
|  |─ conftest.py                   # Pytest fixtures (SUT lifecycle, shared setup)
├─ requirements.txt                 # Python dependencies
├─ requirements-dev.txt             # Dev dependencies
├─ requirements-ui.txt              # UI dependencies
├─ pytest.ini                       # pytest settings
├─ pyproject.toml                   # ruff settings
└─ README.md                        # project documentation
```
## Testing approach
This repository is a learning-focused mini framework for API test automation.
The FastAPI application serves as a local system-under-test (SUT), while the test suite is implemented using `pytest`.

The goal is to evolve towards a maintainable, scalable structure by introducing:
- clear test separation (e.g. smoke vs integration),
- shared fixtures for setup/teardown,
- configuration via environment variables,
- and reusable API client abstractions (added incrementally).

## Roadmap
- [x] Add README quickstart + project structure
- [ ] Add basic linting (ruff/black)
- [ ] Add ApiClient + retries/timeouts
- [ ] Add logging request/response with redaction
- [ ] Add pytest markers smoke/integration
- [ ] Add junitxml/allure reporting
- [ ] Add GitHub Actions CIS