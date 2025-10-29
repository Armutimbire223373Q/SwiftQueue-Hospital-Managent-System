#!/usr/bin/env python3
"""
Fix medication data in tests to match API schema.
API expects: duration (str), quantity (int)
Tests currently have: duration_days (int), missing quantity
"""

import re
from pathlib import Path

def fix_medication_data(file_path):
    """Fix medication objects in test file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace "duration_days": 30 with "duration": "30 days", "quantity": 30
    # Pattern: find medication dictionaries
    # Look for: "duration_days": <number>
    # Replace with: "duration": "<number> days",\n                "quantity": <number>
    
    def fix_medication_dict(match):
        days = match.group(1)
        indent = match.group(2) if match.lastindex >= 2 else "                "
        return f'"duration": "{days} days",\n{indent}"quantity": {days}'
    
    # Pattern: "duration_days": 30 (with optional trailing comma)
    content = re.sub(
        r'"duration_days":\s*(\d+),?(\s*)',
        fix_medication_dict,
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name}: Fixed medication data")
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
    
    print("🔧 Fixing medication data in test files...\n")
    print("Changes:")
    print('  duration_days: 30  →  duration: "30 days", quantity: 30\n')
    
    fixed_count = 0
    for filename in test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            if fix_medication_data(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  {filename}: Not found")
    
    print(f"\n✅ Fixed {fixed_count} files!")

if __name__ == "__main__":
    main()
