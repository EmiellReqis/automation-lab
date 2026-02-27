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
pytest -m smoke -q
pytest -m integration -q
pytest -m "api and smoke" -q
pytest -m "api and integration" -q
```
If tests require a running app on a non-default address/port, set BASE_URL:
```
BASE_URL=http://127.0.0.1:8000 pytest -q
```

## Project structure
```text
automation-lab/
├─ app/                      # FastAPI sample service (system under test)
│  └─ main.py                # FastAPI app entrypoint (FastAPI() instance)
├─ tests/                    # pytest test suite
│  └─ api
│     └─   test_health.py         # example API test(s)
│  └─ ui
│     └─   TODO
│  └─ unit
│     └─   TODO
├─ requirements.txt          # Python dependencies
├─ requirements-dev.txt      # Dev dependencies
├─ pytest.ini                # pytest settings
├─ pyproject.toml            # ruff settings
└─ README.md                 # project documentation
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