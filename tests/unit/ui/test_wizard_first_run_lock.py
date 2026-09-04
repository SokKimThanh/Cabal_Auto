import pytest
pytest.importorskip('tkinter')
"""
Test Setup Wizard First-Run Lock Feature
-----------------------------------------
Tests that the "Experienced User" option is:
1. Locked (disabled) for first-time users
2. Available for returning users
3. Updates correctly when language is changed

Test scenarios:
- Scenario 1: First-time user (empty/incomplete hunt_config.json)
- Scenario 2: Returning user (complete hunt_config.json)
- Scenario 3: Language switching with locked option
- Scenario 4: Language switching with unlocked option
"""

import pytest
import tkinter as tk
from pathlib import Path
import json
import sys

# Mark as Windows-only and GUI test (requires ctypes.wintypes and display)
pytestmark = [pytest.mark.windows, pytest.mark.gui]

if sys.platform != "win32":
    pytest.skip("Requires Windows environment", allow_module_level=True)

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
        "window_title": "",  # Empty - triggers first-run detection
        "monster_list": [],   # Empty - triggers first-run detection
        "skill_slots": []     # Empty - triggers first-run detection
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(incomplete_config, f, indent=2)
    
    print(f"✅ Created incomplete config at: {config_path}")
    return config_path


def setup_returning_user_config():
    """Create a complete config to simulate returning user."""
    config_path = project_root / 'lib' / 'data' / 'hunt_config.json'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create complete config
    complete_config = {
        "version": "1.0",
        "window_title": "CABAL Online",
        "monster_list": ["Dummy Monster"],
        "skill_slots": [
            {"slot": 1, "name": "Skill 1", "key": "1"},
            {"slot": 2, "name": "Skill 2", "key": "2"}
        ]
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(complete_config, f, indent=2)
    
    print(f"✅ Created complete config at: {config_path}")
    return config_path


def test_scenario_1_first_time_user():
    """Test Scenario 1: First-time user sees locked 'Experienced User' option."""
    print("\n" + "="*70)
    print("SCENARIO 1: First-Time User (Locked 'Experienced User' Option)")
    print("="*70)
    
    # Setup first-time config
    setup_first_time_config()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: First-Time User - Locked Option")
    root.geometry("700x600")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "TEST SCENARIO 1: First-Time User\n\n"
            "Expected Behavior:\n"
            "✓ 'Experienced User' radio button should be DISABLED (grayed out)\n"
            "✓ Hint label should show: 'First-time users must start with New User option'\n"
            "✓ Only 'New User' should be selectable\n\n"
            "Actions to Test:\n"
            "1. Verify 'Experienced User' is disabled\n"
            "2. Try clicking it (should not work)\n"
            "3. Check hint label is visible\n"
            "4. Click 'Open Wizard' button below"
        ),
        justify='left',
        bg='#fff3cd',
        fg='#856404',
        padx=20,
        pady=15,
        font=('Arial', 10)
    )
    instructions.pack(fill='x', padx=10, pady=10)
    
    def open_wizard():
        """Open the setup wizard."""
        wizard = SetupWizard(root, on_complete=lambda cfg: print(f"Config saved: {cfg}"))
    
    # Button to open wizard
    open_btn = tk.Button(
        root,
        text="🚀 Open Setup Wizard (First-Time User)",
        command=open_wizard,
        font=('Arial', 12, 'bold'),
        bg='#007bff',
        fg='white',
        padx=20,
        pady=10
    )
    open_btn.pack(pady=20)
    
    root.mainloop()


def test_scenario_2_returning_user():
    """Test Scenario 2: Returning user sees unlocked 'Experienced User' option."""
    print("\n" + "="*70)
    print("SCENARIO 2: Returning User (Unlocked 'Experienced User' Option)")
    print("="*70)
    
    # Setup returning user config
    setup_returning_user_config()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: Returning User - Unlocked Option")
    root.geometry("700x600")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "TEST SCENARIO 2: Returning User\n\n"
            "Expected Behavior:\n"
            "✓ 'Experienced User' radio button should be ENABLED (clickable)\n"
            "✓ No hint label about first-time restriction\n"
            "✓ Both 'New User' and 'Experienced User' are selectable\n\n"
            "Actions to Test:\n"
            "1. Verify 'Experienced User' is enabled\n"
            "2. Try selecting both options\n"
            "3. Check no restriction hint is shown\n"
            "4. Click 'Open Wizard' button below"
        ),
        justify='left',
        bg='#d4edda',
        fg='#155724',
        padx=20,
        pady=15,
        font=('Arial', 10)
    )
    instructions.pack(fill='x', padx=10, pady=10)
    
    def open_wizard():
        """Open the setup wizard."""
        wizard = SetupWizard(root, on_complete=lambda cfg: print(f"Config saved: {cfg}"))
    
    # Button to open wizard
    open_btn = tk.Button(
        root,
        text="🚀 Open Setup Wizard (Returning User)",
        command=open_wizard,
        font=('Arial', 12, 'bold'),
        bg='#28a745',
        fg='white',
        padx=20,
        pady=10
    )
    open_btn.pack(pady=20)
    
    root.mainloop()


def test_scenario_3_language_switching_locked():
    """Test Scenario 3: Language switching with locked option."""
    print("\n" + "="*70)
    print("SCENARIO 3: Language Switching (First-Time User - Locked)")
    print("="*70)
    
    # Setup first-time config
    setup_first_time_config()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: Language Switching - First-Time User")
    root.geometry("700x600")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "TEST SCENARIO 3: Language Switching (First-Time User)\n\n"
            "Expected Behavior:\n"
            "✓ When switching to Vietnamese:\n"
            "  - 'New User' → '🌱 Người mới'\n"
            "  - 'Experienced User' → '⚙️ Người có kinh nghiệm' (DISABLED)\n"
            "  - Hint → 'Người dùng lần đầu phải bắt đầu với tùy chọn Người mới'\n"
            "✓ Radio button tooltips update to Vietnamese\n"
            "✓ Description texts update to Vietnamese\n\n"
            "Actions to Test:\n"
            "1. Open wizard and note English texts\n"
            "2. Switch language to Vietnamese (🇻🇳)\n"
            "3. Verify all texts in Step 1 update to Vietnamese\n"
            "4. Hover over radio buttons to check tooltip language\n"
            "5. Switch back to English and verify texts update"
        ),
        justify='left',
        bg='#d1ecf1',
        fg='#0c5460',
        padx=20,
        pady=15,
        font=('Arial', 10)
    )
    instructions.pack(fill='x', padx=10, pady=10)
    
    def open_wizard():
        """Open the setup wizard."""
        wizard = SetupWizard(root, on_complete=lambda cfg: print(f"Config saved: {cfg}"))
    
    # Button to open wizard
    open_btn = tk.Button(
        root,
        text="🚀 Open Wizard - Test Language Switching (Locked)",
        command=open_wizard,
        font=('Arial', 12, 'bold'),
        bg='#17a2b8',
        fg='white',
        padx=20,
        pady=10
    )
    open_btn.pack(pady=20)
    
    root.mainloop()


def test_scenario_4_language_switching_unlocked():
    """Test Scenario 4: Language switching with unlocked option."""
    print("\n" + "="*70)
    print("SCENARIO 4: Language Switching (Returning User - Unlocked)")
    print("="*70)
    
    # Setup returning user config
    setup_returning_user_config()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: Language Switching - Returning User")
    root.geometry("700x600")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "TEST SCENARIO 4: Language Switching (Returning User)\n\n"
            "Expected Behavior:\n"
            "✓ When switching to Vietnamese:\n"
            "  - 'New User' → '🌱 Người mới'\n"
            "  - 'Experienced User' → '⚙️ Người có kinh nghiệm' (ENABLED)\n"
            "  - No first-time restriction hint\n"
            "✓ Radio button tooltips update to Vietnamese\n"
            "✓ Description texts update to Vietnamese\n"
            "✓ Both options remain selectable\n\n"
            "Actions to Test:\n"
            "1. Open wizard and note English texts\n"
            "2. Switch language to Vietnamese (🇻🇳)\n"
            "3. Verify all texts update to Vietnamese\n"
            "4. Try selecting 'Người có kinh nghiệm' (should work)\n"
            "5. Hover over radio buttons to check tooltip language\n"
            "6. Switch back to English and verify texts update"
        ),
        justify='left',
        bg='#d4edda',
        fg='#155724',
        padx=20,
        pady=15,
        font=('Arial', 10)
    )
    instructions.pack(fill='x', padx=10, pady=10)
    
    def open_wizard():
        """Open the setup wizard."""
        wizard = SetupWizard(root, on_complete=lambda cfg: print(f"Config saved: {cfg}"))
    
    # Button to open wizard
    open_btn = tk.Button(
        root,
        text="🚀 Open Wizard - Test Language Switching (Unlocked)",
        command=open_wizard,
        font=('Arial', 12, 'bold'),
        bg='#28a745',
        fg='white',
        padx=20,
        pady=10
    )
    open_btn.pack(pady=20)
    
    root.mainloop()


def show_menu():
    """Show test scenario selection menu."""
    root = tk.Tk()
    root.title("Setup Wizard First-Run Lock - Test Menu")
    root.geometry("800x650")
    
    # Header
    header = tk.Label(
        root,
        text="🧪 Setup Wizard First-Run Lock - Test Suite",
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
            "This test suite verifies the first-time user lock feature.\n"
            "Select a test scenario to run:\n"
        ),
        font=('Arial', 11),
        justify='center',
        pady=10
    )
    desc.pack()
    
    # Test buttons frame
    buttons_frame = tk.Frame(root)
    buttons_frame.pack(expand=True, fill='both', padx=30, pady=10)
    
    # Scenario 1 button
    btn1 = tk.Button(
        buttons_frame,
        text="1️⃣ First-Time User (Locked Option)\n\nTests that 'Experienced User' is disabled for new users",
        command=lambda: [root.destroy(), test_scenario_1_first_time_user()],
        font=('Arial', 11),
        bg='#ffc107',
        fg='#000',
        padx=20,
        pady=20,
        justify='center',
        relief='raised',
        bd=3
    )
    btn1.pack(fill='x', pady=10)
    
    # Scenario 2 button
    btn2 = tk.Button(
        buttons_frame,
        text="2️⃣ Returning User (Unlocked Option)\n\nTests that 'Experienced User' is enabled for returning users",
        command=lambda: [root.destroy(), test_scenario_2_returning_user()],
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
    
    # Scenario 3 button
    btn3 = tk.Button(
        buttons_frame,
        text="3️⃣ Language Switching (First-Time User)\n\nTests that UI texts update when language changes (with lock)",
        command=lambda: [root.destroy(), test_scenario_3_language_switching_locked()],
        font=('Arial', 11),
        bg='#17a2b8',
        fg='white',
        padx=20,
        pady=20,
        justify='center',
        relief='raised',
        bd=3
    )
    btn3.pack(fill='x', pady=10)
    
    # Scenario 4 button
    btn4 = tk.Button(
        buttons_frame,
        text="4️⃣ Language Switching (Returning User)\n\nTests that UI texts update when language changes (without lock)",
        command=lambda: [root.destroy(), test_scenario_4_language_switching_unlocked()],
        font=('Arial', 11),
        bg='#6f42c1',
        fg='white',
        padx=20,
        pady=20,
        justify='center',
        relief='raised',
        bd=3
    )
    btn4.pack(fill='x', pady=10)
    
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
    print("SETUP WIZARD FIRST-RUN LOCK TEST SUITE")
    print("="*70)
    print("\nThis test suite verifies:")
    print("  1. First-time users see locked 'Experienced User' option")
    print("  2. Returning users can select 'Experienced User'")
    print("  3. Language switching updates all UI texts correctly")
    print("  4. Tooltips update with language changes")
    print("\nStarting test menu...")
    
    show_menu()
