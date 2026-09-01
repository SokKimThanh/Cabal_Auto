# Package
__all__ = ["TargetBarDetector"]


def __getattr__(name):
    if name == "TargetBarDetector":
        from .target_bar_detector import TargetBarDetector
        return TargetBarDetector
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
