import re

with open("ui/tabs/hunt_tab.py", "r") as f:
    content = f.read()

# Look for variable assignments
vars_found = set(re.findall(r'self\.(?:app\.)?([a-zA-Z0-9_]+)\s*=', content))
print("Variables assigned to self or self.app:")
for v in sorted(list(vars_found)):
    print(v)
