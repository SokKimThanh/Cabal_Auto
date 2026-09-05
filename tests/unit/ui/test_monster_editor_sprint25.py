import pytest
pytest.importorskip("tkinter", reason="Skipping UI imports because tkinter is not available in headless environment")

import tkinter as tk
from unittest.mock import patch
import json
from pathlib import Path
from lib.i18n.monster_editor_translations import MONSTER_EDITOR_TRANSLATIONS

import os
pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)

def test_new_monster_generates_id():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()
    try:
        dialog = MonsterEditDialog(root)
        data = dialog._collect_form_data()
        assert "id" in data
        assert len(data["id"]) > 0
        assert data["id"] != ""
        # The ID should also be displayed
        assert dialog.id_val_label.cget("text").startswith("#")
        assert len(dialog.id_val_label.cget("text")) > 1
    finally:
        root.destroy()

def test_edit_monster_preserves_id():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()
    try:
        existing_monster = {"id": "test-uuid-1234", "name": "Existing"}
        dialog = MonsterEditDialog(root, monster=existing_monster)
        data = dialog._collect_form_data()
        assert data["id"] == "test-uuid-1234"
        assert dialog.id_val_label.cget("text") == "#test-uuid-1234"
    finally:
        root.destroy()

def test_full_db_field_emission():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()

    saved_data = None
    def mock_save(data):
        nonlocal saved_data
        saved_data = data

    try:
        dialog = MonsterEditDialog(root, on_save=mock_save)

        # Populate DB fields
        dialog.name_entry.insert(0, "FullDBMonster")
        dialog.level_spinbox.delete(0, tk.END)
        dialog.level_spinbox.insert(0, "15")

        dialog.hp_entry.delete(0, tk.END)
        dialog.hp_entry.insert(0, "1000")

        dialog.primary_atk_min_entry.delete(0, tk.END)
        dialog.primary_atk_min_entry.insert(0, "10")
        dialog.primary_atk_max_entry.delete(0, tk.END)
        dialog.primary_atk_max_entry.insert(0, "20")

        # Simulate null value reference
        dialog.dungeon_combo.set("<Không / None>")

        with patch('tkinter.messagebox.askyesno', return_value=True):
            dialog._on_save()

        assert saved_data is not None
        # Assert full emission
        assert saved_data["level"] == 15
        assert saved_data["hp"] == 1000
        assert saved_data["primaryAttackMin"] == 10
        assert saved_data["primaryAttackMax"] == 20
        assert saved_data["dungeonId"] is None

    finally:
        root.destroy()

def test_persistence_success_failure_retention(tmp_path):
    from ui.windows.monster_manager_win import MonsterManagerWin

    temp_file = tmp_path / "monsters.json"
    temp_file.write_text('[]', encoding='utf-8')

    root = tk.Tk()
    root.withdraw()

    try:
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_file), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            editor = MonsterManagerWin(root)

            # Setup db mock that fails on 'm2' but succeeds on 'm1'
            class MockDB:
                def insert_or_update_monster(self, m):
                    if m["id"] == "m2":
                        return False
                    return True
            editor.db = MockDB()
            editor.sync_manager = None

            # Create pending changes
            editor.pending_changes = {
                "m1": {"id": "m1", "name": "Success Monster"},
                "m2": {"id": "m2", "name": "Failed Monster"}
            }

            with patch.object(editor, '_show_status_message'):
                result = editor._save_monsters()

            assert result is False
            # m1 succeeded and removed, m2 failed and kept
            assert "m1" not in editor.pending_changes
            assert "m2" in editor.pending_changes
    finally:
        root.destroy()

def test_nullable_references():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()

    try:
        dialog = MonsterEditDialog(root)
        dialog.dungeon_combo.set("<Không / None>")
        dialog.boss_type_combo.set("<Không / None>")

        data = dialog._collect_form_data()
        assert data["dungeonId"] is None
        assert data["serverBossType"] is None
    finally:
        root.destroy()

def test_min_max_validation():
    from dialogs.monster_edit import MonsterEditDialog
    root = tk.Tk()
    root.withdraw()

    try:
        dialog = MonsterEditDialog(root)

        dialog.name_entry.insert(0, "InvalidMonster")

        dialog.primary_atk_min_entry.delete(0, tk.END)
        dialog.primary_atk_min_entry.insert(0, "50")
        dialog.primary_atk_max_entry.delete(0, tk.END)
        dialog.primary_atk_max_entry.insert(0, "10") # min > max

        with patch('tkinter.messagebox.showerror') as mock_err:
            dialog._on_save()
            mock_err.assert_called()
            call_args = mock_err.call_args[0]
            assert "Tối đa" in call_args[1] or "Max" in call_args[1]
    finally:
        root.destroy()

def test_language_labels():
    assert "error_min_max" in MONSTER_EDITOR_TRANSLATIONS["vi"]
    assert "error_min_max" in MONSTER_EDITOR_TRANSLATIONS["en"]
    assert "error_negative" in MONSTER_EDITOR_TRANSLATIONS["vi"]
    assert "error_negative" in MONSTER_EDITOR_TRANSLATIONS["en"]
