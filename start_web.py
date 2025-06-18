#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web界面启动脚本
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 启动金融监管总局爬虫Web界面...")
    print("=" * 50)
    
    # 检查是否在正确的目录
    required_files = ['main.py', 'crawler.py', 'config.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 错误：缺少必要文件: {', '.join(missing_files)}")
        print("请确保在项目根目录运行此脚本")
        input("按 Enter 键退出...")
        return
    
    # 检查Streamlit是否安装
    try:
        import streamlit
        print(f"✅ Streamlit 已安装: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit 未安装")
        print("正在安装 Streamlit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # 选择Web界面版本
    print("\n请选择Web界面版本:")
    print("1. 基础版 (web_app.py) - 简单易用")
    print("2. 增强版 (web_enhanced.py) - 功能完整")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == '1':
        web_file = 'web_app.py'
        port = 8501
    elif choice == '2':
        web_file = 'web_enhanced.py'
        port = 8502
    else:
        print("无效选择，使用默认增强版")
        web_file = 'web_enhanced.py'
        port = 8502
    
    # 启动Web界面
    print(f"\n🌐 启动 {web_file}...")
    print(f"📡 端口: {port}")
    print("💡 界面将在浏览器中自动打开")
    print("🛑 按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 启动Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", web_file, "--server.port", str(port)]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Web界面已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按 Enter 键退出...")

if __name__ == "__main__":
    main() 