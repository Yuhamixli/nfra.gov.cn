#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融监管总局行政处罚信息爬虫 - 简化Web界面
集成现有爬虫功能的简化版界面
"""

import streamlit as st
import os
import sys
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
import queue

# 导入现有模块
try:
    from main import run_crawl_by_mode
    from config import RUN_MODES
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    IMPORT_ERROR = str(e)

# 页面配置
st.set_page_config(
    page_title="金融监管总局行政处罚信息爬虫",
    page_icon="🏦",
    layout="wide"
)

# 线程安全的数据结构
thread_data = {
    'logs': [],
    'running': False,
    'completed': False,
    'error': False,
    'start_time': None,
    'end_time': None,
    'mode': None,
    'current_task': '',
    'total_records': 0,
    'lock': threading.Lock()
}

# 初始化会话状态
if 'execution_status' not in st.session_state:
    st.session_state.execution_status = {
        'running': False,
        'completed': False,
        'error': False,
        'logs': [],
        'start_time': None,
        'end_time': None,
        'mode': None,
        'progress': 0,
        'current_task': '',
        'total_records': 0
    }

def update_from_thread_data():
    """从线程数据更新session_state（线程安全）"""
    with thread_data['lock']:
        st.session_state.execution_status.update({
            'running': thread_data['running'],
            'completed': thread_data['completed'],
            'error': thread_data['error'],
            'start_time': thread_data['start_time'],
            'end_time': thread_data['end_time'],
            'mode': thread_data['mode'],
            'current_task': thread_data['current_task'],
            'total_records': thread_data['total_records'],
            'logs': thread_data['logs'][-200:]  # 只保留最新200条
        })

def add_log_to_thread(level, message):
    """线程安全地添加日志到线程数据"""
    log_entry = {
        'time': datetime.now().strftime("%H:%M:%S"),
        'level': level, 
        'message': message
    }
    
    with thread_data['lock']:
        thread_data['logs'].append(log_entry)
        
        # 处理任务状态更新
        try:
            if "正在处理" in message:
                thread_data['current_task'] = message
            elif "智能爬取完成" in message and "共获得" in message:
                # 提取记录数
                import re
                count_match = re.search(r'共获得.*?(\d+).*?条', message)
                if count_match:
                    thread_data['total_records'] = int(count_match.group(1))
        except:
            pass
        
        # 限制日志数量
        if len(thread_data['logs']) > 300:
            thread_data['logs'] = thread_data['logs'][-200:]

class WebLogHandler(logging.Handler):
    """Web界面日志处理器（线程安全版）"""
    
    def emit(self, record):
        try:
            message = record.getMessage()
            add_log_to_thread(record.levelname, message)
        except:
            pass  # 忽略日志错误，避免影响主程序

def show_header():
    """显示页面头部"""
    st.title("🏦 金融监管总局行政处罚信息爬虫")
    st.markdown("### 专业数据采集工具")
    st.markdown("---")

def show_system_status():
    """显示系统状态"""
    with st.expander("🔧 系统状态", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("模块状态")
            if MODULES_LOADED:
                st.success("✅ 核心模块已加载")
            else:
                st.error(f"❌ 模块加载失败: {IMPORT_ERROR}")
        
        with col2:
            st.subheader("环境检查")
            st.write(f"Python: {sys.version.split()[0]}")
            st.write(f"工作目录: {os.path.basename(os.getcwd())}")
            st.write(f"输出目录: {'✅' if os.path.exists('excel_output') else '❌'}")

def show_control_panel():
    """显示控制面板"""
    st.subheader("🎛️ 操作控制")
    
    if not MODULES_LOADED:
        st.error("核心模块未加载，无法执行")
        return
    
    # 模式选择
    mode_options = {
        'init': '🚀 初始化模式 (下载全部数据)',
        'monthly': '📅 月度更新 (最近45天)',
        'daily': '📰 每日更新 (昨天数据)',
        'test': '🧪 测试模式 (功能测试)'
    }
    
    selected_mode = st.selectbox(
        "选择运行模式:",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x]
    )
    
    # 执行按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 开始执行", disabled=st.session_state.execution_status['running']):
            start_execution(selected_mode)
    
    with col2:
        if st.button("🔄 刷新状态"):
            update_from_thread_data()
            st.rerun()

def show_status_display():
    """显示执行状态"""
    st.subheader("📊 执行状态")
    
    # 更新状态
    update_from_thread_data()
    status = st.session_state.execution_status
    
    # 状态指示器
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if status['running']:
            st.markdown("### 🟡 运行中")
        elif status['completed']:
            st.markdown("### 🟢 已完成")
        elif status['error']:
            st.markdown("### 🔴 错误")
        else:
            st.markdown("### ⚪ 就绪")
    
    with col2:
        st.metric("执行模式", status['mode'] or "未选择")
    
    with col3:
        if status['start_time']:
            if status['end_time']:
                duration = status['end_time'] - status['start_time']
                st.metric("执行时长", f"{duration:.1f}秒")
            elif status['running']:
                current_time = time.time()
                duration = current_time - status['start_time']
                st.metric("执行时长", f"{duration:.1f}秒")
        else:
            st.metric("执行时长", "未开始")
    
    with col4:
        st.metric("获取记录", status['total_records'])
    
    # 当前任务
    if status['current_task']:
        st.info(f"🔄 {status['current_task']}")
    
    # 进度条（如果正在运行）
    if status['running']:
        st.progress(0.5)  # 简单的不确定进度条
        st.caption("正在执行中...")

def show_logs():
    """显示执行日志"""
    st.subheader("📋 执行日志")
    
    # 更新日志
    update_from_thread_data()
    logs = st.session_state.execution_status['logs']
    
    if logs:
        # 显示最新的20条日志
        recent_logs = logs[-20:]
        
        for log in recent_logs:
            level_colors = {
                'INFO': '🔵',
                'WARNING': '🟡', 
                'ERROR': '🔴',
                'SUCCESS': '🟢'
            }
            icon = level_colors.get(log['level'], '⚪')
            st.text(f"{icon} [{log['time']}] {log['message']}")
        
        # 下载完整日志
        if len(logs) > 20:
            st.caption(f"显示最新20条，共{len(logs)}条日志")
        
        full_log = '\n'.join([f"[{log['time']}] {log['level']}: {log['message']}" for log in logs])
        st.download_button(
            "📥 下载完整日志",
            data=full_log,
            file_name=f"crawl_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    else:
        st.info("暂无执行日志")

def show_results():
    """显示结果文件"""
    st.subheader("📁 结果文件")
    
    excel_dir = Path("excel_output")
    if excel_dir.exists():
        excel_files = sorted(excel_dir.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if excel_files:
            st.write(f"找到 {len(excel_files)} 个Excel文件：")
            
            for file_path in excel_files[:5]:  # 显示最新5个文件
                file_stat = file_path.stat()
                file_size = file_stat.st_size / 1024 / 1024
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {file_path.name}")
                with col2:
                    st.write(f"{file_size:.1f} MB")
                with col3:
                    st.write(mod_time.strftime('%m-%d %H:%M'))
                
                # 下载按钮
                try:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            "📥 下载",
                            data=f.read(),
                            file_name=file_path.name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_{file_path.name}"
                        )
                except Exception as e:
                    st.error(f"文件读取失败: {e}")
                
                st.markdown("---")
        else:
            st.info("暂无结果文件")
    else:
        st.warning("输出目录不存在")

def start_execution(mode):
    """开始执行爬取"""
    # 重置线程数据
    with thread_data['lock']:
        thread_data.update({
            'running': True,
            'completed': False,
            'error': False,
            'logs': [],
            'start_time': time.time(),
            'end_time': None,
            'mode': mode.upper(),
            'current_task': f'正在启动{mode.upper()}模式...',
            'total_records': 0
        })
    
    add_log_to_thread("INFO", f"开始执行 {mode.upper()} 模式")
    
    def execution_worker():
        """执行工作线程"""
        try:
            # 设置日志处理器
            log_handler = WebLogHandler()
            log_handler.setLevel(logging.INFO)
            
            # 添加到相关的logger
            loggers = [
                logging.getLogger('utils'),
                logging.getLogger('crawler'), 
                logging.getLogger('data_processor'),
                logging.getLogger()
            ]
            
            for logger in loggers:
                logger.addHandler(log_handler)
                logger.setLevel(logging.INFO)
            
            # 执行爬取
            success = run_crawl_by_mode(mode)
            
            # 清理日志处理器
            for logger in loggers:
                logger.removeHandler(log_handler)
            
            # 更新状态
            with thread_data['lock']:
                if success:
                    thread_data.update({
                        'running': False,
                        'completed': True,
                        'end_time': time.time(),
                        'current_task': '执行完成'
                    })
                    add_log_to_thread("SUCCESS", "执行完成")
                else:
                    thread_data.update({
                        'running': False,
                        'error': True,
                        'current_task': '执行失败'
                    })
                    add_log_to_thread("ERROR", "执行失败")
                    
        except Exception as e:
            with thread_data['lock']:
                thread_data.update({
                    'running': False,
                    'error': True,
                    'current_task': f'执行异常: {str(e)}'
                })
            add_log_to_thread("ERROR", f"执行异常: {str(e)}")
    
    # 启动后台线程
    thread = threading.Thread(target=execution_worker)
    thread.daemon = True
    thread.start()

def main():
    """主函数"""
    show_header()
    show_system_status()
    show_control_panel()
    
    st.markdown("---")
    
    # 主要内容区域
    tab1, tab2, tab3 = st.tabs(["📊 执行状态", "📋 执行日志", "📁 结果文件"])
    
    with tab1:
        show_status_display()
        
        # 自动刷新提示（避免阻塞）
        if st.session_state.execution_status['running']:
            st.info("💡 页面每5秒自动刷新状态，或点击上方'刷新状态'按钮手动刷新")
            # 使用前端自动刷新而不是后端sleep
            st.components.v1.html("""
                <script>
                setTimeout(function(){
                    window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollIntoView();
                    window.parent.location.reload();
                }, 5000);
                </script>
            """, height=0)
    
    with tab2:
        show_logs()
    
    with tab3:
        show_results()
    
    # 使用说明
    st.markdown("---")
    st.markdown("### 💡 使用说明")
    st.info("""
    1. 选择合适的运行模式
    2. 点击"开始执行"启动爬取
    3. 在"执行状态"标签页监控进度
    4. 在"结果文件"标签页下载数据
    """)

if __name__ == "__main__":
    main() 