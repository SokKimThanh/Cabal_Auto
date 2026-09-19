import unittest
from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor, CommonUI

class TestUIElementRegistry(unittest.TestCase):
    def setUp(self):
        UIElementRegistry.instance().clear()

    def tearDown(self):
        UIElementRegistry.instance().clear()

    def test_registry_is_singleton(self):
        registry1 = UIElementRegistry.instance()
        registry2 = UIElementRegistry.instance()
        registry3 = UIElementRegistry()

        self.assertIs(registry1, registry2)
        self.assertIs(registry1, registry3)
        self.assertEqual(id(registry1), id(registry2))

    def test_registry_idempotent_registration(self):
        registry = UIElementRegistry.instance()
        desc = UIElementDescriptor(
            element_id=CommonUI.BTN_SAVE,
            module="test_module",
            screen="test_screen",
            element_type="button"
        )

        # Register first time
        registry.register(desc)
        items = registry.get_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].element_id, CommonUI.BTN_SAVE)

        # Register exact same descriptor second time
        registry.register(desc)

        # Should still be 1 item, no duplicate
        items_after = registry.get_all()
        self.assertEqual(len(items_after), 1)
        self.assertEqual(items_after[0].element_id, CommonUI.BTN_SAVE)

    def test_registry_metadata_only(self):
        registry = UIElementRegistry.instance()
        desc = UIElementDescriptor(
            element_id="custom_btn",
            module="mod_a",
            screen="scr_b",
            element_type="button"
        )
        registry.register(desc)

        retrieved_desc = registry.get_all()[0]

        self.assertIsInstance(retrieved_desc.element_id, str)
        self.assertIsInstance(retrieved_desc.module, str)
        self.assertIsInstance(retrieved_desc.screen, str)
        self.assertIsInstance(retrieved_desc.element_type, str)

        # Ensure it's exactly the dataclass with no extra properties
        self.assertFalse(hasattr(retrieved_desc, 'widget'))
        self.assertFalse(hasattr(retrieved_desc, 'state'))

    def test_registry_clear(self):
        registry = UIElementRegistry.instance()
        desc = UIElementDescriptor(
            element_id="btn_1",
            module="mod_1",
            screen="scr_1",
            element_type="button"
        )
        registry.register(desc)

        self.assertEqual(len(registry.get_all()), 1)

        registry.clear()

        self.assertEqual(len(registry.get_all()), 0)

if __name__ == '__main__':
    unittest.main()
