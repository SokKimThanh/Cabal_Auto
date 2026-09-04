"""
Test: Skills Loading in Rotation Tab from Setup Wizard
--------------------------------------------------------
Tests that skills appear in the Rotation tab when opened from Setup Wizard.

Bug Fixed: SkillRotationUI was only loading from hunt_config.json, 
which doesn't exist or is incomplete during Setup Wizard flow.

Solution: Load skills from library_manager.skills first (Setup Wizard context),
fallback to hunt_config.json if not available.
"""

import sys
import pytest
from pathlib import Path
import json
import tkinter as tk

# Mark as GUI test requiring Windows
pytestmark = [pytest.mark.gui, pytest.mark.windows]

# Skip on non-Windows platforms
if sys.platform != "win32":
    pytest.skip("Requires Windows environment with GUI", allow_module_level=True)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def setup_test_data():
    """Create test skills data in lib/data/skills.json"""
    skills_path = project_root / 'lib' / 'data' / 'skills.json'
    skills_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create sample skills
    test_skills = [
        {
            "name": "Fireball",
            "key": "1",
            "cooldown": 5,
            "type": "attack",
            "image_path": ""
        },
        {
            "name": "Ice Blast",
            "key": "2",
            "cooldown": 8,
            "type": "attack",
            "image_path": ""
        },
        {
            "name": "Lightning Strike",
            "key": "3",
            "cooldown": 10,
            "type": "attack",
            "image_path": ""
        },
        {
            "name": "Heal",
            "key": "4",
            "cooldown": 15,
            "type": "buff",
            "image_path": ""
        }
    ]
    
    with open(skills_path, 'w', encoding='utf-8') as f:
        json.dump(test_skills, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created test skills at: {skills_path}")
    return test_skills


def test_rotation_tab_from_wizard():
    """Test opening rotation tab with skills from wizard context"""
    print("\n" + "="*70)
    print("TEST: Skills in Rotation Tab (Setup Wizard Context)")
    print("="*70)
    
    # Setup test data
    test_skills = setup_test_data()
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: Rotation Tab Skills from Wizard")
    root.geometry("900x700")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "🧪 TEST SCENARIO: Skills in Rotation Tab from Setup Wizard\n\n"
            "Bug: When opening Library Manager → Rotation tab from Setup Wizard,\n"
            "no skills appear because SkillRotationUI only loaded from\n"
            "hunt_config.json (which doesn't exist during wizard).\n\n"
            "📋 Test Steps:\n"
            "1. Click 'Open Library Manager (Wizard Context)' below\n"
            "2. Library Manager opens with skills loaded from memory\n"
            "3. Go to 'Rotation' / 'Chu Kỳ Chiêu' tab\n"
            "4. ✅ VERIFY: Skills appear in left panel (Available Skills)\n"
            "5. Skills should include: Fireball, Ice Blast, Lightning Strike, Heal\n\n"
            "❌ BUG (Before Fix):\n"
            "Left panel shows: 'No skills found in hunt_config.json'\n\n"
            "✅ EXPECTED (After Fix):\n"
            "Skills load from library_manager.skills and display correctly"
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
    
    def open_library_manager():
        """Simulate opening library manager from wizard context"""
        try:
            from ui.windows.library_manager import LibraryManagerWindow
            
            status_label.config(
                text="Status: Loading Library Manager with test skills...",
                bg='#17a2b8',
                fg='white'
            )
            root.update()
            
            # Mock hunt config
            hunt_cfg = {
                'window_title': 'Test Window',
                'window_pid': None,
                'window_hwnd': None
            }
            
            # Mock monsters (empty for this test)
            monsters = []
            
            # Test skills (loaded from file)
            skills = test_skills
            
            def on_close(changes):
                status_label.config(
                    text=f"Status: Library Manager closed - Skills changed: {changes.get('skills_changed', False)}",
                    bg='#6c757d',
                    fg='white'
                )
                print(f"ℹ️ Library Manager closed with changes: {changes}")
            
            # Create library manager (simulating wizard context)
            lib_manager = LibraryManagerWindow(
                parent=root,
                hunt_cfg=hunt_cfg,
                monsters=monsters,
                skills=skills,  # ← Skills passed from wizard/memory
                lang='en',
                on_close_callback=on_close
            )
            
            status_label.config(
                text="Status: Library Manager opened! Go to Rotation tab to verify skills appear",
                bg='#28a745',
                fg='white'
            )
            print("✅ Library Manager opened with skills from wizard context")
            print(f"   Skills loaded: {len(skills)} items")
            
        except Exception as e:
            status_label.config(
                text=f"Status: Error - {str(e)[:80]}",
                bg='#dc3545',
                fg='white'
            )
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test button
    test_btn = tk.Button(
        root,
        text="🚀 Open Library Manager (Wizard Context)",
        command=open_library_manager,
        font=('Arial', 12, 'bold'),
        bg='#007bff',
        fg='white',
        padx=30,
        pady=15,
        relief='raised',
        bd=3
    )
    test_btn.pack(pady=20)
    
    # Expected result
    expected = tk.Label(
        root,
        text=(
            "✅ Expected Result:\n"
            "• Library Manager opens with 'Rotation' tab\n"
            "• Left panel shows 4 skills (Fireball, Ice Blast, Lightning Strike, Heal)\n"
            "• Skills are loaded from memory (library_manager.skills)\n"
            "• NOT from hunt_config.json (which doesn't exist yet)"
        ),
        justify='left',
        bg='#d4edda',
        fg='#155724',
        padx=15,
        pady=10,
        font=('Arial', 9),
        relief='solid',
        borderwidth=1
    )
    expected.pack(fill='x', padx=20, pady=(0, 20))
    
    print("\nTest window opened. Click 'Open Library Manager' to test.")
    root.mainloop()


def test_rotation_tab_from_app():
    """Test opening rotation tab from main app (normal context)"""
    print("\n" + "="*70)
    print("TEST: Skills in Rotation Tab (Main App Context)")
    print("="*70)
    
    # Setup test data in hunt_config
    hunt_config_path = project_root / 'lib' / 'data' / 'hunt_config.json'
    hunt_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    test_config = {
        "version": "1.0",
        "window_title": "CABAL Online",
        "monster_list": ["Dummy Monster"],
        "skill_slots": [
            {"name": "Slash", "key": "1", "cooldown": 3, "type": "attack"},
            {"name": "Thrust", "key": "2", "cooldown": 5, "type": "attack"},
            {"name": "Defense", "key": "3", "cooldown": 10, "type": "buff"}
        ]
    }
    
    with open(hunt_config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2)
    
    print(f"✅ Created test hunt_config at: {hunt_config_path}")
    
    # Create GUI
    root = tk.Tk()
    root.title("Test: Rotation Tab Skills from Main App")
    root.geometry("900x700")
    
    # Instructions
    instructions = tk.Label(
        root,
        text=(
            "🧪 TEST SCENARIO: Skills in Rotation Tab from Main App\n\n"
            "This tests the fallback mechanism: when library_manager.skills\n"
            "is empty, skills load from hunt_config.json instead.\n\n"
            "📋 Test Steps:\n"
            "1. Click 'Open Library Manager (App Context)' below\n"
            "2. Library Manager opens WITHOUT skills in memory\n"
            "3. Go to 'Rotation' tab\n"
            "4. ✅ VERIFY: Skills appear (loaded from hunt_config.json)\n"
            "5. Skills should include: Slash, Thrust, Defense\n\n"
            "✅ EXPECTED:\n"
            "Skills load from hunt_config.json fallback mechanism"
        ),
        justify='left',
        bg='#fff3cd',
        fg='#856404',
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
    
    def open_library_manager():
        """Simulate opening library manager from main app"""
        try:
            from ui.windows.library_manager import LibraryManagerWindow
            
            status_label.config(
                text="Status: Loading Library Manager (fallback to hunt_config)...",
                bg='#17a2b8',
                fg='white'
            )
            root.update()
            
            # Mock hunt config
            hunt_cfg = test_config.copy()
            
            # Empty skills (simulate main app not passing skills)
            monsters = []
            skills = []  # ← Empty! Should fallback to hunt_config.json
            
            def on_close(changes):
                status_label.config(
                    text=f"Status: Closed - Changes: {changes}",
                    bg='#6c757d',
                    fg='white'
                )
            
            # Create library manager
            lib_manager = LibraryManagerWindow(
                parent=root,
                hunt_cfg=hunt_cfg,
                monsters=monsters,
                skills=skills,  # Empty - triggers fallback
                lang='en',
                on_close_callback=on_close
            )
            
            status_label.config(
                text="Status: Opened! Rotation tab should load from hunt_config.json",
                bg='#28a745',
                fg='white'
            )
            print("✅ Library Manager opened (fallback mode)")
            
        except Exception as e:
            status_label.config(
                text=f"Status: Error - {str(e)[:80]}",
                bg='#dc3545',
                fg='white'
            )
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Test button
    test_btn = tk.Button(
        root,
        text="🚀 Open Library Manager (App Context)",
        command=open_library_manager,
        font=('Arial', 12, 'bold'),
        bg='#28a745',
        fg='white',
        padx=30,
        pady=15,
        relief='raised',
        bd=3
    )
    test_btn.pack(pady=20)
    
    root.mainloop()


def show_menu():
    """Show test menu"""
    root = tk.Tk()
    root.title("Rotation Tab Skills - Test Suite")
    root.geometry("700x550")
    
    # Header
    header = tk.Label(
        root,
        text="🧪 Rotation Tab Skills Loading Tests",
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
            "These tests verify that skills load correctly in Rotation tab\n"
            "from both Setup Wizard context and main app context.\n\n"
            "Bug: Skills weren't appearing when opened from Setup Wizard.\n"
            "Fix: Load from library_manager.skills first, fallback to hunt_config.json."
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
            "1️⃣ Test from Setup Wizard Context\n\n"
            "Skills loaded from memory\n"
            "(library_manager.skills)"
        ),
        command=lambda: [root.destroy(), test_rotation_tab_from_wizard()],
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
            "2️⃣ Test from Main App Context\n\n"
            "Skills loaded from hunt_config.json\n"
            "(fallback mechanism)"
        ),
        command=lambda: [root.destroy(), test_rotation_tab_from_app()],
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
    print("ROTATION TAB SKILLS LOADING TEST SUITE")
    print("="*70)
    print("\nTests that skills load correctly in Rotation tab:")
    print("  1. From Setup Wizard (library_manager.skills)")
    print("  2. From Main App (hunt_config.json fallback)\n")
    
    show_menu()
