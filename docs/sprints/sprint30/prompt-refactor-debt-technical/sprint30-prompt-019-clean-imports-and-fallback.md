# Prompt 019: Clean Imports and Move Fallback Component

## Objective
Remove useless `try: pass except Exception:` blocks from `app_gui.py` and move the large fallback function `_create_icon_btn_component` to a dedicated helper file to reduce surface-level clutter in the God Class.

## Tasks
1. **Clean up useless try-except blocks in `app_gui.py`:**
   - Find and remove blocks like `try: pass except Exception: keyboard = None` and `try: pass except ImportError: ScreenCapture = None`.
   - Ensure imports like `import keyboard` or `import pyautogui` are properly handled if they need a `try/except` block, but without a useless `pass`.
2. **Extract Fallback Function:**
   - Create a new file `lib/ui/helpers/fallback_components.py` (ensure `lib/ui/helpers/__init__.py` exists).
   - Move the definition of `_create_icon_btn_component` (lines 83-147 in `app_gui.py`) into this new file.
   - In `app_gui.py`, import this fallback function instead of defining it inline when `_HAS_ICON_COMPONENT` is False.
3. **Verify:**
   - Ensure `app_gui.py` starts without syntax errors.
   - Ensure icon buttons still fallback correctly if the primary component is missing.
