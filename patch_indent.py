import re

with open("lib/features/hunt/hunt_config.py", "r") as f:
    content = f.read()

# Wait, I didn't verify whether git restore reverted my previous atomic changes!
# Yes, git restore reverted them!
