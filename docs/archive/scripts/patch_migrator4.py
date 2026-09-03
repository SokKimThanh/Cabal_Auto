import re
with open("lib/features/hunt/config_migrator.py", "r") as f:
    content = f.read()

# Fix priority schema enforced test where we discarded the "Test" entry because it had no ID (id=0)
# We can just change the test to provide a valid ID instead of expecting it to accept ID 0, since the new schema says:
# monster_id > 0 is required.
