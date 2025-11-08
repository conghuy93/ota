"""
Ví dụ sử dụng Auto OTA Client
Thiết bị tự động kiểm tra và cập nhật firmware
"""
from auto_ota_client import AutoOTAClient
import time

# ============================================
# CẤU HÌNH
# ============================================

SERVER_URL = "http://localhost:8000"  # Hoặc URL server của bạn
DEVICE_ID = "ESP32_001"
DEVICE_TOKEN = None  # Thêm token nếu server yêu cầu auth
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
    # import esptool
    # esptool.write_flash(0x1000, str(file_path))
    
    # Ví dụ cho Linux device:
    # import shutil
    # shutil.copy(file_path, "/tmp/firmware.bin")
    # os.system("flash_tool /tmp/firmware.bin")
    # os.system("reboot")
    
    print(f"[INSTALL] Firmware đã được cài đặt!")
    print("[INSTALL] Thiết bị sẽ khởi động lại...")
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
    print("=" * 60)
    print("Auto OTA Client - Tự động cập nhật firmware")
    print("=" * 60)
    
    # Khởi tạo Auto OTA Client
    auto_client = AutoOTAClient(
        server_url=SERVER_URL,
        device_id=DEVICE_ID,
        device_token=DEVICE_TOKEN,
        check_interval_minutes=60,  # Kiểm tra mỗi 60 phút
        auto_install=True  # Tự động cài đặt
    )
    
    # Thiết lập phiên bản hiện tại
    auto_client.set_current_version(CURRENT_VERSION)
    
    # Thiết lập callbacks
    auto_client.set_install_callback(install_firmware)
    auto_client.set_progress_callback(progress_callback)
    
    print(f"Server: {SERVER_URL}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Current Version: {CURRENT_VERSION}")
    print(f"Check Interval: 60 minutes")
    print("-" * 60)
    
    # Bắt đầu tự động kiểm tra
    auto_client.start()
    
    print("\n✓ Auto OTA Client đã khởi động!")
    print("Thiết bị sẽ tự động kiểm tra và cập nhật firmware.")
    print("Nhấn Ctrl+C để dừng.\n")
    
    # Giữ chương trình chạy
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nĐang dừng Auto OTA Client...")
        auto_client.stop()
        print("Đã dừng.")

if __name__ == "__main__":
    main()

