"""Script to convert test_training_mode.py from return True/False to assert style."""

import re

# Read the file
with open('tests/sprints/sprint22/test_training_mode.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern replacements
replacements = [
    # Convert print-then-return-False to assert with message
    (r'    if ([^:]+):\n        print\("❌ FAIL: ([^"]+)"\)\n        return False',
     r'    assert not (\1), "\2"'),
    
    (r'    if not ([^:]+):\n        print\("❌ FAIL: ([^"]+)"\)\n        return False',
     r'    assert \1, "\2"'),
    
    # Remove standalone return True
    (r'    return True\n', ''),
    
    # Remove print statements with ✅ PASS
    (r'    print\("✅ PASS: [^"]+"\)\n', ''),
    (r'    print\("✅ [^"]+"\)\n', ''),
    
    # Remove TEST header prints
    (r'    print\("\\n" \+ "="\*60\)\n    print\("TEST \d+: [^"]+"\)\n    print\("="\*60\)\n', ''),
    
    # Remove test summary prints but keep data prints
    (r'    print\(f?"✅ [^"]+"\)\n', ''),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Remove empty lines (more than 2 consecutive)
content = re.sub(r'\n\n\n+', '\n\n', content)

# Write back
with open('tests/sprints/sprint22/test_training_mode.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Converted test_training_mode.py to assert-based tests")
