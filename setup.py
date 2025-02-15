import sys
import platform
import os
from setuptools import setup, find_packages

# 从环境变量获取当前构建平台
target_platform = os.environ.get('TARGET_PLATFORM', '').lower()

# 平台到二进制路径的映射
PLATFORM_BINARIES = {
    'linux_x86_64': ['binaries/linux_x64/XYWechatPad'],
    'linux_aarch64': ['binaries/linux_aarch64/XYWechatPad'],
    'macos_x86_64': ['binaries/macos_x64/XYWechatPad'],
    'macos_arm64': ['binaries/macos_arm64/XYWechatPad'],
    'win_amd64': ['binaries/win_x64/XYWechatPad.exe']
}

# 版本检查
if sys.version_info < (3, 11):
    raise RuntimeError("Requires Python 3.11 or higher")

setup(
    name="xywechatpad-binary",
    version="1.0.0",
    author="HenryXiaoYang",
    author_email="henryyang666@hotmail.com",
    description="XYBotV2 Binary Distribution",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HenryXiaoYang/xywechatpad-binary",
    packages=find_packages(),
    package_data={
        "xywechatpad_binary": PLATFORM_BINARIES.get(target_platform, [])
    },
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