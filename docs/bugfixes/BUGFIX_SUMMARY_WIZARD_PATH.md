# ✅ Đã Sửa: Lỗi Đường Dẫn File Monsters & Skills trong Setup Wizard

## 🐛 Vấn Đề

Setup Wizard không load được danh sách quái và kỹ năng vì đường dẫn file sai.

## 🔍 Nguyên Nhân

Code đang tìm file ở:
- ❌ `data/monsters.json`
- ❌ `data/skills.json`

Nhưng file thực tế nằm ở:
- ✅ `lib/data/monsters.json`
- ✅ `lib/data/skills.json`

## ✅ Giải Pháp

Đã sửa 3 vị trí trong `ui/setup_wizard.py`:

1. **Step 3** (Line 635) - Load monsters
2. **Step 4** (Line 723) - Load skills
3. **_open_rotation_builder()** (Line 1094-1095) - Load cho Library Manager

Thay đổi:
```python
# Cũ:
'data', 'monsters.json'
'data', 'skills.json'

# Mới:
'lib', 'data', 'monsters.json'
'lib', 'data', 'skills.json'
```

## 🧪 Đã Test

```bash
# Test đường dẫn
python -c "..."  # ✅ Files exist

# Test wizard
python tests\demo_wizard_user_level.py  # ✅ Hoạt động bình thường
```

## 📊 Kết Quả

**Trước khi sửa:**
- Step 3: Không có quái nào
- Step 4: Không có skill nào
- Có lỗi hiển thị

**Sau khi sửa:**
- Step 3: Hiển thị đầy đủ quái ✅
- Step 4: Hiển thị đầy đủ skills ✅
- Không có lỗi ✅

## 📁 File Đã Sửa

- `ui/setup_wizard.py` - 3 dòng thay đổi

---

**Status:** ✅ ĐÃ SỬA & TEST XONG  
**Date:** October 21, 2025
