# Library Directory

This directory contains all reusable library modules and helper functions.

## Core Modules

### `win_input.py`
Windows SendInput wrapper for sending keyboard input.

**Functions:**
- `tap(key, hold_ms)`: Send key press with optional hold time
- Uses ctypes and Windows SendInput API
- More reliable than PyAutoGUI for game input

**Usage:**
```python
from lib.win_input import tap

tap('1')  # Quick tap
tap('5', 500)  # Hold for 500ms
```

### `hunt_logger.py`
Centralized logging system with dual output formats.

**Features:**
- Text logging: hunt.log (human-readable)
- JSON logging: hunt_structured.jsonl (machine-readable)
- Session tracking
- State change logging
- Rotating file handler (10MB, 5 backups)

**Usage:**
```python
from lib.hunt_logger import get_hunt_logger

logger = get_hunt_logger()
logger.log_hunt_start(config)
logger.log_match(template_name, box, threshold, confidence)
logger.log_lost(template_name, monster_name, duration)
logger.log_hunt_stop(reason)
```

### `template_matcher.py`
Unified template matching interface supporting OpenCV and PyAutoGUI.

**Features:**
- Auto-select best method (OpenCV preferred)
- Accurate confidence values (0.0-1.0)
- Graceful fallback to PyAutoGUI
- Region and grayscale support

**Usage:**
```python
from lib.template_matcher import locate_template

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

### `timing_calculator.py`
Data-driven timing optimization calculator.

**Features:**
- Calculate optimal lost_timeout and attack_duration
- Attack speed presets (slow/normal/fast/very_fast)
- Safety margins (50% for timeout, 20% for duration)
- Localized output formatting (EN/VI)

**Usage:**
```python
from lib.timing_calculator import calculate_timing, format_timing_recommendation

rec = calculate_timing(
    monster_hp=10000,
    damage_per_hit=500,
    attacks_per_second=2.0
)

print(f"Lost timeout: {rec.lost_timeout_sec}s")
print(f"Attack duration: {rec.attack_min_duration_sec}s")
```

### `skill_runtime.py`
Intelligent skill management system with buff auto-casting.

**Features:**
- Separate attack/buff lanes
- Round-robin attack rotation
- Auto-refresh buffs before expiration
- Cooldown tracking
- Per-skill timing configuration

**Usage:**
```python
from lib.skill_runtime import SkillRuntime
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

### `skill_migrator.py`
Schema migration tool for skills.json.

**Features:**
- Add new schema fields
- Copy images to project
- Generate unique filenames
- Create automatic backups
- Validate schema

**Usage:**
```python
from lib.skill_migrator import SkillMigrator

migrator = SkillMigrator('data/skills.json')
migrator.migrate()
migrator.print_summary()
```

## Module Dependencies

```
win_input.py
  └─ (no dependencies)

hunt_logger.py
  └─ (logging, json, pathlib)

template_matcher.py
  ├─ opencv-python (optional, preferred)
  └─ pyautogui (fallback)

timing_calculator.py
  └─ (dataclasses, math)

skill_runtime.py
  └─ (dataclasses, time, typing, json)

skill_migrator.py
  ├─ skill_runtime.py
  └─ (pathlib, json, shutil)
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
