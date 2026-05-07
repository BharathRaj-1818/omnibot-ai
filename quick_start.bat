@echo off
REM OmniBot Quick Start Script for Windows

echo 🤖 OmniBot - Quick Start Setup
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

echo ✅ Python and Node.js found!
echo.

REM Setup Backend
echo 📦 Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist "..\\.env" (
    echo Creating .env file...
    copy "..\\.env.example" "..\\.env"
    echo ⚠️  Please edit .env file with your API keys before running bots!
)

REM Initialize database
echo Initializing database...
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

echo ✅ Backend setup complete!
echo.

REM Setup Frontend
echo 📦 Setting up frontend...
cd ..\\frontend

REM Install dependencies
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    call npm install
)

echo ✅ Frontend setup complete!
echo.

REM Instructions
echo 🎉 Setup Complete!
echo.
echo To start the application:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   venv\\Scripts\\activate
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm start
echo.
echo Terminal 3 (Optional) - Telegram Bot:
echo   cd bots\\telegram
echo   python bot.py
echo.
echo 🌐 Web Interface: http://localhost:3000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Happy coding! 🚀
echo.
pause
