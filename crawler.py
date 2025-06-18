"""
金融监管总局行政处罚信息爬虫
"""

import time
import logging
import re
import os
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import urllib.parse
import random

from config import BASE_URLS, SELENIUM_CONFIG, CRAWL_CONFIG
from utils import setup_logging, clean_text, format_date, get_current_timestamp


class NFRACrawler:
    """金融监管总局行政处罚信息爬虫"""
    
    def __init__(self, headless: bool = True):
        self.logger = setup_logging()
        self.driver = None
        self.wait = None
        self.headless = headless  # 添加headless属性
        self.driver_path = None  # 缓存driver路径
        
    def _get_driver_path(self):
        """获取或缓存ChromeDriver路径"""
        if self.driver_path and os.path.exists(self.driver_path):
            self.logger.info(f"使用缓存的ChromeDriver: {self.driver_path}")
            return self.driver_path
        
        try:
            # 设置缓存目录
            cache_dir = os.path.join(os.getcwd(), 'webdriver_cache')
            os.makedirs(cache_dir, exist_ok=True)
            
            # 使用webdriver_manager下载并缓存driver - 修正参数
            self.logger.info("正在获取ChromeDriver...")
            # 使用默认配置，webdriver_manager会自动处理缓存
            manager = ChromeDriverManager()
            driver_path = manager.install()
            self.driver_path = driver_path
            self.logger.info(f"ChromeDriver已缓存至: {driver_path}")
            return driver_path
            
        except Exception as e:
            self.logger.error(f"获取ChromeDriver失败: {e}")
            # 尝试从环境变量或系统路径查找
            try:
                # 检查是否有系统安装的chromedriver
                import shutil
                system_driver = shutil.which('chromedriver')
                if system_driver:
                    self.logger.info(f"使用系统ChromeDriver: {system_driver}")
                    return system_driver
            except:
                pass
            
            self.logger.warning("无法获取ChromeDriver，将尝试使用默认配置")
            return None
        
    def _setup_chrome_options(self):
        """配置Chrome选项以绕过反爬虫检测"""
        options = Options()
        
        # 基础配置
        if self.headless:
            options.add_argument('--headless')
        
        # 增强反检测配置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        # 移除禁用图片和JavaScript的配置 - 这些会导致现代网站无法正常加载
        # options.add_argument('--disable-images')  # 禁用图片加载加速
        # options.add_argument('--disable-javascript')  # 暂时禁用JS
        
        # SSL 和网络配置
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # 用户代理配置
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 窗口大小
        options.add_argument('--window-size=1920,1080')
        
        # 实验性选项
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 禁用blink特性
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        return options
    
    def setup_driver(self) -> bool:
        """初始化Chrome WebDriver"""
        try:
            chrome_options = self._setup_chrome_options()
            
            # 获取ChromeDriver路径
            driver_path = self._get_driver_path()
            
            # 创建Service对象
            if driver_path:
                service = Service(driver_path)
            else:
                # 如果没有指定路径，让selenium自动查找
                service = Service()
            
            # 创建driver实例
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 配置页面加载和脚本超时
            self.driver.set_page_load_timeout(60)  # 增加到60秒
            self.driver.implicitly_wait(15)  # 增加到15秒
            self.driver.set_script_timeout(60)  # 脚本执行超时
            
            # 隐藏WebDriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 初始化WebDriverWait
            self.wait = WebDriverWait(self.driver, 45)  # 增加等待时间
            
            self.logger.info("Chrome WebDriver 初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"初始化WebDriver失败: {e}")
            return False
    
    def close_driver(self):
        """关闭WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver 已关闭")
            except Exception as e:
                self.logger.error(f"关闭WebDriver失败: {e}")
    
    def load_page_with_retry(self, url: str, max_retries: int = 3) -> bool:
        """带重试机制的页面加载"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"正在加载页面: {url} (尝试 {attempt + 1}/{max_retries})")
                
                self.driver.get(url)
                
                # 等待页面完全加载完成 - 和debug_test.py保持一致
                self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                
                # 额外等待时间让内容加载
                time.sleep(random.uniform(2, 4))
                
                self.logger.info("页面加载成功")
                return True
                
            except TimeoutException:
                self.logger.warning(f"页面加载超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    # 等待后重试
                    time.sleep(random.uniform(3, 6))
                    continue
            except Exception as e:
                self.logger.error(f"页面加载失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(3, 6))
                    continue
        
        self.logger.error(f"无法加载 {url} 页面")
        return False
    
    def get_page_publish_dates(self) -> List[str]:
        """获取当前页面所有记录的发布时间"""
        try:
            # 查找所有可能的时间格式
            time_elements = []
            
            # 方式1：查找常见的时间格式元素 
            time_patterns = [
                '//td[contains(text(), "2024") or contains(text(), "2025")]',
                '//span[contains(text(), "2024") or contains(text(), "2025")]',
                '//div[contains(text(), "2024") or contains(text(), "2025")]'
            ]
            
            for pattern in time_patterns:
                elements = self.driver.find_elements(By.XPATH, pattern)
                time_elements.extend(elements)
            
            # 提取和清理时间文本
            publish_dates = []
            for element in time_elements:
                text = clean_text(element.text)
                # 使用正则表达式匹配日期格式
                import re
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                if date_match:
                    publish_dates.append(date_match.group(1))
            
            # 去重并排序
            unique_dates = list(set(publish_dates))
            unique_dates.sort(reverse=True)  # 降序排列，最新的在前
            
            self.logger.debug(f"当前页面发现的发布时间: {unique_dates}")
            return unique_dates
            
        except Exception as e:
            self.logger.warning(f"获取页面发布时间失败: {e}")
            return []

    def get_punishment_list_smart(self, category: str, target_year: int = None, target_month: int = None, max_pages: int = 10) -> List[Dict]:
        """智能获取处罚信息列表 - 支持按月份过滤"""
        url = BASE_URLS.get(category)
        if not url:
            self.logger.error(f"未找到类别 '{category}' 对应的URL")
            return []
        
        if not self.load_page_with_retry(url):
            self.logger.error(f"无法加载 {category} 页面")
            return []
        
        all_punishment_list = []
        current_page = 1
        found_target_month = False
        previous_page_latest_date = None  # 记录前一页的最新日期
        
        # 如果指定了目标年月，使用智能检查
        use_smart_check = target_year is not None and target_month is not None
        if use_smart_check:
            self.logger.info(f"启用智能月份检查: {target_year}年{target_month}月")
            target_month_str = f"{target_year}-{target_month:02d}"
        
        try:
            while current_page <= max_pages:
                self.logger.info(f"正在解析 {category} 第 {current_page} 页")
                
                # 等待页面加载完成
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)  # 额外等待确保内容加载
                
                # 智能检查：如果指定了目标月份，先检查当前页面是否包含目标月份的数据
                if use_smart_check:
                    # 获取当前页面的发布时间
                    publish_dates = self.get_page_publish_dates()
                    current_page_latest_date = publish_dates[0] if publish_dates else None
                    
                    # 检查是否包含目标月份
                    page_has_target = any(date.startswith(target_month_str) for date in publish_dates)
                    
                    if page_has_target:
                        found_target_month = True
                        self.logger.info(f"第 {current_page} 页包含目标月份 {target_month_str} 数据，继续爬取")
                    else:
                        # 没有目标月份数据的处理逻辑
                        if found_target_month:
                            # 之前找到过目标月份，现在没有了，说明已经超过目标月份范围（降序排列）
                            self.logger.info(f"第 {current_page} 页不再包含目标月份数据，目标月份范围已结束，停止爬取")
                            break
                        elif current_page == 1:
                            # 第1页没有目标月份数据
                            if current_page_latest_date and current_page_latest_date > target_month_str:
                                self.logger.info(f"第1页最新数据({current_page_latest_date})比目标月份({target_month_str})新，该分类无目标月份数据")
                                break
                            else:
                                self.logger.info(f"第1页暂无目标月份数据，检查第2页确认")
                        elif current_page == 2:
                            # 第2页的安全检查
                            if (previous_page_latest_date and current_page_latest_date and 
                                current_page_latest_date < previous_page_latest_date):
                                self.logger.info(f"第2页数据({current_page_latest_date})比第1页({previous_page_latest_date})更老且无目标月份，停止翻页")
                                break
                            else:
                                self.logger.info(f"第2页暂无目标月份数据，继续查找")
                        else:
                            # 第3页及以后，如果还没找到目标月份就停止
                            self.logger.info(f"第{current_page}页仍无目标月份数据，停止查找")
                            break
                        
                        # 记录当前页最新日期，用于下一页比较
                        previous_page_latest_date = current_page_latest_date
                        
                        # 没有目标月份数据，翻到下一页继续检查
                        if current_page < max_pages:
                            try:
                                next_buttons = self.driver.find_elements(
                                    By.XPATH, 
                                    '//span[text()="下一页"] | //a[text()="下一页"] | //a[contains(text(), "下一页")]'
                                )
                                
                                if next_buttons:
                                    next_button = next_buttons[0]
                                    if next_button.is_enabled():
                                        self.driver.execute_script("arguments[0].click();", next_button)
                                        current_page += 1
                                        time.sleep(3)
                                        continue
                                    else:
                                        self.logger.info("已到达最后一页")
                                        break
                                else:
                                    self.logger.info("未找到下一页按钮")
                                    break
                            except Exception as e:
                                self.logger.warning(f"翻页失败: {e}")
                                break
                        else:
                            break
                
                # 解析当前页面的处罚信息
                try:
                    # 查找包含"行政处罚信息公开表"的链接
                    punishment_links = self.driver.find_elements(
                        By.XPATH, 
                        '//a[contains(text(), "行政处罚信息公示") or contains(text(), "行政处罚信息公开") or contains(text(), "处罚信息")]'
                    )
                    
                    if not punishment_links:
                        # 尝试其他可能的链接模式
                        punishment_links = self.driver.find_elements(
                            By.XPATH, 
                            '//a[contains(@href, "ItemDetail")]'
                        )
                    
                    page_punishment_list = []
                    for link in punishment_links:
                        try:
                            href = link.get_attribute('href')
                            title = clean_text(link.text)
                            
                            if href and title:
                                # 构建完整URL
                                if not href.startswith('http'):
                                    href = urllib.parse.urljoin('https://www.nfra.gov.cn', href)
                                
                                punishment_info = {
                                    'title': title,
                                    'detail_url': href,
                                    'category': category,
                                    'page': current_page
                                }
                                page_punishment_list.append(punishment_info)
                                
                        except Exception as e:
                            self.logger.warning(f"解析链接失败: {e}")
                            continue
                    
                    self.logger.info(f"第 {current_page} 页找到 {len(page_punishment_list)} 条处罚信息")
                    all_punishment_list.extend(page_punishment_list)
                    
                    # 检查是否有下一页
                    if current_page < max_pages:
                        try:
                            # 查找下一页按钮
                            next_buttons = self.driver.find_elements(
                                By.XPATH, 
                                '//span[text()="下一页"] | //a[text()="下一页"] | //a[contains(text(), "下一页")]'
                            )
                            
                            if next_buttons:
                                next_button = next_buttons[0]
                                # 检查按钮是否可点击
                                if next_button.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    current_page += 1
                                    time.sleep(3)  # 等待页面跳转
                                else:
                                    self.logger.info("已到达最后一页")
                                    break
                            else:
                                self.logger.info("未找到下一页按钮，可能已到达最后一页")
                                break
                                
                        except Exception as e:
                            self.logger.warning(f"翻页失败: {e}")
                            break
                    else:
                        break
                        
                except Exception as e:
                    self.logger.error(f"解析第 {current_page} 页失败: {e}")
                    break
            
            # 智能检查结果反馈
            if use_smart_check and not found_target_month:
                self.logger.info(f"{category} 智能检查完成，未找到 {target_year}年{target_month}月 的数据")
            
            self.logger.info(f"{category} 处罚列表解析完成，共找到 {len(all_punishment_list)} 条记录")
            return all_punishment_list
            
        except Exception as e:
            self.logger.error(f"解析 {category} 处罚列表失败: {e}")
            return all_punishment_list
    
    def get_punishment_list(self, category: str, max_pages: int = 10) -> List[Dict]:
        """获取处罚信息列表"""
        url = BASE_URLS.get(category)
        if not url:
            self.logger.error(f"未找到类别 '{category}' 对应的URL")
            return []
        
        if not self.load_page_with_retry(url):
            self.logger.error(f"无法加载 {category} 页面")
            return []
        
        all_punishment_list = []
        current_page = 1
        
        try:
            while current_page <= max_pages:
                self.logger.info(f"正在解析 {category} 第 {current_page} 页")
                
                # 等待页面加载完成
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)  # 额外等待确保内容加载
                
                # 查找包含"行政处罚信息公开表"的链接
                try:
                    # 使用更宽泛的XPath选择器
                    punishment_links = self.driver.find_elements(
                        By.XPATH, 
                        '//a[contains(text(), "行政处罚信息公示") or contains(text(), "行政处罚信息公开") or contains(text(), "处罚信息")]'
                    )
                    
                    if not punishment_links:
                        # 尝试其他可能的链接模式
                        punishment_links = self.driver.find_elements(
                            By.XPATH, 
                            '//a[contains(@href, "ItemDetail")]'
                        )
                    
                    page_punishment_list = []
                    for link in punishment_links:
                        try:
                            href = link.get_attribute('href')
                            title = clean_text(link.text)
                            
                            if href and title:
                                # 构建完整URL
                                if not href.startswith('http'):
                                    href = urllib.parse.urljoin('https://www.nfra.gov.cn', href)
                                
                                punishment_info = {
                                    'title': title,
                                    'detail_url': href,
                                    'category': category,
                                    'page': current_page
                                }
                                page_punishment_list.append(punishment_info)
                                
                        except Exception as e:
                            self.logger.warning(f"解析链接失败: {e}")
                            continue
                    
                    self.logger.info(f"第 {current_page} 页找到 {len(page_punishment_list)} 条处罚信息")
                    all_punishment_list.extend(page_punishment_list)
                    
                    # 检查是否有下一页
                    if current_page < max_pages:
                        try:
                            # 查找下一页按钮
                            next_buttons = self.driver.find_elements(
                                By.XPATH, 
                                '//span[text()="下一页"] | //a[text()="下一页"] | //a[contains(text(), "下一页")]'
                            )
                            
                            if next_buttons:
                                next_button = next_buttons[0]
                                # 检查按钮是否可点击
                                if next_button.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    current_page += 1
                                    time.sleep(3)  # 等待页面跳转
                                else:
                                    self.logger.info("已到达最后一页")
                                    break
                            else:
                                self.logger.info("未找到下一页按钮，可能已到达最后一页")
                                break
                                
                        except Exception as e:
                            self.logger.warning(f"翻页失败: {e}")
                            break
                    else:
                        break
                        
                except Exception as e:
                    self.logger.error(f"解析第 {current_page} 页失败: {e}")
                    break
            
            self.logger.info(f"{category} 处罚列表解析完成，共找到 {len(all_punishment_list)} 条记录")
            return all_punishment_list
            
        except Exception as e:
            self.logger.error(f"解析 {category} 处罚列表失败: {e}")
            return all_punishment_list
    
    def get_punishment_detail(self, detail_url: str) -> Dict:
        """获取处罚详情"""
        if not self.load_page_with_retry(detail_url):
            self.logger.error(f"无法加载详情页面: {detail_url}")
            return {}
        
        try:
            # 等待表格加载 - 支持多种表格类型
            table = None
            try:
                # 首先尝试查找 MsoTableGrid 类型的表格
                table = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "MsoTableGrid"))
                )
            except:
                try:
                    # 如果没找到，尝试查找 MsoNormalTable 类型的表格
                    table = self.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "MsoNormalTable"))
                    )
                except:
                    # 如果都没找到，尝试查找任何table元素
                    tables = self.driver.find_elements(By.TAG_NAME, "table")
                    if tables:
                        table = tables[0]  # 使用第一个表格
            
            if table:
                # 解析表格数据
                detail_data = self.parse_punishment_table(table)
                
                # 添加抓取时间和链接
                detail_data['抓取时间'] = get_current_timestamp()
                detail_data['详情链接'] = detail_url
                
                return detail_data
            else:
                self.logger.error(f"未找到表格元素: {detail_url}")
                return {}
                
        except TimeoutException:
            self.logger.error(f"详情页面表格加载超时: {detail_url}")
        except Exception as e:
            self.logger.error(f"解析详情页面失败: {e}")
        
        return {}
    
    def parse_punishment_table(self, table_element) -> Dict:
        """解析处罚信息表格 - 增强版本支持多种表格格式"""
        try:
            # 将Selenium元素转换为BeautifulSoup对象进行解析
            table_html = table_element.get_attribute('outerHTML')
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            
            if not table:
                return {}
            
            # 首先尝试提取完整的页面文本内容用于备用解析
            page_text = clean_text(table.get_text())
            self.logger.debug(f"页面文本内容长度: {len(page_text)}")
            
            # 尝试从完整文本中提取行政处罚依据
            punishment_basis = self.extract_punishment_basis_from_text(page_text)
            
            # 初始化数据字典
            data = {}
            if punishment_basis:
                data['行政处罚依据'] = punishment_basis
            
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                return data if data else {}
            
            # 检查表格类型：横向多列 vs 键值对
            first_row = rows[0]
            first_row_cells = first_row.find_all(['td', 'th'])
            
            # 如果第一行有多个列（>=3），且包含常见的表头关键词，则为横向表格
            if len(first_row_cells) >= 3:
                header_texts = [clean_text(cell.get_text()) for cell in first_row_cells]
                
                # 检查是否包含典型的表头关键词
                header_keywords = ['序号', '当事人', '违法', '处罚', '机关']
                if any(any(keyword in header for keyword in header_keywords) for header in header_texts):
                    self.logger.info("检测到横向多列表格，使用横向解析逻辑")
                    table_data = self.parse_horizontal_table(rows)
                    data.update(table_data)
                    return data
            
            # 否则使用键值对解析逻辑
            self.logger.info("检测到键值对表格，使用键值对解析逻辑")
            table_data = self.parse_key_value_table(rows)
            data.update(table_data)
            
            # 如果键值对解析没有找到处罚内容，尝试从完整文本中提取
            if '行政处罚内容' not in data or not data['行政处罚内容']:
                punishment_content = self.extract_punishment_content_from_text(page_text)
                if punishment_content:
                    data['行政处罚内容'] = punishment_content
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析处罚表格失败: {e}")
            return {}
    
    def extract_punishment_basis_from_text(self, text: str) -> str:
        """从完整文本中提取行政处罚依据"""
        try:
            import re
            
            # 常见的处罚依据关键词模式
            basis_patterns = [
                # 完整的法条引用
                r'依据[《]?([^》。；\n]+第[^。；\n]+条[^。；\n]*)[》]?',
                r'根据[《]?([^》。；\n]+第[^。；\n]+条[^。；\n]*)[》]?',
                r'按照[《]?([^》。；\n]+第[^。；\n]+条[^。；\n]*)[》]?',
                # 法律法规名称
                r'《([^》]+法[^》]*)》',
                r'《([^》]+规定[^》]*)》',
                r'《([^》]+办法[^》]*)》',
                r'《([^》]+条例[^》]*)》',
                # 简单的依据引用
                r'依据[《]?([^》。；\n]+)[》]?[，。]',
                r'根据[《]?([^》。；\n]+)[》]?[，。]',
                r'违反[了]?[《]?([^》。；\n]+)[》]?',
            ]
            
            found_basis = []
            
            for pattern in basis_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if match and len(match.strip()) > 3:
                        clean_match = clean_text(match).strip()
                        # 避免重复和过短的匹配
                        if clean_match not in found_basis and len(clean_match) > 5:
                            found_basis.append(clean_match)
            
            if found_basis:
                basis_text = "；".join(found_basis)
                self.logger.debug(f"提取到行政处罚依据: {basis_text}")
                return basis_text
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"提取行政处罚依据失败: {e}")
            return ""
    
    def extract_punishment_content_from_text(self, text: str) -> str:
        """从完整文本中提取完整的行政处罚内容"""
        try:
            import re
            
            # 查找所有处罚相关的句子
            punishment_sentences = []
            
            # 改进的匹配"对...处罚"模式
            fine_patterns = [
                # 匹配：对XXX警告并罚款X万元
                r'对([^对。；\n]+?)(警告并罚款[0-9]+万元)',
                # 匹配：对XXX罚款X万元
                r'对([^对。；\n]+?)(罚款[0-9]+万元[^。；\n]*)',
                # 匹配：对XXX警告
                r'对([^对。；\n]+?)(警告[^。；\n]*)',
            ]
            
            for pattern in fine_patterns:
                matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        # 对当事人的处罚
                        person = clean_text(match[0]).strip()
                        punishment = clean_text(match[1]).strip()
                        if person and punishment:
                            sentence = f"对{person}{punishment}"
                            punishment_sentences.append(sentence)
            
            # 单独提取合计信息和详细说明
            summary_patterns = [
                r'(合计罚款[0-9]+万元[^。；\n]*)',
                r'(其中[^。；\n]*[0-9]+万元[^。；\n]*)',
            ]
            
            for pattern in summary_patterns:
                matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
                for match in matches:
                    sentence = clean_text(match).strip()
                    if sentence and len(sentence) > 3:
                        punishment_sentences.append(sentence)
            
            # 使用行分割的方式重新提取，确保不遗漏
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 查找包含处罚关键词的行
                if any(keyword in line for keyword in ['对', '罚款', '万元', '警告']):
                    # 进一步处理每一行
                    # 分割可能包含多个处罚的行
                    sub_sentences = re.split(r'(?=对[^对]*(?:警告|罚款))', line)
                    for sub_sentence in sub_sentences:
                        sub_sentence = sub_sentence.strip()
                        if len(sub_sentence) > 3 and ('罚款' in sub_sentence or '警告' in sub_sentence):
                            clean_sentence = clean_text(sub_sentence)
                            # 避免重复添加
                            if clean_sentence not in punishment_sentences:
                                punishment_sentences.append(clean_sentence)
            
            # 智能去重：移除完全包含在其他句子中的内容
            unique_sentences = []
            for sentence in punishment_sentences:
                if sentence and len(sentence) > 3:
                    sentence = sentence.strip('。；，')
                    
                    # 检查是否被其他句子包含
                    is_duplicate = False
                    for existing in unique_sentences:
                        if sentence in existing or existing in sentence:
                            # 保留更完整的版本
                            if len(sentence) > len(existing):
                                unique_sentences.remove(existing)
                                break
                            else:
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        unique_sentences.append(sentence)
            
            if unique_sentences:
                content = "；".join(unique_sentences)
                self.logger.debug(f"提取到行政处罚内容，共{len(unique_sentences)}条: {content[:200]}...")
                return content
            
            return ""
            
        except Exception as e:
            self.logger.warning(f"提取行政处罚内容失败: {e}")
            return ""
    
    def parse_horizontal_table(self, rows: list) -> Dict:
        """解析横向多列表格，支持多行数据"""
        try:
            if len(rows) < 2:
                return {}
            
            # 解析表头
            header_row = rows[0]
            header_cells = header_row.find_all(['td', 'th'])
            headers = [clean_text(cell.get_text()) for cell in header_cells]
            
            self.logger.debug(f"表头: {headers}")
            
            # 如果只有2行，使用原有逻辑（单条记录）
            if len(rows) == 2:
                return self.parse_single_row_table(headers, rows[1])
            
            # 多行数据处理
            elif len(rows) > 2:
                return self.parse_multi_row_table(headers, rows[1:])
            
            return {}
            
        except Exception as e:
            self.logger.error(f"解析横向表格失败: {e}")
            return {}
    
    def parse_single_row_table(self, headers: list, data_row) -> Dict:
        """解析单行数据表格"""
        try:
            data_cells = data_row.find_all(['td', 'th'])
            
            if len(data_cells) < len(headers):
                self.logger.warning(f"数据列数({len(data_cells)})少于表头列数({len(headers)})")
                return {}
            
            data = {}
            
            # 根据表头映射数据
            for i, header in enumerate(headers):
                if i < len(data_cells):
                    cell_text = clean_text(data_cells[i].get_text())
                    
                    # 字段映射
                    if any(keyword in header for keyword in ['序号']):
                        data['序号'] = cell_text
                    elif any(keyword in header for keyword in ['当事人', '被处罚当事人']):
                        data['当事人名称'] = cell_text
                    elif any(keyword in header for keyword in ['违法违规', '主要违法违规', '违法行为', '违法违规事实', '主要违法违规事实']):
                        data['主要违法违规行为'] = cell_text
                    elif any(keyword in header for keyword in ['处罚内容', '行政处罚', '处罚决定', '行政处罚内容', '行政处罚决定']):
                        data['行政处罚内容'] = cell_text
                    elif any(keyword in header for keyword in ['决定机关', '机关名称', '作出决定机关', '作出处罚决定的机关', '作出处罚决定的机关名称']):
                        data['作出决定机关'] = cell_text
                    elif any(keyword in header for keyword in ['决定日期', '作出处罚决定的日期', '处罚决定日期']):
                        data['作出决定日期'] = cell_text
                    elif any(keyword in header for keyword in ['处罚依据', '行政处罚依据']):
                        data['行政处罚依据'] = cell_text
                    elif any(keyword in header for keyword in ['决定书文号', '行政处罚决定书文号']):
                        data['行政处罚决定书文号'] = cell_text
                    else:
                        # 保存其他字段
                        data[header] = cell_text
            
            self.logger.debug(f"单行表格解析结果: {data}")
            return data
            
        except Exception as e:
            self.logger.error(f"解析单行表格失败: {e}")
            return {}
    
    def parse_multi_row_table(self, headers: list, data_rows: list) -> Dict:
        """解析多行数据表格，返回多条记录"""
        try:
            # 首先检查是否有合并单元格
            if self.has_merged_cells(data_rows):
                self.logger.info("检测到合并单元格，使用合并单元格解析逻辑")
                return self.parse_merged_cells_table(headers, data_rows)
            
            # 原有的多行表格解析逻辑
            all_records = []
            
            for row_index, data_row in enumerate(data_rows, 1):
                data_cells = data_row.find_all(['td', 'th'])
                
                if len(data_cells) < len(headers):
                    self.logger.warning(f"第{row_index}行数据列数({len(data_cells)})少于表头列数({len(headers)})")
                    continue
                
                record = {}
                
                # 根据表头映射数据
                for i, header in enumerate(headers):
                    if i < len(data_cells):
                        cell_text = clean_text(data_cells[i].get_text())
                        
                        # 字段映射
                        if any(keyword in header for keyword in ['序号']):
                            record['序号'] = cell_text
                            record['原始序号'] = cell_text  # 保留原始序号
                        elif any(keyword in header for keyword in ['当事人', '被处罚当事人']):
                            record['当事人名称'] = cell_text
                        elif any(keyword in header for keyword in ['违法违规', '主要违法违规', '违法行为', '违法违规事实', '主要违法违规事实']):
                            record['主要违法违规行为'] = cell_text
                        elif any(keyword in header for keyword in ['处罚内容', '行政处罚', '处罚决定', '行政处罚内容', '行政处罚决定']):
                            record['行政处罚内容'] = cell_text
                        elif any(keyword in header for keyword in ['决定机关', '机关名称', '作出决定机关', '作出处罚决定的机关', '作出处罚决定的机关名称']):
                            record['作出决定机关'] = cell_text
                        elif any(keyword in header for keyword in ['决定日期', '作出处罚决定的日期', '处罚决定日期']):
                            record['作出决定日期'] = cell_text
                        elif any(keyword in header for keyword in ['处罚依据', '行政处罚依据']):
                            record['行政处罚依据'] = cell_text
                        elif any(keyword in header for keyword in ['决定书文号', '行政处罚决定书文号']):
                            record['行政处罚决定书文号'] = cell_text
                        else:
                            # 保存其他字段
                            record[header] = cell_text
                
                # 添加记录标识信息
                record['批文内序号'] = row_index
                record['是否多记录批文'] = '是'
                
                if any(record.values()):  # 只添加非空记录
                    all_records.append(record)
                    self.logger.debug(f"解析第{row_index}条记录: {record.get('当事人名称', '未知')}")
            
            # 返回格式：如果有多条记录，使用特殊格式
            if len(all_records) > 1:
                self.logger.info(f"检测到多记录批文，共{len(all_records)}条记录")
                # 返回第一条记录作为主记录，其他记录作为additional_records
                result = all_records[0].copy()
                result['additional_records'] = all_records[1:]
                result['记录总数'] = len(all_records)
                return result
            elif len(all_records) == 1:
                all_records[0]['是否多记录批文'] = '否'
                return all_records[0]
            else:
                self.logger.warning("多行表格未解析到有效数据")
                return {}
            
        except Exception as e:
            self.logger.error(f"解析多行表格失败: {e}")
            return {}
    
    def has_merged_cells(self, data_rows: list) -> bool:
        """检测表格是否有合并单元格"""
        try:
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    rowspan = cell.get('rowspan')
                    colspan = cell.get('colspan') 
                    if (rowspan and int(rowspan) > 1) or (colspan and int(colspan) > 1):
                        return True
            return False
        except Exception as e:
            self.logger.warning(f"检测合并单元格失败: {e}")
            return False
    
    def parse_merged_cells_table(self, headers: list, data_rows: list) -> Dict:
        """解析包含合并单元格的表格"""
        try:
            all_records = []
            
            # 创建一个虚拟网格来追踪合并单元格
            grid = {}
            max_cols = len(headers)
            
            for row_idx, row in enumerate(data_rows):
                cells = row.find_all(['td', 'th'])
                cell_idx = 0
                col_idx = 0
                
                for cell in cells:
                    # 跳过被合并单元格占用的位置
                    while (row_idx, col_idx) in grid:
                        col_idx += 1
                    
                    # 获取单元格内容
                    cell_text = clean_text(cell.get_text())
                    
                    # 获取合并属性
                    rowspan = int(cell.get('rowspan', 1))
                    colspan = int(cell.get('colspan', 1))
                    
                    # 在网格中标记这个单元格及其合并范围
                    for r in range(row_idx, row_idx + rowspan):
                        for c in range(col_idx, col_idx + colspan):
                            if c < max_cols:  # 确保不超出表头范围
                                grid[(r, c)] = {
                                    'text': cell_text,
                                    'original_row': row_idx,
                                    'original_col': col_idx,
                                    'rowspan': rowspan,
                                    'colspan': colspan
                                }
                    
                    col_idx += colspan
                    cell_idx += 1
            
            # 现在根据网格数据构建记录
            processed_rows = {}
            
            for (row_idx, col_idx), cell_info in grid.items():
                if row_idx not in processed_rows:
                    processed_rows[row_idx] = {}
                
                if col_idx < len(headers):
                    header = headers[col_idx]
                    processed_rows[row_idx][header] = cell_info['text']
            
            # 处理每一行数据
            for row_idx in sorted(processed_rows.keys()):
                row_data = processed_rows[row_idx]
                
                # 对于合并单元格，需要从前面的行继承数据
                if row_idx > 0:
                    # 检查哪些字段在这一行是空的（可能被合并单元格跨行覆盖）
                    for col_idx, header in enumerate(headers):
                        if header not in row_data or not row_data[header]:
                            # 查找这个位置是否被前面行的合并单元格覆盖
                            for prev_row_idx in range(row_idx - 1, -1, -1):
                                cell_key = (prev_row_idx, col_idx)
                                if cell_key in grid:
                                    cell_info = grid[cell_key]
                                    # 检查这个合并单元格是否覆盖当前行
                                    if (prev_row_idx + cell_info['rowspan'] > row_idx):
                                        row_data[header] = cell_info['text']
                                        break
                
                # 构建记录
                record = {}
                
                for header, cell_text in row_data.items():
                    if not cell_text:
                        continue
                        
                    # 字段映射逻辑
                    if any(keyword in header for keyword in ['序号']):
                        record['序号'] = cell_text
                        record['原始序号'] = cell_text
                    elif any(keyword in header for keyword in ['当事人', '被处罚当事人']):
                        record['当事人名称'] = cell_text
                    elif any(keyword in header for keyword in ['违法违规', '主要违法违规', '违法行为', '违法违规事实', '主要违法违规事实']):
                        record['主要违法违规行为'] = cell_text
                    elif any(keyword in header for keyword in ['处罚内容', '行政处罚', '处罚决定', '行政处罚内容', '行政处罚决定']):
                        record['行政处罚内容'] = cell_text
                    elif any(keyword in header for keyword in ['决定机关', '机关名称', '作出决定机关', '作出处罚决定的机关', '作出处罚决定的机关名称']):
                        record['作出决定机关'] = cell_text
                    elif any(keyword in header for keyword in ['决定日期', '作出处罚决定的日期', '处罚决定日期']):
                        record['作出决定日期'] = cell_text
                    elif any(keyword in header for keyword in ['处罚依据', '行政处罚依据']):
                        record['行政处罚依据'] = cell_text
                    elif any(keyword in header for keyword in ['决定书文号', '行政处罚决定书文号']):
                        record['行政处罚决定书文号'] = cell_text
                    else:
                        record[header] = cell_text
                
                # 添加记录标识信息
                record['批文内序号'] = row_idx + 1
                record['是否多记录批文'] = '是'
                
                # 只添加有实际当事人数据的记录（避免添加只有合并单元格数据的空记录）
                if record.get('当事人名称') and record['当事人名称'].strip():
                    all_records.append(record)
                    self.logger.info(f"解析合并单元格记录: {record.get('当事人名称', '未知')}")
            
            # 返回结果
            if len(all_records) > 1:
                self.logger.info(f"合并单元格表格解析完成，共{len(all_records)}条记录")
                result = all_records[0].copy()
                result['additional_records'] = all_records[1:]
                result['记录总数'] = len(all_records)
                return result
            elif len(all_records) == 1:
                all_records[0]['是否多记录批文'] = '否'
                return all_records[0]
            else:
                self.logger.warning("合并单元格表格未解析到有效数据")
                return {}
                
        except Exception as e:
            self.logger.error(f"解析合并单元格表格失败: {e}")
            return {}
    
    def parse_key_value_table(self, rows: list) -> Dict:
        """解析键值对表格（左右两列）"""
        try:
            data = {}
            
            # 遍历所有行，查找字段对应关系
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 2:
                    # 获取左右两列的内容
                    left_cell = cells[0]
                    right_cell = cells[1]
                    
                    left_text = clean_text(left_cell.get_text())
                    right_text = clean_text(right_cell.get_text())
                    
                    # 跳过空内容
                    if not left_text or not right_text:
                        continue
                    
                    # 增强的字段映射规则 - 使用更精确的匹配，优先匹配更具体的字段名
                    # 精确匹配优先
                    if left_text in ['序号']:
                        data['序号'] = right_text
                    elif left_text in ['当事人名称', '被处罚当事人', '当事人']:
                        data['当事人名称'] = right_text
                    elif left_text in ['主要违法违规事实', '主要违法违规行为', '违法违规事实', '违法违规行为', '违法行为']:
                        data['主要违法违规行为'] = right_text
                    elif left_text in ['行政处罚依据', '处罚依据']:
                        data['行政处罚依据'] = right_text
                    elif left_text in ['行政处罚决定', '处罚决定']:
                        data['行政处罚内容'] = right_text
                    elif left_text in ['行政处罚内容', '处罚内容']:
                        data['行政处罚内容'] = right_text
                    elif left_text in ['作出处罚决定的机关名称', '作出决定机关', '决定机关', '机关名称', '作出处罚决定的机关']:
                        data['作出决定机关'] = right_text
                    elif left_text in ['作出处罚决定的日期', '作出决定日期', '决定日期', '处罚决定日期']:
                        data['作出决定日期'] = right_text
                    elif left_text in ['行政处罚决定书文号', '决定书文号']:
                        data['行政处罚决定书文号'] = right_text
                    # 包含匹配（作为后备）
                    elif '序号' in left_text:
                        data['序号'] = right_text
                    elif any(keyword in left_text for keyword in ['当事人', '被处罚当事人']):
                        data['当事人名称'] = right_text
                    elif any(keyword in left_text for keyword in ['违法违规事实', '违法违规行为', '主要违法违规', '违法行为']):
                        data['主要违法违规行为'] = right_text
                    elif '行政处罚依据' in left_text or '处罚依据' in left_text:
                        data['行政处罚依据'] = right_text
                    elif '行政处罚决定' in left_text and '机关' not in left_text and '日期' not in left_text:
                        data['行政处罚内容'] = right_text
                    elif '处罚内容' in left_text:
                        data['行政处罚内容'] = right_text
                    elif any(keyword in left_text for keyword in ['作出处罚决定的机关', '决定机关', '机关名称']) and '日期' not in left_text:
                        data['作出决定机关'] = right_text
                    elif any(keyword in left_text for keyword in ['作出处罚决定的日期', '决定日期', '处罚决定日期']):
                        data['作出决定日期'] = right_text
                    elif any(keyword in left_text for keyword in ['决定书文号', '行政处罚决定书文号']):
                        data['行政处罚决定书文号'] = right_text
                    else:
                        # 保存其他字段
                        data[left_text] = right_text
            
            self.logger.debug(f"键值对表格解析结果: {data}")
            return data
            
        except Exception as e:
            self.logger.error(f"解析键值对表格失败: {e}")
            return {}
    
    def process_link_with_new_window(self, href: str, title: str) -> Dict:
        """在新窗口中处理链接 - 参考用户代码的窗口处理方式"""
        try:
            self.logger.info(f"正在处理: {title}")
            time.sleep(1)  # 避免请求过快
            
            # 在新窗口中打开链接
            self.driver.execute_script("window.open(arguments[0], '_blank');", href)
            new_window = self.driver.window_handles[-1]
            original_window = self.driver.window_handles[0]
            
            # 切换到新窗口
            self.driver.switch_to.window(new_window)
            
            try:
                # 等待页面加载
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                time.sleep(2)
                
                # 提取发布时间
                publish_time = self.extract_publish_time()
                
                # 查找表格
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                # 支持多种表格类型
                tables = soup.find_all('table', class_=['MsoTableGrid', 'MsoNormalTable'])
                
                if not tables:
                    # 如果没找到指定类的表格，查找所有表格
                    tables = soup.find_all('table')
                
                detail_data = {}
                for table in tables:
                    # 解析表格内容
                    table_data = self.parse_table_from_soup(table)
                    if table_data:
                        detail_data.update(table_data)
                        break  # 只处理第一个有效表格
                
                if detail_data:
                    # 处理多记录情况
                    result_records = []
                    
                    # 添加基础信息
                    base_info = {
                        '抓取时间': get_current_timestamp(),
                        '详情链接': href,
                        '标题': title,
                        '发布时间': publish_time  # 确保发布时间被包含
                    }
                    
                    # 检查是否有additional_records（多记录批文）
                    if 'additional_records' in detail_data:
                        additional_records = detail_data.pop('additional_records')
                        
                        # 主记录
                        main_record = {**detail_data, **base_info}
                        result_records.append(main_record)
                        
                        # 附加记录
                        for add_record in additional_records:
                            # 继承主记录的共同信息（如决定机关、标题等）
                            combined_record = {**base_info}
                            
                            # 添加附加记录的特定信息
                            combined_record.update(add_record)
                            
                            # 继承主记录中的共同字段（如果附加记录中没有）
                            for key in ['作出决定机关', '行政处罚决定书文号', '标题', '发布时间']:
                                if key in detail_data and (key not in combined_record or not combined_record[key]):
                                    combined_record[key] = detail_data[key]
                            
                            result_records.append(combined_record)
                        
                        self.logger.info(f"成功解析多记录处罚信息: {title}，共{len(result_records)}条记录")
                        
                        # 返回多记录标识
                        return {
                            'is_multi_record': True,
                            'records': result_records,
                            'total_count': len(result_records)
                        }
                    else:
                        # 单记录情况
                        detail_data.update(base_info)
                        self.logger.info(f"成功解析处罚信息: {title}")
                        return detail_data
                else:
                    self.logger.warning(f"未找到有效表格数据: {title}")
                
                return detail_data
                
            finally:
                # 关闭新窗口并切换回原窗口
                self.driver.close()
                self.driver.switch_to.window(original_window)
                
        except Exception as e:
            self.logger.error(f"处理链接失败 {href}: {e}")
            try:
                # 确保切换回原窗口
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return {}
    
    def parse_table_from_soup(self, table) -> Dict:
        """从BeautifulSoup表格对象解析数据 - 增强版本支持多种表格格式"""
        try:
            # 首先尝试提取完整的页面文本内容用于备用解析
            page_text = clean_text(table.get_text())
            self.logger.debug(f"表格文本内容长度: {len(page_text)}")
            
            # 尝试从完整文本中提取行政处罚依据
            punishment_basis = self.extract_punishment_basis_from_text(page_text)
            
            # 初始化数据字典
            data = {}
            if punishment_basis:
                data['行政处罚依据'] = punishment_basis
            
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                return data if data else {}
            
            # 检查表格类型：横向多列 vs 键值对
            first_row = rows[0]
            first_row_cells = first_row.find_all(['td', 'th'])
            
            # 如果第一行有多个列（>=3），且包含常见的表头关键词，则为横向表格
            if len(first_row_cells) >= 3:
                header_texts = [clean_text(cell.get_text()) for cell in first_row_cells]
                
                # 检查是否包含典型的表头关键词
                header_keywords = ['序号', '当事人', '违法', '处罚', '机关']
                if any(any(keyword in header for keyword in header_keywords) for header in header_texts):
                    self.logger.info("检测到横向多列表格，使用横向解析逻辑")
                    table_data = self.parse_horizontal_table(rows)
                    data.update(table_data)
                    return data
            
            # 否则使用键值对解析逻辑
            self.logger.info("检测到键值对表格，使用键值对解析逻辑")
            table_data = self.parse_key_value_table(rows)
            data.update(table_data)
            
            # 如果键值对解析没有找到处罚内容，尝试从完整文本中提取
            if '行政处罚内容' not in data or not data['行政处罚内容']:
                punishment_content = self.extract_punishment_content_from_text(page_text)
                if punishment_content:
                    data['行政处罚内容'] = punishment_content
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析表格失败: {e}")
            return {}
    
    def crawl_category_smart(self, category: str, target_year: int = None, target_month: int = None, max_pages: int = 10, max_records: int = None) -> List[Dict]:
        """智能爬取指定类别的处罚信息 - 支持按月份过滤"""
        self.logger.info(f"开始智能爬取 {category} 处罚信息")
        
        if target_year and target_month:
            self.logger.info(f"目标月份: {target_year}年{target_month}月")
        
        # 使用智能方法获取处罚列表
        punishment_list = self.get_punishment_list_smart(category, target_year, target_month, max_pages)
        
        if not punishment_list:
            self.logger.warning(f"{category} 没有找到处罚信息")
            return []
        
        # 如果设置了max_records，限制处理的记录数量
        if max_records and len(punishment_list) > max_records:
            self.logger.info(f"{category} 找到 {len(punishment_list)} 条记录，限制处理前 {max_records} 条（测试模式）")
            punishment_list = punishment_list[:max_records]
        
        # 获取详情信息
        detailed_data = []
        for i, item in enumerate(punishment_list, 1):
            self.logger.info(f"正在处理 {category} 第 {i}/{len(punishment_list)} 条记录")
            
            detail_url = item.get('detail_url')
            if not detail_url:
                self.logger.warning(f"第 {i} 条记录缺少详情链接")
                continue
            
            # 使用新窗口处理方式
            detail_data = self.process_link_with_new_window(detail_url, item.get('title', ''))
            
            if detail_data:
                # 检查是否为多记录批文
                if isinstance(detail_data, dict) and detail_data.get('is_multi_record'):
                    # 多记录情况：展开所有记录
                    records = detail_data.get('records', [])
                    for record in records:
                        # 合并列表信息和详情信息
                        combined_data = {**item, **record}
                        detailed_data.append(combined_data)
                    
                    self.logger.info(f"多记录批文处理完成，展开为{len(records)}条独立记录")
                else:
                    # 单记录情况
                    combined_data = {**item, **detail_data}
                    detailed_data.append(combined_data)
            
            # 请求间隔
            time.sleep(CRAWL_CONFIG['delay_between_requests'])
        
        self.logger.info(f"{category} 处罚信息爬取完成，共获得 {len(detailed_data)} 条详细记录")
        return detailed_data

    def crawl_category(self, category: str, max_pages: int = 5, max_records: int = None) -> List[Dict]:
        """爬取指定类别的所有处罚信息"""
        self.logger.info(f"开始爬取 {category} 处罚信息")
        
        # 获取处罚列表
        punishment_list = self.get_punishment_list(category, max_pages)
        
        if not punishment_list:
            self.logger.warning(f"{category} 没有找到处罚信息")
            return []
        
        # 如果设置了max_records，限制处理的记录数量
        if max_records and len(punishment_list) > max_records:
            self.logger.info(f"{category} 找到 {len(punishment_list)} 条记录，限制处理前 {max_records} 条（测试模式）")
            punishment_list = punishment_list[:max_records]
        
        # 获取详情信息
        detailed_data = []
        for i, item in enumerate(punishment_list, 1):
            self.logger.info(f"正在处理 {category} 第 {i}/{len(punishment_list)} 条记录")
            
            detail_url = item.get('detail_url')
            if not detail_url:
                self.logger.warning(f"第 {i} 条记录缺少详情链接")
                continue
            
            # 使用新窗口处理方式
            detail_data = self.process_link_with_new_window(detail_url, item.get('title', ''))
            
            if detail_data:
                # 检查是否为多记录批文
                if isinstance(detail_data, dict) and detail_data.get('is_multi_record'):
                    # 多记录情况：展开所有记录
                    records = detail_data.get('records', [])
                    for record in records:
                        # 合并列表信息和详情信息
                        combined_data = {**item, **record}
                        detailed_data.append(combined_data)
                    
                    self.logger.info(f"多记录批文处理完成，展开为{len(records)}条独立记录")
                else:
                    # 单记录情况
                    combined_data = {**item, **detail_data}
                    detailed_data.append(combined_data)
            
            # 请求间隔
            time.sleep(CRAWL_CONFIG['delay_between_requests'])
        
        self.logger.info(f"{category} 处罚信息爬取完成，共获得 {len(detailed_data)} 条详细记录")
        return detailed_data
    
    def crawl_all_smart(self, target_year: int = None, target_month: int = None, max_pages_per_category: int = 10, max_records_per_category: int = None) -> Dict[str, List[Dict]]:
        """智能爬取所有类别的处罚信息 - 支持按月份过滤"""
        if not self.setup_driver():
            self.logger.error("无法初始化WebDriver，爬取失败")
            return {}
        
        all_data = {}
        
        # 打印智能爬取信息
        if target_year and target_month:
            self.logger.info(f"启用智能爬取模式，目标月份: {target_year}年{target_month}月")
        
        try:
            for category in BASE_URLS.keys():
                self.logger.info(f"开始智能爬取 {category}")
                
                # 使用智能方法爬取
                category_data = self.crawl_category_smart(
                    category, 
                    target_year, 
                    target_month, 
                    max_pages_per_category, 
                    max_records_per_category
                )
                
                all_data[category] = category_data
                
                # 记录这个分类的结果
                if category_data:
                    self.logger.info(f"{category} 完成，获得 {len(category_data)} 条记录")
                else:
                    self.logger.info(f"{category} 完成，未找到目标月份的数据")
                
                # 类别间延迟
                time.sleep(CRAWL_CONFIG['delay_between_requests'] * 2)
            
            # 统计总结果
            total_records = sum(len(records) for records in all_data.values())
            if target_year and target_month:
                self.logger.info(f"智能爬取完成，{target_year}年{target_month}月共获得 {total_records} 条记录")
            else:
                self.logger.info(f"爬取完成，共获得 {total_records} 条记录")
            
        except Exception as e:
            self.logger.error(f"爬取过程中发生错误: {e}")
        finally:
            self.close_driver()
        
        return all_data

    def crawl_all(self, max_pages_per_category: int = 5, max_records_per_category: int = None) -> Dict[str, List[Dict]]:
        """爬取所有类别的处罚信息"""
        if not self.setup_driver():
            self.logger.error("无法初始化WebDriver，爬取失败")
            return {}
        
        all_data = {}
        
        try:
            for category in BASE_URLS.keys():
                self.logger.info(f"开始爬取 {category}")
                category_data = self.crawl_category(category, max_pages_per_category, max_records_per_category)
                all_data[category] = category_data
                
                # 类别间延迟
                time.sleep(CRAWL_CONFIG['delay_between_requests'] * 2)
            
            self.logger.info("所有类别爬取完成")
            
        except Exception as e:
            self.logger.error(f"爬取过程中发生错误: {e}")
        finally:
            self.close_driver()
        
        return all_data

    def extract_publish_time(self) -> str:
        """提取页面发布时间"""
        try:
            # 查找发布时间元素 - 支持多种格式
            time_selectors = [
                'span.ng-binding',  # 你提供的格式
                'span[ng-bind*="time"]',
                '.publish-time',
                '.pub-time',
                '.time',
                '*[class*="time"]'
            ]
            
            for selector in time_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if '发布时间' in text or '时间' in text:
                            # 提取时间部分，支持多种格式
                            import re
                            # 匹配 YYYY-MM-DD 格式
                            time_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
                            if time_match:
                                self.logger.debug(f"找到发布时间: {time_match.group(1)}")
                                return time_match.group(1)
                except:
                    continue
            
            # 如果没找到专门的发布时间元素，尝试从页面内容中提取
            try:
                page_source = self.driver.page_source
                import re
                # 查找发布时间相关的模式
                patterns = [
                    r'发布时间[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                    r'时间[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                    r'日期[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, page_source)
                    if match:
                        self.logger.debug(f"从页面源码提取发布时间: {match.group(1)}")
                        return match.group(1)
                        
            except Exception as e:
                self.logger.debug(f"从页面源码提取时间失败: {e}")
            
            self.logger.debug("未找到发布时间信息")
            return ""
            
        except Exception as e:
            self.logger.warning(f"提取发布时间失败: {e}")
            return ""

    def crawl_all_smart_by_year(self, target_year: int, max_pages_per_category: int = 50, max_records_per_category: int = None) -> Dict[str, List[Dict]]:
        """智能爬取指定年份的所有处罚信息 - 支持按年份过滤"""
        if not self.setup_driver():
            self.logger.error("无法初始化WebDriver，爬取失败")
            return {}
        
        all_data = {}
        
        self.logger.info(f"启用智能年份爬取模式，目标年份: {target_year}年")
        
        try:
            for category in BASE_URLS.keys():
                self.logger.info(f"开始智能爬取 {category} - {target_year}年数据")
                
                # 使用智能方法爬取指定年份
                category_data = self.crawl_category_smart_by_year(
                    category, 
                    target_year, 
                    max_pages_per_category, 
                    max_records_per_category
                )
                
                all_data[category] = category_data
                
                # 记录这个分类的结果
                if category_data:
                    self.logger.info(f"{category} 完成，获得 {len(category_data)} 条{target_year}年记录")
                else:
                    self.logger.info(f"{category} 完成，未找到{target_year}年的数据")
                
                # 类别间延迟
                time.sleep(CRAWL_CONFIG['delay_between_requests'] * 2)
            
            # 统计总结果
            total_records = sum(len(records) for records in all_data.values())
            self.logger.info(f"智能年份爬取完成，{target_year}年共获得 {total_records} 条记录")
            
        except Exception as e:
            self.logger.error(f"智能年份爬取过程中发生错误: {e}")
        finally:
            self.close_driver()
        
        return all_data

    def crawl_category_smart_by_year(self, category: str, target_year: int, max_pages: int = 50, max_records: int = None) -> List[Dict]:
        """智能爬取指定类别指定年份的处罚信息"""
        self.logger.info(f"开始智能爬取 {category} {target_year}年处罚信息")
        
        # 使用智能方法获取处罚列表，按年份过滤
        punishment_list = self.get_punishment_list_smart_by_year(category, target_year, max_pages)
        
        if not punishment_list:
            self.logger.warning(f"{category} 没有找到{target_year}年处罚信息")
            return []
        
        # 如果设置了max_records，限制处理的记录数量
        if max_records and len(punishment_list) > max_records:
            self.logger.info(f"{category} 找到 {len(punishment_list)} 条记录，限制处理前 {max_records} 条（测试模式）")
            punishment_list = punishment_list[:max_records]
        
        # 获取详情信息
        detailed_data = []
        for i, item in enumerate(punishment_list, 1):
            self.logger.info(f"正在处理 {category} 第 {i}/{len(punishment_list)} 条记录")
            
            detail_url = item.get('detail_url')
            if not detail_url:
                self.logger.warning(f"第 {i} 条记录缺少详情链接")
                continue
            
            # 使用新窗口处理方式
            detail_data = self.process_link_with_new_window(detail_url, item.get('title', ''))
            
            if detail_data:
                # 检查是否为多记录批文
                if isinstance(detail_data, dict) and detail_data.get('is_multi_record'):
                    # 多记录情况：展开所有记录
                    records = detail_data.get('records', [])
                    for record in records:
                        # 合并列表信息和详情信息
                        combined_data = {**item, **record}
                        detailed_data.append(combined_data)
                    
                    self.logger.info(f"多记录批文处理完成，展开为{len(records)}条独立记录")
                else:
                    # 单记录情况
                    combined_data = {**item, **detail_data}
                    detailed_data.append(combined_data)
            
            # 请求间隔
            time.sleep(CRAWL_CONFIG['delay_between_requests'])
        
        self.logger.info(f"{category} {target_year}年处罚信息爬取完成，共获得 {len(detailed_data)} 条详细记录")
        return detailed_data

    def get_punishment_list_smart_by_year(self, category: str, target_year: int, max_pages: int = 50) -> List[Dict]:
        """智能获取指定年份的处罚信息列表"""
        url = BASE_URLS.get(category)
        if not url:
            self.logger.error(f"未找到类别 '{category}' 对应的URL")
            return []
        
        if not self.load_page_with_retry(url):
            self.logger.error(f"无法加载 {category} 页面")
            return []
        
        all_punishment_list = []
        current_page = 1
        found_target_year = False
        previous_page_latest_date = None
        
        self.logger.info(f"启用智能年份检查: {target_year}年")
        target_year_str = str(target_year)
        
        try:
            while current_page <= max_pages:
                self.logger.info(f"正在解析 {category} 第 {current_page} 页")
                
                # 等待页面加载完成
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)
                
                # 智能检查：获取当前页面的发布时间
                publish_dates = self.get_page_publish_dates()
                current_page_latest_date = publish_dates[0] if publish_dates else None
                
                # 检查是否包含目标年份
                page_has_target_year = any(date.startswith(target_year_str) for date in publish_dates)
                
                if page_has_target_year:
                    found_target_year = True
                    self.logger.info(f"第 {current_page} 页包含目标年份 {target_year} 数据，继续爬取")
                else:
                    # 没有目标年份数据的处理逻辑
                    if found_target_year:
                        # 之前找到过目标年份，现在没有了，说明已经超过目标年份范围
                        self.logger.info(f"第 {current_page} 页不再包含目标年份数据，目标年份范围已结束，停止爬取")
                        break
                    elif current_page == 1:
                        # 第1页没有目标年份数据
                        if current_page_latest_date and current_page_latest_date > target_year_str:
                            self.logger.info(f"第1页最新数据({current_page_latest_date})比目标年份({target_year})新，该分类无目标年份数据")
                            break
                        else:
                            self.logger.info(f"第1页暂无目标年份数据，检查第2页确认")
                    elif current_page == 2:
                        # 第2页的安全检查
                        if (previous_page_latest_date and current_page_latest_date and 
                            current_page_latest_date < previous_page_latest_date):
                            # 检查是否数据过老（比目标年份小很多）
                            if current_page_latest_date and current_page_latest_date < target_year_str:
                                self.logger.info(f"第2页数据({current_page_latest_date})比目标年份({target_year})更老且无目标年份，停止翻页")
                                break
                            else:
                                self.logger.info(f"第2页数据({current_page_latest_date})比第1页({previous_page_latest_date})更老但年份接近，继续查找")
                        else:
                            self.logger.info(f"第2页暂无目标年份数据，继续查找")
                    else:
                        # 第3页及以后，如果还没找到目标年份就停止
                        if current_page_latest_date and current_page_latest_date < target_year_str:
                            self.logger.info(f"第{current_page}页数据({current_page_latest_date})比目标年份({target_year})更老，停止查找")
                            break
                        else:
                            self.logger.info(f"第{current_page}页仍无目标年份数据，继续查找")
                    
                    # 记录当前页最新日期，用于下一页比较
                    previous_page_latest_date = current_page_latest_date
                    
                    # 没有目标年份数据，翻到下一页继续检查
                    if current_page < max_pages:
                        try:
                            next_buttons = self.driver.find_elements(
                                By.XPATH, 
                                '//span[text()="下一页"] | //a[text()="下一页"] | //a[contains(text(), "下一页")]'
                            )
                            
                            if next_buttons:
                                next_button = next_buttons[0]
                                if next_button.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    current_page += 1
                                    time.sleep(3)
                                    continue
                                else:
                                    self.logger.info("已到达最后一页")
                                    break
                            else:
                                self.logger.info("未找到下一页按钮")
                                break
                        except Exception as e:
                            self.logger.warning(f"翻页失败: {e}")
                            break
                    else:
                        break
                
                # 解析当前页面的处罚信息
                try:
                    # 查找包含"行政处罚信息公开表"的链接
                    punishment_links = self.driver.find_elements(
                        By.XPATH, 
                        '//a[contains(text(), "行政处罚信息公示") or contains(text(), "行政处罚信息公开") or contains(text(), "处罚信息")]'
                    )
                    
                    if not punishment_links:
                        # 尝试其他可能的链接模式
                        punishment_links = self.driver.find_elements(
                            By.XPATH, 
                            '//a[contains(@href, "ItemDetail")]'
                        )
                    
                    page_punishment_list = []
                    for link in punishment_links:
                        try:
                            href = link.get_attribute('href')
                            title = clean_text(link.text)
                            
                            if href and title:
                                # 构建完整URL
                                if not href.startswith('http'):
                                    href = urllib.parse.urljoin('https://www.nfra.gov.cn', href)
                                
                                punishment_info = {
                                    'title': title,
                                    'detail_url': href,
                                    'category': category,
                                    'page': current_page
                                }
                                page_punishment_list.append(punishment_info)
                                
                        except Exception as e:
                            self.logger.warning(f"解析链接失败: {e}")
                            continue
                    
                    self.logger.info(f"第 {current_page} 页找到 {len(page_punishment_list)} 条处罚信息")
                    all_punishment_list.extend(page_punishment_list)
                    
                    # 检查是否有下一页
                    if current_page < max_pages:
                        try:
                            # 查找下一页按钮
                            next_buttons = self.driver.find_elements(
                                By.XPATH, 
                                '//span[text()="下一页"] | //a[text()="下一页"] | //a[contains(text(), "下一页")]'
                            )
                            
                            if next_buttons:
                                next_button = next_buttons[0]
                                # 检查按钮是否可点击
                                if next_button.is_enabled():
                                    self.driver.execute_script("arguments[0].click();", next_button)
                                    current_page += 1
                                    time.sleep(3)  # 等待页面跳转
                                else:
                                    self.logger.info("已到达最后一页")
                                    break
                            else:
                                self.logger.info("未找到下一页按钮，可能已到达最后一页")
                                break
                                
                        except Exception as e:
                            self.logger.warning(f"翻页失败: {e}")
                            break
                    else:
                        break
                        
                except Exception as e:
                    self.logger.error(f"解析第 {current_page} 页失败: {e}")
                    break
            
            # 智能检查结果反馈
            if not found_target_year:
                self.logger.info(f"{category} 智能检查完成，未找到 {target_year}年 的数据")
            
            self.logger.info(f"{category} 处罚列表解析完成，共找到 {len(all_punishment_list)} 条记录")
            return all_punishment_list
            
        except Exception as e:
            self.logger.error(f"解析 {category} 处罚列表失败: {e}")
            return all_punishment_list

    def crawl_all_smart_by_date(self, target_year: int, target_month: int, target_day: int, max_pages_per_category: int = 3, max_records_per_category: int = None) -> Dict[str, List[Dict]]:
        """智能爬取指定日期的所有处罚信息 - 支持按日期过滤"""
        if not self.setup_driver():
            self.logger.error("无法初始化WebDriver，爬取失败")
            return {}
        
        all_data = {}
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"
        
        self.logger.info(f"启用智能日期爬取模式，目标日期: {target_date_str}")
        
        try:
            for category in BASE_URLS.keys():
                self.logger.info(f"开始智能爬取 {category} - {target_date_str}数据")
                
                # 使用智能方法爬取指定日期
                category_data = self.crawl_category_smart_by_date(
                    category, 
                    target_year, 
                    target_month, 
                    target_day,
                    max_pages_per_category, 
                    max_records_per_category
                )
                
                all_data[category] = category_data
                
                # 记录这个分类的结果
                if category_data:
                    self.logger.info(f"{category} 完成，获得 {len(category_data)} 条{target_date_str}记录")
                else:
                    self.logger.info(f"{category} 完成，未找到{target_date_str}的数据")
                
                # 类别间延迟
                time.sleep(CRAWL_CONFIG['delay_between_requests'] * 2)
            
            # 统计总结果
            total_records = sum(len(records) for records in all_data.values())
            self.logger.info(f"智能日期爬取完成，{target_date_str}共获得 {total_records} 条记录")
            
        except Exception as e:
            self.logger.error(f"智能日期爬取过程中发生错误: {e}")
        finally:
            self.close_driver()
        
        return all_data

    def crawl_category_smart_by_date(self, category: str, target_year: int, target_month: int, target_day: int, max_pages: int = 3, max_records: int = None) -> List[Dict]:
        """智能爬取指定类别指定日期的处罚信息"""
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"
        self.logger.info(f"开始智能爬取 {category} {target_date_str}处罚信息")
        
        # 使用智能方法获取处罚列表，按日期过滤
        punishment_list = self.get_punishment_list_smart_by_date(category, target_year, target_month, target_day, max_pages)
        
        if not punishment_list:
            self.logger.warning(f"{category} 没有找到{target_date_str}处罚信息")
            return []
        
        # 如果设置了max_records，限制处理的记录数量
        if max_records and len(punishment_list) > max_records:
            self.logger.info(f"{category} 找到 {len(punishment_list)} 条记录，限制处理前 {max_records} 条（测试模式）")
            punishment_list = punishment_list[:max_records]
        
        # 获取详情信息
        detailed_data = []
        for i, item in enumerate(punishment_list, 1):
            self.logger.info(f"正在处理 {category} 第 {i}/{len(punishment_list)} 条记录")
            
            detail_url = item.get('detail_url')
            if not detail_url:
                self.logger.warning(f"第 {i} 条记录缺少详情链接")
                continue
            
            # 使用新窗口处理方式
            detail_data = self.process_link_with_new_window(detail_url, item.get('title', ''))
            
            if detail_data:
                # 检查是否为多记录批文
                if isinstance(detail_data, dict) and detail_data.get('is_multi_record'):
                    # 多记录情况：展开所有记录
                    records = detail_data.get('records', [])
                    for record in records:
                        # 合并列表信息和详情信息
                        combined_data = {**item, **record}
                        detailed_data.append(combined_data)
                    
                    self.logger.info(f"多记录批文处理完成，展开为{len(records)}条独立记录")
                else:
                    # 单记录情况
                    combined_data = {**item, **detail_data}
                    detailed_data.append(combined_data)
            
            # 请求间隔
            time.sleep(CRAWL_CONFIG['delay_between_requests'])
        
        self.logger.info(f"{category} {target_date_str}处罚信息爬取完成，共获得 {len(detailed_data)} 条详细记录")
        return detailed_data

    def get_punishment_list_smart_by_date(self, category: str, target_year: int, target_month: int, target_day: int, max_pages: int = 3) -> List[Dict]:
        """智能获取指定日期的处罚信息列表"""
        url = BASE_URLS.get(category)
        if not url:
            self.logger.error(f"未找到类别 '{category}' 对应的URL")
            return []
        
        if not self.load_page_with_retry(url):
            self.logger.error(f"无法加载 {category} 页面")
            return []
        
        all_punishment_list = []
        current_page = 1
        found_target_date = False
        target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"
        
        self.logger.info(f"启用智能日期检查: {target_date_str}")
        
        try:
            while current_page <= max_pages:
                self.logger.info(f"正在解析 {category} 第 {current_page} 页")
                
                # 等待页面加载完成
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(2)
                
                # 智能检查：获取当前页面的发布时间
                publish_dates = self.get_page_publish_dates()
                
                # 检查是否包含目标日期
                page_has_target_date = any(date.startswith(target_date_str) for date in publish_dates)
                
                if page_has_target_date:
                    found_target_date = True
                    self.logger.info(f"第 {current_page} 页包含目标日期 {target_date_str} 数据，开始爬取")
                    
                    # 解析当前页面，只获取目标日期的记录
                    try:
                        page_punishment_list = []
                        
                        # 查找包含"行政处罚信息公开表"的链接
                        punishment_links = self.driver.find_elements(
                            By.XPATH, 
                            '//a[contains(text(), "行政处罚信息公示") or contains(text(), "行政处罚信息公开") or contains(text(), "处罚信息")]'
                        )
                        
                        if not punishment_links:
                            # 尝试其他可能的链接模式
                            punishment_links = self.driver.find_elements(
                                By.XPATH, 
                                '//a[contains(@href, "ItemDetail")]'
                            )
                        
                        # 对每个链接检查其对应的发布日期
                        for link in punishment_links:
                            try:
                                href = link.get_attribute('href')
                                title = clean_text(link.text)
                                
                                if href and title:
                                    # 获取该链接对应的发布时间
                                    link_publish_date = self.get_link_publish_date(link)
                                    
                                    # 只处理目标日期的记录
                                    if link_publish_date and link_publish_date.startswith(target_date_str):
                                        # 构建完整URL
                                        if not href.startswith('http'):
                                            href = urllib.parse.urljoin('https://www.nfra.gov.cn', href)
                                        
                                        punishment_info = {
                                            'title': title,
                                            'detail_url': href,
                                            'category': category,
                                            'page': current_page,
                                            'publish_date': link_publish_date
                                        }
                                        page_punishment_list.append(punishment_info)
                                        self.logger.debug(f"找到目标日期记录: {title} ({link_publish_date})")
                                    else:
                                        self.logger.debug(f"跳过非目标日期记录: {title} ({link_publish_date})")
                                        
                            except Exception as e:
                                self.logger.warning(f"解析链接失败: {e}")
                                continue
                        
                        target_date_count = len(page_punishment_list)
                        total_count = len(punishment_links)
                        self.logger.info(f"第 {current_page} 页找到 {target_date_count} 条目标日期记录 (共{total_count}条)")
                        all_punishment_list.extend(page_punishment_list)
                        
                    except Exception as e:
                        self.logger.error(f"解析第 {current_page} 页失败: {e}")
                else:
                    # 没有目标日期数据
                    if found_target_date:
                        # 之前找到过目标日期，现在没有了，说明已经超过目标日期范围
                        self.logger.info(f"第 {current_page} 页不再包含目标日期数据，停止爬取")
                        break
                    elif current_page == 1:
                        # 第1页没有目标日期数据，由于页面是降序排列，后面页面更不可能有
                        self.logger.info(f"第1页暂无目标日期 {target_date_str} 数据，由于页面降序排列，直接跳过该分类")
                        break
                    else:
                        # 理论上不应该到达这里，因为第1页没有数据应该已经break了
                        self.logger.info(f"第 {current_page} 页暂无目标日期 {target_date_str} 数据")
                        break
                
                # 检查是否有下一页并且还需要继续
                if current_page < max_pages:
                    try:
                        next_buttons = self.driver.find_elements(
                            By.XPATH, 
                            '//span[text()="下一页"] | //a[text()="下一页"] | //a[contains(text(), "下一页")]'
                        )
                        
                        if next_buttons:
                            next_button = next_buttons[0]
                            if next_button.is_enabled():
                                self.driver.execute_script("arguments[0].click();", next_button)
                                current_page += 1
                                time.sleep(3)
                                continue
                            else:
                                self.logger.info("已到达最后一页")
                                break
                        else:
                            self.logger.info("未找到下一页按钮")
                            break
                    except Exception as e:
                        self.logger.warning(f"翻页失败: {e}")
                        break
                else:
                    break
            
            # 智能检查结果反馈
            if not found_target_date:
                self.logger.info(f"{category} 智能检查完成，未找到 {target_date_str} 的数据")
            
            self.logger.info(f"{category} 处罚列表解析完成，共找到 {len(all_punishment_list)} 条目标日期记录")
            return all_punishment_list
            
        except Exception as e:
            self.logger.error(f"解析 {category} 处罚列表失败: {e}")
            return all_punishment_list

    def get_link_publish_date(self, link_element) -> str:
        """获取链接对应的发布日期"""
        try:
            # 方法1：查找链接所在行的时间信息
            # 向上查找父元素，寻找包含日期的元素
            parent = link_element
            for _ in range(5):  # 最多向上查找5层
                try:
                    parent = parent.find_element(By.XPATH, "..")
                    # 在父元素中查找包含日期的文本
                    date_elements = parent.find_elements(
                        By.XPATH, 
                        './/*[contains(text(), "2024") or contains(text(), "2025")]'
                    )
                    
                    for date_elem in date_elements:
                        text = clean_text(date_elem.text)
                        # 使用正则表达式匹配日期格式
                        import re
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                        if date_match:
                            found_date = date_match.group(1)
                            self.logger.debug(f"找到链接发布日期: {found_date}")
                            return found_date
                except:
                    continue
            
            # 方法2：查找链接同行的时间信息
            try:
                # 查找同一行的时间元素
                row_element = link_element.find_element(By.XPATH, "./ancestor::tr[1]")
                date_cells = row_element.find_elements(
                    By.XPATH, 
                    './/td[contains(text(), "2024") or contains(text(), "2025")]'
                )
                
                for cell in date_cells:
                    text = clean_text(cell.text)
                    import re
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                    if date_match:
                        found_date = date_match.group(1)
                        self.logger.debug(f"从表格行找到发布日期: {found_date}")
                        return found_date
            except:
                pass
            
            # 方法3：检查链接后面紧邻的文本
            try:
                next_sibling = link_element.find_element(By.XPATH, "./following-sibling::*[1]")
                text = clean_text(next_sibling.text)
                import re
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                if date_match:
                    found_date = date_match.group(1)
                    self.logger.debug(f"从相邻元素找到发布日期: {found_date}")
                    return found_date
            except:
                pass
            
            self.logger.debug("未能获取链接的发布日期")
            return ""
            
        except Exception as e:
            self.logger.warning(f"获取链接发布日期失败: {e}")
            return ""


if __name__ == "__main__":
    crawler = NFRACrawler()
    data = crawler.crawl_all_smart()
    
    # 输出结果统计
    for category, records in data.items():
        print(f"{category}: {len(records)} 条记录") 