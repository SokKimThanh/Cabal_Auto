"""
Skill Rotation Builder UI Integration
Integrates rotation builder into Library Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
import json
from pathlib import Path

from lib.features.skill_rotation.builder import (
    calculate_rotation_timing,
    generate_rotation_preview,
    generate_execution_preview,
    SkillRotation
)


class SkillRotationUI:
    """UI components for Skill Rotation Builder"""
    
    def __init__(self, parent_frame: tk.Frame, library_manager):
        """
        Initialize Skill Rotation UI
        
        Args:
            parent_frame: Parent tkinter frame
            library_manager: Reference to LibraryManager instance
        """
        self.parent = parent_frame
        self.lib_manager = library_manager
        self.lang = library_manager.lang
        
        # State
        self.available_skills = []  # From hunt_config.json
        self.rotation_sequence = []  # User-selected sequence
        self.current_rotation: Optional[SkillRotation] = None
        
        # Build UI
        self._build_ui()
        self._load_available_skills()
    
    def _t(self, key: str) -> str:
        """Translation helper"""
        return self.lib_manager._t(key) if hasattr(self.lib_manager, '_t') else key
    
    def _build_ui(self):
        """Build complete UI layout"""
        # Main container with canvas for scrolling
        main_canvas = tk.Canvas(self.parent, bg='white', highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.parent, orient='vertical', command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        main_canvas.pack(side='left', fill='both', expand=True)
        main_scrollbar.pack(side='right', fill='y')
        
        # Title
        title_frame = tk.Frame(scrollable_frame, bg='#1976D2', pady=15)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(
            title_frame,
            text="🎮 SKILL ROTATION BUILDER" if self.lang == 'en' else "🎮 XÂY DỰNG CHU KỲ CHIÊU THỨC",
            font=('Arial', 16, 'bold'),
            bg='#1976D2',
            fg='white'
        )
        title_label.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Build precise skill rotation with cooldown tracking" if self.lang == 'en' 
                 else "Xây dựng chu kỳ chiêu chính xác với theo dõi cooldown",
            font=('Arial', 10, 'italic'),
            bg='#1976D2',
            fg='#E3F2FD'
        )
        subtitle.pack()
        
        # Two-panel layout
        panels_frame = tk.Frame(scrollable_frame, bg='white')
        panels_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel: Available Skills
        self._build_available_skills_panel(panels_frame)
        
        # Right panel: Rotation Sequence
        self._build_rotation_sequence_panel(panels_frame)
        
        # Bottom: Analysis & Preview
        self._build_analysis_panel(scrollable_frame)
        
        # Action buttons
        self._build_action_buttons(scrollable_frame)
    
    def _build_available_skills_panel(self, parent):
        """Build left panel with available skills"""
        left_frame = tk.Frame(parent, bg='white')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Header
        header = tk.LabelFrame(
            left_frame,
            text="📚 " + ("Available Skills" if self.lang == 'en' else "Các Chiêu Có Sẵn"),
            font=('Arial', 11, 'bold'),
            bg='#E8F5E9',
            fg='#2E7D32',
            padx=10,
            pady=10
        )
        header.pack(fill='both', expand=True)
        
        # Scrollable skill list
        list_canvas = tk.Canvas(header, bg='white', highlightthickness=0, height=400)
        list_scrollbar = ttk.Scrollbar(header, orient='vertical', command=list_canvas.yview)
        self.skills_list_frame = tk.Frame(list_canvas, bg='white')
        
        self.skills_list_frame.bind(
            "<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        )
        
        list_canvas.create_window((0, 0), window=self.skills_list_frame, anchor='nw')
        list_canvas.configure(yscrollcommand=list_scrollbar.set)
        
        list_canvas.pack(side='left', fill='both', expand=True)
        list_scrollbar.pack(side='right', fill='y')
        
        # Placeholder
        placeholder = tk.Label(
            self.skills_list_frame,
            text="Loading skills..." if self.lang == 'en' else "Đang tải chiêu...",
            font=('Arial', 10, 'italic'),
            fg='#999',
            bg='white'
        )
        placeholder.pack(pady=20)
        
        # Add button
        add_btn_frame = tk.Frame(header, bg='#E8F5E9')
        add_btn_frame.pack(fill='x', pady=(10, 0))
        
        self.add_skills_btn = tk.Button(
            add_btn_frame,
            text="➜ " + ("Add Selected" if self.lang == 'en' else "Thêm Đã Chọn"),
            command=self._add_selected_skills,
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            padx=15,
            pady=8
        )
        self.add_skills_btn.pack(expand=True)
    
    def _build_rotation_sequence_panel(self, parent):
        """Build right panel with rotation sequence"""
        right_frame = tk.Frame(parent, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Header
        header = tk.LabelFrame(
            right_frame,
            text="🎯 " + ("Rotation Sequence" if self.lang == 'en' else "Thứ Tự Chiêu"),
            font=('Arial', 11, 'bold'),
            bg='#E3F2FD',
            fg='#1565C0',
            padx=10,
            pady=10
        )
        header.pack(fill='both', expand=True)
        
        # Scrollable sequence list
        seq_canvas = tk.Canvas(header, bg='white', highlightthickness=0, height=400)
        seq_scrollbar = ttk.Scrollbar(header, orient='vertical', command=seq_canvas.yview)
        self.sequence_list_frame = tk.Frame(seq_canvas, bg='white')
        
        self.sequence_list_frame.bind(
            "<Configure>",
            lambda e: seq_canvas.configure(scrollregion=seq_canvas.bbox("all"))
        )
        
        seq_canvas.create_window((0, 0), window=self.sequence_list_frame, anchor='nw')
        seq_canvas.configure(yscrollcommand=seq_scrollbar.set)
        
        seq_canvas.pack(side='left', fill='both', expand=True)
        seq_scrollbar.pack(side='right', fill='y')
        
        # Empty state
        self.empty_sequence_label = tk.Label(
            self.sequence_list_frame,
            text="No skills in rotation\nAdd skills from left panel" if self.lang == 'en' 
                 else "Chưa có chiêu nào\nThêm chiêu từ panel bên trái",
            font=('Arial', 10, 'italic'),
            fg='#999',
            bg='white',
            justify='center'
        )
        self.empty_sequence_label.pack(pady=50)
        
        # Control buttons
        control_frame = tk.Frame(header, bg='#E3F2FD')
        control_frame.pack(fill='x', pady=(10, 0))
        
        self.clear_btn = tk.Button(
            control_frame,
            text="🗑️ " + ("Clear All" if self.lang == 'en' else "Xóa Hết"),
            command=self._clear_rotation,
            font=('Arial', 9),
            bg='#F44336',
            fg='white',
            cursor='hand2',
            padx=10,
            pady=5
        )
        self.clear_btn.pack(side='left', padx=5)
        
        self.test_btn = tk.Button(
            control_frame,
            text="🔍 " + ("Preview" if self.lang == 'en' else "Xem Trước"),
            command=self._preview_rotation,
            font=('Arial', 9),
            bg='#2196F3',
            fg='white',
            cursor='hand2',
            padx=10,
            pady=5
        )
        self.test_btn.pack(side='left', padx=5)
    
    def _build_analysis_panel(self, parent):
        """Build analysis/preview panel"""
        analysis_frame = tk.LabelFrame(
            parent,
            text="📊 " + ("Rotation Analysis" if self.lang == 'en' else "Phân Tích Chu Kỳ"),
            font=('Arial', 11, 'bold'),
            bg='#FFF3E0',
            fg='#E65100',
            padx=10,
            pady=10
        )
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Analysis text widget
        self.analysis_text = tk.Text(
            analysis_frame,
            height=20,
            state='disabled',
            bg='white',
            font=('Consolas', 9),
            wrap='word',
            padx=10,
            pady=10
        )
        self.analysis_text.pack(fill='both', expand=True)
        
        # Default message
        self._update_analysis_text(
            "ℹ️  " + ("Add skills to rotation and click 'Calculate' to see analysis" if self.lang == 'en'
                      else "Thêm chiêu vào chu kỳ và bấm 'Tính Toán' để xem phân tích")
        )
    
    def _build_action_buttons(self, parent):
        """Build action buttons at bottom"""
        btn_frame = tk.Frame(parent, bg='white', pady=15)
        btn_frame.pack(fill='x', padx=10)
        
        self.calculate_btn = tk.Button(
            btn_frame,
            text="⚡ " + ("Calculate Rotation" if self.lang == 'en' else "Tính Toán Chu Kỳ"),
            command=self._calculate_rotation,
            font=('Arial', 12, 'bold'),
            bg='#FF9800',
            fg='white',
            cursor='hand2',
            padx=30,
            pady=12
        )
        self.calculate_btn.pack(side='left', padx=5)
        
        self.apply_btn = tk.Button(
            btn_frame,
            text="✅ " + ("Apply to Hunt Config" if self.lang == 'en' else "Áp Dụng Vào Hunt Config"),
            command=self._apply_rotation,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            padx=30,
            pady=12,
            state='disabled'
        )
        self.apply_btn.pack(side='left', padx=5)
        
        self.save_preset_btn = tk.Button(
            btn_frame,
            text="💾 " + ("Save as Preset" if self.lang == 'en' else "Lưu Thành Preset"),
            command=self._save_preset,
            font=('Arial', 10),
            bg='#607D8B',
            fg='white',
            cursor='hand2',
            padx=20,
            pady=10,
            state='disabled'
        )
        self.save_preset_btn.pack(side='right', padx=5)
    
    def _load_available_skills(self):
        """Load skills from library manager or hunt_config.json"""
        try:
            # Priority 1: Load from library manager's skills (for Setup Wizard context)
            if hasattr(self.lib_manager, 'skills') and self.lib_manager.skills:
                # Skills from library manager (master list)
                # Convert to skill_slots format if needed
                self.available_skills = []
                for skill in self.lib_manager.skills:
                    skill_slot = {
                        'name': skill.get('name', 'Unnamed'),
                        'key': skill.get('key', ''),
                        'cooldown': skill.get('cooldown', 0),
                        'cast_time': skill.get('cast_time', 0),  # FIX: Added cast_time
                        'type': skill.get('type', 'attack'),
                        'image': skill.get('image', '')  # FIX: Added image path
                    }
                    self.available_skills.append(skill_slot)
            else:
                # Priority 2: Fallback to hunt_config.json
                hunt_config_path = Path(__file__).parent.parent.parent / 'lib' / 'data' / 'hunt_config.json'
                
                if hunt_config_path.exists():
                    with open(hunt_config_path, 'r', encoding='utf-8') as f:
                        hunt_config = json.load(f)
                        self.available_skills = hunt_config.get('skill_slots', [])
            
            # Render skill checkboxes
            self._render_available_skills()
            
        except Exception as e:
            messagebox.showerror(
                "Error" if self.lang == 'en' else "Lỗi",
                f"Failed to load skills: {str(e)}"
            )
    
    def _render_available_skills(self):
        """Render skill checkboxes in left panel"""
        # Clear existing
        for widget in self.skills_list_frame.winfo_children():
            widget.destroy()
        
        if not self.available_skills:
            tk.Label(
                self.skills_list_frame,
                text="No skills found in hunt_config.json" if self.lang == 'en'
                     else "Không tìm thấy chiêu trong hunt_config.json",
                font=('Arial', 10, 'italic'),
                fg='#999',
                bg='white'
            ).pack(pady=20)
            return
        
        # Skill checkboxes
        self.skill_vars = {}
        
        for i, skill in enumerate(self.available_skills):
            skill_frame = tk.Frame(
                self.skills_list_frame,
                bg='#F5F5F5' if i % 2 == 0 else 'white',
                relief='flat',
                padx=10,
                pady=8
            )
            skill_frame.pack(fill='x', pady=1)
            
            # Checkbox
            var = tk.BooleanVar(value=False)
            self.skill_vars[skill['name']] = var
            
            cb = tk.Checkbutton(
                skill_frame,
                variable=var,
                bg=skill_frame['bg'],
                font=('Arial', 10)
            )
            cb.pack(side='left')
            
            # Skill info
            info_frame = tk.Frame(skill_frame, bg=skill_frame['bg'])
            info_frame.pack(side='left', fill='x', expand=True)
            
            name_label = tk.Label(
                info_frame,
                text=f"[{skill['key']}] {skill['name']}",
                font=('Arial', 10, 'bold'),
                bg=skill_frame['bg'],
                anchor='w'
            )
            name_label.pack(fill='x')
            
            type_color = '#FF5722' if skill['type'] == 'attack' else '#2196F3'
            type_label = tk.Label(
                info_frame,
                text=f"Type: {skill['type'].upper()} | CD: {skill['cooldown']}s | Cast: {skill['cast_time']}s",
                font=('Arial', 8),
                fg=type_color,
                bg=skill_frame['bg'],
                anchor='w'
            )
            type_label.pack(fill='x')
    
    def _add_selected_skills(self):
        """Add selected skills to rotation sequence"""
        selected = [
            skill for skill in self.available_skills
            if self.skill_vars.get(skill['name'], tk.BooleanVar()).get()
        ]
        
        if not selected:
            messagebox.showwarning(
                "Warning" if self.lang == 'en' else "Cảnh Báo",
                "Please select at least one skill" if self.lang == 'en'
                else "Vui lòng chọn ít nhất một chiêu"
            )
            return
        
        # Add to sequence
        self.rotation_sequence.extend(selected)
        
        # Uncheck added skills
        for skill in selected:
            self.skill_vars[skill['name']].set(False)
        
        # Render sequence
        self._render_rotation_sequence()
    
    def _render_rotation_sequence(self):
        """Render rotation sequence in right panel"""
        # Clear existing
        for widget in self.sequence_list_frame.winfo_children():
            widget.destroy()
        
        if not self.rotation_sequence:
            self.empty_sequence_label = tk.Label(
                self.sequence_list_frame,
                text="No skills in rotation\nAdd skills from left panel" if self.lang == 'en'
                     else "Chưa có chiêu nào\nThêm chiêu từ panel bên trái",
                font=('Arial', 10, 'italic'),
                fg='#999',
                bg='white',
                justify='center'
            )
            self.empty_sequence_label.pack(pady=50)
            return
        
        # Render each skill in sequence
        for i, skill in enumerate(self.rotation_sequence):
            self._render_sequence_item(i, skill)
    
    def _render_sequence_item(self, index: int, skill: dict):
        """Render a single skill in sequence"""
        item_frame = tk.Frame(
            self.sequence_list_frame,
            bg='#E3F2FD',
            relief='raised',
            borderwidth=1,
            padx=10,
            pady=8
        )
        item_frame.pack(fill='x', pady=2)
        
        # Index number
        num_label = tk.Label(
            item_frame,
            text=f"{index + 1}.",
            font=('Arial', 12, 'bold'),
            bg='#E3F2FD',
            width=3
        )
        num_label.pack(side='left')
        
        # Skill info
        info_frame = tk.Frame(item_frame, bg='#E3F2FD')
        info_frame.pack(side='left', fill='x', expand=True)
        
        name_label = tk.Label(
            info_frame,
            text=f"[{skill['key']}] {skill['name']}",
            font=('Arial', 10, 'bold'),
            bg='#E3F2FD',
            anchor='w'
        )
        name_label.pack(fill='x')
        
        type_color = '#FF5722' if skill['type'] == 'attack' else '#2196F3'
        details = tk.Label(
            info_frame,
            text=f"⏱️  {skill['cast_time']}s cast | 🔄 {skill['cooldown']}s CD | Type: {skill['type']}",
            font=('Arial', 8),
            fg=type_color,
            bg='#E3F2FD',
            anchor='w'
        )
        details.pack(fill='x')
        
        # Control buttons
        btn_frame = tk.Frame(item_frame, bg='#E3F2FD')
        btn_frame.pack(side='right')
        
        # Move up
        if index > 0:
            up_btn = tk.Button(
                btn_frame,
                text="▲",
                command=lambda: self._move_skill(index, -1),
                font=('Arial', 8),
                bg='#90CAF9',
                fg='white',
                cursor='hand2',
                width=3
            )
            up_btn.pack(side='left', padx=2)
        
        # Move down
        if index < len(self.rotation_sequence) - 1:
            down_btn = tk.Button(
                btn_frame,
                text="▼",
                command=lambda: self._move_skill(index, 1),
                font=('Arial', 8),
                bg='#90CAF9',
                fg='white',
                cursor='hand2',
                width=3
            )
            down_btn.pack(side='left', padx=2)
        
        # Remove
        remove_btn = tk.Button(
            btn_frame,
            text="✕",
            command=lambda: self._remove_skill(index),
            font=('Arial', 8, 'bold'),
            bg='#EF5350',
            fg='white',
            cursor='hand2',
            width=3
        )
        remove_btn.pack(side='left', padx=2)
    
    def _move_skill(self, index: int, direction: int):
        """Move skill up or down in sequence"""
        new_index = index + direction
        if 0 <= new_index < len(self.rotation_sequence):
            # Swap
            self.rotation_sequence[index], self.rotation_sequence[new_index] = \
                self.rotation_sequence[new_index], self.rotation_sequence[index]
            self._render_rotation_sequence()
    
    def _remove_skill(self, index: int):
        """Remove skill from sequence"""
        del self.rotation_sequence[index]
        self._render_rotation_sequence()
    
    def _clear_rotation(self):
        """Clear entire rotation"""
        if self.rotation_sequence:
            confirm = messagebox.askyesno(
                "Confirm" if self.lang == 'en' else "Xác Nhận",
                "Clear all skills from rotation?" if self.lang == 'en'
                else "Xóa tất cả chiêu khỏi chu kỳ?"
            )
            if confirm:
                self.rotation_sequence = []
                self._render_rotation_sequence()
                self.current_rotation = None
                self.apply_btn.config(state='disabled')
                self.save_preset_btn.config(state='disabled')
    
    def _preview_rotation(self):
        """Preview current rotation without calculating"""
        if not self.rotation_sequence:
            messagebox.showwarning(
                "Warning" if self.lang == 'en' else "Cảnh Báo",
                "No skills in rotation" if self.lang == 'en'
                else "Chưa có chiêu nào trong chu kỳ"
            )
            return
        
        # Show simple preview
        preview_text = ("📋 Current Rotation Sequence:\n" if self.lang == 'en'
                       else "📋 Thứ Tự Chiêu Hiện Tại:\n")
        preview_text += "─" * 50 + "\n"
        
        for i, skill in enumerate(self.rotation_sequence, 1):
            preview_text += f"{i}. [{skill['key']}] {skill['name']}\n"
            preview_text += f"   Type: {skill['type']} | CD: {skill['cooldown']}s | Cast: {skill['cast_time']}s\n\n"
        
        self._update_analysis_text(preview_text)
    
    def _calculate_rotation(self):
        """Calculate rotation timing"""
        if not self.rotation_sequence:
            messagebox.showwarning(
                "Warning" if self.lang == 'en' else "Cảnh Báo",
                "Please add skills to rotation first" if self.lang == 'en'
                else "Vui lòng thêm chiêu vào chu kỳ trước"
            )
            return
        
        try:
            # Calculate rotation
            self.current_rotation = calculate_rotation_timing(self.rotation_sequence)
            
            # Generate preview
            preview_text = generate_rotation_preview(self.current_rotation)
            self._update_analysis_text(preview_text)
            
            # Enable apply button
            self.apply_btn.config(state='normal')
            self.save_preset_btn.config(state='normal')
            
            messagebox.showinfo(
                "Success" if self.lang == 'en' else "Thành Công",
                f"Rotation calculated successfully!\nTotal cycle: {self.current_rotation.total_cycle_time:.2f}s"
                if self.lang == 'en' else
                f"Đã tính toán chu kỳ thành công!\nThời gian: {self.current_rotation.total_cycle_time:.2f}s"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error" if self.lang == 'en' else "Lỗi",
                f"Calculation failed: {str(e)}"
            )
    
    def _apply_rotation(self):
        """Apply rotation to hunt_config.json"""
        if not self.current_rotation:
            messagebox.showwarning(
                "Warning" if self.lang == 'en' else "Cảnh Báo",
                "Please calculate rotation first" if self.lang == 'en'
                else "Vui lòng tính toán chu kỳ trước"
            )
            return
        
        try:
            # Load hunt_config
            hunt_config_path = Path(__file__).parent.parent.parent / 'lib' / 'data' / 'hunt_config.json'
            
            with open(hunt_config_path, 'r', encoding='utf-8') as f:
                hunt_config = json.load(f)
            
            # Update with rotation data
            hunt_config['skill_rotation'] = {
                'enabled': True,
                'sequence': self.rotation_sequence,
                'total_cycle_time': self.current_rotation.total_cycle_time,
                'attack_interval': self.current_rotation.attack_interval,
                'attack_press_ms': self.current_rotation.attack_press_ms,
                'rotation_cycle_ms': self.current_rotation.rotation_cycle_ms
            }
            
            # Also update individual timing settings for backward compatibility
            hunt_config['attack_interval'] = self.current_rotation.attack_interval
            hunt_config['attack_press_ms'] = self.current_rotation.attack_press_ms
            
            # Save
            with open(hunt_config_path, 'w', encoding='utf-8') as f:
                json.dump(hunt_config, f, indent=2, ensure_ascii=False)
            
            # Show execution preview
            exec_preview = generate_execution_preview(self.current_rotation)
            self._update_analysis_text(exec_preview)
            
            messagebox.showinfo(
                "Success" if self.lang == 'en' else "Thành Công",
                "Rotation applied to hunt_config.json successfully!" if self.lang == 'en'
                else "Đã áp dụng chu kỳ vào hunt_config.json thành công!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error" if self.lang == 'en' else "Lỗi",
                f"Failed to apply rotation: {str(e)}"
            )
    
    def _save_preset(self):
        """Save rotation as preset (for future feature)"""
        messagebox.showinfo(
            "Coming Soon" if self.lang == 'en' else "Sắp Ra Mắt",
            "Preset saving feature coming soon!" if self.lang == 'en'
            else "Tính năng lưu preset sắp ra mắt!"
        )
    
    def _update_analysis_text(self, text: str):
        """Update analysis text widget"""
        self.analysis_text.config(state='normal')
        self.analysis_text.delete('1.0', 'end')
        self.analysis_text.insert('1.0', text)
        self.analysis_text.config(state='disabled')


def integrate_rotation_builder(library_manager, notebook: ttk.Notebook):
    """
    Integrate Skill Rotation Builder into Library Manager
    
    Args:
        library_manager: LibraryManager instance
        notebook: ttk.Notebook to add tab to
    """
    # Create tab
    rotation_frame = tk.Frame(notebook, bg='white')
    notebook.add(
        rotation_frame,
        text="🎮 Skill Rotation" if library_manager.lang == 'en' else "🎮 Chu Kỳ Chiêu"
    )
    
    # Create UI
    rotation_ui = SkillRotationUI(rotation_frame, library_manager)
    
    return rotation_ui
