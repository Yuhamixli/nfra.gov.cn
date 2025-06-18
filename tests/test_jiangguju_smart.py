#!/usr/bin/env python3
"""
测试监管局本级的智能月度更新功能
"""

import logging
from datetime import datetime, timedelta
from crawler import NFRACrawler
from main import get_last_month

def test_jiangguju_smart():
    """测试监管局本级的智能处理"""
    
    # 设置日志级别为INFO以便看到详细过程
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("=" * 60)
    print("测试监管局本级智能月度更新")
    print("=" * 60)
    
    # 获取上个月信息
    last_year, last_month = get_last_month()
    print(f"目标月份: {last_year}年{last_month}月")
    
    # 创建爬虫实例（显示浏览器以便观察）
    crawler = NFRACrawler(headless=False)
    
    if not crawler.setup_driver():
        print("无法初始化WebDriver")
        return
    
    try:
        print("\n开始测试监管局本级智能爬取...")
        
        # 测试监管局本级智能爬取
        category_data = crawler.crawl_category_smart(
            category='监管局本级', 
            target_year=last_year, 
            target_month=last_month, 
            max_pages=10,
            max_records=5  # 测试模式，限制5条记录
        )
        
        print(f"\n监管局本级智能爬取结果:")
        print(f"- 找到记录数: {len(category_data)}")
        
        if category_data:
            print("\n前几条记录概览:")
            for i, record in enumerate(category_data[:3], 1):
                print(f"  {i}. 当事人: {record.get('当事人名称', '未知')}")
                print(f"     决定日期: {record.get('作出决定日期', '未知')}")
                print(f"     机关: {record.get('作出决定机关', '未知')}")
                print()
        else:
            print("  未找到符合条件的记录")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        crawler.close_driver()
        print("\n测试完成")

if __name__ == "__main__":
    test_jiangguju_smart() 