@echo off
REM Run PyQt6 application with Docker MySQL configuration

echo.
echo Starting Secure Academic Browser with Docker MySQL...
echo.

REM Set environment variables for Docker MySQL
set DB_HOST=localhost
set DB_PORT=3307

REM Run the application
python main.py

