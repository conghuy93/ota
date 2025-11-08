"""
Script tự động: Build firmware → Upload GitHub → Flash ESP32
Workflow hoàn chỉnh từ code đến ESP32
"""
import subprocess
import sys
import argparse
import os
from pathlib import Path
try:
    from github_raw_upload import upload_firmware_and_version
except ImportError:
    print("Warning: github_raw_upload not found")
    def upload_firmware_and_version(*args, **kwargs):
        return False

def build_arduino_sketch(sketch_path: str, fqbn: str = "esp32:esp32:esp32s3"):
    """
    Build Arduino sketch sử dụng arduino-cli
    
    Args:
        sketch_path: Đường dẫn đến file .ino
        fqbn: Fully Qualified Board Name
    """
    sketch_path = Path(sketch_path)
    
    if not sketch_path.exists():
        print(f"❌ Sketch không tồn tại: {sketch_path}")
        return None
    
    print(f"🔨 Đang build sketch: {sketch_path}")
    print(f"   Board: {fqbn}")
    
    # Kiểm tra arduino-cli
    try:
        subprocess.run(["arduino-cli", "version"], 
                      capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ arduino-cli không tìm thấy!")
        print("\nCài đặt arduino-cli:")
        print("  https://arduino.github.io/arduino-cli/")
        return None
    
    # Build
    cmd = [
        "arduino-cli",
        "compile",
        "--fqbn", fqbn,
        str(sketch_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build thành công!")
            
            # Tìm file .bin
            build_dir = sketch_path.parent / "build" / fqbn.replace(":", ".")
            bin_files = list(build_dir.rglob("*.bin"))
            
            if bin_files:
                firmware_bin = bin_files[0]
                print(f"📦 Firmware: {firmware_bin}")
                return firmware_bin
            else:
                # Thử tìm trong sketch directory
                bin_files = list(sketch_path.parent.rglob("*.bin"))
                if bin_files:
                    firmware_bin = bin_files[0]
                    print(f"📦 Firmware: {firmware_bin}")
                    return firmware_bin
                else:
                    print("⚠️  Không tìm thấy file .bin")
                    return None
        else:
            print("❌ Build thất bại!")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"❌ Lỗi khi build: {e}")
        return None

def flash_esp32(port: str, firmware_path: Path):
    """Flash firmware vào ESP32"""
    from flash_esp32 import flash_firmware
    
    print(f"\n📤 Đang flash vào {port}...")
    return flash_firmware(port, str(firmware_path))

def main():
    parser = argparse.ArgumentParser(
        description='Auto: Build → Upload GitHub → Flash ESP32'
    )
    parser.add_argument('sketch', help='Đường dẫn đến file .ino')
    parser.add_argument('-r', '--repo',
                       help='GitHub repo (ví dụ: username/ota)')
    parser.add_argument('-t', '--token',
                       default=os.getenv('GITHUB_TOKEN'),
                       help='GitHub token')
    parser.add_argument('-p', '--port', default='COM31',
                       help='Serial port (default: COM31)')
    parser.add_argument('--fqbn', default='esp32:esp32:esp32s3',
                       help='Board FQBN (default: esp32:esp32:esp32s3)')
    parser.add_argument('--no-upload', action='store_true',
                       help='Không upload lên GitHub')
    parser.add_argument('--no-flash', action='store_true',
                       help='Không flash vào ESP32')
    parser.add_argument('--version', type=int,
                       help='Version cụ thể (tự động tăng nếu không chỉ định)')
    
    args = parser.parse_args()
    
    # 1. Build
    firmware_bin = build_arduino_sketch(args.sketch, args.fqbn)
    if not firmware_bin:
        sys.exit(1)
    
    # 2. Upload GitHub (nếu có)
    if not args.no_upload and args.repo:
        if not args.token:
            print("⚠️  Không có GitHub token, bỏ qua upload")
        else:
            print(f"\n📤 Đang upload lên GitHub...")
            success = upload_firmware_and_version(
                repo=args.repo,
                token=args.token,
                firmware_path=str(firmware_bin),
                new_version=args.version
            )
            if not success:
                print("⚠️  Upload thất bại, tiếp tục flash...")
    
    # 3. Flash ESP32 (nếu có)
    if not args.no_flash:
        success = flash_esp32(args.port, firmware_bin)
        if not success:
            sys.exit(1)
    
    print("\n✅ Hoàn thành!")

if __name__ == "__main__":
    main()

