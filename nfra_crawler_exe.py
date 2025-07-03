#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFRA金融监管行政处罚信息爬虫 - EXE版本
专为打包成独立可执行文件设计
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# 获取exe程序的根目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe
    APPLICATION_PATH = Path(sys.executable).parent
else:
    # 如果是开发环境
    APPLICATION_PATH = Path(__file__).parent

# 设置工作目录为exe所在目录
os.chdir(APPLICATION_PATH)

# 设置环境变量，让其他模块知道当前是exe模式
os.environ['NFRA_EXE_MODE'] = '1'

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """打印程序标题"""
    clear_screen()
    print("=" * 80)
    print("                  国家金融监督管理总局")
    print("                   行政处罚信息爬虫")
    print("                    v2.3.1 EXE版")
    print("=" * 80)
    print(f"📁 程序目录: {APPLICATION_PATH}")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def print_main_menu():
    """打印主菜单"""
    # 计算上个月和昨天
    today = datetime.now()
    
    # 计算上个月
    if today.month == 1:
        last_month_date = datetime(today.year - 1, 12, 1)
    else:
        last_month_date = datetime(today.year, today.month - 1, 1)
    
    yesterday = today - timedelta(days=1)
    
    # 格式化显示文本
    last_month_text = last_month_date.strftime('%Y年%m月')
    yesterday_text = yesterday.strftime('%Y年%m月%d日')
    
    print("\n🎯 请选择功能:")
    print()
    print("┌─ 数据爬取功能 ─────────────────────────────────────────┐")
    print("│ 1. 🚀 初始化模式     - 下载2025年全部数据 (2-4小时)      │")
    print(f"│ 2. 📅 月度更新模式   - 获取{last_month_text}数据 (10-20分钟)      │")
    print(f"│ 3. 📆 每日更新模式   - 获取{yesterday_text}数据 (2-5分钟)     │")
    print("│ 4. 🧪 测试模式       - 快速测试各功能 (5-10分钟)        │")
    print("└───────────────────────────────────────────────────────┘")
    print()
    print("┌─ 类别选择功能 ─────────────────────────────────────────┐")
    print("│ 5. 🎯 自定义爬取     - 选择特定类别进行爬取             │")
    print("└───────────────────────────────────────────────────────┘")
    print()
    print("┌─ 管理功能 ─────────────────────────────────────────────┐")
    print("│ 6. 📊 查看现有数据   - 显示已生成的文件                 │")
    print("│ 7. 🔧 WebDriver设置  - 管理ChromeDriver                │")
    print("│ 8. 📖 使用帮助       - 查看详细说明                     │")
    print("│ 9. ❌ 退出程序       - 安全退出                         │")
    print("└───────────────────────────────────────────────────────┘")
    print()

def print_category_menu():
    """打印类别选择菜单"""
    print("\n🎯 类别选择:")
    print()
    print("┌─ 可选类别 ─────────────────────────────────────────────┐")
    print("│ 1. 总局机关         - 国家金融监督管理总局机关           │")
    print("│ 2. 监管局本级       - 各地监管局本级                   │")
    print("│ 3. 监管分局本级     - 各地监管分局本级                 │")
    print("│ 4. 全部类别         - 爬取所有类别                     │")
    print("│ 5. 返回主菜单       - 返回上级菜单                     │")
    print("└───────────────────────────────────────────────────────┘")
    print()

def print_mode_menu():
    """打印运行模式菜单"""
    # 计算上个月
    today = datetime.now()
    if today.month == 1:
        last_month_date = datetime(today.year - 1, 12, 1)
    else:
        last_month_date = datetime(today.year, today.month - 1, 1)
    
    last_month_text = last_month_date.strftime('%Y年%m月')
    
    print("\n🎯 运行模式:")
    print()
    print("┌─ 可选模式 ─────────────────────────────────────────────┐")
    print(f"│ 1. 月度更新模式     - 获取{last_month_text}数据                 │")
    print("│ 2. 测试模式         - 快速测试选定类别                 │")
    print("│ 3. 返回上级菜单     - 重新选择类别                     │")
    print("└───────────────────────────────────────────────────────┘")
    print()

def show_files():
    """显示现有文件"""
    print("\n📁 当前数据文件:")
    print("=" * 60)
    
    # 检查Excel文件
    excel_dir = APPLICATION_PATH / 'excel_output'
    if excel_dir.exists():
        excel_files = list(excel_dir.glob('*.xlsx'))
        if excel_files:
            print("📊 Excel文件:")
            for f in sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True):
                size = f.stat().st_size / 1024
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                print(f"  📄 {f.name}")
                print(f"      大小: {size:.1f} KB  |  修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("📊 Excel文件: 暂无文件")
    else:
        print("📊 Excel文件: 目录不存在")
    
    # 检查文本文件
    text_dir = APPLICATION_PATH / 'text_output'
    if text_dir.exists():
        text_files = list(text_dir.glob('*.txt'))
        if text_files:
            print("📝 文本文件:")
            recent_files = sorted(text_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            for f in recent_files:
                size = f.stat().st_size / 1024
                print(f"  📄 {f.name} ({size:.1f} KB)")
            if len(text_files) > 5:
                print(f"  ... 还有 {len(text_files) - 5} 个文件")
        else:
            print("📝 文本文件: 暂无文件")
    else:
        print("📝 文本文件: 目录不存在")
    
    print("=" * 60)

def show_help():
    """显示使用帮助"""
    print("\n📖 使用说明:")
    print("=" * 60)
    print("🎯 功能说明:")
    print("  • 初始化模式    : 首次使用，下载2025年全部数据")
    print("  • 月度更新模式  : 定期获取上个月发布的新数据")
    print("  • 每日更新模式  : 获取昨天发布的最新数据")
    print("  • 测试模式      : 快速测试，验证程序功能")
    print("  • 自定义爬取    : 灵活选择要爬取的类别")
    print()
    print("🎯 类别说明:")
    print("  • 总局机关      : 国家金融监督管理总局机关发布")
    print("  • 监管局本级    : 各地监管局本级发布")
    print("  • 监管分局本级  : 各地监管分局本级发布")
    print()
    print("🎯 输出文件:")
    print("  • Excel文件保存在: excel_output/ 目录")
    print("  • 文本文件保存在: text_output/ 目录")
    print("  • 主总表文件: 金融监管总局行政处罚信息_总表.xlsx")
    print()
    print("🎯 性能提示:")
    print("  • 首次运行建议使用测试模式验证功能")
    print("  • 使用类别选择功能可大幅提升效率")
    print("  • 程序支持断点续传和智能去重")
    print("=" * 60)

def webdriver_menu():
    """WebDriver管理菜单"""
    while True:
        print("\n🔧 WebDriver管理:")
        print("=" * 60)
        print("1. 📊 检查状态     - 查看ChromeDriver状态")
        print("2. ⬇️  下载设置     - 下载并设置ChromeDriver")
        print("3. 🧪 测试功能     - 测试ChromeDriver是否正常")
        print("4. 🗑️  清理重置     - 清理并重新下载")
        print("5. 🔙 返回主菜单   - 返回上级菜单")
        print("=" * 60)
        
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == '1':
            print("\n📊 检查ChromeDriver状态...")
            run_python_script("setup_driver.py status")
        elif choice == '2':
            print("\n⬇️ 下载并设置ChromeDriver...")
            run_python_script("setup_driver.py download")
        elif choice == '3':
            print("\n🧪 测试ChromeDriver功能...")
            run_python_script("setup_driver.py test")
        elif choice == '4':
            print("\n🗑️ 清理并重新下载...")
            run_python_script("setup_driver.py clean")
            print("正在重新下载...")
            run_python_script("setup_driver.py download")
        elif choice == '5':
            break
        else:
            print("❌ 无效选择，请输入 1-5")
        
        input("\n按回车键继续...")

def run_python_script(command):
    """运行Python脚本"""
    try:
        if getattr(sys, 'frozen', False):
            # EXE模式：直接导入和执行模块
            return run_module_directly(command)
        else:
            # 开发环境：使用subprocess
            result = subprocess.run(f"{sys.executable} {command}", shell=True, 
                                   cwd=APPLICATION_PATH, capture_output=False)
            return result.returncode == 0
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def run_module_directly(command):
    """EXE模式下直接执行模块"""
    try:
        # 解析命令
        parts = command.split()
        script_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # 根据脚本名称执行相应的功能
        if script_name == "main.py":
            return run_main_module(args)
        elif script_name == "setup_driver.py":
            return run_setup_driver_module(args)
        else:
            print(f"❌ 未知脚本: {script_name}")
            return False
            
    except Exception as e:
        print(f"❌ 模块执行失败: {e}")
        return False

def run_main_module(args):
    """执行主爬虫模块"""
    try:
        # 设置命令行参数
        original_argv = sys.argv
        sys.argv = ['main.py'] + args
        
        # 导入并执行main模块
        import main
        # 重新加载模块以确保最新状态
        import importlib
        importlib.reload(main)
        
        # 调用main函数
        main.main()
        
        # 恢复原始参数
        sys.argv = original_argv
        return True
        
    except SystemExit as e:
        # 捕获sys.exit()调用
        sys.argv = original_argv
        return e.code == 0
    except Exception as e:
        print(f"❌ 主模块执行失败: {e}")
        sys.argv = original_argv
        return False

def run_setup_driver_module(args):
    """执行WebDriver设置模块"""
    try:
        # 设置命令行参数
        original_argv = sys.argv
        sys.argv = ['setup_driver.py'] + args
        
        # 导入并执行setup_driver模块
        import setup_driver
        # 重新加载模块以确保最新状态
        import importlib
        importlib.reload(setup_driver)
        
        # 调用main函数
        setup_driver.main()
        
        # 恢复原始参数
        sys.argv = original_argv
        return True
        
    except SystemExit as e:
        # 捕获sys.exit()调用
        sys.argv = original_argv
        return e.code == 0
    except Exception as e:
        print(f"❌ WebDriver设置模块执行失败: {e}")
        sys.argv = original_argv
        return False

def estimate_time_and_data(mode, category=None):
    """估算运行时间和数据量"""
    estimates = {
        'init': {'time': '2-4小时', 'data': '约1000+条记录', 'desc': '下载2025年全部数据'},
        'monthly': {'time': '10-20分钟', 'data': '约50-200条记录', 'desc': '获取上个月数据'},
        'daily': {'time': '2-5分钟', 'data': '约5-20条记录', 'desc': '获取昨天数据'},
        'test': {'time': '5-10分钟', 'data': '约30条记录', 'desc': '快速功能测试'}
    }
    
    # 如果指定了类别，调整估算
    if category and category != 'all':
        if category == '总局':
            estimates[mode]['time'] = estimates[mode]['time'].split('-')[0] + '-' + str(int(estimates[mode]['time'].split('-')[1].replace('分钟', '').replace('小时', '')) // 3) + ('分钟' if '分钟' in estimates[mode]['time'] else '小时')
            estimates[mode]['data'] = estimates[mode]['data'].replace('约', '约').replace('+', '').replace('条记录', '').split('-')
            if len(estimates[mode]['data']) == 1:
                estimates[mode]['data'] = f"约{int(estimates[mode]['data'][0]) // 3}条记录"
            else:
                estimates[mode]['data'] = f"约{int(estimates[mode]['data'][0]) // 3}-{int(estimates[mode]['data'][1]) // 3}条记录"
    
    return estimates.get(mode, {'time': '未知', 'data': '未知', 'desc': '未知'})

def custom_crawl():
    """自定义爬取功能"""
    while True:
        print_category_menu()
        choice = input("请选择类别 (1-5): ").strip()
        
        if choice == '5':
            return  # 返回主菜单
        
        # 类别映射
        category_map = {
            '1': '总局',
            '2': '监管局', 
            '3': '监管分局',
            '4': 'all'
        }
        
        if choice not in category_map:
            print("❌ 无效选择，请输入 1-5")
            continue
            
        category = category_map[choice]
        category_name = {
            '总局': '总局机关',
            '监管局': '监管局本级', 
            '监管分局': '监管分局本级',
            'all': '全部类别'
        }[category]
        
        # 选择运行模式
        while True:
            print_mode_menu()
            mode_choice = input("请选择运行模式 (1-3): ").strip()
            
            if mode_choice == '3':
                break  # 返回类别选择
            
            if mode_choice not in ['1', '2']:
                print("❌ 无效选择，请输入 1-3")
                continue
            
            mode = 'monthly' if mode_choice == '1' else 'test'
            mode_name = '月度更新模式' if mode_choice == '1' else '测试模式'
            
            # 显示执行信息
            estimate = estimate_time_and_data(mode, category if category != 'all' else None)
            print(f"\n🎯 执行配置:")
            print(f"📂 选择类别: {category_name}")
            print(f"⚙️ 运行模式: {mode_name}")
            print(f"⏱️ 预计耗时: {estimate['time']}")
            print(f"📊 预计数据: {estimate['data']}")
            print(f"📋 说明: {estimate['desc']}")
            
            confirm = input(f"\n确认执行？(y/N): ").strip().lower()
            if confirm != 'y':
                print("已取消执行")
                continue
                
            # 构建命令
            if category == 'all':
                command = f"main.py {mode}"
            else:
                command = f"main.py {mode} --categories={category}"
            
            print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"正在执行: {mode_name} - {category_name}")
            print("-" * 60)
            
            success = run_python_script(command)
            
            print("-" * 60)
            if success:
                print("✅ 执行完成！")
                print(f"📁 结果文件保存在: {APPLICATION_PATH / 'excel_output'}")
            else:
                print("❌ 执行失败，请查看错误信息")
            
            input("\n按回车键继续...")
            return  # 完成后返回主菜单

def main():
    """主函数"""
    try:
        while True:
            print_header()
            print_main_menu()
            
            choice = input("请输入选择 (1-9): ").strip()
            
            if choice == '1':
                # 初始化模式
                estimate = estimate_time_and_data('init')
                print(f"\n🚀 初始化模式")
                print(f"⏱️ 预计耗时: {estimate['time']}")
                print(f"📊 预计数据: {estimate['data']}")
                print(f"📋 说明: {estimate['desc']}")
                print("⚠️ 注意: 这将花费较长时间，请确保网络稳定")
                
                confirm = input("\n确认开始初始化？(y/N): ").strip().lower()
                if confirm == 'y':
                    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("正在执行初始化...")
                    print("-" * 60)
                    success = run_python_script("main.py init")
                    print("-" * 60)
                    if success:
                        print("✅ 初始化完成！")
                    else:
                        print("❌ 初始化失败，请查看错误信息")
                else:
                    print("已取消初始化")
                    
            elif choice == '2':
                # 月度更新模式
                estimate = estimate_time_and_data('monthly')
                today = datetime.now()
                if today.month == 1:
                    last_year, last_month = today.year - 1, 12
                else:
                    last_year, last_month = today.year, today.month - 1
                
                print(f"\n📅 月度更新模式")
                print(f"⏱️ 预计耗时: {estimate['time']}")
                print(f"📊 预计数据: {estimate['data']}")
                print(f"📅 目标月份: {last_year}年{last_month}月")
                print(f"🧠 智能检查: 自动分析页面发布时间，跳过无关数据")
                
                print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("正在执行月度更新...")
                print("-" * 60)
                success = run_python_script("main.py monthly")
                print("-" * 60)
                if success:
                    print("✅ 月度更新完成！")
                else:
                    print("❌ 月度更新失败，请查看错误信息")
                    
            elif choice == '3':
                # 每日更新模式
                estimate = estimate_time_and_data('daily')
                yesterday = datetime.now() - timedelta(days=1)
                
                print(f"\n📆 每日更新模式")
                print(f"⏱️ 预计耗时: {estimate['time']}")
                print(f"📊 预计数据: {estimate['data']}")
                print(f"📅 目标日期: {yesterday.strftime('%Y年%m月%d日')}")
                print(f"🧠 智能检查: 精确定位目标日期数据")
                
                print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("正在执行每日更新...")
                print("-" * 60)
                success = run_python_script("main.py daily")
                print("-" * 60)
                if success:
                    print("✅ 每日更新完成！")
                else:
                    print("❌ 每日更新失败，请查看错误信息")
                    
            elif choice == '4':
                # 测试模式
                estimate = estimate_time_and_data('test')
                print(f"\n🧪 测试模式")
                print(f"⏱️ 预计耗时: {estimate['time']}")
                print(f"📊 预计数据: {estimate['data']}")
                print(f"📋 说明: 快速测试各功能，每类爬取少量数据")
                
                print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("正在执行测试...")
                print("-" * 60)
                success = run_python_script("main.py test")
                print("-" * 60)
                if success:
                    print("✅ 测试完成！")
                else:
                    print("❌ 测试失败，请查看错误信息")
                    
            elif choice == '5':
                # 自定义爬取
                custom_crawl()
                continue  # 不显示"按回车继续"
                
            elif choice == '6':
                # 查看文件
                show_files()
                
            elif choice == '7':
                # WebDriver设置
                webdriver_menu()
                continue  # 不显示"按回车继续"
                
            elif choice == '8':
                # 使用帮助
                show_help()
                
            elif choice == '9':
                # 退出
                print("\n👋 感谢使用，再见！")
                break
                
            else:
                print("❌ 无效选择，请输入 1-9")
            
            input("\n按回车键继续...")
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main() 