@echo off
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.12 from https://www.python.org
    pause
    exit /b 1
)
python --version

echo [1/3] Creating virtual environment...
python -c "import venv" > nul 2>&1
if errorlevel 1 (
    echo venv module missing. Installing virtualenv...
    python -m pip install virtualenv
    python -m virtualenv .venv
) else (
    if not exist .venv (
        python -m venv .venv
    ) else (
        echo Virtual environment already exists.
    )
)

if not exist .venv (
    echo [ERROR] Failed to create virtual environment.
    echo Try reinstalling Python 3.12 with default options.
    pause
    exit /b 1
)

echo [2/3] Installing packages...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r kiosk_backend\requirements.txt

echo [3/3] Installing PyTorch (CUDA 12.1)...
.venv\Scripts\python.exe -m pip install torch transformers --index-url https://download.pytorch.org/whl/cu121

echo Verifying uvicorn installation...
.venv\Scripts\python.exe -c "import uvicorn" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] uvicorn not installed. Retrying...
    .venv\Scripts\python.exe -m pip install uvicorn
    if errorlevel 1 (
        echo [ERROR] Failed to install uvicorn.
        pause
        exit /b 1
    )
)
echo uvicorn OK

echo.
echo Setup complete! Run start.bat
pause
