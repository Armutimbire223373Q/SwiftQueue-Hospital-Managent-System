import re

# Read the file
with open('backend/app/routes/staff.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match and fix parameter order
# Matches:     current_user: User = Depends(get_current_active_user),
#              db: Session = Depends(get_db)
pattern = r'(\s+)current_user: User = Depends\(get_current_active_user\),\s*\n(\s+)db: Session = Depends\(get_db\)'
replacement = r'\1db: Session = Depends(get_db),\n\2current_user: User = Depends(get_current_active_user)'

# Apply the fix
fixed_content = re.sub(pattern, replacement, content)

# Write back
with open('backend/app/routes/staff.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

# Count how many replacements were made
count = len(re.findall(pattern, content))
print(f"✅ Fixed {count} parameter order issues in staff.py")
