"""
Ví dụ client kết nối từ xa đến OTA Server
Sử dụng khi server được deploy trên cloud hoặc qua ngrok
"""
from ota_client import OTAClient
import time

# ============================================
# CẤU HÌNH - Thay đổi theo server của bạn
# ============================================

# URL server (thay đổi theo server của bạn)
# Ví dụ với ngrok: "https://abc123.ngrok.io"
# Ví dụ với IP: "http://192.168.1.100:8000"
# Ví dụ với cloud: "https://ota-server.herokuapp.com"
SERVER_URL = "https://abc123.ngrok.io"  # ← THAY ĐỔI URL NÀY

# ID thiết bị
DEVICE_ID = "ESP32_001"

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
    print("OTA Firmware Update Client (Remote)")
    print("=" * 60)
    
    # Kiểm tra URL server
    if "abc123" in SERVER_URL or SERVER_URL == "":
        print("\n⚠️  CẢNH BÁO: Chưa cấu hình SERVER_URL!")
        print("Vui lòng sửa SERVER_URL trong file này.")
        print("\nVí dụ:")
        print("  SERVER_URL = 'https://abc123.ngrok.io'")
        print("  SERVER_URL = 'http://192.168.1.100:8000'")
        return
    
    # Khởi tạo client
    try:
        client = OTAClient(
            server_url=SERVER_URL,
            device_id=DEVICE_ID
        )
        
        # Thiết lập phiên bản hiện tại
        client.set_current_version(CURRENT_VERSION)
        
        print(f"Server: {SERVER_URL}")
        print(f"Device ID: {DEVICE_ID}")
        print(f"Current Version: {CURRENT_VERSION}")
        print("-" * 60)
        
        # Kiểm tra kết nối
        print("Đang kiểm tra kết nối đến server...")
        firmwares = client.list_available_firmwares()
        if "error" in firmwares:
            print(f"✗ Không thể kết nối đến server: {firmwares.get('error')}")
            print("\nKiểm tra:")
            print("  1. Server có đang chạy không?")
            print("  2. URL server đúng chưa?")
            print("  3. Firewall có chặn không?")
            return
        
        print(f"✓ Kết nối thành công! Tìm thấy {firmwares.get('count', 0)} firmware")
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

