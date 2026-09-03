import re
with open('conftest.py', 'r') as f:
    content = f.read()

# Fix duplication of createcommand/deletecommand
content = re.sub(r'        def createcommand\(self, \*args, \*\*kwargs\):\n            return None\n        def deletecommand\(self, \*args, \*\*kwargs\):\n            return None\n        def createcommand\(self, \*args, \*\*kwargs\):\n            return None\n        def deletecommand\(self, \*args, \*\*kwargs\):\n            return None',
'''        def createcommand(self, *args, **kwargs):
            return None
        def deletecommand(self, *args, **kwargs):
            return None''', content)

with open('conftest.py', 'w') as f:
    f.write(content)
