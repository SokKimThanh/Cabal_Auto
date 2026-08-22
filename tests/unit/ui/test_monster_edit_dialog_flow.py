"""
Unit tests for MonsterEditDialog refactoring, Singleton behavior, header gear button removal,
tab renaming, title formatting, and duplicate name confirmation flow.
"""

import json
import tkinter as tk
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestMonsterEditDialogFlow:
    """Test suite for MonsterEditDialog and QuickMonsterEditor UI refactorings."""

    @pytest.fixture
    def temp_data_file(self, tmp_path: Path) -> Path:
        data_file = tmp_path / "monsters.json"
        data_file.write_text(json.dumps([
            {'id': 'm1', 'name': 'Quái Đen', 'level': 10, 'hp': 100, 'damage_per_hit': 5, 'templates': []},
            {'id': 'm2', 'name': 'Quái Đỏ', 'level': 20, 'hp': 200, 'damage_per_hit': 10, 'templates': []}
        ]), encoding='utf-8')
        return data_file

    def test_header_settings_button_removed(self, temp_data_file: Path) -> None:
        """Test that header gear settings button is removed (None)."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
                return

            root.withdraw()
            try:
                editor = QuickMonsterEditor(root)
                assert editor.settings_button is None, "Header gear settings button should be removed"
            finally:
                editor.destroy()
                root.destroy()

    def test_edit_dialog_title_format_and_tab_name(self, temp_data_file: Path) -> None:
        """Test MonsterEditDialog title contains ID and tab 3 is renamed to 'Hiển thị'."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor, MonsterEditDialog
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
                return

            root.withdraw()
            try:
                editor = QuickMonsterEditor(root)
                dialog = MonsterEditDialog(editor, monster={'id': 'm1', 'name': 'Quái Đen'})

                title = dialog.title()
                assert "Sửa Quái Vật: Quái Đen (ID: #m1)" in title

                # Verify tab 3 text
                tab_text = dialog.notebook.tab(dialog.settings_tab, "text")
                assert tab_text == "Hiển thị"

                dialog.destroy()
            finally:
                editor.destroy()
                root.destroy()

    def test_singleton_edit_dialog_enforcement(self, temp_data_file: Path) -> None:
        """Test that opening MonsterEditDialog twice lifts existing dialog instead of creating new."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
                return

            root.withdraw()
            try:
                editor = QuickMonsterEditor(root)

                dialog1 = editor._open_edit_dialog('m1')
                assert dialog1 is not None

                # Attempt to open dialog again
                with patch.object(dialog1, 'lift') as mock_lift:
                    dialog2 = editor._open_edit_dialog('m2')
                    assert dialog2 is dialog1, "Should return existing dialog instance"
                    assert mock_lift.called, "Should call lift() on existing dialog"

                dialog1.destroy()
                root.update_idletasks()

                # After destroying, opening dialog creates new instance
                dialog3 = editor._open_edit_dialog('m2')
                assert dialog3 is not None
                assert dialog3 is not dialog1
                dialog3.destroy()
            finally:
                editor.destroy()
                root.destroy()

    def test_duplicate_name_check_accepted(self, temp_data_file: Path) -> None:
        """Test duplicate name prompt on save: user accepts auto rename."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor, MonsterEditDialog
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
                return

            root.withdraw()
            try:
                editor = QuickMonsterEditor(root)
                # Create edit dialog for a new monster with name 'Quái Đen' (duplicate of m1)
                saved_data = []
                def on_save(data):
                    saved_data.append(data)

                dialog = MonsterEditDialog(editor, monster=None, on_save=on_save)
                dialog.name_entry.delete(0, tk.END)
                dialog.name_entry.insert(0, 'Quái Đen')

                with patch('tkinter.messagebox.askyesno', return_value=True) as mock_ask:
                    dialog._on_save()
                    assert mock_ask.called
                    assert len(saved_data) == 1
                    assert saved_data[0]['name'] == 'Quái Đen (1)'

            finally:
                editor.destroy()
                root.destroy()

    def test_duplicate_name_check_rejected(self, temp_data_file: Path) -> None:
        """Test duplicate name prompt on save: user rejects auto rename (dialog stays open)."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor, MonsterEditDialog
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
                return

            root.withdraw()
            try:
                editor = QuickMonsterEditor(root)
                saved_data = []
                def on_save(data):
                    saved_data.append(data)

                dialog = MonsterEditDialog(editor, monster=None, on_save=on_save)
                dialog.name_entry.delete(0, tk.END)
                dialog.name_entry.insert(0, 'Quái Đen')

                with patch('tkinter.messagebox.askyesno', return_value=False) as mock_ask:
                    dialog._on_save()
                    assert mock_ask.called
                    assert len(saved_data) == 0, "Should not save when user rejects auto rename"
                    assert dialog.winfo_exists(), "Dialog should stay open"

                dialog.destroy()
            finally:
                editor.destroy()
                root.destroy()

    def test_search_entry_escape_clears_text(self, temp_data_file: Path) -> None:
        """Test that pressing Escape in search_entry clears search and refreshes table."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter unavailable: {e}")
                return

            root.withdraw()
            try:
                editor = QuickMonsterEditor(root)
                editor.search_entry.insert(0, 'Quái Đen')
                assert editor.search_entry.get() == 'Quái Đen'

                editor._on_clear_search()
                assert editor.search_entry.get() == ''
            finally:
                editor.destroy()
                root.destroy()
