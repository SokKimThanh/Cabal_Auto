1. **Update ID generation in `_get_default_monster`:** Modify `str(uuid.uuid4())` to `str(uuid.uuid4())[:8]` in `dialogs/monster_edit.py` to generate short IDs.
2. **Change ID Label Display in `dialogs/monster_edit.py`:** Update `_populate_form` so it always formats the ID label using `f"#{m_id}"`, even for new monsters (since they auto-generate a UUID), instead of showing "<Mới / New>". Update `_on_reset_form` and `_on_clear_form` to set the ID label text to the newly generated ID or "" instead of "<Mới / New>".
3. **Add "Generate ID" Button in `dialogs/monster_edit.py`:**
   - Modify `_setup_ui` (around line 387) to create a `tk.Frame` for the ID field, holding the label and a new "Generate ID" button.
   - The button should only be added or displayed for new monsters.
   - Add a method `_on_generate_id` to generate a short ID, update `self.monster_data["id"]`, and update the UI label.
4. **Run Tests:** Explicitly run the test suite (e.g., `xvfb-run -a pytest tests/focused/test_monster_editor_id.py`) to verify the changes.
5. **Complete pre-commit steps:** Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.
6. **Submit the changes:** Submit the git branch.
