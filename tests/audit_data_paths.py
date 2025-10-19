"""Audit all data path references in the project."""
import sys
from pathlib import Path
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("DATA PATH AUDIT - Finding all config/data file references")
print("=" * 80)

# Files to check
files_to_check = [
    'app_gui.py',
    'ui/setup_wizard.py',
    'ui/auto_hunt.py',
    'lib/ui/library_manager.py',
    'scripts/main.py',
    'scripts/main_skills.py',
]

results = {
    'correct': [],  # Points to lib/data
    'incorrect': [], # Points to root/data or other
    'unclear': []   # Can't determine
}

def analyze_path_line(filepath: str, line_num: int, line: str):
    """Analyze a line containing path references."""
    # Patterns to look for
    patterns = [
        (r"Path\(__file__\)\.parent\s*/\s*'data'", 'WRONG: root/data'),
        (r"Path\(__file__\)\.parent\.parent\s*/\s*'data'", 'CHECK: Depends on file location'),
        (r"'data'\s*/\s*'[^']+\.json'", 'AMBIGUOUS: Relative data path'),
        (r"lib/data", 'CORRECT: lib/data'),
        (r"'lib'\s*/\s*'data'", 'CORRECT: lib/data'),
    ]
    
    for pattern, status in patterns:
        if re.search(pattern, line):
            return status
    
    return None

print("\n[Scanning Files]\n")

for filepath in files_to_check:
    full_path = Path(__file__).parent / filepath
    
    if not full_path.exists():
        print(f"⚠️  SKIP: {filepath} (not found)")
        continue
    
    print(f"📄 Checking: {filepath}")
    
    with open(full_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found_refs = []
    for i, line in enumerate(lines, 1):
        # Look for data path references
        if 'data' in line.lower() and ('.json' in line or 'Path(' in line or 'data/' in line):
            analysis = analyze_path_line(filepath, i, line.strip())
            if analysis:
                found_refs.append({
                    'line': i,
                    'code': line.strip(),
                    'analysis': analysis
                })
    
    if found_refs:
        for ref in found_refs:
            status_marker = "✅" if "CORRECT" in ref['analysis'] else "❌" if "WRONG" in ref['analysis'] else "⚠️"
            print(f"  {status_marker} Line {ref['line']:4d}: {ref['analysis']}")
            print(f"     {ref['code'][:100]}")
            
            if "CORRECT" in ref['analysis']:
                results['correct'].append((filepath, ref['line']))
            elif "WRONG" in ref['analysis']:
                results['incorrect'].append((filepath, ref['line']))
            else:
                results['unclear'].append((filepath, ref['line']))
    else:
        print("  ✓ No data path references found")
    
    print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"\n✅ CORRECT (lib/data): {len(results['correct'])} references")
for filepath, line in results['correct']:
    print(f"   - {filepath}:{line}")

print(f"\n❌ INCORRECT (root/data or other): {len(results['incorrect'])} references")
for filepath, line in results['incorrect']:
    print(f"   - {filepath}:{line}")

print(f"\n⚠️  UNCLEAR (needs manual check): {len(results['unclear'])} references")
for filepath, line in results['unclear']:
    print(f"   - {filepath}:{line}")

# Physical check
print("\n" + "=" * 80)
print("PHYSICAL DIRECTORY CHECK")
print("=" * 80)

root = Path(__file__).parent
lib_data = root / 'lib' / 'data'
root_data = root / 'data'

print(f"\n📁 lib/data: {lib_data}")
print(f"   Exists: {lib_data.exists()}")
if lib_data.exists():
    files = list(lib_data.glob('*.json'))
    print(f"   JSON files: {len(files)}")
    for f in files:
        print(f"     - {f.name}")

print(f"\n📁 root/data: {root_data}")
print(f"   Exists: {root_data.exists()}")
if root_data.exists():
    files = list(root_data.glob('*.json'))
    print(f"   JSON files: {len(files)}")
    for f in files:
        print(f"     - {f.name}")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print("\n📌 All data files should be in: lib/data/")
print("📌 Update all incorrect paths to point to lib/data")
print("📌 Centralized data location improves maintainability")
print("=" * 80)
