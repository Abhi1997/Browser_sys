@echo off
REM EduBrowser Docker Startup Script for Windows
REM Usage: start.bat [command]

setlocal enabledelayedexpansion

set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=up

title EduBrowser Docker Manager

echo.
echo ====================================
echo  EduBrowser Docker Manager
echo ====================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Desktop.
    exit /b 1
)

REM Create .env if it doesn't exist
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo [OK] Created .env file
        echo [INFO] Please review and edit .env if needed
    )
)

if "%COMMAND%"=="up" goto cmd_up
if "%COMMAND%"=="start" goto cmd_up
if "%COMMAND%"=="down" goto cmd_down
if "%COMMAND%"=="stop" goto cmd_down
if "%COMMAND%"=="restart" goto cmd_restart
if "%COMMAND%"=="logs" goto cmd_logs
if "%COMMAND%"=="status" goto cmd_status
if "%COMMAND%"=="ps" goto cmd_status
if "%COMMAND%"=="rebuild" goto cmd_rebuild
if "%COMMAND%"=="clean" goto cmd_clean
if "%COMMAND%"=="health" goto cmd_health
if "%COMMAND%"=="help" goto cmd_help
goto cmd_unknown

:cmd_up
echo [INFO] Starting EduBrowser services...
docker-compose up -d
echo [OK] Services started
timeout /t 2 /nobreak
cls
docker-compose ps
echo.
echo [INFO] Access points:
echo   React Dashboard: http://localhost:3000
echo   API Server:      http://localhost:5000
echo   Database:        localhost:3306
echo.
goto end

:cmd_down
echo [INFO] Stopping EduBrowser services...
docker-compose down
echo [OK] Services stopped
goto end

:cmd_restart
echo [INFO] Restarting EduBrowser services...
docker-compose restart
echo [OK] Services restarted
goto end

:cmd_logs
set SERVICE=%2
if "%SERVICE%"=="" set SERVICE=app
echo [INFO] Showing logs for %SERVICE%...
docker-compose logs -f %SERVICE%
goto end

:cmd_status
echo [INFO] Service Status:
docker-compose ps
goto end

:cmd_rebuild
echo [INFO] Rebuilding containers...
docker-compose build
echo [INFO] Starting services...
docker-compose up -d
echo [OK] Rebuilt and started
goto end

:cmd_clean
echo.
echo [WARNING] This will remove all containers and volumes
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    echo [INFO] Cleaning up...
    docker-compose down -v
    echo [OK] Cleaned up
) else (
    echo [INFO] Cancelled
)
goto end

:cmd_health
echo [INFO] Checking service health...
echo.
echo [INFO] Testing API Server...
curl -s http://localhost:5000/health
echo.
echo.
echo [INFO] Checking Database...
docker-compose exec db mysqladmin ping -h localhost -pInnovation || echo [ERROR] Database not responding
goto end

:cmd_help
echo [INFO] Available commands:
echo.
echo   start.bat up        - Start services
echo   start.bat down      - Stop services
echo   start.bat restart   - Restart services
echo   start.bat rebuild   - Rebuild containers
echo   start.bat logs [service] - View logs
echo   start.bat status    - Show service status
echo   start.bat health    - Check service health
echo   start.bat clean     - Remove all containers and volumes
echo   start.bat help      - Show this help message
echo.
echo [INFO] Examples:
echo   start.bat           - Start all services
echo   start.bat logs app  - Show API server logs
echo   start.bat logs dashboard - Show dashboard logs
echo.
goto end

:cmd_unknown
echo [ERROR] Unknown command: %COMMAND%
echo Run 'start.bat help' for available commands
exit /b 1

:end
echo.
