@echo off
echo ========================================
echo Live Task Review Agent - Backend Server
echo ========================================
echo.
echo Starting FastAPI server...
echo Backend URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload