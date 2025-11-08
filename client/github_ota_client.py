"""
OTA Client để tải firmware từ GitHub Releases
Khách hàng có thể tự cập nhật bằng link GitHub
"""
import requests
import hashlib
from pathlib import Path
from typing import Optional, Callable, Dict
import re

class GitHubOTAClient:
    """Client để tải firmware từ GitHub Releases"""
    
    def __init__(self, repo: str, token: Optional[str] = None):
        """
        Khởi tạo GitHub OTA Client
        
        Args:
            repo: Tên repo GitHub (ví dụ: "username/repo-name")
            token: GitHub token (tùy chọn, cần cho private repo)
        """
        self.repo = repo
        self.token = token
        self.api_base = f"https://api.github.com/repos/{repo}"
        self.download_dir = Path("downloads")
        self.download_dir.mkdir(exist_ok=True)
        self.current_version = "0.0.0"
    
    def set_current_version(self, version: str):
        """Thiết lập phiên bản hiện tại"""
        self.current_version = version
    
    def get_headers(self):
        """Lấy headers cho API request"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def get_latest_release(self) -> Optional[Dict]:
        """
        Lấy thông tin release mới nhất
        
        Returns:
            Dict chứa thông tin release hoặc None
        """
        try:
            url = f"{self.api_base}/releases/latest"
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy release: {e}")
            return None
    
    def get_release_by_tag(self, tag: str) -> Optional[Dict]:
        """
        Lấy thông tin release theo tag
        
        Args:
            tag: Tag version (ví dụ: "v1.0.1")
        """
        try:
            url = f"{self.api_base}/releases/tags/{tag}"
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy release: {e}")
            return None
    
    def list_releases(self) -> list:
        """Liệt kê tất cả releases"""
        try:
            url = f"{self.api_base}/releases"
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy danh sách releases: {e}")
            return []
    
    def extract_version_from_tag(self, tag: str) -> str:
        """Trích xuất version từ tag (ví dụ: "v1.0.1" -> "1.0.1")"""
        # Loại bỏ "v" prefix nếu có
        version = tag.lstrip('vV')
        return version
    
    def compare_versions(self, v1: str, v2: str) -> int:
        """So sánh 2 phiên bản"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        return 0
    
    def find_firmware_asset(self, release: Dict) -> Optional[Dict]:
        """
        Tìm file firmware trong release assets
        Tự động tìm file .bin, .hex, .elf
        """
        assets = release.get("assets", [])
        firmware_extensions = ['.bin', '.hex', '.elf', '.fw']
        
        for asset in assets:
            name = asset.get("name", "").lower()
            if any(name.endswith(ext) for ext in firmware_extensions):
                return asset
        
        # Nếu không tìm thấy, lấy asset đầu tiên
        if assets:
            return assets[0]
        
        return None
    
    def check_update(self) -> Dict:
        """
        Kiểm tra có firmware mới không
        
        Returns:
            Dict chứa thông tin update
        """
        release = self.get_latest_release()
        
        if not release:
            return {
                "update_available": False,
                "error": "Không thể lấy thông tin release"
            }
        
        tag = release.get("tag_name", "")
        latest_version = self.extract_version_from_tag(tag)
        
        # So sánh version
        if self.compare_versions(latest_version, self.current_version) > 0:
            asset = self.find_firmware_asset(release)
            
            if not asset:
                return {
                    "update_available": False,
                    "error": "Không tìm thấy file firmware trong release"
                }
            
            return {
                "update_available": True,
                "latest_version": latest_version,
                "current_version": self.current_version,
                "tag": tag,
                "release_name": release.get("name", tag),
                "release_url": release.get("html_url", ""),
                "firmware_info": {
                    "name": asset.get("name", ""),
                    "size": asset.get("size", 0),
                    "download_url": asset.get("browser_download_url", ""),
                    "download_count": asset.get("download_count", 0)
                },
                "release_notes": release.get("body", "")
            }
        else:
            return {
                "update_available": False,
                "current_version": self.current_version,
                "latest_version": latest_version,
                "message": "Đã sử dụng phiên bản mới nhất"
            }
    
    def download_firmware(self, 
                          download_url: str,
                          filename: Optional[str] = None,
                          progress_callback: Optional[Callable] = None) -> Optional[Path]:
        """
        Tải firmware từ GitHub
        
        Args:
            download_url: URL download từ GitHub
            filename: Tên file (mặc định lấy từ URL)
            progress_callback: Callback hiển thị tiến trình
        """
        try:
            # Lấy filename từ URL nếu chưa có
            if not filename:
                filename = download_url.split('/')[-1].split('?')[0]
            
            file_path = self.download_dir / filename
            
            print(f"Đang tải firmware từ GitHub...")
            print(f"  URL: {download_url}")
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            print(f"✓ Đã tải: {file_path} ({downloaded:,} bytes)")
            return file_path
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Lỗi khi tải firmware: {e}")
            return None
    
    def verify_checksum(self, file_path: Path, expected_checksum: str) -> bool:
        """Xác minh checksum SHA256"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            calculated = sha256_hash.hexdigest()
            return calculated.lower() == expected_checksum.lower()
        except Exception as e:
            print(f"Lỗi khi xác minh checksum: {e}")
            return False
    
    def update_firmware(self,
                       install_callback: Optional[Callable] = None,
                       progress_callback: Optional[Callable] = None) -> Dict:
        """
        Kiểm tra và cập nhật firmware tự động
        
        Args:
            install_callback: Hàm cài đặt firmware
            progress_callback: Hàm hiển thị tiến trình
        """
        print(f"Đang kiểm tra update từ GitHub: {self.repo}...")
        
        update_info = self.check_update()
        
        if not update_info.get("update_available", False):
            print(f"Không có update mới. Phiên bản hiện tại: {self.current_version}")
            return {
                "success": False,
                "message": "Không có update mới",
                "current_version": self.current_version
            }
        
        firmware_info = update_info.get("firmware_info", {})
        latest_version = update_info.get("latest_version")
        download_url = firmware_info.get("download_url")
        
        print(f"\n✓ Tìm thấy firmware mới!")
        print(f"  Version: {latest_version}")
        print(f"  Release: {update_info.get('release_name')}")
        print(f"  File: {firmware_info.get('name')}")
        print(f"  Size: {firmware_info.get('size'):,} bytes")
        
        # Tải firmware
        file_path = self.download_firmware(
            download_url,
            firmware_info.get("name"),
            progress_callback
        )
        
        if not file_path:
            return {
                "success": False,
                "message": "Lỗi khi tải firmware"
            }
        
        # Cài đặt
        if install_callback:
            print("\nĐang cài đặt firmware...")
            try:
                install_callback(file_path)
                print(f"✓ Cài đặt thành công! Phiên bản mới: {latest_version}")
                self.current_version = latest_version
                return {
                    "success": True,
                    "message": "Cập nhật firmware thành công",
                    "new_version": latest_version,
                    "file_path": str(file_path)
                }
            except Exception as e:
                print(f"✗ Lỗi khi cài đặt: {e}")
                return {
                    "success": False,
                    "message": f"Lỗi khi cài đặt: {str(e)}"
                }
        else:
            print(f"\n✓ Firmware đã sẵn sàng tại: {file_path}")
            return {
                "success": True,
                "message": "Firmware đã tải về",
                "new_version": latest_version,
                "file_path": str(file_path),
                "needs_manual_install": True
            }


# Ví dụ sử dụng
if __name__ == "__main__":
    # Khởi tạo client
    # Thay đổi repo của bạn
    client = GitHubOTAClient(
        repo="username/repo-name",  # ← Thay đổi repo của bạn
        token=None  # Cần token nếu là private repo
    )
    
    client.set_current_version("1.0.0")
    
    def progress_callback(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            print(f"\rTiến trình: {percent:.1f}% ({downloaded}/{total} bytes)", end="")
    
    def install_firmware(file_path):
        print(f"\nCài đặt firmware từ {file_path}...")
        # Logic cài đặt của bạn
    
    result = client.update_firmware(
        install_callback=install_firmware,
        progress_callback=progress_callback
    )
    
    print(f"\nKết quả: {result}")

