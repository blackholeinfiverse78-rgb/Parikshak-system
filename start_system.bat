@echo off
echo ========================================
echo Live Task Review Agent - FULL SYSTEM
echo ========================================
echo.
echo Starting both Backend and Frontend servers...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo ========================================

echo Starting Backend Server...
start "Live Task Review Agent - Backend" cmd /k "echo Backend Server Starting... && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
start "Live Task Review Agent - Frontend" cmd /k "echo Frontend Server Starting... && cd frontend && npm start"

echo.
echo ========================================
echo SYSTEM STARTED SUCCESSFULLY!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo ========================================

pause