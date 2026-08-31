import re

with open("lib/db/services/db5b_audit_magic_ranged.py", "r") as f:
    code = f.read()

# Update run_audit to allow passing content so we can test it easily
code = code.replace("def run_audit():\n    with open(SOURCE_FILE, \"r\", encoding=\"utf-8\") as f:\n        content = f.read()", "def run_audit(content=None):\n    if content is None:\n        with open(SOURCE_FILE, \"r\", encoding=\"utf-8\") as f:\n            content = f.read()")

with open("lib/db/services/db5b_audit_magic_ranged.py", "w") as f:
    f.write(code)
