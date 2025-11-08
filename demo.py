"""
Demo script để test OTA system
Tạo file firmware giả và test upload/check/download
"""
import os
import sys
import time
from pathlib import Path

# Thêm thư mục vào path
sys.path.insert(0, str(Path(__file__).parent))

from client.ota_client import OTAClient
import requests

SERVER_URL = "http://localhost:8000"

def create_dummy_firmware(version: str) -> Path:
    """Tạo file firmware giả để test"""
    firmware_dir = Path("firmware")
    firmware_dir.mkdir(exist_ok=True)
    
    file_path = firmware_dir / f"firmware_{version}.bin"
    # Tạo file với nội dung giả
    content = f"FIRMWARE_VERSION_{version}\n".encode() * 1000
    with open(file_path, "wb") as f:
        f.write(content)
    
    print(f"✓ Đã tạo file firmware giả: {file_path} ({len(content)} bytes)")
    return file_path

def test_server():
    """Test server có đang chạy không"""
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            print("✓ Server đang chạy")
            return True
    except:
        pass
    print("✗ Server không chạy. Hãy khởi động server trước!")
    print(f"  Chạy: cd server && python main.py")
    return False

def test_upload(file_path: Path, version: str):
    """Test upload firmware"""
    print(f"\n[TEST] Upload firmware version {version}...")
    try:
        url = f"{SERVER_URL}/api/upload"
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            data = {
                'version': version,
                'description': f'Firmware test version {version}'
            }
            response = requests.post(url, files=files, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"✓ Upload thành công!")
            print(f"  Checksum: {result['firmware_info']['checksum'][:16]}...")
            return True
    except Exception as e:
        print(f"✗ Upload thất bại: {e}")
        return False

def test_check_update(current_version: str):
    """Test check update"""
    print(f"\n[TEST] Kiểm tra update từ version {current_version}...")
    try:
        url = f"{SERVER_URL}/api/check-update"
        payload = {
            "current_version": current_version,
            "device_id": "demo_device"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("update_available"):
            print(f"✓ Có update mới!")
            print(f"  Latest: {data.get('latest_version')}")
        else:
            print(f"✓ Không có update (đã là phiên bản mới nhất)")
        return True
    except Exception as e:
        print(f"✗ Check update thất bại: {e}")
        return False

def test_client():
    """Test OTA client"""
    print(f"\n[TEST] Test OTA Client...")
    try:
        client = OTAClient(SERVER_URL, "demo_device")
        client.set_current_version("1.0.0")
        
        # Kiểm tra update
        update_info = client.check_update()
        print(f"✓ Client check update thành công")
        
        if update_info.get("update_available"):
            fw_info = update_info.get("firmware_info", {})
            print(f"  Có firmware mới: {fw_info.get('version')}")
            
            # Test download
            print(f"  Đang tải firmware...")
            file_path = client.download_firmware(fw_info.get('version'))
            if file_path:
                print(f"✓ Download thành công: {file_path}")
                
                # Test checksum
                if client.verify_checksum(file_path, fw_info.get('checksum')):
                    print(f"✓ Checksum hợp lệ")
                else:
                    print(f"✗ Checksum không khớp")
        else:
            print(f"  Không có update mới")
        
        return True
    except Exception as e:
        print(f"✗ Client test thất bại: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("OTA System Demo")
    print("=" * 60)
    
    # Test server
    if not test_server():
        return
    
    # Tạo firmware giả
    print("\n[STEP 1] Tạo firmware giả...")
    fw_v1 = create_dummy_firmware("1.0.0")
    fw_v2 = create_dummy_firmware("1.0.1")
    fw_v3 = create_dummy_firmware("1.1.0")
    
    # Upload firmware
    print("\n[STEP 2] Upload firmware...")
    test_upload(fw_v1, "1.0.0")
    time.sleep(1)
    test_upload(fw_v2, "1.0.1")
    time.sleep(1)
    test_upload(fw_v3, "1.1.0")
    
    # Test check update
    print("\n[STEP 3] Test check update...")
    test_check_update("1.0.0")
    test_check_update("1.1.0")
    
    # Test client
    print("\n[STEP 4] Test OTA Client...")
    test_client()
    
    print("\n" + "=" * 60)
    print("Demo hoàn thành!")
    print("=" * 60)
    print("\nĐể xem danh sách firmware:")
    print("  python utils/list_firmwares.py")
    print("\nĐể test từ thiết bị:")
    print("  python utils/check_update.py 1.0.0")

if __name__ == "__main__":
    main()

