with open("tests/integration/test_orchestrator_loop.py", "r") as f:
    content = f.read()

import_sys_mock = """import sys
import pytest
import time
from unittest.mock import MagicMock, patch

# Mock out window_manager and other windows specifics before import
sys.modules['lib.system.window_manager'] = MagicMock()
sys.modules['lib.features.hunt.window_selection_service'] = MagicMock()
"""

content = content.replace("import pytest\nimport time\nfrom unittest.mock import MagicMock, patch", import_sys_mock)

# Also fix the monkeypatch target for validate_selected_cabal_window
# Since it's dynamically imported in the loop, we mock it via a patch context manager or module patching

with open("tests/integration/test_orchestrator_loop.py", "w") as f:
    f.write(content)
