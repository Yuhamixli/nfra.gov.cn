#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver设置脚本
用于下载和设置本地ChromeDriver，避免每次启动时重新下载
"""

import os
import sys
import shutil
import platform
from pathlib import Path

# 添加项目路径以便导入配置
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 检测exe模式并导入相应配置
if os.environ.get('NFRA_EXE_MODE') == '1':
    from config_exe import WEBDRIVER_CONFIG
else:
    from config import WEBDRIVER_CONFIG

from utils import setup_logging

def check_chrome_version():
    """检查Chrome浏览器版本"""
    try:
        if platform.system() == "Windows":
            import winreg
            try:
                # 尝试从注册表获取Chrome版本
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                return version
            except:
                # 尝试从程序文件获取
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                if os.path.exists(chrome_path):
                    return "已安装（版本获取失败）"
        else:
            # Linux/Mac
            import subprocess
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
    except Exception as e:
        print(f"检查Chrome版本失败: {e}")
    
    return None

def download_chromedriver():
    """下载ChromeDriver"""
    print("[检查] 正在检查Chrome浏览器...")
    chrome_version = check_chrome_version()
    
    if not chrome_version:
        print("❌ 未检测到Chrome浏览器，请先安装Chrome")
        print("   下载地址: https://www.google.com/chrome/")
        return False
    
    print(f"✅ 检测到Chrome: {chrome_version}")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("⏬ 正在下载匹配的ChromeDriver...")
        manager = ChromeDriverManager()
        downloaded_path = manager.install()
        
        print(f"✅ ChromeDriver下载完成: {downloaded_path}")
        
        # 复制到本地drivers目录
        local_dir = Path(WEBDRIVER_CONFIG['local_driver_dir'])
        local_dir.mkdir(exist_ok=True)
        
        driver_file = WEBDRIVER_CONFIG['driver_filename']
        local_path = local_dir / driver_file
        
        shutil.copy2(downloaded_path, local_path)
        print(f"📥 已复制到本地目录: {local_path}")
        
        # 在非Windows系统上设置执行权限
        if os.name != 'nt':
            os.chmod(local_path, 0o755)
            print("✅ 已设置执行权限")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载ChromeDriver失败: {e}")
        return False

def check_local_driver():
    """检查本地ChromeDriver"""
    local_dir = Path(WEBDRIVER_CONFIG['local_driver_dir'])
    driver_file = WEBDRIVER_CONFIG['driver_filename']
    local_path = local_dir / driver_file
    
    if local_path.exists():
        print(f"✅ 发现本地ChromeDriver: {local_path}")
        
        # 检查执行权限
        if os.access(local_path, os.X_OK) or os.name == 'nt':
            print("✅ 具有执行权限")
            return True
        else:
            print("⚠️  缺少执行权限，正在修复...")
            try:
                os.chmod(local_path, 0o755)
                print("✅ 执行权限已修复")
                return True
            except Exception as e:
                print(f"❌ 修复执行权限失败: {e}")
                return False
    else:
        print(f"❌ 本地ChromeDriver不存在: {local_path}")
        return False

def test_driver():
    """测试ChromeDriver是否工作正常"""
    print("\n🧪 测试ChromeDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # 使用本地driver
        local_dir = Path(WEBDRIVER_CONFIG['local_driver_dir'])
        driver_file = WEBDRIVER_CONFIG['driver_filename'] 
        local_path = local_dir / driver_file
        
        if not local_path.exists():
            print("❌ 本地ChromeDriver不存在，无法测试")
            return False
        
        # 配置Chrome选项
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 创建Service
        service = Service(str(local_path))
        
        # 创建WebDriver
        driver = webdriver.Chrome(service=service, options=options)
        
        # 简单测试
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ ChromeDriver测试成功！访问页面标题: {title}")
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver测试失败: {e}")
        return False

def show_status():
    """显示当前状态"""
    print("=" * 60)
    print("🚗 ChromeDriver 状态检查")
    print("=" * 60)
    
    # 检查配置
    print(f"📁 本地目录: {WEBDRIVER_CONFIG['local_driver_dir']}")
    print(f"📄 Driver文件: {WEBDRIVER_CONFIG['driver_filename']}")
    print(f"⚙️  使用本地Driver: {WEBDRIVER_CONFIG['use_local_driver']}")
    print(f"📥 自动下载: {WEBDRIVER_CONFIG['auto_download']}")
    
    print("\n🔍 检查状态:")
    
    # 检查Chrome
    chrome_version = check_chrome_version()
    if chrome_version:
        print(f"✅ Chrome浏览器: {chrome_version}")
    else:
        print("❌ Chrome浏览器: 未安装")
    
    # 检查本地driver
    has_local = check_local_driver()
    
    # 检查webdriver_manager缓存
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        manager = ChromeDriverManager()
        # 检查是否有缓存
        print("✅ webdriver_manager: 可用")
    except Exception as e:
        print(f"❌ webdriver_manager: {e}")

def main():
    """主函数"""
    print("[工具] ChromeDriver 设置工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status':
            show_status()
        elif command == 'download':
            success = download_chromedriver()
            if success:
                print("\n🎉 ChromeDriver设置完成！")
                print("💡 现在程序启动时将直接使用本地driver，无需重新下载")
            else:
                print("\n❌ ChromeDriver设置失败")
        elif command == 'test':
            test_driver()
        elif command == 'clean':
            # 清理本地driver
            local_dir = Path(WEBDRIVER_CONFIG['local_driver_dir'])
            if local_dir.exists():
                shutil.rmtree(local_dir)
                print(f"✅ 已清理本地driver目录: {local_dir}")
            else:
                print("📁 本地driver目录不存在")
        else:
            print(f"❌ 未知命令: {command}")
            print_help()
    else:
        print_help()

def print_help():
    """打印帮助信息"""
    print("""
使用方法:
    python setup_driver.py <command>

命令:
    status      显示当前ChromeDriver状态
    download    下载并设置ChromeDriver到本地
    test        测试本地ChromeDriver是否正常工作
    clean       清理本地ChromeDriver文件

示例:
    python setup_driver.py status     # 检查状态
    python setup_driver.py download   # 下载设置
    python setup_driver.py test       # 测试功能

说明:
    设置完成后，程序启动时将优先使用本地driver，
    避免每次都通过webdriver_manager重新下载，大幅提升启动速度。
    """)

if __name__ == "__main__":
    main() 