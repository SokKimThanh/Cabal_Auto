@echo off
REM Check and install missing dependencies
REM Sprint 23 Phase 5 - Overlay Window Setup

echo ========================================
echo Cabal_Auto Dependency Check
echo ========================================
echo.

REM Find Python executable
SET PY=
IF EXIST "venv\Scripts\python.exe" (
    SET PY=venv\Scripts\python.exe
    echo Using venv Python: venv\Scripts\python.exe
) ELSE IF EXIST ".venv\Scripts\python.exe" (
    SET PY=.venv\Scripts\python.exe
    echo Using venv Python: .venv\Scripts\python.exe
) ELSE (
    FOR /F "usebackq tokens=*" %%i IN (`where python 2^>nul`) DO SET PY=%%i & GOTO :foundpy
    :foundpy
    echo Using system Python: %PY%
)

IF NOT DEFINED PY (
    echo ERROR: Python not found!
    echo Please install Python or activate virtual environment.
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
echo.

REM Run dependency checker with auto-install
"%PY%" "%~dp0..\scripts\check_dependencies.py" --install

echo.
echo ========================================
IF %ERRORLEVEL% EQU 0 (
    echo ✓ All dependencies installed!
) ELSE (
    echo ✗ Some dependencies failed to install
    echo Please check the errors above
)
echo ========================================
echo.
pause
