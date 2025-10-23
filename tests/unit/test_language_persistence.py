"""
Test Language Persistence in Setup Wizard
------------------------------------------
Tests that language selection is preserved when navigating:
- Next → Back → language remains
- Change language → Next → Back → language remains

Bug Fixed: Previously, language_var was reset to 'en' every time
Step 1 was rebuilt, causing language to revert when navigating back.

Solution: Use self.language to restore language_var value when
rebuilding Step 1.
"""

import pytest
import tkinter as tk
from pathlib import Path
import json
import sys

# Mark as Windows-only and GUI test (requires ctypes.wintypes and display)
pytestmark = [pytest.mark.windows, pytest.mark.gui]

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.setup_wizard import SetupWizard


def setup_first_time_config():
    """Create an incomplete config to simulate first-time user."""
    config_path = project_root / 'lib' / 'data' / 'hunt_config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create incomplete config (missing required fields)
    incomplete_config = {
        "version": "1.0",
        "window_title": "",
        "monster_list": [],
        "skill_slots": []
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(incomplete_config, f, indent=2)
    
    print(f"✅ Created first-time config at: {config_path}")
    return config_path


def test_language_persistence():
    """Test language persistence when navigating through wizard steps."""
    print("\n" + "="*70)
    print("TEST: Language Persistence During Navigation")
    print("="*70)
    
    # Setup first-time config
    setup_first_time_config()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: Language Persistence")
    root.geometry("800x700")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "🧪 TEST SCENARIO: Language Persistence\n\n"
            "This test verifies that language selection is preserved when\n"
            "navigating back and forth between wizard steps.\n\n"
            "📋 Test Steps:\n"
            "1. Open wizard (should start in English)\n"
            "2. Select Vietnamese (🇻🇳 Tiếng Việt)\n"
            "3. Verify all texts update to Vietnamese\n"
            "4. Click 'Next →' to go to Step 2\n"
            "5. Click '← Back' to return to Step 1\n"
            "6. ✅ VERIFY: Language is still Vietnamese (NOT reset to English)\n"
            "7. Select English (🇬🇧 English)\n"
            "8. Verify all texts update to English\n"
            "9. Click 'Next →' to go to Step 2\n"
            "10. Click '← Back' to return to Step 1\n"
            "11. ✅ VERIFY: Language is still English\n"
            "12. Repeat steps 4-11 multiple times\n\n"
            "❌ BUG (Before Fix):\n"
            "Language always resets to English when returning to Step 1\n\n"
            "✅ EXPECTED (After Fix):\n"
            "Language persists across navigation - selected language remains"
        ),
        justify='left',
        bg='#e7f3ff',
        fg='#004085',
        padx=20,
        pady=20,
        font=('Arial', 10),
        relief='solid',
        borderwidth=1
    )
    instructions.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Status label
    status_label = tk.Label(
        root,
        text="Status: Ready to test",
        font=('Arial', 11, 'bold'),
        bg='#ffc107',
        fg='#000',
        pady=10
    )
    status_label.pack(fill='x')
    
    def open_wizard():
        """Open the setup wizard."""
        status_label.config(
            text="Status: Wizard opened - Follow test steps above",
            bg='#28a745',
            fg='white'
        )
        wizard = SetupWizard(root, on_complete=lambda cfg: on_wizard_complete(cfg))
    
    def on_wizard_complete(config):
        """Handle wizard completion."""
        lang = config.get('language', 'unknown')
        status_label.config(
            text=f"Status: Wizard completed - Final language: {lang}",
            bg='#17a2b8',
            fg='white'
        )
        print(f"✅ Wizard completed with language: {lang}")
    
    # Button to open wizard
    open_btn = tk.Button(
        root,
        text="🚀 Open Setup Wizard - Test Language Persistence",
        command=open_wizard,
        font=('Arial', 12, 'bold'),
        bg='#007bff',
        fg='white',
        padx=20,
        pady=15,
        relief='raised',
        bd=3
    )
    open_btn.pack(pady=20)
    
    # Quick reference
    quick_ref = tk.Label(
        root,
        text=(
            "🔍 Quick Reference:\n"
            "• Language should PERSIST when clicking Next → Back\n"
            "• User level should PERSIST when clicking Next → Back\n"
            "• Test both EN → VI and VI → EN transitions\n"
            "• Test multiple navigation cycles"
        ),
        justify='left',
        bg='#f8f9fa',
        fg='#495057',
        padx=15,
        pady=10,
        font=('Arial', 9),
        relief='solid',
        borderwidth=1
    )
    quick_ref.pack(fill='x', padx=20, pady=(0, 20))
    
    root.mainloop()


def test_user_level_persistence():
    """Test user level persistence when navigating through wizard steps."""
    print("\n" + "="*70)
    print("TEST: User Level Persistence During Navigation")
    print("="*70)
    
    # Setup first-time config
    setup_first_time_config()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: User Level Persistence")
    root.geometry("800x700")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "🧪 TEST SCENARIO: User Level Persistence\n\n"
            "This test verifies that user level selection is preserved when\n"
            "navigating back and forth between wizard steps.\n\n"
            "📋 Test Steps:\n"
            "1. Open wizard (should start with 'New User' selected)\n"
            "2. Keep 'New User' selected\n"
            "3. Click 'Next →' to go to Step 2\n"
            "4. Click '← Back' to return to Step 1\n"
            "5. ✅ VERIFY: 'New User' is still selected\n"
            "6. Note: 'Experienced User' should be locked (first-time user)\n\n"
            "❌ BUG (Before Fix):\n"
            "User level always resets to 'New User' when returning to Step 1\n"
            "(This was not visible as a bug since 'New User' is the default,\n"
            "but the variable was being recreated unnecessarily)\n\n"
            "✅ EXPECTED (After Fix):\n"
            "User level persists - 'New User' remains selected"
        ),
        justify='left',
        bg='#d4edda',
        fg='#155724',
        padx=20,
        pady=20,
        font=('Arial', 10),
        relief='solid',
        borderwidth=1
    )
    instructions.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Status label
    status_label = tk.Label(
        root,
        text="Status: Ready to test",
        font=('Arial', 11, 'bold'),
        bg='#ffc107',
        fg='#000',
        pady=10
    )
    status_label.pack(fill='x')
    
    def open_wizard():
        """Open the setup wizard."""
        status_label.config(
            text="Status: Wizard opened - Follow test steps above",
            bg='#28a745',
            fg='white'
        )
        wizard = SetupWizard(root, on_complete=lambda cfg: on_wizard_complete(cfg))
    
    def on_wizard_complete(config):
        """Handle wizard completion."""
        level = config.get('user_level', 'unknown')
        status_label.config(
            text=f"Status: Wizard completed - Final user level: {level}",
            bg='#17a2b8',
            fg='white'
        )
        print(f"✅ Wizard completed with user level: {level}")
    
    # Button to open wizard
    open_btn = tk.Button(
        root,
        text="🚀 Open Setup Wizard - Test User Level Persistence",
        command=open_wizard,
        font=('Arial', 12, 'bold'),
        bg='#28a745',
        fg='white',
        padx=20,
        pady=15,
        relief='raised',
        bd=3
    )
    open_btn.pack(pady=20)
    
    root.mainloop()


def show_menu():
    """Show test menu."""
    root = tk.Tk()
    root.title("Language & User Level Persistence Tests")
    root.geometry("700x500")
    
    # Header
    header = tk.Label(
        root,
        text="🧪 Setup Wizard Persistence Tests",
        font=('Arial', 16, 'bold'),
        bg='#343a40',
        fg='white',
        pady=15
    )
    header.pack(fill='x')
    
    # Description
    desc = tk.Label(
        root,
        text=(
            "These tests verify that wizard state persists correctly\n"
            "when navigating between steps using Next/Back buttons.\n\n"
            "Bug Fixed: language_var and user_level_var were being\n"
            "reset to default values every time Step 1 was rebuilt."
        ),
        font=('Arial', 11),
        justify='center',
        pady=20
    )
    desc.pack()
    
    # Test buttons frame
    buttons_frame = tk.Frame(root)
    buttons_frame.pack(expand=True, fill='both', padx=30, pady=10)
    
    # Test 1 button
    btn1 = tk.Button(
        buttons_frame,
        text=(
            "1️⃣ Test Language Persistence\n\n"
            "Change language → Next → Back\n"
            "Verify language doesn't reset"
        ),
        command=lambda: [root.destroy(), test_language_persistence()],
        font=('Arial', 11),
        bg='#007bff',
        fg='white',
        padx=20,
        pady=20,
        justify='center',
        relief='raised',
        bd=3
    )
    btn1.pack(fill='x', pady=10)
    
    # Test 2 button
    btn2 = tk.Button(
        buttons_frame,
        text=(
            "2️⃣ Test User Level Persistence\n\n"
            "Select user level → Next → Back\n"
            "Verify selection doesn't reset"
        ),
        command=lambda: [root.destroy(), test_user_level_persistence()],
        font=('Arial', 11),
        bg='#28a745',
        fg='white',
        padx=20,
        pady=20,
        justify='center',
        relief='raised',
        bd=3
    )
    btn2.pack(fill='x', pady=10)
    
    # Exit button
    exit_btn = tk.Button(
        buttons_frame,
        text="❌ Exit Tests",
        command=root.destroy,
        font=('Arial', 11),
        bg='#dc3545',
        fg='white',
        padx=20,
        pady=15,
        relief='raised',
        bd=3
    )
    exit_btn.pack(fill='x', pady=20)
    
    root.mainloop()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("SETUP WIZARD PERSISTENCE TEST SUITE")
    print("="*70)
    print("\nTests that wizard state persists when navigating between steps.")
    print("Bug: language_var and user_level_var were reset on Step 1 rebuild.")
    print("Fix: Restore from self.language and self.user_level.\n")
    
    show_menu()
