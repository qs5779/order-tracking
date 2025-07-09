"""Tests test_routes level module."""

from fastapi.testclient import TestClient


def test_default_route(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    checks = ("Show Pending Orders", "Show All Orders", "Add Order", "Health Check")
    for text in checks:
        assert text in response.text


def test_favicon_route(client: TestClient) -> None:
    response = client.get("/favicon.ico")
    assert response.status_code == 200


def test_docs_route(client: TestClient) -> None:
    response = client.get("/docs/")
    assert response.status_code == 200


def test_health_route(client: TestClient, version: str) -> None:
    response = client.get("/health")
    text = "Healthy version: {0}".format(version)
    assert response.status_code == 200
    assert text in response.text


def test_orders_route(client: TestClient, version: str) -> None:
    response = client.get("/orders/")
    checks = ("Version: {0}".format(version), "Number of orders displayed: 49")
    assert response.status_code == 200
    for text in checks:
        assert text in response.text


def test_orders_pending_route(client: TestClient, version: str) -> None:
    response = client.get("/orders/pending")
    checks = ("Version: {0}".format(version), "Number of orders displayed: 2")
    assert response.status_code == 200
    for text in checks:
        assert text in response.text


def test_add_order_route(client: TestClient, version: str) -> None:
    response = client.get("/forms/fetch/0")
    checks = ("Add Order", "Order ID 0", "Shipped")
    assert response.status_code == 200
    for text in checks:
        assert text in response.text
