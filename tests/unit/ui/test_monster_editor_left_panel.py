import pytest
pytest.importorskip("tkinter", reason="Skipping UI imports because tkinter is not available in headless environment")

"""
Unit Tests for Monster Editor Left Panel (Batch 4).

Tests cover:
- Monster list display and refresh
- Monster selection handling
- Add monster functionality
- Delete monster functionality with confirmation
- Listbox updates and state management

Author: SokKimThanh
Created: 2025-10-24
"""
import tkinter as tk
from pathlib import Path
from typing import Any
from unittest.mock import patch, MagicMock
import json


import os
pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)
class TestMonsterEditorLeftPanel:
    """Test suite for Monster Editor left panel functionality."""
    
    @pytest.fixture
    def temp_data_file(self, tmp_path: Path):
        """
        Create temporary monsters.json file safely for Windows.
        """
        temp_file = tmp_path / "monsters.json"
        temp_file.write_text('[]', encoding='utf-8')
        yield temp_file

        try:
            if temp_file.exists():
                temp_file.unlink()
        except (PermissionError, OSError):
            import time
            time.sleep(0.05)
            try:
                temp_file.unlink()
            except Exception:
                pass
    
    @pytest.fixture
    def sample_monsters(self) -> list:
        """Sample monster data for testing."""
        return [
            {
                'id': 'test-id-1',
                'name': 'Goblin',
                'level': 5,
                'priority': 1,
                'hp': 100,
                'damage_per_hit': 10,
                'templates': []
            },
            {
                'id': 'test-id-2',
                'name': 'Orc',
                'level': 10,
                'priority': 2,
                'hp': 200,
                'damage_per_hit': 20,
                'templates': []
            }
        ]
    
    def test_left_panel_creation(self, temp_data_file: Path) -> None:
        """Test that left panel widgets are created correctly."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin

            root = tk.Tk()
            root.withdraw()
            editor = None

            try:
                editor = MonsterManagerWin(root)

                # Verify left panel widgets exist
                assert editor.monster_listbox is not None
                assert editor.add_monster_button is not None
                assert editor.delete_monster_button is not None

            finally:
                if editor:
                    editor.destroy()
                root.destroy()

    def test_refresh_monster_list(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test that monster list refreshes correctly."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None), \
             patch('tkinter.messagebox.askyesno', return_value=True):
            from ui.windows.monster_manager_win import MonsterManagerWin

            root = tk.Tk()
            root.withdraw()
            editor = None

            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Verify listbox contains monsters
                assert editor.monster_listbox.size() == 2

                # Verify display format
                item1 = editor.monster_listbox.get(0)
                assert 'Goblin' in item1
                assert 'Lv.5' in item1

                item2 = editor.monster_listbox.get(1)
                assert 'Orc' in item2
                assert 'Lv.10' in item2

            finally:
                if editor:
                    editor.destroy()
                root.destroy()

    def test_monster_selection(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test monster selection from listbox."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Select first monster
                editor.monster_listbox.selection_set(0)
                editor.monster_listbox.event_generate('<<ListboxSelect>>')
                root.update_idletasks()

                # Verify current_monster_id is set
                assert editor.current_monster_id == 'test-id-1'

                # Select second monster
                editor.monster_listbox.selection_clear(0)
                editor.monster_listbox.selection_set(1)
                editor.monster_listbox.event_generate('<<ListboxSelect>>')
                root.update_idletasks()

                # Verify current_monster_id is updated
                assert editor.current_monster_id == 'test-id-2'

            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_add_monster(self, temp_data_file: Path) -> None:
        """Test adding a new monster."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Initially empty
                assert len(editor.monsters) == 0
                assert editor.monster_listbox.size() == 0

                # Add monster via dialog
                dialog = editor._open_edit_dialog(None)
                assert dialog is not None
                dialog._on_save()
                root.update_idletasks()

                # Verify monster added
                assert len(editor.monsters) == 1
                assert editor.monster_listbox.size() == 1

                # Verify new monster has required fields
                new_monster = editor.monsters[0]
                assert 'id' in new_monster
                assert 'name' in new_monster
                assert 'level' in new_monster
                assert new_monster['level'] == 1
                assert new_monster['priority'] == 1

                # Verify dirty flag
                assert editor.is_dirty is True

            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_delete_monster_with_confirmation(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test deleting a monster with confirmation."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Select first monster
                editor.monster_listbox.selection_set(0)
                editor.current_monster_id = 'test-id-1'

                # Mock messagebox.askyesno to return True (confirm)
                with patch('tkinter.messagebox.askyesno', return_value=True):
                    editor._on_delete_monster()
                    root.update_idletasks()

                # Verify monster deleted
                assert len(editor.monsters) == 1
                assert editor.monster_listbox.size() == 1
                assert editor.monsters[0]['name'] == 'Orc'

                # Verify dirty flag
                assert editor.is_dirty is True

                # Verify current_monster_id cleared
                assert editor.current_monster_id is None

            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_delete_monster_cancelled(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test cancelling monster deletion."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Select first monster
                editor.monster_listbox.selection_set(0)
                editor.current_monster_id = 'test-id-1'

                # Mock messagebox.askyesno to return False (cancel)
                with patch('tkinter.messagebox.askyesno', return_value=False):
                    editor._on_delete_monster()
                    root.update_idletasks()

                # Verify monster NOT deleted
                assert len(editor.monsters) == 2
                assert editor.monster_listbox.size() == 2

                # Verify dirty flag not set
                assert editor.is_dirty is False

            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_delete_monster_no_selection(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test deleting monster with no selection shows warning."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Clear selection
                editor.monster_listbox.selection_clear(0, tk.END)

                # Mock messagebox.showwarning
                with patch('tkinter.messagebox.showwarning') as mock_warning:
                    editor._on_delete_monster()
                    root.update_idletasks()

                    # Verify warning shown
                    mock_warning.assert_called_once()

                # Verify no changes
                assert len(editor.monsters) == 2
                assert editor.is_dirty is False

            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_add_multiple_monsters(self, temp_data_file: Path) -> None:
        """Test adding multiple monsters."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file), \
             patch('ui.windows.monster_manager_win.get_db', return_value=None), \
             patch('ui.windows.monster_manager_win.DataSyncManager', None):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.monster_listbox is not None

                # Add 3 monsters
                for i in range(3):
                    dialog = editor._open_edit_dialog(None)
                    assert dialog is not None
                    dialog.name_entry.delete(0, tk.END)
                    dialog.name_entry.insert(0, f"Monster {i+1}")
                    dialog._on_save()
                    root.update_idletasks()

                # Verify all added
                assert len(editor.monsters) == 3
                assert editor.monster_listbox.size() == 3

            finally:
                if editor:
                    editor.destroy()
                root.destroy()
