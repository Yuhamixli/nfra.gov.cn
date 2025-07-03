#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXE构建脚本
自动化构建NFRA金融监管爬虫的exe应用程序
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

def print_step(step_name, description):
    """打印构建步骤"""
    print("=" * 60)
    print(f"🔧 {step_name}: {description}")
    print("=" * 60)

def check_requirements():
    """检查构建环境"""
    print_step("环境检查", "检查构建所需的依赖")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 未安装PyInstaller，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✅ PyInstaller安装完成")
    
    # 检查关键依赖
    required_packages = [
        ('selenium', 'selenium'),
        ('webdriver_manager', 'webdriver_manager'),
        ('beautifulsoup4', 'bs4'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('lxml', 'lxml')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}")
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def clean_build_dirs():
    """清理构建目录"""
    print_step("清理构建", "清理之前的构建文件")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🗑️ 删除目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理Python缓存文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                print(f"🗑️ 删除文件: {file_path}")
                os.remove(file_path)
        
        # 删除__pycache__目录
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            print(f"🗑️ 删除缓存: {cache_path}")
            shutil.rmtree(cache_path)
            dirs.remove('__pycache__')

def setup_chromedriver():
    """设置ChromeDriver"""
    print_step("ChromeDriver设置", "确保ChromeDriver可用")
    
    try:
        # 运行setup_driver.py来设置ChromeDriver
        result = subprocess.run([sys.executable, 'setup_driver.py', 'download'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ChromeDriver设置成功")
            return True
        else:
            print(f"⚠️ ChromeDriver设置可能有问题: {result.stderr}")
            return True  # 继续构建，因为exe可以在运行时下载
            
    except Exception as e:
        print(f"⚠️ ChromeDriver设置失败: {e}")
        return True  # 继续构建

def build_exe():
    """构建exe文件"""
    print_step("构建EXE", "使用PyInstaller构建可执行文件")
    
    # 构建命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',  # 清理缓存
        '--noconfirm',  # 不询问覆盖
        'nfra_crawler.spec'
    ]
    
    print(f"🔧 构建命令: {' '.join(cmd)}")
    print("⏳ 开始构建，这可能需要几分钟...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        build_time = time.time() - start_time
        print(f"✅ 构建成功！耗时: {build_time:.1f}秒")
        print("📁 输出文件位置: dist/NFRA金融监管爬虫.exe")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败:")
        print(f"返回码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        return False

def create_release_package():
    """创建发布包"""
    print_step("创建发布包", "准备最终的发布文件")
    
    release_dir = Path('release')
    
    # 清理并创建发布目录
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    
    # 复制exe文件
    exe_file = Path('dist/NFRA金融监管爬虫.exe')
    if exe_file.exists():
        shutil.copy2(exe_file, release_dir / 'NFRA金融监管爬虫.exe')
        print(f"✅ 复制exe文件: {exe_file}")
    else:
        print(f"❌ 找不到exe文件: {exe_file}")
        return False
    
    # 创建必要的目录结构
    dirs_to_create = ['excel_output', 'text_output', 'logs', 'drivers']
    for dir_name in dirs_to_create:
        (release_dir / dir_name).mkdir()
        print(f"📁 创建目录: {dir_name}")
    
    # 复制说明文件
    docs_to_copy = [
        ('README.md', '使用说明.md'),
        ('WEB界面使用说明.md', 'WEB界面使用说明.md'),
        ('drivers/README.md', 'drivers/README.md'),
    ]
    
    for src, dst in docs_to_copy:
        src_path = Path(src)
        if src_path.exists():
            dst_path = release_dir / dst
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            print(f"📄 复制文档: {src} -> {dst}")
    
    # 创建快速启动说明
    quick_start = release_dir / '快速开始.txt'
    with open(quick_start, 'w', encoding='utf-8') as f:
        f.write("""🚀 NFRA金融监管爬虫 - 快速开始

1. 双击运行 "NFRA金融监管爬虫.exe"

2. 首次使用建议：
   - 选择 "7. WebDriver设置" -> "2. 下载设置" 来配置ChromeDriver
   - 选择 "4. 测试模式" 验证程序功能

3. 正常使用：
   - 选择 "1. 初始化模式" 下载全部数据（首次使用）
   - 选择 "2. 月度更新模式" 获取最新数据（日常使用）
   - 选择 "5. 自定义爬取" 进行灵活配置

4. 输出文件：
   - Excel文件: excel_output/ 目录
   - 文本文件: text_output/ 目录

5. 注意事项：
   - 请确保网络连接正常
   - 程序运行时会显示浏览器窗口，属正常现象
   - 如遇问题请查看 "使用说明.md"

版本: v2.3.1 EXE版
更新时间: 2025-01-03
""")
    print("📄 创建快速启动说明")
    
    print(f"✅ 发布包创建完成: {release_dir}")
    
    # 显示文件大小
    exe_size = exe_file.stat().st_size / 1024 / 1024
    print(f"📊 exe文件大小: {exe_size:.1f} MB")
    
    return True

def test_exe():
    """测试exe文件"""
    print_step("测试EXE", "验证exe文件是否正常工作")
    
    exe_file = Path('release/NFRA金融监管爬虫.exe')
    
    if not exe_file.exists():
        print(f"❌ 找不到exe文件: {exe_file}")
        return False
    
    print("⚠️ 手动测试提示:")
    print("1. 进入release目录")
    print("2. 双击运行 'NFRA金融监管爬虫.exe'")
    print("3. 验证程序能否正常启动并显示菜单")
    print("4. 建议测试WebDriver设置和测试模式功能")
    
    return True

def main():
    """主构建流程"""
    print("🚀 NFRA金融监管爬虫 - EXE构建工具")
    print("=" * 60)
    
    try:
        # 1. 环境检查
        if not check_requirements():
            print("❌ 环境检查失败，请解决依赖问题后重试")
            return False
        
        # 2. 清理构建目录
        clean_build_dirs()
        
        # 3. 设置ChromeDriver
        setup_chromedriver()
        
        # 4. 构建exe
        if not build_exe():
            print("❌ 构建失败")
            return False
        
        # 5. 创建发布包
        if not create_release_package():
            print("❌ 创建发布包失败")
            return False
        
        # 6. 测试提示
        test_exe()
        
        print("\n" + "=" * 60)
        print("🎉 构建完成！")
        print("📁 发布文件位置: release/")
        print("📄 快速启动: release/NFRA金融监管爬虫.exe")
        print("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断构建")
        return False
    except Exception as e:
        print(f"\n❌ 构建过程出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 