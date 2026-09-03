# 📑 Index Công Cụ Thực Thi Tự Động - Sprint 26

## 🎯 Các File Hỗ Trợ Thực Thi

### 1. **AUTOMATED_EXECUTION_PROMPTS.md** (📌 Chính)
   - **Mục đích**: Chứa đầy đủ prompt chi tiết cho 5 sessions
   - **Cách dùng**: Copy prompt → Paste vào Copilot → Execute
   - **Nội dung**:
     - Prompt Session 1: Consolidate Platform Mocks (2-3 hours)
     - Prompt Session 2: Create Test Fixtures (1 day)
     - Prompt Session 3: Replace Nested Patches (4-6 hours)
     - Prompt Session 4: Refactor HuntOrchestrator (3-5 days)
     - Prompt Session 5: Split Integration/Unit Tests (2-3 days)
   - **Đặc điểm**: Mỗi prompt có step-by-step, acceptance criteria, expected output

### 2. **HOW_TO_EXECUTE_AUTOMATED_PROMPTS.md** (📚 Hướng dẫn)
   - **Mục đích**: Hướng dẫn chi tiết cách sử dụng prompts
   - **Cách dùng**: Đọc trước khi bắt đầu
   - **Nội dung**:
     - 3 phương pháp thực thi
     - Danh sách kiểm tra trước/trong/sau
     - Troubleshooting
     - Progress tracking
     - Tips & tricks
   - **Lợi ích**: Rõ ràng, an toàn, dễ debug

### 3. **scripts/run_cleanup_sessions.py** (🔧 Công cụ)
   - **Mục đích**: Script Python để tổ chức execution
   - **Cách dùng**: `python scripts/run_cleanup_sessions.py [options]`
   - **Chức năng**:
     ```bash
     --summary      # In tóm tắt tất cả sessions
     --export FILE  # Export session plan sang JSON
     --session NUM  # Xem hướng dẫn cho session cụ thể
     --all          # Execute tất cả sessions
     ```
   - **Output**: Session metadata, dependencies, time estimates

---

## 🚀 Quick Start (3 Cách Thực Thi)

### Cách 1️⃣: Direct Copy-Paste (Nhanh nhất)

```
1. Mở: AUTOMATED_EXECUTION_PROMPTS.md
2. Tìm: "## 🎯 Session X: [Tên]"
3. Copy: Section "### Automated Execution Prompt"
4. Paste: Vào GitHub Copilot chat
5. Send: "Execute this task"
6. ✅ Done!
```

**Thời gian**: 2 phút per session

---

### Cách 2️⃣: Sử Dụng Script

```bash
# Xem tóm tắt
python scripts/run_cleanup_sessions.py --summary

# Export để tracking
python scripts/run_cleanup_sessions.py --export cleanup-plan.json

# Chi tiết session
python scripts/run_cleanup_sessions.py --session 1
```

**Ưu điểm**: Structured, theo dõi được progress

---

### Cách 3️⃣: Manual Step-by-Step

1. Đọc `HOW_TO_EXECUTE_AUTOMATED_PROMPTS.md`
2. Chọn session → Copy prompt
3. Paste + Execute
4. Tick danh sách kiểm tra
5. Commit kết quả

**Ưu điểm**: An toàn, dễ debug, có checkpoint

---

## 📋 Session Overview

| # | Tên | Thời Gian | Effort | Risk | Files | Depends |
|---|-----|----------|--------|------|-------|---------|
| 1️⃣ | Platform Mocks | 2-3h | Low | Very Low | 6 | None |
| 2️⃣ | Fixtures | 1 day | Med | Low | 12+ | 1 |
| 3️⃣ | Patch Chains | 4-6h | Low | Very Low | 3-5 | None |
| 4️⃣ | Orchestrator | 3-5d | High | Medium | 15+ | 1,2 |
| 5️⃣ | Test Split | 2-3d | Med | Low | 30+ | 1-4 |

---

## 🎯 Execution Plan

```
Week 1:
  Mon:   Session 1 (Copy prompt → Execute → Verify)
  Tue:   Session 2 (Test fixtures)
  Wed:   Session 3 (Patch chains) - Parallel có thể
  
Week 2:
  Mon-Wed: Session 4 (⚠️ Major refactoring - Orchestrator)
  Thu-Fri: Session 5 (Test reorganization)
  
Week 3:
  Mon-Tue: Verification, testing
  Wed-Fri: Code review, merge
```

---

## ✅ Checklist Trước/Sau Mỗi Session

### Trước Session
```
□ Read prompt carefully (AUTOMATED_EXECUTION_PROMPTS.md)
□ Commit current state (git commit)
□ Ensure tests pass (pytest tests/ -q)
□ No WIP code
□ Understand dependencies
```

### Sau Session
```
□ Run verification: pytest tests/ -v
□ Check acceptance criteria
□ Review changes: git diff HEAD~1
□ Commit: git commit -m "refactor: Session X - ..."
□ Update progress in this file
□ Tag: git tag -a "s26-sessionX" -m "..."
```

---

## 📊 Progress Dashboard

### ✅ Completed
- [ ] Session 1: Platform Mocks Consolidation
- [ ] Session 2: Standard Test Fixtures
- [ ] Session 3: Replace Nested Patches
- [ ] Session 4: Refactor HuntOrchestrator
- [ ] Session 5: Split Integration/Unit Tests

### Metrics Before/After

| Metric | Before | Target | After |
|--------|--------|--------|-------|
| Total Mocks | 500+ | 250-300 | ? |
| Mock Setup Lines | 20-30 | 1-2 | ? |
| Platform Mock Files | 5+ | 1 | ? |
| Orchestrator Callbacks | 15 | 1 | ? |
| Unit Test Time | 50s | <15s | ? |
| Nested Patch Depth | 5 | ≤2 | ? |

---

## 🔗 File Relationships

```
AUTOMATED_EXECUTION_PROMPTS.md (📌 Prompts - Copy từ đây!)
├── Session 1 Prompt
├── Session 2 Prompt
├── Session 3 Prompt
├── Session 4 Prompt
└── Session 5 Prompt
     ↓ (Reference)
HOW_TO_EXECUTE_AUTOMATED_PROMPTS.md (📚 Hướng dẫn)
├── Phương pháp thực thi
├── Checklist
├── Troubleshooting
└── Progress tracking
     ↓ (Support)
scripts/run_cleanup_sessions.py (🔧 Công cụ)
├── --summary: Show session info
├── --session N: Get specific session details
├── --export: Save as JSON
└── --all: Execute all
```

---

## 🎓 Hướng Dẫn Chi Tiết

### Để Thực Thi Session 1

**B1: Mở prompt file**
```
f:\Cabal_Auto\docs\sprints\sprint26-combat-refactor\cleanup\
  └─ AUTOMATED_EXECUTION_PROMPTS.md
```

**B2: Tìm "## 🎯 Session 1: Consolidate Platform Mocks"**

**B3: Copy section "### Automated Execution Prompt"**
```
TASK: Consolidate duplicated sys.modules...
OBJECTIVE:
  - Remove platform mock duplication...
IMPLEMENTATION STEPS:
  1. ANALYSIS PHASE (10 min)
  ...
```

**B4: Paste vào Copilot Chat**

**B5: Thêm instruction**
```
Execute this task using automated tools.
Follow all steps in order.
Verify with pytest after each phase.
```

**B6: Đợi kết quả**
- Copilot sẽ thực thi step by step
- Xem progress trong terminal
- Verify kết quả cuối cùng

**B7: Verify & Commit**
```bash
pytest tests/ -q           # Should pass
git diff HEAD~1            # Review changes
git commit -m "refactor: Session 1 - Consolidate platform mocks"
```

---

## 🆘 Nếu Có Vấn Đề

### Tests Fail
```bash
# 1. Xem lỗi chi tiết
pytest tests/ -v --tb=long

# 2. Rollback
git checkout HEAD -- tests/

# 3. Xem lại prompt
# 4. Thử lại
```

### Import Errors
```bash
# 1. Check conftest locations
find tests/ -name "conftest*.py"

# 2. Verify pytest config
cat pytest.ini

# 3. Test discovery
pytest tests/ --collect-only
```

### Need Help
1. Xem: `HOW_TO_EXECUTE_AUTOMATED_PROMPTS.md` → Troubleshooting
2. Refer: Original `SESSION_X.md` files
3. Check: CLEANUP_AND_MERGE_PROTOCOL.md

---

## 🎯 Success = Tất cả 5 Checkboxes Ticked

```
✅ Session 1: Platform Mocks (2-3h)
✅ Session 2: Fixtures (1d)
✅ Session 3: Patch Chains (4-6h)
✅ Session 4: Orchestrator (3-5d)
✅ Session 5: Test Split (2-3d)

Result:
  - Mocks: 500+ → 250-300 ✅
  - Setup: 20-30 lines → 1-2 lines ✅
  - Unit Test: 50s → <15s ✅
  - Code Quality: ⬆️ ✅
  - Team Velocity: ⬆️ ✅
```

---

## 📞 Documentation Map

```
📁 docs/sprints/sprint26-combat-refactor/cleanup/
├── README_MOCK_REMEDIATION_INDEX.md          ← Why this sprint matters
├── SESSION_REMEDIATION_PLAN.md               ← Overall strategy
├── SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md   ← Original detailed session
├── SESSION_2_TEST_FIXTURES.md                ← Original detailed session
├── SESSION_3_PATCH_CHAINS.md                 ← Original detailed session
├── SESSION_4_ORCHESTRATOR_REFACTOR.md        ← Original detailed session
├── SESSION_5_TEST_SEPARATION.md              ← Original detailed session
├── CLEANUP_AND_MERGE_PROTOCOL.md             ← How to merge safely
│
├── 🆕 AUTOMATED_EXECUTION_PROMPTS.md         ← 👈 USE THIS FOR EXECUTION
├── 🆕 HOW_TO_EXECUTE_AUTOMATED_PROMPTS.md    ← 👈 USE THIS FOR GUIDANCE
└── 🆕 INDEX.md                              ← 👈 YOU ARE HERE
```

---

**Last Updated**: 2026-09-04  
**Status**: ✅ Ready for Execution  
**Next Step**: Copy Session 1 Prompt → Paste to Copilot → Execute 🚀

