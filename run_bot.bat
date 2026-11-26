@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".env" (
    echo [!] .env fayli topilmadi. .env.example ni nusxalab .env deb nomlang va BOT_TOKEN ni yozing.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Virtual muhit yaratilmoqda...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo Bot ishga tushmoqda... To'xtatish uchun Ctrl+C
python bot.py
pause
