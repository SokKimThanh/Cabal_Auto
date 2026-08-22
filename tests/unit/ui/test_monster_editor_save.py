"""
Unit tests for Monster Editor Save All Functionality (Batch 9).

Tests verify save button handler, validation, and dirty state clearing.
Following PYTHON_CODING_GUIDELINES.md - Type hints, None checks, proper assertions.
"""

import json
import tkinter as tk
from pathlib import Path
from typing import Optional
from unittest.mock import patch, MagicMock

import pytest


class TestMonsterEditorSaveAll:
    """Test suite for Save All functionality."""
    
    @pytest.fixture
    def temp_data_file(self, tmp_path: Path) -> Path:
        """
        Create temporary monsters.json file.
        
        Args:
            tmp_path: pytest temporary directory fixture
            
        Returns:
            Path to temporary data file
        """
        data_file = tmp_path / "monsters.json"
        return data_file
    
    @pytest.fixture
    def sample_monsters(self) -> list:
        """
        Create sample monster data for testing.
        
        Returns:
            List of monster dictionaries
        """
        return [
            {
                'id': 'monster_1',
                'name': 'Goblin',
                'level': 5,
                'priority': 1,
                'hp': 100,
                'damage': 10,
                'description': 'A weak monster'
            },
            {
                'id': 'monster_2',
                'name': 'Orc',
                'level': 10,
                'priority': 2,
                'hp': 200,
                'damage': 20,
                'description': 'A stronger monster'
            }
        ]
    
    def test_save_button_saves_all_monsters(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test that clicking Save button saves all monsters to JSON."""
        # Write initial data
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[QuickMonsterEditor] = None
            
            try:
                editor = QuickMonsterEditor(root)
                
                # Rule 2: Check None before access
                assert editor.monsters is not None, "Monsters list should be loaded"
                assert len(editor.monsters) == 2, "Should load 2 monsters"
                
                # Modify a monster
                if editor.name_entry is not None:
                    editor.name_entry.delete(0, tk.END)
                    editor.name_entry.insert(0, 'Modified Goblin')
                    editor._on_info_change()
                
                # Rule 2: Check button exists
                assert editor.save_button is not None, "Save button should exist"
                
                # Click save button
                editor.save_button.invoke()
                root.update_idletasks()
                
                # Verify file was saved
                assert temp_data_file.exists(), "Data file should exist after save"
                
                # Read and verify saved data
                with open(temp_data_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                # Rule 1: Type check saved data
                assert isinstance(saved_data, list), "Saved data should be a list"
                assert len(saved_data) == 2, "Should save 2 monsters"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_save_clears_dirty_state(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test that saving clears dirty state and updates UI."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[QuickMonsterEditor] = None
            
            try:
                editor = QuickMonsterEditor(root)
                
                # Make a change to set dirty
                editor.set_dirty(True)
                root.update_idletasks()
                
                # Verify dirty before save
                assert editor.is_dirty is True, "Should be dirty after change"
                
                # Rule 2: Check widgets exist
                assert editor.save_button is not None, "Save button should exist"
                assert editor.status_label is not None, "Status label should exist"
                
                # Save
                with patch('tkinter.messagebox.showinfo'):  # Suppress messagebox
                    editor.save_button.invoke()
                    root.update_idletasks()
                
                # Verify clean state
                assert editor.is_dirty is False, "Should be clean after save"
                assert editor.is_monster_dirty is False, "Monster should be clean after save"
                
                # Verify UI updated
                status_text = editor.status_label.cget('text')
                assert 'All saved' in status_text or 'Đã lưu tất cả' in status_text, "Status should show saved"
                
                # Verify save button disabled
                assert editor.save_button['state'] == 'disabled', "Save button should be disabled when clean"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_save_validates_monster_names(self, temp_data_file: Path) -> None:
        """Test that save validates monster names (no empty names)."""
        # Create monster with empty name
        invalid_monsters = [
            {
                'id': 'monster_1',
                'name': '',  # Empty name
                'level': 5,
                'priority': 1,
                'hp': 100,
                'damage': 10,
                'description': ''
            }
        ]
        temp_data_file.write_text(json.dumps(invalid_monsters), encoding='utf-8')
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[QuickMonsterEditor] = None
            
            try:
                editor = QuickMonsterEditor(root)
                
                # Rule 2: Check button exists
                assert editor.save_button is not None, "Save button should exist"
                
                # Mock messagebox to capture error
                with patch('tkinter.messagebox.showerror') as mock_error:
                    editor.save_button.invoke()
                    root.update_idletasks()
                    
                    # Verify error shown
                    assert mock_error.called, "Should show error for empty name"
                    call_args = mock_error.call_args[0]
                    assert 'no name' in call_args[1].lower(), "Error should mention missing name"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_save_with_no_monsters_shows_warning(self, temp_data_file: Path) -> None:
        """Test that saving with no monsters shows warning."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[QuickMonsterEditor] = None
            
            try:
                editor = QuickMonsterEditor(root)
                
                # Verify no monsters
                assert len(editor.monsters) == 0, "Should have no monsters"
                
                # Rule 2: Check button exists
                assert editor.save_button is not None, "Save button should exist"
                
                # Mock messagebox
                with patch('tkinter.messagebox.showwarning') as mock_warning:
                    editor.save_button.invoke()
                    root.update_idletasks()
                    
                    # Verify warning shown
                    assert mock_warning.called, "Should show warning when no data"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_save_button_initially_disabled(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test that Save button is initially disabled when clean."""
        temp_data_file.write_text(json.dumps(sample_monsters), encoding='utf-8')
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file), \
             patch('ui.windows.quick_monster_editor.get_db', return_value=None), \
             patch('ui.windows.quick_monster_editor.DataSyncManager', None):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[QuickMonsterEditor] = None
            
            try:
                editor = QuickMonsterEditor(root)
                
                # Rule 2: Check button exists
                assert editor.save_button is not None, "Save button should exist"
                
                # Verify initially disabled (clean state)
                assert editor.is_dirty is False, "Should be clean initially"
                assert editor.save_button['state'] == 'disabled', "Save button should be disabled when clean"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
