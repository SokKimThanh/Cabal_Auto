"""Regression test for the i18n registration bug (2026-08-27, re-lost 2026-08-27 by PR #96).

Root cause: GLOBAL_TRANSLATIONS was imported but never registered into the
i18n registry after a refactor accidentally dropped the module-level
`i18n_register_bulk(...)` call. Since then, GLOBAL_TRANSLATIONS self-registers
on import (see lib/i18n/translations.py), so this test just guards against
that safety net being removed again (it was dropped once already by a stale
branch merge in PR #96, which motivated recreating this test).
"""

import pytest

pytestmark = pytest.mark.fast


def test_global_translations_self_register_on_import():
    """Importing GLOBAL_TRANSLATIONS must register it into the i18n registry."""
    from lib.i18n import GLOBAL_NS, set_default_lang, t
    from lib.i18n.translations import GLOBAL_TRANSLATIONS

    assert "app_title" in GLOBAL_TRANSLATIONS.get("en", {})
    assert "app_title" in GLOBAL_TRANSLATIONS.get("vi", {})

    for lang in ("en", "vi"):
        set_default_lang(lang)
        resolved = t("app_title", ns=GLOBAL_NS)
        # If registration is missing, t() falls back to returning the raw key.
        assert resolved != "app_title", (
            f"GLOBAL_TRANSLATIONS not registered for lang={lang}; "
            "t() returned the raw key instead of a translated string"
        )
        assert resolved == GLOBAL_TRANSLATIONS[lang]["app_title"]

def test_other_translations_self_register_on_import():
    """Importing other translations must register them into the i18n registry."""
    from lib.i18n import set_default_lang, t

    # Import the modules that should trigger self-registration
    from lib.i18n.translations import LIBRARY_MANAGER_TRANSLATIONS, SETUP_WIZARD_TRANSLATIONS, VISION_WIZARD_TRANSLATIONS
    from lib.i18n.monster_editor_translations import MONSTER_EDITOR_TRANSLATIONS

    test_cases = [
        ("library_manager", LIBRARY_MANAGER_TRANSLATIONS, "library_manager_title"),
        ("setup_wizard", SETUP_WIZARD_TRANSLATIONS, "wizard_title"),
        ("vision_wizard", VISION_WIZARD_TRANSLATIONS, "vision_wizard_title"),
        ("monster_editor", MONSTER_EDITOR_TRANSLATIONS, "quick_editor_title"),
    ]

    for ns, translations, key in test_cases:
        assert key in translations.get("en", {})
        assert key in translations.get("vi", {})

        for lang in ("en", "vi"):
            set_default_lang(lang)
            resolved = t(key, ns=ns)
            assert resolved != key, (
                f"{ns} not registered for lang={lang}; "
                "t() returned the raw key instead of a translated string"
            )
            assert resolved == translations[lang][key]
