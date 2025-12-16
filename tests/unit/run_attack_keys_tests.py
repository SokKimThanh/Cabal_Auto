import importlib.util
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import tests.unit.test_attack_keys_migration as t

failed = 0

for name in dir(t):
    if name.startswith('test_'):
        func = getattr(t, name)
        if callable(func):
            try:
                with tempfile.TemporaryDirectory(prefix='cabal_auto_tmp_test_dir_') as temp_dir:
                    func(Path(temp_dir))
            except TypeError:
                # no args
                try:
                    func()
                except Exception as e:
                    print(f"{name}: FAIL -> {e}")
                    failed += 1
                else:
                    print(f"{name}: OK")
            except Exception as e:
                print(f"{name}: FAIL -> {e}")
                failed += 1

if failed:
    print(f"{failed} test(s) failed")
    sys.exit(1)
else:
    print("All tests passed")
    sys.exit(0)
