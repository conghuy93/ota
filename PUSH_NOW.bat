@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   Push Code lên GitHub - OTA System
echo ========================================
echo.

REM Kiểm tra git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git chưa được cài đặt!
    pause
    exit /b 1
)

REM Kiểm tra đã có remote chưa
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] Chưa có remote GitHub
    echo.
    echo Vui lòng tạo repo trên GitHub trước:
    echo   1. Vào: https://github.com/new
    echo   2. Tên repo: ota (hoặc tên bạn muốn)
    echo   3. Chọn Public hoặc Private
    echo   4. KHÔNG tích README, .gitignore, license
    echo   5. Click "Create repository"
    echo.
    set /p REPO_URL="Nhập GitHub repo URL (ví dụ: https://github.com/conghuy93/ota.git): "
    if "!REPO_URL!"=="" (
        echo [ERROR] Cần nhập repo URL!
        pause
        exit /b 1
    )
    git remote add origin !REPO_URL!
    echo ✓ Đã thêm remote
    echo.
)

REM Add và commit
echo [1/3] Đang add files...
git add .
echo ✓ Đã add

echo [2/3] Đang commit...
git commit -m "Update OTA system" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Đã commit
) else (
    echo   Không có thay đổi để commit
)

REM Push
echo [3/3] Đang push lên GitHub...
git branch -M main >nul 2>&1
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push thất bại!
    echo.
    echo Có thể cần:
    echo   1. Tạo repo trên GitHub trước
    echo   2. Set GitHub token (set_github_token.bat)
    echo   3. Kiểm tra quyền truy cập
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✓ HOÀN THÀNH!
echo ========================================
echo.
echo Code đã được push lên GitHub!
echo.

REM Lấy repo URL
for /f "tokens=*" %%a in ('git remote get-url origin') do set REPO_URL=%%a
set REPO_URL=!REPO_URL:https://github.com/=!
set REPO_URL=!REPO_URL:http://github.com/=!
set REPO_URL=!REPO_URL:.git=!

echo 📥 URLs cho OTA:
echo.
echo   Version:
echo   https://raw.githubusercontent.com/!REPO_URL!/main/ota/version.json
echo.
echo   Firmware:
echo   https://raw.githubusercontent.com/!REPO_URL!/main/ota/firmware/firmware.bin
echo.
echo 📋 Bước tiếp theo:
echo   1. Upload firmware.bin vào ota/firmware/
echo   2. Update version trong ota/version.json
echo   3. Commit và push
echo   4. ESP32 sẽ tự động update!
echo.
pause

