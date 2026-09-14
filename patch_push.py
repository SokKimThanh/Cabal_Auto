import subprocess
import sys

try:
    # Use subprocess.run to execute git push
    result = subprocess.run(["git", "push", "origin", "revert-531-refactor-app-gui-god-class-16174782814009284069"],
                            capture_output=True, text=True, check=True)
    print("Push successful!")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Push failed!")
    print(e.stderr)
    sys.exit(1)
