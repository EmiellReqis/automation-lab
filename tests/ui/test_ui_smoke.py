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
