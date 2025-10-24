# Quick Reference: Python Coding Rules

**Auto-apply for ALL Python code written by AI Assistant**

## ✅ The 7 Rules (Must Follow)

### 1. Type Check First
```python
def func(data: Optional[List[str]] = None) -> List[str]:
    if data is None: data = []
    if not isinstance(data, list): raise TypeError()
```

### 2. No None Access
```python
obj = get_object()
if obj is not None:  # Always check!
    value = obj.attribute
```

### 3. Complete Arguments
```python
# Check signature first!
result = function(arg1, arg2, arg3)  # All required args
```

### 4. Method Calls
```python
instance.instance_method()  # Instance via self/instance
ClassName.static_method()   # Static via Class
```

### 5. No Duplication
```python
result = expensive_call()  # Call once
print(result.x, result.y)  # Reuse
```

### 6. Stable Versions
```powershell
python -m pip install package==1.0.0  # Stable only
```

### 7. Check Namespace
```python
try:
    obj = lib.new_api.method()  # Try new
except AttributeError:
    obj = lib.old_api.method()  # Fallback
```

## 🔍 Pre-Code Checklist

- [ ] Type hints?
- [ ] None checks?
- [ ] Correct args?
- [ ] Right method calls?
- [ ] No duplicates?
- [ ] Stable versions?
- [ ] Compatibility?

## 🚨 Auto-Enforce

This file is loaded automatically. All 7 rules apply to every code suggestion.

**Reference**: See `docs/PYTHON_CODING_GUIDELINES.md` for details.
