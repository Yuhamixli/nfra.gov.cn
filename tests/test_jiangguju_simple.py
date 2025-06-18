#!/usr/bin/env python3
"""
简化版监管局本级智能月度更新测试
"""

import logging
from crawler import NFRACrawler

def test_jiangguju_simple():
    """测试监管局本级的智能处理 - 简化版"""
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("=" * 60)
    print("测试监管局本级智能月度更新（简化版）")
    print("=" * 60)
    
    # 直接使用固定目标月份：2025年5月
    target_year = 2025
    target_month = 5
    print(f"目标月份: {target_year}年{target_month}月")
    
    # 创建爬虫实例（显示浏览器）
    crawler = NFRACrawler(headless=False)
    
    print("\n正在初始化WebDriver...")
    if not crawler.setup_driver():
        print("❌ 无法初始化WebDriver")
        return
    else:
        print("✅ WebDriver初始化成功")
    
    try:
        print(f"\n开始测试监管局本级智能爬取...")
        print(f"- 目标: {target_year}年{target_month}月数据")
        print(f"- 最大页数: 3页（测试）")
        print(f"- 最大记录: 3条（测试）")
        
        # 测试监管局本级智能爬取
        category_data = crawler.crawl_category_smart(
            category='监管局本级', 
            target_year=target_year, 
            target_month=target_month, 
            max_pages=3,  # 减少页数以便快速测试
            max_records=3  # 限制记录数
        )
        
        print(f"\n📊 监管局本级智能爬取结果:")
        print(f"   找到记录数: {len(category_data)}")
        
        if category_data:
            print(f"\n📋 记录详情:")
            for i, record in enumerate(category_data, 1):
                print(f"   {i}. 当事人: {record.get('当事人名称', '未知')}")
                print(f"      决定日期: {record.get('作出决定日期', '未知')}")
                print(f"      决定机关: {record.get('作出决定机关', '未知')}")
                print(f"      标题: {record.get('title', '未知')[:50]}...")
                print()
        else:
            print(f"   ⚠️  未找到{target_year}年{target_month}月的记录")
            print("   这可能是正常的，因为:")
            print("   1. 该月份确实没有处罚数据")
            print("   2. 智能检查正确跳过了不相关的页面")
            
        print("✅ 测试完成")
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔄 正在关闭WebDriver...")
        crawler.close_driver()
        print("✅ WebDriver已关闭")

if __name__ == "__main__":
    test_jiangguju_simple() 