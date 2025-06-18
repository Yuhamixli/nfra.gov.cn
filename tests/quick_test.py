#!/usr/bin/env python3
"""
快速测试脚本 - 验证爬虫功能
"""

import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler import NFRACrawler
from data_processor import process_and_save_data
from utils import setup_logging


def test_environment():
    """测试运行环境"""
    print("🔍 检查运行环境...")
    
    try:
        # 测试导入
        from selenium import webdriver
        from bs4 import BeautifulSoup
        import pandas as pd
        print("✅ 所需库导入成功")
        
        # 测试WebDriver
        crawler = NFRACrawler()
        if crawler.setup_driver():
            print("✅ WebDriver 初始化成功")
            crawler.close_driver()
            return True
        else:
            print("❌ WebDriver 初始化失败")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 环境检查失败: {e}")
        return False


def test_single_page():
    """测试单页爬取"""
    print("\n📄 测试单页爬取...")
    
    try:
        crawler = NFRACrawler()
        
        # 测试爬取总局机关第一页
        category = '总局机关'
        test_data = crawler.crawl_category(category, max_pages=1)
        
        if test_data:
            print(f"✅ 成功爬取 {len(test_data)} 条数据")
            
            # 显示样本数据
            if test_data:
                sample = test_data[0]
                print("\n📝 样本数据:")
                for key, value in sample.items():
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"  {key}: {value}")
            
            return test_data
        else:
            print("❌ 未能获取数据")
            return None
            
    except Exception as e:
        print(f"❌ 爬取测试失败: {e}")
        return None


def test_data_processing(test_data):
    """测试数据处理"""
    print("\n🔄 测试数据处理...")
    
    try:
        if not test_data:
            print("❌ 没有测试数据")
            return False
        
        # 构造测试数据结构
        test_dataset = {
            '总局机关': test_data
        }
        
        # 生成测试文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_filename = f'快速测试_{timestamp}.xlsx'
        
        success = process_and_save_data(
            test_dataset, 
            test_filename, 
            include_text_export=True
        )
        
        if success:
            print(f"✅ 数据处理成功，文件保存为: {test_filename}")
            
            # 检查文件是否存在
            if os.path.exists(test_filename):
                file_size = os.path.getsize(test_filename)
                print(f"📊 文件大小: {file_size} 字节")
            
            return True
        else:
            print("❌ 数据处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据处理测试失败: {e}")
        return False


def test_html_parsing():
    """测试HTML解析"""
    print("\n🔧 测试HTML解析...")
    
    try:
        # 读取示例HTML文件
        html_file = 'assets/element.html'
        if not os.path.exists(html_file):
            print(f"❌ 示例HTML文件不存在: {html_file}")
            return False
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='MsoTableGrid')
        
        if table:
            # 解析表格
            crawler = NFRACrawler()
            data = crawler.parse_table_from_soup(table)
            
            if data:
                print("✅ HTML解析成功")
                print("📝 解析结果:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
                return True
            else:
                print("❌ 解析结果为空")
                return False
        else:
            print("❌ 未找到目标表格")
            return False
            
    except Exception as e:
        print(f"❌ HTML解析测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 金融监管总局爬虫 - 快速测试")
    print("=" * 50)
    
    # 设置日志
    logger = setup_logging()
    
    # 测试步骤
    steps = [
        ("环境检查", test_environment),
        ("HTML解析", test_html_parsing),
        ("单页爬取", test_single_page),
    ]
    
    test_data = None
    all_passed = True
    
    for step_name, test_func in steps:
        print(f"\n🔸 {step_name}")
        try:
            if step_name == "单页爬取":
                result = test_func()
                if result:
                    test_data = result
                    # 测试数据处理
                    print("\n🔸 数据处理")
                    if not test_data_processing(test_data):
                        all_passed = False
                else:
                    all_passed = False
            else:
                if not test_func():
                    all_passed = False
        except Exception as e:
            print(f"❌ {step_name} 异常: {e}")
            all_passed = False
    
    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！爬虫已准备就绪。")
        print("\n📚 接下来可以运行:")
        print("  python main.py run 5      # 爬取5页数据")
        print("  python main.py analysis   # 分析数据")
        print("  python main.py schedule   # 启动定时任务")
    else:
        print("❌ 部分测试失败，请检查配置和依赖。")
        print("\n💡 建议:")
        print("  1. 检查网络连接")
        print("  2. 确保Chrome浏览器已安装")
        print("  3. 运行: pip install -r requirements.txt")
    
    print("\n📋 详细日志请查看: crawl.log")


if __name__ == "__main__":
    main() 