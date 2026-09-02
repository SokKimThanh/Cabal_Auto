1. **Run Black and Flake8**: Run formatting and linting tools on the specified files (`app_gui.py`, `ui/tabs/hunt_tab.py`, `lib/system/hunt_logger.py`, `lib/ui_style.py`) and ensure they pass. I have already run `black` and it reformatted files, so I need to commit these formatting changes.
2. **Review Geometry ACs (1366x768 at 100%)**:
   - Verify `tests/ui/test_hunt_bottom_logs.py::test_hunt_tab_geometry_with_collapsed_logs` passes and meets AC-1, AC-4, AC-18. (It passes).
   - Create a test for AC-F1, AC-F2, AC-F3 to verify the footer elements (`global_apply_btn` and `_db_status_bar`) are visible, and mapped properly, and bottom chrome does not overlap the `main_shell`. I already created `tests/ui/test_footer_visibility.py` and modified `app_gui.py` to fix a layout regression where `main_shell` was expanding to push footer elements off-screen.
   - Run tests for `test_bottom_logs.py` to verify AC-7, AC-8, AC-12, AC-13, AC-15, AC-16 (logs auto-collapse, buffer limits).
3. **Execute test matrix**:
   - Given the headless test environment, I can simulate DPI by modifying the scale factor calculation in the app, or manually setting `tk scaling`.
   - I will run a script simulating 100%, 125%, and 150% DPI by calling `app.tk.call('tk', 'scaling', DPI_FACTOR * 72 / 72)` and test both languages (`en`, `vi`).
4. **Complete pre-commit checks**: Run `pre_commit_instructions` to ensure code is verified.
5. **Generate AC Report**: I will output a table mapping AC-1 to AC-19 and AC-F1 to AC-F3 with Pass/Fail results, plus the DPI/Language matrix.
