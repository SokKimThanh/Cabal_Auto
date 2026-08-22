"""Demo: Save button tooltip changes with unsaved state."""
import tkinter as tk
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

try:
    from ui.helpers.tooltip import attach_i18n_tooltip
    from lib.i18n import register_bulk
    from lib.i18n.translations import LIBRARY_MANAGER_TRANSLATIONS
except Exception as e:
    print(f"Failed to import: {e}")
    sys.exit(1)

# Register translations
register_bulk('library_manager', LIBRARY_MANAGER_TRANSLATIONS)

class TooltipDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Save Button Tooltip Demo")
        self.root.geometry("500x300")
        
        self.lang = 'vi'
        self.has_unsaved = False
        
        # Title
        title = tk.Label(
            self.root,
            text="Demo: Tooltip thay đổi theo trạng thái lưu",
            font=('Arial', 14, 'bold'),
            pady=20
        )
        title.pack()
        
        # State indicator
        self.state_label = tk.Label(
            self.root,
            text="Trạng thái: ✅ Đã lưu",
            font=('Arial', 12),
            bg='#E8F5E9',
            fg='#2E7D32',
            padx=20,
            pady=10
        )
        self.state_label.pack(pady=10)
        
        # Save button
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        self.save_btn = tk.Button(
            btn_frame,
            text="💾",
            font=('Arial', 24),
            bg='#1976D2',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.save_changes
        )
        self.save_btn.pack()
        
        # Initial tooltip
        self._update_tooltip()
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text=(
                "Hướng dẫn:\n"
                "1. Hover vào nút 💾 để xem tooltip\n"
                "2. Click nút bên dưới để thay đổi trạng thái\n"
                "3. Hover lại để thấy tooltip đã thay đổi"
            ),
            font=('Arial', 10),
            fg='#666',
            justify='left'
        )
        instructions.pack(pady=10)
        
        # Toggle button
        toggle_btn = tk.Button(
            self.root,
            text="🔄 Thay đổi trạng thái (Unsaved ↔ Saved)",
            font=('Arial', 10),
            command=self.toggle_state,
            padx=10,
            pady=5
        )
        toggle_btn.pack(pady=10)
        
        # Language toggle
        lang_btn = tk.Button(
            self.root,
            text="🌐 Switch Language (VI ↔ EN)",
            font=('Arial', 10),
            command=self.toggle_language,
            padx=10,
            pady=5
        )
        lang_btn.pack()
        
    def _update_tooltip(self):
        """Update tooltip based on current state."""
        # Unbind old tooltip
        try:
            self.save_btn.unbind('<Enter>')
            self.save_btn.unbind('<Leave>')
            self.save_btn.unbind('<ButtonPress>')
        except Exception:
            pass
        
        # Determine key
        tooltip_key = 'tip_apply_all_unsaved' if self.has_unsaved else 'tip_apply_all_saved'
        
        # Attach new tooltip
        attach_i18n_tooltip(
            self.save_btn,
            key=tooltip_key,
            ns='library_manager',
            lang_provider=lambda: self.lang
        )
    
    def toggle_state(self):
        """Toggle between saved and unsaved state."""
        self.has_unsaved = not self.has_unsaved
        
        if self.has_unsaved:
            self.state_label.config(
                text="Trạng thái: ⚠️ Chưa lưu" if self.lang == 'vi' else "State: ⚠️ Unsaved",
                bg='#FFF3E0',
                fg='#E65100'
            )
        else:
            self.state_label.config(
                text="Trạng thái: ✅ Đã lưu" if self.lang == 'vi' else "State: ✅ Saved",
                bg='#E8F5E9',
                fg='#2E7D32'
            )
        
        # Update tooltip
        self._update_tooltip()
        
        print(f"State changed to: {'UNSAVED' if self.has_unsaved else 'SAVED'}")
    
    def save_changes(self):
        """Simulate saving changes."""
        if self.has_unsaved:
            self.has_unsaved = False
            self.state_label.config(
                text="Trạng thái: ✅ Đã lưu" if self.lang == 'vi' else "State: ✅ Saved",
                bg='#E8F5E9',
                fg='#2E7D32'
            )
            self._update_tooltip()
            print("Changes saved!")
        else:
            print("No changes to save")
    
    def toggle_language(self):
        """Toggle between Vietnamese and English."""
        self.lang = 'en' if self.lang == 'vi' else 'vi'
        
        # Update state label
        if self.has_unsaved:
            self.state_label.config(
                text="State: ⚠️ Unsaved" if self.lang == 'en' else "Trạng thái: ⚠️ Chưa lưu"
            )
        else:
            self.state_label.config(
                text="State: ✅ Saved" if self.lang == 'en' else "Trạng thái: ✅ Đã lưu"
            )
        
        # Update tooltip (language change)
        self._update_tooltip()
        
        print(f"Language changed to: {self.lang.upper()}")
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    print("=" * 60)
    print("SAVE BUTTON DYNAMIC TOOLTIP DEMO")
    print("=" * 60)
    print("\nStarting demo window...")
    print("Hover over 💾 button to see tooltip change based on state")
    print("=" * 60)
    
    demo = TooltipDemo()
    demo.run()
