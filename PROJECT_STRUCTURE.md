# Project Structure

Tài liệu này mô tả cấu trúc thư mục của dự án Cabal Auto Hunt.

**Last Updated:** 2025-10-23

---

## 📁 Root Directory Structure

```
Cabal_Auto/
├── 📄 app_gui.py              # Main GUI application entry point
├── 📄 requirements.txt        # Python dependencies
├── 📄 pytest.ini             # Pytest configuration
├── 📄 CHANGELOG.md           # Project changelog
├── 📄 README.md              # Main project documentation
├── 📄 run.bat                # Quick launcher (wrapper)
├── ⚙️ .editorconfig          # Editor configuration for code consistency
├── ⚙️ .gitignore             # Git ignore rules
├── ⚙️ .flake8                # Flake8 linting configuration
│
├── 📂 assets/                # Static assets
│   ├── images/              # Images for templates, icons, etc.
│   └── documents/           # Documentation assets
│
├── 📂 config/                # Configuration files
│   ├── bot_config.json      # Bot configuration
│   └── README.md            # Config documentation
│
├── 📂 docs/                  # Documentation
│   ├── INDEX.md             # Documentation index
│   ├── README.md            # Docs overview
│   ├── architecture/        # Architecture documentation
│   ├── guides/              # User guides and tutorials
│   ├── features/            # Feature documentation
│   ├── sprints/             # Sprint planning and reports
│   ├── notes/               # Personal notes (gitignored)
│   │   ├── README.md
│   │   └── *.txt            # Note files (gitignored)
│   └── archive/             # Archived documentation
│
├── 📂 lib/                   # Main source code library
│   ├── __init__.py
│   ├── i18n.py              # Internationalization
│   ├── ui_style.py          # UI styling utilities
│   ├── data/                # Data files (monsters, skills, configs)
│   ├── features/            # Feature implementations
│   │   ├── hunt/           # Auto hunt features
│   │   ├── skills/         # Skill management
│   │   └── ...
│   ├── i18n/               # Translation files
│   ├── system/             # System utilities
│   ├── ui/                 # UI components
│   └── vision/             # Computer vision engine
│
├── 📂 logs/                  # Log files
│   ├── hunt_structured.jsonl
│   └── README.md
│
├── 📂 scripts/               # Utility scripts
│   ├── launchers/           # Application launchers
│   │   ├── run.bat
│   │   ├── run_venv.bat
│   │   ├── run_venv.ps1
│   │   └── README.md
│   ├── main.py              # Main script
│   ├── main_safe.py         # Safe mode script
│   └── ...
│
├── 📂 tests/                 # Test suite
│   ├── conftest.py          # Pytest configuration
│   ├── README.md            # Test documentation
│   ├── QUICK_REFERENCE.md   # Quick test reference
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── vision/              # Vision system tests
│   ├── sprints/             # Sprint-specific tests
│   └── samples/             # Test sample data
│
├── 📂 tmp/                   # Temporary files (gitignored)
│   └── captures/            # Screenshot captures
│
└── 📂 ui/                    # Legacy UI files (to be refactored)
    ├── auto_hunt.py
    ├── setup_wizard.py
    └── ...
```

---

## 🎯 Key Directories Explained

### `/lib` - Core Library
Thư mục chứa toàn bộ source code chính của ứng dụng.

**Subdirectories:**
- `data/` - JSON data files (monsters, skills, hunt configs)
- `features/` - Feature implementations (hunt, skills, etc.)
- `i18n/` - Translation files (EN, VI)
- `system/` - System utilities (hotkeys, input, etc.)
- `ui/` - UI components and dialogs
- `vision/` - Computer vision engine for template matching

### `/tests` - Test Suite
Structured test organization following pytest best practices.

**Categories:**
- `unit/` - Fast, isolated unit tests
- `integration/` - Integration tests
- `vision/` - Vision system tests (basic + performance)
- `sprints/` - Sprint-specific feature tests
- `manual/` - Manual testing scripts

**Markers:**
```python
pytest -m unit              # Run unit tests only
pytest -m vision            # Run vision tests
pytest -m "not windows"     # Skip Windows-specific tests
```

### `/docs` - Documentation
Comprehensive project documentation.

**Structure:**
- `architecture/` - System architecture docs
- `guides/` - User guides and tutorials (e.g., PYTEST_TEMPLATE_CI_CD.md)
- `features/` - Feature specifications
- `sprints/` - Sprint planning and retrospectives
- `notes/` - Personal development notes (gitignored)

### `/scripts` - Utility Scripts

**`/scripts/launchers`** - Application launchers
- `run.bat` - Simple hardcoded launcher
- `run_venv.bat` - Smart launcher with auto-detection
- `run_venv.ps1` - PowerShell launcher (most features)

**Other scripts:**
- `main.py` - Direct Python entry point
- `convert_training_tests.py` - Test conversion utilities
- `restructure_project.py` - Project restructuring tools

### `/config` - Configuration
Application configuration files.

- `bot_config.json` - Main bot configuration
- Schema and validation documentation

---

## 🚀 Quick Start

### Running the Application

**Method 1: Quick Launch (Windows)**
```cmd
run.bat
```

**Method 2: Flexible Launch**
```cmd
# Command Prompt
scripts\launchers\run_venv.bat

# PowerShell
.\scripts\launchers\run_venv.ps1
```

**Method 3: Python Direct**
```cmd
python app_gui.py
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# CI/CD mode (skip Windows/GUI)
pytest -m "not windows and not gui"

# Specific test file
pytest tests/unit/test_timing_calculator_ui.py -v
```

### Development Setup

1. **Create virtual environment:**
   ```cmd
   python -m venv .venv
   ```

2. **Activate venv:**
   ```cmd
   # PowerShell
   .\.venv\Scripts\Activate.ps1
   
   # Command Prompt
   .venv\Scripts\activate.bat
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run application:**
   ```cmd
   python app_gui.py
   ```

---

## 📝 Notes

### Gitignored Items
- `__pycache__/` - Python cache
- `.pytest_cache/` - Pytest cache
- `tmp/`, `tmp_*/` - Temporary directories
- `venv/`, `.venv/` - Virtual environments

### Backward Compatibility
- Root `run.bat` redirects to `scripts/launchers/run_venv.bat`
- Legacy UI files refactored into new `/ui` structure (`ui/helpers`, `ui/windows`, `ui/utils`, `ui/components`)

---

## 🔄 Recent Changes (2025-10-23)

1. ✅ Reorganized launchers into `scripts/launchers/`
2. ✅ Removed internal notes folder (`docs/notes/`) from repo (gitignored)
3. ✅ Enhanced `.gitignore` with project-specific rules
4. ✅ Added `.editorconfig` for code consistency
5. ✅ Created structured documentation

---

**See Also:**
- [Main README](../README.md)
- [Test Documentation](../tests/README.md)
- [Architecture Docs](../docs/architecture/README.md)
