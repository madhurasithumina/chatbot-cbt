@echo off
REM Quick Installation Script for CBT Chatbot
REM Windows Batch File

echo ============================================================
echo    CBT Mental Health Chatbot - Installation Script
echo ============================================================
echo.

REM Check Python
echo [1] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo [2] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo [3] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Install dependencies
echo [4] Installing dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed
echo.

REM Create .env file
echo [5] Setting up environment configuration...
if exist .env (
    echo .env file already exists
) else (
    copy .env.example .env
    echo .env file created
    echo.
    echo IMPORTANT: Please edit .env and add your OPENAI_API_KEY
)
echo.

REM Create directories
echo [6] Creating data directories...
if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed
if not exist data\models mkdir data\models
if not exist logs mkdir logs
echo Directories created
echo.

echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo Next Steps:
echo.
echo 1. Edit .env file and add your OpenAI API key:
echo    notepad .env
echo.
echo 2. Train the model (first time only, takes 30-60 min):
echo    python scripts\train_model.py
echo.
echo 3. Run the chatbot:
echo    python console_chat.py    (Console interface)
echo    python main.py            (API server)
echo.
echo For more information, see:
echo    README.md, QUICKSTART.md, or PROJECT_SUMMARY.md
echo.
echo ============================================================
pause
