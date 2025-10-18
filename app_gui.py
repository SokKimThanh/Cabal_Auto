import ctypes
import json
import math
import os
import threading
import time
import copy
from ctypes import wintypes
from pathlib import Path
from typing import Dict, List, Optional

import pyautogui
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from lib.template_matcher import locate_template
from lib.skill_runtime import SkillRuntime

try:
    from PIL import Image, ImageTk, ImageDraw  # type: ignore
except Exception:
    Image = None
    ImageTk = None
    ImageDraw = None

try:
    import keyboard  # type: ignore
except Exception:
    keyboard = None  # type: ignore

from lib.win_input import tap
from lib.hunt_logger import get_hunt_logger
from lib.timing_calculator import calculate_timing, format_timing_recommendation, get_timing_presets
from setup_wizard import show_setup_wizard


class ToolTip:
    """Simple tooltip helper for Tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("tahoma", "8", "normal"), padx=4, pady=2)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


LANG: Dict[str, Dict[str, str]] = {
    'en': {
        'app_title': 'Cabal Auto Manager',
        'language': 'Language',
        'tab_hunt': 'Hunt',
        'window_title_contains': 'Window title contains:',
        'find_windows': 'Find windows',
        'bring_to_front': 'Bring to front',
        'win_list_label': 'Filtered window list:',
        'target_key': 'Target key:',
        'attack_keys': 'Attack keys (comma separated):',
        'press_ms': 'Key press (ms):',
        'target_cycle': 'Target cycle (s):',
        'search_interval': 'Search interval (s):',
        'attack_interval': 'Attack interval (s):',
        'lost_timeout': 'Extra attack after lost (s):',
        'attack_duration': 'Minimum attack duration (s):',
        'template': 'Target template:',
        'browse': 'Browse',
        'region_l': 'Region L',
        't': 'T',
        'w': 'W',
        'h': 'H',
        'bring_each_cycle': 'Bring window to front each loop (only if needed)',
        'pick_tl': 'Pick top-left (3s)',
        'pick_br': 'Pick bottom-right (3s)',
        'save_hunt': 'Save hunt config',
        'start_hunt': 'Start hunt',
        'stop_hunt': 'Stop hunt',
        'setup_wizard': '🧙 Setup Wizard',
        'wizard_first_time_title': 'Welcome to Cabal Auto Hunt!',
        'wizard_first_time_message': (
            "It looks like this is your first time using Cabal Auto Hunt.\n\n"
            "Would you like to run the Setup Wizard to configure your settings?\n\n"
            "The wizard will guide you through:\n"
            "  • Selecting your game window\n"
            "  • Choosing a monster to hunt\n"
            "  • Configuring your attack skills\n\n"
            "You can always run the wizard later by clicking the '🧙 Setup Wizard' button."
        ),
        'wizard_skipped_hint': "Setup wizard skipped. Click '🧙 Setup Wizard' button to run it later.",
        'hunt_idle': 'Ready to hunt',
        'hunt_running': 'Hunting…',
        'hunt_stopped': 'Hunt stopped',
        'hunt_mode': 'Interface Mode',
        'mode_beginner': '🌱 Beginner',
        'mode_beginner_desc': 'Simple 4-step workflow - perfect for first-time users',
        'mode_intermediate': '⚙️ Intermediate',
        'mode_intermediate_desc': 'Basic fields + timing controls for experienced users',
        'mode_advanced': '🔧 Advanced',
        'mode_advanced_desc': 'Full control - all parameters and technical settings',
        'selected_window': 'Selected window: {title}',
        'bring_ok': 'Brought to front',
        'bring_fail': 'Unable to bring to front',
        'invalid_hunt': 'Invalid hunt config: {e}',
        'no_windows': 'No window matched',
        'error_title': 'Error',
        'error_copy_image': 'Failed to copy image: {exc}',
        'error_pil_required': 'PIL required for preview',
        'error_preview': 'Preview error: {exc}',
        'monster_section': 'Monster library',
        'monster_list': 'Monsters:',
        'monster_name': 'Name:',
        'monster_hp': 'HP:',
        'monster_damage': 'Damage per hit:',
        'monster_calculate_timing': 'Calculate Timing',
        'monster_timing_title': 'Timing Recommendations',
        'monster_timing_no_stats': 'Please enter HP and Damage per hit values first.',
        'monster_template': 'Template:',
    'monster_description': 'Description:',
    'monster_description_hint': 'Optional notes about this monster or spawn location.',
    'monster_bounds': 'Window bounds (L,T,W,H):',
    'monster_bounds_hint': 'Leave blank to auto-detect during hunt.',
    'monster_bounds_clear': 'Clear bounds',
    'monster_open_templates': 'Quick-add template…',
    'monster_templates': 'Templates',
    'monster_template_list': 'Template variants:',
    'monster_template_name': 'Label:',
    'monster_template_path': 'Image path:',
    'monster_template_threshold': 'Threshold:',
    'monster_template_threshold_hint': 'Match score between 0 and 1 (default 0.85).',
    'monster_template_region': 'Region override (L,T,W,H):',
    'monster_template_region_hint': 'Leave blank to reuse hunt window bounds.',
    'monster_template_browse': 'Browse image…',
    'monster_template_capture': 'Capture screenshot',
    'monster_template_capture_hint': 'Instructions:\n1. Click button and wait 3s\n2. Select region by dragging rectangle\n3. Image will be saved automatically',
    'monster_template_capture_wait': 'Position window... (3s)',
    'monster_template_capture_select': 'Drag to select region...',
    'monster_template_capture_success': 'Screenshot saved: {filename}',
    'monster_template_capture_cancelled': 'Capture cancelled',
    'monster_template_preview_overlay': 'Preview with overlay',
    'monster_template_test_recognition': 'Test Recognition',
    'monster_template_test_hint': 'Test template matching on current screen',
    'monster_template_test_running': 'Testing recognition...',
    'monster_template_test_found': 'Match found at ({x}, {y}) - Confidence: {conf:.2f}',
    'monster_template_test_not_found': 'No match found (threshold: {threshold})',
    'monster_template_test_error': 'Test failed: {error}',
    'monster_template_no_image': 'No template image selected',
    'monster_template_add': 'Add',
    'monster_template_update': 'Update',
    'monster_template_delete': 'Delete',
    'monster_template_invalid': 'Invalid template data: {e}',
    'monster_template_not_selected': 'Pick a template first',
    'monster_template_duplicate': 'Template name already exists',
    'monster_template_added': 'Template added',
    'monster_template_saved': 'Template updated',
    'monster_template_removed': 'Template removed',
        'monster_new': 'Create',
        'monster_save': 'Save',
        'monster_delete': 'Delete',
        'monster_use_template': 'Apply to hunt',
        'monster_estimate': 'Estimate kill time',
        'close': 'Close',
        'monster_estimate_result': 'Estimated time: {time:.2f}s (DPS {dps:.1f})',
        'monster_estimate_detail': '{base} -> minimum attack {attack:.2f}s, keep hitting {lost:.2f}s',
        'monster_saved': 'Monster saved',
        'monster_deleted': 'Monster deleted',
        'monster_invalid': 'Invalid monster data: {e}',
        'monster_not_selected': 'Pick a monster first',
        'monster_applied': 'Applied to hunt config',
        'monster_duplicate': 'Monster name already exists',
    'hunt_window_bounds': 'Saved window bounds: {value}',
    'hunt_window_bounds_none': 'Saved window bounds: not set',
        'hunt_monster_select': 'Quick select monster:',
        'hunt_monster_auto_applied': 'Auto-applied: {name}',
        'hunt_template_active': 'Active template: {name}',
        'tooltip_threshold': 'Match confidence: 0.0 (any) to 1.0 (exact). Higher = stricter matching. Recommended: 0.80-0.90',
        'tooltip_region_strategy': 'Window: use game window bounds\nCustom: use specific region below',
        'tooltip_window_bounds': 'Game window area (Left, Top, Width, Height). Leave blank to auto-detect.',
        'tooltip_lost_timeout': 'Keep attacking this long after losing visual on target (prevents premature target switch)',
        'tooltip_attack_duration': 'Minimum attack time even if target lost early (ensures skill combos complete)',
        'error_invalid_number': 'Invalid number: {field}',
        'error_value_must_be_positive': '{field} must be greater than 0',
        'error_threshold_range': 'Threshold must be between 0.0 and 1.0',
        'skill_section': 'Skill library',
        'skill_list': 'Skills:',
        'skill_name': 'Name:',
        'skill_key': 'Key:',
        'skill_type': 'Type:',
        'skill_type_attack': 'Attack',
        'skill_type_buff': 'Buff',
        'skill_cooldown': 'Cooldown (s):',
        'skill_cast_time': 'Cast time (s):',
        'skill_duration': 'Buff duration (s):',
        'skill_pre_refresh': 'Pre-refresh (s):',
        'skill_duration_hint': 'How long the buff lasts (0 for attack skills)',
        'skill_pre_refresh_hint': 'Recast before expiration (e.g., 5s = recast 5s early)',
        'skill_image': 'Skill image:',
        'skill_no_image': 'No image',
        'skill_image_error': 'Cannot preview image',
        'skill_new': 'Create',
        'skill_save': 'Save',
        'skill_delete': 'Delete',
        'skill_saved': 'Skill saved',
        'skill_deleted': 'Skill deleted',
        'skill_invalid': 'Invalid skill data: {e}',
        'skill_not_selected': 'Pick a skill first',
        'skill_slots': 'Skill slots',
        'skill_slot_label': 'Slot {i}:',
        'skill_slot_clear': 'Clear',
        'skill_estimate_missing': 'Missing skill info',
        'skill_duplicate': 'Skill name already exists',
        'manage_button': 'Manage…',
        'skill_manage': 'Manage skills…',
    },
    'vi': {
        'app_title': 'Trợ lý săn Cabal',
        'language': 'Ngôn ngữ',
        'tab_hunt': 'Săn',
        'window_title_contains': 'Tiêu đề cửa sổ chứa:',
        'find_windows': 'Tìm cửa sổ',
        'bring_to_front': 'Đưa lên trước',
        'win_list_label': 'Danh sách cửa sổ (đã lọc):',
        'target_key': 'Phím chọn mục tiêu:',
        'attack_keys': 'Phím đánh (cách nhau bằng dấu phẩy):',
        'press_ms': 'Giữ phím (ms):',
        'target_cycle': 'Chu kỳ đổi mục tiêu (s):',
        'search_interval': 'Chu kỳ tìm (s):',
        'attack_interval': 'Chu kỳ đánh (s):',
        'lost_timeout': 'Giữ đánh thêm (giây):',
        'attack_duration': 'Thời gian đánh tối thiểu (giây):',
        'template': 'Ảnh mẫu:',
        'browse': 'Chọn ảnh',
        'region_l': 'Vùng tìm: L',
        't': 'T',
        'w': 'R',
        'h': 'D',
        'bring_each_cycle': 'Đưa cửa sổ lên mỗi vòng (chỉ dùng khi cần)',
        'pick_tl': 'Chọn góc trái trên (3s)',
        'pick_br': 'Chọn góc phải dưới (3s)',
        'save_hunt': 'Lưu cấu hình săn',
        'start_hunt': 'Bắt đầu săn',
        'stop_hunt': 'Dừng săn',
        'setup_wizard': '🧙 Trợ lý thiết lập',
        'wizard_first_time_title': 'Chào mừng đến Cabal Auto Hunt!',
        'wizard_first_time_message': (
            "Có vẻ đây là lần đầu bạn sử dụng Cabal Auto Hunt.\n\n"
            "Bạn có muốn chạy Trợ lý thiết lập để cấu hình không?\n\n"
            "Trợ lý sẽ hướng dẫn bạn:\n"
            "  • Chọn cửa sổ game\n"
            "  • Chọn quái để săn\n"
            "  • Cấu hình kỹ năng tấn công\n\n"
            "Bạn luôn có thể chạy trợ lý sau bằng nút '🧙 Trợ lý thiết lập'."
        ),
        'wizard_skipped_hint': "Đã bỏ qua trợ lý. Nhấn nút '🧙 Trợ lý thiết lập' để chạy sau.",
        'hunt_idle': 'Sẵn sàng săn',
        'hunt_running': 'Đang săn…',
        'hunt_stopped': 'Đã dừng săn',
        'hunt_mode': 'Chế độ giao diện',
        'mode_beginner': '🌱 Người mới',
        'mode_beginner_desc': 'Quy trình 4 bước đơn giản - hoàn hảo cho người dùng lần đầu',
        'mode_intermediate': '⚙️ Trung cấp',
        'mode_intermediate_desc': 'Các trường cơ bản + điều khiển thời gian cho người dùng có kinh nghiệm',
        'mode_advanced': '🔧 Nâng cao',
        'mode_advanced_desc': 'Toàn quyền kiểm soát - tất cả các tham số và cài đặt kỹ thuật',
        'selected_window': 'Đã chọn cửa sổ: {title}',
        'bring_ok': 'Đã đưa lên trên',
        'bring_fail': 'Không thể đưa lên trên',
        'invalid_hunt': 'Cấu hình săn không hợp lệ: {e}',
        'no_windows': 'Không tìm thấy cửa sổ',
        'error_title': 'Lỗi',
        'error_copy_image': 'Không sao chép được ảnh: {exc}',
        'error_pil_required': 'Cần cài PIL để xem trước',
        'error_preview': 'Lỗi xem trước: {exc}',
        'hunt_stopped': 'Đã dừng săn',
        'selected_window': 'Đã chọn cửa sổ: {title}',
        'bring_ok': 'Đã đưa lên trước',
        'bring_fail': 'Không đưa lên trước được',
        'invalid_hunt': 'Cấu hình săn không hợp lệ: {e}',
        'no_windows': 'Không tìm thấy cửa sổ phù hợp',
        'monster_section': 'Thư viện quái',
        'monster_list': 'Danh sách quái:',
        'monster_name': 'Tên:',
        'monster_hp': 'HP:',
        'monster_damage': 'Sát thương mỗi đòn:',
        'monster_calculate_timing': 'Tính thời gian',
        'monster_timing_title': 'Khuyến nghị thời gian',
        'monster_timing_no_stats': 'Vui lòng nhập HP và Sát thương trước.',
        'monster_template': 'Ảnh template:',
    'monster_description': 'Mô tả:',
    'monster_description_hint': 'Ghi chú thêm về quái hoặc vị trí spawn (tùy chọn).',
    'monster_bounds': 'Biên cửa sổ (L,T,R,D):',
    'monster_bounds_hint': 'Để trống để hệ thống tự dò khi chạy săn.',
    'monster_bounds_clear': 'Xóa biên',
    'monster_open_templates': 'Thêm ảnh mẫu nhanh…',
    'monster_templates': 'Ảnh mẫu',
    'monster_template_list': 'Danh sách ảnh mẫu:',
    'monster_template_name': 'Tên hiển thị:',
    'monster_template_path': 'Đường dẫn ảnh:',
    'monster_template_threshold': 'Ngưỡng:',
    'monster_template_threshold_hint': 'Điểm khớp từ 0 đến 1 (mặc định 0.85).',
    'monster_template_region': 'Vùng ghi đè (L,T,R,D):',
    'monster_template_region_hint': 'Để trống để dùng lại biên cửa sổ săn.',
    'monster_template_browse': 'Chọn ảnh…',
    'monster_template_capture': 'Chụp màn hình',
    'monster_template_capture_hint': 'Hướng dẫn:\n1. Nhấn nút và đợi 3 giây\n2. Chọn vùng bằng cách kéo hình chữ nhật\n3. Ảnh sẽ tự động lưu',
    'monster_template_capture_wait': 'Chuẩn bị cửa sổ... (3s)',
    'monster_template_capture_select': 'Kéo để chọn vùng...',
    'monster_template_capture_success': 'Đã lưu ảnh: {filename}',
    'monster_template_capture_cancelled': 'Đã hủy chụp',
    'monster_template_preview_overlay': 'Xem trước với overlay',
    'monster_template_test_recognition': 'Kiểm tra nhận diện',
    'monster_template_test_hint': 'Test khớp ảnh mẫu trên màn hình hiện tại',
    'monster_template_test_running': 'Đang kiểm tra...',
    'monster_template_test_found': 'Tìm thấy tại ({x}, {y}) - Độ khớp: {conf:.2f}',
    'monster_template_test_not_found': 'Không tìm thấy (ngưỡng: {threshold})',
    'monster_template_test_error': 'Lỗi kiểm tra: {error}',
    'monster_template_no_image': 'Chưa chọn ảnh mẫu',
    'monster_template_add': 'Thêm',
    'monster_template_update': 'Cập nhật',
    'monster_template_delete': 'Xóa',
    'monster_template_invalid': 'Thông tin ảnh mẫu không hợp lệ: {e}',
    'monster_template_not_selected': 'Hãy chọn một ảnh mẫu trước',
    'monster_template_duplicate': 'Tên ảnh mẫu đã tồn tại',
    'monster_template_added': 'Đã thêm ảnh mẫu',
    'monster_template_saved': 'Đã cập nhật ảnh mẫu',
    'monster_template_removed': 'Đã xóa ảnh mẫu',
        'monster_new': 'Tạo mới',
        'monster_save': 'Lưu',
        'monster_delete': 'Xóa',
        'monster_use_template': 'Áp dụng săn',
        'monster_estimate': 'Tính thời gian hạ',
        'close': 'Đóng',
        'monster_estimate_result': 'Thời gian ước tính: {time:.2f}s (DPS {dps:.1f})',
        'monster_estimate_detail': '{base} -> đánh tối thiểu {attack:.2f}s, giữ thêm {lost:.2f}s',
        'monster_saved': 'Đã lưu quái',
        'monster_deleted': 'Đã xóa quái',
        'monster_invalid': 'Thông tin quái không hợp lệ: {e}',
        'monster_not_selected': 'Hãy chọn một quái trước',
        'monster_applied': 'Đã áp dụng vào cấu hình săn',
        'monster_duplicate': 'Tên quái đã tồn tại',
    'hunt_window_bounds': 'Vùng cửa sổ đã lưu: {value}',
    'hunt_window_bounds_none': 'Vùng cửa sổ đã lưu: chưa có',
        'hunt_monster_select': 'Chọn nhanh quái:',
        'hunt_monster_auto_applied': 'Đã tự động áp dụng: {name}',
        'hunt_template_active': 'Template đang dùng: {name}',
        'tooltip_threshold': 'Độ khớp: 0.0 (bất kỳ) đến 1.0 (chính xác). Cao hơn = khớp chặt hơn. Khuyến nghị: 0.80-0.90',
        'tooltip_region_strategy': 'Window: dùng biên cửa sổ game\nCustom: dùng vùng cụ thể bên dưới',
        'tooltip_window_bounds': 'Vùng cửa sổ game (Trái, Trên, Rộng, Cao). Để trống để tự phát hiện.',
        'tooltip_lost_timeout': 'Tiếp tục đánh trong khoảng thời gian này sau khi mất hình ảnh mục tiêu (tránh đổi mục tiêu quá sớm)',
        'tooltip_attack_duration': 'Thời gian đánh tối thiểu ngay cả khi mất mục tiêu sớm (đảm bảo combo kỹ năng hoàn tất)',
        'error_invalid_number': 'Số không hợp lệ: {field}',
        'error_value_must_be_positive': '{field} phải lớn hơn 0',
        'error_threshold_range': 'Threshold phải từ 0.0 đến 1.0',
        'skill_section': 'Thư viện kỹ năng',
        'skill_list': 'Danh sách kỹ năng:',
        'skill_name': 'Tên kỹ năng:',
        'skill_key': 'Phím:',
        'skill_type': 'Loại:',
        'skill_type_attack': 'Tấn công',
        'skill_type_buff': 'Buff',
        'skill_cooldown': 'Hồi chiêu (giây):',
        'skill_cast_time': 'Thi triển (giây):',
        'skill_duration': 'Thời gian duy trì (giây):',
        'skill_pre_refresh': 'Cast lại trước (giây):',
        'skill_duration_hint': 'Thời gian buff tồn tại (0 nếu là skill tấn công)',
        'skill_pre_refresh_hint': 'Cast lại trước khi hết (VD: 5 giây = cast lại sớm 5s)',
        'skill_image': 'Ảnh kỹ năng:',
        'skill_no_image': 'Chưa có ảnh',
        'skill_image_error': 'Không xem được ảnh',
        'skill_new': 'Tạo kỹ năng',
        'skill_save': 'Lưu',
        'skill_delete': 'Xóa',
        'skill_saved': 'Đã lưu kỹ năng',
        'skill_deleted': 'Đã xóa kỹ năng',
        'skill_invalid': 'Thông tin kỹ năng không hợp lệ: {e}',
        'skill_not_selected': 'Hãy chọn một kỹ năng trước',
        'skill_slots': 'Thiết lập kỹ năng',
        'skill_slot_label': 'Ô {i}:',
        'skill_slot_clear': 'Xóa',
        'skill_estimate_missing': 'Thiếu thông tin kỹ năng',
        'skill_duplicate': 'Tên kỹ năng đã tồn tại',
        'manage_button': 'Quản lý…',
        'skill_manage': 'Quản lý kỹ năng…',
    },
}

CONFIG_PATH = Path(__file__).parent / 'data' / 'config.json'
HUNT_CONFIG_PATH = Path(__file__).parent / 'data' / 'hunt_config.json'
MONSTER_DB_PATH = Path(__file__).parent / 'data' / 'monsters.json'
SKILL_DB_PATH = Path(__file__).parent / 'data' / 'skills.json'


def _normalize_window_bounds(value):
    keys = ('left', 'top', 'width', 'height')
    if isinstance(value, dict):
        try:
            normalized = {k: int(value.get(k, 0)) for k in keys}
        except (TypeError, ValueError):
            return None
        if normalized['width'] <= 0 or normalized['height'] <= 0:
            return None
        return normalized
    if isinstance(value, (list, tuple)) and len(value) == 4:
        try:
            left, top, width, height = [int(v) for v in value]
        except (TypeError, ValueError):
            return None
        if width <= 0 or height <= 0:
            return None
        return {'left': left, 'top': top, 'width': width, 'height': height}
    return None


def _normalize_template_entry(item):
    if not isinstance(item, dict):
        return None
    path = str(item.get('path', '') or '').strip()
    if not path:
        return None
    name = str(item.get('name', '') or '').strip()
    if not name:
        try:
            name = Path(path).stem
        except Exception:
            name = 'template'
    try:
        threshold = float(item.get('threshold', 0.85))
    except (TypeError, ValueError):
        threshold = 0.85
    if not math.isfinite(threshold):
        threshold = 0.85
    threshold = max(0.0, min(threshold, 1.0))
    region = _normalize_window_bounds(item.get('region'))
    region_strategy = str(item.get('region_strategy', '') or '').strip()
    grayscale = item.get('grayscale')
    tmpl = {
        'name': name,
        'path': path,
        'threshold': threshold,
        'region': region,
    }
    if region_strategy:
        tmpl['region_strategy'] = region_strategy
    if grayscale is not None:
        tmpl['grayscale'] = bool(grayscale)
    return tmpl


def _sanitize_templates(value):
    templates = []
    if isinstance(value, list):
        for entry in value:
            normalized = _normalize_template_entry(entry)
            if normalized:
                templates.append(normalized)
    return templates


def load_monster_library():
    if not MONSTER_DB_PATH.exists():
        return []
    try:
        with open(MONSTER_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        monsters = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip()
                if not name:
                    continue
                try:
                    hp = float(item.get('hp', 0))
                    dmg = float(item.get('damage_per_hit', 0))
                except (TypeError, ValueError):
                    continue
                if hp <= 0 or dmg <= 0:
                    continue
                template = str(item.get('template', '') or '').strip()
                description = str(item.get('description', '') or '').strip()
                window_bounds = _normalize_window_bounds(item.get('window_bounds'))
                templates = _sanitize_templates(item.get('templates'))
                monsters.append({
                    'name': name,
                    'hp': hp,
                    'damage_per_hit': dmg,
                    'template': template,
                    'description': description,
                    'window_bounds': window_bounds,
                    'templates': templates,
                })
        return monsters
    except Exception:
        return []


def save_monster_library(monsters):
    safe = []
    for item in monsters:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name', '')).strip()
        if not name:
            continue
        try:
            hp = float(item.get('hp', 0))
            dmg = float(item.get('damage_per_hit', 0))
        except (TypeError, ValueError):
            continue
        template = str(item.get('template', '') or '').strip()
        description = str(item.get('description', '') or '').strip()
        window_bounds = _normalize_window_bounds(item.get('window_bounds'))
        templates = _sanitize_templates(item.get('templates'))
        safe.append({
            'name': name,
            'hp': hp,
            'damage_per_hit': dmg,
            'template': template,
            'description': description,
            'window_bounds': window_bounds,
            'templates': templates,
        })
    with open(MONSTER_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def load_skill_library():
    if not SKILL_DB_PATH.exists():
        return []
    try:
        with open(SKILL_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        skills = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get('name', '')).strip()
                key = str(item.get('key', '')).strip().upper()
                if not name or not key:
                    continue
                skill_type = str(item.get('type', 'attack')).strip().lower()
                if skill_type not in ('attack', 'buff'):
                    skill_type = 'attack'
                try:
                    cooldown = float(item.get('cooldown', 0.0))
                    cast_time = float(item.get('cast_time', 0.0))
                except (TypeError, ValueError):
                    cooldown = 0.0
                    cast_time = 0.0
                image = str(item.get('image', '') or '').strip()
                skills.append({
                    'name': name,
                    'key': key,
                    'type': skill_type,
                    'cooldown': max(cooldown, 0.0),
                    'cast_time': max(cast_time, 0.0),
                    'image': image,
                })
        return skills
    except Exception:
        return []


def save_skill_library(skills):
    safe = []
    for item in skills:
        if not isinstance(item, dict):
            continue
        name = str(item.get('name', '')).strip()
        key = str(item.get('key', '')).strip().upper()
        if not name or not key:
            continue
        skill_type = str(item.get('type', 'attack')).strip().lower()
        if skill_type not in ('attack', 'buff'):
            skill_type = 'attack'
        try:
            cooldown = float(item.get('cooldown', 0.0))
            cast_time = float(item.get('cast_time', 0.0))
        except (TypeError, ValueError):
            continue
        image = str(item.get('image', '') or '').strip()
        safe.append({
            'name': name,
            'key': key,
            'type': skill_type,
            'cooldown': max(cooldown, 0.0),
            'cast_time': max(cast_time, 0.0),
            'image': image,
        })
    with open(SKILL_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def calculate_attack_speed_from_skills(skill_names):
    """
    Calculate effective attack speed from selected skills.
    
    Args:
        skill_names: List of skill names to use for hunting
        
    Returns:
        tuple: (attacks_per_second, average_cooldown, skill_count)
        Returns (None, None, 0) if no valid skills
        
    Example:
        skills = ["Dark Explosion", "Fire Ball"]
        aps, avg_cd, count = calculate_attack_speed_from_skills(skills)
        # aps = 0.67 (if avg cooldown is 1.5s)
    """
    if not skill_names:
        return (None, None, 0)
    
    skills_data = load_skill_library()
    if not skills_data:
        return (None, None, 0)
    
    # Build skill lookup dict
    skill_dict = {s['name']: s for s in skills_data}
    
    # Collect cooldowns for selected skills
    total_cooldown = 0.0
    valid_count = 0
    
    for skill_name in skill_names:
        if skill_name in skill_dict:
            skill = skill_dict[skill_name]
            # Only count attack skills for attack speed calculation
            if skill.get('type', 'attack').lower() == 'attack':
                cooldown = float(skill.get('cooldown', 1.0))
                if cooldown > 0:
                    total_cooldown += cooldown
                    valid_count += 1
    
    if valid_count == 0:
        return (None, None, 0)
    
    avg_cooldown = total_cooldown / valid_count
    attacks_per_second = 1.0 / avg_cooldown if avg_cooldown > 0 else 1.0
    
    return (attacks_per_second, avg_cooldown, valid_count)


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "click": {"x": 500, "y": 400, "interval_sec": 2.0},
        "hotkeys": {"toggle": "f8", "exit": "f9"},
        "safety": {"failsafe": True, "pause_key": "f7"},
        "ui": {"topmost": False}
    }


def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_hunt_config():
    # Default hunt config if file missing
    default = {
        "window_title": "Cabal",
        "target_key": "TAB",
        "attack_keys": ["1", "2", "3"],
        "attack_press_ms": 60,
        "target_cycle_delay": 0.2,
        "search_interval": 0.25,
    "attack_interval": 0.15,
        "template_path": "assets/images/target_frame.png",
        "region": None,
        "confidence": 0.85,
        "grayscale": True,
        "lost_timeout_sec": 1.2,
        "attack_min_duration_sec": 1.5,
    "bring_to_front_each_cycle": False,
        "skill_slots": [],
        "window_bounds": None,
    }
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            default.update(data)
        except Exception:
            pass
    default.setdefault('skill_slots', [])
    return default


def save_hunt_config(cfg):
    with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class ConfigManager:
    """Wrapper class for config management to interface with SetupWizard."""
    def __init__(self, cfg, hunt_cfg):
        self.cfg = cfg
        self.hunt_cfg = hunt_cfg
    
    def set(self, section, key, value):
        """Set a configuration value."""
        if section == 'hunt_config':
            self.hunt_cfg[key] = value
        elif section == 'config':
            self.cfg[key] = value
        else:
            # Handle other sections if needed
            if section not in self.cfg:
                self.cfg[section] = {}
            self.cfg[section][key] = value
    
    def get(self, section, key, default=None):
        """Get a configuration value."""
        if section == 'hunt_config':
            return self.hunt_cfg.get(key, default)
        elif section == 'config':
            return self.cfg.get(key, default)
        else:
            return self.cfg.get(section, {}).get(key, default)
    
    def save(self):
        """Save both config files."""
        save_config(self.cfg)
        save_hunt_config(self.hunt_cfg)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Load config and language
        self.cfg = load_config()
        self.hunt_cfg = load_hunt_config()
        self.lang = str(self.cfg.get('ui', {}).get('language', 'vi'))
        
        # Create config manager for wizard
        self.config_mgr = ConfigManager(self.cfg, self.hunt_cfg)

        self.title(self._t('app_title'))
        self.resizable(False, False)

        # State
        self.click_running = False
        self.click_thread = None
        self.hunt_running = False
        self.hunt_thread = None
        self.win_items = []  # list of {'hwnd','pid','title','proc'}
        self.hunt_selected = None  # currently selected window info
        self._stop_hotkey = None
        self.monsters = load_monster_library()
        self.monster_selected_index = None
        self.monster_selected_name = self.monsters[0]['name'] if self.monsters else None
        self.skills = load_skill_library()
        self.skill_selected_index = None
        self.skill_selected_name = self.skills[0]['name'] if self.skills else None
        self.skill_preview_image = None
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        self.skill_slot_count = 6
        self.skill_slot_saved_names = [slot.get('name', '') for slot in self.hunt_cfg.get('skill_slots', []) if isinstance(slot, dict) and slot.get('name')]
        self.monster_manager_win = None
        self.skill_manager_win = None
        self.monster_listbox = None
        self.monster_name_var = tk.StringVar()
        self.monster_hp_var = tk.StringVar()
        self.monster_damage_var = tk.StringVar()
        self.monster_template_var = tk.StringVar()
        self.monster_estimate_var = tk.StringVar(value='')
        self.skill_listbox = None
        self.skill_name_var = tk.StringVar()
        self.skill_key_var = tk.StringVar()
        self.skill_type_var = tk.StringVar(value=self._t('skill_type_attack'))
        self.skill_cooldown_var = tk.StringVar()
        self.skill_cast_time_var = tk.StringVar()
        self.skill_duration_var = tk.StringVar()
        self.skill_pre_refresh_var = tk.StringVar()
        self.skill_image_var = tk.StringVar()
        self.skill_preview_label = None
        self._skill_image_trace = None
        self.monster_description_text = None
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self.monster_template_listbox = None
        self.monster_template_name_var = tk.StringVar()
        self.monster_template_path_var = tk.StringVar()
        self.monster_template_threshold_var = tk.StringVar(value='0.85')
        self.monster_template_region_vars = {
            'left': tk.StringVar(),
            'top': tk.StringVar(),
            'width': tk.StringVar(),
            'height': tk.StringVar(),
        }
        self.monster_template_preview_label = None
        self.monster_template_preview_image = None
        self._monster_template_path_trace = None
        self._thumbnail_cache = {}  # path -> PhotoImage cache
        self.monster_bounds_vars = {
            'left': tk.StringVar(),
            'top': tk.StringVar(),
            'width': tk.StringVar(),
            'height': tk.StringVar(),
        }
        self.current_window_bounds = _normalize_window_bounds(self.hunt_cfg.get('window_bounds'))
        self.hunt_cfg['window_bounds'] = self.current_window_bounds
        self.window_bounds_display_var = tk.StringVar(value='')
        
        # Hunt tab widget groups for progressive disclosure
        self.hunt_intermediate_widgets = []  # Shown in intermediate+ modes
        self.hunt_advanced_widgets = []      # Shown only in advanced mode

        pyautogui.FAILSAFE = bool(self.cfg.get('safety', {}).get('failsafe', True))

        self._build_ui()
        # ESC to stop hunt quickly
        self.bind('<Escape>', lambda e: self.on_hunt_stop())
        
        # Auto-launch Setup Wizard for new users (after UI is ready)
        self.after(500, self._check_first_time_setup)

    # -----------------
    # UI Construction
    # -----------------
    def _build_ui(self):
        # Clear (for language rebuild)
        for w in self.winfo_children():
            w.destroy()

        # Topbar with language selector
        top = tk.Frame(self, padx=8, pady=6)
        top.pack(fill='x')
        tk.Label(top, text=self._t('language')).pack(side='left')
        self.lang_var = tk.StringVar(value=self.lang)
        lang_cmb = ttk.Combobox(top, textvariable=self.lang_var, state='readonly', width=12)
        lang_cmb['values'] = ('en', 'vi')
        lang_cmb.pack(side='left', padx=(6,0))
        lang_cmb.bind('<<ComboboxSelected>>', self.on_language_change)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)

        # Hunt tab
        tab_hunt = tk.Frame(nb, padx=12, pady=12)
        nb.add(tab_hunt, text=self._t('tab_hunt'))
        self._build_hunt_tab(tab_hunt)

    # Click Tab removed

    # Hunt Tab
    def _build_hunt_tab(self, frm):
        # Mode Selection (Beginner/Intermediate/Advanced)
        mode_frame = tk.LabelFrame(frm, text=self._t('hunt_mode'), padx=10, pady=8)
        mode_frame.grid(row=0, column=0, columnspan=4, sticky='we', pady=(0,12))
        
        self.hunt_mode_var = tk.StringVar(value=self.hunt_cfg.get('ui_mode', 'beginner'))
        
        modes = [
            ('beginner', self._t('mode_beginner'), self._t('mode_beginner_desc')),
            ('intermediate', self._t('mode_intermediate'), self._t('mode_intermediate_desc')),
            ('advanced', self._t('mode_advanced'), self._t('mode_advanced_desc'))
        ]
        
        for idx, (mode_val, mode_label, mode_desc) in enumerate(modes):
            rb = tk.Radiobutton(
                mode_frame,
                text=mode_label,
                variable=self.hunt_mode_var,
                value=mode_val,
                command=self._on_hunt_mode_changed,
                font=('Arial', 9, 'bold')
            )
            rb.grid(row=idx, column=0, sticky='w', pady=2)
            
            desc_label = tk.Label(mode_frame, text=f"  {mode_desc}", fg='#666', font=('Arial', 8))
            desc_label.grid(row=idx, column=1, sticky='w', padx=(4,0), pady=2)
        
        # Separator line (using Frame since ttk.Separator doesn't work well with grid)
        sep_line = tk.Frame(frm, height=2, bd=1, relief='sunken')
        sep_line.grid(row=1, column=0, columnspan=4, sticky='we', pady=(0,12))
        
        # Window title
        tk.Label(frm, text=self._t('window_title_contains')).grid(row=2, column=0, sticky='e')
        self.win_title_var = tk.StringVar(value=str(self.hunt_cfg.get('window_title', 'Cabal')))
        tk.Entry(frm, textvariable=self.win_title_var, width=24).grid(row=2, column=1, sticky='w')

        tk.Button(frm, text=self._t('find_windows'), command=self.on_hunt_find_windows).grid(row=2, column=2, padx=(8,0))
        tk.Button(frm, text=self._t('bring_to_front'), command=self.on_hunt_bring_front).grid(row=2, column=3)

        # Window list (filtered)
        tk.Label(frm, text=self._t('win_list_label')).grid(row=3, column=0, columnspan=4, sticky='w', pady=(6,0))
        self.win_listbox = tk.Listbox(frm, height=6, exportselection=False)
        self.win_listbox.grid(row=4, column=0, columnspan=4, sticky='we')
        self.win_listbox.bind('<<ListboxSelect>>', self.on_window_selected)

        # Target/Attack keys (ADVANCED)
        self.target_key_label = tk.Label(frm, text=self._t('target_key'))
        self.target_key_label.grid(row=5, column=0, sticky='e', pady=(8,0))
        self.target_key_var = tk.StringVar(value=str(self.hunt_cfg.get('target_key', 'TAB')))
        self.target_key_entry = tk.Entry(frm, textvariable=self.target_key_var, width=8)
        self.target_key_entry.grid(row=5, column=1, sticky='w', pady=(8,0))

        self.attack_keys_label = tk.Label(frm, text=self._t('attack_keys'))
        self.attack_keys_label.grid(row=5, column=2, sticky='e', pady=(8,0))
        self.attack_keys_var = tk.StringVar(value=','.join(self.hunt_cfg.get('attack_keys', ['1','2','3'])))
        self.attack_keys_entry = tk.Entry(frm, textvariable=self.attack_keys_var, width=18)
        self.attack_keys_entry.grid(row=5, column=3, sticky='w', pady=(8,0))

        # Timing intervals (ADVANCED)
        self.press_ms_label = tk.Label(frm, text=self._t('press_ms'))
        self.press_ms_label.grid(row=6, column=0, sticky='e')
        self.attack_press_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_press_ms', 60)))
        self.press_ms_entry = tk.Entry(frm, textvariable=self.attack_press_var, width=8)
        self.press_ms_entry.grid(row=6, column=1, sticky='w')

        self.target_cycle_label = tk.Label(frm, text=self._t('target_cycle'))
        self.target_cycle_label.grid(row=6, column=2, sticky='e')
        self.target_cycle_var = tk.StringVar(value=str(self.hunt_cfg.get('target_cycle_delay', 0.2)))
        self.target_cycle_entry = tk.Entry(frm, textvariable=self.target_cycle_var, width=8)
        self.target_cycle_entry.grid(row=6, column=3, sticky='w')

        self.search_interval_label = tk.Label(frm, text=self._t('search_interval'))
        self.search_interval_label.grid(row=7, column=0, sticky='e')
        self.search_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('search_interval', 0.25)))
        self.search_interval_entry = tk.Entry(frm, textvariable=self.search_interval_var, width=8)
        self.search_interval_entry.grid(row=7, column=1, sticky='w')

        self.attack_interval_label = tk.Label(frm, text=self._t('attack_interval'))
        self.attack_interval_label.grid(row=7, column=2, sticky='e')
        self.attack_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_interval', 0.15)))
        self.attack_interval_entry = tk.Entry(frm, textvariable=self.attack_interval_var, width=8)
        self.attack_interval_entry.grid(row=7, column=3, sticky='w')

        # Lost timeout & Attack duration (INTERMEDIATE)
        self.lost_timeout_label = tk.Label(frm, text=self._t('lost_timeout'))
        self.lost_timeout_label.grid(row=8, column=0, sticky='e', pady=(8,0))
        self.lost_timeout_var = tk.StringVar(value=str(self.hunt_cfg.get('lost_timeout_sec', 1.2)))
        self.lost_timeout_entry = tk.Entry(frm, textvariable=self.lost_timeout_var, width=8)
        self.lost_timeout_entry.grid(row=8, column=1, sticky='w', pady=(8,0))
        ToolTip(self.lost_timeout_entry, self._t('tooltip_lost_timeout'))

        self.attack_duration_label = tk.Label(frm, text=self._t('attack_duration'))
        self.attack_duration_label.grid(row=8, column=2, sticky='e', pady=(8,0))
        self.attack_duration_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_min_duration_sec', 1.5)))
        self.attack_duration_entry = tk.Entry(frm, textvariable=self.attack_duration_var, width=8)
        self.attack_duration_entry.grid(row=8, column=3, sticky='w', pady=(8,0))
        ToolTip(self.attack_duration_entry, self._t('tooltip_attack_duration'))

        # Template & Region (ADVANCED)
        self.template_label = tk.Label(frm, text=self._t('template'))
        self.template_label.grid(row=9, column=0, sticky='e')
        self.template_var = tk.StringVar(value=str(self.hunt_cfg.get('template_path', 'assets/images/target_frame.png')))
        self.template_entry = tk.Entry(frm, textvariable=self.template_var, width=36)
        self.template_entry.grid(row=9, column=1, columnspan=2, sticky='w')
        self.template_browse_btn = tk.Button(frm, text=self._t('browse'), command=self.on_hunt_browse_template)
        self.template_browse_btn.grid(row=9, column=3)

        self.region_l_label = tk.Label(frm, text=self._t('region_l'))
        self.region_l_label.grid(row=10, column=0, sticky='e')
        region = self.hunt_cfg.get('region') or ["", "", "", ""]
        self.reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")
        self.reg_l_entry = tk.Entry(frm, textvariable=self.reg_l, width=6)
        self.reg_l_entry.grid(row=10, column=1, sticky='w')
        self.reg_t_label = tk.Label(frm, text=self._t('t'))
        self.reg_t_label.grid(row=10, column=1, sticky='e', padx=(48,0))
        self.reg_t_entry = tk.Entry(frm, textvariable=self.reg_t, width=6)
        self.reg_t_entry.grid(row=10, column=2, sticky='w')
        self.reg_w_label = tk.Label(frm, text=self._t('w'))
        self.reg_w_label.grid(row=10, column=2, sticky='e', padx=(48,0))
        self.reg_w_entry = tk.Entry(frm, textvariable=self.reg_w, width=6)
        self.reg_w_entry.grid(row=10, column=3, sticky='w')
        self.reg_h_label = tk.Label(frm, text=self._t('h'))
        self.reg_h_label.grid(row=10, column=3, sticky='e', padx=(48,0))
        self.reg_h_entry = tk.Entry(frm, textvariable=self.reg_h, width=6)
        self.reg_h_entry.grid(row=10, column=3, sticky='e', padx=(24,0))

        self.window_bounds_label = tk.Label(frm, textvariable=self.window_bounds_display_var, fg='gray')
        self.window_bounds_label.grid(row=11, column=0, columnspan=4, sticky='w', pady=(6,0))

        self.bring_front_var = tk.BooleanVar(value=bool(self.hunt_cfg.get('bring_to_front_each_cycle', False)))
        self.bring_front_check = tk.Checkbutton(frm, text=self._t('bring_each_cycle'), variable=self.bring_front_var)
        self.bring_front_check.grid(row=12, column=0, columnspan=4, sticky='w', pady=(6,0))

        self.pick_frame = tk.Frame(frm)
        self.pick_frame.grid(row=13, column=0, columnspan=4, pady=(6,0))
        tk.Button(self.pick_frame, text=self._t('pick_tl'), command=lambda: self.on_hunt_pick_corner('tl')).pack(side='left')
        tk.Button(self.pick_frame, text=self._t('pick_br'), command=lambda: self.on_hunt_pick_corner('br')).pack(side='left', padx=(8,0))

        # Hunt buttons
        hbtn = tk.Frame(frm)
        hbtn.grid(row=14, column=0, columnspan=4, pady=(12,0))
        tk.Button(hbtn, text=self._t('setup_wizard'), command=self.on_setup_wizard, 
                  font=('Arial', 9, 'bold'), fg='#2196F3').pack(side='left')
        tk.Button(hbtn, text=self._t('save_hunt'), command=self.on_hunt_save).pack(side='left', padx=(8,0))
        self.hunt_start_btn = tk.Button(hbtn, text=self._t('start_hunt'), command=self.on_hunt_start)
        self.hunt_start_btn.pack(side='left', padx=(8,0))
        self.hunt_stop_btn = tk.Button(hbtn, text=self._t('stop_hunt'), command=self.on_hunt_stop, state='disabled')
        self.hunt_stop_btn.pack(side='left', padx=(8,0))

        # Monster quick apply
        monster_bar = tk.Frame(frm)
        monster_bar.grid(row=15, column=0, columnspan=4, sticky='we', pady=(12,0))
        monster_bar.grid_columnconfigure(1, weight=1)
        tk.Label(monster_bar, text=self._t('hunt_monster_select')).grid(row=0, column=0, sticky='w')
        self.monster_select_var = tk.StringVar(value=self.monster_selected_name or '')
        self.monster_select_combo = ttk.Combobox(monster_bar, textvariable=self.monster_select_var, state='readonly', width=28)
        self.monster_select_combo.grid(row=0, column=1, sticky='we', padx=(6,0))
        self.monster_select_combo.bind('<<ComboboxSelected>>', self.on_monster_select_change)
        tk.Button(monster_bar, text=self._t('monster_use_template'), command=self.on_monster_apply_from_select).grid(row=0, column=2, padx=(6,0))
        tk.Button(monster_bar, text=self._t('manage_button'), command=self._open_monster_manager).grid(row=0, column=3, padx=(6,0))
        self.monster_estimate_var.set('')
        tk.Label(monster_bar, textvariable=self.monster_estimate_var, fg='gray').grid(row=1, column=0, columnspan=4, sticky='w', pady=(6,0))

        # Skill slots selection
        skill_header = tk.Frame(frm)
        skill_header.grid(row=16, column=0, columnspan=4, sticky='we', pady=(12,0))
        tk.Label(skill_header, text=self._t('skill_slots')).pack(side='left')
        tk.Button(skill_header, text=self._t('skill_manage'), command=self._open_skill_manager).pack(side='left', padx=(6,0))

        slot_frame = tk.Frame(frm)
        slot_frame.grid(row=17, column=0, columnspan=4, sticky='we')
        slot_frame.grid_columnconfigure(1, weight=1)
        self.skill_slot_vars = []
        self.skill_slot_boxes = []
        for idx in range(self.skill_slot_count):
            var = tk.StringVar()
            self.skill_slot_vars.append(var)
            label = self._t('skill_slot_label').format(i=idx + 1)
            tk.Label(slot_frame, text=label).grid(row=idx, column=0, sticky='e', pady=2)
            cmb = ttk.Combobox(slot_frame, textvariable=var, state='readonly', width=24)
            cmb.grid(row=idx, column=1, sticky='we', padx=(4,0), pady=2)
            cmb.bind('<<ComboboxSelected>>', self.on_skill_slot_changed)
            tk.Button(slot_frame, text=self._t('skill_slot_clear'), command=lambda v=var: self._clear_skill_slot(v)).grid(row=idx, column=2, padx=(6,0))
            self.skill_slot_boxes.append(cmb)

        self._refresh_monster_select_options()
        self._load_skill_slots_from_cfg()

        # Status
        self.hunt_status = tk.StringVar(value=self._t('hunt_idle'))
        tk.Label(frm, textvariable=self.hunt_status, fg='gray').grid(row=18, column=0, columnspan=4, pady=(8,0))

        # Track widgets for progressive disclosure
        # Intermediate widgets (shown in intermediate+ modes)
        self.hunt_intermediate_widgets = [
            (self.lost_timeout_label, 8, 0, {'sticky': 'e', 'pady': (8,0)}),
            (self.lost_timeout_entry, 8, 1, {'sticky': 'w', 'pady': (8,0)}),
            (self.attack_duration_label, 8, 2, {'sticky': 'e', 'pady': (8,0)}),
            (self.attack_duration_entry, 8, 3, {'sticky': 'w', 'pady': (8,0)}),
        ]
        
        # Advanced widgets (shown only in advanced mode)
        self.hunt_advanced_widgets = [
            (self.target_key_label, 5, 0, {'sticky': 'e', 'pady': (8,0)}),
            (self.target_key_entry, 5, 1, {'sticky': 'w', 'pady': (8,0)}),
            (self.attack_keys_label, 5, 2, {'sticky': 'e', 'pady': (8,0)}),
            (self.attack_keys_entry, 5, 3, {'sticky': 'w', 'pady': (8,0)}),
            (self.press_ms_label, 6, 0, {'sticky': 'e'}),
            (self.press_ms_entry, 6, 1, {'sticky': 'w'}),
            (self.target_cycle_label, 6, 2, {'sticky': 'e'}),
            (self.target_cycle_entry, 6, 3, {'sticky': 'w'}),
            (self.search_interval_label, 7, 0, {'sticky': 'e'}),
            (self.search_interval_entry, 7, 1, {'sticky': 'w'}),
            (self.attack_interval_label, 7, 2, {'sticky': 'e'}),
            (self.attack_interval_entry, 7, 3, {'sticky': 'w'}),
            (self.template_label, 9, 0, {'sticky': 'e'}),
            (self.template_entry, 9, 1, {'sticky': 'w', 'columnspan': 2}),
            (self.template_browse_btn, 9, 3, {}),
            (self.region_l_label, 10, 0, {'sticky': 'e'}),
            (self.reg_l_entry, 10, 1, {'sticky': 'w'}),
            (self.reg_t_label, 10, 1, {'sticky': 'e', 'padx': (48,0)}),
            (self.reg_t_entry, 10, 2, {'sticky': 'w'}),
            (self.reg_w_label, 10, 2, {'sticky': 'e', 'padx': (48,0)}),
            (self.reg_w_entry, 10, 3, {'sticky': 'w'}),
            (self.reg_h_label, 10, 3, {'sticky': 'e', 'padx': (48,0)}),
            (self.reg_h_entry, 10, 3, {'sticky': 'e', 'padx': (24,0)}),
            (self.window_bounds_label, 11, 0, {'sticky': 'w', 'pady': (6,0), 'columnspan': 4}),
            (self.bring_front_check, 12, 0, {'sticky': 'w', 'pady': (6,0), 'columnspan': 4}),
            (self.pick_frame, 13, 0, {'pady': (6,0), 'columnspan': 4}),
        ]
        
        # Apply initial mode visibility
        self._apply_hunt_mode()

        for i in range(4):
            frm.grid_columnconfigure(i, weight=1)
        self._update_window_bounds_display()
        
        # Auto-populate window selection if config exists (UX FIX #3)
        # This prevents users from having to re-select window every time
        self._auto_populate_saved_window()

    # Click UI and handlers removed

    # -----------------
    # Hunt Handlers
    # -----------------
    def _on_hunt_mode_changed(self):
        """Handle mode toggle - show/hide fields based on selected mode."""
        mode = self.hunt_mode_var.get()
        
        # Save mode preference
        self.hunt_cfg['ui_mode'] = mode
        try:
            with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.hunt_cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save ui_mode: {e}")
        
        # Apply visibility changes
        self._apply_hunt_mode()
        
        # Update status
        mode_labels = {
            'beginner': self._t('mode_beginner'),
            'intermediate': self._t('mode_intermediate'),
            'advanced': self._t('mode_advanced')
        }
        self.hunt_status.set(f"Mode: {mode_labels.get(mode, mode)} - {self._t('hunt_idle')}")
    
    def _apply_hunt_mode(self):
        """Show/hide widgets based on current mode setting."""
        mode = self.hunt_mode_var.get() if hasattr(self, 'hunt_mode_var') else 'beginner'
        
        if mode == 'beginner':
            # Hide intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid_remove()
            # Hide advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid_remove()
                
        elif mode == 'intermediate':
            # Show intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid(row=row, column=col, **kwargs)
            # Hide advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid_remove()
                
        elif mode == 'advanced':
            # Show intermediate widgets
            for widget, row, col, kwargs in self.hunt_intermediate_widgets:
                widget.grid(row=row, column=col, **kwargs)
            # Show advanced widgets
            for widget, row, col, kwargs in self.hunt_advanced_widgets:
                widget.grid(row=row, column=col, **kwargs)
    
    def _update_window_bounds_display(self):
        if not hasattr(self, 'window_bounds_display_var'):
            return
        if self.current_window_bounds:
            bounds_text = '{left},{top},{width},{height}'.format(**self.current_window_bounds)
            self.window_bounds_display_var.set(self._t('hunt_window_bounds').format(value=bounds_text))
        else:
            self.window_bounds_display_var.set(self._t('hunt_window_bounds_none'))

    def on_hunt_browse_template(self):
        path = filedialog.askopenfilename(title='Select template image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if path:
            self.template_var.set(path)

    def on_hunt_pick_corner(self, which: str):
        def do_pick():
            for i in range(3, 0, -1):
                self.hunt_status.set(f'Pick {which.upper()} in {i}... Move mouse to corner')
                time.sleep(1)
            try:
                x, y = pyautogui.position()
                if which == 'tl':
                    self.reg_l.set(str(x))
                    self.reg_t.set(str(y))
                else:
                    # compute width/height using TL if present
                    try:
                        l = int(self.reg_l.get())
                        t = int(self.reg_t.get())
                        w = max(1, x - l)
                        h = max(1, y - t)
                        self.reg_w.set(str(w))
                        self.reg_h.set(str(h))
                    except Exception:
                        self.reg_w.set('')
                        self.reg_h.set('')
                self.hunt_status.set(f'Picked {which.upper()} at ({x},{y})')
            except Exception as e:
                self.hunt_status.set(f'Pick error: {e!r}')

        threading.Thread(target=do_pick, daemon=True).start()

    def on_hunt_find_windows(self):
        # Enumerate windows using WinAPI to get hwnd and PID
        items = self._enum_windows()
        sub = (self.win_title_var.get() or 'cabal').strip().lower()
        candidates = [w for w in items if sub in w['title'].lower() or sub in (w['proc'] or '').lower()]
        # Populate listbox
        self.win_items = candidates
        self.win_listbox.delete(0, tk.END)
        for w in candidates:
            label = f"{w['title']}  [PID:{w['pid']}]"
            if w.get('proc'):
                label += f" ({w['proc']})"
            self.win_listbox.insert(tk.END, label)
        if not candidates:
            messagebox.showinfo(self._t('find_windows'), self._t('no_windows'))
            return
        # Select first
        self.win_listbox.selection_clear(0, tk.END)
        self.win_listbox.selection_set(0)
        self.win_listbox.activate(0)
        self.hunt_selected = candidates[0]
        self.win_title_var.set(candidates[0]['title'])
        self.hunt_status.set(self._t('selected_window').format(title=candidates[0]['title']))

    def on_hunt_bring_front(self):
        # Prefer selected item in list
        hwnd = None
        try:
            idx = self.win_listbox.curselection()
            if idx:
                hwnd = self.win_items[idx[0]]['hwnd']
                self.hunt_selected = self.win_items[idx[0]]
        except Exception:
            hwnd = None
        ok = False
        if hwnd:
            ok = self._bring_window_to_front_by_hwnd(hwnd)
        else:
            ok = self._bring_window_to_front(self.win_title_var.get().strip())
        self.hunt_status.set(self._t('bring_ok') if ok else self._t('bring_fail'))

    def on_window_selected(self, _evt=None):
        try:
            idx = self.win_listbox.curselection()
            if not idx:
                return
            item = self.win_items[idx[0]] if idx[0] < len(self.win_items) else None
            if not item:
                return
            self.hunt_selected = item
            self.win_title_var.set(item['title'])
            self.hunt_status.set(self._t('selected_window').format(title=item['title']))
        except Exception:
            pass

    def _bring_window_to_front(self, title_sub: str) -> bool:
        try:
            import pygetwindow as gw
        except Exception:
            return False
        try:
            wins = [w for w in gw.getAllTitles() if title_sub.lower() in w.lower()]
            if not wins:
                return False
            win = gw.getWindowsWithTitle(wins[0])[0]
            win.activate()
            return True
        except Exception:
            return False

    def _bring_window_to_front_by_hwnd(self, hwnd: int) -> bool:
        try:
            user32 = ctypes.windll.user32
            hwnd_obj = wintypes.HWND(int(hwnd))
            SW_SHOW = 5
            SW_RESTORE = 9

            if user32.IsIconic(hwnd_obj):
                user32.ShowWindow(hwnd_obj, SW_RESTORE)
            else:
                user32.ShowWindow(hwnd_obj, SW_SHOW)

            res = user32.SetForegroundWindow(hwnd_obj)
            if not res:
                user32.BringWindowToTop(hwnd_obj)
                res = user32.SetForegroundWindow(hwnd_obj)
            time.sleep(0.02)
            return bool(res and user32.GetForegroundWindow() == hwnd_obj.value)
        except Exception:
            return False

    def _bring_window_to_front_by_pid(self, pid: int) -> bool:
        try:
            items = self._enum_windows()
            for w in items:
                try:
                    if int(w['pid']) == int(pid):
                        return self._bring_window_to_front_by_hwnd(int(w['hwnd']))
                except Exception:
                    continue
            return False
        except Exception:
            return False

    def _enum_windows(self):
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        IsWindowVisible = user32.IsWindowVisible
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW
        GetWindowThreadProcessId = user32.GetWindowThreadProcessId

        results = []
        # optional: process name via psutil
        try:
            import psutil  # type: ignore
        except Exception:
            psutil = None  # type: ignore

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
                results.append({'hwnd': int(hwnd), 'pid': pid_val, 'title': title, 'proc': proc_name})
            except Exception:
                pass
            return True

        EnumWindows(EnumWindowsProc(callback), 0)
        return results

    def _hunt_locate_target(self, cfg):
        """
        Try to locate target using templates[] or fallback to template_path.
        Uses template_matcher.locate_template() for accurate confidence tracking with OpenCV.
        Returns tuple (box, match_info) or (None, None).
        """
        # Try new templates[] array first
        templates = cfg.get('templates', [])
        if templates:
            window_bounds = cfg.get('window_bounds')
            for tmpl in templates:
                path = tmpl.get('path', '')
                if not path or not Path(path).exists():
                    continue
                
                threshold = tmpl.get('threshold', 0.85)
                
                # Determine region
                region_strategy = tmpl.get('region_strategy', 'window')
                if region_strategy == 'custom' and tmpl.get('region'):
                    reg_dict = tmpl['region']
                    region = (reg_dict.get('left', 0), reg_dict.get('top', 0), 
                             reg_dict.get('width', 0), reg_dict.get('height', 0))
                elif window_bounds:
                    wb = window_bounds
                    region = (wb.get('left', 0), wb.get('top', 0), 
                             wb.get('width', 0), wb.get('height', 0))
                else:
                    region = None
                
                # Use template_matcher for accurate confidence tracking
                box, confidence = locate_template(path, region, threshold, method='auto')
                if box:
                    return box, {
                        'name': tmpl.get('name', ''), 
                        'path': path, 
                        'threshold': threshold,
                        'confidence': confidence
                    }
            
            return None, None
        
        # Fallback to legacy template_path
        region_list = cfg.get('region')
        region = tuple(region_list) if region_list else None
        template = cfg.get('template_path')
        threshold = cfg.get('confidence', 0.8)
        if not template or not Path(template).exists():
            return None, None
        
        # Use template_matcher for accurate confidence tracking
        box, confidence = locate_template(template, region, threshold, method='auto')
        return (box, {'path': template, 'threshold': threshold, 'confidence': confidence}) if box else (None, None)

    def _check_first_time_setup(self):
        """Check if this is first-time user and auto-launch wizard if needed."""
        # Check if user has completed basic setup
        # Must have ALL THREE to be considered configured
        has_window = bool(self.hunt_cfg.get('window_title', '').strip())
        has_monster = bool(self.hunt_cfg.get('monster_selected_name', '').strip())
        has_skills = bool(self.hunt_cfg.get('skill_slots')) and len(self.hunt_cfg.get('skill_slots', [])) > 0
        
        is_new_user = not (has_window and has_monster and has_skills)
        
        # Debug log to understand detection
        print(f"[First-time check] window={has_window}, monster={has_monster}, skills={has_skills}, is_new={is_new_user}")
        
        if is_new_user:
            # Ask user if they want to run setup wizard
            response = messagebox.askyesno(
                self._t('wizard_first_time_title'),
                self._t('wizard_first_time_message'),
                icon='question'
            )
            
            if response:
                # User clicked Yes - launch wizard
                self.on_setup_wizard()
            else:
                # User clicked No - show hint about wizard button
                self.hunt_status.set(self._t('wizard_skipped_hint'))
    
    def on_setup_wizard(self):
        """Launch setup wizard to guide user through initial configuration."""
        def on_wizard_complete(wizard_data):
            """Callback when wizard completes - apply settings to UI."""
            # Show main window again
            self.deiconify()
            
            # Reload config to get wizard changes
            self.hunt_cfg = load_hunt_config()
            
            # Populate Hunt tab UI with wizard data
            self._populate_hunt_ui_from_config()
            
            # Update status message
            lang = wizard_data.get('language', 'en')
            self.hunt_status.set(f"✅ Wizard completed! Configuration loaded. Ready to hunt. (Language: {lang})")
        
        def on_wizard_cancel():
            """Callback when wizard is cancelled - restore main window."""
            self.deiconify()
        
        # Launch wizard - use 'self' instead of 'self.root' (App inherits from tk.Tk)
        # Note: Wizard will hide main window after setup to avoid transient() issues
        show_setup_wizard(self, config_manager=self.config_mgr, on_complete=on_wizard_complete, on_cancel=on_wizard_cancel)
    
    def _populate_hunt_ui_from_config(self):
        """Populate Hunt tab UI elements from hunt_config.json data."""
        # 1. Window selection
        window_title = self.hunt_cfg.get('window_title', '').strip()
        window_pid = self.hunt_cfg.get('window_pid')
        window_hwnd = self.hunt_cfg.get('window_hwnd')
        
        if window_title:
            # Update window title entry
            self.win_title_var.set(window_title)
            
            # If we have PID/HWND, create hunt_selected object and populate listbox
            if window_pid and window_hwnd:
                self.hunt_selected = {
                    'title': window_title,
                    'pid': window_pid,
                    'hwnd': window_hwnd,
                    'proc': None  # Process name not saved in config
                }
                
                # Populate listbox with saved window
                self.win_listbox.delete(0, tk.END)
                label = f"{window_title}  [PID:{window_pid}]"
                self.win_listbox.insert(tk.END, label)
                self.win_listbox.selection_set(0)
                self.win_listbox.activate(0)
                self.win_items = [self.hunt_selected]
        
        # 2. Monster template (if exists)
        monster_name = self.hunt_cfg.get('monster_selected_name', '').strip()
        template_path = self.hunt_cfg.get('template_path', '').strip()
        
        if monster_name:
            # Update monster name display (assuming you have a monster_name variable)
            # This will be shown in UI when monster selection is implemented
            pass
        
        # 3. Skill slots
        skill_slots = self.hunt_cfg.get('skill_slots', [])
        if skill_slots:
            # Update skill UI (assuming skill slot UI variables exist)
            # This will populate skill comboboxes when skill UI is ready
            pass
        
        # 4. Update any other UI elements that depend on config
        # (Add more as needed based on your UI structure)
        pass
    
    def _auto_populate_saved_window(self):
        """
        Auto-populate window selection from hunt_config.json on app startup.
        Prevents users from having to re-select window if already configured.
        Users can still use 'Find Windows' to change if needed.
        """
        window_title = self.hunt_cfg.get('window_title', '').strip()
        window_pid = self.hunt_cfg.get('window_pid')
        window_hwnd = self.hunt_cfg.get('window_hwnd')
        
        # Only auto-populate if we have all required data
        if not (window_title and window_pid and window_hwnd):
            return
        
        # Create hunt_selected object
        self.hunt_selected = {
            'title': window_title,
            'pid': window_pid,
            'hwnd': window_hwnd,
            'proc': None  # Process name not saved in config
        }
        
        # Populate listbox with saved window
        self.win_listbox.delete(0, tk.END)
        label = f"{window_title}  [PID:{window_pid}]"
        self.win_listbox.insert(tk.END, label)
        self.win_listbox.selection_set(0)
        self.win_listbox.activate(0)
        self.win_items = [self.hunt_selected]
        
        # Update status to inform user
        self.hunt_status.set(f"✓ Loaded saved window: {window_title} (PID: {window_pid})")
    
    def on_hunt_save(self):
        try:
            cfg = self._hunt_from_ui()
            save_hunt_config(cfg)
            self.hunt_cfg = cfg
            self.hunt_status.set('Saved hunt_config.json')
        except Exception as e:
            messagebox.showerror(self._t('error_title'), self._t('invalid_hunt').format(e=e))

    def _hunt_from_ui(self):
        title = self.win_title_var.get().strip()
        target_key = self.target_key_var.get().strip() or 'TAB'
        attack_keys = [k.strip() for k in self.attack_keys_var.get().split(',') if k.strip()]
        
        # Validate numeric inputs
        try:
            press_ms = int(float(self.attack_press_var.get()))
        except ValueError:
            raise ValueError(self._t('error_invalid_number').format(field='attack_press_ms'))
        
        try:
            cycle_d = float(self.target_cycle_var.get())
            if cycle_d <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='target_cycle_delay'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='target_cycle_delay'))
        
        try:
            search_i = float(self.search_interval_var.get())
            if search_i <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='search_interval'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='search_interval'))
        
        try:
            attack_i = float(self.attack_interval_var.get())
            if attack_i <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='attack_interval'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='attack_interval'))
        
        try:
            lost_timeout = float(self.lost_timeout_var.get())
            if lost_timeout <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='lost_timeout'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='lost_timeout'))
        
        try:
            attack_min_duration = float(self.attack_duration_var.get())
            if attack_min_duration <= 0:
                raise ValueError(self._t('error_value_must_be_positive').format(field='attack_min_duration'))
        except ValueError as e:
            if 'must be' in str(e):
                raise
            raise ValueError(self._t('error_invalid_number').format(field='attack_min_duration'))
        
        template = self.template_var.get().strip()
        # Region
        region = None
        if all(v.strip() != '' for v in (self.reg_l.get(), self.reg_t.get(), self.reg_w.get(), self.reg_h.get())):
            region = [int(self.reg_l.get()), int(self.reg_t.get()), int(self.reg_w.get()), int(self.reg_h.get())]
        cfg = {
            "window_title": title or 'Cabal',
            "window_pid": int(self.hunt_selected['pid']) if self.hunt_selected else None,
            "target_key": target_key,
            "attack_keys": attack_keys or ['1','2','3'],
            "attack_press_ms": press_ms,
            "target_cycle_delay": cycle_d,
            "search_interval": search_i,
            "attack_interval": attack_i,
            "template_path": template or 'assets/images/target_frame.png',
            "region": region,
            "confidence": float(self.hunt_cfg.get('confidence', 0.85)),
            "grayscale": bool(self.hunt_cfg.get('grayscale', True)),
            "lost_timeout_sec": lost_timeout,
            "attack_min_duration_sec": attack_min_duration,
            "bring_to_front_each_cycle": bool(self.bring_front_var.get()),
            "window_bounds": self.current_window_bounds,
            "templates": self.hunt_cfg.get('templates', []),
        }
        slots = self._collect_skill_slots()
        cfg['skill_slots'] = slots
        if slots:
            cfg['attack_keys'] = [slot['key'] for slot in slots if slot.get('key')]
        return cfg

    # -----------------
    # Monster library helpers
    # -----------------
    def _monster_desc_set(self, text: str):
        if self.monster_description_text:
            self.monster_description_text.delete('1.0', tk.END)
            if text:
                self.monster_description_text.insert('1.0', text)

    def _monster_desc_get(self) -> str:
        if self.monster_description_text:
            return self.monster_description_text.get('1.0', tk.END).strip()
        return ''

    def on_monster_clear_bounds(self):
        for var in self.monster_bounds_vars.values():
            var.set('')

    def _ensure_monster_template_path_trace(self):
        if self._monster_template_path_trace:
            return

        def _trace(*_ignored):
            self._monster_template_update_preview(self.monster_template_path_var.get())

        self._monster_template_path_trace = self.monster_template_path_var.trace_add('write', _trace)

    def _monster_template_update_preview(self, path):
        label = getattr(self, 'monster_template_preview_label', None)
        if not label:
            return
        path = (path or '').strip()
        if not path:
            label.configure(image='', text=self._t('skill_no_image'))
            self.monster_template_preview_image = None
            return
        if Image is None or ImageTk is None:
            label.configure(image='', text=os.path.basename(path))
            self.monster_template_preview_image = None
            return
        
        # Check cache first
        if path in self._thumbnail_cache:
            photo = self._thumbnail_cache[path]
            label.configure(image=photo, text='')
            self.monster_template_preview_image = photo
            return
        
        try:
            img = Image.open(path)
            img.thumbnail((96, 96))
            photo = ImageTk.PhotoImage(img)
            self._thumbnail_cache[path] = photo  # Cache it
            label.configure(image=photo, text='')
            self.monster_template_preview_image = photo
        except Exception:
            label.configure(image='', text=self._t('skill_image_error'))
            self.monster_template_preview_image = None

    def _monster_template_clear_form(self):
        self.monster_template_name_var.set('')
        self.monster_template_path_var.set('')
        self.monster_template_threshold_var.set('0.85')
        for var in self.monster_template_region_vars.values():
            var.set('')
        self._monster_template_update_preview('')

    def _monster_template_fill_form(self, template):
        if not template:
            self._monster_template_clear_form()
            return
        self.monster_template_name_var.set(template.get('name', ''))
        self.monster_template_path_var.set(template.get('path', ''))
        threshold = template.get('threshold', '')
        if threshold == '' or threshold is None:
            self.monster_template_threshold_var.set('0.85')
        else:
            self.monster_template_threshold_var.set(self._format_number(threshold))
        region = template.get('region') if isinstance(template.get('region'), dict) else None
        for key, var in self.monster_template_region_vars.items():
            if region and key in region:
                var.set(str(region.get(key, '')))
            else:
                var.set('')
        self._monster_template_update_preview(template.get('path', ''))

    def _monster_template_read_form(self):
        name = self.monster_template_name_var.get().strip()
        if not name:
            raise ValueError('name required')
        path = self.monster_template_path_var.get().strip()
        if not path:
            raise ValueError('path required')
        try:
            threshold_raw = self.monster_template_threshold_var.get().strip()
            threshold = float(threshold_raw or 0.85)
        except Exception as exc:
            raise ValueError(exc)
        if not math.isfinite(threshold):
            threshold = 0.85
        threshold = max(0.0, min(threshold, 1.0))
        region_input = {k: v.get().strip() for k, v in self.monster_template_region_vars.items()}
        region = None
        if any(region_input.values()):
            if not all(region_input.values()):
                raise ValueError('region requires 4 numbers')
            try:
                region_vals = {k: int(region_input[k]) for k in ('left', 'top', 'width', 'height')}
            except ValueError as exc:
                raise ValueError(f'invalid region: {exc}')
            if region_vals['width'] <= 0 or region_vals['height'] <= 0:
                raise ValueError('region width/height must be positive')
            region = region_vals
        data = {
            'name': name,
            'path': path,
            'threshold': threshold,
        }
        if region:
            data['region'] = region
        return data

    def _refresh_monster_template_list(self, select_index: Optional[int] = None):
        listbox = getattr(self, 'monster_template_listbox', None)
        if listbox is None:
            return
        listbox.delete(0, tk.END)
        for idx, tmpl in enumerate(self.monster_template_working):
            label = tmpl.get('name') or f'Template {idx + 1}'
            threshold = tmpl.get('threshold')
            if threshold is not None and threshold != '':
                try:
                    label += f" ({float(threshold):.2f})"
                except Exception:
                    pass
            listbox.insert(tk.END, label)
        if self.monster_template_working:
            idx = self.monster_template_selected_index if select_index is None else select_index
            if idx is None:
                idx = 0
            idx = int(max(0, min(int(idx), len(self.monster_template_working) - 1)))
            select_index = idx
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(select_index)
            listbox.activate(select_index)
            self.monster_template_selected_index = select_index
            self._monster_template_fill_form(self.monster_template_working[select_index])
        else:
            self.monster_template_selected_index = None
            self._monster_template_clear_form()
        if self.monster_template_working:
            first_path = self.monster_template_working[0].get('path', '')
            if first_path:
                self.monster_template_var.set(first_path)
            listbox.see(self.monster_template_selected_index)

    def on_monster_template_selected(self, _evt=None):
        listbox = getattr(self, 'monster_template_listbox', None)
        if not listbox:
            return
        try:
            idxs = listbox.curselection()
            if not idxs:
                self.monster_template_selected_index = None
                self._monster_template_clear_form()
                return
            idx = idxs[0]
            if idx >= len(self.monster_template_working):
                return
            self.monster_template_selected_index = idx
            self._monster_template_fill_form(self.monster_template_working[idx])
        except Exception:
            pass

    def on_monster_template_import(self):
        """Import template image with option to copy to project assets."""
        path = filedialog.askopenfilename(title=self._t('monster_template_browse'), filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if not path:
            return
        
        # Ask if user wants to copy to project
        copy_to_project = messagebox.askyesno(
            self._t('monster_section'),
            'Copy image to project assets folder?\n\nYes: copy to assets/images/monsters/\nNo: use original path',
            default='yes'
        )
        
        if copy_to_project:
            try:
                # Create target directory
                assets_dir = Path(__file__).parent / 'assets' / 'images' / 'monsters'
                assets_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate unique filename
                import time as time_module
                monster_name = self.monster_name_var.get().strip() or 'monster'
                # Sanitize monster name for filename
                safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in monster_name.lower())
                timestamp = int(time_module.time() * 1000)
                ext = Path(path).suffix or '.png'
                new_filename = f"{safe_name}_{timestamp}{ext}"
                target_path = assets_dir / new_filename
                
                # Copy file
                import shutil
                shutil.copy2(path, target_path)
                
                # Use relative path
                try:
                    relative_path = target_path.relative_to(Path(__file__).parent)
                    path = str(relative_path).replace('\\', '/')
                except Exception:
                    path = str(target_path)
                    
            except Exception as exc:
                messagebox.showerror(self._t('monster_section'), self._t('error_copy_image').format(exc=exc))
                return
        
        self.monster_template_path_var.set(path)
        if not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path).stem)
            except Exception:
                self.monster_template_name_var.set('template')

    def on_monster_template_capture(self):
        """Capture screenshot region and save to assets."""
        try:
            import pyautogui
            import time as time_module
            from pathlib import Path
        except ImportError as exc:
            messagebox.showerror(self._t('monster_section'), f'Missing library: {exc}')
            return
        
        # Show instructions
        messagebox.showinfo(
            self._t('monster_section'),
            self._t('monster_template_capture_hint')
        )
        
        # Minimize this window to allow user to see game
        self.monster_manager_win.iconify()
        
        # Wait 3 seconds
        self.hunt_status.set(self._t('monster_template_capture_wait'))
        self.update()
        time_module.sleep(3)
        
        # Capture full screen first
        try:
            screenshot = pyautogui.screenshot()
        except Exception as exc:
            self.monster_manager_win.deiconify()
            messagebox.showerror(self._t('monster_section'), f'Screenshot failed: {exc}')
            return
        
        # Create selection window
        self.monster_manager_win.deiconify()
        selector = tk.Toplevel(self.monster_manager_win)
        selector.title(self._t('monster_template_capture_select'))
        selector.attributes('-fullscreen', True)
        selector.attributes('-alpha', 0.3)
        selector.attributes('-topmost', True)
        selector.configure(bg='black')
        
        # Variables for selection
        selection = {'start': None, 'end': None, 'cancelled': False}
        canvas = tk.Canvas(selector, cursor='cross', bg='black', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        rect_id = None
        
        def on_mouse_down(event):
            selection['start'] = (event.x, event.y)
        
        def on_mouse_move(event):
            nonlocal rect_id
            if selection['start']:
                if rect_id:
                    canvas.delete(rect_id)
                x1, y1 = selection['start']
                rect_id = canvas.create_rectangle(x1, y1, event.x, event.y, outline='red', width=2)
        
        def on_mouse_up(event):
            selection['end'] = (event.x, event.y)
            selector.destroy()
        
        def on_escape(event):
            selection['cancelled'] = True
            selector.destroy()
        
        canvas.bind('<Button-1>', on_mouse_down)
        canvas.bind('<B1-Motion>', on_mouse_move)
        canvas.bind('<ButtonRelease-1>', on_mouse_up)
        selector.bind('<Escape>', on_escape)
        
        selector.wait_window()
        
        # Check if cancelled
        if selection['cancelled'] or not selection['start'] or not selection['end']:
            self.hunt_status.set(self._t('monster_template_capture_cancelled'))
            return
        
        # Calculate region
        x1, y1 = selection['start']
        x2, y2 = selection['end']
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if width < 10 or height < 10:
            messagebox.showwarning(self._t('monster_section'), 'Region too small (min 10x10)')
            return
        
        # Crop screenshot
        cropped = screenshot.crop((left, top, left + width, top + height))
        
        # Save to assets
        try:
            assets_dir = Path(__file__).parent / 'assets' / 'images' / 'monsters'
            assets_dir.mkdir(parents=True, exist_ok=True)
            
            monster_name = self.monster_name_var.get().strip() or 'monster'
            safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in monster_name.lower())
            timestamp = int(time_module.time() * 1000)
            filename = f"{safe_name}_capture_{timestamp}.png"
            target_path = assets_dir / filename
            
            cropped.save(target_path, 'PNG')
            
            # Use relative path
            try:
                relative_path = target_path.relative_to(Path(__file__).parent)
                path_str = str(relative_path).replace('\\', '/')
            except Exception:
                path_str = str(target_path)
            
            # Set to form
            self.monster_template_path_var.set(path_str)
            
            # Auto-fill region if blank
            if not any(v.get().strip() for v in self.monster_template_region_vars.values()):
                self.monster_template_region_vars['left'].set(str(left))
                self.monster_template_region_vars['top'].set(str(top))
                self.monster_template_region_vars['width'].set(str(width))
                self.monster_template_region_vars['height'].set(str(height))
            
            self.hunt_status.set(self._t('monster_template_capture_success').format(filename=filename))
            
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), f'Save failed: {exc}')

    def on_monster_template_add(self):
        try:
            data = self._monster_template_read_form()
            normalized = _normalize_template_entry(data)
            if not normalized:
                raise ValueError('path required')
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), self._t('monster_template_invalid').format(e=exc))
            return
        for existing in self.monster_template_working:
            if existing.get('name', '').lower() == normalized['name'].lower():
                messagebox.showerror(self._t('monster_section'), self._t('monster_template_duplicate'))
                return
        self.monster_template_working.append(normalized)
        self.monster_template_selected_index = len(self.monster_template_working) - 1
        self._refresh_monster_template_list(self.monster_template_selected_index)
        self.hunt_status.set(self._t('monster_template_added'))

    def on_monster_template_update(self):
        if self.monster_template_selected_index is None or self.monster_template_selected_index >= len(self.monster_template_working):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_not_selected'))
            return
        try:
            data = self._monster_template_read_form()
            normalized = _normalize_template_entry(data)
            if not normalized:
                raise ValueError('path required')
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), self._t('monster_template_invalid').format(e=exc))
            return
        for idx, existing in enumerate(self.monster_template_working):
            if idx == self.monster_template_selected_index:
                continue
            if existing.get('name', '').lower() == normalized['name'].lower():
                messagebox.showerror(self._t('monster_section'), self._t('monster_template_duplicate'))
                return
        self.monster_template_working[self.monster_template_selected_index] = normalized
        self._refresh_monster_template_list(self.monster_template_selected_index)
        self.hunt_status.set(self._t('monster_template_saved'))

    def on_monster_template_delete(self):
        if self.monster_template_selected_index is None or self.monster_template_selected_index >= len(self.monster_template_working):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_not_selected'))
            return
        self.monster_template_working.pop(self.monster_template_selected_index)
        self.monster_template_selected_index = None
        self._refresh_monster_template_list()
        self.hunt_status.set(self._t('monster_template_removed'))

    def on_monster_template_quick_add(self):
        path = filedialog.askopenfilename(title=self._t('monster_template_browse'), filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if not path:
            return
        self.monster_template_path_var.set(path)
        if not self.monster_template_name_var.get().strip():
            try:
                self.monster_template_name_var.set(Path(path).stem)
            except Exception:
                self.monster_template_name_var.set('template')
        if not self.monster_template_threshold_var.get().strip():
            self.monster_template_threshold_var.set('0.85')

    def on_monster_template_preview_overlay(self):
        """Show preview window with template image, window_bounds and region overlay."""
        template_path = self.monster_template_path_var.get().strip()
        if not template_path or not Path(template_path).exists():
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_no_image'))
            return
        
        if Image is None or ImageTk is None or ImageDraw is None:
            messagebox.showerror(self._t('monster_section'), self._t('error_pil_required'))
            return

        try:
            # Load template image
            img = Image.open(template_path).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Draw window_bounds if available
            wb = _normalize_window_bounds({
                k: v.get().strip() for k, v in self.monster_bounds_vars.items()
            })
            if wb:
                # Draw window bounds in blue
                left, top = wb.get('left', 0), wb.get('top', 0)
                width, height = wb.get('width', 0), wb.get('height', 0)
                draw.rectangle([left, top, left + width, top + height], outline='blue', width=2)
                draw.text((left + 5, top + 5), 'Window Bounds', fill='blue')
            
            # Draw region if custom
            region_input = {k: v.get().strip() for k, v in self.monster_template_region_vars.items()}
            region = None
            if any(region_input.values()):
                region = _normalize_window_bounds(region_input)  # reuse same normalization
                if region:
                    rl, rt = region.get('left', 0), region.get('top', 0)
                    rw, rh = region.get('width', 0), region.get('height', 0)
                    draw.rectangle([rl, rt, rl + rw, rt + rh], outline='red', width=3)
                    draw.text((rl + 5, rt + 5), 'Region', fill='red')
            
            # Show in new window
            preview_win = tk.Toplevel(self)
            preview_win.title(self._t('monster_template_preview_overlay'))
            preview_win.geometry('800x600')
            
            # Scale to fit
            img.thumbnail((780, 550))
            photo = ImageTk.PhotoImage(img)
            
            label = tk.Label(preview_win, image=photo)
            label._photo_ref = photo  # keep reference
            label.pack(pady=10)
            
            info_text = f"Template: {Path(template_path).name}"
            if wb:
                info_text += f"\nWindow Bounds: {wb}"
            if region:
                info_text += f"\nRegion: {region}"
            
            tk.Label(preview_win, text=info_text, justify='left').pack()
            tk.Button(preview_win, text=self._t('close'), command=preview_win.destroy).pack(pady=10)
            
        except Exception as exc:
            messagebox.showerror(self._t('monster_section'), self._t('error_preview').format(exc=exc))

    def on_monster_template_test_recognition(self):
        """Test template matching on current screen."""
        template_path = self.monster_template_path_var.get().strip()
        if not template_path or not Path(template_path).exists():
            messagebox.showinfo(self._t('monster_section'), self._t('monster_template_no_image'))
            return
        
        try:
            import pyautogui
            import time as time_module
        except ImportError as exc:
            messagebox.showerror(self._t('monster_section'), f'Missing library: {exc}')
            return
        
        # Get threshold
        try:
            threshold_str = self.monster_template_threshold_var.get().strip()
            threshold = float(threshold_str) if threshold_str else 0.85
            threshold = max(0.0, min(threshold, 1.0))
        except ValueError:
            threshold = 0.85
        
        # Get region if specified
        region_input = {k: v.get().strip() for k, v in self.monster_template_region_vars.items()}
        region = None
        if all(region_input.values()):
            try:
                region = tuple([int(region_input[k]) for k in ('left', 'top', 'width', 'height')])
            except ValueError:
                pass
        
        # Show status
        self.hunt_status.set(self._t('monster_template_test_running'))
        self.update()
        
        # Minimize window briefly
        if self.monster_manager_win:
            self.monster_manager_win.iconify()
        
        time_module.sleep(0.5)  # Brief pause
        
        try:
            # Try to locate on screen using template_matcher
            result = None
            confidence_val = None
            
            # Use locate_template for accurate confidence tracking
            box_and_conf = locate_template(
                template_path=template_path,
                threshold=threshold,
                region=region,
                grayscale=True
            )
            
            # Restore window
            if self.monster_manager_win:
                self.monster_manager_win.deiconify()
            
            if box_and_conf:
                box, confidence_val = box_and_conf
                # Create a Box-like object for compatibility
                class Box:
                    def __init__(self, left, top, width, height):
                        self.left = left
                        self.top = top
                        self.width = width
                        self.height = height
                
                result = Box(box[0], box[1], box[2], box[3])
                
                # Get center coordinates
                center_x = result.left + result.width // 2
                center_y = result.top + result.height // 2
                
                message = self._t('monster_template_test_found').format(
                    x=center_x, 
                    y=center_y, 
                    conf=confidence_val
                )
                
                # Show result with visual overlay
                result_win = tk.Toplevel(self)
                result_win.title(self._t('monster_template_test_recognition'))
                result_win.geometry('400x300')
                
                tk.Label(result_win, text="✅ " + message, fg='green', font=('Arial', 10, 'bold')).pack(pady=10)
                
                details = f"Box: ({result.left}, {result.top}, {result.width}, {result.height})\n"
                details += f"Center: ({center_x}, {center_y})\n"
                details += f"Threshold: {threshold:.2f}\n"
                if region:
                    details += f"Region: {region}"
                
                tk.Label(result_win, text=details, justify='left', font=('Courier', 9)).pack(pady=10)
                
                # Try to capture and show the match
                try:
                    screenshot = pyautogui.screenshot(region=(result.left, result.top, result.width, result.height))
                    screenshot.thumbnail((200, 200))
                    
                    if ImageTk:
                        photo = ImageTk.PhotoImage(screenshot)
                        img_label = tk.Label(result_win, image=photo)
                        img_label._photo_ref = photo
                        img_label.pack(pady=10)
                except Exception:
                    pass
                
                tk.Button(result_win, text=self._t('close'), command=result_win.destroy).pack(pady=10)
                
                self.hunt_status.set(message)
                
            else:
                # Restore window
                if self.monster_manager_win:
                    self.monster_manager_win.deiconify()
                
                message = self._t('monster_template_test_not_found').format(threshold=threshold)
                messagebox.showinfo(
                    self._t('monster_template_test_recognition'),
                    message + "\n\nTry:\n• Lower threshold\n• Adjust region\n• Ensure target is visible"
                )
                self.hunt_status.set(message)
                
        except Exception as exc:
            # Restore window
            if self.monster_manager_win:
                try:
                    self.monster_manager_win.deiconify()
                except Exception:
                    pass
            
            error_msg = self._t('monster_template_test_error').format(error=str(exc))
            messagebox.showerror(self._t('monster_section'), error_msg)
            self.hunt_status.set(error_msg)

    def _monster_clear_form(self):
        if hasattr(self, 'monster_name_var'):
            self.monster_name_var.set('')
        if hasattr(self, 'monster_hp_var'):
            self.monster_hp_var.set('')
        if hasattr(self, 'monster_damage_var'):
            self.monster_damage_var.set('')
        if hasattr(self, 'monster_template_var'):
            self.monster_template_var.set('')
        if hasattr(self, 'monster_estimate_var'):
            self.monster_estimate_var.set('')
        self._monster_desc_set('')
        for var in self.monster_bounds_vars.values():
            var.set('')
        self.monster_template_working = []
        self.monster_template_selected_index = None
        self._monster_template_clear_form()
        self._refresh_monster_template_list()

    def _format_number(self, value):
        try:
            num = float(value)
        except (TypeError, ValueError):
            return ''
        if math.isclose(num, round(num), rel_tol=1e-9, abs_tol=1e-9):
            return str(int(round(num)))
        return f'{num:.2f}'.rstrip('0').rstrip('.')

    def _monster_fill_form(self, monster):
        if not monster:
            self._monster_clear_form()
            return
        if hasattr(self, 'monster_name_var'):
            self.monster_name_var.set(monster.get('name', ''))
        if hasattr(self, 'monster_hp_var'):
            self.monster_hp_var.set(self._format_number(monster.get('hp', '')))
        if hasattr(self, 'monster_damage_var'):
            self.monster_damage_var.set(self._format_number(monster.get('damage_per_hit', '')))
        if hasattr(self, 'monster_template_var'):
            self.monster_template_var.set(monster.get('template', ''))
        self._monster_desc_set(monster.get('description', ''))
        bounds = monster.get('window_bounds') if isinstance(monster.get('window_bounds'), dict) else None
        for key, var in self.monster_bounds_vars.items():
            if bounds and key in bounds:
                var.set(str(bounds.get(key, '')))
            else:
                var.set('')
        self.monster_template_working = copy.deepcopy(_sanitize_templates(monster.get('templates')))
        self.monster_template_selected_index = None
        self._refresh_monster_template_list()
        self._update_monster_estimate_label(monster)

    def _open_monster_manager(self):
        if self.monster_manager_win is not None and self.monster_manager_win.winfo_exists():
            try:
                self.monster_manager_win.deiconify()
                self.monster_manager_win.lift()
                self.monster_manager_win.focus_set()
            except Exception:
                pass
            return

        win = tk.Toplevel(self)
        win.title(self._t('monster_section'))
        win.resizable(False, False)
        self.monster_manager_win = win

        def _on_close():
            if self.monster_manager_win is win:
                self.monster_manager_win = None
            self.monster_listbox = None
            self.monster_description_text = None
            self.monster_template_listbox = None
            self.monster_template_preview_label = None
            self.monster_template_preview_image = None
            win.destroy()

        win.protocol('WM_DELETE_WINDOW', _on_close)
        container = tk.Frame(win, padx=12, pady=12)
        container.grid(row=0, column=0, sticky='nsew')
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(container)
        sidebar.grid(row=0, column=0, sticky='ns')
        sidebar.grid_rowconfigure(1, weight=1)

        tk.Label(sidebar, text=self._t('monster_list')).grid(row=0, column=0, sticky='w')
        self.monster_listbox = tk.Listbox(sidebar, height=16, width=26, exportselection=False)
        self.monster_listbox.grid(row=1, column=0, sticky='ns')
        monster_scroll = tk.Scrollbar(sidebar, orient='vertical', command=self.monster_listbox.yview)
        monster_scroll.grid(row=1, column=1, sticky='ns')
        self.monster_listbox.config(yscrollcommand=monster_scroll.set)
        self.monster_listbox.bind('<<ListboxSelect>>', self.on_monster_selected)

        detail = tk.Frame(container)
        detail.grid(row=0, column=1, sticky='nsew', padx=(16,0))
        detail.grid_columnconfigure(1, weight=1)
        detail.grid_rowconfigure(6, weight=1)

        info_frame = tk.Frame(detail)
        info_frame.grid(row=0, column=0, sticky='we')
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(3, weight=1)

        tk.Label(info_frame, text=self._t('monster_name')).grid(row=0, column=0, sticky='e')
        tk.Entry(info_frame, textvariable=self.monster_name_var, width=24).grid(row=0, column=1, sticky='we', padx=(4,0))
        tk.Button(info_frame, text=self._t('monster_estimate'), command=self.on_monster_estimate).grid(row=0, column=4, padx=(8,0))

        tk.Label(info_frame, text=self._t('monster_hp')).grid(row=1, column=0, sticky='e', pady=(6,0))
        tk.Entry(info_frame, textvariable=self.monster_hp_var, width=12).grid(row=1, column=1, sticky='we', padx=(4,0), pady=(6,0))

        tk.Label(info_frame, text=self._t('monster_damage')).grid(row=1, column=2, sticky='e', pady=(6,0))
        tk.Entry(info_frame, textvariable=self.monster_damage_var, width=12).grid(row=1, column=3, sticky='we', padx=(4,0), pady=(6,0))
        
        tk.Button(info_frame, text=self._t('monster_calculate_timing'), command=self.on_monster_calculate_timing).grid(row=1, column=4, padx=(8,0), pady=(6,0))

        desc_label = tk.Label(detail, text=self._t('monster_description'))
        desc_label.grid(row=1, column=0, sticky='w', pady=(8,0))
        self.monster_description_text = tk.Text(detail, width=46, height=4, wrap='word')
        self.monster_description_text.grid(row=2, column=0, sticky='we')
        tk.Label(detail, text=self._t('monster_description_hint'), fg='gray').grid(row=3, column=0, sticky='w')

        bounds_frame = tk.Frame(detail)
        bounds_frame.grid(row=4, column=0, sticky='w', pady=(8,0))
        bounds_label = tk.Label(bounds_frame, text=self._t('monster_bounds'))
        bounds_label.grid(row=0, column=0, columnspan=5, sticky='w')
        ToolTip(bounds_label, self._t('tooltip_window_bounds'))
        headings = ['L', 'T', 'W', 'H']
        for idx, title in enumerate(headings):
            tk.Label(bounds_frame, text=title).grid(row=1, column=idx, padx=(0,4), sticky='w')
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['left'], width=6).grid(row=2, column=0, padx=(0,4))
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['top'], width=6).grid(row=2, column=1, padx=(0,4))
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['width'], width=6).grid(row=2, column=2, padx=(0,4))
        tk.Entry(bounds_frame, textvariable=self.monster_bounds_vars['height'], width=6).grid(row=2, column=3, padx=(0,10))
        tk.Button(bounds_frame, text=self._t('monster_bounds_clear'), command=self.on_monster_clear_bounds).grid(row=2, column=4)
        tk.Label(bounds_frame, text=self._t('monster_bounds_hint'), fg='gray').grid(row=3, column=0, columnspan=5, sticky='w', pady=(4,0))

        template_frame = tk.Frame(detail)
        template_frame.grid(row=5, column=0, sticky='we', pady=(8,0))
        template_frame.grid_columnconfigure(1, weight=1)
        tk.Label(template_frame, text=self._t('monster_template')).grid(row=0, column=0, sticky='e')
        tk.Entry(template_frame, textvariable=self.monster_template_var, width=32).grid(row=0, column=1, sticky='we', padx=(4,0))
        tk.Button(template_frame, text=self._t('browse'), command=self.on_monster_browse_template).grid(row=0, column=2, padx=(6,0))
        tk.Button(template_frame, text=self._t('monster_open_templates'), command=self.on_monster_template_quick_add).grid(row=1, column=1, sticky='w', pady=(6,0))

        templates_panel = tk.LabelFrame(detail, text=self._t('monster_templates'))
        templates_panel.grid(row=6, column=0, sticky='nsew', pady=(8,0))
        templates_panel.grid_columnconfigure(2, weight=1)
        templates_panel.grid_rowconfigure(0, weight=1)

        self.monster_template_listbox = tk.Listbox(templates_panel, height=8, width=26, exportselection=False)
        self.monster_template_listbox.grid(row=0, column=0, rowspan=5, sticky='nsw')
        template_scroll = tk.Scrollbar(templates_panel, orient='vertical', command=self.monster_template_listbox.yview)
        template_scroll.grid(row=0, column=1, rowspan=5, sticky='ns')
        self.monster_template_listbox.config(yscrollcommand=template_scroll.set)
        self.monster_template_listbox.bind('<<ListboxSelect>>', self.on_monster_template_selected)

        template_form = tk.Frame(templates_panel)
        template_form.grid(row=0, column=2, sticky='nsew', padx=(12,0))
        template_form.grid_columnconfigure(1, weight=1)

        tk.Label(template_form, text=self._t('monster_template_name')).grid(row=0, column=0, sticky='e')
        tk.Entry(template_form, textvariable=self.monster_template_name_var, width=24).grid(row=0, column=1, sticky='we', padx=(4,0))

        tk.Label(template_form, text=self._t('monster_template_path')).grid(row=1, column=0, sticky='e', pady=(6,0))
        tk.Entry(template_form, textvariable=self.monster_template_path_var, width=24).grid(row=1, column=1, sticky='we', padx=(4,0), pady=(6,0))
        self._ensure_monster_template_path_trace()
        path_btn_frame = tk.Frame(template_form)
        path_btn_frame.grid(row=1, column=2, padx=(6,0), pady=(6,0))
        tk.Button(path_btn_frame, text=self._t('monster_template_browse'), command=self.on_monster_template_import).pack(side='left')
        tk.Button(path_btn_frame, text=self._t('monster_template_capture'), command=self.on_monster_template_capture).pack(side='left', padx=(4,0))

        tk.Label(template_form, text=self._t('monster_template_threshold')).grid(row=2, column=0, sticky='e')
        threshold_entry = tk.Entry(template_form, textvariable=self.monster_template_threshold_var, width=8)
        threshold_entry.grid(row=2, column=1, sticky='w', padx=(4,0))
        ToolTip(threshold_entry, self._t('tooltip_threshold'))
        tk.Label(template_form, text=self._t('monster_template_threshold_hint'), fg='gray').grid(row=3, column=0, columnspan=3, sticky='w')

        region_frame = tk.Frame(template_form)
        region_frame.grid(row=4, column=0, columnspan=3, sticky='w', pady=(8,0))
        tk.Label(region_frame, text=self._t('monster_template_region')).grid(row=0, column=0, columnspan=5, sticky='w')
        headers = ['L', 'T', 'W', 'H']
        for idx, title in enumerate(headers):
            tk.Label(region_frame, text=title).grid(row=1, column=idx, padx=(0,4), sticky='w')
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['left'], width=5).grid(row=2, column=0, padx=(0,4))
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['top'], width=5).grid(row=2, column=1, padx=(0,4))
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['width'], width=5).grid(row=2, column=2, padx=(0,4))
        tk.Entry(region_frame, textvariable=self.monster_template_region_vars['height'], width=5).grid(row=2, column=3, padx=(0,8))
        tk.Label(region_frame, text=self._t('monster_template_region_hint'), fg='gray').grid(row=3, column=0, columnspan=5, sticky='w', pady=(4,0))

        preview_frame = tk.Frame(template_form)
        preview_frame.grid(row=5, column=0, columnspan=3, sticky='w', pady=(8,0))
        self.monster_template_preview_label = tk.Label(preview_frame, text=self._t('skill_no_image'), width=16, height=6, relief='groove')
        self.monster_template_preview_label.pack(side='left')
        
        preview_btn_frame = tk.Frame(preview_frame)
        preview_btn_frame.pack(side='left', padx=(8,0))
        tk.Button(preview_btn_frame, text=self._t('monster_template_preview_overlay'), command=self.on_monster_template_preview_overlay).pack(side='top', anchor='w')
        tk.Button(preview_btn_frame, text=self._t('monster_template_test_recognition'), command=self.on_monster_template_test_recognition).pack(side='top', anchor='w', pady=(4,0))

        tmpl_btn_frame = tk.Frame(template_form)
        tmpl_btn_frame.grid(row=6, column=0, columnspan=3, sticky='w', pady=(8,0))
        tk.Button(tmpl_btn_frame, text=self._t('monster_template_add'), command=self.on_monster_template_add).pack(side='left')
        tk.Button(tmpl_btn_frame, text=self._t('monster_template_update'), command=self.on_monster_template_update).pack(side='left', padx=(6,0))
        tk.Button(tmpl_btn_frame, text=self._t('monster_template_delete'), command=self.on_monster_template_delete).pack(side='left', padx=(6,0))

        tk.Label(detail, textvariable=self.monster_estimate_var, fg='gray', wraplength=360, justify='left').grid(row=7, column=0, sticky='we', pady=(8,0))

        btn_frame = tk.Frame(detail)
        btn_frame.grid(row=8, column=0, sticky='w', pady=(12,0))
        tk.Button(btn_frame, text=self._t('monster_new'), command=self.on_monster_new).pack(side='left')
        tk.Button(btn_frame, text=self._t('monster_save'), command=self.on_monster_save).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('monster_delete'), command=self.on_monster_delete).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('monster_use_template'), command=self.on_monster_use_for_hunt).pack(side='left', padx=(12,0))

        self._refresh_monster_list(select_name=self.monster_selected_name)

    def _refresh_monster_select_options(self, select_name: Optional[str] = None):
        if select_name is not None:
            self.monster_selected_name = select_name
        names = [monster['name'] for monster in self.monsters]
        combo = getattr(self, 'monster_select_combo', None)
        if combo is not None:
            combo['values'] = names
            target_name = self.monster_selected_name or (select_name if select_name in names else None)
            current = self.monster_select_var.get() if hasattr(self, 'monster_select_var') else ''
            if target_name and target_name in names:
                self.monster_select_var.set(target_name)
            elif current not in names:
                self.monster_select_var.set(names[0] if names else '')
        self.on_monster_select_change()

    def _refresh_monster_list(self, select_name=None):
        if select_name is not None:
            self.monster_selected_name = select_name
        listbox = getattr(self, 'monster_listbox', None)
        idx = None
        if listbox is not None:
            listbox.delete(0, tk.END)
            for monster in self.monsters:
                listbox.insert(tk.END, monster['name'])
            if self.monster_selected_name:
                for i, monster in enumerate(self.monsters):
                    if monster['name'] == self.monster_selected_name:
                        idx = i
                        break
            if idx is None and self.monsters and self.monster_selected_name is None:
                idx = 0
            if idx is not None and idx < len(self.monsters):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.activate(idx)
                self.monster_selected_index = idx
                self.monster_selected_name = self.monsters[idx]['name']
                self._monster_fill_form(self.monsters[idx])
            else:
                listbox.selection_clear(0, tk.END)
                self.monster_selected_index = None
                self._monster_clear_form()
        else:
            if self.monster_selected_name:
                for i, monster in enumerate(self.monsters):
                    if monster['name'] == self.monster_selected_name:
                        idx = i
                        break
            self.monster_selected_index = idx if idx is not None else None
        self._refresh_monster_select_options(self.monster_selected_name)

    def on_monster_select_change(self, _evt=None):
        """Auto-apply monster config when selected from Hunt tab dropdown."""
        if not hasattr(self, 'monster_select_var'):
            return
        name = self.monster_select_var.get().strip()
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster['name'] == name:
                idx = i
                break
        self.monster_selected_index = idx if idx is not None else None
        self.monster_selected_name = name if idx is not None else None
        
        if idx is not None:
            monster = self.monsters[idx]
            self._update_monster_estimate_label(monster)
            # Auto-apply monster config (templates, window_bounds, timing recommendations)
            self._apply_monster_to_hunt_quick(monster)
        elif hasattr(self, 'monster_estimate_var'):
            self.monster_estimate_var.set('')

    def _apply_monster_to_hunt_quick(self, monster):
        """Apply monster templates and recommended settings to hunt config without opening manager."""
        # Apply window_bounds
        bounds = _normalize_window_bounds(monster.get('window_bounds'))
        self.current_window_bounds = bounds
        self.hunt_cfg['window_bounds'] = bounds
        self._update_window_bounds_display()
        
        # Apply templates[] array
        templates = _sanitize_templates(monster.get('templates'))
        if templates:
            self.hunt_cfg['templates'] = templates
            # Set legacy template_path to first template
            try:
                first_path = templates[0].get('path')
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg['template_path'] = first_path
            except Exception:
                pass
        elif monster.get('template'):
            # Fallback to old single template field
            self.template_var.set(monster['template'])
            self.hunt_cfg['template_path'] = monster['template']
            self.hunt_cfg['templates'] = []
        
        # Apply recommended timing (if monster has HP/damage stats)
        try:
            stats = self._calculate_monster_estimate(monster)
            attack_min, lost_timeout = self._recommend_attack_settings(stats)
            self.attack_duration_var.set(f'{attack_min:.2f}')
            self.lost_timeout_var.set(f'{lost_timeout:.2f}')
        except Exception:
            pass  # Monster may not have complete stats, skip recommendations
        
        # Show brief notification
        if hasattr(self, 'hunt_status'):
            template_count = len(templates) if templates else (1 if monster.get('template') else 0)
            msg = self._t('hunt_monster_auto_applied').format(name=monster.get('name', ''))
            if template_count > 0:
                msg += f" ({template_count} template{'s' if template_count > 1 else ''})"
            self.hunt_status.set(msg)

    def on_monster_apply_from_select(self):
        if not hasattr(self, 'monster_select_var'):
            return
        name = self.monster_select_var.get().strip()
        if not name:
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        idx = None
        for i, monster in enumerate(self.monsters):
            if monster['name'] == name:
                idx = i
                break
        if idx is None:
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        self.monster_selected_index = idx
        self.monster_selected_name = name
        self._update_monster_estimate_label(self.monsters[idx])
        self.on_monster_use_for_hunt()

    def _read_monster_form(self):
        if not hasattr(self, 'monster_name_var'):
            raise ValueError('UI not ready')
        name = self.monster_name_var.get().strip()
        if not name:
            raise ValueError('name required')
        try:
            hp = float(self.monster_hp_var.get())
            dmg = float(self.monster_damage_var.get())
        except Exception as exc:
            raise ValueError(exc)
        if hp <= 0 or dmg <= 0:
            raise ValueError('values must be positive')
        template = self.monster_template_var.get().strip() if hasattr(self, 'monster_template_var') else ''
        description = self._monster_desc_get()
        bounds_input = {k: v.get().strip() for k, v in self.monster_bounds_vars.items()}
        window_bounds = None
        if any(bounds_input.values()):
            if not all(bounds_input.values()):
                raise ValueError('window bounds require left/top/width/height')
            try:
                left = int(bounds_input['left'])
                top = int(bounds_input['top'])
                width = int(bounds_input['width'])
                height = int(bounds_input['height'])
            except ValueError as exc:
                raise ValueError(f'invalid window bounds: {exc}')
            if width <= 0 or height <= 0:
                raise ValueError('window bounds width/height must be positive')
            window_bounds = {'left': left, 'top': top, 'width': width, 'height': height}
        templates = copy.deepcopy(_sanitize_templates(self.monster_template_working))
        return {
            'name': name,
            'hp': hp,
            'damage_per_hit': dmg,
            'template': template,
            'description': description,
            'window_bounds': window_bounds,
            'templates': templates,
        }

    def _current_attack_settings(self):
        try:
            press_ms = max(int(float(self.attack_press_var.get() or 0)), 1)
            attack_interval = max(float(self.attack_interval_var.get() or 0), 0.0)
        except Exception as exc:
            raise ValueError(exc)
        attack_keys = [k.strip() for k in self.attack_keys_var.get().split(',') if k.strip()]
        if not attack_keys:
            attack_keys = ['1']
        return press_ms, attack_interval, attack_keys

    def _calculate_monster_estimate(self, monster):
        hp = float(monster.get('hp', 0))
        dmg = float(monster.get('damage_per_hit', 0))
        if hp <= 0 or dmg <= 0:
            raise ValueError('hp/damage must be positive')
        press_ms, attack_interval, attack_keys = self._current_attack_settings()
        per_hit_time = (press_ms / 1000.0) + attack_interval
        per_hit_time = max(per_hit_time, 0.05)
        hits_needed = max(1, math.ceil(hp / dmg))
        key_count = max(len(attack_keys), 1)
        cycles_needed = math.ceil(hits_needed / key_count)
        cycle_overhead = 0.02  # loop sleep between cycles
        kill_time = hits_needed * per_hit_time + cycles_needed * cycle_overhead
        dps = hp / kill_time if kill_time > 0 else 0.0
        return {
            'kill_time': kill_time,
            'dps': dps,
            'hits': hits_needed,
            'per_hit_time': per_hit_time,
            'key_count': key_count,
        }

    def _recommend_attack_settings(self, stats):
        per_hit_time = stats['per_hit_time']
        kill_time = stats['kill_time']
        attack_padding = max(per_hit_time, 0.3)
        attack_min = kill_time + attack_padding
        lost_timeout = min(max(per_hit_time * 3.0, 0.6), attack_min)
        return attack_min, lost_timeout

    def _update_monster_estimate_label(self, monster=None, stats=None):
        if not hasattr(self, 'monster_estimate_var'):
            return
        try:
            if monster is None and self.monster_selected_index is not None and self.monster_selected_index < len(self.monsters):
                monster = self.monsters[self.monster_selected_index]
            if monster is None:
                raise ValueError('no monster')
            if stats is None:
                stats = self._calculate_monster_estimate(monster)
            base = self._t('monster_estimate_result').format(time=stats['kill_time'], dps=stats['dps'])
            attack_min, lost_timeout = self._recommend_attack_settings(stats)
            text = self._t('monster_estimate_detail').format(base=base, attack=attack_min, lost=lost_timeout)
        except Exception:
            text = ''
        self.monster_estimate_var.set(text)

    def on_monster_browse_template(self):
        path = filedialog.askopenfilename(title='Select template image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if path:
            self.monster_template_var.set(path)

    def on_monster_selected(self, _evt=None):
        if not self.monster_listbox:
            return
        try:
            idxs = self.monster_listbox.curselection()
            if not idxs:
                return
            idx = idxs[0]
            if idx >= len(self.monsters):
                return
            monster = self.monsters[idx]
            self.monster_selected_index = idx
            self.monster_selected_name = monster['name']
            self._monster_fill_form(monster)
        except Exception:
            pass

    def on_monster_new(self):
        self.monster_selected_index = None
        self.monster_selected_name = None
        if self.monster_listbox:
            self.monster_listbox.selection_clear(0, tk.END)
        self._monster_clear_form()

    def on_monster_save(self):
        try:
            monster = self._read_monster_form()
        except Exception as e:
            messagebox.showerror(self._t('monster_section'), self._t('monster_invalid').format(e=e))
            return

        idx = self.monster_selected_index
        if idx is None:
            existing = next((i for i, m in enumerate(self.monsters) if m['name'].lower() == monster['name'].lower()), None)
            if existing is not None:
                idx = existing
                self.monsters[idx] = monster
            else:
                self.monsters.append(monster)
                idx = len(self.monsters) - 1
        else:
            for i, data in enumerate(self.monsters):
                if i != idx and data['name'].lower() == monster['name'].lower():
                    messagebox.showerror(self._t('monster_section'), self._t('monster_duplicate'))
                    return
            self.monsters[idx] = monster

        save_monster_library(self.monsters)
        self.monster_selected_index = idx
        self.monster_selected_name = monster['name']
        self._refresh_monster_list(select_name=monster['name'])
        self.hunt_status.set(self._t('monster_saved'))

    def on_monster_delete(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(self.monsters):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        self.monsters.pop(self.monster_selected_index)
        save_monster_library(self.monsters)
        if self.monsters:
            next_name = self.monsters[min(self.monster_selected_index, len(self.monsters) - 1)]['name']
        else:
            next_name = None
        self.monster_selected_index = None
        self.monster_selected_name = next_name
        self._refresh_monster_list(select_name=next_name)
        self.hunt_status.set(self._t('monster_deleted'))

    def on_monster_calculate_timing(self):
        """Calculate and display timing recommendations based on monster HP and damage."""
        try:
            # Get HP and damage from form
            hp_str = self.monster_hp_var.get().strip()
            damage_str = self.monster_damage_var.get().strip()
            
            if not hp_str or not damage_str:
                messagebox.showinfo(
                    self._t('monster_timing_title'),
                    self._t('monster_timing_no_stats')
                )
                return
            
            hp = float(hp_str)
            damage = float(damage_str)
            
            if hp <= 0 or damage <= 0:
                messagebox.showerror(
                    self._t('monster_timing_title'),
                    'HP and Damage must be greater than 0.'
                )
                return
            
            # Create dialog for attack speed selection
            dialog = tk.Toplevel(self)
            dialog.title(self._t('monster_timing_title'))
            dialog.geometry('500x400')
            dialog.transient(self)
            dialog.grab_set()
            
            # Attack speed selection
            speed_frame = tk.LabelFrame(dialog, text='Attack Speed Source', padx=10, pady=10)
            speed_frame.pack(fill='x', padx=10, pady=10)
            
            speed_var = tk.StringVar(value='from_skills')
            presets = get_timing_presets()
            
            # NEW: From Skills option (Recommended)
            from_skills_frame = tk.Frame(speed_frame)
            from_skills_frame.pack(fill='x', pady=2)
            
            tk.Radiobutton(
                from_skills_frame,
                text='● From Skills (Recommended)',
                variable=speed_var,
                value='from_skills',
                font=('Arial', 9, 'bold')
            ).pack(anchor='w')
            
            # Skill info label (will update dynamically)
            skill_info_label = tk.Label(from_skills_frame, text='', fg='#666', font=('Arial', 8))
            skill_info_label.pack(anchor='w', padx=(20, 0))
            
            # Calculate from current skills
            skills_data = load_skill_library()
            attack_skills = [s['name'] for s in skills_data if s.get('type', 'attack').lower() == 'attack']
            
            if attack_skills:
                aps, avg_cd, count = calculate_attack_speed_from_skills(attack_skills)
                if aps is not None:
                    skill_info_label.config(
                        text=f"  {count} attack skills found | Avg Cooldown: {avg_cd:.2f}s | APS: {aps:.2f} hits/sec"
                    )
                else:
                    skill_info_label.config(text="  No valid attack skills found")
            else:
                skill_info_label.config(text="  No attack skills configured yet")
            
            # Separator
            ttk.Separator(speed_frame, orient='horizontal').pack(fill='x', pady=(8,8))
            
            # Manual presets
            tk.Label(speed_frame, text='Manual Presets:', font=('Arial', 9)).pack(anchor='w', pady=(0,4))
            
            for preset_name, (aps, desc) in presets.items():
                rb = tk.Radiobutton(
                    speed_frame,
                    text=f"  {preset_name.replace('_', ' ').title()}: {desc}",
                    variable=speed_var,
                    value=preset_name
                )
                rb.pack(anchor='w', pady=2)
            
            # Custom speed
            custom_frame = tk.Frame(speed_frame)
            custom_frame.pack(fill='x', pady=(10,0))
            tk.Radiobutton(
                custom_frame,
                text='Custom:',
                variable=speed_var,
                value='custom'
            ).pack(side='left')
            custom_speed_var = tk.StringVar(value='2.0')
            tk.Entry(custom_frame, textvariable=custom_speed_var, width=8).pack(side='left', padx=5)
            tk.Label(custom_frame, text='attacks/sec').pack(side='left')
            
            # Result text
            result_frame = tk.LabelFrame(dialog, text='Recommendations', padx=10, pady=10)
            result_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            result_text = tk.Text(result_frame, width=60, height=12, wrap='word')
            result_text.pack(fill='both', expand=True)
            
            # Store current recommendation for Apply button
            current_rec = {'rec': None}
            
            def update_recommendations():
                """Calculate and display recommendations."""
                try:
                    preset = speed_var.get()
                    
                    # NEW: Handle "from_skills" option
                    if preset == 'from_skills':
                        skills_data = load_skill_library()
                        attack_skills = [s['name'] for s in skills_data if s.get('type', 'attack').lower() == 'attack']
                        aps, avg_cd, count = calculate_attack_speed_from_skills(attack_skills)
                        
                        if aps is None:
                            result_text.delete('1.0', tk.END)
                            error_msg = (
                                'No attack skills found.\n\n'
                                'Please add attack skills in Skills Manager tab first.'
                                if self.lang == 'en' else
                                'Không tìm thấy skill tấn công.\n\n'
                                'Vui lòng thêm skill tấn công ở tab Quản lý Skill trước.'
                            )
                            result_text.insert('1.0', error_msg)
                            current_rec['rec'] = None
                            return
                        
                        # Show skill-based info
                        skill_info = (
                            f"Calculated from {count} attack skills\n"
                            f"Average Cooldown: {avg_cd:.2f}s\n"
                            f"Effective APS: {aps:.2f} hits/sec\n\n"
                            if self.lang == 'en' else
                            f"Tính từ {count} skill tấn công\n"
                            f"Cooldown trung bình: {avg_cd:.2f}s\n"
                            f"Tốc độ tấn công hiệu dụng: {aps:.2f} đòn/giây\n\n"
                        )
                        
                    elif preset == 'custom':
                        aps = float(custom_speed_var.get())
                        skill_info = ''
                    else:
                        aps = presets[preset][0]
                        skill_info = ''
                    
                    # Calculate timing
                    rec = calculate_timing(hp, damage, aps)
                    current_rec['rec'] = rec  # Store for Apply button
                    formatted = format_timing_recommendation(rec, self.lang)
                    
                    # Display results
                    result_text.delete('1.0', tk.END)
                    if skill_info:
                        result_text.insert('1.0', skill_info)
                    result_text.insert(tk.END, f"{rec}\n\n")
                    result_text.insert(tk.END, "=" * 60 + "\n")
                    result_text.insert(tk.END, formatted['summary'])
                    
                except Exception as e:
                    result_text.delete('1.0', tk.END)
                    result_text.insert('1.0', f'Error: {e}')
                    current_rec['rec'] = None
            
            def apply_to_hunt_config():
                """Apply current recommendations to hunt_config.json."""
                if current_rec['rec'] is None:
                    messagebox.showwarning(
                        self._t('monster_timing_title'),
                        'Please calculate timing first.' if self.lang == 'en' else 'Vui lòng tính toán trước.'
                    )
                    return
                
                try:
                    rec = current_rec['rec']
                    
                    # Update hunt config
                    self.hunt_cfg['lost_timeout_sec'] = rec.lost_timeout_sec
                    self.hunt_cfg['attack_min_duration_sec'] = rec.attack_min_duration_sec
                    
                    # Update UI
                    self.lost_timeout_var.set(f'{rec.lost_timeout_sec:.2f}')
                    self.attack_duration_var.set(f'{rec.attack_min_duration_sec:.2f}')
                    
                    # Save to file
                    save_hunt_config(self.hunt_cfg)
                    
                    # Show success message
                    msg = (f'Applied to Hunt Config:\n\n'
                           f'Lost Timeout: {rec.lost_timeout_sec:.2f}s\n'
                           f'Attack Duration: {rec.attack_min_duration_sec:.2f}s\n\n'
                           f'Config saved to hunt_config.json' if self.lang == 'en' else
                           f'Đã áp dụng vào Hunt Config:\n\n'
                           f'Lost Timeout: {rec.lost_timeout_sec:.2f}s\n'
                           f'Attack Duration: {rec.attack_min_duration_sec:.2f}s\n\n'
                           f'Config đã lưu vào hunt_config.json')
                    
                    messagebox.showinfo(
                        self._t('monster_timing_title'),
                        msg
                    )
                    
                    self.hunt_status.set(
                        f'Timing applied: lost={rec.lost_timeout_sec:.2f}s, attack={rec.attack_min_duration_sec:.2f}s'
                    )
                    
                except Exception as e:
                    messagebox.showerror(
                        self._t('error_title'),
                        f'Failed to apply: {e}'
                    )
            
            # Buttons
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(fill='x', padx=10, pady=(0,10))
            
            tk.Button(btn_frame, text='Calculate' if self.lang == 'en' else 'Tính toán',
                     command=update_recommendations).pack(side='left', padx=5)
            tk.Button(btn_frame, text='Apply to Hunt Config' if self.lang == 'en' else 'Áp dụng vào Hunt',
                     command=apply_to_hunt_config, bg='#4CAF50', fg='white').pack(side='left', padx=5)
            tk.Button(btn_frame, text='Close' if self.lang == 'en' else 'Đóng',
                     command=dialog.destroy).pack(side='left', padx=5)
            
            # Initial calculation
            update_recommendations()
            
        except Exception as e:
            messagebox.showerror(self._t('monster_timing_title'), f'Error: {e}')

    def on_monster_estimate(self):
        try:
            monster = self._read_monster_form()
            stats = self._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(self._t('monster_section'), self._t('monster_invalid').format(e=e))
            return
        self._update_monster_estimate_label(monster, stats)
        base = self._t('monster_estimate_result').format(time=stats['kill_time'], dps=stats['dps'])
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        detail = self._t('monster_estimate_detail').format(base=base, attack=attack_min, lost=lost_timeout)
        self.hunt_status.set(detail)

    def on_monster_use_for_hunt(self):
        if self.monster_selected_index is None or self.monster_selected_index >= len(self.monsters):
            messagebox.showinfo(self._t('monster_section'), self._t('monster_not_selected'))
            return
        monster = self.monsters[self.monster_selected_index]
        
        # Apply window_bounds
        bounds = _normalize_window_bounds(monster.get('window_bounds'))
        self.current_window_bounds = bounds
        self.hunt_cfg['window_bounds'] = bounds
        self._update_window_bounds_display()
        
        # Apply templates[] array to config
        templates = _sanitize_templates(monster.get('templates'))
        if templates:
            self.hunt_cfg['templates'] = templates
            # Also set legacy template_path to first template for backward compat
            try:
                first_path = templates[0].get('path')
                if first_path:
                    self.template_var.set(first_path)
                    self.hunt_cfg['template_path'] = first_path
            except Exception:
                pass
        elif monster.get('template'):
            # Fallback to old single template field
            self.template_var.set(monster['template'])
            self.hunt_cfg['template_path'] = monster['template']
            self.hunt_cfg['templates'] = []
        
        try:
            stats = self._calculate_monster_estimate(monster)
        except Exception as e:
            messagebox.showerror(self._t('monster_section'), self._t('monster_invalid').format(e=e))
            return
        kill_time = stats['kill_time']
        attack_min, lost_timeout = self._recommend_attack_settings(stats)
        self.attack_duration_var.set(f'{attack_min:.2f}')
        self.lost_timeout_var.set(f'{lost_timeout:.2f}')
        base = self._t('monster_estimate_result').format(time=kill_time, dps=stats['dps'])
        detail = self._t('monster_estimate_detail').format(base=base, attack=attack_min, lost=lost_timeout)
        self.monster_estimate_var.set(detail)
        self.hunt_status.set(self._t('monster_applied'))

    # -----------------
    # Skill library helpers
    # -----------------
    def _skill_type_label(self, code: str) -> str:
        return self._t('skill_type_buff') if code == 'buff' else self._t('skill_type_attack')

    def _skill_type_from_label(self, label: str) -> str:
        label = label.strip().lower()
        if label in (self._t('skill_type_buff').lower(), 'buff'):
            return 'buff'
        return 'attack'

    def _ensure_skill_image_trace(self):
        if self._skill_image_trace:
            return

        def _trace(*_ignored):
            self._update_skill_preview(self.skill_image_var.get())

        self._skill_image_trace = self.skill_image_var.trace_add('write', _trace)
        # Sync immediately for current value
        self._update_skill_preview(self.skill_image_var.get())

    def _skill_clear_form(self):
        if hasattr(self, 'skill_name_var'):
            self.skill_name_var.set('')
        if hasattr(self, 'skill_key_var'):
            self.skill_key_var.set('')
        if hasattr(self, 'skill_type_var'):
            self.skill_type_var.set(self._t('skill_type_attack'))
        if hasattr(self, 'skill_cooldown_var'):
            self.skill_cooldown_var.set('')
        if hasattr(self, 'skill_cast_time_var'):
            self.skill_cast_time_var.set('')
        if hasattr(self, 'skill_duration_var'):
            self.skill_duration_var.set('')
        if hasattr(self, 'skill_pre_refresh_var'):
            self.skill_pre_refresh_var.set('')
        if hasattr(self, 'skill_image_var'):
            self.skill_image_var.set('')
        self._update_skill_preview('')
        self._toggle_buff_fields()

    def _skill_fill_form(self, skill):
        if not skill:
            self._skill_clear_form()
            return
        if hasattr(self, 'skill_name_var'):
            self.skill_name_var.set(skill.get('name', ''))
        if hasattr(self, 'skill_key_var'):
            self.skill_key_var.set(skill.get('key', ''))
        if hasattr(self, 'skill_type_var'):
            self.skill_type_var.set(self._skill_type_label(skill.get('type', 'attack')))
        if hasattr(self, 'skill_cooldown_var'):
            self.skill_cooldown_var.set(self._format_number(skill.get('cooldown', '')))
        if hasattr(self, 'skill_cast_time_var'):
            self.skill_cast_time_var.set(self._format_number(skill.get('cast_time', '')))
        if hasattr(self, 'skill_duration_var'):
            self.skill_duration_var.set(self._format_number(skill.get('duration_sec', '')))
        if hasattr(self, 'skill_pre_refresh_var'):
            self.skill_pre_refresh_var.set(self._format_number(skill.get('pre_refresh_sec', '')))
        if hasattr(self, 'skill_image_var'):
            self.skill_image_var.set(skill.get('image', ''))
        self._update_skill_preview(skill.get('image', ''))
        self._toggle_buff_fields()

    def _refresh_skill_list(self, select_name=None):
        if select_name is not None:
            self.skill_selected_name = select_name
        listbox = getattr(self, 'skill_listbox', None)
        idx = None
        if listbox is not None:
            listbox.delete(0, tk.END)
            for skill in self.skills:
                listbox.insert(tk.END, skill['name'])
            if self.skill_selected_name:
                for i, skill in enumerate(self.skills):
                    if skill['name'] == self.skill_selected_name:
                        idx = i
                        break
            if idx is None and self.skills and self.skill_selected_name is None:
                idx = 0
            if idx is not None and idx < len(self.skills):
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.activate(idx)
                self.skill_selected_index = idx
                self.skill_selected_name = self.skills[idx]['name']
                self._skill_fill_form(self.skills[idx])
            else:
                listbox.selection_clear(0, tk.END)
                self.skill_selected_index = None
                self._skill_clear_form()
        else:
            if self.skill_selected_name:
                for i, skill in enumerate(self.skills):
                    if skill['name'] == self.skill_selected_name:
                        idx = i
                        break
            self.skill_selected_index = idx if idx is not None else None
        self._refresh_skill_slots_options()

    def _open_skill_manager(self):
        if self.skill_manager_win is not None and self.skill_manager_win.winfo_exists():
            try:
                self.skill_manager_win.deiconify()
                self.skill_manager_win.lift()
                self.skill_manager_win.focus_set()
            except Exception:
                pass
            return

        win = tk.Toplevel(self)
        win.title(self._t('skill_section'))
        win.resizable(False, False)
        self.skill_manager_win = win

        def _on_close():
            if self.skill_manager_win is win:
                self.skill_manager_win = None
            self.skill_listbox = None
            self.skill_preview_label = None
            win.destroy()

        win.protocol('WM_DELETE_WINDOW', _on_close)
        container = tk.Frame(win, padx=10, pady=10)
        container.grid(row=0, column=0, sticky='nsew')
        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(4, weight=1)
        container.grid_rowconfigure(1, weight=1)

        tk.Label(container, text=self._t('skill_list')).grid(row=0, column=0, sticky='w')
        self.skill_listbox = tk.Listbox(container, height=10, exportselection=False)
        self.skill_listbox.grid(row=1, column=0, rowspan=6, sticky='nswe', padx=(0,4))
        skill_scroll = tk.Scrollbar(container, orient='vertical', command=self.skill_listbox.yview)
        skill_scroll.grid(row=1, column=1, rowspan=6, sticky='ns')
        self.skill_listbox.config(yscrollcommand=skill_scroll.set)
        self.skill_listbox.bind('<<ListboxSelect>>', self.on_skill_selected)

        tk.Label(container, text=self._t('skill_name')).grid(row=0, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_name_var, width=24).grid(row=0, column=3, sticky='we', padx=(4,0))

        tk.Label(container, text=self._t('skill_key')).grid(row=1, column=2, sticky='e', pady=(2,0))
        tk.Entry(container, textvariable=self.skill_key_var, width=12).grid(row=1, column=3, sticky='w', padx=(4,0), pady=(2,0))

        tk.Label(container, text=self._t('skill_type')).grid(row=2, column=2, sticky='e')
        self.skill_type_combo = ttk.Combobox(container, textvariable=self.skill_type_var, state='readonly', width=14)
        self.skill_type_combo['values'] = (self._t('skill_type_attack'), self._t('skill_type_buff'))
        self.skill_type_combo.grid(row=2, column=3, sticky='w', padx=(4,0))
        self.skill_type_combo.bind('<<ComboboxSelected>>', self._on_skill_type_changed)
        current_type = self._skill_type_from_label(self.skill_type_var.get() or self._t('skill_type_attack'))
        self.skill_type_var.set(self._skill_type_label(current_type))

        tk.Label(container, text=self._t('skill_cooldown')).grid(row=3, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_cooldown_var, width=12).grid(row=3, column=3, sticky='w', padx=(4,0))

        tk.Label(container, text=self._t('skill_cast_time')).grid(row=4, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_cast_time_var, width=12).grid(row=4, column=3, sticky='w', padx=(4,0))

        # Buff-specific fields (will be shown/hidden based on skill type)
        self.skill_duration_label = tk.Label(container, text=self._t('skill_duration'))
        self.skill_duration_entry = tk.Entry(container, textvariable=self.skill_duration_var, width=12)
        ToolTip(self.skill_duration_entry, self._t('skill_duration_hint'))
        
        self.skill_pre_refresh_label = tk.Label(container, text=self._t('skill_pre_refresh'))
        self.skill_pre_refresh_entry = tk.Entry(container, textvariable=self.skill_pre_refresh_var, width=12)
        ToolTip(self.skill_pre_refresh_entry, self._t('skill_pre_refresh_hint'))

        tk.Label(container, text=self._t('skill_image')).grid(row=7, column=2, sticky='e')
        tk.Entry(container, textvariable=self.skill_image_var, width=24).grid(row=7, column=3, sticky='we', padx=(4,0))
        tk.Button(container, text=self._t('browse'), command=self.on_skill_browse_image).grid(row=7, column=4, padx=(8,0))

        self.skill_preview_label = tk.Label(container, text=self._t('skill_no_image'), width=16, height=6, relief='groove')
        self.skill_preview_label.grid(row=1, column=4, rowspan=6, sticky='nswe', padx=(8,0))
        self._ensure_skill_image_trace()

        btn_frame = tk.Frame(container)
        btn_frame.grid(row=8, column=2, columnspan=3, sticky='w', pady=(8,0))
        tk.Button(btn_frame, text=self._t('skill_new'), command=self.on_skill_new).pack(side='left')
        tk.Button(btn_frame, text=self._t('skill_save'), command=self.on_skill_save).pack(side='left', padx=(6,0))
        tk.Button(btn_frame, text=self._t('skill_delete'), command=self.on_skill_delete).pack(side='left', padx=(6,0))

        self._refresh_skill_list(select_name=self.skill_selected_name)
        
        # Initialize buff fields visibility
        self._toggle_buff_fields()

    def _on_skill_type_changed(self, event=None):
        """Handle skill type change to show/hide buff-specific fields."""
        self._toggle_buff_fields()
    
    def _toggle_buff_fields(self):
        """Show/hide buff duration fields based on skill type."""
        if not hasattr(self, 'skill_duration_label'):
            return
        
        skill_type = self._skill_type_from_label(self.skill_type_var.get())
        is_buff = (skill_type == 'buff')
        
        if is_buff:
            # Show buff fields
            self.skill_duration_label.grid(row=5, column=2, sticky='e')
            self.skill_duration_entry.grid(row=5, column=3, sticky='w', padx=(4,0))
            self.skill_pre_refresh_label.grid(row=6, column=2, sticky='e')
            self.skill_pre_refresh_entry.grid(row=6, column=3, sticky='w', padx=(4,0))
        else:
            # Hide buff fields
            self.skill_duration_label.grid_forget()
            self.skill_duration_entry.grid_forget()
            self.skill_pre_refresh_label.grid_forget()
            self.skill_pre_refresh_entry.grid_forget()

    def _refresh_skill_slots_options(self):
        if not hasattr(self, 'skill_slot_boxes'):
            return
        names = []
        for skill in self.skills:
            if skill['name'] not in names:
                names.append(skill['name'])
        for saved in getattr(self, 'skill_slot_saved_names', []):
            if saved and saved not in names:
                names.append(saved)
        values = [''] + names
        for cmb in self.skill_slot_boxes:
            cmb['values'] = values

    def _load_skill_slots_from_cfg(self):
        saved = self.hunt_cfg.get('skill_slots', []) if hasattr(self, 'hunt_cfg') else []
        self.skill_slot_saved_names = [slot.get('name', '') for slot in saved if slot.get('name')]
        self._refresh_skill_slots_options()
        for idx, var in enumerate(self.skill_slot_vars):
            name = ''
            if idx < len(saved):
                name = saved[idx].get('name', '')
            var.set(name)
        self._update_attack_keys_from_slots()

    def _collect_skill_slots(self):
        if not self.skill_slot_vars:
            self.skill_slot_saved_names = []
            return []
        mapping = {skill['name']: skill for skill in self.skills}
        slots = []
        saved_names = []
        for var in self.skill_slot_vars:
            name = var.get().strip()
            if not name:
                continue
            skill = mapping.get(name)
            if not skill:
                continue
            saved_names.append(name)
            slots.append({
                'name': skill['name'],
                'key': skill['key'],
                'type': skill.get('type', 'attack'),
                'cooldown': float(skill.get('cooldown', 0.0)),
                'cast_time': float(skill.get('cast_time', 0.0)),
                'image': skill.get('image', ''),
            })
        self.skill_slot_saved_names = saved_names
        return slots

    def _clear_skill_slot(self, var):
        var.set('')
        self._update_attack_keys_from_slots()

    def _update_skill_preview(self, path):
        label = getattr(self, 'skill_preview_label', None)
        if not label:
            return
        path = (path or '').strip()
        if not path:
            label.config(image='', text=self._t('skill_no_image'))
            self.skill_preview_image = None
            return
        
        # Check cache first
        if path in self._thumbnail_cache:
            photo = self._thumbnail_cache[path]
            label.config(image=photo, text='')
            self.skill_preview_image = photo
            return
        
        try:
            if Image is not None and ImageTk is not None:
                img = Image.open(path)
                img.thumbnail((96, 96))
                photo = ImageTk.PhotoImage(img)
            else:
                photo = tk.PhotoImage(file=path)
            self._thumbnail_cache[path] = photo  # Cache it
            label.config(image=photo, text='')
            self.skill_preview_image = photo
        except Exception:
            label.config(image='', text=self._t('skill_image_error'))
            self.skill_preview_image = None

    def _update_attack_keys_from_slots(self):
        if not hasattr(self, 'attack_keys_var'):
            return
        mapping = {skill['name']: skill for skill in self.skills}
        keys = []
        for var in self.skill_slot_vars:
            name = var.get().strip()
            if not name:
                continue
            skill = mapping.get(name)
            if not skill:
                continue
            keys.append(skill['key'])
        if keys:
            self.attack_keys_var.set(','.join(keys))
        self.skill_slot_saved_names = [v.get().strip() for v in self.skill_slot_vars if v.get().strip()]
        self._refresh_skill_slots_options()

    def on_skill_browse_image(self):
        path = filedialog.askopenfilename(title='Select skill image', filetypes=[('Images','*.png;*.jpg;*.jpeg;*.bmp')])
        if path:
            self.skill_image_var.set(path)

    def on_skill_selected(self, _evt=None):
        if not self.skill_listbox:
            return
        try:
            idxs = self.skill_listbox.curselection()
            if not idxs:
                return
            idx = idxs[0]
            if idx >= len(self.skills):
                return
            skill = self.skills[idx]
            self.skill_selected_index = idx
            self.skill_selected_name = skill['name']
            self._skill_fill_form(skill)
        except Exception:
            pass

    def _read_skill_form(self):
        if not hasattr(self, 'skill_name_var'):
            raise ValueError('UI not ready')
        name = self.skill_name_var.get().strip()
        if not name:
            raise ValueError('name required')
        key = self.skill_key_var.get().strip().upper()
        if not key:
            raise ValueError('key required')
        type_label = self.skill_type_var.get().strip() if hasattr(self, 'skill_type_var') else self._t('skill_type_attack')
        skill_type = self._skill_type_from_label(type_label)
        try:
            cooldown = float(self.skill_cooldown_var.get() or 0)
            cast_time = float(self.skill_cast_time_var.get() or 0)
            
            # Buff-specific fields
            duration_sec = 0.0
            pre_refresh_sec = 0.0
            
            if skill_type == 'buff':
                # Validate buff duration is required for buff skills
                duration_str = self.skill_duration_var.get().strip() if hasattr(self, 'skill_duration_var') else ''
                if not duration_str:
                    raise ValueError('Buff duration is required for buff skills')
                duration_sec = float(duration_str)
                if duration_sec <= 0:
                    raise ValueError('Buff duration must be greater than 0')
                
                # Pre-refresh is optional but should be validated if provided
                pre_refresh_str = self.skill_pre_refresh_var.get().strip() if hasattr(self, 'skill_pre_refresh_var') else ''
                if pre_refresh_str:
                    pre_refresh_sec = float(pre_refresh_str)
                    if pre_refresh_sec < 0:
                        raise ValueError('Pre-refresh time cannot be negative')
                    if pre_refresh_sec >= duration_sec:
                        raise ValueError('Pre-refresh time must be less than buff duration')
            
        except ValueError as exc:
            raise exc
        except Exception as exc:
            raise ValueError(exc)
        
        image = self.skill_image_var.get().strip() if hasattr(self, 'skill_image_var') else ''
        return {
            'name': name,
            'key': key,
            'type': skill_type,
            'cooldown': max(cooldown, 0.0),
            'cast_time': max(cast_time, 0.0),
            'duration_sec': duration_sec,
            'pre_refresh_sec': pre_refresh_sec,
            'hold_ms': None,  # Keep existing schema field
            'image': image,
        }

    def on_skill_new(self):
        self.skill_selected_index = None
        self.skill_selected_name = None
        if self.skill_listbox:
            self.skill_listbox.selection_clear(0, tk.END)
        self._skill_clear_form()

    def on_skill_save(self):
        try:
            skill = self._read_skill_form()
        except Exception as e:
            messagebox.showerror(self._t('skill_section'), self._t('skill_invalid').format(e=e))
            return

        idx = self.skill_selected_index
        if idx is None:
            existing = next((i for i, s in enumerate(self.skills) if s['name'].lower() == skill['name'].lower()), None)
            if existing is not None:
                idx = existing
                self.skills[idx] = skill
            else:
                self.skills.append(skill)
                idx = len(self.skills) - 1
        else:
            for i, data in enumerate(self.skills):
                if i != idx and data['name'].lower() == skill['name'].lower():
                    messagebox.showerror(self._t('skill_section'), self._t('skill_duplicate'))
                    return
            self.skills[idx] = skill

        save_skill_library(self.skills)
        self.skill_selected_index = idx
        self.skill_selected_name = skill['name']
        self._refresh_skill_list(select_name=skill['name'])
        self._update_attack_keys_from_slots()
        self.hunt_status.set(self._t('skill_saved'))

    def on_skill_delete(self):
        if self.skill_selected_index is None or self.skill_selected_index >= len(self.skills):
            messagebox.showinfo(self._t('skill_section'), self._t('skill_not_selected'))
            return
        removed = self.skills.pop(self.skill_selected_index)
        save_skill_library(self.skills)
        for var in self.skill_slot_vars:
            if var.get().strip() == removed['name']:
                var.set('')
        self.skill_slot_saved_names = [v.get().strip() for v in self.skill_slot_vars if v.get().strip()]
        self.skill_selected_index = None
        self.skill_selected_name = None
        self._refresh_skill_list()
        self._update_attack_keys_from_slots()
        self.hunt_status.set(self._t('skill_deleted'))

    def on_skill_slot_changed(self, _evt=None):
        self._update_attack_keys_from_slots()

    def _prepare_skill_runtime(self, cfg):
        runtime = []
        slots = cfg.get('skill_slots') or []
        default_press = int(cfg.get('attack_press_ms', 60))
        for slot in slots:
            key = str(slot.get('key', '')).strip().upper()
            if not key:
                continue
            cooldown = max(float(slot.get('cooldown', 0.0)), 0.0)
            cast_time = max(float(slot.get('cast_time', 0.0)), 0.0)
            press_ms = max(int(cast_time * 1000), 30)
            if press_ms < default_press:
                press_ms = default_press
            press_ms = min(press_ms, 2000)
            runtime.append({
                'name': slot.get('name', ''),
                'key': key,
                'type': slot.get('type', 'attack'),
                'cooldown': cooldown,
                'cast_time': cast_time,
                'press_ms': press_ms,
                'next_ready': 0.0,
            })
        return runtime

    def _try_cast_skills(self, runtime, now, target_available, attack_phase):
        if not runtime:
            return
        for skill in runtime:
            if now < skill['next_ready']:
                continue
            skill_type = skill.get('type', 'attack')
            if skill_type == 'attack' and not (attack_phase and target_available):
                continue
            if skill_type == 'buff' and attack_phase:
                # allow buffs even during attack phase, but no extra gating
                pass
            try:
                tap(skill['key'], skill['press_ms'])
            except Exception:
                continue
            cooldown = skill.get('cooldown', 0.0)
            skill['next_ready'] = time.time() + cooldown if cooldown > 0 else now
            sleep_extra = max(skill.get('cast_time', 0.0) - (skill['press_ms'] / 1000.0), 0.0)
            if sleep_extra > 0:
                end = time.time() + min(sleep_extra, 0.5)
                while time.time() < end and self.hunt_running:
                    time.sleep(0.02)

    def on_hunt_start(self):
        if self.hunt_running:
            return
        try:
            cfg = self._hunt_from_ui()
        except Exception as e:
            messagebox.showerror('Error', f'Invalid hunt config: {e!r}')
            return
        save_hunt_config(cfg)
        self.hunt_cfg = cfg
        self.hunt_running = True
        self.hunt_start_btn.config(state='disabled')
        self.hunt_stop_btn.config(state='normal')
        self.hunt_status.set(self._t('hunt_running'))

        def worker():
            logger = get_hunt_logger()
            try:
                # Focus the target window; minimize GUI only if focus succeeded
                try:
                    focused = False
                    if self.hunt_selected and self.hunt_selected.get('hwnd'):
                        focused = self._bring_window_to_front_by_hwnd(int(self.hunt_selected['hwnd']))
                    elif cfg.get('window_pid'):
                        focused = self._bring_window_to_front_by_pid(int(cfg['window_pid']))
                    if not focused:
                        focused = self._bring_window_to_front(cfg.get('window_title', 'Cabal'))
                    if focused:
                        try:
                            self.iconify()
                        except Exception:
                            pass
                    time.sleep(0.15)
                except Exception:
                    pass

                # Optional global stop hotkey (F9)
                if keyboard is not None and self._stop_hotkey is None:
                    try:
                        self._stop_hotkey = keyboard.add_hotkey('f9', lambda: setattr(self, 'hunt_running', False))
                    except Exception:
                        self._stop_hotkey = None

                # Start logging
                logger.log_hunt_start(cfg)

                last_search = 0.0
                have_target = False
                mode = 'search'
                last_seen = 0.0
                attack_started = 0.0
                lost_timeout = float(cfg.get('lost_timeout_sec', 0.8))
                attack_min_duration = float(cfg.get('attack_min_duration_sec', 1.5))
                skill_runtime = self._prepare_skill_runtime(cfg)
                has_attack_skills = any(skill.get('type', 'attack') != 'buff' for skill in skill_runtime)
                last_match_info = None
                while self.hunt_running:
                    now = time.time()
                    if cfg.get('bring_to_front_each_cycle'):
                        ok = False
                        try:
                            if self.hunt_selected and self.hunt_selected.get('hwnd'):
                                ok = self._bring_window_to_front_by_hwnd(int(self.hunt_selected['hwnd']))
                            elif cfg.get('window_pid'):
                                ok = self._bring_window_to_front_by_pid(int(cfg['window_pid']))
                        except Exception:
                            ok = False
                        if not ok:
                            self._bring_window_to_front(cfg.get('window_title', 'Cabal'))

                    # periodic detection with multi-template support
                    if now - last_search >= float(cfg['search_interval']):
                        box, match_info = self._hunt_locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                            # Log template match with accurate confidence from template_matcher
                            if match_info and last_match_info != match_info:
                                # Log match details
                                template_name = match_info.get('name') or Path(match_info.get('path', '')).stem
                                threshold = match_info.get('threshold', 0.8)
                                confidence = match_info.get('confidence', 0.0)
                                monster_name = match_info.get('monster_name', '')
                                logger.log_match(template_name, box, threshold, confidence, monster_name)
                                
                                status_msg = f"Target: {template_name} (conf: {confidence:.3f})"
                                self.hunt_status.set(status_msg)
                                last_match_info = match_info
                        else:
                            have_target = False
                            if last_match_info:
                                # Log target lost
                                duration = now - attack_started if mode == 'attack' else 0
                                template_name = last_match_info.get('name') or Path(last_match_info.get('path', '')).stem
                                monster_name = last_match_info.get('monster_name', '')
                                logger.log_lost(template_name, monster_name, duration)
                                
                                self.hunt_status.set(self._t('hunt_running'))
                                last_match_info = None
                        last_search = now

                    if skill_runtime:
                        self._try_cast_skills(skill_runtime, now, have_target, attack_phase=False)

                    if mode == 'search':
                        if have_target:
                            logger.log_state_change('search', 'attack', 'target_found')
                            mode = 'attack'
                            attack_started = now
                            continue
                        tap(cfg['target_key'])
                        time.sleep(float(cfg['target_cycle_delay']))
                        continue

                    # mode == 'attack'
                    if have_target or (now - last_seen) <= lost_timeout or (now - attack_started) <= attack_min_duration:
                        target_active = have_target or (now - last_seen) <= lost_timeout or (now - attack_started) <= attack_min_duration
                        if skill_runtime and has_attack_skills:
                            self._try_cast_skills(skill_runtime, now, target_active, attack_phase=True)
                            if not target_active:
                                logger.log_state_change('attack', 'search', 'lost_timeout')
                                mode = 'search'
                                time.sleep(0.05)
                                continue
                            time.sleep(float(cfg['attack_interval']))
                            continue
                        for k in cfg['attack_keys']:
                            if not self.hunt_running:
                                break
                            try:
                                tap(k, int(cfg['attack_press_ms']))
                            except Exception:
                                pass
                            time.sleep(float(cfg['attack_interval']))
                    else:
                        logger.log_state_change('attack', 'search', 'lost_timeout')
                        mode = 'search'
                        time.sleep(0.05)
                    time.sleep(0.02)
            except Exception as e:
                logger.log_error(f'Hunt error: {str(e)}')
                logger.log_hunt_stop('error')
            finally:
                if not hasattr(logger, '_stop_logged') or not logger._stop_logged:
                    logger.log_hunt_stop('manual_stop')
                    logger._stop_logged = True
                self.hunt_running = False
                self.after(0, self._after_hunt_stop)

        self.hunt_thread = threading.Thread(target=worker, daemon=True)
        self.hunt_thread.start()

    def _after_hunt_stop(self):
        self.hunt_start_btn.config(state='normal')
        self.hunt_stop_btn.config(state='disabled')
        # remove global hotkey if registered
        if hasattr(self, '_stop_hotkey') and self._stop_hotkey is not None:
            try:
                if 'keyboard' in globals() and keyboard is not None:
                    keyboard.remove_hotkey(self._stop_hotkey)
            except Exception:
                pass
            self._stop_hotkey = None
        # restore GUI
        try:
            self.deiconify()
            self.lift()
        except Exception:
            pass
        self.hunt_status.set(self._t('hunt_stopped'))

    def on_hunt_stop(self):
        self.hunt_running = False

    # -----------------
    # Close
    # -----------------
    def on_close(self):
        self.click_running = False
        self.hunt_running = False
        self.destroy()

    # -----------------
    # Language helpers
    # -----------------
    def _t(self, key: str) -> str:
        return LANG.get(self.lang, LANG['en']).get(key, key)

    def on_language_change(self, _evt=None):
        self.lang = self.lang_var.get()
        self.cfg.setdefault('ui', {})
        self.cfg['ui']['language'] = self.lang
        save_config(self.cfg)
        # Rebuild UI with new language
        self.title(self._t('app_title'))
        self._build_ui()


def main():
    app = App()
    app.protocol('WM_DELETE_WINDOW', app.on_close)
    app.mainloop()


if __name__ == '__main__':
    main()
