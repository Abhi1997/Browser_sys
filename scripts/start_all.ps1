# PowerShell script to start both API server and browser
Write-Host "Starting EduBrowser System..." -ForegroundColor Green
Write-Host ""

# Start API Server in a new window
Write-Host "Starting API Server on port 5000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python api_server.py"

# Wait a bit for the server to start
Start-Sleep -Seconds 3

# Start the browser application
Write-Host "Starting Browser Application..." -ForegroundColor Cyan
python main.py
