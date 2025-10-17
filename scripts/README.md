# Scripts Directory

This directory contains example scripts and legacy automation scripts.

## Scripts

### `main.py`
**⚠️ NOT RECOMMENDED - Use main_safe.py instead**

Simple auto-clicker without safety features.

**Features:**
- Infinite loop clicking
- No hotkeys
- No safety controls

**Why Not Recommended:**
- Can't stop easily (must kill process)
- No failsafe
- No configuration

### `main_safe.py`
**✅ RECOMMENDED for simple clicking**

Safe auto-clicker with hotkeys and configuration.

**Features:**
- F8: Toggle auto on/off
- F7: Pause/resume
- F9: Exit program
- Failsafe: Move mouse to (0,0) to stop
- Reads config from `data/config.json`

**Usage:**
```bash
python scripts/main_safe.py
```

**Config (data/config.json):**
```json
{
  "click": {
    "x": 500,
    "y": 400,
    "interval_sec": 2.0
  },
  "hotkeys": {
    "toggle": "f8",
    "exit": "f9"
  },
  "safety": {
    "failsafe": true,
    "pause_key": "f7"
  }
}
```

### `main_skills.py`
**⚠️ LEGACY - Consider using app_gui.py or auto_hunt.py instead**

Auto-cast skills based on cooldowns.

**Features:**
- Reads skills from `data/skills.json`
- Respects cooldown timers
- Simple rotation system

**Why Legacy:**
- Superseded by skill_runtime.py
- No buff auto-casting
- No GUI configuration
- Limited to attack skills only

**Usage:**
```bash
python scripts/main_skills.py
```

## Recommended Workflow

### For Simple Clicking
```bash
# Use main_safe.py with config.json
python scripts/main_safe.py
```

### For Advanced Hunting
```bash
# Use GUI for full features
python app_gui.py

# Or CLI for headless operation
python auto_hunt.py
```

## Comparison

| Feature | main.py | main_safe.py | main_skills.py | app_gui.py | auto_hunt.py |
|---------|---------|--------------|----------------|------------|--------------|
| Hotkeys | ❌ | ✅ | ❌ | ✅ | ❌ |
| Config File | ❌ | ✅ | ✅ | ✅ | ✅ |
| Template Matching | ❌ | ❌ | ❌ | ✅ | ✅ |
| Skill Management | ❌ | ❌ | Basic | Advanced | Advanced |
| Buff Auto-Cast | ❌ | ❌ | ❌ | ✅ | ✅ |
| GUI | ❌ | ❌ | ❌ | ✅ | ❌ |
| Logging | ❌ | ❌ | ❌ | ✅ | ✅ |
| Status | ⚠️ Unsafe | ✅ Safe | ⚠️ Legacy | ✅ Recommended | ✅ Recommended |

## Migration Guide

### From main.py to main_safe.py
1. Create `data/config.json` with click coordinates
2. Run `python scripts/main_safe.py`
3. Use F8 to start/stop, F9 to exit

### From main_safe.py to app_gui.py
1. Run `python app_gui.py`
2. Configure hunt settings in GUI
3. Add monsters and templates
4. Configure skills
5. Use Hunt tab for advanced features

### From main_skills.py to app_gui.py
1. Your skills.json is already compatible
2. Run `python app_gui.py`
3. Configure hunt settings
4. Skills will be managed automatically with buff support

## Safety Reminders

### Always:
- Run as Administrator for reliable hotkeys
- Test in safe environment first
- Keep failsafe enabled
- Monitor first run

### Never:
- Run main.py in production
- Disable failsafe without backup stop method
- Run multiple instances simultaneously
- Use on unsupported game versions

## Script Maintenance

### Status:
- `main.py`: Kept for reference only
- `main_safe.py`: Maintained for simple use cases
- `main_skills.py`: Legacy, may be deprecated in future

### Future:
- Consider removing main.py in next major version
- Migrate main_skills.py users to app_gui.py
- Keep main_safe.py for backward compatibility

## Contributing

When adding new scripts:
1. Add to this README
2. Include safety features (hotkeys, failsafe)
3. Use configuration files
4. Document usage clearly
5. Consider if it should be in main app instead
