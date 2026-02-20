import pytest

@pytest.mark.smoke
def test_health_endpoint(sut_server, api_client):
    r = api_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.integration
def test_sum_endpoint(sut_server, api_client):
    r = api_client.get("/sum",
                     params={"a": 2, "b": 3})
    assert r.status_code == 200
    assert r.json()["sum"] == 5
