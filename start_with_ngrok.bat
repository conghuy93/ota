@echo off
chcp 65001 >nul
echo ========================================
echo   OTA Server với ngrok
echo ========================================
echo.

REM Kiểm tra ngrok đã cài chưa
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] ngrok chưa được cài đặt!
    echo.
    echo Cài đặt ngrok:
    echo   1. Download từ: https://ngrok.com/download
    echo   2. Hoặc dùng: choco install ngrok
    echo   3. Hoặc dùng: npm install -g ngrok
    echo.
    pause
    exit /b 1
)

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python chưa được cài đặt!
    pause
    exit /b 1
)

echo [1/3] Đang khởi động OTA Server...
start "OTA Server" cmd /k "cd /d %~dp0server && python main.py"
timeout /t 3 /nobreak >nul

echo [2/3] Đang khởi động ngrok...
start "ngrok" cmd /k "ngrok http 8000"

echo [3/3] Đang mở ngrok dashboard...
timeout /t 2 /nobreak >nul
start http://localhost:4040

echo.
echo ========================================
echo   ✓ Đã khởi động thành công!
echo ========================================
echo.
echo Server local:  http://localhost:8000
echo Ngrok dashboard: http://localhost:4040
echo.
echo Lấy URL công khai từ ngrok dashboard
echo và gửi cho khách hàng!
echo.
echo Nhấn phím bất kỳ để mở Web UI...
pause >nul
start http://localhost:8000

