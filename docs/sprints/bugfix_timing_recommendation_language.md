# 🐛 Bugfix: Timing Recommendation Language Attribute Error

## ❌ Lỗi gặp phải

```
AttributeError: '_tkinter.tkapp' object has no attribute 'language'
```

**Khi nào xảy ra**: Khi nhấn nút "Calculate Timing" (Tính thời gian) trong Monster Manager

## 🔍 Nguyên nhân

Code đang sử dụng thuộc tính **SAI** `self.language` thay vì thuộc tính **ĐÚNG** `self.lang`.

### Trong class CabalAutoGUI:
```python
def __init__(self, master):
    # ✅ ĐÚNG: Thuộc tính được định nghĩa là 'lang'
    self.lang = str(self.cfg.get('ui', {}).get('language', 'vi'))
```

### Trong on_monster_calculate_timing():
```python
# ❌ SAI: Đang dùng 'self.language' (không tồn tại)
formatted = format_timing_recommendation(rec, self.language)
if self.language == 'en':
text='Calculate' if self.language == 'en' else 'Tính toán'
```

## ✅ Giải pháp

Thay tất cả `self.language` → `self.lang` trong hàm `on_monster_calculate_timing()`.

### Các chỗ đã sửa:

1. **Dòng 2436**: Format recommendation
```python
# ❌ Trước
formatted = format_timing_recommendation(rec, self.language)

# ✅ Sau
formatted = format_timing_recommendation(rec, self.lang)
```

2. **Dòng 2454**: Warning message
```python
# ❌ Trước
'Please calculate timing first.' if self.language == 'en' else 'Vui lòng tính toán trước.'

# ✅ Sau
'Please calculate timing first.' if self.lang == 'en' else 'Vui lòng tính toán trước.'
```

3. **Dòng 2476**: Success message
```python
# ❌ Trước
f'Config saved to hunt_config.json' if self.language == 'en' else ...

# ✅ Sau
f'Config saved to hunt_config.json' if self.lang == 'en' else ...
```

4. **Dòng 2501-2505**: Button labels
```python
# ❌ Trước
tk.Button(btn_frame, text='Calculate' if self.language == 'en' else 'Tính toán', ...)
tk.Button(btn_frame, text='Apply to Hunt Config' if self.language == 'en' else 'Áp dụng vào Hunt', ...)
tk.Button(btn_frame, text='Close' if self.language == 'en' else 'Đóng', ...)

# ✅ Sau
tk.Button(btn_frame, text='Calculate' if self.lang == 'en' else 'Tính toán', ...)
tk.Button(btn_frame, text='Apply to Hunt Config' if self.lang == 'en' else 'Áp dụng vào Hunt', ...)
tk.Button(btn_frame, text='Close' if self.lang == 'en' else 'Đóng', ...)
```

## 🧪 Test lại

### Bước 1: Mở Monster Manager
```python
python app_gui.py
# Chọn tab "Monster Manager"
```

### Bước 2: Nhập thông tin monster
```
Name: Test Monster
HP: 10000
Damage per hit: 500
```

### Bước 3: Nhấn "Calculate Timing"
```
✅ Kết quả: Dialog hiển thị đúng
✅ Không còn lỗi AttributeError
✅ Text hiển thị đúng ngôn ngữ (EN/VI)
```

### Bước 4: Test với cả 2 ngôn ngữ
```python
# Test tiếng Việt
self.lang = 'vi'
# Nhấn Calculate → Text: "Tính toán", "Áp dụng vào Hunt", "Đóng"

# Test tiếng Anh
self.lang = 'en'
# Nhấn Calculate → Text: "Calculate", "Apply to Hunt Config", "Close"
```

## 📊 Tổng kết

### Changes Made
- ✅ 4 vị trí được sửa trong `on_monster_calculate_timing()`
- ✅ Tất cả `self.language` → `self.lang`
- ✅ Không còn syntax errors

### Impact
- 🎯 **User Impact**: HIGH - Chức năng Calculate Timing không thể dùng được
- 🔧 **Fix Difficulty**: EASY - Chỉ cần đổi tên thuộc tính
- ⚡ **Fix Speed**: IMMEDIATE - 4 replace operations

### Validation
- ✅ `get_errors()`: No errors found
- ✅ `grep_search`: Không còn `self.language` nào
- ✅ Chỉ còn `self.lang` (đúng)

## 🎓 Lesson Learned

### Nguyên nhân gốc rễ:
- Thuộc tính `self.lang` được định nghĩa trong `__init__()`
- Nhưng code trong `on_monster_calculate_timing()` dùng sai tên `self.language`
- Lỗi này xảy ra vì copy-paste hoặc nhầm lẫn tên biến

### Cách phòng tránh:
1. **Consistency**: Luôn dùng tên biến nhất quán trong toàn bộ class
2. **IDE autocomplete**: Sử dụng IDE để tự động gợi ý thuộc tính
3. **Type hints**: Thêm type hints để IDE catch lỗi sớm hơn
4. **Testing**: Test chức năng mới ngay sau khi implement

### Best practice:
```python
class CabalAutoGUI:
    def __init__(self, master):
        # ✅ GOOD: Đặt tên rõ ràng, ngắn gọn
        self.lang = str(self.cfg.get('ui', {}).get('language', 'vi'))
        
    def some_method(self):
        # ✅ GOOD: Dùng đúng tên
        text = 'Hello' if self.lang == 'en' else 'Xin chào'
        
        # ❌ BAD: Dùng sai tên (sẽ lỗi)
        text = 'Hello' if self.language == 'en' else 'Xin chào'
```

---

**Date**: October 18, 2025  
**Status**: Fixed ✅  
**Severity**: HIGH (blocking feature)  
**Fix Time**: < 5 minutes  
**Files Modified**: 1 (app_gui.py)
