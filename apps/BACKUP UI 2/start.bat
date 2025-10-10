@echo off
echo ========================================
echo   LLM UI - Starting Application
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "venv\Lib\site-packages\panel\" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if database exists
if not exist "llm_ui.db" (
    echo Database not found. Running setup...
    python setup.py
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please edit .env file with your configuration
    echo.
)

REM Start the application
echo Starting LLM UI...
echo.
echo Application will be available at: http://localhost:5006
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
