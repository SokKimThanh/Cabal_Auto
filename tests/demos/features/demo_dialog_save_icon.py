"""Quick Demo: Dialog Save Icons

Shows MonsterDialog and SkillDialog save button with icon.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from ui.windows.library_manager import MonsterDialog
from ui.helpers.icon_helper import get_icon_helper
from lib.i18n import t as i18n_t

def main():
    print("=" * 60)
    print("Demo: MonsterDialog Save Icon")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Dialog will open with save button")
    print("2. Check if button shows disk icon (not 💾 emoji)")
    print("3. Hover over save button to see tooltip")
    print("4. EN tooltip: 'Save monster'")
    print("5. VI tooltip: 'Lưu quái'")
    print("=" * 60 + "\n")
    
    root = tk.Tk()
    root.withdraw()
    
    icon_helper = get_icon_helper()
    
    print("Opening MonsterDialog in VIETNAMESE...")
    print("Expected: Nút lưu có icon đĩa, tooltip 'Lưu quái'\n")
    
    dialog = MonsterDialog(
        root,
        lang='vi',
        mode='add',
        icon_helper=icon_helper,
        i18n_registry=i18n_t
    )
    
    if dialog.result:
        print(f"\n✅ Monster added: {dialog.result}")
    else:
        print("\nℹ️  Dialog cancelled")
    
    root.destroy()
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()
