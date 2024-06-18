"""Tests test_routes level module."""

from fastapi.testclient import TestClient


def test_health_route(client: TestClient, version: str) -> None:
    response = client.get("/health")
    text = "Healthy version: {0}".format(version)
    assert response.status_code == 200
    assert text in response.text
