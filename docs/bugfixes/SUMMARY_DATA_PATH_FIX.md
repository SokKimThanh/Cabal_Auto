# Fix: Data Path Issues in ui/ Scripts

**Date:** October 19, 2025  
**Commit:** Fix data path resolution in ui/setup_wizard.py and ui/auto_hunt.py

## Summary

Fixed incorrect data directory paths in scripts located in the `ui/` subdirectory. These scripts were looking for `ui/data/` instead of the correct `data/` location at project root.

## Files Changed

1. **ui/setup_wizard.py** (2 fixes)
   - Line 572: monsters.json path
   - Line 660: skills.json path

2. **ui/auto_hunt.py** (2 fixes)
   - Line 12: hunt_config.json path
   - Line 235: skills.json path

## Changes

### Before (Incorrect)
```python
# Looking in ui/data/ (doesn't exist)
Path(__file__).parent / 'data' / 'file.json'
os.path.join(os.path.dirname(__file__), 'data', 'file.json')
```

### After (Correct)
```python
# Looking in data/ at project root (correct)
Path(__file__).parent.parent / 'data' / 'file.json'
os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'file.json')
```

## Impact

✅ **Setup Wizard** - Can now load monsters and skills for Step 3 and Step 4  
✅ **Auto Hunt** - Can now load configuration and skill data at runtime  
✅ **User Experience** - First-time setup and hunting features work correctly

## Directory Structure

```
E:\Cabal_Auto\
├── app_gui.py          ← Root level (paths already correct)
├── data\               ← Data folder at root!
│   ├── config.json
│   ├── hunt_config.json
│   ├── monsters.json   (3 monsters)
│   └── skills.json     (5 skills)
└── ui\                 ← Scripts here need parent.parent
    ├── auto_hunt.py    ← Fixed!
    └── setup_wizard.py ← Fixed!
```

## Testing

All paths verified:
- `E:\Cabal_Auto\data\monsters.json` ✅ (3 items)
- `E:\Cabal_Auto\data\skills.json` ✅ (5 items)
- `E:\Cabal_Auto\data\hunt_config.json` ✅
- Setup wizard runs without "file not found" errors
- Auto hunt can initialize skill runtime

## Documentation

Full bugfix report: `docs/bugfixes/BUGFIX_SETUP_WIZARD_DATA_PATH.md`
