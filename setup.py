import sys
import platform
from setuptools import setup, find_packages

# 平台检测
system = platform.system().lower()
machine = platform.machine().lower()

# 确定当前平台的二进制路径
BINARY_PATH = ""
if system == "linux":
    if machine in ["x86_64", "amd64"]:
        BINARY_PATH = "binaries/linux_x64/XYBotWechatPad"
    elif machine == "aarch64":
        BINARY_PATH = "binaries/linux_aarch64/XYBotWechatPad"
elif system == "darwin":  # macOS
    if machine == "arm64":
        BINARY_PATH = "binaries/macos_arm64/XYBotWechatPad"
    elif machine == "x86_64":
        BINARY_PATH = "binaries/macos_x64/XYBotWechatPad"
elif system == "windows":
    BINARY_PATH = "binaries/win_x64/XYBotWechatPad.exe"

# 版本检查
if sys.version_info < (3, 11):
    raise RuntimeError("Requires Python 3.11 or higher")

setup(
    name="xywechatpad-binary",
    version="0.2",
    author="HenryXiaoYang",
    author_email="henryyang666@hotmail.com",
    description="XYBotV2 Binary Distribution",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HenryXiaoYang/xywechatpad-binary",
    packages=find_packages(),
    package_data={"xywechatpad_binary": [BINARY_PATH]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.11',
    platforms=[
        "Linux-x86_64",
        "Linux-aarch64",
        "macosx-x86_64",
        "macosx-arm64",
        "Windows-x86_64"
    ]
)