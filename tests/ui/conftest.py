from datetime import datetime
from pathlib import Path

import pytest

from tests.config import PW_HEADLESS


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        item.rep_call = rep
    elif rep.when == "setup":
        item.rep_setup = rep
    elif rep.when == "teardown":
        item.rep_teardown = rep


@pytest.fixture(scope="session")
def pw():
    playwright = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright not installed. Install UI deps: pip install -r requirements-ui.txt",
    )

    with playwright.sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(pw):
    from playwright.sync_api import Error

    chromium_exe = Path(pw.chromium.executable_path)
    if not chromium_exe.exists():
        pytest.skip(
            "Playwright browsers not installed (Chromium missing). "
            "Run: python -m playwright install chromium"
        )
    browser = None
    try:
        browser = pw.chromium.launch(headless=PW_HEADLESS)
    except Error as e:
        pytest.skip(
            "Unable to launch Chromium. "
            "Ensure browsers and system deps are installed. "
            "Try: python -m playwright install chromium "
            "and/or: python -m playwright install-deps\n"
            f"Details: {e!r}"
        )

    try:
        yield browser
    finally:
        if browser:
            browser.close()


@pytest.fixture(scope="function")
def page(browser, request):
    logs_dir = Path(".pytest-logs/ui")
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = logs_dir / f"ui-{ts}.png"

    page = browser.new_page()
    try:
        yield page
    finally:
        rep = getattr(request.node, "rep_call", None)
        failed = bool(rep and rep.failed)
        xfail = bool(rep and getattr(rep, "wasxfail", False))
        if failed or xfail:
            page.screenshot(path=log_path)
        page.close()
