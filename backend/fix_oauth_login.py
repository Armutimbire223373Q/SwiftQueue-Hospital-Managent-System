#!/usr/bin/env python3
"""
Fix OAuth2 login format in test files.
Changes from JSON format to form data format for OAuth2PasswordRequestForm.
"""

import re
from pathlib import Path

def fix_oauth_login_in_file(file_path):
    """Fix OAuth2 login calls in a test file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements = 0
    
    # Pattern 1: client.post("/api/auth/login", json={"email": ..., "password": ...})
    # Replace with: client.post("/api/auth/login", data={"username": ..., "password": ...})
    
    # Match multiline login calls with json=
    pattern1 = r'client\.post\(\s*"/api/auth/login"\s*,\s*json\s*=\s*\{([^}]+)\}\s*\)'
    
    def replace_login_call(match):
        nonlocal replacements
        body = match.group(1)
        
        # Replace "email" with "username" in the body
        new_body = body.replace('"email"', '"username"')
        
        replacements += 1
        return f'client.post("/api/auth/login", data={{{new_body}}})'
    
    content = re.sub(pattern1, replace_login_call, content)
    
    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: Made {replacements} replacements")
        return replacements
    else:
        print(f"ℹ️  {file_path.name}: No changes needed")
        return 0

def main():
    """Fix OAuth2 login format in all test files."""
    
    # Get the tests directory
    tests_dir = Path(__file__).parent / "tests"
    
    # Files to fix
    test_files = [
        "test_prescriptions.py",
        "test_inventory.py",
        "test_patient_portal.py",
        "test_security_features.py",
    ]
    
    print("🔧 Fixing OAuth2 login format in test files...\n")
    
    total_replacements = 0
    
    for filename in test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            count = fix_oauth_login_in_file(file_path)
            total_replacements += count
        else:
            print(f"⚠️  {filename}: File not found")
    
    print(f"\n✅ Total replacements: {total_replacements}")
    print("🎉 OAuth2 login format fixed!")

if __name__ == "__main__":
    main()
