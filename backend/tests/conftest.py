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
    # Create all tables before running tests
    Base.metadata.create_all(bind=test_engine)
    
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
    Base.metadata.drop_all(bind=test_engine)

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

@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    # Register and login a test user
    user_data = {
        "name": "Test Auth User",
        "email": "auth_test@example.com",
        "password": "testpass123",
        "role": "patient"
    }
    
    # Register user
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    token = response.json()["access_token"]
    
    # Add authorization header to client
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return client

@pytest.fixture
def test_admin_token(client):
    """Get an admin authentication token."""
    # Register admin user
    admin_data = {
        "name": "Admin User",
        "email": "admin_test@example.com",
        "password": "adminpass123",
        "role": "admin"
    }
    
    client.post("/api/auth/register", json=admin_data)
    
    # Login
    login_data = {
        "email": admin_data["email"],
        "password": admin_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]