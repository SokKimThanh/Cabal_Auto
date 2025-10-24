"""
Test Monster Editor with new icon_button component
"""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).resolve().parents[2]  # tests/manual/* -> project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk

# Now import from ui
from ui.quick_monster_editor import QuickMonsterEditor

def test_monster_editor():
    """Test Monster Editor window with icons."""
    root = tk.Tk()
    root.title("Monster Editor Test")
    root.geometry("1000x700")
    
    # Mock callbacks
    def on_save(data):
        print(f"Save called with data: {data}")
    
    # Create Monster Editor
    editor = QuickMonsterEditor(
        parent=root,
        on_save=on_save
    )
    
    print("Monster Editor created successfully!")
    print(f"Buttons created:")
    print(f"  - Save button: {editor.save_button is not None}")
    print(f"  - Cancel button: {editor.cancel_button is not None}")
    print(f"  - Add button: {editor.add_monster_button is not None}")
    print(f"  - Delete button: {editor.delete_monster_button is not None}")
    print(f"  - Capture button: {editor.capture_button is not None}")
    print(f"  - Browse button: {editor.browse_button is not None}")
    print(f"  - Delete template button: {editor.delete_template_button is not None}")
    print(f"  - Test button: {editor.test_template_button is not None}")
    
    root.mainloop()

if __name__ == '__main__':
    test_monster_editor()
