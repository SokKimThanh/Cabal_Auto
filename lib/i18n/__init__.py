"""
Simple i18n registry for the whole app (package entry point).

Exposes:
- register(namespace, lang, mapping): Register translation key->string map under a namespace and language.
- register_bulk(namespace, translations): Bulk register dictionaries by language.
- set_default_lang(lang): Set the current default language (e.g., 'en' or 'vi').
- t(key, *, ns=None, lang=None, default=None): Retrieve a string by key.
- get_lang(): Get the current language.
- GLOBAL_NS: Special global namespace key.
"""
from __future__ import annotations
from typing import Dict, Optional, List, Set, Iterator

# Structure: _REGISTRY[namespace][lang] = { key: text }
_REGISTRY: Dict[str, Dict[str, Dict[str, str]]] = {}
_DEFAULT_LANG: str = 'vi'

# Special namespace used when no ns provided
GLOBAL_NS = '_global'


def register(namespace: str, lang: str, mapping: Dict[str, str]) -> None:
	ns = _REGISTRY.setdefault(namespace, {})
	existing = ns.setdefault(lang, {})
	existing.update(mapping)


def set_default_lang(lang: str) -> None:
	global _DEFAULT_LANG
	if lang not in ('en', 'vi'):
		# Accept any string but keep guard for common cases
		_DEFAULT_LANG = str(lang)
	else:
		_DEFAULT_LANG = lang


def get_lang() -> str:
	return _DEFAULT_LANG


def t(key: str, *, ns: Optional[str] = None, lang: Optional[str] = None, default: Optional[str] = None) -> str:
	"""Translate a key.
	Lookup order:
	1. If ns provided: (ns, lang) -> (ns, default_lang)
	2. Global namespace: (GLOBAL_NS, lang) -> (GLOBAL_NS, default_lang)
	3. Fallback: return default or key
	"""
	lang_to_use = lang or _DEFAULT_LANG

	def _ns_lookup(namespace: str) -> Optional[str]:
		by_lang = _REGISTRY.get(namespace, {})
		if lang_to_use in by_lang and key in by_lang[lang_to_use]:
			return by_lang[lang_to_use][key]
		# fallback to default language if available
		if _DEFAULT_LANG in by_lang and key in by_lang[_DEFAULT_LANG]:
			return by_lang[_DEFAULT_LANG][key]
		return None

	# 1. explicit namespace first
	if ns:
		val = _ns_lookup(ns)
		if val is not None:
			return val

	# 2. global namespace
	val = _ns_lookup(GLOBAL_NS)
	if val is not None:
		return val

	# 3. final fallback
	return default if default is not None else key


# Register convenience: allow modules to push their dictionaries easily

def register_bulk(namespace: str, translations: Dict[str, Dict[str, str]]) -> None:
	for lang, mapping in translations.items():
		register(namespace, lang, mapping)


def get_registered_namespaces() -> Set[str]:
	"""Return a set of all currently registered namespaces."""
	return set(_REGISTRY.keys())


def iter_missing_keys(namespace: str, langs: List[str]) -> Iterator[str]:
	"""Yield keys that exist in the given namespace for at least one language,
	but are missing in at least one of the specified languages.
	"""
	if namespace not in _REGISTRY:
		return

	ns_dict = _REGISTRY[namespace]

	# Collect all keys across all languages in this namespace
	all_keys: Set[str] = set()
	for lang_dict in ns_dict.values():
		all_keys.update(lang_dict.keys())

	# Check each key against the requested languages
	for key in all_keys:
		for lang in langs:
			if lang not in ns_dict or key not in ns_dict[lang]:
				yield key
				break
