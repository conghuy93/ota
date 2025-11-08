"""
Utility script để upload firmware lên OTA server
"""
import requests
import sys
import argparse
from pathlib import Path

def upload_firmware(server_url: str, file_path: str, version: str, description: str = ""):
    """
    Upload firmware lên server
    
    Args:
        server_url: URL của OTA server
        file_path: Đường dẫn đến file firmware
        version: Phiên bản firmware
        description: Mô tả firmware
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Lỗi: File không tồn tại: {file_path}")
        return False
    
    print(f"Đang upload firmware...")
    print(f"  File: {file_path}")
    print(f"  Version: {version}")
    print(f"  Server: {server_url}")
    
    try:
        url = f"{server_url.rstrip('/')}/api/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            data = {
                'version': version,
                'description': description
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            print(f"\n✓ Upload thành công!")
            print(f"  Version: {result['firmware_info']['version']}")
            print(f"  Size: {result['firmware_info']['size']} bytes")
            print(f"  Checksum: {result['firmware_info']['checksum']}")
            
            return True
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Lỗi khi upload: {e}")
        if hasattr(e.response, 'text'):
            print(f"  Chi tiết: {e.response.text}")
        return False
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload firmware lên OTA server')
    parser.add_argument('file', help='Đường dẫn đến file firmware')
    parser.add_argument('version', help='Phiên bản firmware (ví dụ: 1.0.1)')
    parser.add_argument('-s', '--server', default='http://localhost:8000',
                       help='URL của OTA server (mặc định: http://localhost:8000)')
    parser.add_argument('-d', '--description', default='',
                       help='Mô tả firmware')
    
    args = parser.parse_args()
    
    success = upload_firmware(
        server_url=args.server,
        file_path=args.file,
        version=args.version,
        description=args.description
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

