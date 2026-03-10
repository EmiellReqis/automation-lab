import importlib

import pytest

playwright_installed = importlib.util.find_spec("playwright") is not None


@pytest.mark.ui
@pytest.mark.skipif(
    not playwright_installed,
    reason="Playwright not installed yet / UI suite placeholder",
)
def test_ui_placeholder():
    # Sanity-check: module import works when dependency is installed.
    from playwright.sync_api import sync_playwright  # noqa: F401

    assert True
