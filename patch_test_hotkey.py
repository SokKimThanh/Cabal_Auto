import re

with open("tests/unit/ui/controllers/test_hotkey_controller.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("assert mock_keyboard.add_hotkey.call_count == 6", "assert mock_keyboard.add_hotkey.call_count == 5")
content = content.replace("mock_keyboard.remove_hotkey.call_count == 6", "mock_keyboard.remove_hotkey.call_count == 5")
content = content.replace("# 6 hotkeys registered by default", "# 5 hotkeys registered by default")

with open("tests/unit/ui/controllers/test_hotkey_controller.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched test_hotkey_controller.py")
