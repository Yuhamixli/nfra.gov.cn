#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试daily模式的日期过滤修复
"""

import logging
from datetime import datetime, timedelta
from crawler import NFRACrawler

def test_daily_date_filter():
    """测试daily模式的日期过滤功能"""
    
    # 设置详细日志
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("测试Daily模式日期过滤修复")
    print("=" * 60)
    
    # 测试昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    target_year, target_month, target_day = yesterday.year, yesterday.month, yesterday.day
    target_date_str = f"{target_year}-{target_month:02d}-{target_day:02d}"
    
    print(f"目标日期: {target_date_str}")
    print(f"测试类别: 监管局本级")
    
    # 创建爬虫实例
    crawler = NFRACrawler(headless=False)  # 显示浏览器便于观察
    
    if not crawler.setup_driver():
        print("无法初始化WebDriver")
        return
    
    try:
        print(f"\n开始测试监管局本级 {target_date_str} 数据过滤...")
        
        # 使用修复后的方法
        category_data = crawler.crawl_category_smart_by_date(
            category='监管局本级',
            target_year=target_year,
            target_month=target_month, 
            target_day=target_day,
            max_pages=2,  # 限制2页测试
            max_records=5  # 限制5条记录测试
        )
        
        print(f"\n📊 测试结果:")
        print(f"   找到目标日期记录数: {len(category_data)}")
        
        if category_data:
            print(f"\n📋 记录详情:")
            for i, record in enumerate(category_data, 1):
                print(f"   {i}. 标题: {record.get('title', '未知')[:60]}...")
                print(f"      发布日期: {record.get('publish_date', '未知')}")
                print(f"      详情链接: {record.get('detail_url', '未知')[:60]}...")
                print()
                
            # 验证所有记录都是目标日期
            all_target_date = all(
                record.get('publish_date', '').startswith(target_date_str) 
                for record in category_data
            )
            
            if all_target_date:
                print("✅ 所有记录都是目标日期，过滤功能正常！")
            else:
                print("❌ 发现非目标日期记录，过滤功能存在问题")
                non_target = [
                    record for record in category_data 
                    if not record.get('publish_date', '').startswith(target_date_str)
                ]
                print(f"   非目标日期记录数: {len(non_target)}")
        else:
            print(f"   ⚠️  未找到{target_date_str}的记录")
            print("   这可能是正常的，因为该日期确实没有数据")
            
    except KeyboardInterrupt:
        print("\n🛑 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔄 正在关闭WebDriver...")
        crawler.close_driver()
        print("✅ 测试完成")

if __name__ == "__main__":
    test_daily_date_filter() 