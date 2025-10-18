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


class SetupWizard:
    """
    5-step setup wizard for first-time users.
    Guides through: Welcome → Window → Monster → Skills → Review
    """
    
    def __init__(self, parent, config_manager=None, on_complete=None):
        """
        Initialize setup wizard.
        
        Args:
            parent: Parent tkinter window
            config_manager: ConfigManager instance (optional)
            on_complete: Callback function when wizard completes (optional)
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_complete = on_complete
        
        # Wizard state
        self.current_step = 1
        self.total_steps = 5
        self.language = 'en'  # Default language
        
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
        
        # Create wizard window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Setup Wizard - Cabal Auto Hunt")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # Center window on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Build UI
        self._build_ui()
        
        # Show first step
        self._show_step(1)
    
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
        
        # Content area (will be swapped based on step)
        self.content_frame = tk.Frame(main_frame, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Footer: Navigation buttons
        footer_frame = tk.Frame(main_frame, bg='#f0f0f0', height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        button_frame = tk.Frame(footer_frame, bg='#f0f0f0')
        button_frame.pack(pady=15)
        
        self.back_button = tk.Button(
            button_frame,
            text="← Back",
            command=self._on_back,
            width=10,
            state=tk.DISABLED  # Disabled on first step
        )
        self.back_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(
            button_frame,
            text="Next →",
            command=self._on_next,
            width=10,
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white'
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=10
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
    
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
            self.next_button.config(text="Finish", bg='#2196F3')
        else:
            self.next_button.config(text="Next →", bg='#4CAF50')
        
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
        """Step 2: Game window calibration (placeholder)."""
        title = tk.Label(
            self.content_frame,
            text="Step 2: Select Game Window",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=20)
        
        placeholder = tk.Label(
            self.content_frame,
            text="[Window selection UI will be implemented in Task #5]",
            font=('Arial', 11, 'italic'),
            bg='white',
            fg='#999'
        )
        placeholder.pack(pady=50)
    
    def _build_step3_monster(self):
        """Step 3: Monster selection (placeholder)."""
        title = tk.Label(
            self.content_frame,
            text="Step 3: Choose Monster",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=20)
        
        placeholder = tk.Label(
            self.content_frame,
            text="[Monster selection UI will be implemented in Task #5]",
            font=('Arial', 11, 'italic'),
            bg='white',
            fg='#999'
        )
        placeholder.pack(pady=50)
    
    def _build_step4_skills(self):
        """Step 4: Skill configuration (placeholder)."""
        title = tk.Label(
            self.content_frame,
            text="Step 4: Configure Skills",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=20)
        
        placeholder = tk.Label(
            self.content_frame,
            text="[Skill configuration UI will be implemented in Task #5]",
            font=('Arial', 11, 'italic'),
            bg='white',
            fg='#999'
        )
        placeholder.pack(pady=50)
    
    def _build_step5_review(self):
        """Step 5: Final review (placeholder)."""
        title = tk.Label(
            self.content_frame,
            text="Step 5: Review & Save",
            font=('Arial', 16, 'bold'),
            bg='white'
        )
        title.pack(pady=20)
        
        placeholder = tk.Label(
            self.content_frame,
            text="[Review UI will be implemented in Task #5]",
            font=('Arial', 11, 'italic'),
            bg='white',
            fg='#999'
        )
        placeholder.pack(pady=50)
    
    def _on_language_change(self):
        """Handle language selection change."""
        self.language = self.language_var.get()
        self.wizard_data['language'] = self.language
        # Note: Full UI translation will be implemented when needed
    
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
        
        # Steps 2-4: Will be implemented in Task #5
        if self.current_step in [2, 3, 4]:
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
            
            # Close wizard
            self.dialog.destroy()
    
    def _save_wizard_config(self):
        """Save wizard data to hunt_config.json via config_manager."""
        # This will be fully implemented when config_manager integration is added
        # For now, just store the collected data
        pass
    
    def _on_cancel(self):
        """Cancel wizard and close dialog."""
        confirm = messagebox.askyesno(
            "Cancel Setup",
            "Are you sure you want to cancel the setup wizard?",
            parent=self.dialog
        )
        
        if confirm:
            self.dialog.destroy()


def show_setup_wizard(parent, config_manager=None, on_complete=None):
    """
    Convenience function to show setup wizard.
    
    Args:
        parent: Parent tkinter window
        config_manager: ConfigManager instance (optional)
        on_complete: Callback when wizard completes (optional)
    
    Returns:
        SetupWizard instance
    """
    wizard = SetupWizard(parent, config_manager, on_complete)
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
