"""
Script để upload firmware lên GitHub Releases
Sử dụng GitHub API để tạo release và upload file
"""
import requests
import sys
import argparse
import os
from pathlib import Path
import json

def upload_to_github_release(
    repo: str,
    token: str,
    tag: str,
    file_path: str,
    release_name: str = None,
    description: str = "",
    draft: bool = False,
    prerelease: bool = False
):
    """
    Upload firmware lên GitHub Release
    
    Args:
        repo: Tên repo (ví dụ: "username/repo-name")
        token: GitHub Personal Access Token
        tag: Tag version (ví dụ: "v1.0.1")
        file_path: Đường dẫn đến file firmware
        release_name: Tên release (mặc định = tag)
        description: Mô tả release
        draft: Tạo draft release
        prerelease: Đánh dấu là pre-release
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File không tồn tại: {file_path}")
        return False
    
    # GitHub API base URL
    api_base = f"https://api.github.com/repos/{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print(f"📦 Đang upload firmware lên GitHub...")
    print(f"   Repo: {repo}")
    print(f"   Tag: {tag}")
    print(f"   File: {file_path.name} ({file_path.stat().st_size:,} bytes)")
    
    # 1. Kiểm tra release đã tồn tại chưa
    print("\n[1/3] Kiểm tra release...")
    release_url = f"{api_base}/releases/tags/{tag}"
    response = requests.get(release_url, headers=headers)
    
    if response.status_code == 200:
        # Release đã tồn tại
        release_id = response.json()["id"]
        print(f"   ✓ Release đã tồn tại (ID: {release_id})")
        
        # Xóa asset cũ nếu có cùng tên
        assets_url = f"{api_base}/releases/{release_id}/assets"
        assets = requests.get(assets_url, headers=headers).json()
        for asset in assets:
            if asset["name"] == file_path.name:
                print(f"   🗑️  Xóa asset cũ: {asset['name']}")
                requests.delete(
                    f"{api_base}/releases/assets/{asset['id']}",
                    headers=headers
                )
    else:
        # Tạo release mới
        print(f"   ➕ Tạo release mới...")
        release_data = {
            "tag_name": tag,
            "name": release_name or tag,
            "body": description or f"Firmware version {tag}",
            "draft": draft,
            "prerelease": prerelease
        }
        
        response = requests.post(
            f"{api_base}/releases",
            headers=headers,
            json=release_data
        )
        
        if response.status_code not in [200, 201]:
            print(f"   ❌ Lỗi khi tạo release: {response.text}")
            return False
        
        release_id = response.json()["id"]
        print(f"   ✓ Đã tạo release (ID: {release_id})")
    
    # 2. Upload file
    print(f"\n[2/3] Đang upload file...")
    upload_url = f"{api_base}/releases/{release_id}/assets"
    
    with open(file_path, 'rb') as f:
        headers_upload = {
            "Authorization": f"token {token}",
            "Content-Type": "application/octet-stream"
        }
        
        params = {"name": file_path.name}
        
        response = requests.post(
            upload_url,
            headers=headers_upload,
            params=params,
            data=f,
            timeout=60
        )
    
    if response.status_code == 201:
        asset = response.json()
        print(f"   ✓ Upload thành công!")
        print(f"\n[3/3] Thông tin:")
        print(f"   📥 Download URL: {asset['browser_download_url']}")
        print(f"   📦 Release URL: https://github.com/{repo}/releases/tag/{tag}")
        print(f"   📊 Size: {asset['size']:,} bytes")
        return True
    else:
        print(f"   ❌ Lỗi khi upload: {response.text}")
        return False

def get_latest_release(repo: str, token: str = None):
    """
    Lấy thông tin release mới nhất
    """
    api_base = f"https://api.github.com/repos/{repo}"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    response = requests.get(f"{api_base}/releases/latest", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None

def main():
    parser = argparse.ArgumentParser(
        description='Upload firmware lên GitHub Releases'
    )
    parser.add_argument('file', help='Đường dẫn đến file firmware')
    parser.add_argument('tag', help='Tag version (ví dụ: v1.0.1)')
    parser.add_argument('-r', '--repo', required=True,
                       help='GitHub repo (ví dụ: username/repo-name)')
    parser.add_argument('-t', '--token', 
                       default=os.getenv('GITHUB_TOKEN'),
                       help='GitHub Personal Access Token (hoặc set GITHUB_TOKEN env)')
    parser.add_argument('-n', '--name', 
                       help='Tên release (mặc định = tag)')
    parser.add_argument('-d', '--description', default='',
                       help='Mô tả release')
    parser.add_argument('--draft', action='store_true',
                       help='Tạo draft release')
    parser.add_argument('--prerelease', action='store_true',
                       help='Đánh dấu là pre-release')
    
    args = parser.parse_args()
    
    if not args.token:
        print("❌ Lỗi: Cần GitHub Token!")
        print("\nCách lấy token:")
        print("  1. Vào: https://github.com/settings/tokens")
        print("  2. Tạo token mới với quyền 'repo'")
        print("  3. Set environment variable: set GITHUB_TOKEN=your_token")
        print("     Hoặc dùng: -t your_token")
        sys.exit(1)
    
    success = upload_to_github_release(
        repo=args.repo,
        token=args.token,
        tag=args.tag,
        file_path=args.file,
        release_name=args.name,
        description=args.description,
        draft=args.draft,
        prerelease=args.prerelease
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

