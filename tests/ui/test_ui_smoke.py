import importlib
from pathlib import Path

import pytest

from tests.config import BASE_URL

playwright_installed = importlib.util.find_spec("playwright") is not None


@pytest.mark.ui
@pytest.mark.skipif(
    not playwright_installed,
    reason="Playwright not installed. Install UI deps: pip install -r requirements-ui.txt",
)
def test_ui_can_open_fastapi_docs(sut_server):
    """
    Minimal UI smoke test:
    - requires Playwright package + browser binaries
    - opens FastAPI /docs page (HTML)
    """
    from playwright.sync_api import Error, sync_playwright

    with sync_playwright() as p:
        chromium_exe = Path(p.chromium.executable_path)

        if not chromium_exe.exists():
            pytest.skip(
                "Playwright browsers not installed (Chromium missing). "
                "Run: python -m playwright install chromium"
            )

        try:
            browser = p.chromium.launch(headless=True)
        except Error as e:
            pytest.skip(
                "Unable to launch Chromium. "
                "Ensure browsers and system deps are installed. "
                "Try: python -m playwright install chromium "
                "and/or: python -m playwright install-deps\n"
                f"Details: {e!r}"
            )

        page = browser.new_page()
        response = page.goto(f"{BASE_URL}/docs", wait_until="domcontentloaded")

        assert response is not None
        assert response.ok

        # A simple, stable assertion for FastAPI docs:
        assert "Swagger UI" in page.title()

        browser.close()
