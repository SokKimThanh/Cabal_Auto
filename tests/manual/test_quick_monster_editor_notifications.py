"""
Test QuickMonsterEditor with ActionNotificationMixin integration.

This script opens QuickMonsterEditor to verify:
1. ActionNotificationMixin is properly integrated
2. Notification rules are registered
3. Add/Delete buttons show appropriate notifications
4. Edit mode validation works

Run:
    python tests/manual/test_quick_monster_editor_notifications.py
"""

import pytest
import sys
import tkinter as tk
from pathlib import Path

pytestmark = [
    pytest.mark.manual,
    pytest.mark.gui
]

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ui.windows.quick_monster_editor import QuickMonsterEditor


def main():
    """Test QuickMonsterEditor with notifications."""
    print("="*70)
    print("🎮 QuickMonsterEditor - ActionNotificationMixin Integration Test")
    print("="*70)
    print()
    print("📖 What to Test:")
    print("  1. Click 'Add Monster' in View Mode")
    print("     → Should show warning: 'Please enable Edit Mode first'")
    print()
    print("  2. Toggle to Edit Mode, then click 'Add Monster'")
    print("     → Should add monster + show success notification")
    print()
    print("  3. Select a monster, then click 'Delete' in Edit Mode")
    print("     → Should show confirmation (if has templates)")
    print("     → Then show success notification after delete")
    print()
    print("  4. Try to delete without selection")
    print("     → Should show warning: 'Please select a monster'")
    print()
    print("✨ Key Features:")
    print("  • Button state = Technical condition (enabled/disabled)")
    print("  • Notification = User feedback (info/success/warning/error)")
    print("  • ActionNotificationMixin = Integration layer")
    print()
    print("="*70)
    print()
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide root window
    
    # Open QuickMonsterEditor
    editor = QuickMonsterEditor(root)
    
    # Check if mixin is integrated
    has_mixin = hasattr(editor, 'execute_action')
    print(f"✅ ActionNotificationMixin integrated: {has_mixin}")
    
    if has_mixin:
        # Check if rules are registered
        has_add_rule = editor.has_action_rule('add_monster')
        has_delete_rule = editor.has_action_rule('delete_monster')
        print(f"✅ Add monster rule registered: {has_add_rule}")
        print(f"✅ Delete monster rule registered: {has_delete_rule}")
    else:
        print("⚠️  ActionNotificationMixin not available (using fallback)")
    
    print()
    print("🎯 Editor is now open - try the tests above!")
    print()
    
    # Run event loop
    root.mainloop()


if __name__ == '__main__':
    main()
