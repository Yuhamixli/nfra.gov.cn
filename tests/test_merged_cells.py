"""
测试合并单元格页面的爬取
"""

import time
import logging
from crawler import NFRACrawler
from utils import setup_logging
import json

def test_merged_cells_url():
    """测试含有合并单元格的URL"""
    
    # 设置详细的日志记录
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_merged_cells.log', encoding='utf-8')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # 测试的URL - 含有合并单元格的页面
    test_url = "https://www.nfra.gov.cn/cn/view/pages/ItemDetail.html?docId=1212085&itemId=4114&generaltype=9"
    
    logger.info("=" * 80)
    logger.info(f"开始测试合并单元格URL: {test_url}")
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
                
            except Exception as e:
                logger.error(f"获取页面基本信息失败: {e}")
            
            # 查找表格元素并分析结构
            logger.info("=" * 50)
            logger.info("分析表格结构:")
            logger.info("=" * 50)
            
            try:
                from selenium.webdriver.common.by import By
                
                # 查找所有表格
                tables = crawler.driver.find_elements(By.TAG_NAME, "table")
                logger.info(f"找到 {len(tables)} 个表格")
                
                for i, table in enumerate(tables):
                    logger.info(f"\n--- 表格 {i+1} ---")
                    
                    # 获取表格HTML
                    table_html = table.get_attribute('outerHTML')
                    logger.info(f"表格HTML长度: {len(table_html)} 字符")
                    
                    # 分析表格行
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    logger.info(f"表格有 {len(rows)} 行")
                    
                    for j, row in enumerate(rows):
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if not cells:  # 如果没有td，尝试th
                            cells = row.find_elements(By.TAG_NAME, "th")
                        
                        logger.info(f"第 {j+1} 行有 {len(cells)} 个单元格")
                        
                        # 检查每个单元格的属性
                        for k, cell in enumerate(cells):
                            rowspan = cell.get_attribute('rowspan')
                            colspan = cell.get_attribute('colspan')
                            text = cell.text.strip()
                            
                            span_info = ""
                            if rowspan and rowspan != "1":
                                span_info += f" rowspan={rowspan}"
                            if colspan and colspan != "1":
                                span_info += f" colspan={colspan}"
                            
                            logger.info(f"  单元格 {k+1}: '{text[:50]}...'{span_info}")
                    
                    # 显示表格HTML的前1000字符
                    logger.info(f"\n表格HTML片段:\n{table_html[:1000]}...")
                    
                    if i == 0:  # 只详细分析第一个表格
                        break
                
            except Exception as e:
                logger.error(f"分析表格结构失败: {e}")
            
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
                    
                    # 保存JSON结果
                    with open('merged_cells_result.json', 'w', encoding='utf-8') as f:
                        json.dump(detail_data, f, ensure_ascii=False, indent=2)
                    logger.info("处罚详情已保存到 merged_cells_result.json")
                    
                else:
                    logger.warning("未能解析到处罚详情数据")
                    
            except Exception as e:
                logger.error(f"解析处罚详情失败: {e}")
            
            # 保存页面源码用于调试
            try:
                with open('merged_cells_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(crawler.driver.page_source)
                logger.info("页面源码已保存到 merged_cells_page_source.html")
            except Exception as e:
                logger.warning(f"保存页面源码失败: {e}")
                
        else:
            logger.error(f"页面加载失败，耗时: {load_time:.2f}秒")
    
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

if __name__ == "__main__":
    test_merged_cells_url() 