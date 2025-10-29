#!/usr/bin/env python3
"""
Convert all test fixtures from direct database access to API-based creation.
This ensures fixtures use the test database properly.
"""

import re
from pathlib import Path

def convert_fixture_to_api(fixture_text):
    """Convert a fixture from db_session to client-based."""
    
    # Extract user data from the User() creation
    name_match = re.search(r'name="([^"]+)"', fixture_text)
    email_match = re.search(r'email="([^"]+)"', fixture_text)
    phone_match = re.search(r'phone="([^"]+)"', fixture_text)
    role_match = re.search(r'role="([^"]+)"', fixture_text)
    password_match = re.search(r'get_password_hash\("([^"]+)"\)', fixture_text)
    
    if not all([name_match, email_match, role_match, password_match]):
        return None
    
    name = name_match.group(1)
    email = email_match.group(1)
    phone = phone_match.group(1) if phone_match else "0000000000"
    role = role_match.group(1)
    password = password_match.group(1)
    
    # Get fixture name
    fixture_name_match = re.search(r'def (\w+)\(', fixture_text)
    fixture_name = fixture_name_match.group(1) if fixture_name_match else "unknown"
    
    # Check if this is a token fixture or a user fixture
    if "return response.json()" in fixture_text or "_token" in fixture_name:
        # This is a token fixture
        return f'''@pytest.fixture
def {fixture_name}(client):
    """Create a {role} user and return auth token."""
    # Register {role} user
    user_data = {{
        "name": "{name}",
        "email": "{email}",
        "phone": "{phone}",
        "password": "{password}",
        "role": "{role}",
        "date_of_birth": "1990-01-01"
    }}
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    response = client.post("/api/auth/login", data={{
        "username": "{email}",
        "password": "{password}"
    }})
    return response.json()["access_token"]'''
    else:
        # This is a user object fixture
        return f'''@pytest.fixture
def {fixture_name}(client):
    """Create a {role} user and return user data."""
    # Register {role} user
    user_data = {{
        "name": "{name}",
        "email": "{email}",
        "phone": "{phone}",
        "password": "{password}",
        "role": "{role}",
        "date_of_birth": "1990-01-01"
    }}
    response = client.post("/api/auth/register", json=user_data)
    return response.json()'''

def fix_file(file_path):
    """Fix all fixtures in a file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove db_session fixture if it exists
    content = re.sub(
        r'@pytest\.fixture\s+def db_session\(\):.*?(?=\n@pytest\.fixture|\nclass |\ndef test_|\Z)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Find all fixtures that use db_session
    fixture_pattern = r'@pytest\.fixture\s+def (\w+)\(db_session\):.*?(?=\n@pytest\.fixture|\nclass |\ndef test_|\Z)'
    
    def replace_fixture(match):
        fixture_text = match.group(0)
        new_fixture = convert_fixture_to_api(fixture_text)
        if new_fixture:
            return new_fixture
        return fixture_text  # Keep original if conversion fails
    
    content = re.sub(fixture_pattern, replace_fixture, content, flags=re.DOTALL)
    
    # Remove unnecessary imports
    if 'from app.models.models import User' in content and 'User(' not in content:
        content = re.sub(r'from app\.models\.models import .*User.*\n', '', content)
    if 'from app.services.auth_service import get_password_hash' in content and 'get_password_hash(' not in content:
        content = re.sub(r'from app\.services\.auth_service import .*get_password_hash.*\n', '', content)
    if 'from app.database import get_db' in content and 'get_db(' not in content:
        content = re.sub(r'from app\.database import get_db\n', '', content)
    if 'from datetime import datetime' in content and 'datetime(' not in content:
        # Keep if used elsewhere
        pass
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all test files."""
    tests_dir = Path(__file__).parent / "tests"
    
    test_files = [
        "test_prescriptions.py",
        "test_inventory.py",
        "test_patient_portal.py",
    ]
    
    print("🔧 Converting test fixtures to API-based...\n")
    
    fixed_count = 0
    for filename in test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            if fix_file(file_path):
                print(f"✅ {filename}: Converted fixtures")
                fixed_count += 1
            else:
                print(f"ℹ️  {filename}: No changes needed")
        else:
            print(f"⚠️  {filename}: Not found")
    
    print(f"\n🎉 Fixed {fixed_count} files!")

if __name__ == "__main__":
    main()
