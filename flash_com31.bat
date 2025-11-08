@echo off
chcp 65001 >nul
echo ========================================
echo   ESP32 Flash Tool - COM31
echo ========================================
echo.

REM Kiểm tra esptool
python -c "import esptool" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] esptool chưa được cài đặt!
    echo.
    echo Cài đặt:
    echo   pip install esptool
    echo.
    pause
    exit /b 1
)

REM Tìm file firmware
if exist "ota\firmware\firmware.bin" (
    set FIRMWARE=ota\firmware\firmware.bin
) else if exist "firmware.bin" (
    set FIRMWARE=firmware.bin
) else (
    echo [ERROR] Không tìm thấy file firmware.bin!
    echo.
    echo Tìm trong:
    echo   - ota\firmware\firmware.bin
    echo   - firmware.bin
    echo.
    pause
    exit /b 1
)

echo [INFO] Firmware: %FIRMWARE%
echo [INFO] Port: COM31
echo.

REM Flash firmware
python utils\flash_esp32.py "%FIRMWARE%" -p COM31

echo.
pause

