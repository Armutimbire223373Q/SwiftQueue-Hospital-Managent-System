#!/usr/bin/env python3
"""
Fix test fixtures to use the proper test database.
Remove local db_session fixtures and use client fixture instead.
"""

import re
from pathlib import Path

def fix_test_fixtures(file_path):
    """Fix fixtures in a test file to use client instead of db_session."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements = []
    
    # Remove the local db_session fixture definition (it's wrong)
    pattern1 = r'@pytest\.fixture\s*\ndef db_session\(\):.*?(?=\n@pytest\.fixture|\nclass |\ndef test_|\Z)'
    if re.search(pattern1, content, re.DOTALL):
        content = re.sub(pattern1, '', content, flags=re.DOTALL)
        replacements.append("Removed db_session fixture")
    
    # Replace db_session parameter with client in all fixtures
    # Pattern: def fixture_name(db_session): or def fixture_name(db_session, ...):
    pattern2 = r'def (\w+_token|sample_\w+|drug_interactions)\((db_session)(,|\))' 
    if re.search(pattern2, content):
        content = re.sub(pattern2, r'def \1(client\3', content)
        replacements.append("Changed fixture parameters from db_session to client")
    
    # Replace db_session.add() calls with direct API calls (users should be created via API)
    # This is more complex - need to rewrite fixtures to use client.post() instead
    
    # For now, let's just print what needs fixing
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: {', '.join(replacements)}")
        return len(replacements)
    else:
        print(f"ℹ️  {file_path.name}: No changes needed")
        return 0

def main():
    """Fix test fixtures in all test files."""
    
    # Get the tests directory
    tests_dir = Path(__file__).parent / "tests"
    
    # Files to fix
    test_files = [
        "test_prescriptions.py",
        "test_inventory.py",
        "test_patient_portal.py",
    ]
    
    print("🔧 Fixing test fixtures to use proper test database...\n")
    
    total_files = 0
    
    for filename in test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            count = fix_test_fixtures(file_path)
            if count > 0:
                total_files += 1
        else:
            print(f"⚠️  {filename}: File not found")
    
    print(f"\n✅ Fixed {total_files} files")
    print("\n⚠️  MANUAL STEP REQUIRED:")
    print("Token fixtures need to be rewritten to:")
    print("1. Use client.post('/api/auth/register') to create users")
    print("2. Use client.post('/api/auth/login') to get tokens")
    print("3. Remove direct database access (db_session.add/commit)")

if __name__ == "__main__":
    main()
