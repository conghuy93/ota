@echo off
chcp 65001 >nul
echo ========================================
echo   Push Code lên GitHub cho OTA
echo ========================================
echo.

REM Kiểm tra git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git chưa được cài đặt!
    echo Download từ: https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Kiểm tra đã có remote chưa
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] Chưa có remote GitHub
    echo.
    set /p REPO_URL="Nhập GitHub repo URL (ví dụ: https://github.com/username/ota.git): "
    if "!REPO_URL!"=="" (
        echo [ERROR] Cần nhập repo URL!
        pause
        exit /b 1
    )
    git remote add origin !REPO_URL!
    echo ✓ Đã thêm remote: !REPO_URL!
    echo.
)

REM Add tất cả files
echo [1/4] Đang add files...
git add .
if %errorlevel% neq 0 (
    echo [ERROR] Git add thất bại!
    pause
    exit /b 1
)

REM Commit
echo [2/4] Đang commit...
set /p COMMIT_MSG="Nhập commit message (Enter để dùng mặc định): "
if "!COMMIT_MSG!"=="" set COMMIT_MSG=Update OTA system

git commit -m "!COMMIT_MSG!"
if %errorlevel% neq 0 (
    echo [WARNING] Không có thay đổi để commit hoặc đã commit rồi
)

REM Push
echo [3/4] Đang push lên GitHub...
git branch -M main >nul 2>&1
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push thất bại!
    echo.
    echo Có thể cần:
    echo   1. Tạo repo trên GitHub trước
    echo   2. Set GitHub token
    echo   3. Kiểm tra quyền truy cập
    echo.
    pause
    exit /b 1
)

echo.
echo [4/4] ✓ Hoàn thành!
echo.
echo Code đã được push lên GitHub!
echo.
echo 📥 Raw URLs cho OTA:
git remote get-url origin >temp_url.txt
set /p REPO_URL=<temp_url.txt
del temp_url.txt

REM Extract username/repo từ URL
for /f "tokens=*" %%a in ('echo %REPO_URL%') do set REPO_URL=%%a
set REPO_URL=%REPO_URL:https://github.com/=%
set REPO_URL=%REPO_URL:http://github.com/=%
set REPO_URL=%REPO_URL:.git=%
set REPO_URL=%REPO_URL:/=%

echo   Version: https://raw.githubusercontent.com/%REPO_URL%/main/ota/version.json
echo   Firmware: https://raw.githubusercontent.com/%REPO_URL%/main/ota/firmware/firmware.bin
echo.
pause

