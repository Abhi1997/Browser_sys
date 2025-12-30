@echo off
REM Quick Docker Start Script for Secure Academic Browser (Windows)

echo.
echo 🚀 Starting Secure Academic Browser with Docker...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Start services
echo 📦 Starting Docker services...
docker-compose up -d

REM Wait for database to be ready
echo ⏳ Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo 📊 Service Status:
docker-compose ps

echo.
echo ✅ Services started!
echo.
echo 📋 Next Steps:
echo    1. Wait 30-60 seconds for database initialization
echo    2. Run: python setup_databases.py
echo    3. Run: python populate_sample_data.py
echo    4. Run: python main.py
echo.
echo 🌐 Access Points:
echo    - Dashboard: http://localhost:3000
echo    - API: http://localhost:5000
echo    - Database: localhost:3306
echo.
echo 📝 View logs: docker-compose logs -f
echo 🛑 Stop services: docker-compose down
echo.
pause

