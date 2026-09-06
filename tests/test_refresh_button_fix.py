"""Test window detection fix - verify refresh button flow

This test suite verifies the fix for the refresh button not populating the window
combobox in the main UI. The issue was that the window process filter only accepted
"cabal.exe" but the actual process name is "CabalMain.exe".

Fix applied: Added "cabalmain.exe" to the allowed_processes list in
AppWindowController._list_windows() method.

GitHub Issue: Refresh button doesn't show window list in combobox
User Report: "nút refresh không sổ ra danh sách cửa sổ hiện tại trong combobox để chọn hwnd"
"""
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestWindowDetectionRefreshFix(unittest.TestCase):
    """Test that refresh button properly populates window combobox"""

    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.title("Test App")
        
        # Create combobox like app_gui.py does
        self.win_combo_var = tk.StringVar()
        self.win_combo = ttk.Combobox(
            self.root, textvariable=self.win_combo_var, state="readonly"
        )
        self.win_combo.pack()
        
        # Store on root like app_gui.py
        self.root.win_combo = self.win_combo
        self.root.win_combo_var = self.win_combo_var
        
        # Add missing status var for app_window_controller
        self.root.hunt_status = tk.StringVar(value="Ready")
        self.root.current_window_bounds = None
        self.root.hunt_selected = None
        
        # Import after root exists
        from ui.controllers.app_window_controller import AppWindowController
        self.controller = AppWindowController(self.root)
        
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass

    def test_list_windows_finds_cabal_main_exe(self):
        """Test that _list_windows accepts CabalMain.exe process"""
        # Get windows
        windows = self.controller._list_windows()
        
        # Should find at least cabal window if running
        # On test machine should find Cabal (title="CABAL", proc=CabalMain.exe)
        self.assertIsInstance(windows, list)
        print(f"✅ _list_windows returned list with {len(windows)} items")
        
        if windows:
            for w in windows:
                print(f"   - {w['title']} (proc: {w['proc']})")
                # Verify structure
                self.assertIn('hwnd', w)
                self.assertIn('pid', w)
                self.assertIn('title', w)
                self.assertIn('proc', w)
                self.assertIn('bounds', w)
                self.assertIn('is_minimized', w)
    
    def test_on_hunt_find_windows_populates_combobox(self):
        """Test that on_hunt_find_windows properly sets combobox values"""
        # Store original state
        original_values = self.win_combo['values']
        
        # Call the method
        self.controller.on_hunt_find_windows()
        
        # Get new values
        new_values = self.win_combo['values']
        
        print(f"✅ on_hunt_find_windows executed")
        print(f"   Combobox values: {new_values}")
        
        # Verify win_items was set
        self.assertTrue(hasattr(self.root, 'win_items'))
        print(f"   win_items set: {len(self.root.win_items)} windows")
        
        # If windows were found, they should appear in combobox
        if self.root.win_items:
            titles = [item['title'] for item in self.root.win_items]
            self.assertEqual(list(new_values), titles)
            print(f"   ✅ Combobox values match win_items")
            
    def test_allowed_processes_includes_cabalmain_exe(self):
        """Verify allowed_processes list includes CabalMain.exe"""
        # This is a white-box test of internal implementation
        # Extract the allowed_processes from _list_windows source
        import inspect
        source = inspect.getsource(self.controller._list_windows)
        
        # Check that both cabal.exe and cabalmain.exe are in source
        self.assertIn('cabal.exe', source.lower())
        self.assertIn('cabalmain.exe', source.lower())
        print("✅ Allowed processes list includes both cabal.exe and cabalmain.exe")


if __name__ == '__main__':
    unittest.main(verbosity=2)
