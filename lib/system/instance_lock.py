import os
import sys
import tempfile
from pathlib import Path


class SingleInstanceLock:
    def __init__(self, app_name: str = "CabalAutoHunt"):
        self.app_name = app_name
        self.mutex = None
        self.lock_file = None
        self.is_locked = False

        if sys.platform != "win32":
            lock_dir = Path(tempfile.gettempdir())
            self.lock_file_path = lock_dir / f"{app_name}.lock"

    def acquire(self) -> bool:
        try:
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                mutex_name = f"Global\\{self.app_name}_SingleInstance"
                self.mutex = kernel32.CreateMutexW(None, False, mutex_name)

                last_error = kernel32.GetLastError()
                if last_error == 183:  # ERROR_ALREADY_EXISTS
                    kernel32.CloseHandle(self.mutex)
                    self.mutex = None
                    return False

                self.is_locked = True
                return True
            else:
                import fcntl
                try:
                    self.lock_file = open(self.lock_file_path, "w")
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.is_locked = True
                    self.lock_file.write(str(os.getpid()))
                    self.lock_file.flush()
                    return True
                except (OSError, IOError):
                    if self.lock_file:
                        self.lock_file.close()
                    return False
        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False

    def release(self):
        """Release the lock and clean up."""
        try:
            if sys.platform == "win32":
                if self.mutex and self.is_locked:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.CloseHandle(self.mutex)
                    self.is_locked = False
            else:
                if self.lock_file and self.is_locked:
                    import fcntl
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                    self.lock_file.close()
                    try:
                        os.unlink(self.lock_file_path)
                    except OSError:
                        pass
                    self.is_locked = False
        except Exception as e:
            print(f"Error releasing lock: {e}")
