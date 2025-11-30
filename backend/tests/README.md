# Psi Backend Test Suite

Comprehensive test suite for the Psi emotion-based wellness platform backend.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── pytest.ini                           # Pytest configuration
├── test_food_analysis.py               # Original food analysis tests
├── test_food_api_comprehensive.py      # Comprehensive API tests
├── test_fridge_detection.py            # Fridge detection tests
├── test_wellness_analysis.py           # Wellness analysis tests
└── README.md                           # This file
```

## Test Categories

### 1. Unit Tests
Test individual functions and methods in isolation.

```bash
pytest tests/test_food_api_comprehensive.py::TestFoodUploadServiceUnit -v
```

### 2. Integration Tests
Test API endpoints with mocked dependencies.

```bash
pytest tests/test_food_api_comprehensive.py::TestFoodAPIIntegration -v
```

### 3. Security Tests
Test security vulnerabilities and attack vectors.

```bash
pytest tests/test_food_api_comprehensive.py::TestFoodAPISecurity -v
```

### 4. Performance Tests
Test performance under load and concurrent requests.

```bash
pytest tests/test_food_api_comprehensive.py::TestFoodAPIPerformance -v
```

### 5. Edge Case Tests
Test boundary conditions and unusual inputs.

```bash
pytest tests/test_food_api_comprehensive.py::TestFoodAPIEdgeCases -v
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_food_api_comprehensive.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_food_api_comprehensive.py::TestFoodAPISecurity -v
```

### Run Specific Test Method
```bash
pytest tests/test_food_api_comprehensive.py::TestFoodAPISecurity::test_file_size_limit_enforced -v
```

### Run Tests by Marker
```bash
# Security tests only
pytest -m security -v

# Skip slow tests
pytest -m "not slow" -v

# Integration tests only
pytest -m integration -v
```

### Run Tests in Parallel
```bash
pytest tests/ -n auto  # Requires pytest-xdist
```

## Test Coverage

### Generate Coverage Report
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

### View HTML Coverage Report
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals
- **Overall**: > 80%
- **Critical paths**: > 95%
- **Security functions**: 100%

## Test Data

### Sample Images
Tests use programmatically generated images:
- Valid images (800x600 JPEG)
- Small images (50x50 - should fail)
- Large images (>10MB - should fail)
- Corrupted images (invalid data)

### Mock Users
- `user-123-456-789` - Default test user
- `user-1`, `user-2` - For isolation tests

### Mock Tokens
- `Bearer mock-jwt-token-12345` - Default auth token

## Writing New Tests

### Test Naming Convention
```python
def test_<feature>_<scenario>_<expected_result>():
    """Clear docstring explaining what is tested"""
    pass
```

### Example Test
```python
@pytest.mark.asyncio
async def test_upload_image_with_valid_file_returns_analysis(
    sample_image_bytes,
    mock_user_id
):
    """Test that uploading valid image returns food analysis"""
    service = FoodUploadService()

    # Arrange
    service.db_service.check_daily_usage = AsyncMock(return_value=0)

    # Act
    result = await service.process_food_image(
        sample_image_bytes,
        mock_user_id,
        "test.jpg"
    )

    # Assert
    assert result is not None
    assert result.total_calories > 0
```

## Mocking Guidelines

### Mock External Services
Always mock:
- Database connections
- S3/AWS services
- Redis cache
- YOLO model
- Claude API
- External APIs

### Use AsyncMock for Async Functions
```python
from unittest.mock import AsyncMock

service.async_method = AsyncMock(return_value=expected_value)
```

### Patch at the Right Level
```python
# Good - patches where it's used
@patch('app.api.v1.food_enhanced.food_service')

# Bad - patches at import level
@patch('app.services.image_recognition.YOLO')
```

## Test Fixtures

### Available Fixtures (conftest.py)
- `event_loop` - Async event loop
- `test_settings` - Test configuration
- `mock_redis` - Mock Redis client
- `mock_database` - Mock database
- `mock_s3_client` - Mock S3 client

### Test-Specific Fixtures
- `client` - FastAPI test client
- `mock_auth_token` - JWT token
- `mock_user_id` - User ID
- `sample_image_bytes` - Valid image
- `large_image_bytes` - Large image
- `corrupted_image_bytes` - Invalid image

## Continuous Integration

### GitHub Actions
Tests run automatically on:
- Pull requests
- Pushes to main/develop
- Nightly builds

### Pre-commit Hook
Run tests before committing:
```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ -x --tb=short
```

## Debugging Tests

### Run with Debug Output
```bash
pytest tests/ -v --tb=long --log-cli-level=DEBUG
```

### Run Single Test with PDB
```bash
pytest tests/test_food_api_comprehensive.py::test_name -v --pdb
```

### Print Statements
```python
def test_something():
    print("Debug info")  # Shown with -s flag

# Run with: pytest -s
```

## Performance Benchmarks

### Expected Test Performance
- Unit tests: < 0.1s each
- Integration tests: < 1s each
- Security tests: < 2s each
- Performance tests: < 5s each

### Slow Tests
Mark slow tests:
```python
@pytest.mark.slow
def test_large_dataset():
    pass
```

Skip with: `pytest -m "not slow"`

## Known Issues

### Issue #1: Async Tests on Windows
Some async tests may fail on Windows. Use `asyncio_mode = auto` in pytest.ini.

### Issue #2: Database Cleanup
Tests may leave data in test database. Run cleanup:
```bash
python scripts/cleanup_test_db.py
```

## Contributing

When adding tests:
1. Follow naming conventions
2. Add docstrings
3. Use appropriate fixtures
4. Mark test category (unit/integration/security)
5. Ensure tests are independent
6. Clean up resources
7. Update this README if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Async Testing](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
