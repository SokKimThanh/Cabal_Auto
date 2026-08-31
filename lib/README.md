# Library Directory (`lib/`)

Thư mục này chứa tất cả các module thư viện tái sử dụng được và các hàm hỗ trợ của ứng dụng.

## 📁 Cấu trúc thư mục

```
lib/
├── system/           # System-level utilities
│   ├── win_input.py       # Windows keyboard input
│   └── hunt_logger.py     # Enhanced logging system
├── vision/           # Computer vision modules
│   ├── template_matcher.py  # Template matching engine
│   └── vision_engine.py     # Vision processing core
├── features/         # Game features
│   ├── skills/           # Skill system
│   │   ├── runtime.py         # Skill execution runtime
│   │   ├── skill_stats.py     # Skill statistics
│   │   └── migrator.py        # Skills data migration
│   ├── skill_rotation/   # Skill rotation system
│   │   ├── builder.py         # Rotation builder
│   │   └── ui_integration.py  # UI integration
│   └── timing/           # Timing calculations
│       └── calculator.py      # Timing calculator
├── ui/               # UI components
│   ├── tooltip.py         # i18n tooltip system
│   ├── icon_helper.py     # Icon management with emoji fallback
│   ├── library_manager.py # Library manager window
│   ├── button_styles.py   # Button styling utilities
│   └── capture_helper.py  # Screen capture helper
├── i18n/             # Internationalization
│   └── translations.py    # Translation strings
├── data/             # Data files
│   ├── config.json        # App configuration
│   ├── hunt_config.json   # Hunt settings
│   ├── monsters.json      # Monster database
│   ├── skills.json        # Skills database
│   └── vision_*.json      # Vision configs
├── i18n.py           # i18n registry
└── ui_style.py       # Global UI styles
```

## 🔧 Core Modules

### System Layer (`lib/system/`)

#### `win_input.py`
Windows SendInput wrapper cho việc gửi input bàn phím.

**Tính năng:**
- Sử dụng ctypes và Windows SendInput API
- Đáng tin cậy hơn PyAutoGUI cho game input
- Hỗ trợ các phím thông thường (digits, letters, F1-F24, SPACE, ENTER, ESC, TAB, SHIFT, CTRL, ALT, ARROWS)
- Hỗ trợ giữ phím (hold_ms)

**Sử dụng:**
```python
from lib.system.win_input import tap

tap('1')        # Nhấn phím nhanh
tap('5', 500)   # Giữ phím 500ms
```

**Import trong app:**
- `app_gui.py`: Line 52
- `ui/auto_hunt.py`: Line 7

#### `hunt_logger.py`
Hệ thống logging tập trung với dual output formats.

**Tính năng:**
- Text logging: hunt.log (human-readable)
- JSON logging: hunt_structured.jsonl (machine-readable)
- Session tracking
- State change logging
- Rotating file handler (10MB, 5 backups)

**Sử dụng:**
```python
from lib.system.hunt_logger import get_hunt_logger

logger = get_hunt_logger()
logger.log_hunt_start(config)
logger.log_match(template_name, box, threshold, confidence)
logger.log_lost(template_name, monster_name, duration)
logger.log_hunt_stop(reason)
```

**Import trong app:**
- `app_gui.py`: Line 53
- `ui/auto_hunt.py`: Line 8

### Vision Layer (`lib/vision/`)

#### `template_matcher.py`
Unified template matching interface hỗ trợ OpenCV và PyAutoGUI.

**Tính năng:**
- Auto-select best method (OpenCV preferred)
- Accurate confidence values (0.0-1.0)
- Graceful fallback to PyAutoGUI
- Region và grayscale support

**Sử dụng:**
```python
from lib.vision.template_matcher import locate_template

result = locate_template(
    template_path='assets/images/monsters/dragon.png',
    threshold=0.85,
    region=(0, 0, 1920, 1080),
    grayscale=True
)

if result:
    box, confidence = result
    print(f"Found at {box} with confidence {confidence:.3f}")
```

**Import trong app:**
- `app_gui.py`: Line 37
- `ui/auto_hunt.py`: Line 9
- `ui/windows/library_manager.py`: Line 61

### Features Layer (`lib/features/`)

#### `features/timing/calculator.py`
Data-driven timing optimization calculator.

**Tính năng:**
- Tính toán optimal lost_timeout và attack_duration
- Attack speed presets (slow/normal/fast/very_fast)
- Safety margins (50% for timeout, 20% for duration)
- Localized output formatting (EN/VI)
- Tính toán thêm: attack_press_ms, target_cycle_delay, search_interval, attack_interval

**Sử dụng:**
```python
from lib.features.timing.calculator import calculate_timing

rec = calculate_timing(
    monster_hp=10000,
    damage_per_hit=500,
    attacks_per_second=2.0
)

print(f"Lost timeout: {rec.lost_timeout_sec}s")
print(f"Attack duration: {rec.attack_min_duration_sec}s")
```

**Import trong app:**
- `app_gui.py`: Line 54-58

#### `features/skills/runtime.py`
Intelligent skill management system với buff auto-casting.

**Tính năng:**
- Separate attack/buff lanes
- Round-robin attack rotation
- Auto-refresh buffs before expiration
- Cooldown tracking
- Per-skill timing configuration

**Sử dụng:**
```python
from lib.features.skills.runtime import SkillRuntime
import time

runtime = SkillRuntime(skills_data)

# Every hunt loop
now = time.time()

# Cast buffs (always)
buff_key = runtime.get_buff_to_cast(now)
if buff_key:
    tap(buff_key)
    runtime.mark_cast(buff_key, now)

# Cast attacks (when have target)
if have_target:
    attack_key = runtime.get_attack_to_cast(now)
    if attack_key:
        tap(attack_key)
        runtime.mark_cast(attack_key, now)
```

**Import trong app:**
- `ui/auto_hunt.py`: Line 10

#### `features/skills/skill_stats.py`
Skill statistics và validation utilities.

**Tính năng:**
- Load/save skill library
- Validate skill data
- Track skill usage statistics

**Import trong app:**
- `app_gui.py`: Line 59-61

#### `features/skills/migrator.py`
Schema migration tool cho skills.json.

**Tính năng:**
- Add new schema fields
- Copy images to project
- Generate unique filenames
- Create automatic backups
- Validate schema

**Sử dụng:**
```python
from lib.features.skills.migrator import SkillMigrator

migrator = SkillMigrator('lib/data/skills.json')
migrator.migrate()
migrator.print_summary()
```

### UI Layer (`ui/`)

#### `ui/tooltip.py`
Centralized tooltip utilities với i18n support.

**Tính năng:**
- Tooltips được dịch tại thời điểm hiển thị
- Organize theo namespace (screen/feature)
- Lazy loading translations
- Delay configuration

**Sử dụng:**
```python
from ui.helpers.tooltip import attach_i18n_tooltip

attach_i18n_tooltip(
    widget, 
    key='tip_apply_all', 
    ns='library_manager', 
    lang_provider=lambda: self.lang
)
```

**Import trong app:**
- `app_gui.py`: Line 39
- `ui/setup_wizard.py`: Line 28
- `ui/windows/library_manager.py`: Line 48

#### `ui/icon_helper.py`
Icon management với automatic fallback to Unicode emoji.

**Tính năng:**
- Load PNG icons từ assets/images/icons/
- Automatic fallback to Unicode emoji
- Caching for performance
- UTF-8 support
- Handle PyInstaller frozen state

**Sử dụng:**
```python
from ui.helpers.icon_helper import get_icon_helper

icon_helper = get_icon_helper()
add_icon = icon_helper.get_icon('add', fallback='➕')
```

**Import trong app:**
- `app_gui.py`: Line 622
- `ui/setup_wizard.py`: Line 34
- `ui/windows/library_manager.py`: Line 44-46

#### `ui/library_manager.py`
Library Manager Window - Quản lý tập trung cho Monsters, Skills, và Timing.

**Tính năng:**
- **Monster Library**: CRUD operations, templates, priorities
- **Skill Library**: CRUD operations, cooldowns, types
- **Timing Calculator**: Auto-calculate và apply recommended timing settings
- Template matching test
- Region capture và auto-detect
- Icon management với drag & drop
- Apply All/Clear All operations
- i18n support (EN/VI)

**Sử dụng:**
```python
from ui.windows.library_manager import LibraryManagerWindow

window = LibraryManagerWindow(parent, lang='vi', reload_callback=callback)
```

**Import trong app:**
- `app_gui.py`: Line 2869
- `ui/setup_wizard.py`: Line 1461

#### `ui/button_styles.py`
Button styling utilities và color presets.

**Tính năng:**
- Color presets (GREEN, RED, ORANGE, BLUE, PURPLE, etc.)
- Button configurations
- Label color utilities
- Consistent styling across app

**Sử dụng:**
```python
from ui.helpers.button_styles import get_button_config

config = get_button_config('save')  # returns green button config
button = tk.Button(parent, **config)
```

**Import trong app:**
- `app_gui.py`: Lines 1554, 1673, 7321

#### `ui/capture_helper.py`
Screen capture helper cho region capture.

**Tính năng:**
- Capture specific region
- Save to file
- PIL ImageGrab integration

**Import trong app:**
- `app_gui.py`: Line 48

### i18n Layer

#### `i18n.py`
Simple i18n registry cho toàn bộ app.

**Tính năng:**
- `register(namespace, lang, mapping)`: Đăng ký translations
- `set_default_lang(lang)`: Set default language
- `t(key, *, ns=None, lang=None, default=None)`: Lấy translation
- `get_lang()`: Get current language

**Sử dụng:**
```python
from lib.i18n import t, set_default_lang, register

# Set language
set_default_lang('vi')

# Register translations
register('my_feature', 'vi', {
    'hello': 'Xin chào',
    'goodbye': 'Tạm biệt'
})

# Get translation
text = t('hello', ns='my_feature')  # Returns: 'Xin chào'
```

**Import trong app:**
- `app_gui.py`: Line 40-46
- `ui/setup_wizard.py`: Line 41-59

#### `i18n/translations.py`
Translation strings cho tất cả features.

**Namespaces:**
- `GLOBAL_TRANSLATIONS`: Common UI strings
- `LIBRARY_MANAGER_TRANSLATIONS`: Library Manager window
- `SETUP_WIZARD_TRANSLATIONS`: Setup Wizard

### UI Style

#### `ui_style.py`
Global UI style constants.

**Tính năng:**
- Color palette
- Font configurations
- Spacing constants
- Border/radius styles

**Sử dụng:**
```python
from lib.ui_style import UIStyle as UI

button = tk.Button(
    parent,
    bg=UI.BTN_GREEN_BG,
    fg=UI.BTN_GREEN_FG,
    font=UI.FONT_NORMAL
)
```

**Import trong app:**
- `app_gui.py`: Line 62
- `ui/windows/library_manager.py`: Line 13

## 📊 Module Dependencies

```
System Layer:
  win_input.py
    └─ ctypes, wintypes
  
  hunt_logger.py
    └─ logging, json, pathlib, datetime

Vision Layer:
  template_matcher.py
    ├─ opencv-python (optional, preferred)
    ├─ numpy (optional)
    └─ pyautogui (fallback)
  
  vision_engine.py
    └─ template_matcher.py

Features Layer:
  timing/calculator.py
    └─ dataclasses, math
  
  skills/runtime.py
    └─ dataclasses, time, typing
  
  skills/skill_stats.py
    └─ json, pathlib
  
  skills/migrator.py
    ├─ skills/runtime.py
    └─ pathlib, json, shutil
  
  skill_rotation/builder.py
    └─ typing, dataclasses
  
  skill_rotation/ui_integration.py
    └─ skill_rotation/builder.py

UI Layer:
  ui/tooltip.py
    ├─ tkinter
    └─ i18n.py
  
  ui/icon_helper.py
    ├─ tkinter
    ├─ PIL (optional)
    └─ pathlib
  
  ui/library_manager.py
    ├─ tkinter, ttk
    ├─ i18n.py
    ├─ ui_style.py
    ├─ ui/tooltip.py
    ├─ ui/icon_helper.py
    ├─ ui/capture_helper.py
    ├─ vision/template_matcher.py
    └─ features/timing/calculator.py
  
  ui/button_styles.py
    └─ (constants only)
  
  ui/capture_helper.py
    └─ PIL ImageGrab

i18n Layer:
  i18n.py
    └─ typing
  
  i18n/translations.py
    └─ (constants only)

Style:
  ui_style.py
    └─ (constants only)
```

## 🔄 Import Patterns

### Từ app_gui.py:
```python
from lib.vision.template_matcher import locate_template
from lib.i18n.translations import GLOBAL_TRANSLATIONS
from ui.helpers.tooltip import attach_i18n_tooltip
from lib.i18n import (set_default_lang, t, get_lang, ...)
from ui.helpers.capture_helper import capture_region_and_save
from lib.system.win_input import tap
from lib.system.hunt_logger import get_hunt_logger
from lib.features.timing.calculator import (calculate_timing, ...)
from lib.features.skills.skill_stats import (load_skill_library, ...)
from lib.ui_style import UIStyle as UI
from ui.helpers.icon_helper import get_icon_helper
from ui.helpers.button_styles import get_button_config
from ui.windows.library_manager import LibraryManagerWindow
```

### Từ ui/auto_hunt.py:
```python
from lib.system.win_input import tap
from lib.system.hunt_logger import get_hunt_logger
from lib.vision.template_matcher import locate_template
from lib.features.skills.runtime import SkillRuntime
```

### Từ ui/setup_wizard.py:
```python
from ui.helpers.tooltip import attach_i18n_tooltip
from ui.helpers.icon_helper import get_icon_helper
from lib.i18n import (set_default_lang, t, ...)
import lib.i18n.translations # self-registers
from ui.windows.library_manager import LibraryManagerWindow
```

## 📦 Data Files (`lib/data/`)

- **config.json**: App configuration
- **hunt_config.json**: Hunt settings (timing, attack, target)
- **monsters.json**: Monster database với templates
- **skills.json**: Skills database (attack/buff skills)
- **vision_region.json**: Vision region configurations
- **vision_templates.json**: Template matching configurations

## 🎯 Best Practices

1. **Import Patterns**: Always use absolute imports từ `lib.`
   ```python
   # Good
   from lib.system.win_input import tap
   
   # Bad
   from system.win_input import tap
   ```

2. **i18n**: Tự động register translations qua module import hoặc DB hydration
   ```python
   # Chỉ cần import data dictionary, module sẽ tự đăng ký hoặc được load từ DB
   import lib.i18n.my_screen_translations
   ```

3. **Error Handling**: Always handle optional dependencies
   ```python
   try:
       from PIL import Image
   except ImportError:
       Image = None
   ```

4. **Configuration**: Load từ `lib/data/` directory
   ```python
   config_path = Path(__file__).parent / 'data' / 'config.json'
   ```

5. **Logging**: Use centralized hunt_logger
   ```python
   from lib.system.hunt_logger import get_hunt_logger
   logger = get_hunt_logger()
   ```

## Import Conventions

### From Main Scripts (app_gui.py, auto_hunt.py)
```python
from lib.win_input import tap
from lib.hunt_logger import get_hunt_logger
from lib.template_matcher import locate_template
from lib.timing_calculator import calculate_timing
from lib.skill_runtime import SkillRuntime
```

### From Other Library Modules
```python
# Use relative imports if in same directory
from .win_input import tap

# Or absolute imports
from lib.win_input import tap
```

## Error Handling

All modules include:
- Try-except blocks for external dependencies
- Graceful fallbacks (e.g., PyAutoGUI if no OpenCV)
- Clear error messages
- Logging for debugging

## Testing

Test coverage:
- ✅ template_matcher: tests/test_template_matcher_integration.py
- ✅ OpenCV comparison: tests/opencv_test.py
- ⏳ Other modules: Manual testing via main scripts

## Performance

Optimizations:
- OpenCV preferred for speed (~100-115ms)
- Grayscale matching when possible
- Efficient cooldown tracking
- Minimal I/O operations

## Future Enhancements

Potential additions:
- skill_preset.py: Preset skill configurations
- combat_analyzer.py: Combat statistics
- buff_coordinator.py: Multiple buff timing
- macro_recorder.py: Record action sequences

## Contributing

When adding new library modules:
1. Add to this README
2. Include docstrings
3. Add type hints
4. Write tests if possible
5. Update import examples
6. Document dependencies
