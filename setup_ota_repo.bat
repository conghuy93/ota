@echo off
chcp 65001 >nul
echo ========================================
echo   Setup OTA Repository trên GitHub
echo ========================================
echo.

REM 1. Init git nếu chưa có
if not exist ".git" (
    echo [1/5] Đang init git repository...
    git init
    echo ✓ Đã init git
) else (
    echo [1/5] ✓ Git repository đã có
)

REM 2. Tạo cấu trúc OTA
echo [2/5] Đang tạo cấu trúc OTA...
if not exist "ota\firmware" mkdir ota\firmware
if not exist "ota\version.json" (
    echo {"version": 1} > ota\version.json
    echo ✓ Đã tạo ota/version.json
)
if not exist "ota\README.md" (
    copy /Y github_raw_ota\README.md ota\README.md >nul 2>&1
    echo ✓ Đã tạo ota/README.md
)
echo ✓ Cấu trúc OTA đã sẵn sàng

REM 3. Add files
echo [3/5] Đang add files...
git add .
echo ✓ Đã add files

REM 4. Commit
echo [4/5] Đang commit...
git commit -m "Initial OTA repository setup" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Đã commit
) else (
    echo   Không có thay đổi để commit
)

REM 5. Hướng dẫn
echo [5/5] ✓ Hoàn thành!
echo.
echo 📋 Bước tiếp theo:
echo.
echo 1. Tạo repo trên GitHub:
echo    - Vào: https://github.com/new
echo    - Tên repo: ota (hoặc tên bạn muốn)
echo    - Chọn Public hoặc Private
echo    - KHÔNG tạo README, .gitignore, license
echo    - Click "Create repository"
echo.
echo 2. Push code lên GitHub:
echo    - Chạy: push_to_github.bat
echo    - Hoặc copy URL repo và chạy:
echo      git remote add origin https://github.com/username/ota.git
echo      git push -u origin main
echo.
echo 3. Sau khi push, URLs sẽ là:
echo    Version: https://raw.githubusercontent.com/username/ota/main/ota/version.json
echo    Firmware: https://raw.githubusercontent.com/username/ota/main/ota/firmware/firmware.bin
echo.
pause

