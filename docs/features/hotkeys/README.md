# Features - Global Hotkeys

Tài liệu về hệ thống global hotkeys.

## Documentation

- **[GLOBAL_HOTKEY_MIGRATION.md](GLOBAL_HOTKEY_MIGRATION.md)** - Migration guide cho global hotkeys
- **[HOTKEY_F8_TOGGLE.md](HOTKEY_F8_TOGGLE.md)** - F8 toggle functionality

## Architecture
See [Architecture Documentation](../../architecture/GLOBAL_HOTKEY_ARCHITECTURE.md) for system architecture.

## Registered Hotkeys

### Hunt Control
- `Ctrl+Shift+R` - Start hunt
- `Ctrl+Shift+E` - Stop hunt

### Wizards & Managers
- `Ctrl+Shift+N` - Setup Wizard (beginner mode only)
- `Ctrl+Shift+L` - Library Manager
- `Ctrl+Shift+V` - Vision Wizard (Sprint 22)

### Vision Menu (Sprint 22)
- `Ctrl+Alt+S` - Scan region
- `Ctrl+T` - Add template
- `Ctrl+Shift+T` - Manage templates
- `Ctrl+Shift+O` - Toggle overlay

## Configuration

Hotkeys can be configured in Setup tab:
- Enable/disable global hotkeys
- Customize key combinations
- Fallback bindings (when keyboard module unavailable)

## Technical Details

### Registration
- Uses `keyboard` module for global hotkeys
- Fallback to Tkinter `bind_all()` when keyboard unavailable
- Non-blocking callbacks
- Clean unregistration on exit

### Error Handling
- Diagnostic UI for import errors
- Retry mechanism
- Help links for troubleshooting
