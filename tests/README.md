# PostBot Test Suite

Comprehensive test suite for the PostBot application.

## Structure

```
tests/
├── conftest.py           # Shared fixtures and configuration
├── unit/                 # Unit tests (fast, isolated)
│   ├── test_exceptions.py
│   ├── test_settings.py
│   ├── test_config.py
│   └── ...
└── integration/          # Integration tests
    ├── test_health_endpoint.py
    └── ...
```

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### With Coverage
```bash
pytest --cov=src/backend --cov-report=html
```

### Specific Test File
```bash
pytest tests/unit/test_exceptions.py
```

### Specific Test
```bash
pytest tests/unit/test_exceptions.py::TestExceptions::test_base_exception
```

### By Marker
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Exclude slow tests
```

## Test Markers

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.agent` - AI agent workflow tests

## Writing Tests

### Unit Test Example
```python
import pytest
from src.backend.exceptions import DatabaseException

class TestDatabaseOperations:
    """Test database operations."""
    
    def test_create_record(self, test_db_session):
        """Test creating a record."""
        # Arrange
        data = {"name": "test"}
        
        # Act
        result = create_record(test_db_session, data)
        
        # Assert
        assert result.name == "test"
```

### Integration Test Example
```python
class TestAPIEndpoint:
    """Test API endpoints."""
    
    def test_get_content(self, test_client, mock_auth_token):
        """Test getting content."""
        headers = {"Authorization": f"Bearer {mock_auth_token}"}
        response = test_client.get("/api/content", headers=headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

## Fixtures

### Available Fixtures (see `conftest.py`)

- `test_db_engine` - Test database engine (session scope)
- `test_db_session` - Test database session (function scope)
- `test_client` - FastAPI test client
- `mock_auth_token` - Mock authentication token
- `test_user_data` - Sample user data

## Environment Variables

Set these for testing:

```bash
# Required
TEST_DATABASE_URL=postgresql://localhost/postbot_test

# Optional
AUTH_PROVIDER=supabase
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test_key
```

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Manual workflow dispatch

See `.github/workflows/test.yml` for CI configuration.

## Coverage Goals

Target coverage: **80%+**

Current coverage:
- Overall: TBD
- Unit tests: TBD
- Integration tests: TBD

View coverage report:
```bash
pytest --cov=src/backend --cov-report=html
open htmlcov/index.html
```

## Next Steps

### High Priority Tests to Add

1. **API Endpoints**
   - `tests/integration/test_content_api.py`
   - `tests/integration/test_auth_api.py`
   - `tests/integration/test_profiles_api.py`

2. **Database Repositories**
   - `tests/unit/test_content_repository.py`
   - `tests/unit/test_profile_repository.py`
   - `tests/unit/test_source_repository.py`

3. **Authentication**
   - `tests/unit/test_auth_factory.py`
   - `tests/integration/test_supabase_auth.py`

4. **Agent Workflows**
   - `tests/unit/test_blog_agent.py`
   - `tests/integration/test_workflow_execution.py`

5. **Extractors**
   - `tests/unit/test_twitter_extractor.py`
   - `tests/unit/test_reddit_extractor.py`

## Troubleshooting

### Tests Failing?

1. Check database connection
2. Verify environment variables
3. Clear test database: `dropdb postbot_test && createdb postbot_test`
4. Run with verbose output: `pytest -vv`

### Slow Tests?

1. Use `-m "not slow"` to skip slow tests
2. Run unit tests first: `pytest tests/unit/`
3. Use `pytest-xdist` for parallel execution: `pytest -n auto`

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
