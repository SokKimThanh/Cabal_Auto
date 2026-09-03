#!/usr/bin/env python3
"""
Analyze mock/patch usage patterns in the test suite.
"""
import os
import re
from collections import defaultdict

stats = defaultdict(lambda: {
    'sys_modules': 0,
    'decorator_patches': 0,
    'with_patches': 0,
    'magic_mocks': 0,
    'mocks': 0,
    'monkeypatch': 0
})

for root, dirs, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            stats[filepath]['sys_modules'] = len(re.findall(r'sys\.modules\[.*?\]\s*=\s*(Mock|MagicMock)', content))
            stats[filepath]['decorator_patches'] = len(re.findall(r'@patch\(', content))
            stats[filepath]['with_patches'] = len(re.findall(r'with patch\(', content))
            stats[filepath]['magic_mocks'] = len(re.findall(r'MagicMock\(\)', content))
            stats[filepath]['mocks'] = len(re.findall(r'Mock\(', content))
            stats[filepath]['monkeypatch'] = len(re.findall(r'monkeypatch', content))

# Calculate totals
sorted_stats = sorted(stats.items(), key=lambda x: sum(x[1].values()), reverse=True)

print('=== Top 20 Files with Most Mock/Patch Usage ===')
print(f"{'File':<60} {'Total':>6}")
print('-' * 70)
for file, counts in sorted_stats[:20]:
    total = sum(counts.values())
    rel_path = file.replace('f:\\Cabal_Auto\\', '')
    print(f'{rel_path:<60} {total:>6}')

total_mocks = sum(sum(v.values()) for v in stats.values())
files_using_mocks = len([s for s in stats.values() if sum(s.values()) > 0])
print(f'\n=== Summary Statistics ===')
print(f'Total Mock/Patch Instances: {total_mocks}')
print(f'Files Using Mocks/Patches: {files_using_mocks}')
if files_using_mocks > 0:
    avg = total_mocks / files_using_mocks
    print(f'Average per File: {avg:.2f}')

print(f'\n=== Breakdown by Type ===')
print(f"Total sys.modules patches: {sum(s['sys_modules'] for s in stats.values())}")
print(f"Total @patch decorators: {sum(s['decorator_patches'] for s in stats.values())}")
print(f"Total with patch() statements: {sum(s['with_patches'] for s in stats.values())}")
print(f"Total MagicMock() instances: {sum(s['magic_mocks'] for s in stats.values())}")
print(f"Total Mock() instances: {sum(s['mocks'] for s in stats.values())}")
print(f"Total monkeypatch usages: {sum(s['monkeypatch'] for s in stats.values())}")
