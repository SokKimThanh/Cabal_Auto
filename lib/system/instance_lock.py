import os
import sys
from pathlib import Path


class SingleInstanceLock:
    """Cross-platform single instance lock.

    Ensures only one instance of the application can run at a time.
    Uses Windows mutex on Windows, fcntl file lock on Unix-like systems.
    """

    def __init__(self, app_name: str = "CabalAutoHunt"):
        """Initialize single instance lock.

        Args:
            app_name: Unique application name for mutex/lock identification
        """
        self.app_name = app_name
        self.mutex = None
        self.lock_file = None
        self.is_locked = False

        # For Unix: lock file in tmp directory
        if sys.platform != "win32":
            lock_dir = Path(__file__).parent / "tmp"
            lock_dir.mkdir(parents=True, exist_ok=True)
            self.lock_file_path = lock_dir / f"{app_name}.lock"

    def acquire(self) -> bool:
        """Acquire the lock. Returns True if successful, False if another instance is running.

        Returns:
            bool: True if lock acquired successfully, False if another instance holds the lock.
        """
        try:
            if sys.platform == "win32":
                # Windows: Use named mutex (more reliable than file locking)
                import ctypes

                # Create mutex name (Global for all users, Local for current user)
                mutex_name = f"Global\\{self.app_name}_SingleInstance"

                # Try to create mutex
                kernel32 = ctypes.windll.kernel32
                self.mutex = kernel32.CreateMutexW(None, False, mutex_name)

                # Check if mutex already exists (ERROR_ALREADY_EXISTS = 183)
                last_error = kernel32.GetLastError()
                if last_error == 183:  # ERROR_ALREADY_EXISTS
                    return False

                self.is_locked = True
                return True
            else:
                # Unix: Use fcntl file lock
                import fcntl

                try:
                    self.lock_file = open(self.lock_file_path, "w")
                    fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.is_locked = True
                    # Write PID for debugging
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
                # Windows: Close mutex handle
                if self.mutex and self.is_locked:
                    import ctypes

                    kernel32 = ctypes.windll.kernel32
                    kernel32.CloseHandle(self.mutex)
                    self.is_locked = False
            else:
                # Unix: Unlock and close file
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
