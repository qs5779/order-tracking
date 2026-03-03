"""Tests level module."""

import shutil
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import Client


@pytest.fixture(scope="session", autouse=True)
def setup_test_session():  # noqa: WPS210
    print("\n[Session Fixture] Setting up resources for ALL tests...")  # noqa: WPS421
    repo_path = Path(__file__).parent.parent
    storage_path = repo_path / "storage"
    test_db_path = repo_path / "tests/data/test.db"
    storage_path.mkdir(exist_ok=True, mode=0o755)
    shutil.copy(test_db_path, storage_path)
    yield storage_path  # Pass the resource to tests
    print("\n[Session Fixture] Cleanup resources after ALL tests...")  # noqa: WPS421
    # Delete everything reachable from the directory "top".
    # CAUTION:  This is dangerous! For example, if top == Path('/'),
    # it could delete all of your files.
    for root, dirs, files in storage_path.walk(top_down=False):
        for name in files:
            (root / name).unlink()
        for name in dirs:
            (root / name).rmdir()
    storage_path.rmdir()


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
