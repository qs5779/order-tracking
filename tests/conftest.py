"""Tests level module."""

import pytest
from fastapi import FastAPI
from httpx import Client


@pytest.fixture
def app() -> FastAPI:
    from app.main import app

    return app


@pytest.fixture
def client(app: FastAPI) -> Client:
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture
def version() -> str:
    from app.constants import VERSION

    return VERSION
