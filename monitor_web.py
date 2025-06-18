#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web服务监控脚本
实时监控金融监管总局爬虫Web界面的运行状态
"""

import time
import subprocess
import requests
import psutil
import os
from datetime import datetime

class WebMonitor:
    def __init__(self):
        self.ports = [8501, 8502]  # 监控的端口
        self.process_keywords = ['streamlit', 'python']
        
    def check_ports(self):
        """检查端口监听状态"""
        listening_ports = []
        try:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            
            for port in self.ports:
                port_found = False
                for line in lines:
                    if f':{port}' in line and 'LISTENING' in line:
                        listening_ports.append(port)
                        port_found = True
                        break
                
                if not port_found:
                    for line in lines:
                        if f':{port}' in line and ('ESTABLISHED' in line or 'TIME_WAIT' in line):
                            listening_ports.append(f"{port}(连接中)")
                            break
            
        except Exception as e:
            print(f"❌ 端口检查失败: {e}")
            
        return listening_ports
    
    def check_processes(self):
        """检查相关进程"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
                try:
                    # 检查是否是Python进程且命令行包含streamlit
                    if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        if 'streamlit' in cmdline.lower() or 'web_app' in cmdline.lower():
                            processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline[:80] + '...' if len(cmdline) > 80 else cmdline,
                                'cpu': proc.info['cpu_percent'],
                                'memory': proc.info['memory_info'].rss / 1024 / 1024  # MB
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"❌ 进程检查失败: {e}")
            
        return processes
    
    def check_web_access(self):
        """检查Web界面访问状态"""
        results = {}
        for port in self.ports:
            try:
                url = f"http://localhost:{port}"
                response = requests.get(url, timeout=3)
                results[port] = {
                    'status': 'OK' if response.status_code == 200 else f'HTTP {response.status_code}',
                    'size': len(response.content),
                    'title': self.extract_title(response.text)
                }
            except requests.exceptions.ConnectionError:
                results[port] = {'status': '无法连接', 'size': 0, 'title': ''}
            except requests.exceptions.Timeout:
                results[port] = {'status': '超时', 'size': 0, 'title': ''}
            except Exception as e:
                results[port] = {'status': f'错误: {str(e)[:30]}', 'size': 0, 'title': ''}
        
        return results
    
    def extract_title(self, html):
        """提取页面标题"""
        try:
            start = html.find('<title>') + 7
            end = html.find('</title>')
            if start > 6 and end > start:
                return html[start:end][:50]
        except:
            pass
        return ''
    
    def display_status(self, ports, processes, web_access):
        """显示状态信息"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🔍 金融监管总局爬虫Web界面监控")
        print("=" * 60)
        print(f"⏰ 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 端口监听状态
        print("🌐 端口监听状态:")
        if ports:
            for port in ports:
                print(f"  ✅ 端口 {port} - 正在监听")
        else:
            print("  ❌ 未发现监听端口")
        print()
        
        # 进程状态
        print("🔧 相关进程:")
        if processes:
            for proc in processes:
                print(f"  🟢 PID {proc['pid']}: {proc['name']}")
                print(f"     📝 命令: {proc['cmdline']}")
                print(f"     💾 内存: {proc['memory']:.1f} MB | CPU: {proc['cpu']:.1f}%")
                print()
        else:
            print("  ❌ 未发现相关进程")
        
        # Web访问状态
        print("🌍 Web界面访问:")
        for port, info in web_access.items():
            status_icon = "✅" if info['status'] == 'OK' else "❌"
            print(f"  {status_icon} http://localhost:{port}")
            print(f"     状态: {info['status']}")
            if info['size'] > 0:
                print(f"     大小: {info['size']} bytes")
            if info['title']:
                print(f"     标题: {info['title']}")
            print()
        
        print("=" * 60)
        print("💡 按 Ctrl+C 停止监控")
        
    def run(self):
        """运行监控"""
        print("🚀 启动Web服务监控...")
        
        try:
            while True:
                ports = self.check_ports()
                processes = self.check_processes()
                web_access = self.check_web_access()
                
                self.display_status(ports, processes, web_access)
                
                time.sleep(5)  # 每5秒刷新一次
                
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止")
        except Exception as e:
            print(f"\n❌ 监控出错: {e}")

def main():
    """主函数"""
    monitor = WebMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 