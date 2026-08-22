"""
Unit tests for Monster Editor data operations.

Tests for Batch 3: Load/Save monsters.json functionality.

Author: SokKimThanh
Created: 2025-10-24
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import tkinter as tk
from typing import Any

# Mock the imports before importing the module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

class TestMonsterEditorData:
    """Test data layer operations."""
    
    @pytest.fixture
    def temp_data_file(self):
        """Create temporary data file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            yield temp_path
            if temp_path.exists():
                temp_path.unlink()
    
    @pytest.fixture
    def sample_monsters(self):
        """Sample monster data."""
        return [
            {
                'id': 'monster-1',
                'name': 'Test Monster',
                'level': 50,
                'priority': 1,
                'hp': 1000,
                'damage_per_hit': 50,
                'description': 'Test description',
                'templates': []
            },
            {
                'id': 'monster-2',
                'name': 'Another Monster',
                'level': 75,
                'priority': 2,
                'hp': 2000,
                'damage_per_hit': 100,
                'description': '',
                'templates': []
            }
        ]
    
    def test_load_monsters_empty_file(self, temp_data_file: Path) -> None:
        """Test loading from empty file."""
        # Create empty file
        temp_data_file.write_text('[]', encoding='utf-8')
        
        # Mock DATA_PATH
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = QuickMonsterEditor(root)
                editor._load_monsters()
                
                assert editor.monsters == []
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_load_monsters_valid_data(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test loading valid monster data."""
        # Write sample data
        temp_data_file.write_text(
            json.dumps(sample_monsters, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = QuickMonsterEditor(root)
                editor._load_monsters()
                
                assert len(editor.monsters) == 2
                assert editor.monsters[0]['name'] == 'Test Monster'
                assert editor.monsters[1]['name'] == 'Another Monster'
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_load_monsters_auto_generate_ids(self, temp_data_file: Path) -> None:
        """Test auto-generating IDs for monsters without IDs."""
        # Monsters without IDs
        monsters_without_ids = [
            {
                'name': 'No ID Monster',
                'level': 1,
                'templates': []
            }
        ]
        
        temp_data_file.write_text(
            json.dumps(monsters_without_ids, indent=2),
            encoding='utf-8'
        )
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = QuickMonsterEditor(root)
                editor._load_monsters()
                
                assert len(editor.monsters) == 1
                assert 'id' in editor.monsters[0]
                assert len(editor.monsters[0]['id']) > 0
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_load_monsters_file_not_found(self, temp_data_file: Path) -> None:
        """Test handling missing file."""
        # Use non-existent path
        non_existent = temp_data_file.parent / 'non_existent.json'
        
        with patch('ui.windows.quick_monster_editor.DATA_PATH', non_existent):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = QuickMonsterEditor(root)
                editor._load_monsters()
                
                # Should create empty list and file
                assert editor.monsters == []
                assert non_existent.exists()
                
                # Clean up
                non_existent.unlink()
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_save_monsters(self, temp_data_file: Path, sample_monsters: list) -> None:
        """Test saving monsters to file."""
        with patch('ui.windows.quick_monster_editor.DATA_PATH', temp_data_file):
            from ui.windows.quick_monster_editor import QuickMonsterEditor
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = QuickMonsterEditor(root)
                editor.monsters = sample_monsters
                editor.is_dirty = True
                
                result = editor._save_monsters()
                
                assert result is True
                assert editor.is_dirty is False
                
                # Verify file content
                with open(temp_data_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                assert len(saved_data) == 2
                assert saved_data[0]['name'] == 'Test Monster'
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_save_monsters_error_handling(self) -> None:
        """Test error handling when save fails."""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        
        root = tk.Tk()
        root.withdraw()
        editor = None
        
        try:
            editor = QuickMonsterEditor(root)
            editor.monsters = [{'id': '1', 'name': 'Test'}]
            
            # Mock open to raise error
            with patch('builtins.open', side_effect=IOError('Mock error')):
                result = editor._save_monsters()
                
                assert result is False
        finally:
            if editor:
                editor.destroy()
            root.destroy()
    
    def test_dirty_state_tracking(self) -> None:
        """Test dirty state flags."""
        from ui.windows.quick_monster_editor import QuickMonsterEditor
        
        root = tk.Tk()
        root.withdraw()
        editor = None
        
        try:
            editor = QuickMonsterEditor(root)
            
            # Initial state
            assert editor.is_dirty is False
            assert editor.is_monster_dirty is False
            
            # Mark as dirty
            editor.is_dirty = True
            editor.is_monster_dirty = True
            
            assert editor.is_dirty is True
            assert editor.is_monster_dirty is True
            
            # Save should clear flags
            editor.monsters = []
            editor._save_monsters()
            
            assert editor.is_dirty is False
            assert editor.is_monster_dirty is False
        finally:
            if editor:
                editor.destroy()
            root.destroy()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
