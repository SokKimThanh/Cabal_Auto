# bot_config.json - Reference Sample

**Important**: File này KHÔNG phải là config của Cabal_Auto app!

## 📚 What is this?

`bot_config.json` là file mẫu được khám phá từ một **phần mềm auto Cabal khác**.

**Purpose**:
- 📖 **Research**: Tìm hiểu cách các auto tool khác cấu trúc config
- 💡 **Learning**: Học cách làm automation từ tools khác
- 🔍 **Reference**: Tham khảo khi cần implement features tương tự

## ⚠️ NOT Used By This App

Cabal_Auto app **KHÔNG** sử dụng file này:
- ❌ Không có code nào đọc bot_config.json
- ❌ Không được quản lý bởi Setup Wizard
- ❌ Không được quản lý bởi Library Manager
- ❌ Không có trong hunt flow

## ✅ What App Actually Uses

App này sử dụng hệ thống config hoàn toàn khác:

```
lib/data/
├── hunt_config.json    ⭐ Main hunt configuration
├── monsters.json       ⭐ Monster library với templates
├── skills.json         ⭐ Skills library với auto-rotation
├── vision_region.json  ⭐ Vision system configs
└── vision_templates.json
```

## 🔄 Comparison

### bot_config.json (From other tool)
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

**Features**:
- Simple action sequences
- Manual key pressing
- Basic timing control

### Cabal_Auto (This app)

**hunt_config.json**:
```json
{
  "window_title": "Cabal",
  "target_key": "TAB",
  "attack_keys": ["1", "2", "3"],
  "lost_timeout_sec": 0.75,
  "attack_min_duration_sec": 12.0
}
```

**monsters.json**:
```json
{
  "monsters": [
    {
      "name": "Dragon",
      "hp": 10000,
      "templates": [...]
    }
  ]
}
```

**skills.json**:
```json
{
  "skills": [
    {
      "name": "Power Slash",
      "key": "1",
      "type": "attack",
      "cooldown": 1.9
    }
  ]
}
```

**Features**:
- ✅ Template matching (OpenCV)
- ✅ Monster library management
- ✅ Skills with auto-rotation
- ✅ Buff auto-refresh
- ✅ Timing calculator
- ✅ Library Manager UI
- ✅ Setup Wizard

## 🗑️ Can I Delete It?

**Yes, safely!** 

File này chỉ là tham khảo:
```powershell
# Safe to delete
Remove-Item config\bot_config.json
```

App sẽ vẫn hoạt động bình thường vì không sử dụng file này.

## 📝 Why Keep It?

Nếu bạn muốn giữ lại:
- 📚 Reference cho future features
- 💡 Learning về cách tools khác làm
- 🔍 Research automation patterns

## 🚀 Getting Started

Nếu bạn muốn configure app:

1. **First-time setup**:
   ```powershell
   python app_gui.py
   ```
   → Setup Wizard sẽ tự động tạo configs

2. **Manage configs**:
   - Window/Keys: Setup tab
   - Monsters: Library → Monsters
   - Skills: Library → Skills
   - Timing: Library → Timing Calculator

3. **Config locations**:
   - `lib/data/hunt_config.json` - Auto-generated
   - `lib/data/monsters.json` - Via Library Manager
   - `lib/data/skills.json` - Via Library Manager

## 📚 Related Docs

- **Config Guide**: [README.md](README.md)
- **Setup Wizard**: [../docs/guides/HUONG_DAN_NGUOI_MOI.md](../docs/guides/HUONG_DAN_NGUOI_MOI.md)
- **Library Manager**: [../docs/features/LIBRARY_MANAGER.md](../docs/features/LIBRARY_MANAGER.md)

---

**TL;DR**: bot_config.json là reference sample từ phần mềm khác, KHÔNG phải config của app này. Có thể xóa an toàn.
