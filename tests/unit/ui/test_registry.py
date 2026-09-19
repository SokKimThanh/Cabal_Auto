import pytest
import logging
from lib.events.ui_element_registry import UIElementRegistry, UIElementDescriptor, CommonUI

@pytest.fixture
def registry():
    reg = UIElementRegistry()
    reg.clear()
    return reg

def test_singleton_pattern():
    reg1 = UIElementRegistry()
    reg2 = UIElementRegistry()
    assert reg1 is reg2

def test_register_and_get_all(registry):
    desc1 = UIElementDescriptor(element_id=CommonUI.BTN_SAVE, module="mod1", screen="screen1", element_type="button")
    desc2 = UIElementDescriptor(element_id=CommonUI.BTN_CANCEL, module="mod2", screen="screen2", element_type="button")

    registry.register(desc1)
    registry.register(desc2)

    all_elements = registry.get_all()
    assert len(all_elements) == 2
    assert desc1 in all_elements
    assert desc2 in all_elements

def test_register_duplicate(registry, caplog):
    desc1 = UIElementDescriptor(element_id="test_id", module="mod1", screen="screen1", element_type="button")
    desc2 = UIElementDescriptor(element_id="test_id", module="mod1", screen="screen1", element_type="label")

    with caplog.at_level(logging.WARNING):
        registry.register(desc1)
        registry.register(desc2)

    assert "Duplicate registration: ('mod1', 'screen1', 'test_id')" in caplog.text

    all_elements = registry.get_all()
    assert len(all_elements) == 1
    assert all_elements[0].element_type == "label"

def test_clear(registry):
    desc = UIElementDescriptor(element_id="test", module="mod", screen="scr", element_type="type")
    registry.register(desc)

    assert len(registry.get_all()) == 1
    registry.clear()
    assert len(registry.get_all()) == 0

def test_common_ui_enum():
    assert CommonUI.BTN_SAVE.value == "btn_save"
    assert CommonUI.BTN_CANCEL.value == "btn_cancel"
    assert isinstance(CommonUI.BTN_SAVE, str)
