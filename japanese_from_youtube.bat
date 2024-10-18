@echo off
cd /d %~dp0
echo Current directory: %cd%

if not exist ".\venv\Scripts\activate.bat" (
    echo Virtual environment activation script not found.
    pause
    exit /b 1
)

call .\venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

python main.py
if %errorlevel% neq 0 (
    echo Failed to run main.py.
    pause
    exit /b %errorlevel%
)