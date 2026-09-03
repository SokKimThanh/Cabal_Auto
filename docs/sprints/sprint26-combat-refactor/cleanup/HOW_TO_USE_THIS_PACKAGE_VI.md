# 📖 Hướng Dẫn Sử Dụng Đúng Bộ Tài Liệu Mock Reduction

## 🎯 Mục Đích Của Bộ Tài Liệu Này

Bộ tài liệu này hướng dẫn **từng bước** cách giảm 674 mock test thành 100-200 (70% giảm) trong Cabal Auto.

**Không phải**:
- ❌ Một công cụ tự động (không có magic!)
- ❌ Hướng dẫn lý thuyết chung chung
- ❌ Tài liệu để đọc một lần rồi bỏ đi

**Mà là**:
- ✅ Hướng dẫn **thực hành chi tiết** cho từng session
- ✅ Gồm các bước cụ thể, mã ví dụ, danh sách kiểm tra
- ✅ Công cụ để **thực thi một công việc có kết quả cụ thể**

---

## 📚 Cấu Trúc Bộ Tài Liệu

```
📦 Gói Mock Reduction
│
├─ 📄 README_MOCK_REMEDIATION_INDEX.md (ĐIỂM BẮT ĐẦU)
│  └─ Tóm tắt, quick start, danh sách kiểm tra
│
├─ 📄 SESSION_REMEDIATION_PLAN.md (KẾ HOẠCH CHÍNH)
│  └─ Kế hoạch tổng thể, phân tích vấn đề, timeline
│
├─ 📄 SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md (PHIÊN 1)
│  ├─ 10 bước chi tiết để gộp mock
│  └─ Dành 2-3 giờ
│
├─ 📄 SESSION_2_TEST_FIXTURES.md (PHIÊN 2)
│  ├─ 10 bước chi tiết để tạo fixture
│  └─ Dành 1 ngày
│
├─ 📄 SESSION_3_PATCH_CHAINS.md (PHIÊN 3)
│  ├─ 10 bước để thay patch chain
│  └─ Dành 4-6 giờ
│
├─ 📄 SESSION_4_ORCHESTRATOR_REFACTOR.md (PHIÊN 4 - QUAN TRỌNG)
│  ├─ 30+ bước để refactor HuntOrchestrator
│  └─ Dành 3-5 ngày
│
├─ 📄 SESSION_5_TEST_SEPARATION.md (PHIÊN 5 - TÙY CHỌN)
│  ├─ 13 bước để tổ chức test
│  └─ Dành 2-3 ngày
│
├─ 📄 CLEANUP_AND_MERGE_PROTOCOL.md (DỌN DẸP)
│  ├─ Quy trình dọn dẹp & kiểm tra trước merge
│  └─ Chạy sau mỗi session (3-5 phút)
│
└─ 🐍 scripts/cleanup_and_verify.py (CÔNG CỤ TỰ ĐỘNG)
   └─ Script Python để chạy dọn dẹp (8 phase)
```

---

## 🚀 Workflow Đúng: Từ A Đến Z

### **Ngày 1 - Học & Kế Hoạch (2 giờ)**

#### Bước 1: Đọc Quick Start
**File**: `README_MOCK_REMEDIATION_INDEX.md` hoặc `README_MOCK_REMEDIATION_INDEX_VI.md`
**Thời gian**: 15 phút
**Nội dung**: 
- 📊 Tác động dự kiến (674 → 100-200)
- 🚀 4 bước quick start
- 📋 Danh sách kiểm tra pre-implementation

**Làm gì**: Chỉ đọc phần "Quick Start", không cần đọc chi tiết tất cả.

#### Bước 2: Đọc Kế Hoạch Chính
**File**: `SESSION_REMEDIATION_PLAN.md`
**Thời gian**: 20 phút
**Nội dung**:
- 📋 Phân tích vấn đề (callback hell)
- 🎯 5 session overview
- ⏱️ Timeline & effort estimates
- 📈 Mock count dự kiến mỗi session

**Làm gì**: Hiểu tổng thể, không cần detail từng bước.

#### Bước 3: Lên Kế Hoạch
**Làm gì**: Quyết định
- Bạn có bao nhiêu thời gian?
- Session nào bạn sẽ làm?
- Ai sẽ thực hiện?

**Quyết Định Mẫu**:
```
Tôi có 1 tuần → Sẽ làm tất cả 5 session (S1-S5)
Tôi có 3 ngày → Sẽ làm S1-S3 (nhanh, tác động tốt)
Tôi có 2 giờ → Sẽ làm S1 (quick win)
```

#### Bước 4: Chuẩn Bị Git
**Làm gì**: Tạo nhánh tính năng
```bash
cd f:\Cabal_Auto
git checkout main
git pull origin main  # Đảm bảo mới nhất
git checkout -b chore/reduce-test-mocks-<your-name>
```

**Bước 5: Check Mock Count Baseline**
**Làm gì**: Biết số hiện tại
```bash
python analyze_mocks.py
# Kết quả dự kiến: ~674 mock total
```

---

### **Ngày 2+ - Thực Hiện Phiên (Tuỳ Từng Session)**

#### Workflow Cho Mỗi Session:

**Ví dụ: Session 1 (2-3 giờ)**

```
1️⃣ ĐỌC HƯỚNG DẪN
   File: SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md
   - Đọc toàn bộ file (hiểu mục đích)
   - Ghi chú mục đích (gộp sys.modules patches)
   - Xác định test file nào sẽ thay đổi

2️⃣ THEO DÕI 10 BƯỚC
   Mỗi bước:
   - Đọc hướng dẫn chi tiết
   - Xem code ví dụ
   - Thực hiện thay đổi
   - Kiểm tra: pytest tests/ -v
   - Commit nếu pass

3️⃣ VERIFY MOCK COUNT
   Chạy: python analyze_mocks.py
   Dự kiến: 674 → 620-650 (30-50 mock được tiết)
   
4️⃣ COMMIT TOÀN BỘ
   git add .
   git commit -m "feat: session 1 consolidate platform mocks"

5️⃣ DỌN DẸP & VERIFY
   python scripts/cleanup_and_verify.py --mock-range "620-650"
   
   Xem report: cat cleanup_report.json
   Kiểm tra:
   - status: "PASS" ✅
   - mock_count: trong 620-650
   - Tất cả 8 phase pass

6️⃣ MERGE (nếu cleanup pass)
   git merge --no-ff chore/reduce-test-mocks-session-1
```

---

## 📋 Danh Sách Kiểm Tra: 5 Session Trước-Sau

### **Trước Mỗi Session**

- [ ] Tất cả test pass: `pytest tests/ -v` → ✅
- [ ] Git clean: `git status` → nothing to commit
- [ ] Mock baseline: `python analyze_mocks.py` → ghi lại số cũ
- [ ] Tạo nhánh mới hoặc sạch nhánh cũ
- [ ] Đọc SESSION_X tài liệu hoàn toàn
- [ ] Hiểu 10 bước (hoặc 13 bước cho S5)

### **Trong Quá Trình Session**

- [ ] Theo dõi từng bước theo hướng dẫn
- [ ] Chạy test sau mỗi 2-3 bước: `pytest tests/ -v`
- [ ] Nếu test fail → xem "Common Issues" trong tài liệu
- [ ] Commit sau mỗi 3-4 bước (checkpoint)
- [ ] Không bỏ qua bất kỳ bước nào

### **Sau Mỗi Session**

- [ ] Check mock count: `python analyze_mocks.py`
- [ ] Kiểm tra nằm trong phạm vi dự kiến (S1: 620-650, etc.)
- [ ] Tất cả test pass: `pytest tests/ -v` → ✅
- [ ] Commit final: `git commit -m "chore: session X complete"`
- [ ] **Chạy cleanup**: `python scripts/cleanup_and_verify.py --mock-range "XXX-YYY"`
- [ ] Review cleanup report: `cat cleanup_report.json` → "PASS"?
- [ ] Nếu PASS → Ready to merge!
- [ ] Nếu FAIL → Fix issues, rerun cleanup

---

## ⏰ Thời Gian Chi Tiết Cho Mỗi Session

| Session | Thời Gian | Mock Reduction | Bước | Độ Khó |
|---------|----------|----------------|------|---------|
| **S1** | 2-3h | 30-50 | 10 | 🟢 Dễ |
| **S2** | 1 ngày | 100-150 | 10 | 🟡 Trung Bình |
| **S3** | 4-6h | 20-30 | 10 | 🟡 Trung Bình |
| **S4** | 3-5 ngày | 200-300 | 30+ | 🔴 Khó |
| **S5** | 2-3 ngày | 0 (org) | 13 | 🟡 Trung Bình |
| **Cleanup** | 3-5 phút | N/A | 8 | 🟢 Dễ |

---

## 🔄 Cleanup Protocol - Bắt Buộc!

### **Khi Nào Chạy Cleanup?**

✅ **PHẢI chạy**:
- Sau mỗi session hoàn thành
- Trước mỗi merge sang main
- Trước commit final của session

❌ **KHÔNG cần**:
- Sau mỗi bước nhỏ (chỉ sau session)
- Nếu bạn vẫn đang làm việc (chưa commit)

### **Cách Chạy**

```bash
# Bước 1: Commit tất cả thay đổi
git add .
git commit -m "feat: session 1 complete"

# Bước 2: Chạy cleanup
python scripts/cleanup_and_verify.py --mock-range "620-650"

# Bước 3: Xem report
cat cleanup_report.json
```

### **Hiểu Cleanup Report**

```json
{
  "status": "PASS",           // ✅ PASS = OK to merge
                              // ❌ FAIL = Fix issues first
  "issues": [],               // Danh sách vấn đề (empty = tốt)
  "metrics": {
    "mock_count": 625,        // Số mock hiện tại
    "test_exit_code": 0       // Exit code (0 = pass)
  }
}
```

**Ý Nghĩa**:
- ✅ **PASS + mock_count in range (620-650)** → OK to merge!
- ❌ **FAIL or mock_count out of range** → Fix & rerun cleanup

---

## 📊 Mock Count Tracking Sheet

Dùng bảng này để theo dõi tiến độ:

```
BASELINE (trước làm gì):
python analyze_mocks.py
→ Result: _____ mock total (dự kiến ~674)

SAU SESSION 1:
python analyze_mocks.py
→ Result: _____ (dự kiến 620-650)
→ Giảm: _____ mock
→ Cleanup: PASS ✅ / FAIL ❌

SAU SESSION 2:
python analyze_mocks.py
→ Result: _____ (dự kiến 470-520)
→ Giảm: _____ mock (cumulative từ S1)
→ Cleanup: PASS ✅ / FAIL ❌

... tiếp tục cho S3, S4, S5
```

---

## 🎯 Scenario: Làm Theo Thời Gian Có Sẵn

### **Scenario 1: Tôi Có 2-3 Giờ**

```
✅ CÓ THỂ LÀM: Session 1 (Quick Win)

Thứ Tự:
1. Đọc README_MOCK_REMEDIATION_INDEX (15 min)
2. Đọc SESSION_1_CONSOLIDATE_PLATFORM_MOCKS (20 min)
3. Làm Session 1 theo 10 bước (2h)
4. Chạy cleanup (5 min)
5. Merge (5 min)

Kết Quả: 674 → 620-650 mock (30-50 tiết)
```

---

### **Scenario 2: Tôi Có 1 Ngày Đầy Đủ**

```
✅ CÓ THỂ LÀM: Session 1 + 2

Thứ Tự:
1. BUỔI SÁNG (1 giờ): Đọc README + SESSION_REMEDIATION_PLAN
2. BUỔI SÁNG (2h): Làm Session 1 (10 bước)
3. LUNCH BREAK
4. BUỔI CHIỀU (1h): Làm Session 2 (phần 1 - tạo fixture)
5. BUỔI CHIỀU (2h): Làm Session 2 (phần 2 - cập nhật test)
6. CUỐI NGÀY (15 min): Cleanup & merge S1
7. CUỐI NGÀY (15 min): Cleanup & merge S2

Kết Quả: 674 → 470-520 mock (150-200 tiết)
```

---

### **Scenario 3: Tôi Có 1-2 Tuần**

```
✅ CÓ THỂ LÀM: Tất Cả 5 Session (Hoàn Toàn)

Thứ Tự:
TUẦN 1:
  • Ngày 1 (2h): Học tài liệu, lên kế hoạch
  • Ngày 2-3 (4-6h): Session 1
  • Ngày 3-4 (1 ngày): Session 2
  • Ngày 5 (4-6h): Session 3

TUẦN 2:
  • Ngày 1-3 (3-5 ngày): Session 4 (lớn nhất!)
  • Ngày 4-5 (2-3 ngày): Session 5

Kết Quả: 674 → 100-200 mock (70% reduction!)
```

---

## ⚠️ Những Điểm Cần Lưu Ý

### **1. PHẢI Đọc Toàn Bộ Session Trước Khi Làm**

❌ SAI:
```
1. Đọc Bước 1
2. Làm Bước 1
3. Đọc Bước 2
4. Làm Bước 2
→ Dễ quên context, tốn thời gian
```

✅ ĐÚNG:
```
1. Đọc toàn bộ SESSION_X (10-20 min)
2. Hiểu mục đích, scope, kết quả dự kiến
3. Sau đó mới làm từng bước
→ Hiệu quả, ít lỗi
```

### **2. PHẢI Chạy Cleanup Sau Session**

❌ SAI:
```
1. Làm Session 1
2. Test pass → Merge luôn
→ Có thể test có bug hidden, số mock sai
```

✅ ĐÚNG:
```
1. Làm Session 1
2. Commit
3. Chạy cleanup (tự động chạy tất cả test)
4. Review report
5. Nếu PASS → Merge
6. Nếu FAIL → Fix & rerun cleanup
→ Đảm bảo chất lượng
```

### **3. PHẢI Commit Sau Mỗi Session**

❌ SAI:
```
1. Làm S1 → không commit
2. Làm S2 → không commit
3. Làm S3 → commit tất cả cùng lúc
→ Khó rollback nếu có vấn đề
```

✅ ĐÚNG:
```
1. Làm S1 → commit "feat: session 1"
2. Cleanup S1 → merge
3. Làm S2 → commit "feat: session 2"
4. Cleanup S2 → merge
→ Dễ revert nếu cần
```

### **4. Session 4 Là Lớn Nhất - Hãy Chuẩn Bị**

❌ SAI:
```
1. Làm S1, S2, S3 nhanh chóng
2. Bắt tay vào S4 khi mệt
→ Dễ make mistakes
```

✅ ĐÚNG:
```
1. Hoàn thành S1-S3 (backup good state)
2. Nghỉ ngơi, sạch đầu
3. Quyết tâm 3-5 ngày cho S4
4. Test kỹ lưỡng
→ Thành công Session 4 = 70% công việc hoàn thành!
```

---

## 🔍 Kiểm Tra Tại Mỗi Giai Đoạn

### **Sau Mỗi Bước (Trong Session)**

```bash
# Chạy test nhanh
pytest tests/ -v --tb=short

# Kiểm tra một file cụ thể được sửa
pytest tests/test_hunt_orchestrator.py -v
```

### **Sau Toàn Bộ Session (Pre-Merge)**

```bash
# 1. Check mock count
python analyze_mocks.py

# 2. Kiểm tra range dự kiến
# S1: 620-650? S2: 470-520? ... S4: 200-250?

# 3. Chạy cleanup
python scripts/cleanup_and_verify.py --mock-range "XXX-YYY"

# 4. Xem report
cat cleanup_report.json

# 5. Nếu PASS → merge
# 6. Nếu FAIL → xem lỗi & fix
```

---

## 💾 Lưu Trữ & Rollback

### **Nếu Session Bị Lỗi**

```bash
# Kiểm tra branch
git status

# Nếu chưa merge:
git reset --hard HEAD   # Quay lại trước session
git checkout main
git branch -D session-branch

# Rồi bắt đầu lại session đó
```

### **Nếu Muốn Giữ Tiến Độ**

```bash
# Backup branch trước session lớn
git branch backup-before-session-4
git checkout -b session-4-work

# Làm Session 4
# Nếu fail → quay lại backup
git checkout main
git reset --hard backup-before-session-4
```

---

## 🎓 Học Khi Làm

### **Khi Nào Để Tạm Dừng?**

✅ **DỪng để hiểu**:
- Trước làm bước mới, đọc hướng dẫn chi tiết
- Nếu không hiểu bước nào, tìm "Common Issues" trong tài liệu
- Xem code example trước khi sửa file thực tế

### **Khi Nào Để Tiếp Tục?**

✅ **Tiếp tục**:
- Test pass ✅
- Mock count tính được (analyze_mocks.py chạy OK)
- Bước hiện tại hoàn thành
- Sẵn sàng đến bước tiếp theo

---

## 📞 Troubleshooting - Nếu Bị Stuck

### **Vấn Đề: Test Fail Sau Bước X**

**Cách Sửa**:
1. Xem error message
2. Tìm file SESSION_X_* → phần "Common Issues"
3. Tìm error gần giống nhất
4. Theo hướng dẫn sửa
5. Chạy test lại

### **Vấn Đề: Mock Count Không Giảm**

**Cách Sửa**:
1. Kiểm tra: tất cả bước đã làm chưa?
2. Chạy `python analyze_mocks.py` lại
3. Nếu vẫn không giảm → xem SESSION_X phần "Expected Results"
4. Verify code changes đúng không

### **Vấn Đề: Cleanup Pass Nhưng Git Dirty**

**Cách Sửa**:
```bash
# Cleanup chỉ check file status, không tự commit
# Bạn phải commit trước cleanup

git add .
git commit -m "feat: session X complete"
python scripts/cleanup_and_verify.py --mock-range "XXX"
```

---

## ✨ Tl;dr - Ngắn Gọn

1. **Đọc**: README → SESSION_REMEDIATION_PLAN
2. **Quyết định**: Sẽ làm session nào, mất bao lâu
3. **Làm**: Từng session theo hướng dẫn (10-30 bước)
4. **Verify**: `python analyze_mocks.py` → check range
5. **Cleanup**: `python scripts/cleanup_and_verify.py --mock-range "XXX"`
6. **Merge**: Nếu cleanup PASS
7. **Repeat**: Cho session tiếp theo

---

## 📚 Quick Reference

| Cần Gì | File Nào | Bao Lâu |
|--------|---------|--------|
| Hiểu tổng quát | SESSION_REMEDIATION_PLAN.md | 20 min |
| Quick start | README_MOCK_REMEDIATION_INDEX.md | 15 min |
| Session 1 chi tiết | SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md | 2-3h |
| Session 2 chi tiết | SESSION_2_TEST_FIXTURES.md | 1 day |
| Session 3 chi tiết | SESSION_3_PATCH_CHAINS.md | 4-6h |
| Session 4 chi tiết (LỚN) | SESSION_4_ORCHESTRATOR_REFACTOR.md | 3-5d |
| Session 5 chi tiết (OPT) | SESSION_5_TEST_SEPARATION.md | 2-3d |
| Dọn dẹp & merge | CLEANUP_AND_MERGE_PROTOCOL.md | 5 min |
| Chạy cleanup | scripts/cleanup_and_verify.py | 3-5 min |

---

**Status**: ✅ Sẵn sàng thực hiện  
**Thứ tự**: Tuần tự session 1 → 5  
**Bắt buộc**: Cleanup sau mỗi session  
**Kết Quả**: 674 → 100-200 mock (70% giảm)
