#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFRA金融监管行政处罚信息爬虫 - 快速启动脚本
支持初始化下载和月度更新
"""

import subprocess
import sys
from datetime import datetime, timedelta

def print_header():
    """打印标题"""
    print("=" * 60)
    print("  国家金融监督管理总局行政处罚信息爬虫")
    print("=" * 60)
    print()

def print_menu():
    """打印菜单"""
    # 计算上个月
    today = datetime.now()
    if today.month == 1:
        last_year, last_month = today.year - 1, 12
    else:
        last_year, last_month = today.year, today.month - 1
    
    # 计算昨天
    yesterday = today - timedelta(days=1)
    
    month_names = {
        1: '1月', 2: '2月', 3: '3月', 4: '4月', 5: '5月', 6: '6月',
        7: '7月', 8: '8月', 9: '9月', 10: '10月', 11: '11月', 12: '12月'
    }
    
    print("请选择运行模式：")
    print()
    print("1. 🚀 初始化模式 - 下载2025年全部数据（耗时较长）")
    print(f"2. 📅 月度更新模式 - 获取{last_year}年{month_names[last_month]}数据")
    print(f"3. 📆 每日更新模式 - 获取{yesterday.strftime('%Y年%m月%d日')}数据")
    print("4. 🧪 测试模式 - 快速测试（每类1页数据）")
    print("5. 📊 查看现有数据")
    print("6. ❌ 退出")
    print()

def run_command(command):
    """运行命令并显示结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败：{e}")
        return False

def show_files():
    """显示现有文件"""
    print("\n📁 当前Excel文件：")
    try:
        import os
        if os.path.exists('excel_output'):
            files = [f for f in os.listdir('excel_output') if f.endswith('.xlsx')]
            if files:
                for f in sorted(files, reverse=True):
                    size = os.path.getsize(f'excel_output/{f}') / 1024
                    print(f"  📄 {f} ({size:.1f} KB)")
            else:
                print("  暂无Excel文件")
        else:
            print("  excel_output 目录不存在")
    except Exception as e:
        print(f"  查看文件失败：{e}")
    print()

def estimate_time(mode):
    """估算运行时间"""
    estimates = {
        'init': '2-4小时（约1000+条记录）',
        'monthly': '10-20分钟（约50-200条记录）',  # 更新为更精确的估算
        'daily': '2-5分钟（约5-20条记录）',  # 每日更新通常数据较少
        'test': '5-10分钟（约30条记录）'
    }
    return estimates.get(mode, '未知')

def main():
    """主函数"""
    print_header()
    
    while True:
        print_menu()
        choice = input("请输入选择 (1-6): ").strip()
        
        if choice == '1':
            # 初始化模式
            print("\n🚀 初始化模式")
            print(f"⏱️  预计耗时：{estimate_time('init')}")
            print("📋 说明：将爬取2025年全部行政处罚信息，创建完整数据库")
            print("⚠️  注意：这将花费较长时间，请确保网络稳定")
            
            confirm = input("\n确认开始初始化？(y/N): ").strip().lower()
            if confirm == 'y':
                print(f"\n开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("正在执行初始化...")
                success = run_command("python main.py init")
                if success:
                    print("✅ 初始化完成！")
                else:
                    print("❌ 初始化失败，请查看错误信息")
            else:
                print("已取消初始化")
                
        elif choice == '2':
            # 月度更新模式
            today = datetime.now()
            if today.month == 1:
                last_year, last_month = today.year - 1, 12
            else:
                last_year, last_month = today.year, today.month - 1
            
            month_names = {
                1: '1月', 2: '2月', 3: '3月', 4: '4月', 5: '5月', 6: '6月',
                7: '7月', 8: '8月', 9: '9月', 10: '10月', 11: '11月', 12: '12月'
            }
            
            print(f"\n📅 月度更新模式")
            print(f"⏱️  预计耗时：{estimate_time('monthly')}")
            print(f"📋 说明：智能获取{last_year}年{month_names[last_month]}发布的行政处罚信息")
            print(f"📅 日期范围：{last_year}-{last_month:02d}-01 至 {last_year}-{last_month:02d}-31")
            print(f"🧠 智能检查：自动分析页面发布时间，跳过无关数据")
            
            print(f"\n开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("正在执行月度更新...")
            success = run_command("python main.py monthly")
            if success:
                print("✅ 月度更新完成！")
            else:
                print("❌ 月度更新失败，请查看错误信息")
                
        elif choice == '3':
            # 每日更新模式
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            print(f"\n📆 每日更新模式")
            print(f"⏱️  预计耗时：{estimate_time('daily')}")
            print(f"📋 说明：获取{yesterday.strftime('%Y年%m月%d日')}发布的行政处罚信息")
            print(f"📅 日期范围：仅{yesterday.strftime('%Y-%m-%d')}发布的数据")
            print(f"🧠 智能检查：自动分析页面发布时间，跳过无关数据")
            
            print(f"\n开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("正在执行每日更新...")
            success = run_command("python main.py daily")
            if success:
                print("✅ 每日更新完成！")
            else:
                print("❌ 每日更新失败，请查看错误信息")
                
        elif choice == '4':
            # 测试模式
            print("\n🧪 测试模式")
            print(f"⏱️  预计耗时：{estimate_time('test')}")
            print("📋 说明：快速测试，每个类别爬取第一页数据")
            
            print(f"\n开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("正在执行测试...")
            success = run_command("python main.py test")
            if success:
                print("✅ 测试完成！")
            else:
                print("❌ 测试失败，请查看错误信息")
                
        elif choice == '5':
            # 查看文件
            show_files()
            
        elif choice == '6':
            # 退出
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请输入 1-6")
        
        print("\n" + "-" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序错误：{e}") 