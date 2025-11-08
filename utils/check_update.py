"""
Utility script để kiểm tra update từ client
"""
import requests
import sys
import argparse

def check_update(server_url: str, current_version: str, device_id: str = None):
    """
    Kiểm tra có firmware mới không
    
    Args:
        server_url: URL của OTA server
        current_version: Phiên bản hiện tại
        device_id: ID thiết bị (tùy chọn)
    """
    try:
        url = f"{server_url.rstrip('/')}/api/check-update"
        payload = {
            "current_version": current_version,
            "device_id": device_id
        }
        
        print(f"Đang kiểm tra update...")
        print(f"  Server: {server_url}")
        print(f"  Current Version: {current_version}")
        if device_id:
            print(f"  Device ID: {device_id}")
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        print("\n" + "=" * 60)
        if data.get("update_available"):
            print("✓ Có firmware mới!")
            print(f"  Phiên bản hiện tại: {data.get('current_version')}")
            print(f"  Phiên bản mới: {data.get('latest_version')}")
            
            fw_info = data.get("firmware_info", {})
            print(f"\nThông tin firmware:")
            print(f"  Version: {fw_info.get('version')}")
            print(f"  Size: {fw_info.get('size'):,} bytes")
            print(f"  Checksum: {fw_info.get('checksum')}")
            if fw_info.get('description'):
                print(f"  Mô tả: {fw_info.get('description')}")
            print(f"  Download URL: {server_url}{fw_info.get('download_url')}")
        else:
            print("✗ Không có update mới")
            print(f"  Phiên bản hiện tại: {data.get('current_version')}")
            if data.get('latest_version'):
                print(f"  Phiên bản mới nhất: {data.get('latest_version')}")
            if data.get('message'):
                print(f"  {data.get('message')}")
        
        print("=" * 60)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi kiểm tra update: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Kiểm tra update từ OTA server')
    parser.add_argument('current_version', help='Phiên bản hiện tại (ví dụ: 1.0.0)')
    parser.add_argument('-s', '--server', default='http://localhost:8000',
                       help='URL của OTA server (mặc định: http://localhost:8000)')
    parser.add_argument('-d', '--device-id', default=None,
                       help='ID thiết bị (tùy chọn)')
    
    args = parser.parse_args()
    check_update(args.server, args.current_version, args.device_id)

if __name__ == "__main__":
    main()

