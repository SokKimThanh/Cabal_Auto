import subprocess
try:
    result = subprocess.run(["python3", "app_gui.py"], timeout=2)
except subprocess.TimeoutExpired:
    print("Success: app_gui runs")
