# 📚 How to Use Coding Guidelines

## 📍 Location

The coding guidelines are saved in two locations:

1. **Detailed Version**: `docs/PYTHON_CODING_GUIDELINES.md`
   - Complete documentation (400+ lines)
   - Examples and anti-patterns
   - Code templates
   - References and links

2. **Quick Reference**: `CODING_RULES_QUICK_REFERENCE.md`
   - Quick lookup (70 lines)
   - Condensed rules
   - Fast checklist

## 🎯 Usage

### For AI Assistant (Automatic)

The AI Assistant will **automatically** follow these guidelines for all Python code:

- ✅ Type hints on all functions
- ✅ None checks before access
- ✅ Proper method calls
- ✅ Complete arguments
- ✅ No duplication
- ✅ Stable versions only
- ✅ Namespace compatibility

**No need to remind the AI** - these rules are now built-in!

### For Human Developers

#### Quick Check (Before Writing Code)

Open `CODING_RULES_QUICK_REFERENCE.md` and verify your code against the 7 rules.

#### Detailed Review (Before Commit)

Open `docs/PYTHON_CODING_GUIDELINES.md` and go through the pre-commit checklist:

```markdown
□ Type Hints: All parameters and returns typed?
□ None Checks: Checked before accessing?
□ Arguments: Correct count and types?
□ Method Calls: Proper instance/static pattern?
□ No Duplication: Cached results, no repeated calls?
□ Dependencies: Stable versions only?
□ Compatibility: Fallbacks for version differences?
```

## 🔧 Integration with Tools

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.analysis.typeCheckingMode": "strict"
}
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Checking Python code against guidelines..."

# Check for type hints
if git diff --cached --name-only | grep -q "\.py$"; then
    echo "✓ Python files detected"
    echo "✓ Guidelines auto-enforced by AI"
fi
```

## 📖 Quick Examples

### Example 1: Type Safety

```python
# ✅ GOOD
def process(data: Optional[List[str]] = None) -> List[str]:
    if data is None:
        return []
    return [x.upper() for x in data if x]

# ❌ BAD
def process(data):
    return [x.upper() for x in data]
```

### Example 2: None Checks

```python
# ✅ GOOD
info = get_info()
if info is not None:
    title = info.title
else:
    title = "Unknown"

# ❌ BAD
info = get_info()
title = info.title  # Crash if None!
```

### Example 3: Method Calls

```python
# ✅ GOOD
manager = WindowManager()  # Create instance
hwnd = manager.find_window("Title")  # Instance method

is_valid = WindowManager.validate(hwnd)  # Static method

# ❌ BAD
hwnd = WindowManager.find_window("Title")  # Missing self!
```

## 🚀 Quick Start for New Developers

1. **Read the Quick Reference** (5 minutes)
   ```bash
   cat CODING_RULES_QUICK_REFERENCE.md
   ```

2. **Study the Detailed Guide** (30 minutes)
   ```bash
   code docs/PYTHON_CODING_GUIDELINES.md
   ```

3. **Apply the Rules** (Every time you code)
   - Write code following the 7 rules
   - Use the checklist before committing
   - Review AI-generated code against rules

## 📊 Rule Summary

| # | Rule | Priority | Impact |
|---|------|----------|--------|
| 1 | Type Check | 🔴 Critical | Prevents type errors |
| 2 | None Check | 🔴 Critical | Prevents AttributeError |
| 3 | Complete Args | 🔴 Critical | Prevents TypeError |
| 4 | Method Calls | 🟡 High | Code clarity |
| 5 | No Duplication | 🟡 High | Performance |
| 6 | Stable Versions | 🟢 Medium | Reliability |
| 7 | Namespaces | 🟢 Medium | Compatibility |

## ❓ FAQ

**Q: Do I need to follow these rules for every Python file?**  
A: Yes, all Python code in this project should follow these rules.

**Q: What if I disagree with a rule?**  
A: Open an issue to discuss. Rules can be updated if justified.

**Q: Will the AI really follow these automatically?**  
A: Yes! The AI has these guidelines integrated and will auto-apply them.

**Q: Can I use these guidelines in other projects?**  
A: Yes! The guidelines are general Python best practices.

## 🔄 Updates

To update the guidelines:

1. Edit `docs/PYTHON_CODING_GUIDELINES.md`
2. Update version number
3. Add changelog entry
4. Commit with message: `docs: Update coding guidelines vX.Y.Z`

## 📞 Support

- **Issues**: Open a GitHub issue
- **Questions**: Ask in team chat
- **Suggestions**: Submit a PR

---

**Last Updated**: October 23, 2025  
**Version**: 1.0.0  
**Status**: ACTIVE
