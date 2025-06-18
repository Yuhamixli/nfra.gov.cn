#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller打包脚本
将金融监管总局爬虫打包成可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """清理之前的构建文件"""
    print("🧹 清理构建目录...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   已删除: {dir_name}")

def create_spec_file():
    """创建PyInstaller规格文件"""
    print("📝 创建打包配置...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''
    
    with open('nfra_crawler.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("   已创建: nfra_crawler.spec")

def build_exe():
    """执行打包"""
    print("🔨 开始打包exe...")
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm', 
        'nfra_crawler.spec'
    ]
    
    print(f"   执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ 打包成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        return False

def copy_additional_files():
    """复制额外需要的文件"""
    print("📋 复制附加文件...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ dist目录不存在")
        return False
    
    # 创建输出目录
    output_dirs = ['excel_output', 'text_output']
    for dir_name in output_dirs:
        output_dir = dist_dir / dir_name
        output_dir.mkdir(exist_ok=True)
        print(f"   已创建: {dir_name}")
    
    # 复制运行脚本
    scripts = ['run_daily.bat']
    for script in scripts:
        if os.path.exists(script):
            shutil.copy2(script, dist_dir)
            print(f"   已复制: {script}")
    
    return True

def create_usage_guide():
    """创建使用说明"""
    print("📖 创建使用说明...")
    
    guide_content = """# 金融监管总局行政处罚信息爬虫 - 使用说明

## 快速开始

### 方法一：双击运行exe文件
1. 双击 `金融监管总局行政处罚信息爬虫.exe`
2. 根据菜单选择运行模式
3. 等待程序完成

### 方法二：命令行运行  
```cmd
金融监管总局行政处罚信息爬虫.exe
```

## 运行模式说明

- **初始化模式**：首次使用，下载2025年全部数据（2-4小时）
- **月度更新**：定期获取最近45天新数据（20-40分钟）
- **每日更新**：获取昨天发布的新数据（2-5分钟）
- **测试模式**：快速测试程序功能（5-10分钟）

## 输出文件

程序运行后会在以下目录生成Excel文件：
- `excel_output/` - Excel数据文件
- `text_output/` - 文本数据文件（测试模式）

## 注意事项

1. **首次运行**：选择初始化模式建立数据库
2. **网络要求**：需要稳定的网络连接
3. **浏览器**：需要安装Chrome浏览器
4. **运行时间**：初始化模式需要较长时间，请耐心等待
5. **防火墙**：程序需要访问网络，请允许防火墙通过

## 故障排除

- **WebDriver错误**：确保Chrome浏览器已安装
- **网络超时**：检查网络连接，重新运行即可
- **文件无法保存**：检查磁盘空间，关闭已打开的Excel文件

## 技术支持

如遇问题请查看完整文档 `README.md` 或联系开发者。
"""
    
    with open('dist/使用说明.txt', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print("   已创建: 使用说明.txt")

def main():
    """主函数"""
    print("🚀 开始构建可执行文件...")
    print()
    
    try:
        # 1. 清理构建文件
        clean_build()
        print()
        
        # 2. 创建规格文件
        create_spec_file()
        print()
        
        # 3. 执行打包
        if not build_exe():
            return False
        print()
        
        # 4. 复制附加文件
        if not copy_additional_files():
            return False
        print()
        
        # 5. 创建使用说明
        create_usage_guide()
        print()
        
        print("🎉 构建完成！")
        print(f"📁 可执行文件位于: dist/金融监管总局行政处罚信息爬虫.exe")
        print(f"📋 使用说明位于: dist/使用说明.txt")
        print()
        print("💡 提示：首次运行请选择初始化模式")
        
        return True
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        input("按 Enter 键退出...")
        sys.exit(1) 