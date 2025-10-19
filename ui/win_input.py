# Shim module to allow legacy imports: from win_input import ...
try:
    from lib.system.win_input import *  # noqa: F401,F403
except Exception:  # pyright: ignore[reportMissingImports]
    pass
