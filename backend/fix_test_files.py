"""
Script to fix test files to match the actual User model.

Changes:
1. full_name -> name
2. phone_number -> phone
3. Add set_password replacement with password_hash
4. Add date_of_birth field
"""

import re
from pathlib import Path

def fix_test_file(file_path):
    """Fix a single test file."""
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count replacements
    replacements = 0
    
    # Replace full_name with name
    new_content, count = re.subn(r'\bfull_name\b', 'name', content)
    replacements += count
    
    # Replace phone_number with phone
    new_content, count = re.subn(r'\bphone_number\b', 'phone', new_content)
    replacements += count
    
    # Replace set_password method calls with direct password_hash assignment
    # Pattern: user.set_password("password")
    def replace_set_password(match):
        var_name = match.group(1)
        password = match.group(2)
        return f'{var_name}.password_hash = get_password_hash({password})'
    
    new_content, count = re.subn(
        r'(\w+)\.set_password\(([^)]+)\)',
        replace_set_password,
        new_content
    )
    replacements += count
    
    # Add import for get_password_hash if set_password was replaced
    if count > 0 and 'from app.services.auth_service import get_password_hash' not in new_content:
        # Find the imports section and add the import
        import_pattern = r'(from app\.database import get_db)'
        new_content = re.sub(
            import_pattern,
            r'\1\nfrom app.services.auth_service import get_password_hash',
            new_content
        )
    
    # Add date_of_birth to User creation
    # Find User( ... ) patterns and add date_of_birth if not present
    def add_date_of_birth(match):
        user_block = match.group(0)
        if 'date_of_birth' not in user_block:
            # Add date_of_birth before the closing parenthesis
            user_block = user_block.rstrip('\n )')
            user_block += ',\n        date_of_birth=datetime(1990, 1, 1)\n    )'
        return user_block
    
    # This pattern matches User( ... ) blocks
    new_content = re.sub(
        r'User\([^)]*?\)',
        add_date_of_birth,
        new_content,
        flags=re.DOTALL
    )
    
    # Add datetime import if date_of_birth was added
    if 'datetime' in new_content and 'from datetime import datetime' not in new_content:
        # Check if there's already a datetime import
        if 'import datetime' in new_content:
            # Replace module import with specific import
            new_content = re.sub(
                r'import datetime\b',
                'from datetime import datetime, timedelta',
                new_content
            )
        else:
            # Add new import at the top
            new_content = 'from datetime import datetime, timedelta\n' + new_content
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ Made {replacements} replacements")
    return replacements

def main():
    """Fix all test files."""
    test_dir = Path(__file__).parent / 'tests'
    test_files = [
        test_dir / 'test_prescriptions.py',
        test_dir / 'test_inventory.py',
        test_dir / 'test_patient_portal.py'
    ]
    
    total_replacements = 0
    for test_file in test_files:
        if test_file.exists():
            replacements = fix_test_file(test_file)
            total_replacements += replacements
        else:
            print(f"⚠️  File not found: {test_file}")
    
    print(f"\n✅ Total replacements: {total_replacements}")
    print("🎉 All test files fixed!")

if __name__ == "__main__":
    main()
