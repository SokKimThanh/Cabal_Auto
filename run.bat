@echo off
REM Launcher wrapper - calls the actual launcher in scripts/launchers/
REM This file exists for backward compatibility
echo Redirecting to scripts\launchers\run_venv.bat...
call "%~dp0scripts\launchers\run_venv.bat" %*
