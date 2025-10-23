# Python Coding Guidelines for AI Assistant

**Version**: 1.0.0  
**Date**: October 23, 2025  
**Status**: ACTIVE & ENFORCED  
**Applies to**: All Python code written by AI Assistant

---

## 🎯 Core Principles

These guidelines are **mandatory** and must be followed for every line of Python code written. No exceptions.

---

## 📋 The 7 Golden Rules

### Rule 1: Always Check Data Types Before Use

**Requirement**: Type hints + runtime validation

```python
# ✅ CORRECT
def process_data(data: Optional[List[str]] = None) -> List[str]:
    if data is None:
        data = []
    
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data)}")
    
    return [item.upper() for item in data if item]

# ❌ WRONG
def process_data(data):
    return [item.upper() for item in data]  # Crash if None!
```

**Checklist**:
- [ ] All function parameters have type hints
- [ ] All return types are specified
- [ ] Input validation before use
- [ ] Proper error messages with actual types

---

### Rule 2: Never Call Attributes/Methods on None

**Requirement**: Explicit None checks before access

```python
# ✅ CORRECT
window_info = manager.get_window_info(hwnd)
if window_info is not None:
    title = window_info.title
    width = window_info.rect['width']
else:
    logger.error("Window not found")
    return None

# ❌ WRONG
window_info = manager.get_window_info(hwnd)
title = window_info.title  # AttributeError if None!
```

**Checklist**:
- [ ] Check `is not None` before accessing attributes
- [ ] Check `is not None` before calling methods
- [ ] Early return on None with proper logging
- [ ] Use Optional[T] type hints for nullable types

---

### Rule 3: Pass Complete and Correct Arguments

**Requirement**: Read function signature, pass all required args with correct types

```python
# ✅ CORRECT
def match_templates(
    self,
    frame: np.ndarray,
    roi: Optional[Tuple[int, int, int, int]] = None,
    templates: Optional[List[str]] = None,
    max_results: int = 10
) -> List[Detection]:
    pass

# Call with proper arguments
results = self.match_templates(
    frame=current_frame,
    roi=(10, 10, 100, 100),  # x, y, w, h - all 4 values
    templates=["temp1", "temp2"],
    max_results=5
)

# ❌ WRONG
results = self.match_templates(
    frame=current_frame,
    roi=(10, 10),  # Missing w, h!
    templates="temp1"  # Wrong type, should be List!
)
```

**Checklist**:
- [ ] Read function signature before calling
- [ ] Pass all required arguments
- [ ] Use correct types for each argument
- [ ] Use keyword arguments for clarity

---

### Rule 4: Call Instance and Static Methods Correctly

**Requirement**: Instance via `self`/instance, static via `ClassName`

```python
class WindowManager:
    def find_window(self, title: str) -> Optional[int]:
        """Instance method"""
        pass
    
    @staticmethod
    def validate_hwnd(hwnd: int) -> bool:
        """Static method"""
        pass

# ✅ CORRECT - Instance method
manager = WindowManager()
hwnd = manager.find_window("Game")

# ✅ CORRECT - Static method
is_valid = WindowManager.validate_hwnd(hwnd)

# ❌ WRONG - Instance method via class
hwnd = WindowManager.find_window("Game")  # Missing self!

# ❌ WRONG - Static via instance (confusing)
is_valid = manager.validate_hwnd(hwnd)
```

**Checklist**:
- [ ] Instance methods: Always create instance first
- [ ] Instance methods: Call via `self` or `instance`
- [ ] Static methods: Call via `ClassName`
- [ ] No confusion between instance and static

---

### Rule 5: Avoid Unnecessary Duplicate Logic

**Requirement**: Cache results, don't call same function repeatedly

```python
# ✅ CORRECT - Call once, cache result
stats = self.get_capture_stats()
if stats:
    logger.info(f"FPS: {stats['fps']}")
    logger.info(f"Captured: {stats['frames_captured']}")
    logger.info(f"Dropped: {stats['frames_dropped']}")

# ❌ WRONG - Repeated calls
logger.info(f"FPS: {self.get_capture_stats()['fps']}")
logger.info(f"Captured: {self.get_capture_stats()['frames_captured']}")
logger.info(f"Dropped: {self.get_capture_stats()['frames_dropped']}")

# ❌ WRONG - Duplicate logic
if user.is_admin():
    allow_access()
if user.is_admin():  # Already checked above!
    show_admin_menu()
```

**Checklist**:
- [ ] No duplicate function calls in same scope
- [ ] Cache expensive operations
- [ ] No repeated condition checks
- [ ] DRY principle (Don't Repeat Yourself)

---

### Rule 6: Use Stable Library Versions

**Requirement**: Only stable releases, no dev/alpha/beta versions

```powershell
# ✅ CORRECT - Stable versions with binary wheels
python -m pip install opencv-python==4.12.0
python -m pip install numpy==2.3.4
python -m pip install pywin32==311

# ❌ WRONG - Unstable versions
python -m pip install opencv-python==5.0.0.dev
python -m pip install numpy>=2.5.0a1  # Alpha!

# ✅ CORRECT - Use python -m pip
python -m pip install package

# ❌ WRONG - Direct pip call
pip install package
.\venv\Scripts\pip.exe install package
```

**Checklist**:
- [ ] Only stable/release versions (no dev/alpha/beta)
- [ ] Specify exact versions in requirements
- [ ] Use `python -m pip` not direct `pip`
- [ ] Prefer packages with binary wheels

---

### Rule 7: Check Library Namespaces and Versions

**Requirement**: Verify namespace for different library versions

```python
# ✅ CORRECT - Try new API first, fallback to old
try:
    # OpenCV 4.5+ moved trackers to legacy
    tracker = cv2.legacy.TrackerCSRT_create()
except AttributeError:
    # OpenCV < 4.5 compatibility
    tracker = cv2.TrackerCSRT_create()

# ✅ CORRECT - Explicit version check
import cv2
cv_version = tuple(map(int, cv2.__version__.split('.')[:2]))
if cv_version >= (4, 5):
    tracker = cv2.legacy.TrackerCSRT_create()
else:
    tracker = cv2.TrackerCSRT_create()

# ❌ WRONG - Assume API without checking
tracker = cv2.TrackerCSRT_create()  # Fails on OpenCV 4.5+!
```

**Checklist**:
- [ ] Check library version if API changed
- [ ] Use try-except for namespace compatibility
- [ ] Provide fallback for older versions
- [ ] Document version requirements

---

## 🔍 Pre-Commit Checklist

Before suggesting any code, verify:

```markdown
□ Type Hints: All parameters and returns typed?
□ None Checks: Checked before accessing?
□ Arguments: Correct count and types?
□ Method Calls: Proper instance/static pattern?
□ No Duplication: Cached results, no repeated calls?
□ Dependencies: Stable versions only?
□ Compatibility: Fallbacks for version differences?
□ Tests: Will tests pass?
□ Linting: No Pylance errors?
□ Documentation: Docstrings complete?
```

---

## 📚 Code Template

Standard template following all rules:

```python
from typing import Optional, List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ExampleClass:
    """
    Example class following all 7 rules.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with type checking.
        
        Args:
            config: Optional configuration dictionary
        """
        # Rule 1: Type check
        if config is None:
            config = {}
        
        if not isinstance(config, dict):
            raise TypeError(f"Expected dict, got {type(config)}")
        
        self.config = config
        self.manager: Optional[SomeManager] = None
        
        # Rule 2: Check None before use
        try:
            self.manager = SomeManager(config)
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
    
    def process_items(
        self,
        items: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> List[str]:
        """
        Process items with safety checks.
        
        Args:
            items: Items to process
            options: Processing options
            max_results: Maximum results
            
        Returns:
            Processed results
        """
        # Rule 1 & 3: Validate inputs
        if items is None:
            items = []
        
        if not isinstance(items, list):
            raise TypeError(f"Expected list, got {type(items)}")
        
        if options is None:
            options = {}
        
        # Rule 2: Check manager
        if self.manager is None:
            logger.error("Manager not initialized")
            return []
        
        # Rule 5: Cache result
        config = self._get_config()  # Call once
        
        results = []
        for item in items[:max_results]:
            if item is None:
                continue
            
            # Rule 4: Instance method via self
            result = self._process_single(item, config)
            if result is not None:
                results.append(result)
        
        return results
    
    def _process_single(self, item: str, config: Dict[str, Any]) -> Optional[str]:
        """Process single item."""
        if item is None or not item:
            return None
        return item.upper()
    
    @staticmethod
    def validate_input(value: Optional[str]) -> bool:
        """Validate input (static method)."""
        if value is None:
            return False
        return len(value) > 0
    
    def _get_config(self) -> Dict[str, Any]:
        """Get config copy."""
        return self.config.copy()


# Usage
def main():
    # Rule 3: Proper initialization
    config = {"key": "value"}
    example = ExampleClass(config=config)
    
    # Rule 3: Pass all arguments
    items = ["a", "b", None, "c"]
    results = example.process_items(
        items=items,
        options={"mode": "fast"},
        max_results=10
    )
    
    # Rule 2: Check None
    if results:
        for result in results:
            if result is not None:
                print(result)
    
    # Rule 4: Static via Class
    is_valid = ExampleClass.validate_input("test")
```

---

## 🚨 Common Violations to Avoid

### ❌ Type Safety Violations
```python
# WRONG: No type hints
def process(data):
    return data.upper()

# WRONG: No None check
def get_title(info):
    return info.title  # Crash if None!
```

### ❌ Method Call Violations
```python
# WRONG: Instance method via class
result = MyClass.instance_method()  # Missing self!

# WRONG: Multiple duplicate calls
print(f"Value: {expensive_function()}")
print(f"Double: {expensive_function() * 2}")  # Called again!
```

### ❌ Argument Violations
```python
# WRONG: Missing required arguments
result = function(arg1)  # Missing arg2, arg3!

# WRONG: Wrong types
result = function(items="string")  # Should be List!
```

---

## 📖 References

- Python Type Hints: [PEP 484](https://peps.python.org/pep-0484/)
- Optional Types: [PEP 484 - Optional](https://peps.python.org/pep-0484/#the-optional-type)
- Type Checking: [mypy documentation](http://mypy-lang.org/)
- Best Practices: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## 🔐 Enforcement

**Status**: ACTIVE  
**Authority**: Mandatory for all AI-generated code  
**Violations**: Must be fixed before code submission  
**Review**: Every code suggestion must pass all 7 rules  

**Signed**: GitHub Copilot AI Assistant  
**Date**: October 23, 2025  
**Version**: 1.0.0

---

## 📝 Change Log

### Version 1.0.0 (2025-10-23)
- Initial version
- Established 7 core rules
- Created enforcement checklist
- Added code templates
- Documented common violations

---

**END OF GUIDELINES**
