"""
Setup Wizard for Cabal Auto Hunt
Sprint 16 Phase 2 - Task #4: Welcome Screen

5-step wizard to guide new users through initial setup:
1. Welcome & Language Selection
2. Game Window Calibration
3. Monster Selection
4. Skill Configuration
5. Final Review & Save

This module provides a friendly first-run experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import ctypes
from ctypes import wintypes


class SetupWizard:
    """
    5-step setup wizard for first-time users.
    Guides through: Welcome → Window → Monster → Skills → Review
    """
    
    def __init__(self, parent, config_manager=None, on_complete=None, on_cancel=None):
        """
        Initialize setup wizard.
        
        Args:
            parent: Parent tkinter window
            config_manager: ConfigManager instance (optional)
            on_complete: Callback function when wizard completes (optional)
            on_cancel: Callback function when wizard is cancelled (optional)
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        
        # Wizard state
        self.current_step = 1
        self.total_steps = 5
        self.language = 'en'  # Default language
        
        # Data lists for steps
        self.filtered_windows = []  # Step 2: Window list
        self.monsters_data = []     # Step 3: Monster list
        self.skills_data = []       # Step 4: Skills list
        self.skill_slot_vars = []   # Step 4: Skill slot variables
        self.skill_slot_combos = [] # Step 4: Skill slot comboboxes
        
        # Collected data from wizard steps
        self.wizard_data = {
            'language': 'en',
            'window_title': '',
            'window_pid': None,
            'window_hwnd': None,
            'monster_name': '',
            'monster_templates': [],
            'skill_slots': [],
            'timing': {
                'lost_timeout_sec': 0.5,
                'attack_min_duration_sec': 5.0
            }
        }
        
        # Create wizard window with larger size to fit all content
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Setup Wizard - Cabal Auto Hunt")
        self.dialog.geometry("750x750")  # Increased height to ensure footer buttons are always visible
        self.dialog.minsize(700, 650)  # Minimum size to prevent content from being cut off
        self.dialog.resizable(True, True)  # Allow resizing for different screen sizes
        
        # Center window on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (750 // 2)
        self.dialog.geometry(f"750x750+{x}+{y}")
        
        # Make dialog modal - blocks parent window
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Handle window close (X button) - restore parent window
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close_window)
        
        # Hide parent window AFTER dialog is set up to avoid transient() issues
        # This prevents confusing dual-window state during wizard
        parent.withdraw()
        
        # Build UI
        self._build_ui()
        
        # Show first step
        self._show_step(1)
        
        # Wait for dialog to close (blocks execution until wizard finishes)
        parent.wait_window(self.dialog)
    
    def _build_ui(self):
        """Build wizard UI structure with header, content, and footer."""
        # Main container
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header: Progress indicator
        header_frame = tk.Frame(main_frame, bg='#f0f0f0', height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        self.progress_label = tk.Label(
            header_frame,
            text="Step 1 of 5",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0',
            fg='#333'
        )
        self.progress_label.pack(pady=20)
        
        # Progress dots
        self.dots_frame = tk.Frame(header_frame, bg='#f0f0f0')
        self.dots_frame.pack()
        
        self.progress_dots = []
        for i in range(self.total_steps):
            dot = tk.Label(
                self.dots_frame,
                text='●',
                font=('Arial', 16),
                bg='#f0f0f0',
                fg='#4CAF50' if i == 0 else '#ccc'
            )
            dot.pack(side=tk.LEFT, padx=5)
            self.progress_dots.append(dot)
        
        # Content area with scrollbar (will be swapped based on step)
        # Create a canvas to enable scrolling if content is too tall
        content_container = tk.Frame(main_frame, bg='white')
        content_container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(content_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(content_container, orient='vertical', command=self.canvas.yview)
        
        self.content_frame = tk.Frame(self.canvas, bg='white')
        
        # Configure canvas scrolling
        self.content_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        self.canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Separator line above footer
        separator = tk.Frame(main_frame, height=2, bg='#ddd')
        separator.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Footer: Navigation buttons (auto-expand to fit tall buttons)
        footer_frame = tk.Frame(main_frame, bg='#f0f0f0')
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        # Removed pack_propagate(False) to allow footer to expand with button height
        
        button_frame = tk.Frame(footer_frame, bg='#f0f0f0')
        button_frame.pack(pady=15)
        
        self.back_button = tk.Button(
            button_frame,
            text="← Back",
            command=self._on_back,
            width=12,
            height=2,
            font=('Arial', 10),
            state=tk.DISABLED  # Disabled on first step
        )
        self.back_button.pack(side=tk.LEFT, padx=8)
        
        # Make Next button more prominent
        self.next_button = tk.Button(
            button_frame,
            text="Next →",
            command=self._on_next,
            width=15,
            height=2,
            font=('Arial', 11, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#45a049',
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        self.next_button.pack(side=tk.LEFT, padx=15)  # Extra padding to make it stand out
        
        self.cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=12,
            height=2,
            font=('Arial', 10)
        )
        self.cancel_button.pack(side=tk.LEFT, padx=8)
    
    def _show_step(self, step_number):
        """Show specified wizard step."""
        self.current_step = step_number
        
        # Update progress indicator
        self.progress_label.config(text=f"Step {step_number} of {self.total_steps}")
        
        # Update progress dots
        for i, dot in enumerate(self.progress_dots):
            if i < step_number:
                dot.config(fg='#4CAF50')  # Green for completed/current
            else:
                dot.config(fg='#ccc')  # Gray for upcoming
        
        # Update button states
        self.back_button.config(state=tk.NORMAL if step_number > 1 else tk.DISABLED)
        
        if step_number == self.total_steps:
            # Make Finish button even more prominent
            self.next_button.config(
                text="✓ Finish",
                bg='#2196F3',
                activebackground='#1976D2',
                font=('Arial', 11, 'bold')
            )
        else:
            self.next_button.config(
                text="Next →",
                bg='#4CAF50',
                activebackground='#45a049',
                font=('Arial', 11, 'bold')
            )
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show appropriate step content
        if step_number == 1:
            self._build_step1_welcome()
        elif step_number == 2:
            self._build_step2_window()
        elif step_number == 3:
            self._build_step3_monster()
        elif step_number == 4:
            self._build_step4_skills()
        elif step_number == 5:
            self._build_step5_review()
    
    def _build_step1_welcome(self):
        """Step 1: Welcome screen with language selection."""
        # Welcome title
        title = tk.Label(
            self.content_frame,
            text="🎉 Welcome to Cabal Auto Hunt!",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='#333'
        )
        title.pack(pady=(20, 10))
        
        # Subtitle
        subtitle = tk.Label(
            self.content_frame,
            text="Let's get you set up in just 5 easy steps",
            font=('Arial', 12),
            bg='white',
            fg='#666'
        )
        subtitle.pack(pady=(0, 30))
        
        # What this wizard will do
        info_frame = tk.Frame(self.content_frame, bg='white')
        info_frame.pack(pady=20, fill=tk.X)
        
        info_text = """This wizard will help you:

✓ Select your game window
✓ Choose monsters to hunt
✓ Configure your attack skills
✓ Set up optimal timing

It takes about 2 minutes. Let's begin!"""
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=('Arial', 11),
            bg='white',
            fg='#333',
            justify=tk.LEFT,
            anchor='w'
        )
        info_label.pack(padx=50, fill=tk.X)
        
        # Language selection
        lang_frame = tk.LabelFrame(
            self.content_frame,
            text="Choose Your Language / Chọn ngôn ngữ",
            font=('Arial', 10, 'bold'),
            bg='white',
            padx=20,
            pady=15
        )
        lang_frame.pack(pady=30, fill=tk.X)
        
        self.language_var = tk.StringVar(value='en')
        
        lang_en = tk.Radiobutton(
            lang_frame,
            text="🇬🇧 English",
            variable=self.language_var,
            value='en',
            font=('Arial', 11),
            bg='white',
            command=self._on_language_change
        )
        lang_en.pack(anchor='w', pady=5)
        
        lang_vi = tk.Radiobutton(
            lang_frame,
            text="🇻🇳 Tiếng Việt",
            variable=self.language_var,
            value='vi',
            font=('Arial', 11),
            bg='white',
            command=self._on_language_change
        )
        lang_vi.pack(anchor='w', pady=5)
        
        # Get started hint
        hint = tk.Label(
            self.content_frame,
            text="Click 'Next' to get started →",
            font=('Arial', 10, 'italic'),
            bg='white',
            fg='#999'
        )
        hint.pack(pady=(30, 0))
    
    def _build_step2_window(self):
        """Step 2: Game window calibration."""
        title = tk.Label(
            self.content_frame,
            text="Step 2: Select Game Window",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=(10, 5))
        
        subtitle = tk.Label(
            self.content_frame,
            text="Choose which game window to control",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        )
        subtitle.pack(pady=(0, 15))
        
        # Search frame
        search_frame = tk.Frame(self.content_frame, bg='white')
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        tk.Label(search_frame, text="Filter:", bg='white').pack(side=tk.LEFT)
        self.window_filter_var = tk.StringVar(value='Cabal')
        filter_entry = tk.Entry(search_frame, textvariable=self.window_filter_var, width=20)
        filter_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        tk.Button(
            search_frame,
            text="🔍 Search Windows",
            command=self._search_windows,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9, 'bold')
        ).pack(side=tk.LEFT)
        
        # Window list
        list_frame = tk.Frame(self.content_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.window_listbox = tk.Listbox(
            list_frame,
            height=8,
            yscrollcommand=scrollbar.set,
            font=('Courier New', 9)
        )
        self.window_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.window_listbox.yview)
        
        self.window_listbox.bind('<<ListboxSelect>>', self._on_window_select)
        
        # Info label
        self.window_info_label = tk.Label(
            self.content_frame,
            text="💡 Tip: Make sure your game is running before searching",
            font=('Arial', 9, 'italic'),
            bg='white',
            fg='#666'
        )
        self.window_info_label.pack(pady=(5, 0))
        
        # Auto-search on step load
        self.dialog.after(100, self._search_windows)
    
    def _build_step3_monster(self):
        """Step 3: Monster selection."""
        title = tk.Label(
            self.content_frame,
            text="Step 3: Choose Monster to Hunt",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=(10, 5))
        
        subtitle = tk.Label(
            self.content_frame,
            text="Select which monster you want to hunt",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        )
        subtitle.pack(pady=(0, 15))
        
        # Load monsters
        monsters_path = os.path.join(os.path.dirname(__file__), 'data', 'monsters.json')
        try:
            with open(monsters_path, 'r', encoding='utf-8') as f:
                self.monsters_data = json.load(f)
        except Exception as e:
            self.monsters_data = []
            tk.Label(
                self.content_frame,
                text=f"⚠️ Error loading monsters: {e}",
                fg='red',
                bg='white'
            ).pack(pady=20)
            return
        
        if not self.monsters_data:
            tk.Label(
                self.content_frame,
                text="⚠️ No monsters found. Please add monsters first.",
                fg='orange',
                bg='white'
            ).pack(pady=20)
            return
        
        # Monster list frame
        list_frame = tk.Frame(self.content_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.monster_listbox = tk.Listbox(
            list_frame,
            height=10,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10)
        )
        self.monster_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.monster_listbox.yview)
        
        self.monster_listbox.bind('<<ListboxSelect>>', self._on_monster_select)
        
        # Populate monster list
        for monster in self.monsters_data:
            name = monster.get('name', 'Unnamed')
            hp = monster.get('hp', 0)
            templates_count = len(monster.get('templates', []))
            label = f"{name}  (HP: {hp:,.0f}, {templates_count} template(s))"
            self.monster_listbox.insert(tk.END, label)
        
        # Select first monster by default
        if self.monsters_data:
            self.monster_listbox.selection_set(0)
            self.monster_listbox.activate(0)
            self._on_monster_select()
        
        # Info label
        self.monster_info_label = tk.Label(
            self.content_frame,
            text="",
            font=('Arial', 9),
            bg='white',
            fg='#333',
            justify=tk.LEFT
        )
        self.monster_info_label.pack(pady=(5, 0))
    
    def _build_step4_skills(self):
        """Step 4: Skill configuration."""
        title = tk.Label(
            self.content_frame,
            text="Step 4: Configure Attack Skills",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=(10, 5))
        
        subtitle = tk.Label(
            self.content_frame,
            text="Assign skills to 9 quick slots (leave empty if not needed)",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        )
        subtitle.pack(pady=(0, 15))
        
        # Load skills
        skills_path = os.path.join(os.path.dirname(__file__), 'data', 'skills.json')
        try:
            with open(skills_path, 'r', encoding='utf-8') as f:
                self.skills_data = json.load(f)
        except Exception as e:
            self.skills_data = []
            tk.Label(
                self.content_frame,
                text=f"⚠️ Error loading skills: {e}",
                fg='red',
                bg='white'
            ).pack(pady=20)
            return
        
        # Skill slots frame
        slots_frame = tk.Frame(self.content_frame, bg='white')
        slots_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        self.skill_slot_vars = []
        self.skill_slot_combos = []
        
        # Create skill name list for combobox
        skill_names = ['(Empty)'] + [s.get('name', 'Unnamed') for s in self.skills_data]
        
        # Create 9 skill slots (3 rows x 3 cols)
        for row in range(3):
            for col in range(3):
                slot_num = row * 3 + col + 1
                
                # Slot container
                slot_container = tk.Frame(slots_frame, bg='white')
                slot_container.grid(row=row, column=col, padx=8, pady=5, sticky='w')
                
                # Label
                tk.Label(
                    slot_container,
                    text=f"Slot {slot_num}:",
                    bg='white',
                    font=('Arial', 9, 'bold')
                ).pack(anchor='w')
                
                # Combobox
                var = tk.StringVar(value='(Empty)')
                combo = ttk.Combobox(
                    slot_container,
                    textvariable=var,
                    values=skill_names,
                    state='readonly',
                    width=18
                )
                combo.pack(anchor='w')
                
                self.skill_slot_vars.append(var)
                self.skill_slot_combos.append(combo)
        
        # Buttons frame
        btn_frame = tk.Frame(self.content_frame, bg='white')
        btn_frame.pack(pady=(15, 0))
        
        tk.Button(
            btn_frame,
            text="Clear All Slots",
            command=self._clear_all_skill_slots
        ).pack()
        
        # Info
        info = tk.Label(
            self.content_frame,
            text="💡 Tip: Skills will be used in order from Slot 1 to Slot 9",
            font=('Arial', 9, 'italic'),
            bg='white',
            fg='#666'
        )
        info.pack(pady=(10, 0))
    
    def _build_step5_review(self):
        """Step 5: Final review."""
        title = tk.Label(
            self.content_frame,
            text="Step 5: Review & Confirm",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=(10, 5))
        
        subtitle = tk.Label(
            self.content_frame,
            text="Review your setup and click Finish to save",
            font=('Arial', 10),
            bg='white',
            fg='#666'
        )
        subtitle.pack(pady=(0, 20))
        
        # Review frame with border
        review_frame = tk.LabelFrame(
            self.content_frame,
            text="Configuration Summary",
            font=('Arial', 10, 'bold'),
            bg='white',
            padx=20,
            pady=15
        )
        review_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Window info
        window_info = self.wizard_data.get('window_title', 'Not selected')
        window_pid = self.wizard_data.get('window_pid', 'N/A')
        tk.Label(
            review_frame,
            text=f"🪟 Game Window:",
            font=('Arial', 10, 'bold'),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        tk.Label(
            review_frame,
            text=f"   {window_info} (PID: {window_pid})",
            font=('Arial', 9),
            bg='white',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Monster info
        monster_name = self.wizard_data.get('monster_name', 'Not selected')
        monster_templates = self.wizard_data.get('monster_templates', [])
        tk.Label(
            review_frame,
            text=f"👾 Monster:",
            font=('Arial', 10, 'bold'),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        tk.Label(
            review_frame,
            text=f"   {monster_name} ({len(monster_templates)} template(s))",
            font=('Arial', 9),
            bg='white',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Skills info
        skill_slots = self.wizard_data.get('skill_slots', [])
        assigned_skills = [s for s in skill_slots if s and s != '(Empty)']
        tk.Label(
            review_frame,
            text=f"⚔️ Skills:",
            font=('Arial', 10, 'bold'),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        
        if assigned_skills:
            skills_text = "   " + ", ".join(assigned_skills)
            tk.Label(
                review_frame,
                text=skills_text,
                font=('Arial', 9),
                bg='white',
                fg='#333',
                anchor='w',
                wraplength=450,
                justify=tk.LEFT
            ).pack(fill=tk.X, pady=(0, 10))
        else:
            tk.Label(
                review_frame,
                text="   No skills assigned",
                font=('Arial', 9, 'italic'),
                bg='white',
                fg='#999',
                anchor='w'
            ).pack(fill=tk.X, pady=(0, 10))
        
        # Timing info
        timing = self.wizard_data.get('timing', {})
        tk.Label(
            review_frame,
            text=f"⏱️ Timing:",
            font=('Arial', 10, 'bold'),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 2))
        timing_text = f"   Lost timeout: {timing.get('lost_timeout_sec', 0.5)}s, Attack duration: {timing.get('attack_min_duration_sec', 5.0)}s"
        tk.Label(
            review_frame,
            text=timing_text,
            font=('Arial', 9),
            bg='white',
            fg='#333',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Warning if incomplete
        if not window_info or window_info == 'Not selected':
            tk.Label(
                self.content_frame,
                text="⚠️ Warning: No game window selected",
                font=('Arial', 9, 'bold'),
                bg='white',
                fg='orange'
            ).pack(pady=(10, 0))
        
        if not monster_name or monster_name == 'Not selected':
            tk.Label(
                self.content_frame,
                text="⚠️ Warning: No monster selected",
                font=('Arial', 9, 'bold'),
                bg='white',
                fg='orange'
            ).pack(pady=(5, 0))
    
    def _on_language_change(self):
        """Handle language selection change."""
        self.language = self.language_var.get()
        self.wizard_data['language'] = self.language
        # Note: Full UI translation will be implemented when needed
    
    def _search_windows(self):
        """Search for game windows matching filter."""
        filter_text = self.window_filter_var.get().strip().lower()
        windows = self._enum_windows()
        
        # Filter windows
        self.filtered_windows = [
            w for w in windows 
            if filter_text in w['title'].lower() or filter_text in (w.get('proc') or '').lower()
        ]
        
        # Update listbox
        self.window_listbox.delete(0, tk.END)
        for w in self.filtered_windows:
            label = f"{w['title']}  [PID: {w['pid']}]"
            if w.get('proc'):
                label += f"  ({w['proc']})"
            self.window_listbox.insert(tk.END, label)
        
        # Update info
        if not self.filtered_windows:
            self.window_info_label.config(
                text="⚠️ No windows found. Try a different filter or make sure game is running.",
                fg='orange'
            )
        else:
            self.window_info_label.config(
                text=f"✓ Found {len(self.filtered_windows)} window(s)",
                fg='green'
            )
            # Auto-select first
            self.window_listbox.selection_set(0)
            self.window_listbox.activate(0)
            self._on_window_select()
    
    def _on_window_select(self, event=None):
        """Handle window selection."""
        try:
            idx = self.window_listbox.curselection()
            if not idx:
                return
            
            selected = self.filtered_windows[idx[0]]
            self.wizard_data['window_title'] = selected['title']
            self.wizard_data['window_pid'] = selected['pid']
            self.wizard_data['window_hwnd'] = selected['hwnd']
            
            self.window_info_label.config(
                text=f"✓ Selected: {selected['title']} (PID: {selected['pid']})",
                fg='green'
            )
        except Exception as e:
            pass
    
    def _on_monster_select(self, event=None):
        """Handle monster selection."""
        try:
            idx = self.monster_listbox.curselection()
            if not idx:
                return
            
            selected = self.monsters_data[idx[0]]
            self.wizard_data['monster_name'] = selected.get('name', 'Unnamed')
            self.wizard_data['monster_templates'] = selected.get('templates', [])
            self.wizard_data['monster_hp'] = selected.get('hp', 0)
            self.wizard_data['monster_damage'] = selected.get('damage_per_hit', 0)
            
            # Update info label
            info = f"✓ Selected: {selected.get('name')} | HP: {selected.get('hp', 0):,.0f}"
            templates_count = len(selected.get('templates', []))
            info += f" | {templates_count} template(s)"
            self.monster_info_label.config(text=info)
        except Exception:
            pass
    
    def _clear_all_skill_slots(self):
        """Clear all skill slot selections."""
        for var in self.skill_slot_vars:
            var.set('(Empty)')
    
    def _enum_windows(self):
        """Enumerate visible windows using WinAPI."""
        user32 = ctypes.windll.user32
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        IsWindowVisible = user32.IsWindowVisible
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW
        GetWindowThreadProcessId = user32.GetWindowThreadProcessId

        results = []
        
        # Try to get process name via psutil
        try:
            import psutil
        except Exception:
            psutil = None

        def callback(hwnd, lParam):
            try:
                if not IsWindowVisible(hwnd):
                    return True
                length = GetWindowTextLengthW(hwnd)
                if length == 0:
                    return True
                buf = ctypes.create_unicode_buffer(length + 1)
                GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if not title:
                    return True
                
                pid = wintypes.DWORD()
                GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                pid_val = int(pid.value)
                
                proc_name = None
                if psutil is not None:
                    try:
                        p = psutil.Process(pid_val)
                        proc_name = p.name()
                    except Exception:
                        proc_name = None
                
                results.append({
                    'hwnd': int(hwnd),
                    'pid': pid_val,
                    'title': title,
                    'proc': proc_name
                })
            except Exception:
                pass
            return True
        
        try:
            EnumWindows(EnumWindowsProc(callback), 0)
        except Exception:
            pass
        
        return results
    
    def _on_back(self):
        """Navigate to previous step."""
        if self.current_step > 1:
            self._show_step(self.current_step - 1)
    
    def _on_next(self):
        """Navigate to next step or finish wizard."""
        if self.current_step < self.total_steps:
            # Validate current step before proceeding
            if self._validate_current_step():
                self._show_step(self.current_step + 1)
        else:
            # Final step - finish wizard
            self._on_finish()
    
    def _validate_current_step(self):
        """Validate current step data before moving to next step."""
        # Step 1: Always valid (language selection is optional)
        if self.current_step == 1:
            return True
        
        # Step 2: Window selection
        if self.current_step == 2:
            if not self.wizard_data.get('window_title'):
                messagebox.showwarning(
                    "Window Required",
                    "Please select a game window before continuing.",
                    parent=self.dialog
                )
                return False
            return True
        
        # Step 3: Monster selection
        if self.current_step == 3:
            if not self.wizard_data.get('monster_name'):
                messagebox.showwarning(
                    "Monster Required",
                    "Please select a monster before continuing.",
                    parent=self.dialog
                )
                return False
            return True
        
        # Step 4: Skills (optional - can proceed with empty slots)
        if self.current_step == 4:
            # Collect selected skills
            skill_slots = []
            for var in self.skill_slot_vars:
                value = var.get()
                skill_slots.append(value if value != '(Empty)' else '')
            
            self.wizard_data['skill_slots'] = skill_slots
            
            # Check if at least one skill is assigned (optional warning)
            assigned = [s for s in skill_slots if s]
            if not assigned:
                confirm = messagebox.askyesno(
                    "No Skills",
                    "You haven't assigned any skills. Continue anyway?",
                    parent=self.dialog
                )
                return confirm
            return True
        
        # Step 5: Review - always valid
        if self.current_step == 5:
            return True
        
        return True
    
    def _on_finish(self):
        """Complete wizard and save configuration."""
        # Show confirmation
        confirm = messagebox.askyesno(
            "Finish Setup",
            "Save this configuration and start hunting?",
            parent=self.dialog
        )
        
        if confirm:
            # Save wizard data (will be implemented with config_manager)
            if self.config_manager:
                self._save_wizard_config()
            
            # Call completion callback if provided
            if self.on_complete:
                self.on_complete(self.wizard_data)
            
            # Close wizard (deiconify handled by callback)
            self.dialog.destroy()
        # If user clicks "No", wizard stays open (don't destroy)
    
    def _save_wizard_config(self):
        """Save wizard data to hunt_config.json via config_manager."""
        if not self.config_manager:
            return
        
        try:
            # Update hunt config with wizard data
            # Window settings
            window_title = self.wizard_data.get('window_title', '')
            if window_title:
                self.config_manager.set('hunt_config', 'window_title', window_title)
            
            window_pid = self.wizard_data.get('window_pid')
            if window_pid:
                self.config_manager.set('hunt_config', 'window_pid', window_pid)
            
            window_hwnd = self.wizard_data.get('window_hwnd')
            if window_hwnd:
                self.config_manager.set('hunt_config', 'window_hwnd', window_hwnd)
            
            # Monster settings
            monster_name = self.wizard_data.get('monster_name')
            if monster_name:
                self.config_manager.set('hunt_config', 'monster_selected_name', monster_name)
            
            templates = self.wizard_data.get('monster_templates', [])
            if templates and len(templates) > 0:
                # Use first template's path as primary template
                first_template = templates[0]
                template_path = first_template.get('path', '')
                if template_path:
                    self.config_manager.set('hunt_config', 'template_path', template_path)
            
            # Skill slots
            skill_slots = self.wizard_data.get('skill_slots', [])
            if skill_slots:
                self.config_manager.set('hunt_config', 'skill_slots', skill_slots)
            
            # Timing settings (use defaults from wizard_data or recommended values)
            timing = self.wizard_data.get('timing', {})
            lost_timeout = timing.get('lost_timeout_sec', 0.5)
            attack_duration = timing.get('attack_min_duration_sec', 5.0)
            
            self.config_manager.set('hunt_config', 'lost_timeout_sec', lost_timeout)
            self.config_manager.set('hunt_config', 'attack_min_duration_sec', attack_duration)
            
            # Save to file
            self.config_manager.save()
            
        except Exception as e:
            messagebox.showerror(
                "Save Error",
                f"Failed to save configuration: {e}",
                parent=self.dialog
            )
    
    def _on_cancel(self):
        """Cancel wizard and close dialog."""
        confirm = messagebox.askyesno(
            "Cancel Setup",
            "Are you sure you want to cancel the setup wizard?",
            parent=self.dialog
        )
        
        if confirm:
            self.dialog.destroy()
            # Call cancel callback to restore main window
            if self.on_cancel:
                self.on_cancel()
    
    def _on_close_window(self):
        """Handle window close button (X) - treat as cancel."""
        self._on_cancel()


def show_setup_wizard(parent, config_manager=None, on_complete=None, on_cancel=None):
    """
    Convenience function to show setup wizard.
    
    Args:
        parent: Parent tkinter window
        config_manager: ConfigManager instance (optional)
        on_complete: Callback when wizard completes (optional)
        on_cancel: Callback when wizard is cancelled (optional)
    
    Returns:
        SetupWizard instance
    """
    wizard = SetupWizard(parent, config_manager, on_complete, on_cancel)
    return wizard


# Test/Demo code
if __name__ == "__main__":
    # Create test window
    root = tk.Tk()
    root.title("Setup Wizard Test")
    root.geometry("400x300")
    
    def on_wizard_complete(data):
        print("Wizard completed with data:", data)
    
    # Button to launch wizard
    launch_btn = tk.Button(
        root,
        text="Launch Setup Wizard",
        command=lambda: show_setup_wizard(root, on_complete=on_wizard_complete),
        font=('Arial', 12),
        padx=20,
        pady=10
    )
    launch_btn.pack(expand=True)
    
    root.mainloop()
