import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_queue_management.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create a new session for the test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

    # Drop all tables after test
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    # Override the database dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }

@pytest.fixture
def test_service_data():
    """Sample service data for testing."""
    return {
        "name": "Emergency Department",
        "description": "Emergency medical services",
        "department": "Emergency",
        "estimated_wait_time": 30
    }

@pytest.fixture
def test_queue_data():
    """Sample queue data for testing."""
    return {
        "service_id": 1,
        "patient_name": "John Doe",
        "patient_email": "john@example.com",
        "priority": "normal",
        "symptoms": "Headache and fever"
    }