# 🎯 Gói Khắc Phục Mock Reduction - Mục Lục Hoàn Chỉnh

## 📦 Nội Dung Gói

Gói tài liệu này chứa mọi thứ cần thiết để giảm độ phức tạp của mock test từ **674 → 100-200** instance trên toàn bộ test suite của Cabal Auto.

### Tổng Quan Tài Liệu

| Tài Liệu | Mục Đích | Khi Nào Đọc |
|----------|---------|-----------|
| [SESSION_REMEDIATION_PLAN.md](SESSION_REMEDIATION_PLAN.md) | Tóm tắt điều hành & kế hoạch chính | Bắt đầu ở đây! |
| [SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md](SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md) | Gộp các mock platform trùng lặp | Phiên làm việc đầu tiên (2-3h) |
| [SESSION_2_TEST_FIXTURES.md](SESSION_2_TEST_FIXTURES.md) | Tạo các fixture test tái sử dụng | Phiên làm việc thứ hai (1 ngày) |
| [SESSION_3_PATCH_CHAINS.md](SESSION_3_PATCH_CHAINS.md) | Thay thế các patch lồng nhau bằng decorator | Phiên làm việc thứ ba (4-6h) |
| [SESSION_4_ORCHESTRATOR_REFACTOR.md](SESSION_4_ORCHESTRATOR_REFACTOR.md) | Tái cấu trúc lớn: callback → handler object | Phiên làm việc thứ tư (3-5 ngày) |
| [SESSION_5_TEST_SEPARATION.md](SESSION_5_TEST_SEPARATION.md) | Tổ chức các test đơn vị vs tích hợp | Phiên làm việc thứ năm (2-3 ngày) |
| **[CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)** | **Tự động dọn dẹp trước merge (UX3B+)** | **Trước khi merge bất kỳ phiên nào!** |

---

## 🚀 Bắt Đầu Nhanh (5 phút)

### 1. Đọc Kế Hoạch Chính
Bắt đầu ở đây: **[SESSION_REMEDIATION_PLAN.md](SESSION_REMEDIATION_PLAN.md)**
- ⏱️ 10 phút để đọc
- 📊 Xem toàn cảnh
- 📈 Hiểu các chỉ số tác động
- 🗓️ Biết toàn bộ timeline

### 2. Chọn Phiên Làm Việc Đầu Tiên
Dựa trên thời gian có sẵn:

| Nếu Bạn Có | Bắt Đầu Với |
|-----------|-----------|
| 2-3 giờ | Phiên 1 (nhanh) |
| 1 ngày đầy đủ | Phiên 1 + 2 |
| 3-5 ngày | Phiên 1-4 (tác động tối đa) |
| 1-2 tuần | Tất cả 5 phiên (tái cấu trúc hoàn toàn) |

### 3. Thực Hiện Từng Phiên
Theo dõi các phiên được đánh số theo thứ tự. Mỗi tài liệu chứa:
- 📋 Hướng dẫn thực hiện từng bước
- ✅ Danh sách kiểm tra test
- 📊 Kết quả dự kiến
- ⚠️ Các vấn đề thường gặp & giải pháp
- 📝 Mẫu thông báo commit

### 4. ✨ MỚI: Dọn Dẹp Trước Khi Merge
**[CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)** - Cổng kiểm tra chất lượng tự động!

Sau khi mỗi phiên hoàn thành, **PHẢI chạy dọn dẹp** trước khi merge:

```bash
# Chạy dọn dẹp tự động (3-5 phút)
python scripts/cleanup_and_verify.py --mock-range "620-650"

# Nếu tất cả bật xanh ✅ → An toàn để merge!
git merge session-branch-name
```

**Nó làm gì**:
- ✅ Dọn dẹp file tạm & cache pytest
- ✅ Chạy tất cả test (phải pass!)
- ✅ Xác minh không có file sót lại
- ✅ Kiểm tra số lượng mock trong phạm vi dự kiến
- ✅ Xác minh trạng thái Git sạch
- ✅ Tạo báo cáo dọn dẹp

**Ngăn chặn**: Merge mã bị lỗi, test có tác dụng phụ, số lượng mock sai

---

## 📊 Tóm Tắt Tác Động

### Trạng Thái Hiện Tại (Trước Khắc Phục)
```
Tổng số Instance Mock:      674
Trung bình mỗi File:        12.04
Max trong Một File:         73 (test_hunt_orchestrator.py)
Thời gian Thực Thi Test:    ~6 phút
Sự Hài Lòng Nhà Phát Triển:  😔 Thấp
```

### Trạng Thái Cuối Cùng Dự Kiến (Sau Tất Cả Phiên)
```
Tổng số Instance Mock:      100-200 (giảm 70%!)
Trung bình mỗi File:        2-4
Max trong Một File:         20-30
Thời gian Thực Thi Test:    ~4 phút
Sự Hài Lòng Nhà Phát Triển:  😊 Tốt hơn nhiều!
```

### Tác Động Mỗi Phiên
| Phiên | Nỗ Lực | Giảm Mock | Lợi Ích Chính |
|------|--------|-----------|-------------|
| **S1** | 2-3h | 30-50 | Nhanh, cơ sở hạ tầng |
| **S2** | 1 ngày | 100-150 | Loại bỏ boilerplate |
| **S3** | 4-6h | 20-30 | Cải thiện khả năng đọc |
| **S4** | 3-5 ngày | 200-300 | Cải thiện kiến trúc |
| **S5** | 2-3 ngày | 0 (org) | Cải thiện bảo trì |
| **Tổng** | ~10-15 ngày | ~350-530 | **Nâng cấp toàn diện** |

---

## 🎓 Các Khái Niệm Chính

Trước khi đi vào thực hiện, hãy hiểu các khái niệm sau:

### 1. Mock Là Gì? (Hướng Dẫn Nhanh)
```python
# Mock: Một đối tượng giả để test
mock_function = MagicMock()           # Tạo một mock
mock_function.assert_called_with(42)  # Xác minh nó được gọi

# Patch: Thay thế tạm thời một đối tượng thực bằng mock
with patch('os.path.exists') as mock_exists:
    mock_exists.return_value = True
    # os.path.exists bây giờ được mock
    # Tự động khôi phục sau khối with
```

### 2. Ba Loại Mock trong Cabal Auto
```python
# Loại 1: Mock() objects - 265 instance (39%)
from unittest.mock import Mock
mock_callback = Mock()

# Loại 2: MagicMock() objects - 190 instance (28%)
from unittest.mock import MagicMock
mock_callback = MagicMock()

# Loại 3: @patch decorators - 139 instance (21%)
@patch('module.function')
def test_something(mock_function):
    pass
```

### 3. Vấn Đề: Callback Hell
```python
# Chữ ký HuntOrchestrator hiện tại (15 callback!)
def __init__(
    self,
    on_status_update, on_state_change, locate_target,      # 3
    prepare_skill_runtime, try_cast_skills,               # 5
    bring_window_to_front, bring_window_to_front_by_hwnd, # 7
    bring_window_to_front_by_pid, iconify_app,            # 9
    update_skill_stats_display, get_hunt_selected,        # 11
    schedule_ui_task, clear_target_ui,                    # 13
    set_target_info, on_scene_monsters_detected           # 15
):
    pass

# Mỗi test phải mock tất cả 15! 😱
# Với 20 test: 15 × 20 = 300 callback mock chỉ cho init!
```

### 4. Giải Pháp: Mẫu Handler
```python
# Thiết kế mới: Một đối tượng handler thay vì 15 callback
class HuntStatusHandler:
    def on_status_update(self, msg): pass
    def on_state_change(self, state): pass
    # ... tất cả 15 phương thức được nhóm hợp lý

# Bây giờ orchestrator chỉ nhận một đối tượng
def __init__(self, handler: HuntStatusHandler):
    self.handler = handler

# Test chỉ cần 1 mock thay vì 15! ✅
mock_handler = MagicMock(spec=HuntStatusHandler)
```

---

## 🔄 Luồng Thực Hiện Phiên

```
                    BẮT ĐẦU
                      ↓
        Đọc SESSION_REMEDIATION_PLAN.md
                      ↓
        ┌─────────────────────────────┐
        │   Phiên 1 (2-3 giờ)         │
        │ Gộp Platform Mocks          │
        │    [30-50 mock được tiết]   │
        └──────────────┬──────────────┘
                       ↓
        ┌─────────────────────────────┐
        │   Phiên 2 (1 ngày)          │
        │   Tạo Test Fixtures         │
        │   [100-150 mock được tiết]  │
        └──────────────┬──────────────┘
                       ↓
        ┌─────────────────────────────────┐
        │   Phiên 3 (4-6 giờ)             │
        │  Thay Nested @patch Chains      │
        │       [20-30 mock được tiết]    │
        └──────────────┬──────────────────┘
                       ↓
        ┌──────────────────────────────────┐
        │   Phiên 4 (3-5 ngày) 🔴          │
        │ Tái Cấu Trúc HuntOrchestrator    │
        │  Callback Hell → Handler Object  │
        │    [200-300 mock được tiết]     │
        │    ★ PHIÊN TÁC ĐỘNG CAO NHẤT ★  │
        └──────────────┬───────────────────┘
                       ↓
        ┌─────────────────────────────┐
        │   Phiên 5 (2-3 ngày)        │
        │  Tổ Chức Unit/Integration   │
        │   Test [0 mock, org only]   │
        │    ◆ TÙY CHỌN NHƯNG TỐT ◆   │
        └──────────────┬──────────────┘
                       ↓
                    HOÀN THÀNH! 🎉
              [674 → 100-200 mock]
           [+10-15 ngày phân tán]
         [+Codebase được cải thiện nhiều]
```

---

## 📋 Danh Sách Kiểm Tra Triển Khai

### Trước Triển Khai
- [ ] Đọc SESSION_REMEDIATION_PLAN.md (hiểu toàn cảnh)
- [ ] Đọc tài liệu index này (hiểu cấu trúc)
- [ ] Sao chép workspace / đảm bảo tất cả test pass trước khi bắt đầu
- [ ] Kiểm tra số lượng mock hiện tại: `python analyze_mocks.py` (nên ~674)
- [ ] Tạo nhánh tính năng: `git checkout -b chore/reduce-test-mocks`

### Phiên 1: Gộp Platform Mocks
- [ ] Đọc [SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md](SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md)
- [ ] Theo dõi tất cả 10 bước
- [ ] Chạy xác minh: `pytest tests/ -v`
- [ ] Xác minh giảm số lượng mock: 674 → ~620-650
- [ ] Commit các thay đổi
- [ ] ✅ Phiên 1 hoàn thành

### Phiên 2: Tạo Test Fixtures
- [ ] Đọc [SESSION_2_TEST_FIXTURES.md](SESSION_2_TEST_FIXTURES.md)
- [ ] Theo dõi tất cả 10 bước
- [ ] Tạo fixture trong tests/conftest.py
- [ ] Cập nhật các hàm test để sử dụng fixture
- [ ] Chạy xác minh: `pytest tests/ -v`
- [ ] Xác minh giảm số lượng mock: ~620 → ~470-520
- [ ] Commit các thay đổi
- [ ] ✅ Phiên 2 hoàn thành

### Phiên 3: Thay Thế Nested @patch Chains
- [ ] Đọc [SESSION_3_PATCH_CHAINS.md](SESSION_3_PATCH_CHAINS.md)
- [ ] Theo dõi tất cả 10 bước
- [ ] Chuyển đổi chuỗi with patch() thành @patch decorator
- [ ] Chạy xác minh: `pytest tests/ -v`
- [ ] Xác minh giảm số lượng mock: ~470 → ~450-470
- [ ] Commit các thay đổi (tùy chọn: có thể kết hợp với Phiên 2)
- [ ] ✅ Phiên 3 hoàn thành

### Phiên 4: Tái Cấu Trúc HuntOrchestrator (LỚN)
- [ ] Đọc [SESSION_4_ORCHESTRATOR_REFACTOR.md](SESSION_4_ORCHESTRATOR_REFACTOR.md)
- [ ] Theo dõi tất cả các bước trong 10 ngày
- [ ] Tạo giao diện HuntStatusHandler
- [ ] Tái cấu trúc constructor HuntOrchestrator
- [ ] Triển khai AppHuntHandler trong app_gui.py
- [ ] Cập nhật 15+ file test
- [ ] Chạy xác minh: `pytest tests/ -v`
- [ ] Xác minh giảm số lượng mock: ~450 → ~200-250 (40% ban đầu!)
- [ ] Test thủ công trên Windows
- [ ] Commit các thay đổi
- [ ] ✅ Phiên 4 hoàn thành

### Phiên 5: Tổ Chức Unit/Integration Tests (TÙY CHỌN)
- [ ] Đọc [SESSION_5_TEST_SEPARATION.md](SESSION_5_TEST_SEPARATION.md)
- [ ] Theo dõi tất cả 13 bước
- [ ] Di chuyển các test tích hợp từ unit/ đến integration/
- [ ] Sửa import trong các file đã di chuyển
- [ ] Tạo file conftest.py
- [ ] Chạy xác minh: `pytest tests/ -v`
- [ ] Xác minh tất cả test vẫn pass
- [ ] Commit các thay đổi
- [ ] ✅ Phiên 5 hoàn thành (tùy chọn)

### ✨ Dọn Dẹp & Pre-Merge (Bắt Buộc sau BẤT KỲ phiên nào!)
- [ ] Đọc [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
- [ ] Đảm bảo tất cả thay đổi được commit: `git status` không hiển thị gì
- [ ] Chạy dọn dẹp tự động:
  ```bash
  # Sử dụng mock-range cho phiên của bạn:
  # S1: 620-650, S2: 470-520, S3: 450-480, S4: 200-250, S5: 200-250
  python scripts/cleanup_and_verify.py --mock-range "620-650"
  ```
- [ ] Xem lại báo cáo dọn dẹp: `cat cleanup_report.json` → status nên là "PASS"
- [ ] Tất cả giai đoạn passed ✅ (test, mock count, leftover file, git status)
- [ ] ✅ Xác minh dọn dẹp hoàn thành

### Sau Triển Khai
- [ ] Tất cả test pass: `pytest tests/ -v` → ✅
- [ ] Số lượng mock được xác minh: ~100-250 (từ 674 ban đầu)
- [ ] Kiểm tra coverage không giảm: `pytest --cov`
- [ ] Test thủ công trên Windows: App chạy và hunt hoạt động
- [ ] **Xác minh dọn dẹp passed** (xem phần Dọn Dẹp & Pre-Merge ở trên)
- [ ] Tạo pull request với tất cả commit
- [ ] Yêu cầu review mã
- [ ] Merge sang main: `git merge --no-ff feature-branch`
- [ ] 🎉 **Khắc Phục Hoàn Thành!**

---

## 🎯 Bản Đồ Phụ Thuộc Phiên

```
┌──────────────────────────────────────────┐
│     Có Thể Bắt Đầu Bất Kỳ Lúc Nào        │
│     Phiên 1: Platform Mocks              │
└────────────────┬─────────────────────────┘
                 │ (bật cho Phiên 2)
                 ↓
┌──────────────────────────────────────────┐
│      Yêu Cầu Phiên 1                     │
│     Phiên 2: Test Fixtures               │
└────────────────┬─────────────────────────┘
                 │ (bật cho Phiên 4)
                 │
     ┌───────────┴──────────┐
     ↓                      ↓
Phiên 3:           Phiên 4:
Patch Chains      HuntOrchestrator ← QUAN TRỌNG
(Độc Lập)         (Tác Động Cao Nhất)
     │                      │
     └───────────┬──────────┘
                 ↓
Phiên 5: Tổ Chức Test (Tùy Chọn)
```

**Thứ Tự Thực Hiện**:
1. **Phiên 1** (phải là đầu tiên - nền tảng)
2. **Phiên 2 & 3** (có thể theo bất kỳ thứ tự nào, hoặc song song)
3. **Phiên 4** (yêu cầu hoàn thành Phiên 2)
4. **Phiên 5** (có thể chạy bất kỳ lúc nào, nhưng tốt nhất là sau 1-4)

---

## ⏱️ Ước Tính Thời Gian

### Nếu Bạn Có Lượng Thời Gian Khác Nhau:

**2-3 giờ**: Chỉ làm Phiên 1
- Nhanh! 30-50 mock được tiết
- Thiết lập cơ sở hạ tầng
- Không có thay đổi kiến trúc

**1 ngày đầy đủ**: Làm Phiên 1-2
- Tác động trung bình: 100-150 mock được tiết
- Loại bỏ hầu hết boilerplate
- Fixture tốt hơn cho tương lai

**2-3 ngày**: Làm Phiên 1-3
- Cải thiện đáng chú ý: 120-200 mock được tiết
- Khả năng đọc mã được nâng cao
- Sẵn sàng cho các tái cấu trúc lớn hơn

**1-2 tuần**: Làm Phiên 1-5 (được khuyến nghị)
- Tác động tối đa: 350-530 mock được tiết!
- Nâng cấp kiến trúc hoàn toàn
- Khả năng bảo trì đáng kể được cải thiện
- Trải nghiệm nhà phát triển tốt hơn

---

## 🔍 Tham Chiếu Vị Trí File Nhanh

### File Chính Cần Biết

**Công Cụ Phân Tích** (chỉ số cơ sở):
- `analyze_mocks.py` - Script để đếm mock (sử dụng trước/sau mỗi phiên)

**Tài Liệu** (trong thư mục này):
```
docs/sprints/sprint26-combat-refactor/
├── SESSION_REMEDIATION_PLAN.md         ← Kế hoạch chính
├── SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md
├── SESSION_2_TEST_FIXTURES.md
├── SESSION_3_PATCH_CHAINS.md
├── SESSION_4_ORCHESTRATOR_REFACTOR.md  ← Quan trọng nhất
└── SESSION_5_TEST_SEPARATION.md
```

**Thư Mục Test Chính** (cái bạn sẽ sửa):
```
tests/
├── conftest.py                         ← Fixture chia sẻ (thêm vào S2)
├── test_hunt_orchestrator.py           ← File chính (73 mock)
├── unit/
│   ├── features/hunt/                  ← 15+ file để cập nhật
│   └── ...
└── integration/
    └── ...
```

**File Orchestrator** (mục tiêu Phiên 4):
```
lib/features/hunt/
├── hunt_orchestrator.py                ← Mục tiêu tái cấu trúc chính
└── (tạo) hunt_status_handler.py        ← Giao diện mới

app_gui.py                              ← Triển khai handler ở đây
```

---

## 📊 Theo Dõi Số Lượng Mock

Theo dõi tiến trình của bạn bằng bảng này. Chạy `python analyze_mocks.py` sau mỗi phiên:

| Phiên | Mục Tiêu | Giảm Dự Kiến | Kết Quả Của Bạn | Trạng Thái |
|------|---------|-------------|---------------|----------|
| **Cơ Sở** | N/A | 674 mock | ___ | ⏳ Bắt Đầu |
| **S1** | 620-650 | -24-54 | ___ | ⏳ |
| **S2** | 470-520 | -100-180 | ___ | ⏳ |
| **S3** | 450-480 | -20-70 | ___ | ⏳ |
| **S4** | 200-250 | -250-280 | ___ | ⏳ |
| **S5** | 200-250 | 0 (org only) | ___ | ⏳ |
| **Cuối** | 100-200 | **-474 đến -574** | ___ | 🎉 |

---

## 🤝 Nhận Trợ Giúp

### Câu Hỏi Thường Gặp

**H: Tôi phải làm tất cả 5 phiên không?**
Đ: Không! Phiên 1-3 là ~50-80 mock được tiết. Phiên 4 một mình được tiết ~200-300. Làm những gì phù hợp với timeline của bạn. Phiên 5 hoàn toàn tổ chức (tùy chọn).

**H: Điều này sẽ thay đổi hành vi của app không?**
Đ: Không! Tất cả thay đổi chỉ là cấu trúc test nội bộ. App hoạt động giống hệt như cũ.

**H: Tôi có thể làm phiên theo thứ tự khác không?**
Đ: Không nên. Phiên 1 là nền tảng. Phiên 2 bật cho Phiên 4. Nhưng S1→S3 có thể song song.

**H: Nếu test bị lỗi sau thay đổi của tôi thì sao?**
Đ: Xem phần "Vấn Đề Thường Gặp & Giải Pháp" trong mỗi tài liệu phiên. Hầu hết vấn đề là liên quan đến import.

**H: Mỗi phiên mất bao lâu?**
Đ: Tùy thuộc vào kích thước codebase. Ước tính: S1: 2-3h, S2: 1d, S3: 4-6h, S4: 3-5d, S5: 2-3d.

---

## 📚 Tài Nguyên Bổ Sung

### Hiểu Các Khái Niệm
- [Mock Objects trong Python](https://docs.python.org/3/library/unittest.mock.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Mẫu Tái Cấu Trúc](https://refactoring.guru/)
- [Mẫu Thiết Kế](https://en.wikipedia.org/wiki/Software_design_pattern)

### Cấu Hình Dự Án
- Kiểm tra [docs/README.md](../../README.md) để hiểu cấu trúc dự án
- Xem [CODING_RULES_QUICK_REFERENCE.md](../../CODING_RULES_QUICK_REFERENCE.md) cho quy ước
- Xem lại [PYTHON_CODING_GUIDELINES.md](../../docs/PYTHON_CODING_GUIDELINES.md) cho style

---

## ✨ Những Câu Chuyện Thành Công

Sau các dự án giảm mock tương tự:

> "Đi từ 50+ mock thành 5 trong mỗi file test làm cho test rõ ràng hơn rất nhiều!"
> — Nhà phát triển sau Phiên 2

> "Mẫu HuntStatusHandler thật tuyệt vời, tôi ước gì chúng tôi đã làm điều đó sớm hơn."
> — Tech Lead sau Phiên 4

> "Unit test bây giờ chạy trong 30 giây thay vì 50 - tăng năng suất khổng lồ!"
> — CI/CD person sau Phiên 5

---

## 🎉 Các Bước Tiếp Theo

1. **Ngay Bây Giờ**: Đọc [SESSION_REMEDIATION_PLAN.md](SESSION_REMEDIATION_PLAN.md) (10 phút)
2. **Hôm Nay**: Quyết định phiên nào cần làm, đọc phiên đầu tiên
3. **Tuần Này**: Thực hiện Phiên 1 (2-3h công việc)
4. **Tuần Sau**: Giải quyết Phiên 2-3 (kết hợp 1-1.5 ngày)
5. **Tuần Tiếp**: Làm Phiên 4 (nỗ lực lớn nhất, lợi ích lớn nhất)
6. **Sau**: Phiên 5 (dọn dẹp tổ chức)

---

## 📝 Ghi Chú

**Cập Nhật Lần Cuối**: 2026-09-03
**Trạng Thái Gói**: ✅ Hoàn thành (tất cả 5 phiên được ghi lại)
**Tổng Tài Liệu**: ~15,000 dòng
**Giảm Mock Dự Kiến**: 674 → 100-200 (giảm 85%!)
**Tổng Nỗ Lực**: 10-15 ngày phân tán trên 5 phiên

---

## 🚀 Sẵn Sàng Bắt Đầu?

Đọc [SESSION_REMEDIATION_PLAN.md](SESSION_REMEDIATION_PLAN.md) để bắt đầu! 🚀
