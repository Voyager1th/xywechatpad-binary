import platform
import shutil
from pathlib import Path

def copy_binary(target_dir: Path) -> Path:
    """
    将当前平台的二进制文件复制到指定目录
    :param target_dir: 必须存在的目标目录
    :return: 复制后的完整文件路径
    :raises FileNotFoundError: 当目标目录不存在时
    :raises OSError: 平台不受支持时
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 平台到二进制路径的映射
    BIN_MAP = {
        "linux": {
            "x86_64": "binaries/linux_x64/XYWechatPad",
            "amd64": "binaries/linux_x64/XYWechatPad",
            "aarch64": "binaries/linux_aarch64/XYWechatPad"
        },
        "darwin": {  # macOS
            "x86_64": "binaries/macos_x64/XYWechatPad",
            "arm64": "binaries/macos_arm64/XYWechatPad"
        },
        "windows": {
            "x86_64": "binaries/win_x64/XYWechatPad.exe",
            "amd64": "binaries/win_x64/XYWechatPad.exe"
        }
    }

    # 验证平台支持
    if system not in BIN_MAP or machine not in BIN_MAP[system]:
        raise OSError(f"Unsupported platform: {system}-{machine}")

    # 获取源文件路径
    src_path = Path(__file__).parent / BIN_MAP[system][machine]
    if not src_path.exists():
        raise FileNotFoundError(f"Binary not found: {src_path}")

    # 验证目标目录
    if not target_dir.is_dir():
        raise FileNotFoundError(f"Target directory does not exist: {target_dir}")

    # 构建目标路径
    dest_path = target_dir / src_path.name

    # 如果目标文件已存在且内容相同，直接返回
    if dest_path.exists():
        # 验证文件内容是否一致
        if dest_path.stat().st_size == src_path.stat().st_size:
            return dest_path
            
        # 文件存在但大小不同则删除旧文件
        dest_path.unlink()

    # 执行复制
    shutil.copy2(src_path, dest_path)
    
    # 设置可执行权限（非Windows）
    if system != "windows":
        dest_path.chmod(0o755)

    return dest_path
