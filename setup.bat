@echo off
chcp 65001 > nul
echo ================================
echo  AI Kiosk 환경 설치
echo ================================

where python > nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo https://www.python.org 에서 Python 3.12 를 설치해주세요.
    pause
    exit /b 1
)

echo [1/3] 가상환경 생성 중...
if not exist .venv (
    python -m venv .venv
    echo 가상환경 생성 완료
) else (
    echo 가상환경이 이미 존재합니다.
)

echo [2/3] 기본 패키지 설치 중...
call .venv\Scripts\activate.bat
pip install -r kiosk_backend\requirements.txt

echo [3/3] PyTorch GPU 버전 설치 중...
pip install torch transformers --index-url https://download.pytorch.org/whl/cu121

echo.
echo ================================
echo  설치 완료!
echo  start.bat 으로 서버를 시작하세요.
echo ================================
pause
