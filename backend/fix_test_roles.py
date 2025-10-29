#!/usr/bin/env python3
"""
Fix invalid roles in test fixtures.
Valid roles: admin, staff, patient
Invalid roles: doctor, pharmacist -> should be staff
"""

import re
from pathlib import Path

def fix_roles_in_file(file_path):
    """Fix invalid roles in test file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements = 0
    
    # Replace role="doctor" with role="staff"
    if '"role": "doctor"' in content:
        content = content.replace('"role": "doctor"', '"role": "staff"')
        replacements += content.count('"role": "staff"') - original_content.count('"role": "staff"')
    
    # Replace role="pharmacist" with role="staff"
    if '"role": "pharmacist"' in content:
        count_before = content.count('"role": "staff"')
        content = content.replace('"role": "pharmacist"', '"role": "staff"')
        replacements += content.count('"role": "staff"') - count_before
    
    # Update fixture docstrings
    content = re.sub(r'Create a doctor user', 'Create a staff user (doctor)', content)
    content = re.sub(r'Create a pharmacist user', 'Create a staff user (pharmacist)', content)
    
    # Update fixture comments
    content = re.sub(r'# Register doctor user', '# Register staff user (doctor role)', content)
    content = re.sub(r'# Register pharmacist user', '# Register staff user (pharmacist role)', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: Fixed invalid roles")
        return True
    else:
        print(f"ℹ️  {file_path.name}: No changes needed")
        return False

def main():
    """Fix roles in all test files."""
    
    tests_dir = Path(__file__).parent / "tests"
    
    test_files = [
        "test_prescriptions.py",
        "test_inventory.py",
        "test_patient_portal.py",
    ]
    
    print("🔧 Fixing invalid user roles in test files...\n")
    print("Valid roles: admin, staff, patient\n")
    
    fixed_count = 0
    for filename in test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            if fix_roles_in_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  {filename}: Not found")
    
    print(f"\n✅ Fixed {fixed_count} files!")

if __name__ == "__main__":
    main()
