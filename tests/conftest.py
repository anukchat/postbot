"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
from fastapi.testclient import TestClient

# Ensure required env vars exist BEFORE importing src.backend.api.api (which validates settings at import time)
# Force deterministic values for the test run so developers' local env doesn't leak into test behavior.
os.environ["ENVIRONMENT"] = "test"
os.environ["AUTH_PROVIDER"] = "supabase"

# Provide dummy Supabase config for settings validation.
# These should NOT be real secrets.
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

# Use a syntactically valid Postgres URL by default so SQLAlchemy + psycopg can parse it.
# The database does not need to be running for most tests; readiness may return 503.
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/postbot_test",
)


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
