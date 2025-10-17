# Data Directory

This directory contains all configuration files and data storage.

## Configuration Files

### `config.json`
Basic clicker configuration (legacy, used by scripts/main_safe.py).

**Contents:**
- Click coordinates
- Intervals
- Hotkeys
- Safety settings

### `hunt_config.json`
Main hunt configuration used by app_gui.py and auto_hunt.py.

**Contents:**
- Window settings (title, PID, HWND)
- Target key and attack keys
- Timing parameters (intervals, timeouts)
- Template configurations
- Window bounds
- Skill slots

### `monsters.json`
Monster database with multi-template support.

**Schema:**
```json
{
  "name": "Monster Name",
  "description": "Optional description",
  "hp": 10000,
  "damage_per_hit": 500,
  "window_bounds": {"left": 0, "top": 0, "width": 1920, "height": 1080},
  "templates": [
    {
      "name": "template_name",
      "path": "assets/images/monsters/monster.png",
      "threshold": 0.85,
      "region_strategy": "window",
      "region": {"left": 0, "top": 0, "width": 800, "height": 600}
    }
  ]
}
```

### `skills.json`
Skills database with buff/attack support.

**Schema:**
```json
{
  "name": "Skill Name",
  "key": "1",
  "type": "attack" | "buff",
  "cooldown": 1.9,
  "cast_time": 1.7,
  "duration_sec": 60.0,
  "pre_refresh_sec": 5.0,
  "hold_ms": null,
  "image": "assets/images/skills/skill_name_timestamp.png"
}
```

### `skills.json.backup`
Automatic backup created during skills migration.

## Important Notes

### Path References
All paths in JSON files should use:
- **Relative paths** for project assets: `assets/images/monsters/...`
- **Absolute paths** only if necessary (not recommended)

### Backup Strategy
- `skills.json.backup` is created automatically during migration
- Manual backups recommended before major changes
- Git tracks these files (except backups in .gitignore)

### Loading Order
1. app_gui.py loads configs on startup
2. auto_hunt.py loads hunt_config.json
3. Configs can be edited in GUI or manually
4. Changes saved immediately when using GUI

## File Access

### From Main Scripts
```python
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / 'data' / 'config.json'
HUNT_CONFIG_PATH = Path(__file__).parent / 'data' / 'hunt_config.json'
MONSTER_DB_PATH = Path(__file__).parent / 'data' / 'monsters.json'
SKILL_DB_PATH = Path(__file__).parent / 'data' / 'skills.json'
```

### From Library Modules
```python
from pathlib import Path

# Assuming lib/ is sibling to data/
DATA_DIR = Path(__file__).parent.parent / 'data'
CONFIG_PATH = DATA_DIR / 'config.json'
```

## Configuration Management

### Editing Configs
1. **GUI Method** (Recommended):
   - Use app_gui.py GUI to edit
   - Changes saved automatically
   - Validation included

2. **Manual Method**:
   - Edit JSON files directly
   - Validate JSON syntax
   - Restart application to reload

### Default Values
If config files don't exist, app_gui.py creates them with defaults:
- hunt_config.json: Basic hunt settings
- monsters.json: Empty array
- skills.json: Empty array

## Data Integrity

### Validation
- JSON syntax checked on load
- Schema validation in GUI
- Error messages for invalid data

### Recovery
- Backup files kept for recovery
- Git history for version control
- Manual backups recommended

## Migration Notes

### Sprint 11 Migration
- Added `duration_sec`, `pre_refresh_sec`, `hold_ms` to skills
- Created skills.json.backup
- Copied images to assets/images/skills/
- Updated paths to relative

### Future Migrations
- Use skill_migrator.py (in lib/)
- Always create backups first
- Test after migration
