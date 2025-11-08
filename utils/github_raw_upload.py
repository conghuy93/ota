"""
Script để upload firmware và update version.json lên GitHub
Sử dụng GitHub API để commit file trực tiếp
"""
import requests
import base64
import json
import sys
import argparse
import os
from pathlib import Path

def upload_file_to_github(
    repo: str,
    token: str,
    file_path: str,
    github_path: str,
    commit_message: str = "Update firmware"
):
    """
    Upload file lên GitHub repo
    
    Args:
        repo: Tên repo (ví dụ: "username/repo-name")
        token: GitHub Personal Access Token
        file_path: Đường dẫn file local
        github_path: Đường dẫn trên GitHub (ví dụ: "ota/firmware/firmware.bin")
        commit_message: Commit message
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File không tồn tại: {file_path}")
        return False
    
    # Đọc file và encode base64
    with open(file_path, 'rb') as f:
        content = f.read()
        content_b64 = base64.b64encode(content).decode('utf-8')
    
    # GitHub API
    api_url = f"https://api.github.com/repos/{repo}/contents/{github_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Kiểm tra file đã tồn tại chưa
    response = requests.get(api_url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get("sha")
        print(f"✓ File đã tồn tại, sẽ update...")
    elif response.status_code != 404:
        print(f"❌ Lỗi khi kiểm tra file: {response.text}")
        return False
    
    # Upload file
    data = {
        "message": commit_message,
        "content": content_b64,
        "branch": "main"  # Hoặc "master" tùy repo
    }
    
    if sha:
        data["sha"] = sha
    
    response = requests.put(api_url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"✓ Upload thành công!")
        print(f"  File: {github_path}")
        print(f"  Size: {len(content):,} bytes")
        print(f"  Commit: {result.get('commit', {}).get('sha', 'N/A')[:8]}")
        print(f"  URL: {result.get('content', {}).get('download_url', 'N/A')}")
        return True
    else:
        print(f"❌ Lỗi khi upload: {response.text}")
        return False

def update_version(repo: str, token: str, new_version: int, branch: str = "main"):
    """
    Update version trong version.json
    
    Args:
        repo: Tên repo
        token: GitHub token
        new_version: Version mới
        branch: Branch name
    """
    version_path = "ota/version.json"
    api_url = f"https://api.github.com/repos/{repo}/contents/{version_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Lấy file hiện tại
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Không tìm thấy version.json: {response.text}")
        return False
    
    file_data = response.json()
    current_content = base64.b64decode(file_data["content"]).decode('utf-8')
    current_version_data = json.loads(current_content)
    
    # Update version
    current_version_data["version"] = new_version
    new_content = json.dumps(current_version_data, indent=2)
    new_content_b64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    
    # Commit
    data = {
        "message": f"Update version to {new_version}",
        "content": new_content_b64,
        "sha": file_data["sha"],
        "branch": branch
    }
    
    response = requests.put(api_url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✓ Version updated: {current_version_data.get('version')} → {new_version}")
        return True
    else:
        print(f"❌ Lỗi khi update version: {response.text}")
        return False

def upload_firmware_and_version(
    repo: str,
    token: str,
    firmware_path: str,
    new_version: int = None,
    branch: str = "main"
):
    """
    Upload firmware và tự động tăng version
    """
    # Upload firmware
    print(f"📤 Uploading firmware...")
    success = upload_file_to_github(
        repo=repo,
        token=token,
        file_path=firmware_path,
        github_path="ota/firmware/firmware.bin",
        commit_message="Update firmware"
    )
    
    if not success:
        return False
    
    # Update version nếu có
    if new_version:
        print(f"\n📝 Updating version to {new_version}...")
        update_version(repo, token, new_version, branch)
    
    print(f"\n✅ Hoàn thành!")
    print(f"\n📥 Raw URLs:")
    print(f"  Version: https://raw.githubusercontent.com/{repo}/{branch}/ota/version.json")
    print(f"  Firmware: https://raw.githubusercontent.com/{repo}/{branch}/ota/firmware/firmware.bin")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Upload firmware và update version lên GitHub'
    )
    parser.add_argument('firmware', help='Đường dẫn đến file firmware.bin')
    parser.add_argument('-r', '--repo', required=True,
                       help='GitHub repo (ví dụ: username/repo-name)')
    parser.add_argument('-t', '--token',
                       default=os.getenv('GITHUB_TOKEN'),
                       help='GitHub Personal Access Token')
    parser.add_argument('-v', '--version', type=int,
                       help='Version mới (tự động tăng nếu không chỉ định)')
    parser.add_argument('-b', '--branch', default='main',
                       help='Branch name (default: main)')
    
    args = parser.parse_args()
    
    if not args.token:
        print("❌ Lỗi: Cần GitHub Token!")
        print("\nCách lấy token:")
        print("  1. Vào: https://github.com/settings/tokens")
        print("  2. Tạo token mới với quyền 'repo'")
        print("  3. Set environment variable: set GITHUB_TOKEN=your_token")
        print("     Hoặc dùng: -t your_token")
        sys.exit(1)
    
    # Nếu không chỉ định version, tự động tăng
    if not args.version:
        # Lấy version hiện tại
        try:
            api_url = f"https://api.github.com/repos/{args.repo}/contents/ota/version.json"
            headers = {"Authorization": f"token {args.token}"}
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json()["content"]).decode('utf-8')
                current_version = json.loads(content).get("version", 0)
                args.version = current_version + 1
                print(f"📊 Tự động tăng version: {current_version} → {args.version}")
            else:
                args.version = 1
                print(f"📊 Không tìm thấy version.json, bắt đầu từ version 1")
        except:
            args.version = 1
            print(f"📊 Bắt đầu từ version 1")
    
    success = upload_firmware_and_version(
        repo=args.repo,
        token=args.token,
        firmware_path=args.firmware,
        new_version=args.version,
        branch=args.branch
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

