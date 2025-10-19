# Cabal Auto (Windows)

Hệ thống tự động hóa thông minh cho Cabal VTC Origin với Python: quản lý kỹ năng, nhận diện mục tiêu, tự động cast buff, và nhiều tính năng nâng cao.

## ✨ Tính năng chính

- 🎯 **Template Matching**: Nhận diện mục tiêu với OpenCV (độ chính xác cao)
- 🛡️ **Buff Auto-Casting**: Tự động cast lại buff trước khi hết hiệu ứng
- 🎮 **Skill Management**: Quản lý kỹ năng với cooldown tracking
- 📊 **Timing Optimization**: Tính toán thời gian tối ưu dựa trên HP/damage
- 📝 **Enhanced Logging**: Dual logging (text + JSON) cho debugging
- 🖼️ **Monster Manager**: Quản lý quái vật với multi-template support
- 🌐 **Dual Language**: Hỗ trợ đầy đủ EN/VI

## 📁 Cấu trúc thư mục

```
Cabal_Auto/
├── app_gui.py              # Main GUI application ⭐
├── auto_hunt.py            # CLI hunt script
├── requirements.txt        # Dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
│
├── assets/                # Asset files
│   ├── images/
│   │   ├── monsters/     # Monster templates
│   │   └── skills/       # Skill images
│   └── documents/        # Project documentation
│
├── data/                  # Configuration & data files
│   ├── config.json       # Basic config (legacy)
│   ├── hunt_config.json  # Hunt configuration
│   ├── monsters.json     # Monster database
│   ├── skills.json       # Skills database
│   └── README.md         # Data directory docs
│
├── lib/                   # Library modules
│   ├── win_input.py      # Windows input
│   ├── hunt_logger.py    # Logging system
│   ├── template_matcher.py  # Template matching
│   ├── timing_calculator.py # Timing optimization
│   ├── skill_runtime.py  # Skill management
│   ├── skill_migrator.py # Migration tool
│   └── README.md         # Library docs
│
├── scripts/               # Example scripts
│   ├── main.py           # ⚠️ Unsafe (not recommended)
│   ├── main_safe.py      # ✅ Safe clicker
│   ├── main_skills.py    # Legacy skill script
│   └── README.md         # Scripts docs
│
├── tests/                 # Test files
│   ├── opencv_test.py    # OpenCV testing
│   ├── test_template_matcher_integration.py
│   └── README.md         # Tests docs
│
├── docs/                  # Documentation
│   ├── PROJECT_SUMMARY.py # Complete project summary
│   ├── sprints/          # Sprint documentation
│   │   ├── sprint13_demo.py
│   │   ├── sprint14_demo.py
│   │   ├── sprint15_demo.py
│   │   ├── SPRINT15_SUMMARY.txt
│   │   └── SPRINT15_COMPLETE.md
│   └── README.md         # Docs directory info
│
├── logs/                  # Runtime logs (auto-generated)
│   ├── hunt.log          # Human-readable logs
│   └── hunt_structured.jsonl # JSON logs
│
└── venv/                  # Virtual environment
```

## 🎯 Yêu cầu hệ thống

- **OS**: Windows 10/11
- **Python**: 3.10+ (3.14 tested and working)
- **Dependencies**: 
  - opencv-python 4.12.0 ✅
  - numpy 2.3.4
  - pyautogui 0.9.54
  - pillow
  - keyboard

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

### GUI Application (Recommended)
```powershell
python app_gui.py
```

**Features:**
- Monster Manager: Tạo/sửa/xóa quái, thêm templates
- Skills Manager: Cấu hình kỹ năng và buff
- Hunt tab: Săn tự động với template matching
- Timing Calculator: Tối ưu timing parameters

**Hotkeys:**
- `F9`: Stop hunt (global hotkey)
- `ESC`: Stop hunt (in GUI)

### CLI Hunt Script
```powershell
python auto_hunt.py
```

Headless hunting với config từ `data/hunt_config.json`.

### Simple Clicker (Legacy)
```powershell
python scripts/main_safe.py
```

**Hotkeys:**
- `F8`: Toggle on/off
- `F7`: Pause/resume
- `F9`: Exit

## 📖 Hướng dẫn sử dụng

### 1. Cấu hình Monster
1. Mở `app_gui.py`
2. Vào Monster Manager
3. Tạo monster mới:
   - Nhập tên, HP, damage
   - Thêm template images
   - Set threshold (~0.80-0.90)
   - Configure window bounds

### 2. Cấu hình Skills
1. Vào Skills Manager
2. Tạo skill mới:
   - **Attack**: Nhập tên, key, cooldown, cast time
   - **Buff**: Thêm duration_sec, pre_refresh_sec
3. Save skill

### 3. Configure Hunt
1. Vào Hunt tab
2. Chọn monster từ dropdown
3. Các settings tự động apply:
   - Templates
   - Window bounds
   - Recommended timing
4. Click "Start Hunt"

### 4. Buff Auto-Casting Setup
```json
// data/skills.json
{
  "name": "Regeneration",
  "key": "5",
  "type": "buff",
  "cooldown": 1.0,
  "cast_time": 0.5,
  "duration_sec": 60.0,    // Buff lasts 60s
  "pre_refresh_sec": 5.0   // Recast at 55s mark
}
```

Result: Buff auto-recasts at 55s, seamless uptime!

## 🔧 Configuration Files

### data/hunt_config.json
```json
{
  "window_title": "Cabal",
  "target_key": "TAB",
  "attack_keys": ["1", "2", "3"],
  "lost_timeout_sec": 0.75,
  "attack_min_duration_sec": 12.0,
  "templates": [...],
  "window_bounds": {...}
}
```

### data/monsters.json
```json
{
  "name": "Dragon",
  "hp": 10000,
  "damage_per_hit": 500,
  "templates": [
    {
      "path": "assets/images/monsters/dragon.png",
      "threshold": 0.85
    }
  ]
}
```

### data/skills.json
```json
{
  "name": "Skill Name",
  "key": "1",
  "type": "attack" | "buff",
  "cooldown": 1.9,
  "cast_time": 1.7,
  "duration_sec": 60.0,     // For buffs
  "pre_refresh_sec": 5.0    // For buffs
}
```

## 📊 Features by Sprint

| Sprint | Feature | Status |
|--------|---------|--------|
| 1-4 | Monster/Template Management | ✅ |
| 5 | UX Polish & Optimization | ✅ |
| 6 | Screenshot Capture | ✅ |
| 7 | Test Recognition | ✅ |
| 8 | Enhanced Logging System | ✅ |
| 9 | OpenCV Integration | ✅ |
| 10 | Timing Recommendations | ✅ |
| 11 | Skills Migration | ✅ |
| 12 | Template Matcher Integration | ✅ |
| 13 | Apply Timing to Config | ✅ |
| 14 | Buff Auto-Casting Runtime | ✅ |
| 15 | Buff Duration GUI Fields | ✅ |

**Status**: All 15 sprints complete! 🎉

## 🧪 Testing

### Run tests
```bash
# Template matching test
python tests/opencv_test.py

# Integration test
python tests/test_template_matcher_integration.py
```

### Run demos
```bash
# Sprint demos
python docs/sprints/sprint13_demo.py
python docs/sprints/sprint14_demo.py
python docs/sprints/sprint15_demo.py

# Project summary
python docs/PROJECT_SUMMARY.py
```

## 📝 Logging

### Dual Logging System
- **hunt.log**: Human-readable text format
- **hunt_structured.jsonl**: Machine-readable JSON Lines

### Log Locations
```
logs/
├── hunt.log              # Rotating, 10MB max, 5 backups
└── hunt_structured.jsonl # JSON Lines format
```

### Example Log Entry
```json
{
  "timestamp": "2025-10-18T14:30:45",
  "event": "match",
  "template": "dragon_head",
  "confidence": 0.923,
  "box": [100, 150, 200, 100]
}
```

## 🛡️ Safety Features

- ✅ **Failsafe**: Move mouse to (0,0) to emergency stop
- ✅ **Global Hotkeys**: F9 stops hunt even when minimized
- ✅ **Window Restore**: Guaranteed window restoration on errors
- ✅ **Input Validation**: Prevents invalid configurations
- ✅ **Error Handling**: Graceful degradation on errors

## 🐛 Troubleshooting

### OpenCV not found
```bash
# Install OpenCV
pip install opencv-python==4.12.0
```

### Keyboard module issues
```bash
# Run as Administrator
# Right-click PowerShell → Run as Administrator
python app_gui.py
```

### Template matching fails
1. Lower threshold (try 0.75-0.80)
2. Adjust region to focus on specific area
3. Use Test Recognition button to verify
4. Check template image quality

### Buff not auto-casting
1. Check duration_sec > 0 in skills.json
2. Verify pre_refresh_sec < duration_sec
3. Check skill type = "buff"
4. Monitor logs for skill_runtime errors

## 📚 Documentation

- Main context: `docs/context/CONTEXT_MAIN.txt` (moved from `assets/documents/Ngữ cảnh tạo auto cabal.txt`)
- Project Summary: `docs/PROJECT_SUMMARY.py`
- Sprint 15 Guide: `docs/sprints/SPRINT15_COMPLETE.md`
- API Docs: See README in each directory (lib/, data/, tests/, etc.)

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests if applicable
5. Update documentation
6. Submit pull request

## ⚠️ Disclaimer

This tool is for educational purposes only. Use at your own risk. Ensure compliance with game terms of service.

## 📄 License

[Add your license here]

## 👥 Credits

- **Developer**: SokKimThanh
- **Assistant**: GitHub Copilot
- **Community**: Python community for excellent libraries

## 📞 Support

- **Issues**: Open GitHub issue
- **Documentation**: See `docs/` directory
- **Examples**: See `docs/sprints/` for demos

---

**Version**: 1.0.0  
**Last Updated**: October 18, 2025  
**Status**: Production Ready ✅  
**Total Lines**: ~5,166 lines  
**Sprints Completed**: 15/15 🎉
