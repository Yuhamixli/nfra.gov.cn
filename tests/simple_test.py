#!/usr/bin/env python3
"""
简化测试脚本 - 诊断基础问题
"""

print("🔍 开始基础诊断...")

try:
    print("1. 测试基础Python功能...")
    import sys
    import os
    print(f"   Python版本: {sys.version}")
    print(f"   当前目录: {os.getcwd()}")
    print("   ✅ 基础Python功能正常")
except Exception as e:
    print(f"   ❌ 基础Python功能失败: {e}")
    exit(1)

try:
    print("2. 测试依赖库导入...")
    import selenium
    print(f"   Selenium版本: {selenium.__version__}")
    
    import bs4
    print(f"   BeautifulSoup版本: {bs4.__version__}")
    
    import pandas as pd
    print(f"   Pandas版本: {pd.__version__}")
    
    print("   ✅ 所有依赖库导入成功")
except Exception as e:
    print(f"   ❌ 依赖库导入失败: {e}")
    print("   💡 请运行: pip install -r requirements.txt")
    exit(1)

try:
    print("3. 测试项目模块...")
    # 添加当前目录到路径
    sys.path.insert(0, os.getcwd())
    
    import config
    print("   ✅ config.py 导入成功")
    
    import utils
    print("   ✅ utils.py 导入成功")
    
    from utils import setup_logging
    logger = setup_logging()
    print("   ✅ 日志系统初始化成功")
    
except Exception as e:
    print(f"   ❌ 项目模块导入失败: {e}")
    print(f"   错误详情: {type(e).__name__}: {str(e)}")
    exit(1)

try:
    print("4. 测试WebDriver...")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get("https://www.baidu.com")
    print(f"   页面标题: {driver.title[:20]}...")
    driver.quit()
    
    print("   ✅ WebDriver测试成功")
    
except Exception as e:
    print(f"   ❌ WebDriver测试失败: {e}")
    print("   💡 请确保Chrome浏览器已安装")

try:
    print("5. 测试爬虫模块...")
    import crawler
    print("   ✅ crawler.py 导入成功")
    
    import data_processor
    print("   ✅ data_processor.py 导入成功")
    
except Exception as e:
    print(f"   ❌ 爬虫模块导入失败: {e}")
    print(f"   错误详情: {type(e).__name__}: {str(e)}")

print("\n🎯 诊断完成！")
print("如果所有测试都通过，可以尝试运行: python main.py test")
print("如果有失败项目，请将错误信息反馈给开发者。") 