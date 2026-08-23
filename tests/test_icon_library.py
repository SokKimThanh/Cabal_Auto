from ui.icon_library import register_icons, Icons
from ui.helpers.icon_helper import IconHelper

def test_register_icons():
    helper = IconHelper()
    register_icons(helper)

    assert Icons.SCAN_SCREEN in helper.icon_map
    assert Icons.SCAN_FAILED in helper.icon_map
    assert Icons.SCAN_COMPLETE in helper.icon_map
    assert Icons.SCANNING in helper.icon_map

    assert helper.icon_map[Icons.SCAN_SCREEN][0] == 'scan-screen.ico'
