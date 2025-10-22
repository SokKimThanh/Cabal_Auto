# 🚀 Vision Wizard - Quick Start Guide

**5 phút để bắt đầu sử dụng Vision Wizard**

---

## 📖 Giới Thiệu

Vision Wizard là công cụ quản lý nhận diện hình ảnh và tracking quái vật trong game. Module này giúp bạn:

- 🎯 Quản lý template (ảnh mẫu)
- 📊 Cấu hình ngưỡng nhận diện
- 🔍 Test nhận diện real-time
- 📍 Tracking quái vật tự động

---

## ⚡ Quick Start

### Bước 1: Mở Vision Wizard

**Cách 1: Phím tắt (Khuyến nghị)**
```
Nhấn: Ctrl + Shift + L
```

**Cách 2: Code (nếu tích hợp vào app)**
```python
from ui.setup_wizard_vision import open_vision_wizard_from_parent

# Trong code của bạn:
open_vision_wizard_from_parent(root)
```

**Cách 3: Test độc lập**
```powershell
cd e:\Cabal_Auto
python -m ui.setup_wizard_vision
```

### Bước 2: Chọn Chế Độ Tìm Kiếm

Trong Vision Wizard, chọn một trong 3 chế độ:

| Chế độ | Mô tả | Khi nào dùng |
|--------|-------|--------------|
| **Tìm tại vị trí chỉ định** | Tìm ở vị trí cố định | Khi target luôn ở một chỗ |
| **Tìm toàn màn hình** | Quét toàn bộ màn hình | Khi target di chuyển tự do |
| **Tìm trong vùng (ROI)** | Tìm trong vùng chỉ định | Khi target trong khu vực nhất định |

### Bước 3: Thêm Template

1. Click nút **"Thêm Template"**
2. Chọn file ảnh (PNG, JPG)
   - Ví dụ: `assets/images/monsters/hp_bar.png`
3. Template sẽ xuất hiện trong danh sách

### Bước 4: Cấu Hình Ngưỡng

1. Click chọn template trong danh sách
2. Nhập ngưỡng trong ô "Ngưỡng nhận diện"
   - `0.7` = 70% độ chính xác
   - `0.8` = 80% độ chính xác (khuyến nghị)
   - `0.9` = 90% độ chính xác (rất chặt)
3. Click **"Lưu Ngưỡng"**

### Bước 5: Test Nhận Diện (TODO Phase 2)

1. Click **"Test Nhận Diện"**
2. Xem kết quả trong vùng Preview
3. Điều chỉnh ngưỡng nếu cần

---

## 🎮 Workflow Thực Tế

### Scenario 1: Tracking HP Bar Quái Vật

```
1. Mở game → Tìm một con quái
2. Chụp ảnh HP bar (Snipping Tool hoặc Screenshot)
3. Lưu vào: assets/images/monsters/hp_bar.png
4. Mở Vision Wizard (Ctrl+Shift+L)
5. Thêm template → chọn hp_bar.png
6. Chọn chế độ: "Tìm toàn màn hình"
7. Đặt ngưỡng: 0.8
8. Lưu ngưỡng
9. Test nhận diện
10. Nếu OK → Start Tracking (TODO Phase 4)
```

### Scenario 2: Tracking Skill Icon

```
1. Chụp ảnh skill icon từ skill bar
2. Lưu vào: assets/images/skills/skill_1.png
3. Mở Vision Wizard
4. Thêm template
5. Chế độ: "Tìm tại vị trí chỉ định"
6. Ngưỡng: 0.85 (icon cần chính xác)
7. Lưu và test
```

---

## ⌨️ Keyboard Shortcuts

| Phím | Chức năng |
|------|-----------|
| `Ctrl+Shift+L` | Mở/Focus Vision Wizard |
| `Escape` | Đóng Vision Wizard |
| `Ctrl+S` | Lưu ngưỡng (khi đang chọn template) |
| `Ctrl+T` | Test nhận diện |
| `Delete` | Xóa template đang chọn |

---

## 🔧 Tips & Tricks

### 1. Chụp Template Tốt

✅ **DO:**
- Chụp rõ nét, độ phân giải cao
- Chụp khi game ở độ sáng bình thường
- Chụp chính xác vùng cần nhận diện
- Template nhỏ gọn (50x50 đến 200x200 px)

❌ **DON'T:**
- Chụp mờ hoặc bị nhiễu
- Chụp quá to (giảm tốc độ)
- Chụp có UI khác chồng lên
- Chụp khi game có hiệu ứng đặc biệt

### 2. Chọn Ngưỡng Phù Hợp

| Loại Template | Ngưỡng Khuyến Nghị |
|---------------|-------------------|
| HP Bar | 0.75 - 0.80 |
| Skill Icon | 0.85 - 0.90 |
| Monster Name | 0.80 - 0.85 |
| UI Element | 0.85 - 0.90 |

### 3. Tối Ưu Hiệu Suất

- Dùng ROI thay vì toàn màn hình nếu được
- Template càng nhỏ càng nhanh
- Giảm ngưỡng nếu miss target
- Tăng ngưỡng nếu false positive

---

## 🐛 Troubleshooting

### Không Mở Được Vision Wizard

**Lỗi:** "Module not found"

**Giải pháp:**
```powershell
# Check file tồn tại
ls e:\Cabal_Auto\ui\setup_wizard_vision.py

# Re-import
cd e:\Cabal_Auto
python -c "from ui.setup_wizard_vision import VisionWizard; print('OK')"
```

### Template Không Nhận Diện

**Nguyên nhân có thể:**
1. Ngưỡng quá cao → Giảm xuống 0.7
2. Template chụp không đúng → Chụp lại
3. Game có hiệu ứng làm thay đổi hình ảnh → Chụp nhiều biến thể

**Giải pháp:**
```
1. Chọn template trong list
2. Giảm ngưỡng: 0.9 → 0.8 → 0.7
3. Test lại sau mỗi thay đổi
4. Nếu vẫn không được: chụp template mới
```

### Vision Wizard Không Topmost

**Lỗi:** Bị game che

**Giải pháp:**
```python
# Click vào Vision Wizard window
# Hoặc nhấn Ctrl+Shift+L để focus lại
```

---

## 📚 Tài Liệu Bổ Sung

### Chi Tiết Kỹ Thuật
- [VISION_WIZARD_FRAMEWORK.md](VISION_WIZARD_FRAMEWORK.md)
  - Cấu trúc class đầy đủ
  - API documentation
  - Data structures

### Tích Hợp Vào Code
- [VISION_WIZARD_INTEGRATION_EXAMPLES.py](VISION_WIZARD_INTEGRATION_EXAMPLES.py)
  - 10 ví dụ tích hợp
  - Code mẫu
  - Best practices

### Tổng Quan Sprint
- [README.md](README.md)
  - Roadmap
  - Phase breakdown
  - Version history

---

## 🎯 Checklist Người Dùng Mới

- [ ] Đã mở được Vision Wizard (Ctrl+Shift+L)
- [ ] Đã thêm được template
- [ ] Đã chọn chế độ tìm kiếm
- [ ] Đã cấu hình ngưỡng
- [ ] Đã lưu cấu hình
- [ ] Đã test nhận diện (TODO Phase 2)
- [ ] Đã bắt đầu tracking (TODO Phase 4)

---

## 🆘 Cần Giúp Đỡ?

1. **Check Logs:** `logs/vision_wizard.log` (TODO)
2. **Debug Mode:** Chạy `python -m ui.setup_wizard_vision`
3. **Documentation:** `docs/sprint22/`
4. **Issues:** Create issue trong project

---

## 🚀 Next Steps

Sau khi đã quen với Vision Wizard:

1. **Phase 2:** Chờ tính năng OpenCV integration
2. **Phase 3:** ROI selection
3. **Phase 4:** Monster tracking
4. **Phase 5:** Overlay system

---

**💡 Tip:** Bookmark guide này để tham khảo nhanh!

**📅 Last Updated:** 2025-10-22  
**Version:** 0.1.0 (Phase 1)

