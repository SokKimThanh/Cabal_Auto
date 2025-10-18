# Documentation Directory

This directory contains all project documentation, summaries, and sprint records.

**📋 [Xem INDEX.md](INDEX.md)** để tìm tài liệu nhanh / See INDEX.md for quick reference

## 📁 Structure

```
docs/
├── 📄 INDEX.md                          # Chỉ mục đầy đủ / Full index
├── 📄 REORGANIZATION_SUMMARY.md         # Tóm tắt tổ chức / Reorganization summary
├── 📄 HUONG_DAN_NGUOI_MOI.md           # Hướng dẫn người mới / Beginner guide
├── 📄 HOW_TO_USE_TEST_RECOGNITION.md   # Test recognition guide
├── 📂 sprints/                          # Sprint documentation (25 files)
│   ├── sprint15/
│   ├── sprint16/                        # UI Redesign
│   └── sprint18/                        # 4-Tab Reorganization (current)
├── 📂 bugfixes/                         # Bug fixes (1 file)
├── 📂 ux-enhancements/                  # UX improvements (3 files)
└── 📂 translations/                     # Translation docs (5 files)
```

### 📚 Main Documents
- **[INDEX.md](INDEX.md)** - Complete documentation index with quick links
- **[REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)** - How docs are organized
- **[PROJECT_SUMMARY.py](PROJECT_SUMMARY.py)** - Complete project summary script

### 🚀 Current Sprint: Sprint 18 Phase 4
- **Location**: `sprints/sprint18/`
- **Goal**: 4-Tab UI Reorganization (Hunt, Setup, Stats, Help)
- **Progress**: 75% complete (6/8 tasks done)
- **Latest**: Window Selection UX Enhancement ✅

## Sprint Documentation Format

Each sprint includes:
1. **Demo Script** (`sprintXX_demo.py`): 
   - Demonstrates new features
   - Shows usage examples
   - Explains benefits

2. **Summary Document** (`SPRINTXX_SUMMARY.txt`):
   - Technical details
   - Code changes
   - Implementation notes

3. **Complete Guide** (`SPRINTXX_COMPLETE.md`):
   - User-friendly overview
   - Usage instructions
   - Benefits and examples

## Running Documentation Scripts

```bash
# Run project summary
python docs/PROJECT_SUMMARY.py

# Run sprint demos
python docs/sprints/sprint13_demo.py
python docs/sprints/sprint14_demo.py
python docs/sprints/sprint15_demo.py
```

## Contributing Documentation

When adding new sprints or features:
1. Create demo script in `/sprints/`
2. Write technical summary
3. Create user-friendly guide
4. Update PROJECT_SUMMARY.py
5. Update main README.md
