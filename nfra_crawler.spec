# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('config.py', '.'),
        ('crawler.py', '.'),
        ('data_processor.py', '.'),
        ('main.py', '.'),
        ('utils.py', '.'),
        ('运行脚本.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'selenium',
        'bs4',
        'pandas',
        'openpyxl',
        'lxml',
        'webdriver_manager',
        'schedule',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='金融监管总局行政处罚信息爬虫',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
