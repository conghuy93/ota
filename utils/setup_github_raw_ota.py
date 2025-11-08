"""
Script setup GitHub Raw OTA repo
Tạo cấu trúc ban đầu cho repo OTA
"""
import os
import json
from pathlib import Path

def setup_repo_structure(repo_path: str = "."):
    """
    Tạo cấu trúc thư mục cho GitHub Raw OTA
    """
    repo_path = Path(repo_path)
    
    # Tạo thư mục
    ota_dir = repo_path / "ota" / "firmware"
    ota_dir.mkdir(parents=True, exist_ok=True)
    
    # Tạo version.json
    version_file = repo_path / "ota" / "version.json"
    if not version_file.exists():
        with open(version_file, 'w') as f:
            json.dump({"version": 1}, f, indent=2)
        print(f"✓ Created: {version_file}")
    else:
        print(f"  Exists: {version_file}")
    
    # Tạo README.md
    readme_file = repo_path / "ota" / "README.md"
    if not readme_file.exists():
        readme_content = """# OTA Firmware Repository

Repository này chứa firmware cho OTA updates.

## Cấu trúc

```
ota/
├── firmware/
│   └── firmware.bin    # File firmware ESP32
├── version.json        # Version hiện tại
└── README.md          # File này
```

## Cách sử dụng

1. Build firmware từ Arduino IDE
2. Export compiled binary → `firmware.bin`
3. Upload `firmware.bin` vào `firmware/`
4. Tăng version trong `version.json`
5. Commit & Push
6. ESP32 sẽ tự động cập nhật

## Links RAW

- Version: `https://raw.githubusercontent.com/USERNAME/REPO/main/ota/version.json`
- Firmware: `https://raw.githubusercontent.com/USERNAME/REPO/main/ota/firmware/firmware.bin`

Thay `USERNAME` và `REPO` bằng thông tin repo của bạn.
"""
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✓ Created: {readme_file}")
    else:
        print(f"  Exists: {readme_file}")
    
    # Tạo .gitkeep trong firmware/
    gitkeep = ota_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        print(f"✓ Created: {gitkeep}")
    
    print(f"\n✅ Cấu trúc repo đã được tạo!")
    print(f"\n📁 Cấu trúc:")
    print(f"  {repo_path}/")
    print(f"  ├── ota/")
    print(f"  │   ├── firmware/")
    print(f"  │   │   └── .gitkeep")
    print(f"  │   ├── version.json")
    print(f"  │   └── README.md")
    print(f"\n📝 Bước tiếp theo:")
    print(f"  1. Build firmware ESP32 → Export binary")
    print(f"  2. Copy file .bin vào ota/firmware/firmware.bin")
    print(f"  3. git add ota/")
    print(f"  4. git commit -m 'Initial OTA setup'")
    print(f"  5. git push")

if __name__ == "__main__":
    import sys
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    setup_repo_structure(repo_path)

