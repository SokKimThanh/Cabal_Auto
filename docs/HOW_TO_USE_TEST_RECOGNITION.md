# 🎯 Hướng dẫn sử dụng Test Recognition (Kiểm tra nhận diện)

## 📖 Test Recognition là gì?

**Test Recognition** là chức năng kiểm tra xem một template image (ảnh mẫu) có thể được nhận diện trên màn hình hiện tại hay không.

**Mục đích**:
- ✅ Kiểm tra template image có hoạt động tốt không trước khi hunt
- ✅ Tìm ngưỡng threshold tối ưu cho từng template
- ✅ Kiểm tra region (vùng tìm kiếm) có đúng không
- ✅ Debug khi hunt không tìm thấy target

## 🚀 Cách sử dụng (Step by Step)

### Bước 1: Mở Monster Manager
```
1. Chạy app_gui.py
2. Click nút "Quản lý quái" hoặc "Monster Manager"
3. Chọn quái từ danh sách (hoặc tạo mới)
```

### Bước 2: Vào Template Panel
```
1. Trong form quái, scroll xuống phần "Templates"
2. Click nút "Add Template" hoặc chọn template có sẵn từ danh sách
3. Đảm bảo đã chọn/browse ảnh template
```

### Bước 3: Setup Parameters
```
Template Image: [Browse...] → Chọn ảnh mẫu
Threshold: 0.85  (0.0-1.0, khuyến nghị 0.80-0.90)
Region Strategy: Window / Custom
Region: [Optional] left, top, width, height
```

### Bước 4: Chuẩn bị màn hình
```
⚠️ QUAN TRỌNG:
1. Minimize hoặc move GUI window sang bên
2. Mở game Cabal
3. Đảm bảo target (quái) HIỆN TRÊN MÀN HÌNH
4. Camera angle giống với lúc chụp template
```

### Bước 5: Test Recognition
```
1. Click nút "Test Recognition" / "Kiểm tra nhận diện"
2. GUI window sẽ tự động minimize (thu nhỏ)
3. Đợi 0.5 giây...
4. Hệ thống chụp màn hình và tìm template
5. GUI window restore (hiện lại)
6. Xem kết quả!
```

## ✅ Kết quả tìm thấy (Success)

### Dialog hiển thị
```
✅ Match found at (640, 360) - Confidence: 0.92

Box: (620, 340, 40, 40)
Center: (640, 360)
Threshold: 0.85
Region: None

[Thumbnail 200x200 của vùng khớp]

[Close]
```

### Giải thích
- **Match found**: Tìm thấy template trên màn hình ✅
- **(640, 360)**: Tọa độ center (giữa) của template
- **Confidence: 0.92**: Độ khớp thực tế (0.92 = 92% match)
- **Box**: (left, top, width, height) - vị trí và kích thước
- **Threshold: 0.85**: Ngưỡng yêu cầu (minimum)
- **Region**: Vùng tìm kiếm (None = full screen)
- **Thumbnail**: Preview ảnh vùng khớp để confirm

### Ý nghĩa
- Confidence >= Threshold → ✅ MATCH
- Trong ví dụ: 0.92 >= 0.85 → ✅ Tìm thấy
- Template này OK để dùng cho hunt!

## ❌ Kết quả không tìm thấy (Not Found)

### Dialog hiển thị
```
ℹ️ No match found (threshold: 0.85)

Try:
• Lower threshold (0.80-0.85)
• Adjust region to include target
• Ensure target is visible on screen

[OK]
```

### Troubleshooting

#### 1. Lower Threshold (Giảm ngưỡng)
```
Thử nghiệm:
- Threshold 0.95 → NOT FOUND (quá cao)
- Threshold 0.90 → NOT FOUND (vẫn cao)
- Threshold 0.85 → FOUND ✅ (vừa đủ)
- Threshold 0.80 → FOUND ✅ (an toàn hơn)

Khuyến nghị: Dùng 0.80-0.85 cho most templates
```

**Cách làm**:
1. Giảm threshold từ 0.85 → 0.80
2. Click "Test Recognition" lại
3. Nếu vẫn không thấy → Continue step 2

#### 2. Adjust Region (Điều chỉnh vùng)
```
Có thể target nằm ngoài region đã chọn!

Test:
1. Region: (0, 0, 800, 600) → NOT FOUND
2. Region: None (full screen) → FOUND ✅

→ Target nằm ngoài vùng (0, 0, 800, 600)
```

**Cách làm**:
1. Set Region Strategy = "Window" (search toàn bộ)
2. Hoặc expand region dimensions
3. Test lại

#### 3. Ensure Target Visible (Đảm bảo target hiện)
```
Checklist:
❌ Game window bị che bởi GUI
❌ Target không xuất hiện trên màn hình
❌ Camera angle khác với lúc capture template
❌ Target đang ở xa (quá nhỏ so với template)
❌ Target đang bị effects che (skill effects, fog, etc.)

✅ Game window visible và không bị che
✅ Target rõ ràng trên màn hình
✅ Camera giống lúc capture template
✅ Khoảng cách vừa phải (target size similar)
✅ No effects blocking target
```

**Cách làm**:
1. Move GUI window sang bên
2. Focus game window
3. Di chuyển character đến gần target
4. Adjust camera góc giống template
5. Clear effects nếu có
6. Test lại

#### 4. Template Quality Issue
```
Template image có thể bị:
- Quá nhỏ (< 20x20 pixels)
- Quá mờ (blurry)
- Có background nhiễu
- Không representative (không đại diện)

Solution: Capture template mới!
```

**Cách làm**:
1. Click "Capture screenshot" trong template panel
2. Chọn vùng rõ ràng, đủ lớn (>30x30)
3. Crop chặt quanh target (minimize background)
4. Save và test lại

## 🎓 Best Practices

### 1. Template Capture Tips
```
✅ GOOD template:
- Kích thước: 30x30 đến 100x100 pixels
- Crop chặt quanh target (ít background)
- Rõ nét, không blur
- Đặc trưng dễ nhận (unique features)
- Camera angle phổ biến

❌ BAD template:
- Quá nhỏ (<20x20) hoặc quá lớn (>200x200)
- Nhiều background xung quanh target
- Bị blur, pixel artifacts
- Generic (giống nhiều thứ khác)
- Camera angle hiếm
```

### 2. Threshold Selection
```
Recommendation by use case:

- **Boss monsters** (unique appearance): 0.85-0.90
  → High threshold OK vì boss có đặc trưng riêng

- **Common monsters** (similar looks): 0.75-0.80
  → Lower threshold vì nhiều quái giống nhau

- **UI elements** (exact match): 0.90-0.95
  → Very high threshold cho exact pixel matching

- **Dynamic targets** (moving, changing): 0.70-0.80
  → Lower threshold vì target có thể thay đổi appearance
```

### 3. Region Strategy
```
**Full Screen** (Region = None):
✅ Use when: Target có thể ở bất kỳ đâu
❌ Slower: Phải scan toàn bộ màn hình

**Custom Region**:
✅ Use when: Target luôn ở vùng cố định (e.g., health bar)
✅ Faster: Chỉ scan vùng nhỏ
❌ Risk: Nếu target ra ngoài region → miss

**Window Bounds**:
✅ Use when: Search trong game window only
✅ Moderate speed
✅ Flexible: Cover toàn bộ game area
```

### 4. Testing Workflow
```
Workflow chuẩn:

1. Capture template với "Capture screenshot"
2. Set threshold = 0.85 (default)
3. Click "Test Recognition"
4. ✅ Found → Great! Giữ nguyên settings
5. ❌ Not found → Lower threshold to 0.80 và test lại
6. Still not found → Check target visibility
7. Still not found → Capture template mới với better angle
8. Repeat until success
9. Save template settings
10. Ready to hunt! 🎯
```

## 🔍 Advanced: Interpreting Confidence Values

### Confidence Range Guide
```
0.95-1.00: 🟢 EXCELLENT - Exact or near-exact match
           → Use high threshold (0.90-0.95) OK

0.85-0.94: 🟢 GOOD - Strong match, recommended range
           → Use threshold (0.80-0.85)

0.75-0.84: 🟡 ACCEPTABLE - Moderate match, may have false positives
           → Use threshold (0.70-0.75), test carefully

0.65-0.74: 🟠 WEAK - Poor match, high risk of errors
           → Recapture template recommended

0.00-0.64: 🔴 VERY WEAK - Not reliable, don't use
           → Must recapture template
```

### Example Analysis
```
Test Results:
1. Threshold 0.85 → Confidence 0.91 ✅
2. Threshold 0.80 → Confidence 0.91 ✅
3. Threshold 0.75 → Confidence 0.91 ✅

Analysis:
- Actual confidence: 0.91 (excellent match)
- Threshold 0.85 is safe (0.91 > 0.85)
- Can use lower threshold (0.80) for reliability
- No need to go below 0.75 (wasted tolerance)

Recommendation: Use threshold 0.80-0.85
```

## 🐛 Common Issues & Solutions

### Issue 1: "Lỗi kiểm tra" / "Test failed"
```
Reason: Template image path invalid or file not found

Solution:
1. Check template path is correct
2. Click "Browse" và select image again
3. Ensure file exists at specified path
4. Try absolute path instead of relative
```

### Issue 2: Dialog không hiện
```
Reason: Window restore failed hoặc behind other windows

Solution:
1. Check taskbar for result window
2. Alt+Tab to find window
3. Minimize other windows
4. Try test again
```

### Issue 3: Confidence luôn = Threshold
```
Reason: (FIXED in current version)
Old version used threshold as confidence approximation

Current version: Shows actual OpenCV confidence ✅
```

### Issue 4: Test nhanh quá, không kịp
```
Reason: Template match rất fast (~100-200ms)

This is GOOD! Means:
✅ Template found immediately
✅ Performance is excellent
✅ Hunt will be fast

Not a problem, it's a feature!
```

## 📊 Example Scenarios

### Scenario 1: New Monster Setup
```
Task: Setup template cho "Forest Goblin"

Steps:
1. Open Monster Manager → Create "Forest Goblin"
2. Add template
3. Click "Capture screenshot"
4. Select goblin head (50x50 region)
5. Set threshold 0.85
6. Go to game, stand near goblin
7. Click "Test Recognition"
8. Result: ✅ Found at (720, 400), Confidence 0.89
9. Save template
10. Done! Ready to hunt goblins 🎯
```

### Scenario 2: Template Not Working
```
Problem: Hunt không tìm thấy target

Debug:
1. Open Monster Manager
2. Select problem monster template
3. Stand near target in game
4. Click "Test Recognition"
5. Result: ❌ Not found (threshold: 0.85)
6. Lower threshold to 0.75
7. Test again → ❌ Still not found
8. Check target visibility → Target bị tree che!
9. Move camera
10. Test again → ✅ Found, Confidence 0.82
11. Adjust threshold to 0.75
12. Save and hunt again → Working! ✅
```

### Scenario 3: Optimization
```
Goal: Tối ưu template cho boss hunt

Method:
1. Test với threshold 0.90 → ✅ Found, conf 0.94
2. Test với threshold 0.92 → ✅ Found, conf 0.94
3. Test với threshold 0.93 → ✅ Found, conf 0.94
4. Test với threshold 0.94 → ✅ Found, conf 0.94
5. Test với threshold 0.95 → ❌ Not found

Analysis:
- Actual confidence: 0.94 (consistent)
- Max safe threshold: 0.94
- Recommended: 0.90 (safety margin)

Result: Use threshold 0.90 for boss
```

---

**Tóm tắt**: Test Recognition giúp bạn verify template hoạt động tốt trước khi hunt, tìm threshold tối ưu, và debug vấn đề nhận diện. Luôn test template trước khi bắt đầu hunt session! 🎯
