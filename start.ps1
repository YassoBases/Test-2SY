Write-Host "Starting EduSpark..." -ForegroundColor Cyan

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; & '$PSScriptRoot\eduspark-venv310\Scripts\python.exe' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

# Start Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run dev"

Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host "Done! Opening browser..." -ForegroundColor Green
