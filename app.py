#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融监管总局行政处罚信息爬虫 - 应用入口
用于打包exe的主入口文件
"""

import sys
import os
import subprocess
import traceback
from pathlib import Path

def show_welcome():
    """显示欢迎界面"""
    print("=" * 60)
    print("        金融监管总局行政处罚信息爬虫")
    print("              v1.0 专业版")
    print("=" * 60)
    print()
    print("功能说明：")
    print("• 初始化模式：下载2025年全部数据（2-4小时）")
    print("• 月度更新：获取最近45天新数据（20-40分钟）") 
    print("• 每日更新：获取昨天发布的新数据（2-5分钟）")
    print("• 测试模式：快速测试（5-10分钟）")
    print()

def show_menu():
    """显示菜单选项"""
    print("请选择运行模式：")
    print("1. 初始化模式 - 下载2025年全部数据")
    print("2. 月度更新 - 获取最近45天新数据")
    print("3. 每日更新 - 获取昨天发布的数据")  
    print("4. 测试模式 - 快速测试")
    print("5. 查看帮助")
    print("0. 退出程序")
    print()

def run_command(mode):
    """执行对应的爬虫命令"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(current_dir, "main.py")
        
        # 检查main.py是否存在
        if not os.path.exists(main_script):
            print(f"❌ 错误：找不到 main.py 文件")
            print(f"   预期路径：{main_script}")
            return False
        
        # 构建命令
        cmd = [sys.executable, main_script, mode]
        print(f"🚀 正在执行：python main.py {mode}")
        print("=" * 50)
        print("开始执行，请稍候...")
        print("💡 提示：程序运行期间请勿关闭此窗口")
        print("=" * 50)
        print()
        
        # 执行命令并等待完成
        result = subprocess.run(cmd, cwd=current_dir)
        
        print()
        print("=" * 50)
        if result.returncode == 0:
            print("✅ 执行成功完成！")
            print("📁 请查看 excel_output 目录获取生成的数据文件")
        else:
            print("❌ 执行过程中出现错误")
            print("📋 请查看上方的错误信息或日志文件")
        print("=" * 50)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 执行失败：{e}")
        traceback.print_exc()
        return False

def show_help():
    """显示帮助信息"""
    print("=" * 60)
    print("                    帮助信息")
    print("=" * 60)
    print()
    print("📖 详细说明：")
    print("• 初始化模式：首次使用时建立完整数据库")
    print("• 月度更新：定期获取最新一个月的数据") 
    print("• 每日更新：获取昨天发布的最新数据")
    print("• 测试模式：快速验证程序功能")
    print()
    print("📁 输出目录：")
    print("• excel_output/ - Excel数据文件")
    print("• text_output/ - 文本数据文件（测试模式）")
    print()
    print("⚠️ 注意事项：")
    print("• 需要稳定的网络连接")
    print("• 需要安装Chrome浏览器") 
    print("• 初始化模式运行时间较长，请耐心等待")
    print()
    print("🔧 故障排除：")
    print("• 如遇网络错误，请重新运行相同模式")
    print("• 如遇WebDriver错误，请确保Chrome已安装")
    print("• 详细文档请查看 README.md")
    print("=" * 60)

def main():
    """主函数"""
    try:
        while True:
            # 清屏（Windows）
            try:
                os.system('cls')
            except:
                pass
                
            show_welcome()
            show_menu()
            
            try:
                choice = input("请输入选择 (0-5): ").strip()
                print()
                
                if choice == '0':
                    print("👋 感谢使用！程序即将退出...")
                    input("按 Enter 键确认退出")
                    break
                    
                elif choice == '1':
                    print("🔄 启动初始化模式...")
                    print("⚠️ 注意：此模式需要2-4小时，请确保网络稳定")
                    confirm = input("是否确认执行？(y/n): ").strip().lower()
                    if confirm in ['y', 'yes', '确认']:
                        success = run_command('init')
                        input("\n按 Enter 键继续...")
                    else:
                        print("❌ 用户取消执行")
                        input("按 Enter 键返回菜单...")
                        
                elif choice == '2':
                    print("🔄 启动月度更新...")
                    success = run_command('monthly')
                    input("\n按 Enter 键继续...")
                    
                elif choice == '3':
                    print("🔄 启动每日更新...")
                    success = run_command('daily')
                    input("\n按 Enter 键继续...")
                    
                elif choice == '4':
                    print("🔄 启动测试模式...")
                    success = run_command('test')
                    input("\n按 Enter 键继续...")
                    
                elif choice == '5':
                    show_help()
                    input("\n按 Enter 键返回菜单...")
                    
                else:
                    print("❌ 无效选择，请输入 0-5")
                    input("按 Enter 键重新选择...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出程序")
                break
            except EOFError:
                print("\n\n👋 程序结束")
                break
                
    except Exception as e:
        print(f"❌ 程序异常：{e}")
        traceback.print_exc()
        input("按 Enter 键退出...")

if __name__ == "__main__":
    main() 