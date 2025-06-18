#!/usr/bin/env python3
"""
调试测试脚本 - 专门解决网络连接问题
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def setup_robust_chrome():
    """设置最强健的Chrome配置"""
    options = Options()
    
    # 基础配置
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage') 
    options.add_argument('--disable-gpu')
    
    # SSL 和证书问题解决
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    
    # 网络优化
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows') 
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    
    # 用户代理和反检测
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 窗口大小
    options.add_argument('--window-size=1920,1080')
    
    return options

def test_network_connection():
    """测试网络连接和页面加载"""
    print("🌐 开始网络连接测试...")
    
    driver = None
    try:
        # 设置Chrome
        options = setup_robust_chrome()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 超时设置
        driver.set_page_load_timeout(90)
        driver.implicitly_wait(20)
        driver.set_script_timeout(90)
        
        # 隐藏webdriver特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome WebDriver 初始化成功")
        
        # 测试基础网络连接
        test_urls = [
            "https://www.baidu.com",
            "https://www.nfra.gov.cn",
            "https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4114&itemUrl=ItemListRightList.html&itemName=%E7%9B%91%E7%AE%A1%E5%B1%80%E6%9C%AC%E7%BA%A7&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A"
        ]
        
        for i, url in enumerate(test_urls):
            print(f"\n🔍 测试 URL {i+1}: {url[:50]}...")
            
            try:
                start_time = time.time()
                driver.get(url)
                
                # 等待页面加载
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                load_time = time.time() - start_time
                title = driver.title[:30]
                
                print(f"✅ 加载成功 - 用时: {load_time:.2f}s, 标题: {title}")
                
                # 如果是NFRA网站，尝试查找关键元素
                if "nfra.gov.cn" in url:
                    try:
                        # 查找链接元素
                        links = driver.find_elements(By.TAG_NAME, "a")
                        print(f"   找到 {len(links)} 个链接")
                        
                        # 查找包含"行政处罚"的链接
                        penalty_links = [link for link in links if "行政处罚" in link.text]
                        print(f"   找到 {len(penalty_links)} 个处罚相关链接")
                        
                    except Exception as e:
                        print(f"   ⚠️ 元素查找失败: {e}")
                
                # 随机等待
                time.sleep(random.uniform(2, 4))
                
            except TimeoutException:
                print(f"❌ 超时失败 - URL: {url}")
            except Exception as e:
                print(f"❌ 加载失败 - 错误: {e}")
        
        print("\n🎯 网络测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_network_connection() 