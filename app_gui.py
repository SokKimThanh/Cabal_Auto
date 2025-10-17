import json
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import tkinter.ttk as ttk

import pyautogui

from win_input import tap
import ctypes
from ctypes import wintypes
try:
    import keyboard  # global hotkeys for stopping
except Exception:
    keyboard = None

# Simple i18n dictionary
LANG = {
    'en': {
        'app_title': 'Cabal Auto GUI',
        'tab_click': 'Click',
        'tab_hunt': 'Hunt',
        'language': 'Language',
        'lang_en': 'English',
        'lang_vi': 'Tiếng Việt',
        'x': 'X', 'y': 'Y', 'interval': 'Interval (s)',
        'pick': 'Pick (3s)', 'always_on_top': 'Always on top',
        'start': 'Start', 'stop': 'Stop', 'save_config': 'Save Config',
        'ready': 'Ready', 'stopped': 'Stopped', 'failsafe_stopped': 'FAILSAFE triggered. Stopped.',
        'pick_in': 'Pick in {i}... Move mouse to target',
        'picked': 'Picked: ({x}, {y})', 'pick_error': 'Pick error: {e}',
        'window_title_contains': 'Window title contains:',
        'find_windows': 'Find Windows', 'bring_to_front': 'Bring To Front',
        'target_key': 'Target key:', 'attack_keys': 'Attack keys (, sep):',
        'press_ms': 'Press ms:', 'target_cycle': 'Target cycle (s):',
        'search_interval': 'Search interval (s):', 'attack_interval': 'Attack interval (s):',
        'template': 'Template:', 'browse': 'Browse',
        'region_l': 'Region: L', 't': 'T', 'w': 'W', 'h': 'H',
        'pick_tl': 'Pick TL (3s)', 'pick_br': 'Pick BR (3s)',
        'save_hunt': 'Save Hunt Config', 'start_hunt': 'Start Hunt', 'stop_hunt': 'Stop Hunt',
        'hunt_idle': 'Hunt idle', 'hunt_running': 'Hunt running', 'hunt_stopped': 'Hunt stopped',
        'selected_window': 'Selected window: {title}', 'bring_ok': 'Brought to front', 'bring_fail': 'Bring to front failed',
        'invalid_input': 'Invalid input: {e}', 'invalid_hunt': 'Invalid hunt config: {e}',
        'no_windows': 'No matching windows found', 'warn_pygetwindow': 'pygetwindow not available',
        'win_list_label': 'Windows (filtered):',
    },
    'vi': {
        'app_title': 'Cabal Auto GUI',
        'tab_click': 'Click',
        'tab_hunt': 'Săn quái',
        'language': 'Ngôn ngữ',
        'lang_en': 'English',
        'lang_vi': 'Tiếng Việt',
        'x': 'X', 'y': 'Y', 'interval': 'Khoảng (giây)',
        'pick': 'Lấy tọa độ (3s)', 'always_on_top': 'Luôn nổi (Always on top)',
        'start': 'Bắt đầu', 'stop': 'Dừng', 'save_config': 'Lưu cấu hình',
        'ready': 'Sẵn sàng', 'stopped': 'Đã dừng', 'failsafe_stopped': 'Đã dừng (FAILSAFE)',
        'pick_in': 'Lấy sau {i}s... Di chuột đến vị trí',
        'picked': 'Đã lấy: ({x}, {y})', 'pick_error': 'Lỗi lấy tọa độ: {e}',
        'window_title_contains': 'Tiêu đề cửa sổ chứa:',
        'find_windows': 'Tìm cửa sổ', 'bring_to_front': 'Đưa lên trước',
        'target_key': 'Phím chọn mục tiêu:', 'attack_keys': 'Phím đánh (cách nhau bằng dấu phẩy):',
        'press_ms': 'Giữ phím (ms):', 'target_cycle': 'Chu kỳ đổi mục tiêu (s):',
        'search_interval': 'Chu kỳ tìm (s):', 'attack_interval': 'Chu kỳ đánh (s):',
        'template': 'Ảnh mẫu:', 'browse': 'Chọn ảnh',
        'region_l': 'Vùng tìm: L', 't': 'T', 'w': 'R', 'h': 'D',
        'pick_tl': 'Chọn góc TL (3s)', 'pick_br': 'Chọn góc BR (3s)',
        'save_hunt': 'Lưu cấu hình săn', 'start_hunt': 'Chạy săn', 'stop_hunt': 'Dừng săn',
        'hunt_idle': 'Sẵn sàng săn', 'hunt_running': 'Đang săn', 'hunt_stopped': 'Đã dừng săn',
        'selected_window': 'Đã chọn cửa sổ: {title}', 'bring_ok': 'Đã đưa lên trước', 'bring_fail': 'Không đưa lên trước được',
        'invalid_input': 'Dữ liệu không hợp lệ: {e}', 'invalid_hunt': 'Cấu hình săn không hợp lệ: {e}',
        'no_windows': 'Không tìm thấy cửa sổ phù hợp', 'warn_pygetwindow': 'Chưa có pygetwindow',
        'win_list_label': 'Danh sách cửa sổ (đã lọc):',
    }
}

CONFIG_PATH = Path(__file__).with_name('config.json')
HUNT_CONFIG_PATH = Path(__file__).with_name('hunt_config.json')


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
        "bring_to_front_each_cycle": True
    }
    if HUNT_CONFIG_PATH.exists():
        try:
            with open(HUNT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            default.update(data)
        except Exception:
            pass
    return default


def save_hunt_config(cfg):
    with open(HUNT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Load config and language
        self.cfg = load_config()
        self.hunt_cfg = load_hunt_config()
        self.lang = str(self.cfg.get('ui', {}).get('language', 'vi'))

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

        pyautogui.FAILSAFE = bool(self.cfg.get('safety', {}).get('failsafe', True))

        self._build_ui()
        # ESC to stop hunt quickly
        self.bind('<Escape>', lambda e: self.on_hunt_stop())

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
        # Window title
        tk.Label(frm, text=self._t('window_title_contains')).grid(row=0, column=0, sticky='e')
        self.win_title_var = tk.StringVar(value=str(self.hunt_cfg.get('window_title', 'Cabal')))
        tk.Entry(frm, textvariable=self.win_title_var, width=24).grid(row=0, column=1, sticky='w')

        tk.Button(frm, text=self._t('find_windows'), command=self.on_hunt_find_windows).grid(row=0, column=2, padx=(8,0))
        tk.Button(frm, text=self._t('bring_to_front'), command=self.on_hunt_bring_front).grid(row=0, column=3)

        # Window list (filtered)
        tk.Label(frm, text=self._t('win_list_label')).grid(row=1, column=0, columnspan=4, sticky='w', pady=(6,0))
        self.win_listbox = tk.Listbox(frm, height=6, exportselection=False)
        self.win_listbox.grid(row=2, column=0, columnspan=4, sticky='we')
        self.win_listbox.bind('<<ListboxSelect>>', self.on_window_selected)

        # Target/Attack keys
        tk.Label(frm, text=self._t('target_key')).grid(row=3, column=0, sticky='e', pady=(8,0))
        self.target_key_var = tk.StringVar(value=str(self.hunt_cfg.get('target_key', 'TAB')))
        tk.Entry(frm, textvariable=self.target_key_var, width=8).grid(row=3, column=1, sticky='w', pady=(8,0))

        tk.Label(frm, text=self._t('attack_keys')).grid(row=3, column=2, sticky='e', pady=(8,0))
        self.attack_keys_var = tk.StringVar(value=','.join(self.hunt_cfg.get('attack_keys', ['1','2','3'])))
        tk.Entry(frm, textvariable=self.attack_keys_var, width=18).grid(row=3, column=3, sticky='w', pady=(8,0))

        # Timing
        tk.Label(frm, text=self._t('press_ms')).grid(row=4, column=0, sticky='e')
        self.attack_press_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_press_ms', 60)))
        tk.Entry(frm, textvariable=self.attack_press_var, width=8).grid(row=4, column=1, sticky='w')

        tk.Label(frm, text=self._t('target_cycle')).grid(row=4, column=2, sticky='e')
        self.target_cycle_var = tk.StringVar(value=str(self.hunt_cfg.get('target_cycle_delay', 0.2)))
        tk.Entry(frm, textvariable=self.target_cycle_var, width=8).grid(row=4, column=3, sticky='w')

        tk.Label(frm, text=self._t('search_interval')).grid(row=5, column=0, sticky='e')
        self.search_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('search_interval', 0.25)))
        tk.Entry(frm, textvariable=self.search_interval_var, width=8).grid(row=5, column=1, sticky='w')

        tk.Label(frm, text=self._t('attack_interval')).grid(row=5, column=2, sticky='e')
        self.attack_interval_var = tk.StringVar(value=str(self.hunt_cfg.get('attack_interval', 0.15)))
        tk.Entry(frm, textvariable=self.attack_interval_var, width=8).grid(row=5, column=3, sticky='w')

        # Template & Region
        tk.Label(frm, text=self._t('template')).grid(row=6, column=0, sticky='e', pady=(8,0))
        self.template_var = tk.StringVar(value=str(self.hunt_cfg.get('template_path', 'assets/images/target_frame.png')))
        tk.Entry(frm, textvariable=self.template_var, width=36).grid(row=6, column=1, columnspan=2, sticky='w', pady=(8,0))
        tk.Button(frm, text=self._t('browse'), command=self.on_hunt_browse_template).grid(row=6, column=3, pady=(8,0))

        tk.Label(frm, text=self._t('region_l')).grid(row=7, column=0, sticky='e')
        region = self.hunt_cfg.get('region') or ["", "", "", ""]
        self.reg_l = tk.StringVar(value=str(region[0]) if region[0] != "" else "")
        self.reg_t = tk.StringVar(value=str(region[1]) if region[1] != "" else "")
        self.reg_w = tk.StringVar(value=str(region[2]) if region[2] != "" else "")
        self.reg_h = tk.StringVar(value=str(region[3]) if region[3] != "" else "")
        tk.Entry(frm, textvariable=self.reg_l, width=6).grid(row=7, column=1, sticky='w')
        tk.Label(frm, text=self._t('t')).grid(row=7, column=1, sticky='e', padx=(48,0))
        tk.Entry(frm, textvariable=self.reg_t, width=6).grid(row=7, column=2, sticky='w')
        tk.Label(frm, text=self._t('w')).grid(row=7, column=2, sticky='e', padx=(48,0))
        tk.Entry(frm, textvariable=self.reg_w, width=6).grid(row=7, column=3, sticky='w')
        tk.Label(frm, text=self._t('h')).grid(row=7, column=3, sticky='e', padx=(48,0))
        tk.Entry(frm, textvariable=self.reg_h, width=6).grid(row=7, column=3, sticky='e', padx=(24,0))

        pick_frame = tk.Frame(frm)
        pick_frame.grid(row=8, column=0, columnspan=4, pady=(6,0))
        tk.Button(pick_frame, text=self._t('pick_tl'), command=lambda: self.on_hunt_pick_corner('tl')).pack(side='left')
        tk.Button(pick_frame, text=self._t('pick_br'), command=lambda: self.on_hunt_pick_corner('br')).pack(side='left', padx=(8,0))

        # Hunt buttons
        hbtn = tk.Frame(frm)
        hbtn.grid(row=9, column=0, columnspan=4, pady=(12,0))
        tk.Button(hbtn, text=self._t('save_hunt'), command=self.on_hunt_save).pack(side='left')
        self.hunt_start_btn = tk.Button(hbtn, text=self._t('start_hunt'), command=self.on_hunt_start)
        self.hunt_start_btn.pack(side='left', padx=(8,0))
        self.hunt_stop_btn = tk.Button(hbtn, text=self._t('stop_hunt'), command=self.on_hunt_stop, state='disabled')
        self.hunt_stop_btn.pack(side='left', padx=(8,0))

        # Status
        self.hunt_status = tk.StringVar(value=self._t('hunt_idle'))
        tk.Label(frm, textvariable=self.hunt_status, fg='gray').grid(row=10, column=0, columnspan=4, pady=(8,0))

        for i in range(4):
            frm.grid_columnconfigure(i, weight=1)

    # Click UI and handlers removed

    # -----------------
    # Hunt Handlers
    # -----------------
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
            kernel32 = ctypes.windll.kernel32
            hwnd_obj = wintypes.HWND(int(hwnd))
            SW_SHOW = 5
            SW_RESTORE = 9

            try:
                user32.AllowSetForegroundWindow(0xFFFFFFFF)
            except Exception:
                pass

            if user32.IsIconic(hwnd_obj):
                user32.ShowWindow(hwnd_obj, SW_RESTORE)
            else:
                user32.ShowWindow(hwnd_obj, SW_SHOW)

            fg_hwnd = user32.GetForegroundWindow()
            if fg_hwnd == hwnd_obj.value:
                return True

            current_thread = kernel32.GetCurrentThreadId()
            fg_thread = 0
            if fg_hwnd:
                fg_pid = wintypes.DWORD()
                fg_thread = user32.GetWindowThreadProcessId(wintypes.HWND(fg_hwnd), ctypes.byref(fg_pid))
            target_pid = wintypes.DWORD()
            target_thread = user32.GetWindowThreadProcessId(hwnd_obj, ctypes.byref(target_pid))

            attached_fg = False
            attached_target = False
            if fg_thread and fg_thread != current_thread:
                attached_fg = bool(user32.AttachThreadInput(fg_thread, current_thread, True))
            if target_thread and target_thread != current_thread:
                attached_target = bool(user32.AttachThreadInput(target_thread, current_thread, True))

            user32.BringWindowToTop(hwnd_obj)
            user32.SetForegroundWindow(hwnd_obj)
            user32.SetFocus(hwnd_obj)
            user32.SetActiveWindow(hwnd_obj)

            if attached_target:
                user32.AttachThreadInput(target_thread, current_thread, False)
            if attached_fg:
                user32.AttachThreadInput(fg_thread, current_thread, False)

            time.sleep(0.05)
            return user32.GetForegroundWindow() == hwnd_obj.value
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
        region = cfg.get('region')
        template = cfg.get('template_path')
        grayscale = bool(cfg.get('grayscale', True))
        if not template or not Path(template).exists():
            return None
        try:
            if region:
                box = pyautogui.locateOnScreen(template, region=tuple(region), grayscale=grayscale, confidence=cfg.get('confidence', None))
            else:
                box = pyautogui.locateOnScreen(template, grayscale=grayscale, confidence=cfg.get('confidence', None))
            return box
        except TypeError:
            # Retry without confidence when OpenCV absent
            try:
                if region:
                    box = pyautogui.locateOnScreen(template, region=tuple(region), grayscale=grayscale)
                else:
                    box = pyautogui.locateOnScreen(template, grayscale=grayscale)
                return box
            except Exception:
                return None
        except Exception:
            return None

    def on_hunt_save(self):
        try:
            cfg = self._hunt_from_ui()
            save_hunt_config(cfg)
            self.hunt_status.set('Saved hunt_config.json')
        except Exception as e:
            messagebox.showerror('Error', self._t('invalid_hunt').format(e=e))

    def _hunt_from_ui(self):
        title = self.win_title_var.get().strip()
        target_key = self.target_key_var.get().strip() or 'TAB'
        attack_keys = [k.strip() for k in self.attack_keys_var.get().split(',') if k.strip()]
        press_ms = int(float(self.attack_press_var.get()))
        cycle_d = float(self.target_cycle_var.get())
        search_i = float(self.search_interval_var.get())
        attack_i = float(self.attack_interval_var.get())
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
            "confidence": float(load_hunt_config().get('confidence', 0.85)),
            "grayscale": bool(load_hunt_config().get('grayscale', True)),
            "bring_to_front_each_cycle": True
        }
        return cfg

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

                last_search = 0.0
                have_target = False
                mode = 'search'
                last_seen = 0.0
                lost_timeout = float(cfg.get('lost_timeout_sec', load_hunt_config().get('lost_timeout_sec', 0.8)))
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

                    # periodic detection
                    if now - last_search >= float(cfg['search_interval']):
                        box = self._hunt_locate_target(cfg)
                        if box is not None:
                            have_target = True
                            last_seen = now
                        else:
                            have_target = False
                        last_search = now

                    if mode == 'search':
                        if have_target:
                            mode = 'attack'
                            continue
                        tap(cfg['target_key'])
                        time.sleep(float(cfg['target_cycle_delay']))
                        continue

                    # mode == 'attack'
                    if have_target or (now - last_seen) <= lost_timeout:
                        for k in cfg['attack_keys']:
                            if not self.hunt_running:
                                break
                            try:
                                tap(k, int(cfg['attack_press_ms']))
                            except Exception:
                                pass
                            time.sleep(float(cfg['attack_interval']))
                    else:
                        mode = 'search'
                        time.sleep(0.05)
                    time.sleep(0.02)
            finally:
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
