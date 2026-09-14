# Review Prompt 015: Clean Imports and Move Fallback Component

## Verification Steps
1. Open `app_gui.py` and inspect the top of the file. Ensure that blocks like `try: pass except Exception: keyboard = None` have been completely removed or replaced with proper import attempts (e.g., `try: import keyboard except ImportError: keyboard = None`).
2. Verify that `_create_icon_btn_component` is no longer defined inside `app_gui.py`.
3. Check `lib/ui/helpers/fallback_components.py` to ensure the function was moved there and is imported correctly into `app_gui.py`.
4. Run the application to ensure it boots without import errors or UI crashes related to icons.

## Checklist
- [ ] No useless `try: pass` blocks in `app_gui.py`.
- [ ] Fallback function extracted to `lib/ui/helpers/fallback_components.py`.
- [ ] Application starts successfully.
