"""
Fix invalid role checks in route files.
Changes 'doctor' and 'pharmacist' to 'staff' in role validation checks.
"""
import re
from pathlib import Path

def fix_role_checks():
    """Fix role checks in route files"""
    route_files = [
        Path("app/routes/prescriptions.py"),
        Path("app/routes/inventory.py"),
        Path("app/routes/patient_portal.py")
    ]
    
    total_fixed = 0
    
    print("🔧 Fixing role checks in route files...")
    print("Changes:")
    print('  if current_user.role not in ["doctor", ...] → if current_user.role not in ["staff", ...]')
    print('  if current_user.role == "pharmacist" → if current_user.role == "staff"')
    print('  "Only doctors can..." → "Only staff/admins can..."')
    print()
    
    for file_path in route_files:
        if not file_path.exists():
            print(f"⚠️  {file_path}: File not found, skipping")
            continue
            
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        changes = 0
        
        # Fix role checks: "doctor" → "staff"
        content, n = re.subn(
            r'(current_user\.role\s+(?:not\s+)?in\s+\[)"doctor"',
            r'\1"staff"',
            content
        )
        changes += n
        
        # Fix role equality: role == "doctor" → role == "staff"
        content, n = re.subn(
            r'(current_user\.role\s+==\s+)"doctor"',
            r'\1"staff"',
            content
        )
        changes += n
        
        # Fix role equality: role == "pharmacist" → role == "staff"
        content, n = re.subn(
            r'(current_user\.role\s+==\s+)"pharmacist"',
            r'\1"staff"',
            content
        )
        changes += n
        
        # Fix error messages
        content, n = re.subn(
            r'"Only doctors can',
            '"Only staff/admins can',
            content
        )
        changes += n
        
        content, n = re.subn(
            r'"Only pharmacists can',
            '"Only staff/admins can',
            content
        )
        changes += n
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ {file_path.name}: Fixed {changes} role checks")
            total_fixed += 1
        else:
            print(f"ℹ️  {file_path.name}: No changes needed")
    
    print()
    if total_fixed > 0:
        print(f"✅ Fixed {total_fixed} files!")
    else:
        print("ℹ️  No files needed fixing")

if __name__ == "__main__":
    fix_role_checks()
