"""
测试指定URL的爬取过程，输出详细日志
"""

import time
import logging
from crawler import NFRACrawler
from utils import setup_logging
import json

def test_specific_url():
    """测试指定URL的爬取过程"""
    
    # 设置详细的日志记录
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_specific_url.log', encoding='utf-8')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # 测试的URL
    test_url = "https://www.nfra.gov.cn/cn/view/pages/ItemDetail.html?docId=1170162&itemId=4113&generaltype=9"
    
    logger.info("=" * 80)
    logger.info(f"开始测试指定URL: {test_url}")
    logger.info("=" * 80)
    
    # 初始化爬虫（非无头模式便于观察）
    crawler = NFRACrawler(headless=False)
    
    try:
        # 初始化WebDriver
        logger.info("正在初始化WebDriver...")
        if not crawler.setup_driver():
            logger.error("WebDriver初始化失败")
            return
        
        logger.info("WebDriver初始化成功")
        
        # 尝试加载页面
        logger.info(f"正在加载页面: {test_url}")
        
        start_time = time.time()
        success = crawler.load_page_with_retry(test_url, max_retries=3)
        load_time = time.time() - start_time
        
        if success:
            logger.info(f"页面加载成功，耗时: {load_time:.2f}秒")
            
            # 获取页面基本信息
            logger.info("=" * 50)
            logger.info("页面基本信息:")
            logger.info("=" * 50)
            
            try:
                page_title = crawler.driver.title
                logger.info(f"页面标题: {page_title}")
                
                current_url = crawler.driver.current_url
                logger.info(f"当前URL: {current_url}")
                
                # 获取页面源码长度
                page_source_length = len(crawler.driver.page_source)
                logger.info(f"页面源码长度: {page_source_length} 字符")
                
            except Exception as e:
                logger.error(f"获取页面基本信息失败: {e}")
            
            # 尝试提取发布时间
            logger.info("=" * 50)
            logger.info("提取发布时间:")
            logger.info("=" * 50)
            
            publish_time = crawler.extract_publish_time()
            if publish_time:
                logger.info(f"发布时间: {publish_time}")
            else:
                logger.warning("未找到发布时间")
            
            # 查找表格元素
            logger.info("=" * 50)
            logger.info("查找表格元素:")
            logger.info("=" * 50)
            
            try:
                from selenium.webdriver.common.by import By
                
                # 查找不同类型的表格
                table_types = [
                    ("MsoTableGrid", By.CLASS_NAME, "MsoTableGrid"),
                    ("MsoNormalTable", By.CLASS_NAME, "MsoNormalTable"),
                    ("普通table", By.TAG_NAME, "table")
                ]
                
                table_found = False
                for table_type, by_type, selector in table_types:
                    try:
                        tables = crawler.driver.find_elements(by_type, selector)
                        if tables:
                            logger.info(f"找到 {len(tables)} 个 {table_type} 表格")
                            table_found = True
                            
                            # 分析第一个表格
                            if tables:
                                first_table = tables[0]
                                table_html = first_table.get_attribute('outerHTML')
                                logger.info(f"第一个表格HTML长度: {len(table_html)} 字符")
                                
                                # 显示表格HTML的前500字符
                                logger.debug(f"表格HTML片段:\n{table_html[:500]}...")
                                
                                break
                    except Exception as e:
                        logger.debug(f"查找 {table_type} 失败: {e}")
                
                if not table_found:
                    logger.warning("未找到任何表格元素")
                    
                    # 尝试查找其他可能包含数据的元素
                    logger.info("尝试查找其他数据容器...")
                    
                    potential_selectors = [
                        ("div包含'处罚'", By.XPATH, "//div[contains(text(), '处罚')]"),
                        ("span包含'处罚'", By.XPATH, "//span[contains(text(), '处罚')]"),
                        ("所有div", By.TAG_NAME, "div"),
                    ]
                    
                    for desc, by_type, selector in potential_selectors:
                        try:
                            elements = crawler.driver.find_elements(by_type, selector)
                            if elements:
                                logger.info(f"找到 {len(elements)} 个 {desc}")
                                if elements and len(elements) < 10:  # 只显示少量元素的内容
                                    for i, elem in enumerate(elements[:3]):
                                        text = elem.text[:100] if elem.text else "无文本"
                                        logger.debug(f"  {desc}[{i}]: {text}...")
                                break
                        except Exception as e:
                            logger.debug(f"查找 {desc} 失败: {e}")
                
            except Exception as e:
                logger.error(f"查找表格元素过程出错: {e}")
            
            # 尝试解析处罚详情
            logger.info("=" * 50)
            logger.info("尝试解析处罚详情:")
            logger.info("=" * 50)
            
            try:
                detail_data = crawler.get_punishment_detail(test_url)
                
                if detail_data:
                    logger.info("成功解析到处罚详情:")
                    logger.info("-" * 30)
                    
                    for key, value in detail_data.items():
                        if isinstance(value, str) and len(value) > 100:
                            logger.info(f"{key}: {value[:100]}...")
                        else:
                            logger.info(f"{key}: {value}")
                    
                    logger.info("-" * 30)
                    logger.info("完整JSON格式:")
                    print(json.dumps(detail_data, ensure_ascii=False, indent=2))
                    
                else:
                    logger.warning("未能解析到处罚详情数据")
                    
            except Exception as e:
                logger.error(f"解析处罚详情失败: {e}")
            
            # 保存页面源码用于调试
            try:
                with open('page_source_debug.html', 'w', encoding='utf-8') as f:
                    f.write(crawler.driver.page_source)
                logger.info("页面源码已保存到 page_source_debug.html")
            except Exception as e:
                logger.warning(f"保存页面源码失败: {e}")
                
        else:
            logger.error(f"页面加载失败，耗时: {load_time:.2f}秒")
            
            # 尝试获取错误信息
            try:
                current_url = crawler.driver.current_url
                logger.info(f"当前所在URL: {current_url}")
                
                page_title = crawler.driver.title
                logger.info(f"当前页面标题: {page_title}")
                
            except Exception as e:
                logger.error(f"获取错误信息失败: {e}")
    
    except Exception as e:
        logger.error(f"测试过程中发生严重错误: {e}")
        import traceback
        logger.error(f"详细错误信息:\n{traceback.format_exc()}")
    
    finally:
        logger.info("=" * 50)
        logger.info("清理资源...")
        logger.info("=" * 50)
        
        try:
            crawler.close_driver()
            logger.info("WebDriver已关闭")
        except Exception as e:
            logger.error(f"关闭WebDriver失败: {e}")
        
        logger.info("测试完成")
        
        # 显示日志文件位置
        import os
        log_file_path = os.path.abspath('test_specific_url.log')
        logger.info(f"详细日志已保存到: {log_file_path}")

if __name__ == "__main__":
    test_specific_url() 