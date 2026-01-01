"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    from src.backend.db.models import Base
    
    engine = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False} if "sqlite" in os.environ["DATABASE_URL"] else {}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_client():
    """Create test client for FastAPI app."""
    from src.backend.api.api import app
    return TestClient(app)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token for testing."""
    return "test_token_12345"


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "test@example.com",
        "full_name": "Test User"
    }
