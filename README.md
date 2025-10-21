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
- ⌨️ **Global Hotkeys**: Ctrl+Shift+R (start hunt), Ctrl+Shift+E (stop hunt) - hoạt động khi minimize
- 🌐 **Dual Language**: Hỗ trợ đầy đủ EN/VI với persistence
- 🔒 **First-Run Lock**: Khóa an toàn khi hunt, ngăn chỉnh sửa nhầm
- 📝 **Enhanced Logging**: Dual logging (text + JSON) với structured hunt data

## 📁 Cấu trúc dự án

```
Cabal_Auto/
├── app_gui.py              # 🚀 Main GUI Application (4-tab layout)
├── README.md               # This file
├── requirements.txt        # Python dependencies
│
├── assets/                 # Assets & resources
│   ├── images/
│   │   ├── icons/         # UI icons (.ico, .png) - 31 files
│   │   ├── monsters/      # Monster templates
│   │   └── skills/        # Skill images
│   └── documents/         # Legacy documents
│
├── data/                   # Configuration & database
│   ├── hunt_config.json   # Hunt configuration (auto-generated)
│   ├── monsters.json      # Monster library database
│   ├── skills.json        # Skills library database
│   └── README.md          # Data directory docs
│
├── lib/                    # Core library modules
│   ├── features/          # Feature modules
│   │   ├── combat/       # Combat system (skill_runtime.py, timing_calculator.py)
│   │   ├── library/      # Library managers
│   │   └── wizard/       # Setup Wizard
│   ├── system/           # System modules (hunt_logger.py, win_input.py)
│   ├── ui/               # UI components (dialogs, frames, helpers)
│   ├── vision/           # Vision modules (template_matcher.py)
│   ├── i18n/             # i18n translations (en.json, vi.json)
│   ├── i18n.py           # i18n handler
│   ├── ui_style.py       # UI styling & theming
│   └── README.md         # Library docs
│
├── ui/                     # Legacy UI modules (being phased out)
│   ├── setup_wizard.py    # 5-step Setup Wizard ⭐
│   ├── template_matcher.py # Template Matcher UI
│   └── auto_hunt.py       # Hunt UI module
│
├── scripts/                # Example & utility scripts
│   ├── main_safe.py       # ✅ Safe clicker (legacy)
│   └── README.md          # Scripts docs
│
├── tests/                  # Test & demo files
│   ├── test_*.py          # Unit tests
│   ├── demo_*.py          # Feature demos
│   ├── opencv_test.py     # OpenCV testing
│   └── README.md          # Tests docs
│
├── docs/                   # 📚 Documentation (Reorganized v2.0)
│   ├── INDEX.md           # Complete documentation index ⭐
│   ├── README.md          # Docs overview
│   ├── features/          # Feature specifications (2 files)
│   ├── enhancements/      # UI/UX enhancements (4 files)
│   ├── guides/            # User guides & tutorials (5 files)
│   ├── sprint21/          # Sprint 21 - UI/UX Icons (8 files) ⭐
│   ├── bugfixes/          # Bug fix documentation (16 files)
│   ├── sprints/           # Historical sprints (16-20)
│   ├── archive/           # Archived docs (18 files)
│   └── context/           # System context
│
├── logs/                   # Runtime logs (auto-generated)
│   └── hunt_structured.jsonl # JSON structured logs
│
└── tmp/                    # Temporary files
    └── captures/          # Screenshot captures
```

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
```powershell
python app_gui.py
```

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

### data/hunt_config.json (Auto-generated)
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

---

### data/monsters.json (Monster Database)
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

---

### data/skills.json (Skills Database)
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

**Buff Fields**:
- `duration_sec`: Thời gian buff tồn tại (giây)
- `pre_refresh_sec`: Recast trước khi hết bao nhiêu giây

**Example**: `duration_sec=60`, `pre_refresh_sec=5` → Buff recast ở giây thứ 55.

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

## 📊 Project Stats

**Version**: 2.0.0  
**Last Updated**: October 21, 2025  
**Status**: Production Ready ✅

**Development**:
- **Total Sprints**: 21 (Sprint 21 complete)
- **Total Patches (Sprint 21)**: 16/16 (100%)
- **Lines of Code**: ~8,000+ lines
- **Documentation**: 40+ markdown files (reorganized v2.0)
- **Icon Coverage**: 72% (28/39 buttons with .ico files)
- **Languages**: English, Tiếng Việt 🇻🇳

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
