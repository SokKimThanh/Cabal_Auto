# 🎯 Session-Based Mock/Patch Remediation Plan

## 📋 Tổng Quan (Overview)

Dựa trên báo cáo phân tích, dưới đây là kế hoạch cải thiện được chia thành **5 sessions có thứ tự ưu tiên**.

### Chiến Lược Thực Hiện
- **Sessions 1-3**: Quick wins + infrastructure (hoàn thành trong 2-3 ngày)
- **Session 4**: Major refactor (3-5 ngày, high impact)
- **Session 5**: Long-term organization (2-3 ngày, preventive)

### Lợi Ích Kỳ Vọng
- **Trước**: 674 mocks across 56 files (12.04 avg/file)
- **Sau**: ~100-200 mocks (60-80% reduction)
- **Thời gian total**: ~10-15 ngày engineering time (distributed)

---

## 🗓️ Session Schedule

### **Session 1: Consolidate Platform Mocks** ⚡ QUICK WIN
- **Duration**: 2-3 hours
- **Effort**: 🟢 Low
- **Impact**: 🟡 Medium (5-10% mock reduction)
- **Status**: ✅ Ready to start
- **Main Goal**: Remove platform mock duplication in 5+ test files
- **Expected Savings**: 30-50 mock instances

**Document**: [SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md](SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md)

---

### **Session 2: Create Standard Test Fixtures** 🏗️ BUILD INFRASTRUCTURE
- **Duration**: 1 day
- **Effort**: 🟡 Medium
- **Impact**: 🟠 High (15-20% mock reduction)
- **Status**: ⏳ Depends on Session 1
- **Main Goal**: Centralize mock setup in conftest.py
- **Expected Savings**: 100-150 mock instances

**Document**: [SESSION_2_TEST_FIXTURES.md](SESSION_2_TEST_FIXTURES.md)

---

### **Session 3: Replace Nested Patch Chains** 🧹 CODE CLEANUP
- **Duration**: 4-6 hours
- **Effort**: 🟢 Low
- **Impact**: 🟢 Low (readability improvement)
- **Status**: ⏳ Independent (can be parallel)
- **Main Goal**: Improve test readability
- **Files to Update**: 3-5 files

**Document**: [SESSION_3_PATCH_CHAINS.md](SESSION_3_PATCH_CHAINS.md)

---

### **Session 4: Refactor HuntOrchestrator** 🎯 MAJOR REFACTOR
- **Duration**: 3-5 days
- **Effort**: 🔴 High
- **Impact**: 🔴 Critical (30% mock reduction + architectural improvement)
- **Status**: ⏳ Depends on Sessions 1-2
- **Main Goal**: Reduce callbacks from 15 to 1 handler object
- **Expected Savings**: 200-300 mock instances
- **Affected Files**: 15+ files (orchestrator + tests + app_gui)

**Document**: [SESSION_4_ORCHESTRATOR_REFACTOR.md](SESSION_4_ORCHESTRATOR_REFACTOR.md)

---

### **Session 5: Split Integration/Unit Tests** 🏛️ LONG-TERM ORGANIZATION
- **Duration**: 2-3 days
- **Effort**: 🟡 Medium
- **Impact**: 🟡 Medium (organization + test clarity)
- **Status**: ⏳ Can be done anytime after Session 4
- **Main Goal**: Separate concerns, improve test intent
- **Expected Improvements**: Better structure, easier debugging

**Document**: [SESSION_5_TEST_SEPARATION.md](SESSION_5_TEST_SEPARATION.md)

---

## 📊 Progress Tracking

### Checklist by Session

#### Session 1: Platform Mocks ✅
- [ ] Identify all `sys.modules[...]` patches across test files
- [ ] Create platform mock fixtures in `tests/conftest.py`
- [ ] Remove duplicated patches from individual test files
- [ ] Verify all tests still pass
- [ ] Commit: "refactor: consolidate platform mocks in conftest"

#### Session 2: Test Fixtures ✅
- [ ] Create `@pytest.fixture` for `mock_orchestrator`
- [ ] Create `@pytest.fixture` for `mock_hunt_app`
- [ ] Create `@pytest.fixture` for `mock_bot_manager`
- [ ] Refactor existing tests to use new fixtures
- [ ] Document fixture API in conftest.py
- [ ] Commit: "refactor: add standard test fixtures"

#### Session 3: Patch Chains ✅
- [ ] Identify nested `with patch()` chains in test files
- [ ] Convert to `@patch` decorators where appropriate
- [ ] Improve readability of parametrized patches
- [ ] Verify all tests still pass
- [ ] Commit: "refactor: replace nested patch chains with decorators"

#### Session 4: Orchestrator Refactor ✅
- [ ] Design HuntStatusHandler callback object
- [ ] Refactor HuntOrchestrator constructor
- [ ] Update app_gui.py to implement HuntStatusHandler
- [ ] Update all test fixtures for new orchestrator signature
- [ ] Update integration tests with new patterns
- [ ] Verify hunt functionality still works
- [ ] Commit: "refactor: reduce HuntOrchestrator callbacks via handler object"

#### Session 5: Test Separation ✅
- [ ] Create directory structure for separated tests
- [ ] Move files from `tests/unit/` to appropriate locations
- [ ] Update import paths and relative references
- [ ] Verify test discovery still works
- [ ] Commit: "refactor: separate integration and unit tests"

---

## 📈 Metrics Dashboard

### Current State (Baseline)
```
Total Mock/Patch Instances:     674
Files Using Mocks:              56
Average per File:               12.04
Largest File:                   73 (test_hunt_orchestrator.py)

Breakdown:
  Mock() calls:                 265 (39.3%)
  MagicMock():                  190 (28.2%)
  with patch():                 139 (20.6%)
  @patch decorators:            19 (2.8%)
  monkeypatch:                  46 (6.8%)
  sys.modules patches:          15 (2.2%)
```

### Post-Session 1 (Expected)
```
Total Mock/Patch Instances:     624  (-50)
System Mocks in conftest:       15   (centralized)
Duplicated patches removed:     7 files
```

### Post-Session 2 (Expected)
```
Total Mock/Patch Instances:     474  (-200 cumulative)
Standard Fixtures Created:      3
Test boilerplate reduced:       ~40%
```

### Post-Session 3 (Expected)
```
Total Mock/Patch Instances:     454  (-220 cumulative)
Nested patch chains:            0
Decorator-based patches:        +50
Readability improvement:        High
```

### Post-Session 4 (Expected)
```
Total Mock/Patch Instances:     154  (-520 cumulative)
HuntOrchestrator callbacks:     1 handler object
Callback mocks:                 Down from 300 to 50
Files refactored:               15
```

### Post-Session 5 (Expected)
```
Total Mock/Patch Instances:     144  (-530 cumulative)
Test file organization:         Clear separation
Test intent:                     Crystal clear
Maintenance:                     Much easier
```

---

## 🚀 Execution Strategy

### How to Use This Plan

1. **Start with Session 1** - It's a quick win that sets up infrastructure
2. **Complete in order** - Sessions build on each other (1→2→3→4→5)
3. **Session 4 is optional but recommended** - Highest impact if you have time
4. **Session 5 is preventive** - Do it if you want long-term maintainability

### For Each Session

1. Read the session document fully
2. Review the "Files to Update" section
3. Follow the step-by-step implementation guide
4. Run tests after each change
5. Commit with the suggested message
6. Mark checklist items as complete

### Testing Strategy

After each session:
```bash
# Run all tests
pytest tests/ -v

# Run only tests for changed files
pytest tests/unit/test_action_bar.py -v
pytest tests/unit/features/hunt/ -v

# Check test count and speed
pytest tests/ --collect-only | grep "test session starts"
pytest tests/ --durations=10
```

### Rollback Plan

Each session is independent. If something breaks:
1. Check git diff to see exactly what changed
2. Revert just that session's changes
3. Fix the issue (usually a mock signature change)
4. Re-apply the changes

```bash
# If a session breaks tests
git diff HEAD~1..HEAD  # See what changed
git revert HEAD        # Rollback
git reset --hard HEAD  # Or complete reset
```

---

## 📚 Document Structure

Each session document includes:

### Header
- **Objective**: What we're fixing
- **Duration**: Time estimate
- **Effort Level**: 🟢 Low / 🟡 Medium / 🔴 High
- **Impact**: Expected mock reduction
- **Prerequisites**: Required before this session

### Main Content
- **Problem Analysis**: Why this needs fixing
- **Solution Design**: How we'll fix it
- **Files to Update**: Exact files to modify
- **Step-by-Step Guide**: Detailed implementation
- **Testing Checklist**: How to verify the work

### Examples
- **Before**: Original code with many mocks
- **After**: Refactored code with fewer mocks

### Artifacts
- Code samples ready to copy-paste
- Test examples
- Common patterns to apply

---

## ⚠️ Important Notes

### Session Interdependencies
```
Session 1 (Platform Mocks)
        ↓
Session 2 (Test Fixtures) ← Use results from S1
        ↓
Session 3 (Patch Chains) ← Parallel or after S2
        ↓
Session 4 (Orchestrator) ← Most important, uses S1+S2
        ↓
Session 5 (Test Separation) ← Optional, cleanup
```

### Backward Compatibility
- ✅ All changes maintain existing test behavior
- ✅ No breaking changes to public APIs
- ✅ Existing tests should still pass (after refactoring)
- ⚠️ May need minor fixture adjustments in downstream tests

### Communication with Team
```markdown
## Sprint Notes for Each Session

### Session 1
"Consolidating platform-specific mocks in conftest.py to reduce duplication"

### Session 2
"Creating standard test fixtures to reduce boilerplate setup code"

### Session 3
"Improving test readability by converting nested patch chains"

### Session 4
"Architectural improvement: refactoring HuntOrchestrator to reduce callback complexity"

### Session 5
"Organizing test structure for better separation of concerns"
```

---

## ✅ Success Criteria

### For Each Session
- ✅ All tests pass (green CI)
- ✅ Reduction in mock/patch count achieved
- ✅ Code review approved
- ✅ No breaking changes to APIs
- ✅ Documentation updated

### For the Entire Plan
- ✅ Total mock reduction: 60-80% (674 → 100-200)
- ✅ All 56 files updated/improved
- ✅ Average mocks/file: 12 → 2-4
- ✅ Maintainability significantly improved
- ✅ No test regressions

---

## 📞 Quick Links

| Session | Document | Focus | Duration |
|---------|----------|-------|----------|
| 1 | [SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md](SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md) | Remove duplication | 2-3h |
| 2 | [SESSION_2_TEST_FIXTURES.md](SESSION_2_TEST_FIXTURES.md) | Build infrastructure | 1 day |
| 3 | [SESSION_3_PATCH_CHAINS.md](SESSION_3_PATCH_CHAINS.md) | Improve readability | 4-6h |
| 4 | [SESSION_4_ORCHESTRATOR_REFACTOR.md](SESSION_4_ORCHESTRATOR_REFACTOR.md) | Major refactor | 3-5 days |
| 5 | [SESSION_5_TEST_SEPARATION.md](SESSION_5_TEST_SEPARATION.md) | Organize structure | 2-3 days |

---

## 🎓 Key Learnings

### What We'll Learn
1. How to identify and consolidate duplicated mocks
2. Creating effective test fixtures and harnesses
3. Proper use of @patch vs with patch()
4. Dependency injection patterns for large objects
5. Test organization best practices

### Anti-patterns to Avoid
- ❌ Duplicating mock setup across multiple test files
- ❌ Having tests with 50+ mocks without refactoring
- ❌ Calling sys.modules directly in test files (use fixtures)
- ❌ Deep nesting of with patch() statements
- ❌ Mixing integration and unit tests in same file

### Best Practices to Adopt
- ✅ Centralize platform mocks in conftest.py
- ✅ Create reusable test fixtures for complex objects
- ✅ Use @patch decorators for clean, readable tests
- ✅ Design classes with dependency injection in mind
- ✅ Clearly separate unit and integration tests

---

**Last Updated**: 2026-09-03
**Status**: 🟢 Ready to Execute
**Recommended Start**: Session 1 (today)

Next: Read [SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md](SESSION_1_CONSOLIDATE_PLATFORM_MOCKS.md)
