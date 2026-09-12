import re

with open('lib/features/hunt/hunt_runner.py', 'r') as f:
    content = f.read()

# I will fix the """ issue left in the code
content = content.replace('return None, 0, """', '')

with open('lib/features/hunt/hunt_runner.py', 'w') as f:
    f.write(content)
