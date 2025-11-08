"""
Ví dụ sử dụng GitHub OTA Client
Khách hàng chỉ cần thay đổi REPO và chạy
"""
from github_ota_client import GitHubOTAClient
import time

# ============================================
# CẤU HÌNH - Thay đổi theo repo của bạn
# ============================================

# GitHub repo (ví dụ: "username/repo-name")
REPO = "username/repo-name"  # ← THAY ĐỔI REPO NÀY

# GitHub token (chỉ cần nếu repo là private)
# Lấy tại: https://github.com/settings/tokens
TOKEN = None  # ← Thêm token nếu repo private

# Phiên bản hiện tại của thiết bị
CURRENT_VERSION = "1.0.0"

# ============================================
# Hàm cài đặt firmware
# ============================================

def install_firmware(file_path):
    """
    Hàm cài đặt firmware
    Thay đổi logic này theo thiết bị của bạn
    """
    print(f"\n[INSTALL] Bắt đầu cài đặt firmware từ: {file_path}")
    
    # Ví dụ cho ESP32/ESP8266:
    # - Copy file vào thư mục firmware
    # - Khởi động lại thiết bị
    # - Flash firmware vào bộ nhớ
    
    # Ví dụ cho Linux device:
    # - Copy file vào /tmp
    # - Chạy script cài đặt
    # - Khởi động lại service
    
    import shutil
    import os
    
    target_path = f"/tmp/firmware_{int(time.time())}.bin"
    shutil.copy(file_path, target_path)
    
    print(f"[INSTALL] Firmware đã được copy đến: {target_path}")
    print("[INSTALL] Thực hiện flash firmware...")
    
    # TODO: Thêm logic flash firmware thực tế ở đây
    # Ví dụ cho ESP32:
    #   os.system(f"esptool.py --port /dev/ttyUSB0 write_flash 0x1000 {target_path}")
    
    # Ví dụ cho Linux:
    #   os.system(f"flash_tool {target_path}")
    
    print("[INSTALL] Hoàn thành! Thiết bị sẽ khởi động lại...")
    # os.system("reboot")

def progress_callback(downloaded, total):
    """Hiển thị tiến trình tải"""
    if total > 0:
        percent = (downloaded / total) * 100
        bar_length = 40
        filled = int(bar_length * downloaded // total)
        bar = '=' * filled + '-' * (bar_length - filled)
        print(f"\r[{bar}] {percent:.1f}% ({downloaded}/{total} bytes)", end="", flush=True)

# ============================================
# Hàm chính
# ============================================

def main():
    """Hàm chính - chạy kiểm tra và update firmware"""
    print("=" * 60)
    print("GitHub OTA Firmware Update Client")
    print("=" * 60)
    
    # Kiểm tra cấu hình
    if "username" in REPO or REPO == "":
        print("\n⚠️  CẢNH BÁO: Chưa cấu hình REPO!")
        print("Vui lòng sửa REPO trong file này.")
        print("\nVí dụ:")
        print("  REPO = 'conghuy93/firmware-releases'")
        return
    
    # Khởi tạo client
    try:
        client = GitHubOTAClient(
            repo=REPO,
            token=TOKEN
        )
        
        # Thiết lập phiên bản hiện tại
        client.set_current_version(CURRENT_VERSION)
        
        print(f"GitHub Repo: {REPO}")
        print(f"Current Version: {CURRENT_VERSION}")
        print("-" * 60)
        
        # Kiểm tra kết nối
        print("Đang kiểm tra kết nối đến GitHub...")
        release = client.get_latest_release()
        
        if not release:
            print("✗ Không thể kết nối đến GitHub!")
            print("\nKiểm tra:")
            print("  1. Repo name đúng chưa?")
            print("  2. Repo có public không? (nếu private cần TOKEN)")
            print("  3. Có release nào trong repo không?")
            return
        
        print(f"✓ Kết nối thành công!")
        print(f"  Latest Release: {release.get('tag_name')}")
        print(f"  Release Name: {release.get('name')}")
        print("-" * 60)
        
        # Kiểm tra và cập nhật
        result = client.update_firmware(
            install_callback=install_firmware,
            progress_callback=progress_callback
        )
        
        print("\n" + "=" * 60)
        if result.get("success"):
            print("✓ Cập nhật thành công!")
            print(f"  Phiên bản mới: {result.get('new_version')}")
            if result.get("needs_manual_install"):
                print("  ⚠️  Cần cài đặt firmware thủ công")
        else:
            print("✗ Cập nhật thất bại")
            print(f"  Lý do: {result.get('message')}")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nĐã hủy bởi người dùng")
    except Exception as e:
        print(f"\n\nLỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Chạy một lần
    main()
    
    # Hoặc chạy định kỳ (uncomment để bật)
    # import schedule
    # schedule.every(5).minutes.do(main)
    # 
    # print("\nĐang chạy ở chế độ định kỳ (kiểm tra mỗi 5 phút)...")
    # print("Nhấn Ctrl+C để dừng")
    # 
    # try:
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("\nĐã dừng")

