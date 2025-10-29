"""Script to convert route functions to async"""
import re

def convert_file_to_async(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match function definitions that are NOT helper functions
    # We want to convert @router decorated functions
    pattern = r'(@router\.[a-z]+\([^)]+\)[^\n]*\n(?:@[^\n]+\n)*)def ([a-z_]+)\('
    
    def replace_with_async(match):
        decorators = match.group(1)
        func_name = match.group(2)
        # Skip helper functions (they don't have @router decorator)
        return f'{decorators}async def {func_name}('
    
    new_content = re.sub(pattern, replace_with_async, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Converted {filepath}")

# Convert both files
convert_file_to_async('C:/Users/armut/Documents/GitHub/1.1/backend/app/routes/inventory.py')
convert_file_to_async('C:/Users/armut/Documents/GitHub/1.1/backend/app/routes/patient_portal.py')

print("\n✅ All route functions converted to async!")
