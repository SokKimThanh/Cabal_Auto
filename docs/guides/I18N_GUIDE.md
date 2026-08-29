# I18N Guide: Adding a New Bilingual Screen

This guide outlines the mandatory pattern for adding a new screen that requires translated copy in both English and Vietnamese.

For the historical context of why this pattern is strictly enforced, please see [.jules/i18n-sprint-roadmap.md](../../.jules/i18n-sprint-roadmap.md).

## The Mandatory Pattern

When adding translations for a new screen, the translation data must live in its own data module and **self-register** upon import.
You must **never** call `lib.i18n.register_bulk(...)` from the consumer UI code (e.g., inside your Window or Controller classes).

### 1. Create the Translation Dictionary
Create a new file in `lib/i18n/` (e.g. `lib/i18n/my_screen_translations.py`) and define your `*_TRANSLATIONS` dictionary:

```python
# lib/i18n/my_screen_translations.py
from typing import Dict
from lib.i18n import register_bulk

# Define your unique namespace string
MY_SCREEN_NS = "my_screen"

# Define your translation dictionary, strictly mapping keys to localized strings
MY_SCREEN_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "my_screen.title": "My Screen Title",
        "my_screen.save_button": "Save Settings",
    },
    "vi": {
        "my_screen.title": "Tiêu đề Màn hình",
        "my_screen.save_button": "Lưu Cài đặt",
    }
}

# MANDATORY: Self-register the dictionary at the bottom of the data file
register_bulk(MY_SCREEN_NS, MY_SCREEN_TRANSLATIONS)
```

### 2. Consume It In Your UI
In your UI module (e.g. `ui/windows/my_screen.py`), you only need to import the data module once so that it registers itself. Then, use the standard `lib.i18n.t()` API to retrieve strings:

```python
# ui/windows/my_screen.py
import lib.i18n.my_screen_translations as my_screen_data
from lib.i18n import t

# Retrieve a translated string by providing the key and the specific namespace
title_text = t("my_screen.title", ns=my_screen_data.MY_SCREEN_NS)
```

## Checklist for Adding a New Screen

- [ ] I have created a unique namespace string.
- [ ] My dictionary is named with the `_TRANSLATIONS` suffix.
- [ ] My dictionary contains identical keys in both `en` and `vi`.
- [ ] My dictionary self-registers at the bottom of the file using `register_bulk`.
- [ ] I am **not** calling `register_bulk` from any consumer/UI module.

## How Errors Are Caught

The integrity test at `tests/unit/test_i18n_registry_integrity.py` dynamically scans the `lib/i18n/` directory for any constant ending in `_TRANSLATIONS`.
If you define a translation dictionary but forget to self-register it, this test will fail loudly during CI, preventing the application from silently showing raw keys to users.
