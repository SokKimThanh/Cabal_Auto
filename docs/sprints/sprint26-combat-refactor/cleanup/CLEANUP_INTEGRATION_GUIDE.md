# 🔄 Cleanup Protocol Integration Guide

## Overview

This guide shows how to integrate cleanup verification into each SESSION document.

**Status**: Reference guide for updating SESSION_1-5 documents  
**When**: After each session implementation is complete  
**Tool**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md) + [scripts/cleanup_and_verify.py](../../scripts/cleanup_and_verify.py)

---

## Quick Integration

Add this section to the **END** of each SESSION document:

### Session 1 Example

At the end of `SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md`, add:

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing Session 1

Before merging your changes, **MUST run cleanup verification**:

```bash
# Navigate to project root
cd f:\Cabal_Auto

# Run cleanup with Session 1's expected mock range
python scripts/cleanup_and_verify.py --mock-range "620-650"
```

### Expected Results
- **Previous mock count**: 674
- **Expected after S1**: 620-650 mocks
- **Expected reduction**: 24-54 mocks (3-8% reduction)
- **All phases**: Must show ✅

### If Cleanup Passes ✅
```bash
# Ready to merge!
git merge --no-ff session-1-platform-mocks
git push origin main
```

### If Cleanup Fails ❌
See [CLEANUP_AND_MERGE_PROTOCOL.md - Troubleshooting](CLEANUP_AND_MERGE_PROTOCOL.md#%EF%B8%8F-troubleshooting)
```bash
# Common causes:
# 1. Tests fail → Fix failing tests
# 2. Mock count wrong → Verify consolidation completed
# 3. Git dirty → Commit remaining changes
# 4. Leftover files → Check test cleanup

# Then rerun cleanup
python scripts/cleanup_and_verify.py --mock-range "620-650"
```

---
```

---

## Session-by-Session Integration

Add this exact cleanup section to each SESSION file:

### Session 1: Platform Mocks
**File**: `SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md`  
**Location**: End of file, after all steps  
**Mock Range**: `620-650`

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing Session 1

Before merging your changes to main, run automated cleanup:

```bash
python scripts/cleanup_and_verify.py --mock-range "620-650"
```

**Expected Results**:
- Mock count: 620-650 (from 674 baseline)
- All 8 cleanup phases: ✅ Pass
- Cleanup report: cleanup_report.json with "PASS" status

**See Full Details**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
```

---

### Session 2: Test Fixtures
**File**: `SESSION_2_TEST_FIXTURES.md`  
**Location**: End of file, after all steps  
**Mock Range**: `470-520`

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing Session 2

Run cleanup with updated mock range:

```bash
python scripts/cleanup_and_verify.py --mock-range "470-520"
```

**Expected Results**:
- Mock count: 470-520 (from 674 baseline → 30% reduction!)
- All 8 cleanup phases: ✅ Pass
- Cumulative reduction from Sessions 1+2: 154-204 mocks saved

**Fixture Performance Check**:
```bash
# Verify test speed improved
pytest tests/ -v --durations=10
# Should see faster test execution than baseline
```

**See Full Details**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
```

---

### Session 3: Patch Chains
**File**: `SESSION_3_PATCH_CHAINS.md`  
**Location**: End of file, after all steps  
**Mock Range**: `450-480`

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing Session 3

Run cleanup with Session 3's mock range:

```bash
python scripts/cleanup_and_verify.py --mock-range "450-480"
```

**Expected Results**:
- Mock count: 450-480 (from 674 baseline → 33% reduction!)
- All 8 cleanup phases: ✅ Pass
- Cumulative reduction from Sessions 1+2+3: 194-224 mocks saved
- **Readability Improvement**: @patch decorators over with chains

**Code Quality Check**:
```bash
# Verify decorator stacking looks clean
pytest tests/unit/features/hunt/ -v

# Should see cleaner @patch decorator usage
# vs previous with patch() nesting
```

**See Full Details**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
```

---

### Session 4: HuntOrchestrator Refactor
**File**: `SESSION_4_ORCHESTRATOR_REFACTOR.md`  
**Location**: End of file, after all steps  
**Mock Range**: `200-250`

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing Session 4 (MAJOR REFACTOR!)

Session 4 is the highest-impact session. Extra verification needed:

#### Phase 1: Quick Cleanup Check
```bash
# Fast check without running full test suite
python scripts/cleanup_and_verify.py --skip-tests --mock-range "200-250"
```

#### Phase 2: Full Verification
```bash
# Run complete verification with tests
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

**Expected Results**:
- Mock count: 200-250 (from 674 baseline → **70% reduction!**)
- All 8 cleanup phases: ✅ Pass
- Cumulative reduction from Sessions 1-4: 424-474 mocks saved!
- **Critical Tests Pass**: 
  - test_hunt_orchestrator.py: 73 → ~35 mocks (52% reduction!)
  - All callback-related tests

**Integration Testing**:
```bash
# Verify app still works after major refactor
pytest tests/integration/ -v

# Manual test on Windows:
# 1. Run app: python scripts/main.py
# 2. Start hunt
# 3. Verify all status updates work
# 4. Check no callback errors in console
```

**If Tests Fail**:
This is expected for such a large refactor!
1. See [SESSION_4_ORCHESTRATOR_REFACTOR.md - Troubleshooting](SESSION_4_ORCHESTRATOR_REFACTOR.md#troubleshooting)
2. Fix failing tests
3. Rerun cleanup verification

**See Full Details**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
```

---

### Session 5: Test Separation
**File**: `SESSION_5_TEST_SEPARATION.md`  
**Location**: End of file, after all steps  
**Mock Range**: `200-250`

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing Session 5

Run cleanup with Session 5's mock range:

```bash
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

**Expected Results**:
- Mock count: 200-250 (same as Session 4, Session 5 is organizational)
- All 8 cleanup phases: ✅ Pass
- **Test Organization Improved**:
  - Unit tests in `tests/unit/` → ~30 seconds execution
  - Integration tests in `tests/integration/` → ~20 seconds execution
  - Total time: ~50s → ~50s (reorganization, not speed improvement)

**Test Discovery Verification**:
```bash
# Verify unit tests run in isolation
pytest tests/unit/ -v
# Should run ~30-35 seconds

# Verify integration tests run separately
pytest tests/integration/ -v
# Should run ~15-20 seconds

# Both together
pytest tests/ -v
# Should run ~50s total
```

**Code Organization Check**:
```bash
# Verify directory structure is clean
tree tests/ /F
# Should see:
# tests/
#   ├── unit/
#   │   ├── features/
#   │   ├── views/
#   │   └── conftest.py
#   ├── integration/
#   │   ├── orchestrator/
#   │   ├── vision/
#   │   └── conftest.py
#   └── conftest.py
```

**See Full Details**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
```

---

## Integration Checklist

To integrate cleanup into all session documents:

### Task List

```bash
# 1. Update SESSION_1
# Add cleanup section to end of SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md
# Mock range: 620-650

# 2. Update SESSION_2
# Add cleanup section to end of SESSION_2_TEST_FIXTURES.md
# Mock range: 470-520

# 3. Update SESSION_3
# Add cleanup section to end of SESSION_3_PATCH_CHAINS.md
# Mock range: 450-480

# 4. Update SESSION_4
# Add cleanup section to end of SESSION_4_ORCHESTRATOR_REFACTOR.md
# Mock range: 200-250
# Note: Include integration testing step!

# 5. Update SESSION_5
# Add cleanup section to end of SESSION_5_TEST_SEPARATION.md
# Mock range: 200-250

# Verification
# Run all cleanup sections to ensure they work
pytest tests/ -v  # Must all pass first!
```

---

## Template for Copy-Paste

Use this minimal template to add cleanup to any session:

```markdown
---

## 🧹 Cleanup & Pre-Merge Verification

### After Completing This Session

Before merging, run automated cleanup verification:

```bash
# Replace MOCK_RANGE with your session's expected range
python scripts/cleanup_and_verify.py --mock-range "MOCK_RANGE"
```

**Expected**: All phases ✅, mock count in range, cleanup_report.json with "PASS"

**If it fails**: See [CLEANUP_AND_MERGE_PROTOCOL.md#troubleshooting](CLEANUP_AND_MERGE_PROTOCOL.md#%EF%B8%8F-troubleshooting)

**See Full Details**: [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)
```

---

## Testing the Cleanup Process

Before using cleanup in real session, test it:

```bash
# 1. Ensure all tests pass
pytest tests/ -v

# 2. Test cleanup script exists
ls -la scripts/cleanup_and_verify.py

# 3. Dry run with --skip-tests
python scripts/cleanup_and_verify.py --skip-tests

# 4. Check report was created
cat cleanup_report.json

# 5. Full run (takes 3-5 minutes)
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

---

## FAQ

### Q: Should I add cleanup to all 5 sessions?
**A:** Yes! Each session should have cleanup section at end.

### Q: Do I need to run cleanup after EVERY commit?
**A:** No. Only run cleanup:
- After session is COMPLETE
- Before merging to main
- When reviewing changes for PR

### Q: What if cleanup fails?
**A:** See the troubleshooting guide in [CLEANUP_AND_MERGE_PROTOCOL.md](CLEANUP_AND_MERGE_PROTOCOL.md)  
Most common: tests fail or mock count is wrong

### Q: Can I merge without cleanup?
**A:** Technically yes, but **NOT RECOMMENDED**.  
Cleanup is a quality gate - it catches bugs, side effects, and wrong mock counts!

### Q: How often should I update the cleanup protocol?
**A:** As you learn more about your tests:
- If certain tests always fail in CI, fix root cause
- If mock ranges are consistently off, adjust expectations
- If cleanup takes too long, optimize slow tests

---

## Status

✅ **CLEANUP_AND_MERGE_PROTOCOL.md** - Complete and ready  
✅ **scripts/cleanup_and_verify.py** - Implemented and tested  
✅ **README_MOCK_REMEDIATION_INDEX.md** - Updated with cleanup integration  
⏳ **SESSION_1-5 documents** - Ready for cleanup section integration  

**Next Steps**: Add cleanup sections to each SESSION_X document following this guide.
