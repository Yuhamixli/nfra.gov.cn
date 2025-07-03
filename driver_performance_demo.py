#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromeDriver性能演示脚本
演示本地缓存vs在线下载的性能差异
"""

import time
import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import WEBDRIVER_CONFIG
from crawler import NFRACrawler
from utils import setup_logging

def demo_local_driver():
    """演示本地ChromeDriver的性能"""
    print("=" * 60)
    print("🚀 本地ChromeDriver演示")
    print("=" * 60)
    
    # 检查本地driver是否存在
    local_dir = Path(WEBDRIVER_CONFIG['local_driver_dir'])
    driver_file = WEBDRIVER_CONFIG['driver_filename']
    local_path = local_dir / driver_file
    
    if not local_path.exists():
        print("❌ 本地ChromeDriver不存在！")
        print("请先运行: python setup_driver.py download")
        return
    
    print(f"✅ 本地ChromeDriver: {local_path}")
    print(f"📏 文件大小: {local_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # 测试启动时间
    print("\n⏱️ 测试启动时间...")
    start_time = time.time()
    
    try:
        # 创建爬虫实例（无头模式）
        crawler = NFRACrawler(headless=True)
        
        # 初始化WebDriver
        setup_success = crawler.setup_driver()
        
        if setup_success:
            init_time = time.time() - start_time
            print(f"✅ WebDriver初始化成功！")
            print(f"⚡ 启动时间: {init_time:.2f} 秒")
            
            # 测试访问页面
            print("\n🌐 测试访问页面...")
            page_start = time.time()
            
            test_url = "https://www.google.com"
            crawler.driver.get(test_url)
            title = crawler.driver.title
            
            page_time = time.time() - page_start
            print(f"✅ 页面加载成功: {title}")
            print(f"⚡ 页面加载时间: {page_time:.2f} 秒")
            
            # 关闭driver
            crawler.close_driver()
            
            total_time = time.time() - start_time
            print(f"\n🎯 总耗时: {total_time:.2f} 秒")
            
        else:
            print("❌ WebDriver初始化失败！")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def demo_download_manager():
    """演示webdriver_manager的性能"""
    print("=" * 60)
    print("📥 webdriver_manager演示")
    print("=" * 60)
    
    # 临时禁用本地driver
    from config import WEBDRIVER_CONFIG
    original_setting = WEBDRIVER_CONFIG['use_local_driver']
    WEBDRIVER_CONFIG['use_local_driver'] = False
    
    print("🔧 临时禁用本地driver，强制使用webdriver_manager...")
    
    # 测试启动时间
    print("\n⏱️ 测试启动时间...")
    start_time = time.time()
    
    try:
        # 创建爬虫实例（无头模式）
        crawler = NFRACrawler(headless=True)
        
        # 初始化WebDriver
        setup_success = crawler.setup_driver()
        
        if setup_success:
            init_time = time.time() - start_time
            print(f"✅ WebDriver初始化成功！")
            print(f"⚡ 启动时间: {init_time:.2f} 秒")
            
            # 测试访问页面
            print("\n🌐 测试访问页面...")
            page_start = time.time()
            
            test_url = "https://www.google.com"
            crawler.driver.get(test_url)
            title = crawler.driver.title
            
            page_time = time.time() - page_start
            print(f"✅ 页面加载成功: {title}")
            print(f"⚡ 页面加载时间: {page_time:.2f} 秒")
            
            # 关闭driver
            crawler.close_driver()
            
            total_time = time.time() - start_time
            print(f"\n🎯 总耗时: {total_time:.2f} 秒")
            
        else:
            print("❌ WebDriver初始化失败！")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 恢复原始设置
        WEBDRIVER_CONFIG['use_local_driver'] = original_setting

def compare_performance():
    """性能对比"""
    print("=" * 60)
    print("⚡ 性能对比测试")
    print("=" * 60)
    
    # 检查本地driver是否存在
    local_dir = Path(WEBDRIVER_CONFIG['local_driver_dir'])
    driver_file = WEBDRIVER_CONFIG['driver_filename']
    local_path = local_dir / driver_file
    
    if not local_path.exists():
        print("❌ 本地ChromeDriver不存在！")
        print("请先运行: python setup_driver.py download")
        return
    
    local_times = []
    manager_times = []
    
    # 测试本地driver (3次)
    print("🔵 测试本地ChromeDriver (3次)...")
    for i in range(3):
        print(f"  第{i+1}次测试...")
        start_time = time.time()
        
        try:
            crawler = NFRACrawler(headless=True)
            if crawler.setup_driver():
                crawler.close_driver()
                elapsed = time.time() - start_time
                local_times.append(elapsed)
                print(f"  ✅ 耗时: {elapsed:.2f}秒")
            else:
                print(f"  ❌ 失败")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    # 测试webdriver_manager (3次)
    print("\n🔴 测试webdriver_manager (3次)...")
    original_setting = WEBDRIVER_CONFIG['use_local_driver']
    WEBDRIVER_CONFIG['use_local_driver'] = False
    
    try:
        for i in range(3):
            print(f"  第{i+1}次测试...")
            start_time = time.time()
            
            try:
                crawler = NFRACrawler(headless=True)
                if crawler.setup_driver():
                    crawler.close_driver()
                    elapsed = time.time() - start_time
                    manager_times.append(elapsed)
                    print(f"  ✅ 耗时: {elapsed:.2f}秒")
                else:
                    print(f"  ❌ 失败")
            except Exception as e:
                print(f"  ❌ 错误: {e}")
    finally:
        WEBDRIVER_CONFIG['use_local_driver'] = original_setting
    
    # 计算平均时间
    if local_times and manager_times:
        local_avg = sum(local_times) / len(local_times)
        manager_avg = sum(manager_times) / len(manager_times)
        
        print("\n📊 性能对比结果:")
        print(f"🔵 本地ChromeDriver平均时间: {local_avg:.2f}秒")
        print(f"🔴 webdriver_manager平均时间: {manager_avg:.2f}秒")
        
        if local_avg < manager_avg:
            improvement = ((manager_avg - local_avg) / manager_avg) * 100
            print(f"🚀 本地driver性能提升: {improvement:.1f}%")
        else:
            print("🤔 本次测试中webdriver_manager更快（可能是网络缓存等因素）")

def main():
    """主函数"""
    print("🔧 ChromeDriver性能演示")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'local':
            demo_local_driver()
        elif command == 'manager':
            demo_download_manager()
        elif command == 'compare':
            compare_performance()
        else:
            print(f"❌ 未知命令: {command}")
            print_help()
    else:
        print_help()

def print_help():
    """打印帮助信息"""
    print("""
使用方法:
    python driver_performance_demo.py <command>

命令:
    local      演示本地ChromeDriver性能
    manager    演示webdriver_manager性能
    compare    对比两种方式的性能差异

示例:
    python driver_performance_demo.py local     # 测试本地driver
    python driver_performance_demo.py manager   # 测试在线下载
    python driver_performance_demo.py compare   # 性能对比

说明:
    本脚本用于演示WebDriver初始化优化的效果，
    对比本地缓存driver和在线下载的性能差异。
    """)

if __name__ == "__main__":
    main() 