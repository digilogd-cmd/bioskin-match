@echo off
cd /d "%~dp0"
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting BioSkin Match 2.0 Server...
echo Please open http://localhost:8002 in your web browser.
uvicorn backend_rag_api:app --host 0.0.0.0 --port 8002
pause
