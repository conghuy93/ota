@echo off
chcp 65001 >nul
echo ========================================
echo   Auto Build and Flash ESP32
echo ========================================
echo.

REM Cấu hình
set SKETCH=example\esp32_ota_example.ino
set PORT=COM31
set REPO=username/ota
set TOKEN=%GITHUB_TOKEN%

REM Kiểm tra sketch
if not exist "%SKETCH%" (
    echo [ERROR] Không tìm thấy sketch: %SKETCH%
    pause
    exit /b 1
)

echo [INFO] Sketch: %SKETCH%
echo [INFO] Port: %PORT%
if not "%REPO%"=="" (
    echo [INFO] GitHub Repo: %REPO%
)
echo.

REM Chạy auto build và flash
python utils\auto_build_flash.py "%SKETCH%" -p %PORT% -r %REPO% -t %TOKEN%

echo.
pause

