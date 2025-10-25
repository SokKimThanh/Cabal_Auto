"""
Unit Tests for ButtonStateMixin

Comprehensive test coverage for all methods and edge cases.

Author: SokKimThanh
Date: 2025-10-25
"""

import unittest
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.mixins import ButtonStateMixin


class TestButtonStateMixin(unittest.TestCase):
    """Test cases for ButtonStateMixin class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during tests
        
        # Create test window
        class TestWindow(tk.Frame, ButtonStateMixin):
            def __init__(self, parent, debug_mode=False):
                tk.Frame.__init__(self, parent)
                ButtonStateMixin.__init__(self, debug_mode=debug_mode)
        
        self.window = TestWindow(self.root)
        
        # Create test widgets
        self.test_tree = ttk.Treeview(self.window)
        self.test_listbox = tk.Listbox(self.window)
        self.test_button = tk.Button(self.window, text="Test")
        self.test_ttk_button = ttk.Button(self.window, text="Test TTK")
        
    def tearDown(self):
        """Clean up after tests."""
        try:
            self.root.destroy()
        except:
            pass
    
    # === Registration Tests ===
    
    def test_register_button_valid(self):
        """Test registering a valid button."""
        self.window.register_button('test_btn', self.test_button)
        self.assertIn('test_btn', self.window._button_refs)
        
    def test_register_button_none(self):
        """Test registering None button raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_button('test_btn', None)
            
    def test_register_button_empty_name(self):
        """Test registering button with empty name raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_button('', self.test_button)
            
    def test_register_button_wrong_type(self):
        """Test registering wrong type raises TypeError."""
        with self.assertRaises(TypeError):
            self.window.register_button('test_btn', "not a button")
            
    def test_register_widget_valid_treeview(self):
        """Test registering a valid Treeview."""
        self.window.register_selection_widget('test_tree', self.test_tree)
        self.assertIn('test_tree', self.window._selection_widgets)
        
    def test_register_widget_valid_listbox(self):
        """Test registering a valid Listbox."""
        self.window.register_selection_widget('test_list', self.test_listbox)
        self.assertIn('test_list', self.window._selection_widgets)
        
    def test_register_widget_none(self):
        """Test registering None widget raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_selection_widget('test_widget', None)
            
    def test_register_widget_empty_name(self):
        """Test registering widget with empty name raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_selection_widget('', self.test_tree)
            
    def test_register_widget_wrong_type(self):
        """Test registering wrong type raises TypeError."""
        with self.assertRaises(TypeError):
            self.window.register_selection_widget('test_widget', "not a widget")
            
    def test_register_button_rules_valid(self):
        """Test registering valid button rules."""
        rules = {
            'btn1': {'always': True},
            'btn2': {'requires_selection': 'widget1'}
        }
        self.window.register_button_rules(rules)
        self.assertEqual(len(self.window._button_rules), 2)
        
    def test_register_button_rules_not_dict(self):
        """Test registering non-dict rules raises TypeError."""
        with self.assertRaises(TypeError):
            self.window.register_button_rules("not a dict")
            
    def test_register_button_rules_invalid_rule_type(self):
        """Test registering invalid rule type raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_button_rules({'btn1': "not a dict"})
            
    def test_register_button_rules_invalid_always_type(self):
        """Test invalid 'always' type raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_button_rules({'btn1': {'always': "yes"}})
            
    def test_register_button_rules_invalid_requires_selection_type(self):
        """Test invalid 'requires_selection' type raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_button_rules({'btn1': {'requires_selection': 123}})
            
    def test_register_button_rules_invalid_custom_type(self):
        """Test invalid 'custom' type raises ValueError."""
        with self.assertRaises(ValueError):
            self.window.register_button_rules({'btn1': {'custom': "not callable"}})
    
    # === Batch Registration Tests ===
    
    def test_register_buttons_batch(self):
        """Test batch button registration."""
        buttons = {
            'btn1': self.test_button,
            'btn2': self.test_ttk_button
        }
        self.window.register_buttons_batch(buttons)
        self.assertEqual(len(self.window._button_refs), 2)
        
    def test_register_widgets_batch(self):
        """Test batch widget registration."""
        widgets = {
            'tree': self.test_tree,
            'list': self.test_listbox
        }
        self.window.register_widgets_batch(widgets)
        self.assertEqual(len(self.window._selection_widgets), 2)
    
    # === Selection Tests ===
    
    def test_has_selection_treeview_empty(self):
        """Test Treeview with no selection."""
        self.window.register_selection_widget('tree', self.test_tree)
        self.assertFalse(self.window.has_selection('tree'))
        
    def test_has_selection_treeview_with_selection(self):
        """Test Treeview with selection."""
        self.window.register_selection_widget('tree', self.test_tree)
        item_id = self.test_tree.insert('', 'end', text='Test')
        self.test_tree.selection_set(item_id)
        self.assertTrue(self.window.has_selection('tree'))
        
    def test_has_selection_listbox_empty(self):
        """Test Listbox with no selection."""
        self.window.register_selection_widget('list', self.test_listbox)
        self.assertFalse(self.window.has_selection('list'))
        
    def test_has_selection_listbox_with_selection(self):
        """Test Listbox with selection."""
        self.window.register_selection_widget('list', self.test_listbox)
        self.test_listbox.insert('end', 'Test')
        self.test_listbox.selection_set(0)
        self.assertTrue(self.window.has_selection('list'))
        
    def test_has_selection_unregistered_widget(self):
        """Test checking selection on unregistered widget."""
        self.assertFalse(self.window.has_selection('nonexistent'))
        
    def test_get_selection_value_treeview(self):
        """Test getting selection value from Treeview."""
        self.window.register_selection_widget('tree', self.test_tree)
        item_id = self.test_tree.insert('', 'end', text='Test')
        self.test_tree.selection_set(item_id)
        self.assertEqual(self.window.get_selection_value('tree'), item_id)
        
    def test_get_selection_value_listbox(self):
        """Test getting selection value from Listbox."""
        self.window.register_selection_widget('list', self.test_listbox)
        self.test_listbox.insert('end', 'Test')
        self.test_listbox.selection_set(0)
        self.assertEqual(self.window.get_selection_value('list'), 0)
        
    def test_get_selection_value_no_selection(self):
        """Test getting selection value when no selection."""
        self.window.register_selection_widget('tree', self.test_tree)
        self.assertIsNone(self.window.get_selection_value('tree'))
    
    # === Button State Tests ===
    
    def test_should_enable_button_always_true(self):
        """Test button with always=True rule."""
        self.window.register_button_rules({'btn1': {'always': True}})
        self.assertTrue(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_always_false(self):
        """Test button with always=False rule."""
        self.window.register_button_rules({'btn1': {'always': False}})
        self.assertFalse(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_requires_selection_no_selection(self):
        """Test button requiring selection when no selection."""
        self.window.register_selection_widget('tree', self.test_tree)
        self.window.register_button_rules({'btn1': {'requires_selection': 'tree'}})
        self.assertFalse(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_requires_selection_with_selection(self):
        """Test button requiring selection when has selection."""
        self.window.register_selection_widget('tree', self.test_tree)
        item_id = self.test_tree.insert('', 'end', text='Test')
        self.test_tree.selection_set(item_id)
        self.window.register_button_rules({'btn1': {'requires_selection': 'tree'}})
        self.assertTrue(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_requires_parent_no_parent(self):
        """Test child button requiring parent when no parent selected."""
        self.window.register_selection_widget('parent', self.test_tree)
        self.window.register_button_rules({'child_btn': {'requires_parent': 'parent'}})
        self.assertFalse(self.window.should_enable_button('child_btn'))
        
    def test_should_enable_button_requires_parent_with_parent(self):
        """Test child button requiring parent when parent selected."""
        self.window.register_selection_widget('parent', self.test_tree)
        item_id = self.test_tree.insert('', 'end', text='Parent')
        self.test_tree.selection_set(item_id)
        self.window.register_button_rules({'child_btn': {'requires_parent': 'parent'}})
        self.assertTrue(self.window.should_enable_button('child_btn'))
        
    def test_should_enable_button_requires_multiple_partial(self):
        """Test button requiring multiple selections with only partial selection."""
        tree1 = ttk.Treeview(self.window)
        tree2 = ttk.Treeview(self.window)
        self.window.register_selection_widget('tree1', tree1)
        self.window.register_selection_widget('tree2', tree2)
        
        # Only select in tree1
        item = tree1.insert('', 'end', text='Item')
        tree1.selection_set(item)
        
        self.window.register_button_rules({
            'btn1': {'requires_multiple': ['tree1', 'tree2']}
        })
        self.assertFalse(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_requires_multiple_all(self):
        """Test button requiring multiple selections with all selected."""
        tree1 = ttk.Treeview(self.window)
        tree2 = ttk.Treeview(self.window)
        self.window.register_selection_widget('tree1', tree1)
        self.window.register_selection_widget('tree2', tree2)
        
        # Select in both
        item1 = tree1.insert('', 'end', text='Item1')
        item2 = tree2.insert('', 'end', text='Item2')
        tree1.selection_set(item1)
        tree2.selection_set(item2)
        
        self.window.register_button_rules({
            'btn1': {'requires_multiple': ['tree1', 'tree2']}
        })
        self.assertTrue(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_custom_true(self):
        """Test button with custom rule returning True."""
        self.window.register_button_rules({
            'btn1': {'custom': lambda: True}
        })
        self.assertTrue(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_custom_false(self):
        """Test button with custom rule returning False."""
        self.window.register_button_rules({
            'btn1': {'custom': lambda: False}
        })
        self.assertFalse(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_custom_exception(self):
        """Test button with custom rule raising exception."""
        def raise_error():
            raise RuntimeError("Test error")
        
        self.window.register_button_rules({
            'btn1': {'custom': raise_error}
        })
        # Should return False when custom function raises
        self.assertFalse(self.window.should_enable_button('btn1'))
        
    def test_should_enable_button_no_rule(self):
        """Test button with no rule defaults to enabled."""
        self.assertTrue(self.window.should_enable_button('unknown_btn'))
    
    # === State Inspection Tests ===
    
    def test_get_enabled_buttons(self):
        """Test getting list of enabled buttons."""
        self.window.register_button_rules({
            'btn1': {'always': True},
            'btn2': {'always': False},
            'btn3': {'always': True}
        })
        enabled = self.window.get_enabled_buttons()
        self.assertEqual(set(enabled), {'btn1', 'btn3'})
        
    def test_get_disabled_buttons(self):
        """Test getting list of disabled buttons."""
        self.window.register_button_rules({
            'btn1': {'always': True},
            'btn2': {'always': False},
            'btn3': {'always': False}
        })
        disabled = self.window.get_disabled_buttons()
        self.assertEqual(set(disabled), {'btn2', 'btn3'})
        
    def test_debug_state(self):
        """Test debug state information."""
        self.window.register_selection_widget('tree', self.test_tree)
        self.window.register_button('btn1', self.test_button)
        self.window.register_button_rules({'btn1': {'always': True}})
        
        state = self.window.debug_state()
        
        self.assertIn('registered_widgets', state)
        self.assertIn('registered_buttons', state)
        self.assertIn('button_rules', state)
        self.assertIn('selections', state)
        self.assertIn('enabled_buttons', state)
        self.assertIn('disabled_buttons', state)
        
        self.assertEqual(state['registered_widgets'], ['tree'])
        self.assertEqual(state['registered_buttons'], ['btn1'])
    
    # === Update Button States Tests ===
    
    def test_update_button_states_enables_button(self):
        """Test update_button_states enables button when should be enabled."""
        self.window.register_button('btn1', self.test_button)
        self.window.register_button_rules({'btn1': {'always': True}})
        
        self.window.update_button_states()
        
        self.assertEqual(str(self.test_button['state']), 'normal')
        
    def test_update_button_states_disables_button(self):
        """Test update_button_states disables button when should be disabled."""
        self.window.register_button('btn1', self.test_button)
        self.window.register_button_rules({'btn1': {'always': False}})
        
        self.window.update_button_states()
        
        self.assertEqual(str(self.test_button['state']), 'disabled')
    
    # === Hierarchical Setup Tests ===
    
    def test_setup_hierarchical_buttons(self):
        """Test hierarchical button setup."""
        parent_tree = ttk.Treeview(self.window)
        child_tree = ttk.Treeview(self.window)
        
        parent_add = tk.Button(self.window)
        parent_edit = tk.Button(self.window)
        parent_delete = tk.Button(self.window)
        
        child_add = tk.Button(self.window)
        child_edit = tk.Button(self.window)
        child_delete = tk.Button(self.window)
        
        self.window.register_selection_widget('parent', parent_tree)
        self.window.register_selection_widget('child', child_tree)
        
        self.window.setup_hierarchical_buttons(
            parent_widget='parent',
            child_widget='child',
            parent_buttons={
                'add': parent_add,
                'edit': parent_edit,
                'delete': parent_delete
            },
            child_buttons={
                'add': child_add,
                'edit': child_edit,
                'delete': child_delete
            }
        )
        
        # Check all buttons registered
        self.assertIn('parent_add', self.window._button_refs)
        self.assertIn('parent_edit', self.window._button_refs)
        self.assertIn('parent_delete', self.window._button_refs)
        self.assertIn('child_add', self.window._button_refs)
        self.assertIn('child_edit', self.window._button_refs)
        self.assertIn('child_delete', self.window._button_refs)
        
        # Check rules created
        self.assertIn('parent_add', self.window._button_rules)
        self.assertIn('child_add', self.window._button_rules)


class TestButtonStateMixinDebugMode(unittest.TestCase):
    """Test debug mode functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        class TestWindow(tk.Frame, ButtonStateMixin):
            def __init__(self, parent):
                tk.Frame.__init__(self, parent)
                ButtonStateMixin.__init__(self, debug_mode=True)
        
        self.window = TestWindow(self.root)
        
    def tearDown(self):
        """Clean up after tests."""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_debug_mode_enabled(self):
        """Test debug mode is enabled."""
        self.assertTrue(self.window._debug_mode)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
