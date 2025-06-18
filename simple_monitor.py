#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Web服务监控脚本
"""

import time
import subprocess
import requests
import os
from datetime import datetime

def check_port_simple(port):
    """简单检查端口是否监听"""
    try:
        result = subprocess.run(
            ['netstat', '-an'], 
            capture_output=True, 
            text=True, 
            shell=True,
            timeout=5
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                return True
        return False
    except Exception as e:
        print(f"端口检查错误: {e}")
        return False

def check_web_simple(port):
    """简单检查Web访问"""
    try:
        url = f"http://localhost:{port}"
        response = requests.get(url, timeout=3)
        return {
            'accessible': True,
            'status_code': response.status_code,
            'size': len(response.content)
        }
    except requests.exceptions.ConnectionError:
        return {'accessible': False, 'error': '连接失败'}
    except requests.exceptions.Timeout:
        return {'accessible': False, 'error': '超时'}
    except Exception as e:
        return {'accessible': False, 'error': str(e)[:50]}

def display_simple_status():
    """显示简化状态"""
    print("\n" + "="*50)
    print(f"🕐 {datetime.now().strftime('%H:%M:%S')} - Web服务状态检查")
    print("="*50)
    
    # 检查常用端口
    ports = [8501, 8502]
    
    for port in ports:
        print(f"\n🔍 检查端口 {port}:")
        
        # 端口监听检查
        listening = check_port_simple(port)
        print(f"  📡 端口监听: {'✅ 是' if listening else '❌ 否'}")
        
        # Web访问检查
        web_status = check_web_simple(port)
        if web_status['accessible']:
            print(f"  🌐 Web访问: ✅ 可访问 (HTTP {web_status['status_code']})")
            print(f"  📄 页面大小: {web_status['size']} bytes")
            print(f"  🔗 访问地址: http://localhost:{port}")
        else:
            print(f"  🌐 Web访问: ❌ {web_status['error']}")

def monitor_once():
    """执行一次监控"""
    try:
        display_simple_status()
        print(f"\n💡 提示: 如需启动Web服务，运行: python start_web.py")
        print("="*50)
        return True
    except Exception as e:
        print(f"❌ 监控出错: {e}")
        return False

def monitor_continuous():
    """持续监控"""
    print("🚀 启动持续监控模式...")
    print("💡 按 Ctrl+C 停止监控")
    
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            monitor_once()
            time.sleep(10)  # 每10秒刷新
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")

def main():
    """主函数"""
    print("选择监控模式:")
    print("1. 单次检查")
    print("2. 持续监控")
    
    try:
        choice = input("请选择 (1/2): ").strip()
        
        if choice == '1':
            monitor_once()
        elif choice == '2':
            monitor_continuous()
        else:
            print("无效选择，执行单次检查...")
            monitor_once()
            
    except KeyboardInterrupt:
        print("\n👋 已取消")
    except Exception as e:
        print(f"❌ 程序出错: {e}")

if __name__ == "__main__":
    main() 