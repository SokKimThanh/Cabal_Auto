# ✅ Automated Cleanup & Merge Protocol

## 📋 Overview

| Aspect | Details |
|--------|---------|
| **Purpose** | Automatic cleanup and pre-merge verification |
| **When** | After Session testing complete, before merging to main |
| **Scope** | Sessions 1-5 (UX3B onwards) |
| **Automation** | Python script (cleanup_and_verify.py) |
| **Duration** | ~2-5 minutes per run |
| **Status** | Pre-merge verification gate |

---

## 🚀 Quick Start

### One-Command Cleanup

```bash
# Navigate to project root
cd f:\Cabal_Auto

# Run full cleanup with expected mock range for your session
python scripts/cleanup_and_verify.py --mock-range "200-250"

# Script will:
# 1. Clean temporary files (pyc, cache, logs)
# 2. Clean pytest cache
# 3. Clean test databases
# 4. Run all tests
# 5. Verify no leftover files
# 6. Check mock count
# 7. Verify Git status
# 8. Generate report

# If all green ✅:
git merge session-branch-name
```

---

## 🧹 8-Phase Cleanup Process

### Phase 1: Temporary File Cleanup
Removes:
- `*.pyc` - Compiled Python files
- `__pycache__/` - Python cache directories
- `*.tmp` - Temporary files
- `.pytest_cache/` - Pytest cache
- `.coverage` - Coverage reports
- `htmlcov/` - Coverage HTML

### Phase 2: Pytest Cache Cleanup
Removes:
- `.pytest_cache` directory
- Coverage cache files
- Test state from previous runs

### Phase 3: Test Database Cleanup
Removes:
- `tests/*.db` - Test databases
- `tmp/*.db` - Temporary databases
- Only deletes files with "test" in name (safe)

### Phase 4: Verification Tests
Runs:
```bash
pytest tests/ -v --tb=short -x
```
- All tests must pass
- First failure stops (with -x flag)
- Exit code must be 0

### Phase 5: Leftover Files Check
Verifies no files left behind:
- `tests/**/tmp*.json`
- `tests/**/test_*.db`
- `tests/**/mock_*.json`

Auto-deletes leftover files and reports them

### Phase 6: Mock Count Verification
Runs:
```bash
python analyze_mocks.py
```
- Extracts total mock count
- Verifies it's in expected range
- Example: S4 expects 200-250 mocks (from 674 baseline)

### Phase 7: Git Status Check
Verifies:
- No unexpected file modifications
- Only expected directories modified (tests/, lib/, docs/, etc.)
- Working directory is clean

### Phase 8: Generate Report
Creates `cleanup_report.json`:
```json
{
  "status": "PASS",
  "issues": [],
  "metrics": {
    "mock_count": 225,
    "test_exit_code": 0
  }
}
```

---

## 📊 By-Session Mock Ranges

Use these ranges when running cleanup for each session:

```bash
# Session 1: Consolidate Platform Mocks
python scripts/cleanup_and_verify.py --mock-range "620-650"

# Session 2: Create Test Fixtures
python scripts/cleanup_and_verify.py --mock-range "470-520"

# Session 3: Replace Patch Chains
python scripts/cleanup_and_verify.py --mock-range "450-480"

# Session 4: Refactor HuntOrchestrator ⭐
python scripts/cleanup_and_verify.py --mock-range "200-250"

# Session 5: Test Separation
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

---

## 📋 Pre-Merge Checklist

### Before Running Cleanup

- [ ] All features implemented in feature branch
- [ ] All code committed: `git status` shows nothing
- [ ] Branch is up to date: `git pull origin main`
- [ ] No uncommitted work: `git diff --stat`

### Run Cleanup

```bash
# Check your current mock count
python analyze_mocks.py

# Run cleanup (replace range with your session's expected range)
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

### Review Cleanup Report

```bash
# Check report
cat cleanup_report.json

# Should show:
# - "status": "PASS"
# - "issues": [] (empty!)
# - "metrics": {...with your mock_count...}
```

### After Cleanup ✅

- [ ] Cleanup report shows PASS
- [ ] All 8 phases completed successfully
- [ ] Mock count in expected range
- [ ] No issues reported

### Merge to Main

```bash
# Switch to main
git checkout main

# Ensure main is up to date
git pull origin main

# Merge feature branch
git merge --no-ff session-branch-name
# Creates merge commit for history

# Push to remote
git push origin main

# Delete feature branch
git branch -d session-branch-name
git push origin --delete session-branch-name
```

---

## ⚡ Quick Options

### Skip Test Running (Fast Mode)
```bash
python scripts/cleanup_and_verify.py --skip-tests
```
- Skips Phase 4 (verification tests)
- Useful for quick cleanup check
- Still cleans files and verifies git status

### Quick Cleanup Only
```bash
python scripts/cleanup_and_verify.py --skip-tests --mock-range "200-250"
```
- Cleans files (Phases 1-3, 5)
- Checks mock count (Phase 6)
- Verifies git status (Phase 7)
- **Doesn't run tests** (~2 minutes instead of ~5)

---

## 🔍 Understanding the Report

### cleanup_report.json Structure

```json
{
  "timestamp": "1693689600.0",
  "status": "PASS|FAIL",
  "issues": [
    "Any problems found during cleanup"
  ],
  "metrics": {
    "mock_count": 225,
    "test_exit_code": 0
  }
}
```

### Status Meanings

- **PASS** ✅: All phases succeeded, ready to merge
- **FAIL** ❌: One or more phases failed, fix issues before merge

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Tests failed with exit code X | Code has bugs | Fix failing tests, rerun cleanup |
| Mock count outside range | Changes didn't reduce mocks as expected | Review changes, verify correctness |
| Unexpected modifications | Files changed that shouldn't | `git status` to see what, revert or commit |
| Leftover files found | Tests leave behind state | Fix tests to cleanup after themselves |
| Git status not clean | Uncommitted changes | `git add` and `git commit` first |

---

## 🔧 Troubleshooting

### Q: Tests fail during cleanup
**A:**
```bash
# See which test failed
pytest tests/ -v --tb=short

# Fix the failing test
# ... edit test file ...

# Rerun cleanup
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

### Q: Mock count not in range
**A:**
```bash
# Check actual mock count
python analyze_mocks.py

# If count seems wrong:
# - Verify all session changes were applied
# - Check if all old mocks were removed
# - Rerun analysis

# If count is correct but range is wrong:
# - Update --mock-range parameter to match your session
```

### Q: Git status shows unexpected changes
**A:**
```bash
# See what's modified
git status

# If should be committed:
git add .
git commit -m "chore: session changes"

# If should be reverted:
git checkout -- .

# Rerun cleanup
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

### Q: Can I run cleanup before all tests pass?
**A:** No. Use `--skip-tests` to skip test phase temporarily:
```bash
python scripts/cleanup_and_verify.py --skip-tests

# Fix tests, then run full cleanup:
python scripts/cleanup_and_verify.py --mock-range "200-250"
```

---

## 🎯 Typical Session Workflow

```
1. Create feature branch
   git checkout -b session-1-platform-mocks
   
2. Implement changes
   - Edit tests/conftest.py
   - Remove duplicate mocks
   - Add shared fixtures
   - ... all session work ...
   
3. Commit changes
   git add .
   git commit -m "feat: session 1 consolidate platform mocks"
   
4. Run cleanup & verify
   python scripts/cleanup_and_verify.py --mock-range "620-650"
   
5. If cleanup passes ✅
   git merge --no-ff session-1-platform-mocks
   
6. If cleanup fails ❌
   - Fix issues (failed tests, wrong mock count, etc.)
   - Commit fixes
   - Run cleanup again
   - Try merge when cleanup passes
```

---

## 📈 Expected Cleanup Times

| Phase | Time | Notes |
|-------|------|-------|
| Temp File Cleanup | ~1s | Fast local cleanup |
| Pytest Cache | ~1s | Just directory removal |
| Test DB Cleanup | ~1s | Few test databases |
| **Verification Tests** | **~2-3m** | Most time spent here! |
| Leftover Files | ~1s | Quick glob search |
| Mock Count | ~10s | Runs analyze_mocks.py |
| Git Status | ~1s | Quick git command |
| Report Generation | ~1s | JSON write |
| **Total (full run)** | **~3-5m** | With tests |
| **Total (skip tests)** | **~15-30s** | Fast mode |

---

## 🚨 Pre-Merge Gates

Cleanup enforces these gates before merge:

| Gate | Requirement | Blocks Merge |
|------|-------------|-------------|
| **Tests Pass** | exit_code == 0 | YES ✋ |
| **Mock Count** | In expected range | YES ✋ |
| **No Leftover Files** | Clean workspace | YES ✋ |
| **Git Status Clean** | Only expected files modified | YES ✋ |

**All 4 gates must pass to merge!**

---

## 📚 Integration with CI/CD

For GitHub Actions, add `.github/workflows/cleanup-verify.yml`:

```yaml
name: Cleanup & Merge Verification

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  cleanup-verify:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run cleanup verification
        run: python scripts/cleanup_and_verify.py
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: cleanup-report
          path: cleanup_report.json
```

This runs cleanup on every PR, ensuring code is clean before merging!

---

## ✨ Best Practices

1. **Always run cleanup before merge**
   - Don't skip this step!
   - It catches bugs early

2. **Use correct --mock-range for your session**
   - Session 1: `620-650`
   - Session 4: `200-250`
   - See table above

3. **If cleanup fails, fix before merge**
   - Don't merge with failing tests
   - Don't merge with wrong mock count
   - These are quality gates!

4. **Review cleanup_report.json**
   - Check the metrics
   - Verify mock count matches expectations
   - Understand any issues reported

5. **Keep cleanup report in PR**
   - Attach to pull request description
   - Shows reviewers you followed process
   - Proves code passed all gates

---

## 🎓 Learning Path

**Understanding Cleanup**:
1. Run cleanup once manually: `python scripts/cleanup_and_verify.py --skip-tests`
2. Review the report: `cat cleanup_report.json`
3. Read the phases that failed (if any)
4. Fix issues and rerun

**Integrating into Workflow**:
1. Add to your pre-merge checklist
2. Make it part of your team's workflow
3. Eventually automate via CI/CD

**Scaling to Team**:
1. Document in team wiki
2. Add cleanup as required merge step
3. Enforce via branch protection rules
4. Monitor cleanup reports over time

---

## 📞 Support

If cleanup fails:

1. **Read the error message** - Usually clear!
2. **Check cleanup_report.json** - Has all details
3. **Run in verbose mode** - See each phase output
4. **Try --skip-tests first** - Narrow down issue
5. **Fix the underlying problem** - Usually test or git issue

---

**Status**: 🟢 Ready to use from UX3B onwards
**Last Updated**: 2026-09-03
**For Sessions**: 1-5 (mock reduction remediation)
**Fits Into**: Pre-merge workflow, quality gate
