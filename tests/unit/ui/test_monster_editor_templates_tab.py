"""
Unit tests for Monster Editor Templates Tab UI.

Tests verify Templates tab widget creation, layout, and initial state.
Following PYTHON_CODING_GUIDELINES.md - Type hints, None checks, proper assertions.
"""

import json
import tkinter as tk
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import pytest


import os
pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)
class TestMonsterEditorTemplatesTab:
    """Test suite for Templates tab UI components."""
    
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
    
    def test_templates_tab_created(self, temp_data_file: Path) -> None:
        """Test that Templates tab is created in notebook."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[MonsterManagerWin] = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Rule 2: Check None before access
                assert editor.notebook is not None, "Notebook should be created"
                assert editor.templates_tab is not None, "Templates tab should be created"
                
                # Verify tab added to notebook
                tab_count = editor.notebook.index('end')
                assert tab_count == 2, "Should have 2 tabs (Info, Templates)"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_template_listbox_created(self, temp_data_file: Path) -> None:
        """Test that template listbox is created with scrollbar."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[MonsterManagerWin] = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Rule 2: Check None before accessing attributes
                assert editor.template_listbox is not None, "Template listbox should be created"
                assert editor.template_scrollbar is not None, "Scrollbar should be created"
                
                # Rule 1: Type check widget types
                assert isinstance(editor.template_listbox, tk.Listbox), "Should be Listbox widget"
                assert isinstance(editor.template_scrollbar, tk.Scrollbar), "Should be Scrollbar widget"
                
                # Verify listbox configuration
                assert editor.template_listbox['selectmode'] == tk.SINGLE, "Should be single select"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_control_buttons_created(self, temp_data_file: Path) -> None:
        """Test that all control buttons are created."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[MonsterManagerWin] = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Rule 2: Check None before access
                assert editor.capture_button is not None, "Capture button should be created"
                assert editor.browse_button is not None, "Browse button should be created"
                assert editor.delete_template_button is not None, "Delete button should be created"
                assert editor.test_template_button is not None, "Test button should be created"
                
                # Rule 1: Type check all buttons
                assert isinstance(editor.capture_button, tk.Button), "Should be Button widget"
                assert isinstance(editor.browse_button, tk.Button), "Should be Button widget"
                assert isinstance(editor.delete_template_button, tk.Button), "Should be Button widget"
                assert isinstance(editor.test_template_button, tk.Button), "Should be Button widget"
                
                # Verify button texts (check translation keys work)
                capture_text = editor.capture_button['text']
                assert capture_text is not None and len(capture_text) > 0, "Capture button should have text"
                
                browse_text = editor.browse_button['text']
                assert browse_text is not None and len(browse_text) > 0, "Browse button should have text"
                
                delete_text = editor.delete_template_button['text']
                assert delete_text is not None and len(delete_text) > 0, "Delete button should have text"
                
                test_text = editor.test_template_button['text']
                assert test_text is not None and len(test_text) > 0, "Test button should have text"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_threshold_slider_created(self, temp_data_file: Path) -> None:
        """Test that threshold slider is created with correct range and default."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[MonsterManagerWin] = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Rule 2: Check None before access
                assert editor.threshold_scale is not None, "Threshold scale should be created"
                assert editor.threshold_label is not None, "Threshold label should be created"
                
                # Rule 1: Type check widgets
                assert isinstance(editor.threshold_scale, tk.Scale), "Should be Scale widget"
                assert isinstance(editor.threshold_label, tk.Label), "Should be Label widget"
                
                # Verify slider configuration
                assert editor.threshold_scale['from'] == 0.0, "Should start at 0.0"
                assert editor.threshold_scale['to'] == 1.0, "Should end at 1.0"
                assert editor.threshold_scale['resolution'] == 0.01, "Should have 0.01 resolution"
                assert editor.threshold_scale['orient'] == 'horizontal', "Should be horizontal"
                
                # Verify default value
                current_value = editor.threshold_scale.get()
                assert current_value == 0.7, "Default threshold should be 0.7"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_threshold_slider_value_range(self, temp_data_file: Path) -> None:
        """Test that threshold slider accepts values in valid range."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[MonsterManagerWin] = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Rule 2: Check None before use
                assert editor.threshold_scale is not None, "Threshold scale should exist"
                
                # Test setting minimum value
                editor.threshold_scale.set(0.0)
                root.update_idletasks()
                assert editor.threshold_scale.get() == 0.0, "Should accept 0.0"
                
                # Test setting maximum value
                editor.threshold_scale.set(1.0)
                root.update_idletasks()
                assert editor.threshold_scale.get() == 1.0, "Should accept 1.0"
                
                # Test setting middle value
                editor.threshold_scale.set(0.5)
                root.update_idletasks()
                assert editor.threshold_scale.get() == 0.5, "Should accept 0.5"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
    
    def test_templates_tab_widgets_all_optional_type(self, temp_data_file: Path) -> None:
        """Test that all template tab widgets are properly typed as Optional."""
        temp_data_file.write_text('[]', encoding='utf-8')
        
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            try:
                root = tk.Tk()
            except Exception as e:
                pytest.skip(f"Tkinter not available: {e}")
                return
            
            root.withdraw()
            editor: Optional[MonsterManagerWin] = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Rule 2: All widgets should be checkable for None
                # This test verifies widgets are created (not None after init)
                widgets_to_check = [
                    ('template_listbox', editor.template_listbox),
                    ('template_scrollbar', editor.template_scrollbar),
                    ('capture_button', editor.capture_button),
                    ('browse_button', editor.browse_button),
                    ('delete_template_button', editor.delete_template_button),
                    ('test_template_button', editor.test_template_button),
                    ('threshold_scale', editor.threshold_scale),
                    ('threshold_label', editor.threshold_label),
                ]
                
                for widget_name, widget in widgets_to_check:
                    assert widget is not None, f"{widget_name} should be created and not None"
                
            finally:
                if editor is not None:
                    editor.destroy()
                root.destroy()
