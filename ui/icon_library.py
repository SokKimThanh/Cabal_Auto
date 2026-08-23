class Icons:
    # Scan Icons
    SCAN_FAILED = "scan-failed"
    SCAN_SCREEN = "scan-screen"
    SCANNING = "scaning"
    SCAN_COMPLETE = "scan-complete"

    # General Icons
    APP = "app"
    SETTINGS = "settings"
    DB_SYNC = "db-sync"
    HELP = "help"
    INFO = "info"
    CLOSE = "close"
    WARNING = "warning"

def get_icon_name(name: str) -> str:
    """Return the name for IconHelper mapping."""
    return name

def register_icons(icon_helper):
    """Register all custom icons mapping in IconHelper."""
    mapping = {
        Icons.SCAN_FAILED: ('scan-failed.ico', '❌'),
        Icons.SCAN_SCREEN: ('scan-screen.ico', '🔍'),
        Icons.SCANNING: ('scaning.ico', '⏳'),
        Icons.SCAN_COMPLETE: ('scan-complete.ico', '✅'),

        Icons.APP: ('app.ico', '📱'),
        Icons.SETTINGS: ('settings.ico', '⚙️'),
        Icons.DB_SYNC: ('db-sync.ico', '🔄'),
        Icons.HELP: ('help.ico', '❓'),
        Icons.INFO: ('info.ico', 'ℹ️'),
        Icons.CLOSE: ('close.ico', '✖️'),
        Icons.WARNING: ('warning.ico', '⚠️'),
    }

    for name, (filename, fallback) in mapping.items():
        if name not in icon_helper.icon_map:
            icon_helper.icon_map[name] = (filename, fallback)
