"""
Comprehensive Example: Monster-Template Editor with Edit Mode

This example demonstrates:
1. Hierarchical data (Monster → Template)
2. Edit mode vs View mode
3. Check All handling
4. Context-based state management
5. All button types (Add/Edit/Delete/Mode toggle)

Author: SokKimThanh
Date: 2025-10-25
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from ui.mixins import ButtonStateMixin


class MonsterTemplateEditor(tk.Tk, ButtonStateMixin):
    """
    Complete example of Monster-Template editor.
    
    Features:
    - Monster list (parent)
    - Template list (child, depends on monster selection)
    - Edit mode toggle
    - Check All support
    - All button states managed automatically
    """
    
    def __init__(self):
        tk.Tk.__init__(self)
        ButtonStateMixin.__init__(self, debug_mode=True)
        
        self.title("Monster-Template Editor (Complete Example)")
        self.geometry("900x600")
        
        self._setup_ui()
        self._setup_button_management()
        self._load_sample_data()
        
        # Initial state update
        self.update_button_states()
        
    def _setup_ui(self):
        """Create UI components."""
        # === Top Bar: Mode Toggle ===
        top_bar = tk.Frame(self, bg='#2c3e50', height=40)
        top_bar.pack(fill='x', side='top')
        top_bar.pack_propagate(False)
        
        mode_label = tk.Label(top_bar, text="Mode:", bg='#2c3e50', fg='white')
        mode_label.pack(side='left', padx=10)
        
        self.view_mode_btn = tk.Button(
            top_bar, 
            text="📖 View Mode", 
            command=lambda: self.set_edit_mode(False),
            relief='sunken'
        )
        self.view_mode_btn.pack(side='left', padx=5)
        
        self.edit_mode_btn = tk.Button(
            top_bar, 
            text="✏️ Edit Mode", 
            command=lambda: self.set_edit_mode(True)
        )
        self.edit_mode_btn.pack(side='left', padx=5)
        
        # === Main Content ===
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # === Monster Panel (Left) ===
        monster_frame = tk.LabelFrame(main_frame, text="🐉 Monsters (Parent)", font=('Arial', 10, 'bold'))
        monster_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Monster list
        list_frame = tk.Frame(monster_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.monster_tree = ttk.Treeview(list_frame, show='tree', selectmode='browse')
        self.monster_tree.pack(side='left', fill='both', expand=True)
        
        scroll = ttk.Scrollbar(list_frame, command=self.monster_tree.yview)
        scroll.pack(side='right', fill='y')
        self.monster_tree.configure(yscrollcommand=scroll.set)
        
        # Monster buttons
        btn_frame = tk.Frame(monster_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        self.check_all_monsters_var = tk.BooleanVar()
        self.check_all_monsters_cb = tk.Checkbutton(
            btn_frame, 
            text="Check All", 
            variable=self.check_all_monsters_var,
            command=self._on_check_all_monsters
        )
        self.check_all_monsters_cb.pack(side='left', padx=5)
        
        self.add_monster_btn = tk.Button(btn_frame, text="➕ Add", command=self._add_monster)
        self.add_monster_btn.pack(side='left', padx=2)
        
        self.edit_monster_btn = tk.Button(btn_frame, text="✏️ Edit", command=self._edit_monster)
        self.edit_monster_btn.pack(side='left', padx=2)
        
        self.delete_monster_btn = tk.Button(btn_frame, text="🗑️ Delete", command=self._delete_monster)
        self.delete_monster_btn.pack(side='left', padx=2)
        
        # === Template Panel (Right) ===
        template_frame = tk.LabelFrame(main_frame, text="🎨 Templates (Child)", font=('Arial', 10, 'bold'))
        template_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Template list
        list_frame = tk.Frame(template_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.template_tree = ttk.Treeview(list_frame, show='tree', selectmode='browse')
        self.template_tree.pack(side='left', fill='both', expand=True)
        
        scroll = ttk.Scrollbar(list_frame, command=self.template_tree.yview)
        scroll.pack(side='right', fill='y')
        self.template_tree.configure(yscrollcommand=scroll.set)
        
        # Template buttons
        btn_frame = tk.Frame(template_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        self.check_all_templates_var = tk.BooleanVar()
        self.check_all_templates_cb = tk.Checkbutton(
            btn_frame, 
            text="Check All", 
            variable=self.check_all_templates_var,
            command=self._on_check_all_templates
        )
        self.check_all_templates_cb.pack(side='left', padx=5)
        
        self.add_template_btn = tk.Button(btn_frame, text="➕ Add", command=self._add_template)
        self.add_template_btn.pack(side='left', padx=2)
        
        self.edit_template_btn = tk.Button(btn_frame, text="✏️ Edit", command=self._edit_template)
        self.edit_template_btn.pack(side='left', padx=2)
        
        self.delete_template_btn = tk.Button(btn_frame, text="🗑️ Delete", command=self._delete_template)
        self.delete_template_btn.pack(side='left', padx=2)
        
        self.capture_template_btn = tk.Button(btn_frame, text="📷 Capture")
        self.capture_template_btn.pack(side='left', padx=2)
        
        self.test_template_btn = tk.Button(btn_frame, text="🧪 Test")
        self.test_template_btn.pack(side='left', padx=2)
        
        # === Status Bar ===
        status_frame = tk.Frame(self, bg='#ecf0f1', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame, 
            text="View Mode | No selection", 
            bg='#ecf0f1', 
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10, pady=5)
        
    def _setup_button_management(self):
        """Setup comprehensive button state management."""
        # Register widgets
        self.register_selection_widget('monsters', self.monster_tree)
        self.register_selection_widget('templates', self.template_tree)
        
        # Register all buttons
        self.register_buttons_batch({
            # Mode buttons
            'view_mode': self.view_mode_btn,
            'edit_mode': self.edit_mode_btn,
            
            # Monster buttons
            'add_monster': self.add_monster_btn,
            'edit_monster': self.edit_monster_btn,
            'delete_monster': self.delete_monster_btn,
            
            # Template buttons
            'add_template': self.add_template_btn,
            'edit_template': self.edit_template_btn,
            'delete_template': self.delete_template_btn,
            'capture_template': self.capture_template_btn,
            'test_template': self.test_template_btn,
        })
        
        # Define comprehensive rules
        self.register_button_rules({
            # Mode buttons - always enabled but styled differently
            'view_mode': {'always': True},
            'edit_mode': {'always': True},
            
            # Monster buttons
            'add_monster': {
                'requires_edit_mode': True  # Only in edit mode
            },
            'edit_monster': {
                'requires_selection': 'monsters',
                'requires_edit_mode': True
            },
            'delete_monster': {
                'enabled_with_check_all_or_selection': 'monsters',
                'requires_edit_mode': True
            },
            
            # Template buttons (hierarchical)
            'add_template': {
                'requires_parent': 'monsters',  # Need monster selected
                'requires_edit_mode': True
            },
            'edit_template': {
                'requires_selection': 'templates',
                'requires_edit_mode': True
            },
            'delete_template': {
                'enabled_with_check_all_or_selection': 'templates',
                'requires_edit_mode': True
            },
            
            # Template operations (available in both modes)
            'capture_template': {
                'requires_parent': 'monsters'
            },
            'test_template': {
                'requires_multiple': ['monsters', 'templates']
            },
        })
        
        # Auto-update on selection change
        self.bind_auto_update('monsters', '<<TreeviewSelect>>')
        self.bind_auto_update('templates', '<<TreeviewSelect>>')
        
    def _load_sample_data(self):
        """Load sample data."""
        monsters = [
            'Goblin', 'Orc', 'Dragon', 'Skeleton', 'Zombie'
        ]
        
        for monster in monsters:
            self.monster_tree.insert('', 'end', text=monster)
    
    # === Mode Toggle ===
    
    def set_edit_mode(self, edit_mode: bool):
        """Override to update UI."""
        # Call parent
        super().set_edit_mode(edit_mode)
        
        # Update mode buttons appearance
        if edit_mode:
            self.view_mode_btn.configure(relief='raised')
            self.edit_mode_btn.configure(relief='sunken')
            status = "✏️ Edit Mode"
        else:
            self.view_mode_btn.configure(relief='sunken')
            self.edit_mode_btn.configure(relief='raised')
            status = "📖 View Mode"
        
        self._update_status(f"{status} | {self._get_selection_info()}")
    
    # === Check All Handlers ===
    
    def _on_check_all_monsters(self):
        """Handle monster check all."""
        check_all = self.check_all_monsters_var.get()
        self.set_check_all(check_all)
        self._update_status(f"{'✅ Check All' if check_all else 'View Mode'} | Monsters")
    
    def _on_check_all_templates(self):
        """Handle template check all."""
        check_all = self.check_all_templates_var.get()
        self.set_check_all(check_all)
        self._update_status(f"{'✅ Check All' if check_all else 'View Mode'} | Templates")
    
    # === Button Actions ===
    
    def _add_monster(self):
        """Add monster."""
        import uuid
        item_id = f'monster_{uuid.uuid4().hex[:8]}'
        self.monster_tree.insert('', 'end', item_id, text=f'New Monster')
        self.monster_tree.selection_set(item_id)
        self.update_button_states()
        self._update_status("Added new monster")
    
    def _edit_monster(self):
        """Edit monster."""
        selection = self.monster_tree.selection()
        if selection:
            self._update_status(f"Editing monster: {self.monster_tree.item(selection[0], 'text')}")
    
    def _delete_monster(self):
        """Delete monster."""
        if self.is_check_all():
            # Delete all
            for item in self.monster_tree.get_children():
                self.monster_tree.delete(item)
            self._update_status("Deleted all monsters")
        else:
            # Delete selected
            selection = self.monster_tree.selection()
            if selection:
                self.monster_tree.delete(selection[0])
                self._update_status("Deleted selected monster")
        
        self.update_button_states()
    
    def _add_template(self):
        """Add template."""
        import uuid
        item_id = f'template_{uuid.uuid4().hex[:8]}'
        self.template_tree.insert('', 'end', item_id, text=f'New Template')
        self.template_tree.selection_set(item_id)
        self.update_button_states()
        self._update_status("Added new template")
    
    def _edit_template(self):
        """Edit template."""
        selection = self.template_tree.selection()
        if selection:
            self._update_status(f"Editing template: {self.template_tree.item(selection[0], 'text')}")
    
    def _delete_template(self):
        """Delete template."""
        if self.is_check_all():
            # Delete all
            for item in self.template_tree.get_children():
                self.template_tree.delete(item)
            self._update_status("Deleted all templates")
        else:
            # Delete selected
            selection = self.template_tree.selection()
            if selection:
                self.template_tree.delete(selection[0])
                self._update_status("Deleted selected template")
        
        self.update_button_states()
    
    # === Helper Methods ===
    
    def _get_selection_info(self) -> str:
        """Get current selection info."""
        parts = []
        
        if self.has_selection('monsters'):
            parts.append("Monster selected")
        if self.has_selection('templates'):
            parts.append("Template selected")
        
        if not parts:
            return "No selection"
        
        return " & ".join(parts)
    
    def _update_status(self, message: str):
        """Update status bar."""
        self.status_label.configure(text=message)


if __name__ == '__main__':
    app = MonsterTemplateEditor()
    
    print("\n" + "="*70)
    print("🎮 Monster-Template Editor - Comprehensive Example")
    print("="*70)
    print("\n📖 Features Demonstrated:")
    print("  1. Hierarchical data (Monster → Template)")
    print("  2. Edit mode vs View mode toggle")
    print("  3. Check All handling")
    print("  4. Context-based button states")
    print("  5. All button types (Add/Edit/Delete/Capture/Test)")
    print("\n🎯 Try This:")
    print("  • Switch between View/Edit modes")
    print("  • Select a monster → Add button enables")
    print("  • Select a template → Edit/Delete buttons enable")
    print("  • Check 'Check All' → Delete works without selection")
    print("  • Select both monster & template → Test button enables")
    print("\n✨ Button State Rules:")
    print("  • Add Monster: Edit mode only")
    print("  • Edit Monster: Edit mode + monster selected")
    print("  • Delete Monster: Edit mode + (selected OR check all)")
    print("  • Add Template: Edit mode + monster selected (parent)")
    print("  • Edit Template: Edit mode + template selected")
    print("  • Delete Template: Edit mode + (selected OR check all)")
    print("  • Capture: Monster selected (any mode)")
    print("  • Test: Both monster & template selected (any mode)")
    print("\n" + "="*70 + "\n")
    
    app.mainloop()
