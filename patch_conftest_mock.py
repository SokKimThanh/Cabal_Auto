import re
with open('conftest.py', 'r') as f:
    content = f.read()

# Make sure we add a proper mock for win32 to sys.modules BEFORE any app code imports it
content = re.sub(r'import pytest\nimport os\nimport sys\nfrom unittest.mock import MagicMock\n',
'''import pytest
import os
import sys
from unittest.mock import MagicMock

# Inject win32 mocks so headless tests can import them without modifying production code
if sys.platform != "win32":
    for mod in ["win32gui", "win32ui", "win32con", "win32api", "win32process", "ctypes"]:
        sys.modules[mod] = MagicMock()
''', content)

with open('conftest.py', 'w') as f:
    f.write(content)
