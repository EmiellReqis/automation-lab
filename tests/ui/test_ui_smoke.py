import pytest


@pytest.mark.ui
def test_ui_can_open_fastapi_docs(sut_server, page):
    """
    Minimal UI smoke test:
    - requires Playwright package + browser binaries
    - opens FastAPI /docs page (HTML)
    """

    base_url = sut_server
    response = page.goto(f"{base_url}/docs", wait_until="domcontentloaded")

    assert response is not None
    assert response.ok

    # A simple, stable assertion for FastAPI docs:
    assert "Swagger UI" in page.title()


@pytest.mark.ui
@pytest.mark.xfail(reason="artifact smoke: verify screenshots on failure", strict=True)
def test_ui_forced_fail(sut_server, page):
    """
    Diagnostic UI test used to verify failure artifacts.

    This test is intentionally designed to FAIL (marked as xfail) to ensure that:
    - the Playwright `page` fixture detects a failing outcome,
    - a screenshot is captured and saved to `.pytest-logs/ui/`.

    Do not treat this as a functional UI scenario.
    """
    base_url = sut_server
    page.goto(f"{base_url}/docs", wait_until="domcontentloaded")

    assert "THIS_SHOULD_NEVER_EXIST" in page.content()
