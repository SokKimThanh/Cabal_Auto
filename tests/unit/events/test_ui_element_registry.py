import pytest
import logging
from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor, CommonUI

@pytest.fixture(autouse=True)
def setup_registry():
    registry = UIElementRegistry()
    registry.clear()
    yield registry
    registry.clear()

def test_singleton_pattern():
    reg1 = UIElementRegistry()
    reg2 = UIElementRegistry()
    assert reg1 is reg2

def test_register_and_get_all(setup_registry):
    desc1 = UIElementDescriptor(element_id="btn_test_1", module="mod_a", screen="scr_a", element_type="button")
    desc2 = UIElementDescriptor(element_id="btn_test_2", module="mod_a", screen="scr_a", element_type="button")

    setup_registry.register(desc1)
    setup_registry.register(desc2)

    all_elements = setup_registry.get_all()
    assert len(all_elements) == 2
    assert desc1 in all_elements
    assert desc2 in all_elements

def test_duplicate_registration(setup_registry, caplog):
    desc1 = UIElementDescriptor(element_id="btn_test_1", module="mod_a", screen="scr_a", element_type="button")
    desc_dup = UIElementDescriptor(element_id="btn_test_1", module="mod_a", screen="scr_a", element_type="label")

    with caplog.at_level(logging.WARNING):
        setup_registry.register(desc1)
        setup_registry.register(desc_dup)

    # Should only contain one element (overwritten)
    all_elements = setup_registry.get_all()
    assert len(all_elements) == 1
    assert all_elements[0].element_type == "label"

    # Should log warning
    assert "[UIRegistry] Duplicate registration: mod_a/scr_a/btn_test_1" in caplog.text

def test_clear(setup_registry):
    desc1 = UIElementDescriptor(element_id="btn_test_1", module="mod_a", screen="scr_a", element_type="button")
    setup_registry.register(desc1)

    assert len(setup_registry.get_all()) == 1
    setup_registry.clear()
    assert len(setup_registry.get_all()) == 0

def test_common_ui_enum():
    assert CommonUI.BTN_SAVE == "btn_save"
    assert CommonUI.BTN_CANCEL == "btn_cancel"
    assert isinstance(CommonUI.BTN_SAVE, str)
