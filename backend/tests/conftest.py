import os
import sys

# Set UTF-8 encoding for Windows compatibility with emojis in output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Disable rate limiting for tests - MUST be set before importing app
os.environ["RATE_LIMIT_ENABLED"] = "false"

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
    import uuid
    from starlette.testclient import TestClient
    
    # Create a new test client with auth headers (don't modify shared client)
    auth_test_client = TestClient(app)
    
    # Register and login a test user with unique email
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": "Test Auth User",
        "email": f"auth_test_{unique_id}@example.com",
        "password": "testpass123",
        "role": "patient"
    }
    
    # Register user
    register_response = auth_test_client.post("/api/auth/register", json=user_data)
    if register_response.status_code != 200:
        print(f"Registration failed: {register_response.status_code} - {register_response.text}")
    
    # Login to get token (using form data, not JSON)
    login_data = {
        "username": user_data["email"],  # OAuth2 uses 'username' field
        "password": user_data["password"]
    }
    response = auth_test_client.post("/api/auth/login", data=login_data)  # Use data= for form data
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        raise ValueError(f"Auth client login failed: {response.status_code} - {response.text}")
    token = response.json()["access_token"]
    
    # Set authorization header
    auth_test_client.headers = {
        **auth_test_client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return auth_test_client

@pytest.fixture
def admin_client(client):
    """Create an authenticated admin test client."""
    import uuid
    from starlette.testclient import TestClient
    
    # Create a new test client with admin auth headers (don't modify shared client)
    admin_test_client = TestClient(app)
    
    # Register and login an admin user with unique email
    unique_id = str(uuid.uuid4())[:8]
    admin_data = {
        "name": "Test Admin User",
        "email": f"admin_auth_test_{unique_id}@example.com",
        "password": "adminpass123",
        "role": "admin"
    }
    
    # Register admin
    register_response = admin_test_client.post("/api/auth/register", json=admin_data)
    if register_response.status_code != 200:
        print(f"Registration failed: {register_response.status_code} - {register_response.text}")
    
    # Login to get token (using form data, not JSON)
    login_data = {
        "username": admin_data["email"],  # OAuth2 uses 'username' field
        "password": admin_data["password"]
    }
    response = admin_test_client.post("/api/auth/login", data=login_data)  # Use data= for form data
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} - {response.text}")
        raise ValueError(f"Admin login failed: {response.status_code} - {response.text}")
    token = response.json()["access_token"]
    
    # Set authorization header
    admin_test_client.headers = {
        **admin_test_client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return admin_test_client

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