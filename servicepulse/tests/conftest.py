"""Test configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.db.database import Base, get_db
from app.main import app


# Override settings for testing
class TestSettings(Settings):
    app_env: str = "test"
    database_url: str = "sqlite:///./test_servicepulse.db"


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_servicepulse.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_request_data():
    return {
        "customer_id": "CUST-001",
        "request_type": "SERVICE",
        "description": "Unable to access account",
    }


@pytest.fixture
def sample_incident_data():
    return {
        "title": "Elevated processing failures",
        "description": "Processing failure rate exceeded threshold",
        "severity": "HIGH",
        "affected_service": "request_processing",
    }
