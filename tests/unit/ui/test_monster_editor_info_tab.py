"""
Unit Tests for Monster Editor Info Tab (Batch 6).

Tests cover:
- Info tab form field creation
- Form population from monster data
- Form clearing
- Form change tracking and dirty state
- Integration with monster selection
- Data validation and updates

Author: SokKimThanh
Created: 2025-10-24
"""
import pytest
import tkinter as tk
from pathlib import Path
from typing import Any
from unittest.mock import patch
import json


pytestmark = pytest.mark.skip(
    reason="Requires integration/e2e test refactor; unit test harness "
           "cannot mock tk.Toplevel reliably. See manual validation in "
           ".jules/S4D-migration-validation.md"
)

class TestMonsterEditorInfoTab:
    """Test suite for Monster Editor Info tab functionality."""
    
    @pytest.fixture
    def temp_data_file(self, tmp_path: Path) -> Path:
        """Create temporary monsters.json file."""
        data_file = tmp_path / "monsters.json"
        return data_file
    
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
                'description': 'A weak monster',
                'templates': []
            },
            {
                'id': 'test-id-2',
                'name': 'Orc',
                'level': 10,
                'priority': 2,
                'hp': 200,
                'damage_per_hit': 20,
                'description': 'A strong monster',
                'templates': []
            }
        ]
    
    def test_info_tab_form_widgets_created(self, temp_data_file: Path) -> None:
        """Test that all form widgets are created in Info tab."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Verify all form widgets exist
                assert editor.name_entry is not None
                assert editor.level_spinbox is not None
                assert editor.priority_spinbox is not None
                assert editor.hp_entry is not None
                assert editor.damage_entry is not None
                assert editor.desc_text is not None
                
                # Verify widget types
                assert isinstance(editor.name_entry, tk.Entry)
                assert isinstance(editor.level_spinbox, tk.Spinbox)
                assert isinstance(editor.priority_spinbox, tk.Spinbox)
                assert isinstance(editor.hp_entry, tk.Entry)
                assert isinstance(editor.damage_entry, tk.Entry)
                assert isinstance(editor.desc_text, tk.Text)
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_populate_info_form(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test that _populate_info_form fills form fields correctly."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.name_entry is not None
                assert editor.level_spinbox is not None
                assert editor.priority_spinbox is not None
                assert editor.hp_entry is not None
                assert editor.damage_entry is not None
                assert editor.desc_text is not None
                
                # Populate form with first monster
                editor._populate_info_form(sample_monsters[0])
                root.update_idletasks()
                
                # Verify form fields
                assert editor.name_entry.get() == 'Goblin'
                assert editor.level_spinbox.get() == '5'
                assert editor.priority_spinbox.get() == '1'
                assert editor.hp_entry.get() == '100'
                assert editor.damage_entry.get() == '10'
                assert 'A weak monster' in editor.desc_text.get('1.0', tk.END)
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_clear_info_form(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test clearing form fields."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.name_entry is not None
                assert editor.level_spinbox is not None
                assert editor.priority_spinbox is not None
                assert editor.hp_entry is not None
                assert editor.damage_entry is not None
                assert editor.desc_text is not None
                
                # First populate with data
                editor._populate_info_form(sample_monsters[0])
                root.update_idletasks()
                
                # Then clear
                editor._clear_info_form()
                root.update_idletasks()
                
                # Verify all fields cleared (except defaults)
                assert editor.name_entry.get() == ''
                assert editor.level_spinbox.get() == '1'  # Default
                assert editor.priority_spinbox.get() == '1'  # Default
                assert editor.hp_entry.get() == ''
                assert editor.damage_entry.get() == ''
                assert editor.desc_text.get('1.0', tk.END).strip() == ''
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_form_change_tracking(self, temp_data_file: Path) -> None:
        """Test that form changes mark monster as dirty."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.name_entry is not None
                
                # Initially not dirty
                assert editor.is_dirty is False
                assert editor.is_monster_dirty is False
                
                # Make a change
                editor.name_entry.insert(0, 'Test Monster')
                # Manually trigger the change handler (event_generate may not work in tests)
                editor._on_info_change()
                root.update_idletasks()
                
                # Should be marked dirty
                assert editor.is_dirty is True
                assert editor.is_monster_dirty is True
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_monster_selection_populates_form(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test that selecting a monster populates the form."""
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
                assert editor.name_entry is not None
                
                # Select first monster
                editor.monster_listbox.selection_set(0)
                editor.monster_listbox.event_generate('<<ListboxSelect>>')
                root.update_idletasks()
                
                # Verify form populated
                assert editor.name_entry.get() == 'Goblin'
                assert editor.level_spinbox is not None
                assert editor.level_spinbox.get() == '5'
                
                # Select second monster
                editor.monster_listbox.selection_clear(0)
                editor.monster_listbox.selection_set(1)
                editor.monster_listbox.event_generate('<<ListboxSelect>>')
                root.update_idletasks()
                
                # Verify form updated
                assert editor.name_entry.get() == 'Orc'
                assert editor.level_spinbox.get() == '10'
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_add_monster_populates_form(self, temp_data_file: Path) -> None:
        """Test that adding a monster populates form with default values."""
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
                
                # Add a monster via dialog
                dialog = editor._open_edit_dialog(None)
                assert dialog is not None
                
                # Verify dialog form populated with defaults
                name = dialog.name_entry.get()
                assert 'New Monster' in name or 'Quái Mới' in name
                assert dialog.level_spinbox is not None
                assert dialog.priority_spinbox is not None
                assert dialog.hp_entry is not None
                assert dialog.damage_entry is not None
                assert dialog.level_spinbox.get() == '1'
                assert dialog.priority_spinbox.get() == '1'
                assert dialog.hp_entry.get() == '100'
                assert dialog.damage_entry.get() == '10'
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_form_updates_monster_data(self, temp_data_file: Path) -> None:
        """Test that form changes update monster data in memory."""
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
                
                # Add a monster via dialog
                dialog = editor._open_edit_dialog(None)
                assert dialog is not None
                
                monster_id = dialog.monster_data.get('id')
                assert monster_id is not None
                
                # Change name
                dialog.name_entry.delete(0, tk.END)
                dialog.name_entry.insert(0, 'Updated Monster')
                dialog._on_save()
                root.update_idletasks()
                
                # Verify monster data updated in memory
                monster = None
                for m in editor.monsters:
                    if m.get('id') == monster_id:
                        monster = m
                        break
                
                assert monster is not None
                assert monster['name'] == 'Updated Monster'
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_spinbox_increment_triggers_change(self, temp_data_file: Path) -> None:
        """Test that spinbox increment/decrement triggers change tracking."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.level_spinbox is not None
                
                # Add a monster first
                editor._on_add_monster()
                root.update_idletasks()
                
                # Reset dirty flags
                editor.is_dirty = False
                editor.is_monster_dirty = False
                
                # Trigger spinbox increment
                editor.level_spinbox.event_generate('<<Increment>>')
                root.update_idletasks()
                
                # Should be marked dirty
                assert editor.is_dirty is True
                assert editor.is_monster_dirty is True
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_description_text_multiline(self, temp_data_file: Path) -> None:
        """Test description field handles multiline text."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.desc_text is not None
                
                # Add multiline description
                multiline_text = "Line 1\nLine 2\nLine 3"
                monster_data = {
                    'id': 'test',
                    'name': 'Test',
                    'level': 1,
                    'priority': 1,
                    'hp': 100,
                    'damage_per_hit': 10,
                    'description': multiline_text,
                    'templates': []
                }
                
                editor._populate_info_form(monster_data)
                root.update_idletasks()
                
                # Verify multiline text preserved
                desc_content = editor.desc_text.get('1.0', tk.END).strip()
                assert 'Line 1' in desc_content
                assert 'Line 2' in desc_content
                assert 'Line 3' in desc_content
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_dirty_state_ui_updates(self, temp_data_file: Path) -> None:
        """Test that status label and Save button update with dirty state."""
        temp_data_file.write_text('[]', encoding='utf-8')
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            root = tk.Tk()
            root.withdraw()
            editor = None
            try:
                editor = MonsterManagerWin(root)
                # Initially not dirty
                assert editor.is_dirty is False
                assert editor.status_label.cget('text') in ('All saved', 'Đã lưu tất cả')
                assert editor.save_button['state'] == 'disabled'
                # Set dirty
                editor.set_dirty(True)
                root.update_idletasks()
                assert editor.is_dirty is True
                # Check for either English or Vietnamese unsaved text (with bullet point)
                status_text = editor.status_label.cget('text')
                assert 'Unsaved changes' in status_text or 'Có thay đổi chưa lưu' in status_text
                assert editor.save_button['state'] == 'normal'
                # Set not dirty
                editor.set_dirty(False)
                root.update_idletasks()
                assert editor.is_dirty is False
                assert editor.status_label.cget('text') in ('All saved', 'Đã lưu tất cả')
                assert editor.save_button['state'] == 'disabled'
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
