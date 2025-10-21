@echo off
REM Batch launcher for Cabal_Auto GUI
REM Usage: run_venv.bat [venv_path] [-- args]
SET VENV=%~1
IF "%VENV%"=="" SET VENV=.venv
IF EXIST "%VENV%\Scripts\python.exe" (
    SET PY=%VENV%\Scripts\python.exe
) ELSE IF EXIST "venv\Scripts\python.exe" (
    SET PY=venv\Scripts\python.exe
) ELSE (
    FOR /F "usebackq tokens=*" %%i IN (`where python 2^>nul`) DO SET PY=%%i & GOTO :foundpy
    :foundpy
)
IF NOT DEFINED PY (
    echo No python found. Please ensure Python is installed or provide a venv path.
    exit /b 1
)

echo Using python: %PY%
"%PY%" e:\Cabal_Auto\app_gui.py %*
