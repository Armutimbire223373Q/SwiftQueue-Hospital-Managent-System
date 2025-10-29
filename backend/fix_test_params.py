#!/usr/bin/env python3
"""
Remove db_session parameter from all test functions.
Tests should only use fixtures (tokens, sample data) and make API calls via client.
"""

import re
from pathlib import Path

def remove_db_session_param(file_path):
    """Remove db_session parameter from test functions."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern: def test_name(params, db_session): or def test_name(params, db_session, more_params):
    # Remove ", db_session" from function signatures
    content = re.sub(r'def test_(\w+)\(([^)]*), db_session(,|\))', r'def test_\1(\2\3', content)
    
    # Pattern: def test_name(db_session): (only parameter)
    content = re.sub(r'def test_(\w+)\(db_session\):', r'def test_\1():', content)
    
    # Pattern: def test_name(db_session, other_params):
    content = re.sub(r'def test_(\w+)\(db_session, ([^)]+)\):', r'def test_\1(\2):', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: Removed db_session parameters")
        return True
    else:
        print(f"ℹ️  {file_path.name}: No changes needed")
        return False

def main():
    """Fix all test files."""
    tests_dir = Path(__file__).parent / "tests"
    
    test_files = [
        "test_prescriptions.py",
        "test_inventory.py",
        "test_patient_portal.py",
    ]
    
    print("🔧 Removing db_session parameters from test functions...\n")
    
    fixed_count = 0
    for filename in test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            if remove_db_session_param(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  {filename}: Not found")
    
    print(f"\n✅ Fixed {fixed_count} files!")

if __name__ == "__main__":
    main()
