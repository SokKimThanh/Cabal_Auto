# 🎮 Cabal Auto Hunt (Windows)

Hệ thống tự động hóa thông minh cho Cabal VTC Origin với Python - Phiên bản 2.0 với UI/UX được thiết kế lại toàn diện.

## ⭐ Tính năng nổi bật

- 🎯 **Template Matching**: Nhận diện mục tiêu với OpenCV (độ chính xác cao, multi-template support)
- 🧙 **Setup Wizard**: Hướng dẫn thiết lập 5 bước cho người mới (Sprint 16)
- 🛡️ **Buff Auto-Casting**: Tự động cast lại buff trước khi hết hiệu ứng
- 🎮 **Skill Rotation Builder**: Tạo rotation kỹ năng tự động với timing tối ưu
- 📊 **Timing Calculator**: Tính toán thời gian tối ưu dựa trên HP/damage/cooldown
- 📚 **Library Manager**: Quản lý tập trung Monster/Skills/Timing (Sprint 19)
- 🎨 **Icon System**: 39 icon entries với .ico files, thiết kế nhất quán (Sprint 21)
- 🪟 **Auto Window Detection**: Tự động phát hiện Cabal window (Sprint 21)
- ⌨️ **Global Hotkeys**: Ctrl+Shift+R (start hunt), Ctrl+Shift+E (stop hunt), Ctrl+Shift+L (open Skill Manager), Ctrl+Shift+N (open Setup Wizard) - hoạt động khi minimize (system-wide)
- 🌐 **Dual Language**: Hỗ trợ đầy đủ EN/VI với persistence
- 🔒 **First-Run Lock**: Khóa an toàn khi hunt, ngăn chỉnh sửa nhầm
- 📝 **Enhanced Logging**: Dual logging (text + JSON) với structured hunt data

## 📁 Cấu trúc dự án

```
Cabal_Auto/
├── 🚀 app_gui.py           # Main GUI Application (4-tab layout)
├── 📖 README.md            # Project documentation (this file)
├── 📋 CHANGELOG.md         # Version history and changes
├── 📦 requirements.txt     # Python dependencies
│
├── 🎨 assets/              # Assets & resources
│   ├── images/
│   │   ├── icons/         # UI icons (.ico, .png) - 31 files
│   │   ├── monsters/      # Monster templates for vision
│   │   └── skills/        # Skill images
│   └── documents/         # Legacy documents
│
├── ⚙️ config/              # Configuration files
│   └── bot_config.json    # Legacy bot configuration
│
├── 💾 lib/data/            # Application data & databases
│   ├── hunt_config.json   # Hunt configuration (auto-generated)
│   ├── monsters.json      # Monster library database
│   ├── skills.json        # Skills library database
│   ├── vision_*.json      # Vision system configs
│   └── README.md          # Data directory documentation
│
├── 📚 lib/                 # Core library modules (see lib/README.md)
│   ├── system/            # System utilities
│   │   ├── win_input.py       # Windows keyboard input
│   │   └── hunt_logger.py     # Enhanced logging
│   ├── vision/            # Computer vision
│   │   ├── template_matcher.py  # Template matching engine
│   │   └── vision_engine.py     # Vision processing
│   ├── features/          # Game features
│   │   ├── skills/            # Skill system
│   │   ├── skill_rotation/    # Rotation builder
│   │   └── timing/            # Timing calculator
│   ├── ui/                # UI components
│   │   ├── tooltip.py         # i18n tooltips
│   │   ├── icon_helper.py     # Icon management
│   │   ├── library_manager.py # Library manager window
│   │   ├── button_styles.py   # Button styling
│   │   └── capture_helper.py  # Screen capture
│   ├── i18n/              # Internationalization
│   │   └── translations.py    # Translation strings
│   ├── i18n.py            # i18n registry
│   ├── ui_style.py        # Global UI styles
│   └── README.md          # Library documentation ⭐
│
├── 🎮 ui/                  # UI modules (legacy, being migrated to lib/ui/)
│   ├── setup_wizard.py    # 5-step Setup Wizard
│   ├── template_matcher.py # Template matching UI
│   └── auto_hunt.py       # Hunt UI module
│
├── 🔧 scripts/             # Utility scripts & examples
│   ├── main.py            # Main entry point (alternative)
│   ├── main_safe.py       # Safe clicker (legacy)
│   ├── main_skills.py     # Skills demo
│   ├── restructure_project.py # Project restructure utility
│   └── README.md          # Scripts documentation
│
├── 🧪 tests/               # Tests & demos
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── demos/             # Feature demos
│   ├── sprints/           # Sprint-specific tests
│   ├── test_*.py          # Various test files
│   ├── demo_*.py          # Demo scripts
│   └── README.md          # Test documentation
│
├── 📚 docs/                # Documentation (Reorganized v2.0)
│   ├── INDEX.md           # Complete documentation index ⭐
│   ├── README.md          # Documentation overview
│   ├── features/          # Feature specifications (2 files)
│   ├── enhancements/      # UI/UX enhancements (4 files)
│   ├── guides/            # User guides (5 files) ⭐
│   ├── architecture/      # Architecture docs
│   ├── sprints/           # Sprint documentation
│   │   ├── sprint21/      # Sprint 21 - UI/UX Icons ⭐
│   │   ├── sprint20/      # Sprint 20 - Performance
│   │   └── sprint16-19/   # Historical sprints
│   ├── bugfixes/          # Bug fix documentation (16 files)
│   ├── translations/      # Translation documentation
│   ├── ux-enhancements/   # UX improvements
│   ├── archive/           # Archived docs (18 files)
│   ├── legacy/            # Legacy planning docs
│   │   └── hotkeyManager.txt  # Hotkey system plan (moved)
│   └── context/           # System context
│
├── 📝 logs/                # Runtime logs (auto-generated)
│   ├── hunt_structured.jsonl  # JSON structured logs
│   └── README.md          # Logs documentation
│
├── 📂 tmp/                 # Temporary files (gitignored)
│   └── captures/          # Screenshot captures
│
├── 🚀 Launcher Scripts
│   ├── run_venv.ps1       # PowerShell launcher (recommended)
│   ├── run_venv.bat       # Batch launcher (Windows)
│   └── run.bat            # Direct launcher (legacy)
│
└── 🔧 Development
    ├── .vscode/           # VSCode settings
    ├── .github/           # GitHub workflows
    ├── .gitignore         # Git ignore rules
    ├── .flake8            # Python linting config
    └── venv/              # Virtual environment (gitignored)
```

### 📂 Cấu trúc thư mục chi tiết

#### 🎯 Thư mục chính (Root)
- **app_gui.py**: Main application entry point - KHÔNG DI CHUYỂN
- **README.md**: Project documentation - Bạn đang đọc file này
- **CHANGELOG.md**: Version history và release notes
- **requirements.txt**: Python dependencies

#### ⚙️ Config (New!)
- **bot_config.json**: Reference sample từ phần mềm auto Cabal khác (không sử dụng)

#### 📚 Lib Structure
Xem chi tiết trong [lib/README.md](lib/README.md) ⭐

**Highlights:**
- `system/`: Win input, logging
- `vision/`: Template matching, vision engine
- `features/`: Skills, timing, rotation
- `ui/`: Tooltips, icons, library manager
- `i18n/`: Translations

#### 📚 Docs Organization
Xem [docs/INDEX.md](docs/INDEX.md) để navigate toàn bộ documentation ⭐

## 🎯 Yêu cầu hệ thống

- **OS**: Windows 10/11
- **Python**: 3.10+ (tested with 3.10-3.14)
- **RAM**: 4GB+ recommended
- **Screen**: 1920x1080+ (support multiple resolutions)
- **Game**: Cabal VTC Origin (windowed mode recommended)

### Dependencies
```txt
opencv-python==4.12.0.132
numpy==2.2.1
pillow==11.0.0
pyautogui==0.9.54
keyboard==0.13.5
```

## 📦 Cài đặt

### 1. Clone repository
```bash
git clone https://github.com/SokKimThanh/Cabal_Auto.git
cd Cabal_Auto
```

### 2. Tạo virtual environment
```powershell
python -m venv venv
```

### 3. Kích hoạt venv
```powershell
E:\Cabal_Auto\venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
E:\Cabal_Auto\venv\Scripts\Activate.ps1
```

### 4. Cài đặt dependencies
```powershell
pip install -r requirements.txt
```

## 🚀 Quick Start

### Khởi động ứng dụng

**Cách 1: PowerShell Launcher (Recommended)** 🌟
```powershell
.\run_venv.ps1
```
- Tự động tìm Python trong venv (`.venv` hoặc `venv`)
- Fallback to system Python nếu không tìm thấy venv
- Cross-platform compatible

**Cách 2: Batch Launcher (Windows)**
```cmd
run_venv.bat
```
- Tương tự run_venv.ps1 nhưng cho cmd.exe

**Cách 3: Direct (Legacy)**
```powershell
python app_gui.py
```
- Sử dụng Python hiện tại trong PATH
- Không đảm bảo sử dụng đúng venv

### Lần đầu sử dụng - Setup Wizard 🧙‍♂️

Khi chạy lần đầu, **Setup Wizard** sẽ tự động mở và hướng dẫn bạn qua 5 bước:

1. **👋 Welcome** - Giới thiệu và chọn ngôn ngữ (EN/VI)
2. **🪟 Window Selection** - Chọn Cabal window (auto-detect hoặc manual)
3. **🎯 Target Key** - Thiết lập phím chọn mục tiêu (default: TAB)
4. **📸 Template Capture** - Chụp template quái vật
5. **🎮 Skill Rotation** - Tạo skill rotation (tùy chọn)

**Hoàn tất**: Wizard tự động apply settings và đóng lại!

### Giao diện chính - 4 Tabs

#### 1️⃣ **Hunt Tab** - Săn tự động
- Chọn monster từ dropdown
- Templates & timing tự động load
- Click **Start Hunt** để bắt đầu
- **Global Hotkeys**: 
  - `Ctrl+Shift+R`: Start hunt (works when minimized)
  - `Ctrl+Shift+E`: Stop hunt (works when minimized)
  - `Ctrl+Shift+L`: Open Skill Manager (Library → Skills)
  - `Ctrl+Shift+N`: Open Setup Wizard (first-run or manual)
  - `Z`: Switch target (in-game)

#### 2️⃣ **Setup Tab** - Cấu hình
- **Window**: Chọn Cabal window, set bounds
- **Keys**: Target key, attack keys configuration
- **Timing**: Lost timeout, attack duration
- **Global Apply**: Apply settings to all tabs (badge + tooltip)

#### 3️⃣ **Library Tab** - Quản lý thư viện
- **📚 Monster Library**: Thêm/sửa/xóa quái vật, manage templates
- **🎮 Skills Library**: Quản lý kỹ năng (attack/buff), cooldown tracking
- **⏱️ Timing Calculator**: Tính toán timing parameters tối ưu

#### 4️⃣ **Help Tab** - Hướng dẫn
- Keyboard shortcuts reference
- Feature explanations
- Quick tips & tricks

### CLI Hunt (Headless)
```powershell
# Chỉ hunt không GUI
python -c "from lib.system.hunt_logger import hunt; hunt()"
```

## 📖 Hướng dẫn sử dụng

### 🧙‍♂️ Setup Wizard (Recommended for Beginners)

Chạy `python app_gui.py` lần đầu → Setup Wizard tự động mở.

**5 Bước thiết lập**:
1. Chọn ngôn ngữ (EN/VI)
2. Chọn Cabal window (auto-detect)
3. Set target key (TAB)
4. Chụp template quái vật
5. Tạo skill rotation (optional)

**Chi tiết**: Xem [guides/HUONG_DAN_NGUOI_MOI.md](docs/guides/HUONG_DAN_NGUOI_MOI.md) 🇻🇳

---

### 📚 Library Manager - Quản lý tập trung

#### **Monster Library**
1. Click **Library** tab → **Monsters** sub-tab
2. Click **Add New Monster**
3. Nhập thông tin:
   - Name: Tên quái
   - HP: Máu quái
   - Damage/Hit: Damage trung bình
4. **Add Templates**:
   - Click **Add Template**
   - Chọn file PNG từ `assets/images/monsters/`
   - Set threshold (~0.80-0.90)
5. Click **Save**

#### **Skills Library**
1. Click **Library** tab → **Skills** sub-tab
2. Click **Add Skill**
3. Set the skill key: each skill has a `Key` field which is used to bind that skill to an in-game key.

### Important: Attack keys are now derived from skill slots

- The legacy `attack_keys` setting is deprecated. The application now uses per-skill `key` values stored in `skill_slots` as the canonical source for which keys will be pressed during the hunt.
- On first-run or if your existing `hunt_config.json` contains `attack_keys` but no `skill_slots`, the app will automatically migrate those keys into anonymous `skill_slots` and persist the updated config. The app will then attempt to map those anonymous slots to actual attack skills in your skill library when possible.
- To control which keys are used during the hunt, open the Library → Skills manager and assign a `Key` to each skill, then choose skills into the Skill Slots on the Setup tab. The hunt fallback will press keys in the order of configured `skill_slots`.

If you relied on `attack_keys` previously, migration preserves your keys; however please open the Skill Manager afterward to confirm the mapping and adjust names or duplicate keys if needed.
 
## 🔔 Global Hotkeys — Troubleshooting & Notes

The app supports several system-wide (global) hotkeys so you can control the hunt even when the app is minimized:

- Ctrl+Shift+R — Start hunt
- Ctrl+Shift+E — Stop hunt
- Ctrl+Shift+L — Open Skill Manager
- Ctrl+Shift+N — Open Setup Wizard (if available)

Requirements & common issues:

- The Python `keyboard` package must be installed (listed in `requirements.txt`). Install manually if needed:

```powershell
pip install keyboard
```

- On Windows, global hotkeys require elevated permissions. Run the app as Administrator to allow system-wide key capture.

- If hotkeys do not trigger:
  1. Verify `keyboard` is installed and importable.
  2. Run `python app_gui.py` from an Administrator PowerShell.
 3. Check the console for errors like `[Hotkey] Failed to register global hotkeys: ...`.

- If you can't run as Administrator, global hotkeys will not work reliably. Window-focused shortcuts (Ctrl+K, Alt+1/2) still work when the app window is focused.

Testing hotkeys:

1. Open an Administrator PowerShell in the project folder.
2. Run:

```powershell
python app_gui.py
```

3. Press Ctrl+Shift+R (start) / Ctrl+Shift+E (stop) / Ctrl+Shift+L (open Skill Manager) from another window. Watch the app or console for activity.

3. Cấu hình skill:

**Attack Skill**:
```json
{
  "name": "Power Slash",
  "key": "1",
  "type": "attack",
  "cooldown": 1.9,
  "cast_time": 1.7
}
```

**Buff Skill**:
```json
{
  "name": "Regeneration",
  "key": "5",
  "type": "buff",
  "cooldown": 1.0,
  "cast_time": 0.5,
  "duration_sec": 60.0,     // Buff lasts 60s
  "pre_refresh_sec": 5.0    // Recast at 55s (60-5)
}
```

**Result**: Buff tự động recast trước 5 giây khi hết!

#### **Timing Calculator**
1. Click **Library** tab → **Timing Calculator** sub-tab
2. Select monster (HP auto-fill)
3. Select skills for rotation
4. Nhập damage/hit
5. Click **Calculate**
6. **Result**: 
   - Recommended `attack_min_duration_sec`
   - Recommended `lost_timeout_sec`
7. Click **Apply to Config** → Tự động update `hunt_config.json`

---

### 🎮 Skill Rotation Builder

**Setup Wizard - Step 5**:
1. Click **Add Skill** to add skills
2. Click **▲▼** để sắp xếp thứ tự
3. Wizard auto-save rotation

**Manual trong Skills Library**:
1. Tạo skills với đúng thứ tự cast
2. Skills tự động execute theo order trong database

---

## 🚀 Launching & Hotkey Diagnostics

If you run into issues with global hotkeys, it's often because the optional hotkey package isn't installed in the same Python interpreter that's launching the GUI. Use the provided launch helpers to ensure you run the app with the intended interpreter or virtual environment.

- Windows PowerShell (use the workspace venv if available):

```powershell
./run_venv.ps1
```

- Windows (cmd):

```bat
run_venv.bat
```

If global hotkeys fail, the app will show a small diagnostic banner. Click "Details" to view the interpreter path (sys.executable) and the import traceback. Use the provided "Copy pip command" button to copy the exact pip install command for that interpreter, paste it into the same shell shown above, install the package, then click "Retry" in the app.

Example pip command copied by the app (uses the same interpreter shown in the dialog):

```powershell
# "Copied!" will appear after you click the button in-app
C:\path\to\python.exe -m pip install keyboard
```

If you prefer not to install system-wide hotkeys, the app will automatically fall back to window-focused key bindings so shortcuts still work while the app window is focused.

### 🎯 Hunting

1. **Preparation**:
   - Monster đã có templates
   - Skills đã configure
   - Window bounds đã set

2. **Start Hunt**:
   - Hunt Tab → Select monster → **Start Hunt**
   - Hoặc nhấn `Ctrl+Shift+R` (global hotkey)

3. **During Hunt**:
   - `Z`: Switch target (in-game)
   - `Ctrl+Shift+R`: Start hunt
   - `Ctrl+Shift+E`: Stop hunt

4. **Monitor**:
   - Status bar hiển thị hunt state
   - Logs: `logs/hunt_structured.jsonl`

---

### 🔒 First-Run Lock

**Khi hunt đang chạy**:
- ❌ Không thể chỉnh sửa templates
- ❌ Không thể thay đổi settings critical
- ✅ Có thể xem thông tin
- ✅ Có thể stop hunt

**Mục đích**: Ngăn chỉnh sửa nhầm khi auto hunt đang hoạt động.

## 🔧 Configuration Files

### lib/data/hunt_config.json (Auto-generated)
```json
{
  "window_title": "Cabal",
  "window_bounds": {
    "left": 100,
    "top": 100,
    "width": 1280,
    "height": 720
  },
  "target_key": "TAB",
  "attack_keys": ["1", "2", "3", "5"],
  "lost_timeout_sec": 0.75,
  "attack_min_duration_sec": 12.0,
  "templates": [
    {
      "path": "assets/images/monsters/dragon_head.png",
      "threshold": 0.85,
      "region": null
    }
  ]
}
```

**⚠️ Note**: File này được Setup Wizard & Library Manager tự động tạo/cập nhật. Không cần chỉnh sửa thủ công.

**Location**: `lib/data/hunt_config.json`

---

### lib/data/monsters.json (Monster Database)
```json
{
  "monsters": [
    {
      "id": "dragon_001",
      "name": "Dragon",
      "hp": 10000,
      "damage_per_hit": 500,
      "templates": [
        {
          "path": "assets/images/monsters/dragon_head.png",
          "threshold": 0.85,
          "region": null
        },
        {
          "path": "assets/images/monsters/dragon_body.png",
          "threshold": 0.80,
          "region": null
        }
      ]
    }
  ]
}
```

**Quản lý**: Dùng **Library → Monsters** tab (không edit JSON thủ công).

**Location**: `lib/data/monsters.json`

---

### lib/data/skills.json (Skills Database)
```json
{
  "skills": [
    {
      "id": "skill_001",
      "name": "Power Slash",
      "key": "1",
      "type": "attack",
      "cooldown": 1.9,
      "cast_time": 1.7
    },
    {
      "id": "buff_001",
      "name": "Regeneration",
      "key": "5",
      "type": "buff",
      "cooldown": 1.0,
      "cast_time": 0.5,
      "duration_sec": 60.0,
      "pre_refresh_sec": 5.0
    }
  ]
}
```

**Quản lý**: Dùng **Library → Skills** tab (không edit JSON thủ công).

**Location**: `lib/data/skills.json`

**Buff Fields**:
- `duration_sec`: Thời gian buff tồn tại (giây)
- `pre_refresh_sec`: Recast trước khi hết bao nhiêu giây

**Example**: `duration_sec=60`, `pre_refresh_sec=5` → Buff recast ở giây thứ 55.

---

### config/bot_config.json (Reference Sample)

```json
{
  "actions": [
    {
      "key": "Z",
      "scanCode": 44,
      "duration": 1,
      "enabled": true
    }
  ]
}
```

**⚠️ Note**: File mẫu tham khảo từ một phần mềm auto Cabal khác (không phải config của app này). Được giữ lại cho mục đích research và học hỏi cách làm của tools khác. App này sử dụng hệ thống config riêng trong `lib/data/`.

**Location**: `config/bot_config.json` (reference only, có thể xóa an toàn)

---

## 📂 File Organization Summary

### ✅ Files đã di chuyển:
1. **bot_config.json** → `config/bot_config.json` (Legacy config)
2. **test_migration.py** → `tests/test_migration.py` (Test file)
3. **hotkeyManager.txt** → `docs/legacy/hotkeyManager.txt` (Planning doc)

### 📍 Files giữ nguyên ở root:
1. **app_gui.py** - Main application (BẮT BUỘC)
2. **README.md** - Project documentation
3. **CHANGELOG.md** - Version history
4. **requirements.txt** - Dependencies
5. **run_*.bat / run_*.ps1** - Launcher scripts
6. **.gitignore, .flake8, .vscode/** - Development configs

### 🗂️ Thư mục mới:
- **config/**: Reference samples (bot_config.json từ phần mềm khác)
- **docs/legacy/**: Legacy planning documents (hotkeyManager.txt)

### 🚫 Files đã xóa/deprecated:
- **interception.dll**: Legacy DLL không còn sử dụng (có thể xóa an toàn)
- **tmp_test_dir/**: Temporary test directory (có thể xóa)

### 📝 Migration Notes:
Khi update code, lưu ý các paths đã thay đổi:
- `bot_config.json` → `config/bot_config.json`
- Các test files ở root → `tests/`
- Planning docs ở root → `docs/legacy/`

## 📊 Development Timeline

### Sprint 21 - UI/UX Icon System Enhancement ⭐ **CURRENT**
**Status**: 16/16 patches complete (100%) 🎉  
**Duration**: Oct 15-21, 2025

**Key Achievements**:
- ✅ **Icon System**: 39 icon entries, 28 with .ico files (72% coverage)
- ✅ **Icon Placement Rules**: Comprehensive design guidelines
  - Action buttons: Icon LEFT
  - Navigation: Next=RIGHT, Back=LEFT
  - Multi-state buttons: Icon changes with state
- ✅ **Contrast Ratio**: 100% button consistency (3:1 minimum)
- ✅ **Documentation Organization**: Reorganized 40+ docs into 8 categories

**Patches**: See [docs/sprint21/](docs/sprint21/) for details.

---

### Sprint 20 - Performance & System Improvements
**Status**: ✅ Complete  
**Focus**: Code optimization, error handling, performance tuning

---

### Sprint 19 - Library Manager
**Status**: ✅ Complete  
**Features**:
- 📚 Monster Library with card UI
- 🎮 Skills Library with buff support
- ⏱️ Timing Calculator integration

---

### Sprint 18 - 4-Tab UI Reorganization
**Status**: ✅ Complete (75%)  
**Features**:
- 🎯 Hunt Tab (main hunting interface)
- ⚙️ Setup Tab (configuration)
- 📊 Stats Tab (statistics - partial)
- ❓ Help Tab (documentation)

---

### Sprint 16 - Setup Wizard
**Status**: ✅ Complete  
**Features**:
- 🧙‍♂️ 5-step wizard for first-time users
- Auto window detection
- Template capture integration
- Skill rotation builder

---

### Sprint 13-15 - Core Features
**Status**: ✅ Complete  
**Features**:
- Template matching system
- Buff auto-casting runtime
- Logging system (dual format)
- Skills migration
- Timing recommendations

---

**Total Sprints**: 21  
**Total Patches (Sprint 21)**: 16  
**Lines of Code**: ~8,000+ lines  
**Documentation Files**: 40+ markdown files

## 🧪 Testing & Debugging

### Test Files
```bash
# Template matching test
python tests/opencv_test.py

# Integration tests
python tests/test_template_matcher_integration.py
python tests/test_comprehensive_system.py

# Feature demos
python tests/demo_template_save.py
python tests/demo_vision_wizard_cleanup.py
python tests/demo_save_tooltip.py

# Specific feature tests
python tests/test_setup_wizard.py
python tests/test_rotation.py
python tests/test_timing_calculator_ui.py
```

### Test Recognition (In-App)
1. Open **Library → Monsters**
2. Select a monster with templates
3. Click **Test Recognition**
4. Screenshot sẽ được capture
5. Kết quả hiển thị: template matched, confidence, box location

### Debugging
- **Logs**: Check `logs/hunt_structured.jsonl` for detailed events
- **Screenshots**: `tmp/captures/` chứa screenshots khi test
- **Config**: Verify `data/hunt_config.json` settings
- **Console**: Run với verbose mode (nếu có lỗi)

## 📝 Logging System

### Dual Logging
- **hunt_structured.jsonl**: Machine-readable JSON Lines format
- Structured events: match, attack, buff, error, etc.
- Real-time logging during hunt

### Log Format
```json
{
  "timestamp": "2025-10-21T14:30:45",
  "event": "match",
  "template": "dragon_head.png",
  "confidence": 0.923,
  "box": [100, 150, 200, 100],
  "monster": "Dragon"
}
```

### Log Events
- `match`: Template matched
- `attack`: Attack skill cast
- `buff`: Buff skill cast  
- `buff_refresh`: Buff auto-recast
- `target_lost`: Target lost (timeout)
- `error`: Error occurred

### Log Location
```
logs/
└── hunt_structured.jsonl  # Rotating, structured format
```

## 🛡️ Safety Features

- ✅ **First-Run Lock**: Khóa chỉnh sửa khi hunt đang chạy
- ✅ **Template Lock**: Hold-to-save mechanism (prevent accidental overwrites)
- ✅ **Prerequisites Validation**: Check config before hunt starts
- ✅ **Global Hotkeys**: 
  - `Ctrl+Shift+R`: Start hunt (works when minimized)
  - `Ctrl+Shift+E`: Stop hunt (works when minimized)
  - Customizable in Setup → Global Hotkeys section
- ✅ **Window Restore**: Guaranteed window restoration on errors
- ✅ **Input Validation**: Prevents invalid configurations
- ✅ **Error Handling**: Graceful degradation on errors
- ✅ **Auto Window Detection**: Tự động detect Cabal window (no manual config)
- ✅ **Safe Failover**: Icon system falls back to emoji if .ico missing

## 🐛 Troubleshooting

### OpenCV not found
```bash
pip install opencv-python==4.12.0.132
```

### Keyboard module issues (Admin required)
```bash
# Run PowerShell as Administrator
# Right-click PowerShell → Run as Administrator
python app_gui.py
```

### Template matching fails
1. **Lower threshold**: Try 0.75-0.80 (default 0.85)
2. **Use Test Recognition**: Library → Monsters → Test Recognition
3. **Check template quality**: Ensure clear, high-contrast images
4. **Set region**: Focus on specific area instead of full screen
5. **Multiple templates**: Add more templates for same monster (different angles)

### Buff not auto-casting
1. **Check duration_sec > 0** in Skills Library
2. **Verify pre_refresh_sec < duration_sec**
3. **Skill type = "buff"** (not "attack")
4. **Monitor logs**: Check `logs/hunt_structured.jsonl` for buff events
5. **Cooldown**: Ensure cooldown allows recast

### Setup Wizard not appearing
1. **Delete config**: Remove `data/hunt_config.json`
2. **Restart app**: `python app_gui.py`
3. **Wizard auto-launches** on first run

### Window not detected
1. **Manual selection**: Setup → Window → Select from dropdown
2. **Cabal running**: Ensure Cabal is running before app
3. **Window title**: Check if window title contains "Cabal"

### Language not saving
- ✅ Fixed in Sprint 21 Patch 3 (BUGFIX_LANGUAGE_PERSISTENCE)
- Language persists across sessions automatically

### Icons showing emoji instead of .ico
- **Expected behavior**: Fallback to emoji if .ico file missing
- **Fix**: Add missing .ico files to `assets/images/icons/`
- **Coverage**: 72% (28/39 buttons have .ico files)

## 📚 Documentation

### Quick Links
- **📖 Complete Index**: [docs/INDEX.md](docs/INDEX.md) - Complete documentation navigator ⭐
- **👋 Beginner Guide**: [docs/guides/HUONG_DAN_NGUOI_MOI.md](docs/guides/HUONG_DAN_NGUOI_MOI.md) 🇻🇳
- **🎨 Icon Design Rules**: [docs/sprint21/ICON_PLACEMENT_RULES.md](docs/sprint21/ICON_PLACEMENT_RULES.md)
- **📊 Icon Coverage**: [docs/sprint21/ICON_STATUS_REPORT.md](docs/sprint21/ICON_STATUS_REPORT.md)
- **🪟 Window Settings**: [docs/guides/ADVANCED_WINDOW_SETTINGS_GUIDE.md](docs/guides/ADVANCED_WINDOW_SETTINGS_GUIDE.md)

### Documentation Structure
```
docs/
├── INDEX.md              # Complete documentation index ⭐
├── features/             # Feature specifications (2 files)
├── enhancements/         # UI/UX enhancements (4 files)
├── guides/               # User guides (5 files)
├── sprint21/             # Sprint 21 docs (8 files)
├── bugfixes/             # Bug fixes (16 files)
├── sprints/              # Historical sprints
└── archive/              # Archived docs (18 files)
```

### By Category
- **Features**: [docs/features/](docs/features/)
- **Enhancements**: [docs/enhancements/](docs/enhancements/)
- **Guides**: [docs/guides/](docs/guides/)
- **Bug Fixes**: [docs/bugfixes/](docs/bugfixes/)
- **Sprint 21**: [docs/sprint21/](docs/sprint21/)
- **Archive**: [docs/archive/](docs/archive/)

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Make changes following project style:
   - **Icon System**: Follow [ICON_PLACEMENT_RULES.md](docs/sprint21/ICON_PLACEMENT_RULES.md)
   - **UI Style**: Use `lib/ui_style.py` for consistent theming
   - **i18n**: Add translations to `lib/i18n/en.json` & `vi.json`
4. Add tests if applicable (see `tests/`)
5. Update documentation
6. Commit changes (`git commit -m 'Add AmazingFeature'`)
7. Push to branch (`git push origin feature/AmazingFeature`)
8. Open Pull Request

### Code Style Guidelines
- **Icons**: .ico > .png > emoji (always try .ico first)
- **Action buttons**: Icon LEFT (`compound='left'`)
- **Navigation buttons**: Context-aware (Next=RIGHT, Back=LEFT)
- **NO emoji in text** when icon present
- **i18n**: All user-facing text must have translations

## ⚠️ Disclaimer

This tool is for **educational purposes only**. 

- Use at your own risk
- Ensure compliance with game terms of service
- Author is not responsible for any account actions
- Recommended for learning Python automation & OpenCV

## 📄 License

MIT License - See LICENSE file for details

## 👥 Credits

- **Developer**: [SokKimThanh](https://github.com/SokKimThanh)
- **AI Assistant**: GitHub Copilot
- **Libraries**: 
  - OpenCV (computer vision)
  - PyAutoGUI (automation)
  - Pillow (image processing)
  - Keyboard (hotkeys)
- **Community**: Python & OpenCV community

## 📞 Support & Resources

### Documentation
- **Complete Index**: [docs/INDEX.md](docs/INDEX.md) ⭐
- **Beginner Guide**: [docs/guides/HUONG_DAN_NGUOI_MOI.md](docs/guides/HUONG_DAN_NGUOI_MOI.md) 🇻🇳
- **Icon Rules**: [docs/sprint21/ICON_PLACEMENT_RULES.md](docs/sprint21/ICON_PLACEMENT_RULES.md)

### Getting Help
1. **Check guides**: [docs/guides/](docs/guides/)
2. **Search bugfixes**: [docs/bugfixes/](docs/bugfixes/)
3. **Open issue**: [GitHub Issues](https://github.com/SokKimThanh/Cabal_Auto/issues)
4. **Review archive**: [docs/archive/](docs/archive/) for historical context

### Links
- **Repository**: [github.com/SokKimThanh/Cabal_Auto](https://github.com/SokKimThanh/Cabal_Auto)
- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **Latest Sprint**: [docs/sprint21/](docs/sprint21/)

---

## � Project Organization & Best Practices

### File Placement Guidelines

#### ✅ Root Directory - Chỉ giữ files quan trọng
- **app_gui.py**: Main entry point (BẮT BUỘC ở root)
- **README.md, CHANGELOG.md**: Project documentation
- **requirements.txt**: Dependencies list
- **Launcher scripts**: run_venv.ps1, run_venv.bat, run.bat
- **Development configs**: .gitignore, .flake8, .vscode/

#### 📦 Configuration Files
- **Active configs**: `lib/data/*.json` (hunt_config, monsters, skills) ⭐
- **Reference samples**: `config/*.json` (bot_config - từ phần mềm khác)
- **Development configs**: `.vscode/`, `.github/`

#### 🧪 Test Files
- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Demo scripts**: `tests/demos/`
- **Sprint tests**: `tests/sprints/`
- ⚠️ **KHÔNG** để test files ở root (ví dụ: test_migration.py đã di chuyển)

#### 📚 Documentation
- **User guides**: `docs/guides/`
- **Technical docs**: `docs/architecture/`, `docs/features/`
- **Sprint docs**: `docs/sprints/sprint21/`, etc.
- **Legacy planning**: `docs/legacy/` (ví dụ: hotkeyManager.txt)
- **Archive**: `docs/archive/` (old summaries, outdated docs)

#### 🔧 Scripts & Utilities
- **Example scripts**: `scripts/main*.py`
- **Utility scripts**: `scripts/restructure_project.py`
- **Project tools**: `scripts/`

### Clean Root Philosophy

**Goal**: Root directory chỉ chứa essential files cần thiết để chạy app.

**Rationale**:
- ✅ Dễ navigate và tìm files
- ✅ Clear separation of concerns
- ✅ Professional project structure
- ✅ Easier for new developers to understand

**Recent Changes (Oct 23, 2025)**:
```
Moved: bot_config.json → config/bot_config.json
Moved: test_migration.py → tests/test_migration.py
Moved: hotkeyManager.txt → docs/legacy/hotkeyManager.txt
```

### Where to Put New Files?

| File Type | Location | Example |
|-----------|----------|---------|
| Test file | `tests/` | `test_feature.py` |
| Demo script | `tests/demos/` | `demo_feature.py` |
| Config file | `lib/data/` or `config/` | `feature_config.json` |
| Documentation | `docs/guides/` or `docs/features/` | `FEATURE_GUIDE.md` |
| UI component | `lib/ui/` | `feature_dialog.py` |
| Feature module | `lib/features/` | `feature/module.py` |
| Legacy script | `scripts/` | `legacy_tool.py` |
| Planning doc | `docs/legacy/` | `feature_plan.txt` |

---

## �📊 Project Stats

**Version**: 2.0.0  
**Last Updated**: October 23, 2025  
**Status**: Production Ready ✅

**Development**:
- **Total Sprints**: 21 (Sprint 21 complete)
- **Total Patches (Sprint 21)**: 16/16 (100%)
- **Lines of Code**: ~8,000+ lines
- **Documentation**: 40+ markdown files (reorganized v2.0)
- **Icon Coverage**: 72% (28/39 buttons with .ico files)
- **Languages**: English, Tiếng Việt 🇻🇳

**Project Structure**:
- **Root files**: 6 essential files only (cleaned Oct 23, 2025)
- **Main directories**: 11 (lib, ui, tests, docs, assets, logs, scripts, config, tmp, venv, .vscode)
- **Config organization**: Active configs in `lib/data/`, legacy in `config/`
- **Documentation**: Organized in 8 categories with INDEX.md navigator

**Features**:
- ✅ 5-step Setup Wizard
- ✅ 4-tab UI layout
- ✅ Library Manager (Monster/Skills/Timing)
- ✅ Template matching with multi-template support
- ✅ Buff auto-casting system
- ✅ Skill rotation builder
- ✅ Auto window detection
- ✅ Keyboard shortcuts
- ✅ First-run lock safety
- ✅ Icon system with .ico priority
- ✅ Dual language (EN/VI)
- ✅ Structured logging (JSON)

**Next Sprint**: Sprint 22 - Target Lock & Advanced Features

---

Made with ❤️ by [SokKimThanh](https://github.com/SokKimThanh)
