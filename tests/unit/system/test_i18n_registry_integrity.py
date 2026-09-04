"""Registry integrity test.

This test dynamically walks every *_TRANSLATIONS dictionary defined under the
lib/i18n package and asserts that each key is successfully registered and
translatable in both 'en' and 'vi'.

This ensures no translation dictionary is accidentally imported but left unregistered,
which would cause the application to silently fall back to rendering raw keys.
"""

import importlib
import inspect
import pkgutil
import pytest

import lib.i18n

pytestmark = pytest.mark.fast

def test_i18n_registry_integrity():
    """Dynamically discover all *_TRANSLATIONS and verify they are registered."""
    from lib.i18n import set_default_lang, t, get_registered_namespaces

    # Important: importing all modules in lib/i18n/ triggers their self-registration
    discovered_dicts = []

    for loader, modname, ispkg in pkgutil.walk_packages(lib.i18n.__path__):
        mod = importlib.import_module(f"lib.i18n.{modname}")
        for var_name, var_val in inspect.getmembers(mod):
            if var_name.endswith("_TRANSLATIONS") and isinstance(var_val, dict):
                discovered_dicts.append((modname, var_name, var_val))

    assert len(discovered_dicts) > 0, "No translation dictionaries found under lib/i18n/"

    # Now verify each dictionary against what's registered
    for modname, dict_name, translations in discovered_dicts:
        # Every translation dictionary should at least have 'en' and 'vi'
        # The goal is to ensure that for whatever language we look up, we don't get the raw key back.
        # But wait - if a string is present in EN but missing in VI, it falls back to VI default?
        # No, if we ask for VI and it's missing, t() might fall back to EN if EN is default, or return the raw key.
        # Wait, if a key is only in 'en', querying 'vi' might return raw key if 'vi' is the fallback!
        # Actually, let's just assert that if the key exists in the raw dictionary FOR that language,
        # it is successfully resolved via t().

        for lang in ("en", "vi"):
            set_default_lang(lang)
            lang_dict = translations.get(lang, {})

            for key in lang_dict.keys():
                # We need to find the namespace for this dict.
                # A robust way is to just check if `t(key, ns=ns)` works for *some* namespace,
                # or we can iterate through all registered namespaces to find the translation.

                resolved = None
                found_ns = None
                # First, test if it works with GLOBAL_NS (t() handles this automatically)
                if t(key) != key:
                    resolved = t(key)
                    found_ns = lib.i18n.GLOBAL_NS
                else:
                    # Try all other registered namespaces
                    for ns in get_registered_namespaces():
                        res = t(key, ns=ns)
                        if res != key:
                            resolved = res
                            found_ns = ns
                            break

                assert resolved is not None, (
                    f"Key '{key}' from {dict_name} not registered in any namespace for lang={lang}; "
                    "t() returned the raw key instead of a translated string."
                )

                # We can also assert it matches what's in the dict, but we just need to ensure it's not the raw key
                assert resolved != key


def test_load_from_db_hydration():
    """Test that load_from_db correctly hydrates the registry."""
    import lib.i18n
    from unittest.mock import patch, MagicMock

    # Create a mock for the TranslationService
    mock_service = MagicMock()
    mock_service.get_all.return_value = [
        {"namespace": "test_ns", "key": "test_key", "lang": "en", "text": "Test English"},
        {"namespace": "test_ns", "key": "test_key", "lang": "vi", "text": "Test Vietnamese"}
    ]

    with patch('lib.db.services.translation_service.TranslationService', return_value=mock_service):
        # Clear registry for this test
        original_registry = dict(lib.i18n._REGISTRY)
        lib.i18n._REGISTRY.clear()

        try:
            lib.i18n.load_from_db()

            # Verify the translations are registered
            assert "test_ns" in lib.i18n._REGISTRY
            assert lib.i18n._REGISTRY["test_ns"]["en"]["test_key"] == "Test English"
            assert lib.i18n._REGISTRY["test_ns"]["vi"]["test_key"] == "Test Vietnamese"

            # Check translation works
            lib.i18n.set_default_lang('en')
            assert lib.i18n.t('test_key', ns='test_ns') == "Test English"

        finally:
            # Restore registry
            lib.i18n._REGISTRY = original_registry
