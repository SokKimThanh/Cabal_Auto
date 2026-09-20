import unittest
from unittest.mock import MagicMock
import tkinter as tk
from ui.components.icon_tree_component import IconTreeComponent

class DummyApp:
    lang = "vi"
    def _t(self, key, **kwargs):
        return key

class DummyVar:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
    def trace_add(self, *args, **kwargs):
        pass

class TestIconTreeComponent(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        # Mock tk.StringVar to return our DummyVar so tests pass
        self._orig_string_var = tk.StringVar
        tk.StringVar = lambda value="": DummyVar(value)
        self.app = DummyApp()
        self.mock_model = MagicMock()
        self.mock_model.loaded = True

        # When get_filtered_tree_data is called, return this dict
        self.mock_model.get_filtered_tree_data = MagicMock(return_value={1: [{"icon_key": "test_icon", "name": "Test Icon"}]})

        self.mock_model.get_category.return_value = {"name": "Test Cat"}
        self.mock_model.status_cache = {}
        self.mock_model.dependency_cache = {}

        self.on_node_selected_mock = MagicMock()
        self.on_interaction_mock = MagicMock()

        self.component = IconTreeComponent(
            self.root,
            app=self.app,
            tree_model=self.mock_model,
            categories_map={"Test Cat": 1},
            on_node_selected_callback=self.on_node_selected_mock,
            on_interaction_callback=self.on_interaction_mock
        )

    def tearDown(self):
        tk.StringVar = self._orig_string_var
        self.root.destroy()

    def test_initialization(self):
        self.assertTrue(hasattr(self.component, "tree"))
        self.assertTrue(hasattr(self.component, "search_entry"))
        self.assertTrue(hasattr(self.component, "category_combo"))
        self.assertTrue(hasattr(self.component, "status_combo"))

    def test_load_tree_data(self):
        self.component.load_tree_data()
        # Process queue
        self.component._process_incremental_queue([], [])
        # Check if node was inserted
        children = self.component.tree.get_children('')
        self.assertTrue(len(children) > 0)
        self.assertEqual(children[0], "cat_1")

    def test_trigger_filter(self):
        self.component.trigger_filter()
        self.assertIsNotNone(self.component._search_after_id)

    def test_tree_selection(self):
        self.component.load_tree_data()
        self.component._process_incremental_queue([], [])

        # Mock selection
        self.component.tree.selection = MagicMock(return_value=["icon_test_icon"])
        self.component.tree.item = MagicMock(return_value=["test_icon"])

        self.component._process_tree_selection()
        self.on_node_selected_mock.assert_called_with("test_icon")

if __name__ == '__main__':
    unittest.main()
