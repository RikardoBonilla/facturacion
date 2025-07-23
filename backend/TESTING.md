# Testing Documentation

This document explains the testing strategy and setup for the Colombian Electronic Invoicing System.

## Overview

The project uses pytest for comprehensive testing with the following approach:
- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Database and API endpoint testing
- **Coverage Reporting**: Minimum 80% code coverage requirement
- **Async Support**: Full async/await testing support

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests (fast, isolated)
│   ├── __init__.py
│   └── test_auth.py           # Authentication service tests
└── integration/               # Integration tests (slower, database)
    ├── __init__.py
    ├── test_auth_endpoints.py  # Authentication endpoint tests
    ├── test_empresas_endpoints.py
    └── test_clientes_endpoints.py
```

## Configuration

### pytest.ini
- Async mode enabled automatically
- Coverage reporting configured
- Test markers for categorization
- Minimum 80% coverage requirement

### .coveragerc
- Source code analysis configuration
- HTML and XML report generation
- Branch coverage enabled
- Exclusion patterns for test files

## Running Tests

### Quick Commands

```bash
# Run all tests with coverage
python scripts/run_tests.py all

# Run only unit tests (fast)
python scripts/run_tests.py unit

# Run only integration tests
python scripts/run_tests.py integration

# Run authentication tests
python scripts/run_tests.py auth

# Generate coverage reports
python scripts/run_tests.py coverage
```

### Direct pytest Commands

```bash
# All tests with coverage
pytest -v --cov=app --cov-report=html

# Unit tests only
pytest tests/unit/ -v -m unit

# Integration tests only
pytest tests/integration/ -v -m integration

# Specific test markers
pytest -v -m "auth or crud"

# Run with verbose output and timing
pytest -v --durations=10
```

## Test Database

### Docker Setup
```bash
# Start test database
docker-compose up -d db_test

# Check database connection
python scripts/run_tests.py check-db
```

### Configuration
- **URL**: `postgresql://admin:admin123@localhost:5433/facturacion_test`
- **Port**: 5433 (different from main database)
- **Storage**: tmpfs for faster test execution
- **Isolation**: Each test uses transaction rollback for cleanup

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Database/API integration tests
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.crud` - CRUD operation tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.database` - Tests requiring database

## Fixtures

### Database Fixtures
- `test_engine` - Test database engine
- `db_session` - Clean database session per test
- `override_get_db` - Override FastAPI database dependency

### Authentication Fixtures
- `auth_service` - Authentication service instance
- `authenticated_headers` - Bearer token headers for requests

### Data Fixtures
- `test_empresa` - Sample company
- `test_usuario` - Sample user
- `test_cliente` - Sample client
- `test_producto` - Sample product

### Client Fixtures
- `client` - Synchronous test client
- `async_client` - Asynchronous test client

## Writing Tests

### Unit Test Example
```python
@pytest.mark.unit
def test_password_hashing(auth_service: AuthService):
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = auth_service.get_password_hash(password)
    
    assert hashed != password
    assert auth_service.verify_password(password, hashed) is True
```

### Integration Test Example
```python
@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_usuario: Usuario):
    """Test successful login"""
    login_data = {
        "username": test_usuario.email,
        "password": "testpass123"
    }
    
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
```

### Async Test Guidelines
- Use `@pytest.mark.asyncio` for async tests
- Use `async_client` fixture for API calls
- Await all async operations
- Use `await db_session.commit()` when needed

## Test Data Management

### Automatic Cleanup
- Each test runs in a database transaction
- Automatic rollback after test completion
- No manual cleanup required

### Test Isolation
- Tests don't interfere with each other
- Fresh database session per test
- Parametrized fixtures for different scenarios

## Coverage Reports

### HTML Report
- Generated in `htmlcov/` directory
- Interactive coverage visualization
- Line-by-line coverage details

### Terminal Report
- Summary displayed after test run
- Missing lines highlighted
- Coverage percentage per module

### XML Report
- `coverage.xml` for CI/CD integration
- Compatible with most CI systems
- Machine-readable format

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### Async Testing
- Always use `async_client` for API tests
- Don't mix sync and async database operations
- Use proper async fixtures

### Database Testing
- Use transactions for isolation
- Don't rely on specific database state
- Create minimal test data

### Authentication Testing
- Use `authenticated_headers` fixture
- Test both authenticated and unauthenticated scenarios
- Verify proper authorization

### Performance Testing
- Mark slow tests with `@pytest.mark.slow`
- Use `--durations` to identify slow tests
- Optimize database operations

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    docker-compose up -d db_test
    python scripts/run_tests.py all
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

### Pre-commit Hooks
```bash
# Run fast tests before commit
python scripts/run_tests.py unit
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if test database is running
   docker-compose ps db_test
   
   # Start test database
   docker-compose up -d db_test
   ```

2. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

3. **Async Test Issues**
   ```python
   # Use async fixtures and clients
   async def test_example(async_client: AsyncClient):
       response = await async_client.get("/api/v1/endpoint")
   ```

4. **Coverage Too Low**
   ```bash
   # Check uncovered lines
   coverage report --show-missing
   
   # Generate HTML report for detailed view
   coverage html
   ```

### Database Reset
```bash
# Reset test database
docker-compose down db_test
docker-compose up -d db_test
```

## Test Metrics

### Current Coverage
- Target: 80% minimum
- Unit tests: Fast execution (< 1s per test)
- Integration tests: Moderate execution (< 5s per test)

### Performance Goals
- Full test suite: < 30 seconds
- Unit tests only: < 5 seconds
- Database setup: < 2 seconds

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python scripts/run_tests.py all` | Run all tests with coverage |
| `python scripts/run_tests.py unit` | Run unit tests only |
| `python scripts/run_tests.py integration` | Run integration tests |
| `python scripts/run_tests.py auth` | Run auth tests |
| `python scripts/run_tests.py coverage` | Generate coverage reports |
| `pytest -v -k "test_name"` | Run specific test |
| `pytest -v -m "unit"` | Run tests with marker |
| `pytest --lf` | Run only failed tests |

For more information, see the [pytest documentation](https://docs.pytest.org/).