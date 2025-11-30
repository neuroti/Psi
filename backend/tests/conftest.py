"""
Pytest Configuration and Shared Fixtures
Provides common setup for all test files
"""
import pytest
import asyncio
from typing import Generator
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Test settings override production settings"""
    return {
        "POSTGRES_SERVER": "localhost",
        "POSTGRES_DB": "test_psi_db",
        "MONGODB_URL": "mongodb://localhost:27017",
        "MONGODB_DB": "test_psi",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": 6379,
        "SECRET_KEY": "test-secret-key-12345",
        "FREE_TIER_DAILY_LIMIT": 3,
        "YOLO_HIGH_CONFIDENCE_THRESHOLD": 0.8,
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Clear any cached service instances
    yield
    # Cleanup after test


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    from unittest.mock import Mock

    redis_mock = Mock()
    redis_mock.get = Mock(return_value=None)
    redis_mock.set = Mock(return_value=True)
    redis_mock.setex = Mock(return_value=True)
    redis_mock.ping = Mock(return_value=True)

    return redis_mock


@pytest.fixture
def mock_database():
    """Mock database connection for testing"""
    from unittest.mock import AsyncMock, Mock

    db_mock = Mock()
    db_mock.execute_query = AsyncMock(return_value=[])
    db_mock.execute_one = AsyncMock(return_value=None)
    db_mock.execute = AsyncMock(return_value="OK")

    return db_mock


@pytest.fixture
def mock_s3_client():
    """Mock AWS S3 client"""
    from unittest.mock import Mock

    s3_mock = Mock()
    s3_mock.put_object = Mock(return_value={'ETag': 'abc123'})
    s3_mock.get_object = Mock(return_value={'Body': b'image data'})

    return s3_mock


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
