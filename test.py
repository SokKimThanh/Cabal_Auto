import py_compile
try:
    py_compile.compile("ui/controllers/app_state_controller.py", doraise=True)
except Exception as e:
    print(e)
