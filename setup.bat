@echo off
echo ========================================
echo DeadOPT Setup Script
echo ========================================
echo.

echo [1/5] Installing root dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install root dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [3/5] Installing backend dependencies...
cd backend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [4/5] Installing Python dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    echo Make sure Python is installed and in PATH
    pause
    exit /b 1
)

echo.
echo [5/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please edit it with your MongoDB URI.
) else (
    echo .env file already exists.
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your MongoDB URI
echo 2. Make sure MongoDB is running
echo 3. Run: npm run dev
echo.
pause