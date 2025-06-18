import os
from bs4 import BeautifulSoup
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def get_valid_input(prompt, validator=int):
    """获取有效的输入，根据传入的验证器类型（默认为整数）"""
    while True:
        try:
            return validator(input(prompt))
        except ValueError:
            print(f"请输入一个有效的{validator.__name__}！")

def get_valid_path(prompt):
    """获取有效的文件路径输入"""
    while True:
        path = input(prompt).strip()
        if os.path.exists(path):
            return path
        print("请输入一个有效的文件路径！")

def setup_chrome_driver(chromedriver_path, headless=True):
    """设置ChromeDriver选项并返回WebDriver实例"""
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--allow-running-insecure-content')
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def process_link(driver, href, title, output_dir):
    """处理给定链接并保存符合条件的内容"""
    print(f"👉正在处理标题: {title}")
    time.sleep(random.uniform(1, 3))

    driver.execute_script("window.open(arguments[0], '_blank');", href)
    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tables = soup.find_all('table')
    
    found_table = False  # 标志是否有符合条件的表格
    for table in tables:
        row_contents = [row.get_text(separator='\t', strip=True) for row in table.find_all('tr')]
        if any("人寿" in row_content for row_content in row_contents):
            safe_title = title.replace('/', '_').replace(':', '_')
            file_name = f"{output_dir}/{safe_title}.txt"
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write('\n'.join(row_contents))
            print(f"————保存了符合要求的内容到文件: {file_name}")
            found_table = True
            break  # 只保存第一个符合条件的表格
    
    if not found_table:
        print(f"——页面 {href} 中没有找到包含'人寿'关键字的表格")
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def main():
    base_url = input("请输入目标网址-以http或https开头：")
    total_pages = get_valid_input("请输入要翻页的总页数: ")
    chromedriver_path = get_valid_path("请输入chromedriver的完整路径(无需包含chromedriver.exe)：") + "\\chromedriver.exe"
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    driver = setup_chrome_driver(chromedriver_path)
    try:
        for page in range(1, total_pages + 1):
            print(f"正在处理第 {page} 页...")
            driver.get(base_url)
            elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[contains(text(), "行政处罚信息公开表")]'))
            )
            
            for element in elements:
                href = element.get_attribute('href')
                title = element.text.strip()
                if title:  # 只处理非空标题
                    process_link(driver, href, title, output_dir)
            
            if page < total_pages:
                next_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="下一页"]'))
                )
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)  # 等待页面加载
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        driver.quit()

    print("----------------------------------------------")
    print("全部页面检索完毕\n请打开本程序同级目录下的output文件夹查看")


if __name__ == "__main__":
    main()