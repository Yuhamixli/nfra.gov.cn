# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(os.getcwd())

# 收集数据文件
def collect_data_files():
    """收集需要包含在exe中的数据文件"""
    datas = []
    
    # 添加README文件
    readme_files = [
        'README.md',
        'WEB界面使用说明.md',
        'drivers/README.md',
    ]
    
    for readme in readme_files:
        if (project_root / readme).exists():
            datas.append((str(project_root / readme), str(Path(readme).parent) if Path(readme).parent != Path('.') else '.'))
    
    # 添加配置文件
    config_files = [
        'config.py',
        'config_exe.py',
    ]
    
    for config in config_files:
        if (project_root / config).exists():
            datas.append((str(project_root / config), '.'))
    
    return datas

# 收集隐藏导入
hiddenimports = [
    'selenium',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'selenium.common.exceptions',
    'webdriver_manager.chrome',
    'bs4',
    'pandas',
    'numpy',
    'openpyxl',
    'xlsxwriter',
    'urllib.parse',
    'configparser',
    'json',
    'csv',
    'lxml',
    'html.parser',
    'config_exe',
]

# 主程序分析
a = Analysis(
    ['nfra_crawler_exe.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=collect_data_files(),
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'tkinter',
        'PIL',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 收集Python文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 生成exe文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NFRA金融监管爬虫',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径
    version_file=None,  # 可以添加版本信息文件
)

# 收集目录（如果需要生成目录而不是单文件exe）
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='NFRA金融监管爬虫'
# )
