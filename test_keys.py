from lib.i18n.translations import GLOBAL_TRANSLATIONS

print("EN keys len:", len(GLOBAL_TRANSLATIONS['en']))
print("VI keys len:", len(GLOBAL_TRANSLATIONS['vi']))

print("EN has apply_all_settings_unsaved:", "apply_all_settings_unsaved" in GLOBAL_TRANSLATIONS['en'])
print("VI has apply_all_settings_unsaved:", "apply_all_settings_unsaved" in GLOBAL_TRANSLATIONS['vi'])
