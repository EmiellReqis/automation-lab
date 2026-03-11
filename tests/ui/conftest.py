from pathlib import Path

import pytest

from tests.config import PW_HEADLESS


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
def page(browser):
    page = browser.new_page()
    try:
        yield page
    finally:
        page.close()
