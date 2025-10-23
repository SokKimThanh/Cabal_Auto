# Configuration Directory

Thư mục này chứa các file cấu hình cho ứng dụng.

## 📁 Files

### bot_config.json

**Status**: Reference Sample / Không sử dụng

**Mô tả**: File mẫu tham khảo từ một phần mềm auto Cabal khác. Không phải config của app này.

**Cấu trúc mẫu**:
```json
{
  "actions": [
    {
      "key": "Z",           // Phím nhấn
      "scanCode": 44,       // Scan code của phím
      "duration": 1,        // Thời gian giữ (giây)
      "enabled": true       // Bật/tắt action
    }
  ]
}
```

**Purpose**: 
- 📚 **Reference only**: Mẫu tham khảo để học cách phần mềm khác làm auto
- 🔍 **Research**: Khám phá cấu trúc config của auto tool khác
- 💡 **Inspiration**: Có thể lấy ý tưởng cho features tương lai

**Current Status**: 
- ⚠️ **KHÔNG** được sử dụng trong `app_gui.py`
- ⚠️ **KHÔNG** được sử dụng trong bất kỳ script nào của project
- ⚠️ **KHÔNG** có code nào đọc file này
- 📝 Chỉ là file tham khảo, có thể xóa an toàn nếu không cần

---

---

## ⚠️ Important Note

**bot_config.json là reference sample từ phần mềm khác, KHÔNG phải config của app này!**

App này (Cabal_Auto) có hệ thống config riêng hoàn toàn khác, xem bên dưới.

---

## 🆕 Cấu hình hiện tại của app

App chính (app_gui.py) sử dụng các file cấu hình sau (KHÔNG dùng bot_config.json):

### Primary Configs (lib/data/)

1. **hunt_config.json** - Hunt configuration
   - Window settings
   - Keys configuration
   - Timing parameters
   - Template paths
   - **Managed by**: Setup Wizard, Library Manager

2. **monsters.json** - Monster database
   - Monster definitions
   - HP, damage stats
   - Template configurations
   - **Managed by**: Library → Monsters tab

3. **skills.json** - Skills database
   - Attack/Buff skills
   - Cooldowns, cast times
   - Buff durations
   - **Managed by**: Library → Skills tab

4. **vision_*.json** - Vision system configs
   - Template matching settings
   - Region configurations
   - **Managed by**: Vision system

### Config Locations

```
Cabal_Auto/
├── config/               # Legacy configs (this directory)
│   └── bot_config.json  # Legacy bot config
│
└── lib/data/            # Active app configs ⭐
    ├── hunt_config.json   # Main hunt config
    ├── monsters.json      # Monster library
    ├── skills.json        # Skills library
    ├── vision_region.json # Vision regions
    └── vision_templates.json # Vision templates
```

---

## 🔧 Quản lý cấu hình

### ❌ KHÔNG làm (Deprecated)
- Edit `config/bot_config.json` cho app chính
- Sử dụng bot_config.json trong hunt flow

### ✅ NÊN làm (Recommended)
- Sử dụng **Setup Wizard** để cấu hình lần đầu
- Dùng **Library Manager** để quản lý Monsters/Skills
- Edit `lib/data/hunt_config.json` qua UI (Setup tab)
- Let the app auto-generate configs

---

## 📝 Migration Notes

### Understanding Config Systems

**bot_config.json** (Reference from other tool):
```
{
  "actions": [...]  // Simple action list
}
```
- Simple key sequences
- No monster/skill management
- Manual timing control

**Cabal_Auto** (This app):
```
lib/data/
  ├── hunt_config.json    // Window, keys, timing
  ├── monsters.json       // Monster library với templates
  └── skills.json         // Skills với auto-rotation
```
- Advanced template matching
- Library management system
- Auto-calculated timing
- Buff auto-refresh
- Skill rotation builder

### If You Want Similar Features

Nếu bạn muốn features giống bot_config.json:

1. **Simple Key Sequences**:
   - Use: Setup Wizard → Keys configuration
   - Config: `hunt_config.json` → `attack_keys[]`

2. **Timing Control**:
   - Use: Library → Timing Calculator
   - Config: `hunt_config.json` → `attack_min_duration_sec`

3. **Advanced Features** (không có trong bot_config.json):
   - ✅ Template matching với monsters.json
   - ✅ Skill rotation với skills.json
   - ✅ Buff auto-refresh
   - ✅ Library Manager UI

---

## 🚀 Quick Start

### Lần đầu chạy app:
```powershell
python app_gui.py
```

→ Setup Wizard sẽ tự động tạo `lib/data/hunt_config.json`

### Nếu muốn reset config:
```powershell
# Xóa config cũ
Remove-Item lib\data\hunt_config.json

# Chạy lại app → Setup Wizard sẽ xuất hiện
python app_gui.py
```

---

## 📚 Related Documentation

- **App Configuration**: [../lib/data/README.md](../lib/data/README.md)
- **Setup Wizard**: [../docs/guides/HUONG_DAN_NGUOI_MOI.md](../docs/guides/HUONG_DAN_NGUOI_MOI.md)
- **Library Manager**: [../docs/features/LIBRARY_MANAGER.md](../docs/features/LIBRARY_MANAGER.md)

---

Last Updated: October 23, 2025
