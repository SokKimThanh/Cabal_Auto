# 🤖 Hướng Dẫn Thực Thi Tự Động - Sprint 26 Cleanup

## 📌 Tóm Tắt Nhanh

| Thành Phần | Mô Tả |
|-----------|-------|
| **File Prompts** | `AUTOMATED_EXECUTION_PROMPTS.md` - Chứa prompt chi tiết cho 5 session |
| **Script Runner** | `scripts/run_cleanup_sessions.py` - Công cụ hỗ trợ tổ chức execution |
| **Thời Gian** | ~2-3 tuần, tổng cộng 3-4 developer-weeks |
| **Rủi Ro** | Thấp-Trung bình (refactoring, tuy nhiên thoải mái rollback) |

---

## 🚀 Cách Sử Dụng Prompts

### Phương Pháp 1: Copy Prompt Trực Tiếp (Nhanh nhất)

1. Mở file: `AUTOMATED_EXECUTION_PROMPTS.md`
2. Chọn Session muốn chạy (ví dụ: Session 1)
3. Copy section **"Automated Execution Prompt"** 
4. Paste vào GitHub Copilot chat
5. Thêm: `"Execute this task using automated tools"` hoặc `"Run this now"`
6. Copilot sẽ thực thi tự động

```
┌─────────────────────────────────────────┐
│ GitHub Copilot Chat                     │
├─────────────────────────────────────────┤
│ [Paste SESSION_1 PROMPT HERE]           │
│                                         │
│ Execute this task using automated tools │
│                                         │
│ [Send] ✓                               │
└─────────────────────────────────────────┘
```

### Phương Pháp 2: Sử Dụng Script Runner

```bash
# Xem tóm tắt tất cả session
python scripts/run_cleanup_sessions.py --summary

# Export session plan sang JSON (để dùng với CI/CD)
python scripts/run_cleanup_sessions.py --export .github/cleanup-plan.json

# Xem hướng dẫn cho session cụ thể
python scripts/run_cleanup_sessions.py --session 1
```

### Phương Pháp 3: Theo Thứ Tự Từng Bước

Chạy theo flow này:

```
┌──────────────────┐
│   Session 1      │  Consolidate Platform Mocks
│ (2-3 hours)      │  → Xóa duplicate sys.modules patches
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│   Session 2      │  Create Test Fixtures
│ (1 full day)     │  → Tạo 4-5 shared fixtures
└────────┬─────────┘
         │
         ├──────────────┬────────────────┐
         ↓              ↓                ↓
    ┌────────┐    ┌────────┐      (Optional)
    │Session3│    │Session4│
    │(4-6 hr)│    │(3-5 d) │ ← Major refactoring
    └────────┘    └────┬───┘
                       │
                       ↓
                  ┌──────────┐
                  │ Session5 │  Split unit/integration
                  │ (2-3 d)  │  → Reorganize tests
                  └──────────┘
```

---

## 📋 Nội Dung Prompts

### Mỗi Session Prompt Bao Gồm:

```
TASK: [Mô tả task]
OBJECTIVE: [Mục tiêu cụ thể]

IMPLEMENTATION STEPS:
├── Phase/Step 1: [Mô tả]
│   ├─ Step 1.1: [Chi tiết]
│   ├─ Step 1.2: [Chi tiết]
│   └─ Verification: [Cách kiểm tra]
├── Phase/Step 2: [Mô tả]
│   └─ ...
└── Final Phase: Verification & Cleanup

EXPECTED OUTCOME:
✅ [Kết quả 1]
✅ [Kết quả 2]
✅ [...]
```

### Ví Dụ Session 1 Prompt

```
TASK: Consolidate duplicated sys.modules platform mocks into tests/conftest.py

OBJECTIVE:
- Remove platform mock duplication from 6+ test files
- Create centralized auto-use fixture in tests/conftest.py
- Expected result: 30-50 fewer mock instances

IMPLEMENTATION STEPS:

1. ANALYSIS PHASE (10 min)
   □ Search: grep -r "sys\.modules\[" tests/ --include="*.py"
   □ Create inventory of all mocked modules
   
2. CREATE FIXTURE PHASE (20 min)
   □ Add to tests/conftest.py: [fixture code here]
   
3. REMOVE DUPLICATION (30 min)
   □ 6 files to update: [list of files]
   
4. VERIFICATION (15 min)
   □ Run: pytest tests/ -v
   
5. CLEANUP (10 min)
   □ Remove unused imports
```

---

## 🎯 Chiến Lược Thực Thi

### Option A: Thực Thi Tuần Tự (Khuyến Nghị cho lần đầu)

**Ưu điểm:**
- ✅ An toàn, dễ debug
- ✅ Có thời gian kiểm chứng từng bước
- ✅ Rollback dễ nếu có vấn đề

**Lịch Trình:**
```
Week 1:
  Monday   → Session 1 (2-3 hours)
  Tuesday  → Session 2 (6-8 hours) 
  Wed-Thu  → Session 3 (4-6 hours)

Week 2:
  Mon-Wed  → Session 4 (3-5 days) ⚠️ Major refactoring
  Thu-Fri  → Session 5 (2-3 days)

Week 3:
  Testing & Integration
  Final Verification
```

### Option B: Thực Thi Song Song (Nhanh hơn, yêu cầu 2 developer)

**Sessions có thể song song:**
- Session 1 & 2 & 3 (độc lập)
- Session 4 (phụ thuộc vào 1-2)
- Session 5 (phụ thuộc vào 1-4)

**Ví Dụ:**
```
Developer 1: Session 1 & 3
Developer 2: Session 2
(Sau 3 ngày)
Developer 1: Session 4
Developer 2: Session 5 (prep)
(Sau 1 tuần)
Both: Session 5 + Verification
```

---

## ✅ Danh Sách Kiểm Tra Thực Thi

### Trước Khi Bắt Đầu
- [ ] Commit hiện tại được push (backup safety)
- [ ] Tất cả tests pass: `pytest tests/ -q`
- [ ] Không có WIP code
- [ ] Đọc kỹ prompt trước execute

### Trong Quá Trình Thực Thi

**Sau Session 1:**
- [ ] Không có `sys.modules['win32*']` ngoài conftest.py
- [ ] `pytest tests/` pass

**Sau Session 2:**
- [ ] 4-5 fixtures tạo thành công
- [ ] 12+ test files refactored
- [ ] Mock count giảm 100+ instances
- [ ] `pytest tests/` pass

**Sau Session 3:**
- [ ] Không có nested patches >2 levels
- [ ] Code readability cải thiện
- [ ] `pytest tests/unit/ui/` pass

**Sau Session 4 (Critical):**
- [ ] `HuntStatusHandler` abstract class tồn tại
- [ ] `HuntOrchestrator` chấp nhận handler param
- [ ] `AppHuntHandler` adapter tạo xong
- [ ] App runs, hunt flow works
- [ ] `pytest tests/` pass
- [ ] **Manual testing**: Start hunt, verify it works

**Sau Session 5:**
- [ ] `tests/unit/` chứa chỉ unit tests
- [ ] `tests/integration/` chứa integration tests
- [ ] Unit tests chạy <15 giây
- [ ] All 400+ tests pass

### Sau Khi Hoàn Thành

- [ ] Tất cả 5 sessions hoàn tất
- [ ] Full test suite pass (400+ tests)
- [ ] Mock count: 250-300 (giảm từ 500+)
- [ ] Unit tests: <15 giây
- [ ] Code review completed
- [ ] Merge to main branch

---

## 🆘 Troubleshooting

### Nếu tests fail sau thay đổi

```bash
# 1. Xem error chi tiết
pytest tests/ -v --tb=long

# 2. Check git diff để hiểu thay đổi
git diff HEAD~1 tests/

# 3. Rollback session hiện tại
git checkout HEAD -- tests/

# 4. Commit lại setup ban đầu
git commit -m "Rollback Session X - Issues found"

# 5. Xem lại prompt, thử lại
```

### Nếu imports bị lỗi

```bash
# 1. Kiểm tra Python path
python -c "import sys; print(sys.path)"

# 2. Verify conftest locations
find tests/ -name conftest.py

# 3. Check test discovery
pytest tests/ --collect-only | grep -E "collected|ERROR"
```

### Nếu CI fails

```bash
# 1. Run locally giống CI
pytest tests/ -v --tb=short

# 2. Check platform (Windows vs Linux)
python -c "import platform; print(platform.system())"

# 3. Verify platform mocks (Session 1)
grep -r "sys.modules" tests/conftest.py
```

---

## 📊 Tracking Progress

Cập nhật file này khi hoàn thành mỗi session:

```markdown
# Sprint 26 Progress

## ✅ Completed Sessions

- [x] Session 1: Consolidate Platform Mocks (2024-XX-XX)
  - Files affected: 6
  - Mocks removed: 35
  - Time spent: 2.5 hours

- [x] Session 2: Create Test Fixtures (2024-XX-XX)
  - Fixtures created: 4
  - Test files refactored: 12
  - Mock reduction: 120
  - Time spent: 8 hours

## ⏳ In Progress

- [ ] Session 3: Replace Nested Patches
  - Status: ...
  - Progress: X/Y files done

## 📅 Pending

- [ ] Session 4: Refactor HuntOrchestrator
- [ ] Session 5: Split Tests
```

---

## 🎯 Success Criteria - Final Checklist

| Criteria | Before | After | Status |
|----------|--------|-------|--------|
| Platform mock files | 5+ | 1 | ✅ |
| Total test mocks | 500+ | 250-300 | ✅ |
| Mock setup per test | 20-30 lines | 1-2 lines | ✅ |
| Callbacks (Orchestrator) | 15 | 1 handler | ✅ |
| Unit test time | 50s | <15s | ✅ |
| Test organization | Confused | Clear | ✅ |
| Nested patch depth | 5 levels | ≤2 levels | ✅ |
| Code review | N/A | Approved | ✅ |
| All tests passing | ? | ✅ Yes | ✅ |

---

## 📚 Tài Liệu Tham Khảo

- **Chi Tiết Prompts**: [`AUTOMATED_EXECUTION_PROMPTS.md`](AUTOMATED_EXECUTION_PROMPTS.md)
- **Session Details**: Xem các file `SESSION_X.md` gốc
- **Test Architecture**: [`../../docs/testing/ARCHITECTURE.md`](../../docs/testing/ARCHITECTURE.md)
- **Cleanup Protocol**: [`CLEANUP_AND_MERGE_PROTOCOL.md`](CLEANUP_AND_MERGE_PROTOCOL.md)

---

## 💡 Tips & Tricks

### Chạy Sessions Nhanh

```bash
# Chỉ session 1
python scripts/run_cleanup_sessions.py --session 1

# Export plan để commit
python scripts/run_cleanup_sessions.py --export .github/sessions.json
git add .github/sessions.json
git commit -m "docs: add cleanup sessions execution plan"

# Kiểm tra mock count
grep -r "MagicMock()" tests/ --include="*.py" | wc -l
```

### Commit Safely

```bash
# Sau mỗi session
git add tests/ lib/ app_gui.py scripts/
git commit -m "refactor: Session X - [Mô tả]"

# Tạo checkpoint tag
git tag -a "sprint26-session1-complete" -m "Session 1 completed"

# Push progress
git push origin main --tags
```

### Verify Changes

```bash
# Mock reduction
echo "Before: $(git show HEAD~1:tests/ | grep -r "MagicMock()" | wc -l) mocks"
echo "After: $(grep -r "MagicMock()" tests/ | wc -l) mocks"

# Test time improvement
echo "Running unit tests..."
time pytest tests/unit/ -q
```

---

## 📞 Support

Nếu gặp vấn đề:

1. **Kiểm tra logs**: Xem `pytest` output chi tiết
2. **Refer prompts**: Xem lại `AUTOMATED_EXECUTION_PROMPTS.md`
3. **Git history**: `git log --oneline` để xem changes
4. **Rollback**: `git checkout HEAD~1` để quay lại safe state

---

**Status**: Ready for Execution 🚀
**Last Updated**: 2026-09-04
**Next Step**: Copy Session 1 prompt → Paste to Copilot → Execute

