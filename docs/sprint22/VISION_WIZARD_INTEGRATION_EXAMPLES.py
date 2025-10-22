"""
Example: Cách tích hợp Vision Wizard vào form chính
File này chứa các ví dụ code để tham khảo
"""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

# ============================================================
# VÍ DỤ 1: Tích hợp vào app_gui.py (Main Application)
# ============================================================

"""
Thêm vào đầu file app_gui.py:
"""

from ui.setup_wizard_vision import open_vision_wizard_from_parent

"""
Trong class AutoHuntApp hoặc tương đương, thêm method:
"""

def open_vision_wizard(self):
    """Mở Vision Wizard"""
    try:
        open_vision_wizard_from_parent(self.root)
    except Exception as e:
        messagebox.showerror('Error', f'Không thể mở Vision Wizard: {e}')

"""
Bind hotkey trong __init__ method:
"""

def __init__(self):
    # ... existing code ...
    
    # Bind Vision Wizard hotkey (Ctrl+Shift+L)
    self.root.bind('<Control-Shift-L>', lambda e: self.open_vision_wizard())
    
    print("Vision Wizard hotkey: Ctrl+Shift+L")


# ============================================================
# VÍ DỤ 2: Thêm menu item
# ============================================================

"""
Nếu có menubar, thêm menu item:
"""

def create_menubar(self):
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)
    
    # ... existing menus ...
    
    # Vision menu
    vision_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Vision', menu=vision_menu)
    
    vision_menu.add_command(
        label='Open Vision Wizard',
        accelerator='Ctrl+Shift+L',
        command=self.open_vision_wizard
    )
    
    vision_menu.add_separator()
    
    vision_menu.add_command(
        label='Template Settings',
        command=self.open_template_settings
    )


# ============================================================
# VÍ DỤ 3: Thêm button vào toolbar
# ============================================================

"""
Thêm button vào toolbar nếu có:
"""

def create_toolbar(self, parent):
    toolbar = tk.Frame(parent, bg='#f0f0f0', height=50)
    toolbar.pack(fill='x', side='top')
    
    # ... existing buttons ...
    
    # Vision Wizard button
    btn_vision = ttk.Button(
        toolbar,
        text='🔍 Vision Wizard',
        command=self.open_vision_wizard
    )
    btn_vision.pack(side='left', padx=5, pady=5)
    
    # Tooltip
    from lib.ui.tooltip import attach_i18n_tooltip
    attach_i18n_tooltip(
        btn_vision,
        'tooltip_vision_wizard',
        ns='main_app',
        default='Mở Vision Wizard để quản lý template và nhận diện (Ctrl+Shift+L)'
    )


# ============================================================
# VÍ DỤ 4: Tích hợp vào setup_wizard.py
# ============================================================

"""
Nếu muốn mở Vision Wizard từ Setup Wizard:
"""

def create_advanced_options(self, parent):
    """Tạo panel Advanced Options trong setup wizard"""
    
    advanced_frame = ttk.LabelFrame(parent, text='Advanced Options', padding=10)
    advanced_frame.pack(fill='x', pady=10)
    
    # Button mở Vision Wizard
    btn_vision = ttk.Button(
        advanced_frame,
        text='⚙️ Configure Vision System',
        command=self.open_vision_wizard_from_setup
    )
    btn_vision.pack(pady=5)
    
    tk.Label(
        advanced_frame,
        text='Cấu hình nhận diện hình ảnh và tracking quái vật',
        font=('Segoe UI', 9),
        fg='gray'
    ).pack()

def open_vision_wizard_from_setup(self):
    """Mở Vision Wizard từ Setup Wizard"""
    from ui.setup_wizard_vision import create_or_show_vision_wizard
    
    # Tạo wizard với parent là self (Setup Wizard window)
    wizard = create_or_show_vision_wizard(
        self,  # parent
        config_path='lib/data/config.json',
        on_close=self.on_vision_wizard_closed
    )
    
def on_vision_wizard_closed(self):
    """Callback khi Vision Wizard đóng"""
    print('Vision Wizard closed')
    # Có thể refresh data hoặc update UI nếu cần


# ============================================================
# VÍ DỤ 5: Tích hợp với Hunt Tab
# ============================================================

"""
Trong Hunt Tab, thêm quick access button:
"""

def create_hunt_controls(self, parent):
    """Tạo controls cho hunt tab"""
    
    control_frame = tk.Frame(parent)
    control_frame.pack(fill='x', pady=10)
    
    # Left side: Start/Stop buttons
    left_frame = tk.Frame(control_frame)
    left_frame.pack(side='left', fill='x', expand=True)
    
    btn_start = ttk.Button(left_frame, text='Start Hunt', command=self.start_hunt)
    btn_start.pack(side='left', padx=5)
    
    btn_stop = ttk.Button(left_frame, text='Stop Hunt', command=self.stop_hunt)
    btn_stop.pack(side='left', padx=5)
    
    # Right side: Vision Wizard button (quick access)
    right_frame = tk.Frame(control_frame)
    right_frame.pack(side='right')
    
    btn_vision = ttk.Button(
        right_frame,
        text='🔍 Vision',
        command=self.open_vision_wizard_quick,
        width=10
    )
    btn_vision.pack(side='right', padx=5)

def open_vision_wizard_quick(self):
    """Quick access to Vision Wizard from Hunt tab"""
    from ui.setup_wizard_vision import create_or_show_vision_wizard
    
    wizard = create_or_show_vision_wizard(self.root)
    
    # Optionally: auto-select monster tracking mode
    # wizard.search_mode_combo.current(2)  # Select "region" mode


# ============================================================
# VÍ DỤ 6: Sử dụng callback để nhận kết quả tracking
# ============================================================

"""
Khi Vision Wizard tracking được quái vật, gửi signal đến main app:
"""

def start_hunt_with_vision_tracking(self):
    """Bắt đầu hunt với vision tracking"""
    
    from ui.setup_wizard_vision import get_vision_wizard_instance
    
    # Lấy instance hiện tại (nếu có)
    vision_wizard = get_vision_wizard_instance()
    
    if vision_wizard and vision_wizard.winfo_exists():
        # Đã mở Vision Wizard, check nếu đang tracking
        if hasattr(vision_wizard, 'is_tracking') and vision_wizard.is_tracking:
            print('Vision tracking is active')
            
            # Set callback để nhận tracking results
            vision_wizard.on_target_found = self.on_monster_detected
            vision_wizard.on_target_lost = self.on_monster_lost
        else:
            print('Vision Wizard opened but not tracking')
            messagebox.showinfo(
                'Info',
                'Please start tracking in Vision Wizard first'
            )
    else:
        print('Vision Wizard not opened')
        messagebox.showinfo(
            'Info',
            'Please open Vision Wizard (Ctrl+Shift+L) and configure tracking'
        )

def on_monster_detected(self, tracking_result):
    """
    Callback khi Vision Wizard phát hiện quái vật
    
    Args:
        tracking_result: Dict với keys:
            - template_name: str
            - position: (x, y)
            - size: (width, height)
            - confidence: float
            - timestamp: float
    """
    print(f"Monster detected: {tracking_result['template_name']}")
    print(f"Position: {tracking_result['position']}")
    print(f"Confidence: {tracking_result['confidence']:.2%}")
    
    # TODO: Trigger skill rotation
    # self.skill_rotation.execute_at_target(tracking_result['position'])
    
def on_monster_lost(self):
    """Callback khi mất tracking"""
    print('Monster lost, searching...')
    # TODO: Stop skill rotation, search for new target


# ============================================================
# VÍ DỤ 7: Đóng Vision Wizard khi thoát app
# ============================================================

"""
Trong main window, xử lý cleanup:
"""

def on_closing(self):
    """Xử lý khi đóng app"""
    
    from ui.setup_wizard_vision import get_vision_wizard_instance
    
    # Đóng Vision Wizard nếu đang mở
    vision_wizard = get_vision_wizard_instance()
    if vision_wizard and vision_wizard.winfo_exists():
        vision_wizard.destroy()
    
    # ... cleanup other resources ...
    
    self.root.destroy()


# ============================================================
# VÍ DỤ 8: Load vision config khi khởi động
# ============================================================

"""
Khi app khởi động, load vision config:
"""

def load_vision_config(self):
    """Load vision configuration"""
    
    config_path = 'lib/data/config.json'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Get vision settings
            vision_config = config.get('vision', {})
            templates = vision_config.get('templates', [])
            
            print(f'Loaded {len(templates)} templates from config')
            
            # Store in app
            self.vision_templates = templates
            self.vision_default_threshold = vision_config.get('default_threshold', 0.7)
            
        except Exception as e:
            print(f'Error loading vision config: {e}')
    else:
        print('No vision config found, using defaults')
        self.vision_templates = []
        self.vision_default_threshold = 0.7


# ============================================================
# VÍ DỤ 9: Test vision wizard đơn giản
# ============================================================

"""
Test script độc lập:
"""

if __name__ == '__main__':
    import tkinter as tk
    from ui.setup_wizard_vision import create_or_show_vision_wizard
    
    # Tạo root window
    root = tk.Tk()
    root.title('Vision Wizard Test')
    root.geometry('300x200')
    
    # Button test
    def open_wizard():
        wizard = create_or_show_vision_wizard(root)
        print(f'Wizard instance: {wizard}')
    
    btn = tk.Button(
        root,
        text='Open Vision Wizard',
        command=open_wizard,
        font=('Segoe UI', 12),
        width=20,
        height=3
    )
    btn.pack(expand=True)
    
    # Hotkey
    root.bind('<Control-Shift-L>', lambda e: open_wizard())
    
    print('Test app started')
    print('Click button or press Ctrl+Shift+L to open Vision Wizard')
    
    root.mainloop()


# ============================================================
# VÍ DỤ 10: Custom styling cho Vision Wizard
# ============================================================

"""
Tùy chỉnh style nếu cần:
"""

def apply_custom_vision_wizard_style(wizard):
    """Áp dụng custom style cho Vision Wizard"""
    
    # Change header color
    for child in wizard.winfo_children():
        if isinstance(child, tk.Frame):
            try:
                if child.cget('bg') == '#2196F3':  # Header frame
                    child.config(bg='#1565C0')  # Darker blue
            except:
                pass
    
    # Change window size
    wizard.geometry('1000x800')
    
    # Change transparency (if needed)
    # wizard.attributes('-alpha', 0.95)


# ============================================================
# NOTES & BEST PRACTICES
# ============================================================

"""
✅ DO:
- Luôn sử dụng create_or_show_vision_wizard() để đảm bảo singleton
- Bind hotkey Ctrl+Shift+L cho quick access
- Xử lý exceptions khi mở wizard
- Cleanup wizard khi đóng app
- Test hotkey và singleton behavior

❌ DON'T:
- Không tạo instance trực tiếp: VisionWizard(parent) 
  → Sử dụng create_or_show_vision_wizard()
- Không quên cleanup khi thoát
- Không hardcode config paths
- Không block main thread với tracking loop

📝 TODO sau này:
- Tích hợp với OpenCV template matching
- Implement ROI selection
- Implement monster tracking
- Implement overlay system
- Kết nối với skill rotation system
"""

