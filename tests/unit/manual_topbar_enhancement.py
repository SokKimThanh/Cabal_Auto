"""
Test: Window Selection & Hunt Controls - Topbar Enhancement
-------------------------------------------------------------
Demonstrates all new features from Sprint 20 topbar redesign:
- Window selection combobox in topbar
- Auto PID detection when canceling setup
- Auto bring-to-front on window selection
- Start/Stop hunt buttons in topbar
- Auto bring-to-front on app startup

This is a comprehensive test showcasing the complete workflow.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TopbarEnhancementDemo(tk.Tk):
    """Demo app showcasing topbar enhancements."""
    
    def __init__(self):
        super().__init__()
        self.title("🎨 Topbar Enhancement - Demo")
        self.geometry("900x700")
        
        # State
        self.windows = []
        self.selected_window = None
        self.hunt_running = False
        
        self._build_ui()
        
        # Simulate auto bring-to-front on startup
        self.after(1000, self._simulate_startup_bring_to_front)
    
    def _build_ui(self):
        """Build demo UI showing new topbar layout."""
        
        # === TOPBAR (NEW LAYOUT) ===
        topbar = tk.Frame(self, bg='#f5f5f5', padx=10, pady=8, relief='ridge', bd=2)
        topbar.pack(fill='x')
        
        # Language selector
        tk.Label(topbar, text="Language:", bg='#f5f5f5', font=('Arial', 9)).pack(side='left', padx=(0,4))
        lang_combo = ttk.Combobox(topbar, state='readonly', width=10, values=['en', 'vi'])
        lang_combo.current(1)  # Vietnamese
        lang_combo.pack(side='left', padx=(0,12))
        
        # Separator
        tk.Frame(topbar, width=2, bg='#ccc', relief='sunken').pack(side='left', fill='y', padx=8)
        
        # Window selection combobox (NEW!)
        tk.Label(topbar, text="🪟 Game Window:", bg='#f5f5f5', font=('Arial', 9, 'bold')).pack(side='left', padx=(0,4))
        self.win_combo = ttk.Combobox(topbar, state='readonly', width=35)
        self.win_combo.pack(side='left', padx=(0,6))
        self.win_combo.bind('<<ComboboxSelected>>', self._on_window_selected)
        
        # Tooltip indicator
        tooltip_label = tk.Label(topbar, text="ⓘ", bg='#f5f5f5', fg='#666', font=('Arial', 8))
        tooltip_label.pack(side='left', padx=(0,6))
        self._create_tooltip(tooltip_label, 
            "Select your Cabal game window.\n"
            "• Click 'Find Windows' to refresh list\n"
            "• Selected window will auto bring-to-front\n"
            "• Tip: Look for window with PID matching your game process"
        )
        
        # Find Windows button
        tk.Button(topbar, text="🔍 Find Windows", command=self._find_windows, 
                 bg='#2196F3', fg='white', padx=10, pady=4, relief='raised', bd=1).pack(side='left', padx=(0,8))
        
        # Separator before hunt controls
        tk.Frame(topbar, width=2, bg='#ccc', relief='sunken').pack(side='left', fill='y', padx=8)
        
        # START button (NEW LOCATION!)
        self.start_btn = tk.Button(
            topbar,
            text="▶ Start Hunt",
            command=self._start_hunt,
            bg='#2E7D32',
            fg='white',
            activebackground='#1B5E20',
            activeforeground='white',
            font=('Arial', 10, 'bold'),
            padx=16,
            pady=6,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        self.start_btn.pack(side='left', padx=(0,6))
        
        # STOP button (NEW LOCATION!)
        self.stop_btn = tk.Button(
            topbar,
            text="■ Stop Hunt",
            command=self._stop_hunt,
            state='disabled',
            bg='#C62828',
            fg='white',
            activebackground='#B71C1C',
            activeforeground='white',
            disabledforeground='#999',
            font=('Arial', 10, 'bold'),
            padx=16,
            pady=6,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        self.stop_btn.pack(side='left')
        
        # === MAIN CONTENT ===
        content = tk.Frame(self, padx=20, pady=15)
        content.pack(fill='both', expand=True)
        
        # Title
        tk.Label(content, text="✨ Topbar Enhancement Features", 
                font=('Arial', 14, 'bold'), fg='#333').pack(anchor='w', pady=(0,10))
        
        # Feature 1
        feature1 = tk.LabelFrame(content, text="1️⃣ Window Selection in Topbar", 
                                font=('Arial', 11, 'bold'), padx=15, pady=10)
        feature1.pack(fill='x', pady=(0,10))
        
        tk.Label(feature1, text=
            "• Window list changed from Listbox → Combobox\n"
            "• Now in topbar for quick access (no scrolling needed)\n"
            "• Auto-selects window matching saved PID\n"
            "• Includes i18n tooltip for guidance",
            justify='left', font=('Arial', 9)
        ).pack(anchor='w')
        
        # Feature 2
        feature2 = tk.LabelFrame(content, text="2️⃣ Auto PID Detection", 
                                font=('Arial', 11, 'bold'), padx=15, pady=10)
        feature2.pack(fill='x', pady=(0,10))
        
        tk.Label(feature2, text=
            "• Triggered when new user cancels Setup Wizard\n"
            "• Automatically finds Cabal windows\n"
            "• Saves first match PID/HWND to config\n"
            "• Shows confirmation dialog",
            justify='left', font=('Arial', 9)
        ).pack(anchor='w')
        
        btn_frame = tk.Frame(feature2)
        btn_frame.pack(anchor='w', pady=(5,0))
        tk.Button(btn_frame, text="🎬 Demo Auto Detection", 
                 command=self._demo_auto_detection, bg='#4CAF50', fg='white', 
                 padx=10, pady=4).pack(side='left', padx=(0,5))
        
        # Feature 3
        feature3 = tk.LabelFrame(content, text="3️⃣ Auto Bring-to-Front", 
                                font=('Arial', 11, 'bold'), padx=15, pady=10)
        feature3.pack(fill='x', pady=(0,10))
        
        tk.Label(feature3, text=
            "• Window auto brought to front when selected from combobox\n"
            "• No separate 'Bring to Front' button needed\n"
            "• On app startup, saved window auto brought to front after 1s\n"
            "• Status message shows confirmation for 3s",
            justify='left', font=('Arial', 9)
        ).pack(anchor='w')
        
        # Feature 4
        feature4 = tk.LabelFrame(content, text="4️⃣ Hunt Controls in Topbar", 
                                font=('Arial', 11, 'bold'), padx=15, pady=10)
        feature4.pack(fill='x', pady=(0,10))
        
        tk.Label(feature4, text=
            "• Start/Stop buttons moved to topbar\n"
            "• Always visible (no scrolling needed)\n"
            "• Enhanced contrast ratio design (CR: 5.8:1 and 6.3:1)\n"
            "• Slightly smaller for topbar (font=10pt vs 11pt)",
            justify='left', font=('Arial', 9)
        ).pack(anchor='w')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Click 'Find Windows' to see window list")
        status_bar = tk.Label(self, textvariable=self.status_var, 
                             bg='#e0e0e0', fg='#333', font=('Arial', 9), 
                             relief='sunken', padx=10, pady=6, anchor='w')
        status_bar.pack(fill='x', side='bottom')
        
        # Log area
        log_frame = tk.LabelFrame(content, text="📋 Demo Log", font=('Arial', 10, 'bold'), padx=10, pady=8)
        log_frame.pack(fill='both', expand=True, pady=(0,10))
        
        self.log_text = tk.Text(log_frame, height=8, bg='#fafafa', font=('Consolas', 9), 
                               relief='sunken', bd=1, wrap='word')
        self.log_text.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self._log("✓ Demo app initialized")
        self._log("💡 Tip: Try clicking 'Find Windows' to populate the combobox")
    
    def _create_tooltip(self, widget, text):
        """Create simple tooltip."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                           relief='solid', borderwidth=1, padx=8, pady=6, 
                           justify='left', font=('Arial', 9))
            label.pack()
            widget._tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                delattr(widget, '_tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def _log(self, message):
        """Add message to log."""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        print(message)
    
    def _find_windows(self):
        """Simulate finding Cabal windows."""
        self._log("\n[Find Windows] Scanning for Cabal windows...")
        
        # Simulate some windows
        self.windows = [
            {'title': 'Cabal Online - Character 1', 'pid': 12345},
            {'title': 'Cabal Online - Character 2', 'pid': 12346},
            {'title': 'Cabal Online - Main', 'pid': 12347},
        ]
        
        # Populate combobox
        window_labels = [f"{w['title']}  [PID:{w['pid']}]" for w in self.windows]
        self.win_combo['values'] = window_labels
        
        # Auto-select first (or matching saved PID)
        self.win_combo.current(0)
        self.selected_window = self.windows[0]
        
        self._log(f"✓ Found {len(self.windows)} Cabal windows")
        self._log(f"✓ Auto-selected: {self.selected_window['title']}")
        self.status_var.set(f"✓ Found {len(self.windows)} windows - Select from combobox to bring to front")
    
    def _on_window_selected(self, event=None):
        """Handle window selection from combobox."""
        idx = self.win_combo.current()
        if idx < 0 or idx >= len(self.windows):
            return
        
        self.selected_window = self.windows[idx]
        
        self._log(f"\n[Window Selected] {self.selected_window['title']}")
        self._log("[Auto Bring-to-Front] Bringing window to front...")
        
        # Simulate bring to front
        self.after(500, lambda: self._simulate_bring_to_front())
    
    def _simulate_bring_to_front(self):
        """Simulate bringing window to front."""
        if not self.selected_window:
            return
        
        self._log(f"✓ Window brought to front: {self.selected_window['title']}")
        self.status_var.set(f"✓ Window active: {self.selected_window['title']} [PID:{self.selected_window['pid']}]")
    
    def _simulate_startup_bring_to_front(self):
        """Simulate auto bring-to-front on app startup."""
        self._log("\n[App Startup] Loading saved window from config...")
        self._log("[Auto Bring-to-Front] Bringing saved window to front...")
        
        # Simulate saved window
        saved_window = {'title': 'Cabal Online - Last Session', 'pid': 99999}
        
        self.after(500, lambda: self._complete_startup(saved_window))
    
    def _complete_startup(self, window):
        """Complete startup simulation."""
        self._log(f"✓ Game window ready: {window['title']}")
        self.status_var.set(f"✓ Game window ready: {window['title']}")
        
        # Restore status after 3s (as in real app)
        self.after(3000, lambda: self.status_var.set("Ready - Click 'Find Windows' to see window list"))
    
    def _demo_auto_detection(self):
        """Demonstrate auto PID detection."""
        self._log("\n[Setup Wizard] User clicked 'No' (skipped setup)")
        self._log("[Auto PID Detection] Searching for Cabal windows...")
        
        self.after(500, self._complete_auto_detection)
    
    def _complete_auto_detection(self):
        """Complete auto detection demo."""
        detected = {'title': 'Cabal Online', 'pid': 54321}
        
        self._log(f"✓ Found Cabal window: {detected['title']} [PID:{detected['pid']}]")
        self._log("✓ Saved to hunt_config.json")
        self._log("✓ Updated UI combobox")
        
        messagebox.showinfo(
            "Auto PID Detection",
            f"✅ Auto-detected Cabal window:\n\n{detected['title']}\nPID: {detected['pid']}\n\nYou can change this anytime using 'Find Windows' button."
        )
        
        self.status_var.set(f"✓ Auto-detected: {detected['title']} [PID:{detected['pid']}]")
    
    def _start_hunt(self):
        """Start hunt simulation."""
        if not self.selected_window:
            messagebox.showwarning("No Window", "Please select a game window first!")
            return
        
        self.hunt_running = True
        self._log(f"\n[Hunt Started] Hunting in: {self.selected_window['title']}")
        
        # Update button states
        self.start_btn.config(
            state='disabled',
            bg='#A5D6A7',
            relief='sunken',
            cursor='arrow'
        )
        self.stop_btn.config(
            state='normal',
            bg='#C62828',
            fg='white',
            relief='raised',
            cursor='hand2'
        )
        
        self.status_var.set(f"🎯 Hunting... (Window: {self.selected_window['title']})")
    
    def _stop_hunt(self):
        """Stop hunt simulation."""
        self.hunt_running = False
        self._log("[Hunt Stopped] Hunt stopped by user")
        
        # Restore button states
        self.start_btn.config(
            state='normal',
            bg='#2E7D32',
            relief='raised',
            cursor='hand2'
        )
        self.stop_btn.config(
            state='disabled',
            bg='#FFCDD2',
            fg='#999',
            relief='sunken',
            cursor='arrow'
        )
        
        self.status_var.set("Hunt stopped - Ready to start again")


def show_comparison():
    """Show before/after comparison."""
    root = tk.Tk()
    root.title("Before & After Comparison")
    root.geometry("1000x650")
    
    # Header
    header = tk.Label(root, text="📊 UI Layout Comparison - Topbar Enhancement", 
                     font=('Arial', 14, 'bold'), bg='#343a40', fg='white', pady=12)
    header.pack(fill='x')
    
    # Comparison frames
    comparison = tk.Frame(root, bg='white')
    comparison.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Left - OLD
    old_frame = tk.LabelFrame(comparison, text="❌ OLD LAYOUT", 
                             font=('Arial', 12, 'bold'), fg='#dc3545', 
                             padx=15, pady=15, bg='#fff5f5')
    old_frame.pack(side='left', fill='both', expand=True, padx=(0,10))
    
    tk.Label(old_frame, text=
        "TOPBAR:\n"
        "  • Language selector\n"
        "  • Window title entry\n"
        "  • Find Windows button\n"
        "  • Bring to Front button\n\n"
        "HUNT TAB:\n"
        "  • Window listbox (4 rows)\n"
        "  • Monster rotation\n"
        "  • Skill slots\n"
        "  • [Setup] [Save] [Start] [Stop]\n\n"
        "ISSUES:\n"
        "  ✗ Window list takes space\n"
        "  ✗ Hunt buttons need scrolling\n"
        "  ✗ Manual bring-to-front\n"
        "  ✗ No auto PID detection\n"
        "  ✗ No auto startup bring-to-front",
        justify='left', bg='#fff5f5', font=('Consolas', 9)
    ).pack(anchor='w', fill='both', expand=True)
    
    # Right - NEW
    new_frame = tk.LabelFrame(comparison, text="✅ NEW LAYOUT", 
                             font=('Arial', 12, 'bold'), fg='#28a745', 
                             padx=15, pady=15, bg='#f0fff4')
    new_frame.pack(side='right', fill='both', expand=True, padx=(10,0))
    
    tk.Label(new_frame, text=
        "TOPBAR:\n"
        "  • Language selector\n"
        "  • Window combobox (with tooltip)\n"
        "  • Find Windows button\n"
        "  • [▶ Start] [■ Stop] buttons\n\n"
        "HUNT TAB:\n"
        "  • Monster rotation\n"
        "  • Skill slots\n"
        "  • [Setup] [Save]\n\n"
        "IMPROVEMENTS:\n"
        "  ✓ Compact window selection\n"
        "  ✓ Hunt buttons always visible\n"
        "  ✓ Auto bring-to-front on select\n"
        "  ✓ Auto PID detection on skip setup\n"
        "  ✓ Auto bring-to-front on startup\n"
        "  ✓ Cleaner UI (removed listbox)",
        justify='left', bg='#f0fff4', font=('Consolas', 9)
    ).pack(anchor='w', fill='both', expand=True)
    
    # Footer
    footer = tk.Label(root, text=
        "💡 Key Benefits: Faster workflow • Less clicks • Cleaner UI • Better new user experience • Auto window management",
        bg='#e7f3ff', fg='#004085', font=('Arial', 9), pady=10
    )
    footer.pack(fill='x')
    
    root.mainloop()


def show_menu():
    """Show test menu."""
    root = tk.Tk()
    root.title("Topbar Enhancement Tests")
    root.geometry("600x450")
    
    # Header
    header = tk.Label(root, text="🎨 Topbar Enhancement - Test Suite", 
                     font=('Arial', 16, 'bold'), bg='#343a40', fg='white', pady=15)
    header.pack(fill='x')
    
    # Description
    desc = tk.Label(root, text=
        "Window Selection & Hunt Controls Enhancement\n\n"
        "✨ Features:\n"
        "• Window selection combobox in topbar\n"
        "• Auto PID detection for new users\n"
        "• Auto bring-to-front on selection & startup\n"
        "• Start/Stop buttons in topbar\n"
        "• i18n tooltip for guidance",
        font=('Arial', 10), justify='center', pady=15, bg='white'
    )
    desc.pack(fill='x')
    
    # Test buttons
    buttons_frame = tk.Frame(root, bg='white')
    buttons_frame.pack(expand=True, fill='both', padx=30, pady=10)
    
    tk.Button(buttons_frame, text=
        "1️⃣ Interactive Demo\n\n"
        "Try all new features in\n"
        "interactive demo app",
        command=lambda: [root.destroy(), TopbarEnhancementDemo().mainloop()],
        font=('Arial', 11), bg='#007bff', fg='white', padx=20, pady=20, 
        justify='center', relief='raised', bd=3
    ).pack(fill='x', pady=8)
    
    tk.Button(buttons_frame, text=
        "2️⃣ Before & After Comparison\n\n"
        "See old vs new layout\n"
        "side by side",
        command=lambda: [root.destroy(), show_comparison()],
        font=('Arial', 11), bg='#28a745', fg='white', padx=20, pady=20, 
        justify='center', relief='raised', bd=3
    ).pack(fill='x', pady=8)
    
    tk.Button(buttons_frame, text="❌ Exit Tests",
        command=root.destroy,
        font=('Arial', 11), bg='#dc3545', fg='white', padx=20, pady=15, 
        relief='raised', bd=3
    ).pack(fill='x', pady=20)
    
    root.mainloop()


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TOPBAR ENHANCEMENT TEST SUITE")
    print("="*70)
    print("\nWindow Selection & Hunt Controls moved to topbar")
    print("\nFeatures:")
    print("  • Window combobox in topbar")
    print("  • Auto PID detection")
    print("  • Auto bring-to-front")
    print("  • Hunt buttons in topbar\n")
    
    show_menu()
