# -*- coding: utf-8 -*-
"""
Test Setup Wizard with Skill Rotation Integration
"""

import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.setup_wizard import SetupWizard


class MockConfigManager:
    def __init__(self):
        self.data = {'config': {}, 'hunt_config': {}}
    
    def get(self, category, key, default=None):
        return self.data.get(category, {}).get(key, default)
    
    def set(self, category, key, value):
        if category not in self.data:
            self.data[category] = {}
        self.data[category][key] = value
    
    def save(self):
        print("[MockConfig] Save called")
        import json
        print(json.dumps(self.data, indent=2, ensure_ascii=False))
        return True


def test_setup_wizard():
    root = tk.Tk()
    root.title("Test Setup Wizard - Skill Rotation")
    root.geometry("500x400")
    
    config_mgr = MockConfigManager()
    
    def on_wizard_complete(data):
        print("\nWIZARD COMPLETED!")
        import json
        print(json.dumps(data, indent=2, ensure_ascii=False))
        root.deiconify()
    
    def on_wizard_cancel():
        print("\nWizard cancelled")
        root.deiconify()
    
    info_frame = tk.Frame(root, bg='#E3F2FD', padx=20, pady=20)
    info_frame.pack(fill='both', expand=True)
    
    title = tk.Label(info_frame, text="Setup Wizard - Skill Rotation Test",
                     font=('Arial', 14, 'bold'), bg='#E3F2FD')
    title.pack(pady=20)
    
    launch_btn = tk.Button(info_frame, text="Launch Setup Wizard",
                          command=lambda: SetupWizard(root, config_manager=config_mgr,
                                                     on_complete=on_wizard_complete,
                                                     on_cancel=on_wizard_cancel),
                          font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white',
                          padx=30, pady=15)
    launch_btn.pack()
    
    print("SETUP WIZARD - SKILL ROTATION TEST")
    print("Click button to launch wizard")
    
    root.mainloop()


if __name__ == "__main__":
    test_setup_wizard()