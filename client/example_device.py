"""
Ví dụ sử dụng OTA Client trên thiết bị
"""
import time
from ota_client import OTAClient

# Cấu hình
SERVER_URL = "http://192.168.1.100:8000"  # Thay đổi theo IP server của bạn
DEVICE_ID = "ESP32_001"
CURRENT_VERSION = "1.0.0"  # Phiên bản hiện tại của thiết bị

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
    # Ví dụ: os.system(f"flash_tool {target_path}")
    
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

def main():
    """Hàm chính - chạy kiểm tra và update firmware"""
    print("=" * 50)
    print("OTA Firmware Update Client")
    print("=" * 50)
    
    # Khởi tạo client
    client = OTAClient(
        server_url=SERVER_URL,
        device_id=DEVICE_ID
    )
    
    # Thiết lập phiên bản hiện tại
    client.set_current_version(CURRENT_VERSION)
    
    print(f"Server: {SERVER_URL}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Current Version: {CURRENT_VERSION}")
    print("-" * 50)
    
    # Kiểm tra và cập nhật
    try:
        result = client.update_firmware(
            install_callback=install_firmware,
            progress_callback=progress_callback
        )
        
        print("\n" + "=" * 50)
        if result.get("success"):
            print("✓ Cập nhật thành công!")
            print(f"  Phiên bản mới: {result.get('new_version')}")
        else:
            print("✗ Cập nhật thất bại")
            print(f"  Lý do: {result.get('message')}")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\nĐã hủy bởi người dùng")
    except Exception as e:
        print(f"\n\nLỗi: {e}")

if __name__ == "__main__":
    # Chạy kiểm tra update mỗi 5 phút
    import schedule
    
    def check_and_update():
        main()
    
    # Chạy ngay lập tức
    check_and_update()
    
    # Lên lịch kiểm tra định kỳ (mỗi 5 phút)
    schedule.every(5).minutes.do(check_and_update)
    
    print("\nĐang chạy ở chế độ định kỳ (kiểm tra mỗi 5 phút)...")
    print("Nhấn Ctrl+C để dừng")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐã dừng")

