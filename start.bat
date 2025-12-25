@echo off
echo ===================================
echo    AI Stock Valuation Agent
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Installing Node.js dependencies...
cd ..\frontend
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Starting Flask backend server...
cd ..\backend
start "Flask Backend" cmd /c "python app.py"

echo.
echo [4/4] Starting React frontend server...
cd ..\frontend
start "React Frontend" cmd /c "npm run dev"

echo.
echo ===================================
echo    Servers are starting...
echo ===================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to open the application in browser...
pause >nul
start http://localhost:3000
