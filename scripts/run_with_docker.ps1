# Run PyQt6 application with Docker MySQL configuration

Write-Host ""
Write-Host "Starting Secure Academic Browser with Docker MySQL..." -ForegroundColor Cyan
Write-Host ""

# Set environment variables for Docker MySQL
$env:DB_HOST = "localhost"
$env:DB_PORT = "3307"

# Run the application (assumes script is run from project root)
python main.py

