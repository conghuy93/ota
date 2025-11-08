"""
Utility script để liệt kê firmware có sẵn trên server
"""
import requests
import sys
import argparse
from datetime import datetime

def list_firmwares(server_url: str):
    """
    Liệt kê tất cả firmware có sẵn
    
    Args:
        server_url: URL của OTA server
    """
    try:
        url = f"{server_url.rstrip('/')}/api/firmwares"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        firmwares = data.get("firmwares", [])
        
        print(f"\nDanh sách firmware có sẵn ({len(firmwares)}):")
        print("=" * 80)
        
        if not firmwares:
            print("Không có firmware nào")
            return
        
        for fw in sorted(firmwares, key=lambda x: x["version"], reverse=True):
            print(f"\nVersion: {fw['version']}")
            print(f"  File: {fw['filename']}")
            print(f"  Size: {fw['size']:,} bytes ({fw['size'] / 1024:.2f} KB)")
            print(f"  Checksum: {fw['checksum']}")
            if fw.get('description'):
                print(f"  Mô tả: {fw['description']}")
            if fw.get('release_date'):
                try:
                    date = datetime.fromisoformat(fw['release_date'].replace('Z', '+00:00'))
                    print(f"  Ngày phát hành: {date.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    print(f"  Ngày phát hành: {fw['release_date']}")
            print(f"  Download: {server_url}/api/download/{fw['version']}")
        
        print("\n" + "=" * 80)
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy danh sách firmware: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Liệt kê firmware có sẵn trên OTA server')
    parser.add_argument('-s', '--server', default='http://localhost:8000',
                       help='URL của OTA server (mặc định: http://localhost:8000)')
    
    args = parser.parse_args()
    list_firmwares(args.server)

if __name__ == "__main__":
    main()

