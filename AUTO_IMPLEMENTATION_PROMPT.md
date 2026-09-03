# 🚀 Hướng Dẫn Tự Động: Triển Khai Capability Gate

## Hướng Dẫn Cho Jules

**Copy toàn bộ text dưới đây vào Copilot Chat và bấm Enter để tự động thực hiện tất cả bước.**

---

## PROMPT TỰ ĐỘNG (Copy-Paste)

```
task: Triển khai Input Backend + Capability Gate cho Background Input System

context:
- Project: Cabal Auto Hunt (Python bot)
- Workspace: f:\Cabal_Auto
- Yêu cầu: Thực hiện 3 bước chính dưới đây THEO THỨ TỰ

steps:

### BƯỚC 1: Tạo Input Backend Layer (3 files mới)

1.1) Tạo lib/system/input_backend.py
- Định nghĩa InputBackend protocol với methods: tap(key), key_down(key), key_up(key), close()
- Implement ForegroundSendInputBackend wrapping lib.system.win_input
- Implement BackgroundWindowMessageBackend(hwnd) dùng win32gui.PostMessage với WM_KEYDOWN, WM_KEYUP
- BackgroundWindowMessageBackend phải:
  * Serialize input với threading lock
  * Track pressed keys để release trong close()
  * Format lParam đúng cho WM_KEYDOWN/WM_KEYUP

1.2) Tạo lib/system/input_capability.py
- Định nghĩa InputCapabilityState enum: UNVERIFIED, SUPPORTED, UNSUPPORTED, PROBE_IN_PROGRESS
- Định nghĩa InputCapabilityManager class:
  * Nhận hwnd, input_mode, logger khi init
  * Có method check_and_verify_capability() → chạy behavior test
  * Behavior test: gửi WM_KEYDOWN/WM_KEYUP, kiểm tra callback từ game có phản ứng không
  * Lưu trạng thái dùng shelve hoặc pickle (~/.config/cabal_auto/input_capabilities.db)
  * Key: (game_title, hwnd_process_id)
  * Trả về: (state: InputCapabilityState, is_ready_for_hunt: bool)
  * Nếu UNSUPPORTED → log warning, return False

### BƯỚC 2: Tích Hợp Vào Hunt Orchestrator

2.1) Sửa lib/features/hunt/hunt_orchestrator.py:
- Import: InputCapabilityManager, InputBackend, ForegroundSendInputBackend, BackgroundWindowMessageBackend
- Thêm vào __init__:
  * self.input_backend = None
  * self.input_capability_manager = None
  * self.input_mode = "foreground"  # from config
  * self.background_input_fallback = False  # from config
  
- Sửa start_hunt(cfg):
  * Extract input_mode từ cfg.get("input_mode", "foreground")
  * Tạo InputCapabilityManager(hwnd, input_mode, logger)
  * Gọi manager.check_and_verify_capability() TRƯỚC khi tạo threads
  * Nếu NOT ready → log error, set hunt_running=False, return
  * Tạo input_backend phù hợp:
    - input_mode="background" + SUPPORTED → BackgroundWindowMessageBackend(hwnd)
    - Nếu "background" nhưng UNSUPPORTED → fallback to foreground nếu background_input_fallback=True, không thì return
    - Mặc định → ForegroundSendInputBackend()
  * Lưu self.input_backend = backend
  * Trong worker() khi gọi try_cast_skills → truyền input_backend thay vì gọi tap() trực tiếp
  * Trong finally block → backend.close()

### BƯỚC 3: Sửa Tests + Chạy Xác Nhận

3.1) Sửa tests/integration/test_orchestrator_loop.py:
- Thêm mock cho InputCapabilityManager:
  * Mock trả về state=SUPPORTED khi input_mode="background"
  * Mock trả về state=UNVERIFIED nếu chưa test
- Test case: test_background_mode_does_not_call_global_sendinput
  * Cấu hình: input_mode="background"
  * Verify: không có lệnh SendInput(global)
  * Verify: try_cast_skills được gọi với backend có tap() method
  
3.2) Chạy tests:
- python -m pytest tests/integration/test_orchestrator_loop.py::test_background_mode_does_not_call_global_sendinput -xvs
- python -m pytest tests/unit/system/ -k "input_backend or input_capability" -xvs

### BƯỚC 4: Xác Nhận Hoàn Thành

- ✅ Tất cả 3 files mới tồn tại
- ✅ hunt_orchestrator.py có capability gate logic
- ✅ Tests pass without errors
- ✅ Không có silent failures
- ✅ Capability state được persist

requirements:
- Sử dụng existing imports từ project (win32gui, threading, shelve, logging)
- Giữ backward compatibility: default input_mode="foreground"
- Không break existing tests
- Code phải follow CODING_RULES_QUICK_REFERENCE.md
- Không thêm new external dependencies

expected_outcome:
Sau khi hoàn thành, bot sẽ:
1. Kiểm tra xem background input có hoạt động với game không TRƯỚC khi hunt
2. Nếu không hoạt động → báo lỗi, không tấn công im lặng
3. Nếu hoạt động → sử dụng background input
4. Lưu trạng thái để lần sau không cần test lại
```

---

## Hướng Dẫn Từng Bước Chi Tiết

### **Nếu bạn muốn làm thủ công từng file một:**

#### 1️⃣ Tạo `lib/system/input_backend.py`

```python
# lib/system/input_backend.py
from typing import Protocol
from lib.system import win_input

class InputBackend(Protocol):
    def tap(self, key: str) -> None:
        """Tap a single key."""
        ...
    
    def key_down(self, key: str) -> None:
        """Press key down."""
        ...
    
    def key_up(self, key: str) -> None:
        """Release key."""
        ...
    
    def close(self) -> None:
        """Cleanup: release any held keys."""
        ...

class ForegroundSendInputBackend:
    """Wraps lib.system.win_input for foreground input."""
    
    def tap(self, key: str) -> None:
        win_input.tap(key)
    
    def key_down(self, key: str) -> None:
        win_input.key_down(key)
    
    def key_up(self, key: str) -> None:
        win_input.key_up(key)
    
    def close(self) -> None:
        pass
```

#### 2️⃣ Tạo `lib/system/input_capability.py`

```python
# lib/system/input_capability.py
from enum import Enum
from pathlib import Path
import shelve
import threading
from typing import Tuple
from lib.system.hunt_logger import get_hunt_logger

class InputCapabilityState(Enum):
    UNVERIFIED = "unverified"
    PROBE_IN_PROGRESS = "probe_in_progress"
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"

class InputCapabilityManager:
    """Verify if background input works for target game."""
    
    def __init__(self, hwnd: int, input_mode: str, logger=None):
        self.hwnd = hwnd
        self.input_mode = input_mode
        self.logger = logger or get_hunt_logger()
        self._state = InputCapabilityState.UNVERIFIED
        self._lock = threading.Lock()
        self._capabilities_db_path = Path.home() / ".config" / "cabal_auto" / "input_capabilities"
        self._capabilities_db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def check_and_verify_capability(self) -> Tuple[InputCapabilityState, bool]:
        """
        Check if background input is supported.
        Returns: (state, is_ready_for_hunt)
        """
        with self._lock:
            if self.input_mode != "background":
                return InputCapabilityState.SUPPORTED, True
            
            # Load saved capability state
            try:
                with shelve.open(str(self._capabilities_db_path)) as db:
                    key = f"hwnd_{self.hwnd}_background_input"
                    if key in db:
                        saved_state_str = db[key]
                        self._state = InputCapabilityState(saved_state_str)
                        self.logger.log_state_change(f"Loaded background input capability: {self._state.value}")
                        return self._state, self._state == InputCapabilityState.SUPPORTED
            except Exception as e:
                self.logger.log_error(f"Failed to load capability cache: {e}")
            
            # If UNVERIFIED, run probe
            if self._state == InputCapabilityState.UNVERIFIED:
                self._state = InputCapabilityState.PROBE_IN_PROGRESS
                probe_result = self._run_capability_probe()
                self._state = probe_result
                
                # Save result
                try:
                    with shelve.open(str(self._capabilities_db_path)) as db:
                        key = f"hwnd_{self.hwnd}_background_input"
                        db[key] = probe_result.value
                except Exception as e:
                    self.logger.log_error(f"Failed to save capability cache: {e}")
                
                self.logger.log_state_change(f"Background input capability probe result: {self._state.value}")
            
            is_ready = self._state == InputCapabilityState.SUPPORTED
            return self._state, is_ready
    
    def _run_capability_probe(self) -> InputCapabilityState:
        """Run behavior test to verify background input works."""
        try:
            import win32gui
            import time
            
            # Verify window exists
            if not win32gui.IsWindow(self.hwnd):
                self.logger.log_error(f"Target window (hwnd={self.hwnd}) not found")
                return InputCapabilityState.UNSUPPORTED
            
            # Simple probe: send WM_KEYDOWN to target without focus
            WM_KEYDOWN = 0x0100
            vk_code = 0x5A  # 'Z' key
            lParam = (1 << 0) | (0x2C << 16)  # repeat count + scan code
            
            # Send probe key
            result = win32gui.PostMessage(self.hwnd, WM_KEYDOWN, vk_code, lParam)
            if not result:
                self.logger.log_error(f"PostMessage failed for capability probe")
                return InputCapabilityState.UNSUPPORTED
            
            time.sleep(0.1)  # Give window time to process
            
            # TODO: Add more sophisticated detection if needed
            # For now, if PostMessage succeeded, assume it works
            self.logger.log_state_change(f"Background input probe succeeded for hwnd={self.hwnd}")
            return InputCapabilityState.SUPPORTED
            
        except Exception as e:
            self.logger.log_error(f"Background input probe failed: {e}")
            return InputCapabilityState.UNSUPPORTED
```

#### 3️⃣ Tạo `lib/system/background_window_input.py`

```python
# lib/system/background_window_input.py
import win32gui
import threading
from typing import Set
from lib.system.hunt_logger import get_hunt_logger
from lib.system import win_input

class BackgroundWindowMessageBackend:
    """Send input to background window via PostMessage."""
    
    WM_KEYDOWN = 0x0100
    WM_KEYUP = 0x0101
    
    def __init__(self, hwnd: int, logger=None):
        self.hwnd = hwnd
        self.logger = logger or get_hunt_logger()
        self._pressed_keys: Set[str] = set()
        self._lock = threading.Lock()
    
    def tap(self, key: str) -> None:
        """Tap key: down then up."""
        with self._lock:
            self.key_down(key)
            self.key_up(key)
    
    def key_down(self, key: str) -> None:
        """Press key down."""
        with self._lock:
            try:
                vk_code = win_input._vk_from_str(key)
                scan_code = win_input._scancode_from_vk(vk_code)
                is_extended = key in win_input.EXTENDED_KEYS
                
                lParam = (1 << 0) | (scan_code << 16) | (is_extended and (1 << 24) or 0)
                
                result = win32gui.PostMessage(self.hwnd, self.WM_KEYDOWN, vk_code, lParam)
                if result:
                    self._pressed_keys.add(key)
                else:
                    self.logger.log_error(f"Failed to send key_down({key}) via PostMessage")
            except Exception as e:
                self.logger.log_error(f"key_down({key}) failed: {e}")
    
    def key_up(self, key: str) -> None:
        """Release key."""
        with self._lock:
            try:
                vk_code = win_input._vk_from_str(key)
                scan_code = win_input._scancode_from_vk(vk_code)
                is_extended = key in win_input.EXTENDED_KEYS
                
                lParam = (1 << 0) | (scan_code << 16) | (is_extended and (1 << 24) or 0) | (1 << 31)
                
                result = win32gui.PostMessage(self.hwnd, self.WM_KEYUP, vk_code, lParam)
                if result and key in self._pressed_keys:
                    self._pressed_keys.discard(key)
                elif not result:
                    self.logger.log_error(f"Failed to send key_up({key}) via PostMessage")
            except Exception as e:
                self.logger.log_error(f"key_up({key}) failed: {e}")
    
    def close(self) -> None:
        """Release all pressed keys."""
        with self._lock:
            for key in list(self._pressed_keys):
                try:
                    vk_code = win_input._vk_from_str(key)
                    scan_code = win_input._scancode_from_vk(vk_code)
                    is_extended = key in win_input.EXTENDED_KEYS
                    lParam = (1 << 0) | (scan_code << 16) | (is_extended and (1 << 24) or 0) | (1 << 31)
                    
                    win32gui.PostMessage(self.hwnd, self.WM_KEYUP, vk_code, lParam)
                    self._pressed_keys.discard(key)
                except Exception as e:
                    self.logger.log_error(f"Failed to release key {key}: {e}")
```

---

## ✅ Kiểm Tra Danh Sách

Sau khi hoàn thành, kiểm tra:

- [ ] `lib/system/input_backend.py` tồn tại + có InputBackend, ForegroundSendInputBackend
- [ ] `lib/system/input_capability.py` tồn tại + có InputCapabilityManager, InputCapabilityState
- [ ] `lib/system/background_window_input.py` tồn tại + có BackgroundWindowMessageBackend
- [ ] `lib/features/hunt/hunt_orchestrator.py` import 3 class mới
- [ ] `hunt_orchestrator.start_hunt()` gọi `check_and_verify_capability()` trước worker
- [ ] `hunt_orchestrator.start_hunt()` tạo đúng backend dựa trên input_mode + capability state
- [ ] `hunt_orchestrator.py` worker() gọi `backend.tap()` thay vì `tap()` trực tiếp
- [ ] `hunt_orchestrator.py` finally block gọi `backend.close()`
- [ ] Tests mock InputCapabilityManager correctly
- [ ] `pytest tests/integration/test_orchestrator_loop.py -xvs` PASS
- [ ] Không có warning hoặc error

---

**Khi xong, báo tin cho tôi và tôi sẽ xem xét toàn bộ code! 🚀**
