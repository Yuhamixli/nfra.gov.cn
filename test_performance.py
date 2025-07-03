#!/usr/bin/env python3
"""
性能测试脚本 - 测试总局机关2025年6月数据
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler import NFRACrawler
from utils import setup_logging

def test_zhongju_june_performance():
    """测试总局机关2025年6月数据的性能"""
    logger = setup_logging()
    
    print("=" * 60)
    print("🚀 性能测试：总局机关2025年6月数据")
    print("=" * 60)
    
    # 记录开始时间
    start_time = time.time()
    
    # 创建爬虫实例（启用无头模式以获得最佳性能）
    crawler = NFRACrawler(headless=True)
    
    try:
        # 设置目标参数
        target_year = 2025
        target_month = 6
        category = "总局机关"
        
        print(f"📊 测试参数:")
        print(f"   - 目标日期: {target_year}年{target_month}月")
        print(f"   - 测试类别: {category}")
        print(f"   - 无头模式: 已启用")
        print(f"   - 智能过滤: 已启用")
        print()
        
        # 初始化WebDriver
        print("🔧 正在初始化WebDriver...")
        setup_start = time.time()
        if not crawler.setup_driver():
            print("❌ WebDriver初始化失败")
            return
        setup_time = time.time() - setup_start
        print(f"✅ WebDriver初始化完成，耗时: {setup_time:.2f}秒")
        print()
        
        # 执行智能爬取
        print("🕷️ 开始智能爬取...")
        crawl_start = time.time()
        
        # 使用智能方法爬取总局机关2025年6月数据
        category_data = crawler.crawl_category_smart(
            category=category,
            target_year=target_year,
            target_month=target_month,
            max_pages=5,  # 限制最大页数
            max_records=10,  # 限制最大记录数（测试模式）
            use_smart_check=True  # 启用智能检查
        )
        
        crawl_time = time.time() - crawl_start
        print(f"✅ 智能爬取完成，耗时: {crawl_time:.2f}秒")
        print()
        
        # 统计结果
        print("📈 测试结果:")
        print(f"   - 找到记录数: {len(category_data)}")
        print(f"   - 爬取耗时: {crawl_time:.2f}秒")
        print(f"   - 初始化耗时: {setup_time:.2f}秒")
        print(f"   - 总耗时: {time.time() - start_time:.2f}秒")
        print()
        
        # 显示找到的记录
        if category_data:
            print("📋 找到的记录:")
            for i, record in enumerate(category_data, 1):
                title = record.get('title', '未知标题')
                publish_date = record.get('publish_date', '未知日期')
                print(f"   {i}. {title[:50]}... ({publish_date})")
        else:
            print("⚠️ 未找到符合条件的记录")
        
        print()
        print("🎯 性能分析:")
        if crawl_time < 120:  # 少于2分钟
            print("   ✅ 性能优秀：爬取速度快于预期")
        elif crawl_time < 180:  # 少于3分钟
            print("   ✅ 性能良好：爬取速度符合预期")
        else:
            print("   ⚠️ 性能一般：可能需要进一步优化")
            
        avg_time_per_record = crawl_time / max(len(category_data), 1)
        print(f"   - 平均每条记录处理时间: {avg_time_per_record:.2f}秒")
        
        return category_data
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # 关闭WebDriver
        if crawler.driver:
            crawler.close_driver()
            print("🔧 WebDriver已关闭")

if __name__ == "__main__":
    test_zhongju_june_performance() 