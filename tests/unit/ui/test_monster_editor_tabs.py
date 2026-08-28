"""
Unit Tests for Monster Editor Right Panel Tabs (Batch 5).

Tests cover:
- Right panel creation with notebook
- Tab creation (Info and Templates)
- Tab switching and visibility
- Notebook widget state

Author: SokKimThanh
Created: 2025-10-24
"""
import pytest
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Any
from unittest.mock import patch
import json


import os
pytestmark = pytest.mark.skipif(
    not os.getenv("DISPLAY") and os.name != "nt",
    reason="Requires active display or xvfb to run Tkinter tests"
)
class TestMonsterEditorRightPanel:
    """Test suite for Monster Editor right panel with tabs."""
    
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
    
    def test_right_panel_creation(self, temp_data_file: Path) -> None:
        """Test that right panel with notebook is created correctly."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Verify notebook widget exists
                assert editor.notebook is not None
                assert isinstance(editor.notebook, ttk.Notebook)
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_info_tab_creation(self, temp_data_file: Path) -> None:
        """Test that Info tab is created correctly."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.notebook is not None
                assert editor.info_tab is not None
                
                # Verify tab exists in notebook
                assert editor.notebook.index('end') >= 1
                
                # Verify tab text
                tab_text = editor.notebook.tab(0, 'text')
                assert 'Monster Info' in tab_text or 'Thông Tin Quái' in tab_text
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_templates_tab_creation(self, temp_data_file: Path) -> None:
        """Test that Templates tab is created correctly."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.notebook is not None
                assert editor.templates_tab is not None
                
                # Verify both tabs exist
                assert editor.notebook.index('end') == 2
                
                # Verify templates tab text
                tab_text = editor.notebook.tab(1, 'text')
                assert 'Templates' in tab_text
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_tab_switching(self, temp_data_file: Path) -> None:
        """Test switching between tabs."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.notebook is not None
                
                # Initially on first tab
                assert editor.notebook.index('current') == 0
                
                # Switch to second tab
                editor.notebook.select(1)
                root.update_idletasks()
                
                # Verify switch
                assert editor.notebook.index('current') == 1
                
                # Switch back to first tab
                editor.notebook.select(0)
                root.update_idletasks()
                
                # Verify switch
                assert editor.notebook.index('current') == 0
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_both_tabs_exist(self, temp_data_file: Path) -> None:
        """Test that both tabs are created in correct order."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.notebook is not None
                
                # Verify exactly 2 tabs
                assert editor.notebook.index('end') == 2
                
                # Verify tab order
                tab0_text = editor.notebook.tab(0, 'text')
                tab1_text = editor.notebook.tab(1, 'text')
                
                # First tab should be Info
                assert 'Info' in tab0_text or 'Thông Tin' in tab0_text
                
                # Second tab should be Templates
                assert 'Templates' in tab1_text
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_tab_frames_distinct(self, temp_data_file: Path) -> None:
        """Test that Info and Templates tabs have distinct frames."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                
                # Verify frames are distinct objects
                assert editor.info_tab is not None
                assert editor.templates_tab is not None
                assert editor.info_tab is not editor.templates_tab
                
                # Verify both are tk.Frame instances
                assert isinstance(editor.info_tab, tk.Frame)
                assert isinstance(editor.templates_tab, tk.Frame)
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
    
    def test_placeholder_content_in_tabs(self, temp_data_file: Path) -> None:
        """Test that tabs contain placeholder content."""
        with patch('ui.windows.monster_manager_win.DATA_PATH', temp_data_file):
            from ui.windows.monster_manager_win import MonsterManagerWin
            
            root = tk.Tk()
            root.withdraw()
            editor = None
            
            try:
                editor = MonsterManagerWin(root)
                assert editor.info_tab is not None
                assert editor.templates_tab is not None
                
                # Verify info tab has children (placeholder label)
                info_children = editor.info_tab.winfo_children()
                assert len(info_children) > 0
                
                # Verify templates tab has children (placeholder label)
                templates_children = editor.templates_tab.winfo_children()
                assert len(templates_children) > 0
                
            finally:
                if editor:
                    editor.destroy()
                root.destroy()
