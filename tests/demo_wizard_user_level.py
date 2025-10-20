# -*- coding: utf-8 -*-
"""
Quick Visual Test - User Level and Rotation Builder Button
Shows both scenarios side by side
"""

import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.setup_wizard import SetupWizard


def test_wizard_scenarios():
    """Launch two wizards to show both scenarios."""
    root = tk.Tk()
    root.title("Setup Wizard - User Level Test")
    root.geometry("600x400")
    
    info_frame = tk.Frame(root, bg='#E3F2FD', padx=30, pady=30)
    info_frame.pack(fill='both', expand=True)
    
    title = tk.Label(
        info_frame,
        text="Setup Wizard - User Level Integration Test",
        font=('Arial', 16, 'bold'),
        bg='#E3F2FD'
    )
    title.pack(pady=(0, 20))
    
    instructions = tk.Label(
        info_frame,
        text=(
            "This test demonstrates the new user level feature:\n\n"
            "1. Click 'Launch Wizard' below\n"
            "2. In Step 1: Try both user level options\n"
            "   • 🌱 New User\n"
            "   • ⚙️ Experienced User\n\n"
            "3. Navigate to Step 4 (Skills)\n"
            "4. Observe the rotation builder button:\n"
            "   • ENABLED (blue) for New Users\n"
            "   • DISABLED (gray) for Experienced Users\n\n"
            "5. When enabled, click it to open Library Manager!"
        ),
        font=('Arial', 10),
        bg='#E3F2FD',
        justify=tk.LEFT
    )
    instructions.pack(pady=(0, 30))
    
    def launch_wizard():
        wizard = SetupWizard(
            root,
            on_complete=lambda data: print("Wizard completed:", data),
            on_cancel=lambda: print("Wizard cancelled")
        )
    
    launch_btn = tk.Button(
        info_frame,
        text="🧙 Launch Setup Wizard",
        command=launch_wizard,
        font=('Arial', 14, 'bold'),
        bg='#4CAF50',
        fg='white',
        padx=30,
        pady=15,
        cursor='hand2'
    )
    launch_btn.pack()
    
    notes = tk.Label(
        info_frame,
        text=(
            "\n💡 Key Features:\n"
            "• User level selection in Step 1\n"
            "• Dynamic button state based on selection\n"
            "• Integration with Library Manager\n"
            "• Full English + Vietnamese support"
        ),
        font=('Arial', 9, 'italic'),
        bg='#E3F2FD',
        fg='#666',
        justify=tk.LEFT
    )
    notes.pack(pady=(20, 0))
    
    root.mainloop()


if __name__ == "__main__":
    print("=" * 60)
    print("SETUP WIZARD - USER LEVEL & ROTATION BUILDER TEST")
    print("=" * 60)
    print("\nFeatures to test:")
    print("  ✓ User level selection (New User / Experienced User)")
    print("  ✓ Dynamic button enable/disable")
    print("  ✓ Library Manager integration")
    print("  ✓ Skill data refresh")
    print("\nLaunching test window...")
    print("=" * 60)
    
    test_wizard_scenarios()
