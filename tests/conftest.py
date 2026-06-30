import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEST_DB_PATH = Path("test_aiot.db")
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB_PATH}"
os.environ["MIGRATION_DATABASE_URL"] = f"sqlite:///./{TEST_DB_PATH}"

from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
import app.models.emoticare  # noqa: E402, F401


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(fastapi_app)
