# Shim module to allow legacy imports: from template_matcher import ...
# Re-export symbols from lib.template_matcher
try:
    from lib.template_matcher import *  # noqa: F401,F403
except Exception:  # pyright: ignore[reportMissingImports]
    pass
