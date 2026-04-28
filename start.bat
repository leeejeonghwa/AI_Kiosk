@echo off
chcp 65001 > nul
echo ================================
echo  AI Kiosk 서버 시작
echo ================================

if not exist .venv (
    echo [오류] 가상환경이 없습니다. setup.bat 을 먼저 실행해주세요.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
cd kiosk_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
