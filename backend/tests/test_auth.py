import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.auth_service import create_user, authenticate_user, get_user_by_email

def test_create_user(db: Session):
    """Test user creation."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }

    user = create_user(db, **user_data)

    assert user.name == user_data["name"]
    assert user.email == user_data["email"]
    assert user.role == user_data["role"]
    assert user.password_hash is not None
    assert user.password_hash != user_data["password"]  # Should be hashed

def test_authenticate_user(db: Session):
    """Test user authentication."""
    # Create a test user
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }
    create_user(db, **user_data)

    # Test successful authentication
    user = authenticate_user(db, user_data["email"], user_data["password"])
    assert user is not None
    assert user.email == user_data["email"]

    # Test failed authentication - wrong password
    user = authenticate_user(db, user_data["email"], "wrongpassword")
    assert user is False

    # Test failed authentication - wrong email
    user = authenticate_user(db, "wrong@example.com", user_data["password"])
    assert user is False

def test_get_user_by_email(db: Session):
    """Test getting user by email."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }
    create_user(db, **user_data)

    user = get_user_by_email(db, user_data["email"])
    assert user is not None
    assert user.email == user_data["email"]

    # Test non-existent user
    user = get_user_by_email(db, "nonexistent@example.com")
    assert user is None

def test_register_user_endpoint(client: TestClient):
    """Test user registration endpoint."""
    user_data = {
        "name": "API Test User",
        "email": "api_test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data

def test_login_endpoint(client: TestClient):
    """Test user login endpoint."""
    # First register a user
    user_data = {
        "name": "Login Test User",
        "email": "login_test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }

    client.post("/api/auth/register", json=user_data)

    # Now try to login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }

    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_credentials(client: TestClient):
    """Test login with wrong credentials."""
    login_data = {
        "username": "wrong@example.com",
        "password": "wrongpassword"
    }

    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401

def test_get_current_user_endpoint(client: TestClient):
    """Test getting current user endpoint."""
    # Register and login first
    user_data = {
        "name": "Current User Test",
        "email": "current_test@example.com",
        "password": "testpassword123",
        "role": "patient"
    }

    client.post("/api/auth/register", json=user_data)

    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }

    login_response = client.post("/api/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Now get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]

def test_get_all_users_endpoint(client: TestClient):
    """Test getting all users endpoint (admin only)."""
    # Create admin user
    admin_data = {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpass123",
        "role": "admin"
    }

    client.post("/api/auth/register", json=admin_data)

    login_data = {
        "username": admin_data["email"],
        "password": admin_data["password"]
    }

    login_response = client.post("/api/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Get all users
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/users", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the admin user