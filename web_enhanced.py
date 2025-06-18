#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融监管总局行政处罚信息爬虫 - 增强Web界面
完全集成现有爬虫功能的专业版界面
"""

import streamlit as st
import pandas as pd
import os
import sys
import time
import json
import threading
import queue
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from io import StringIO
import plotly.express as px
import plotly.graph_objects as go

# 导入现有模块
try:
    from main import run_crawl_by_mode
    from utils import setup_logging, load_existing_data
    from config import RUN_MODES
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    IMPORT_ERROR = str(e)

# 页面配置
st.set_page_config(
    page_title="金融监管总局行政处罚信息爬虫",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .mode-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .status-running {
        color: #ff7f0e;
        font-weight: bold;
    }
    .status-completed {
        color: #2ca02c;
        font-weight: bold;
    }
    .status-error {
        color: #d62728;
        font-weight: bold;
    }
    .log-container {
        height: 300px;
        overflow-y: auto;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 全局变量用于线程间通信
if 'thread_data' not in st.session_state:
    st.session_state.thread_data = {
        'status': 'idle',
        'progress': 0,
        'logs': [],
        'total_records': 0,
        'current_task': '',
        'start_time': None,
        'end_time': None,
        'results': None
    }

def init_session_state():
    """初始化会话状态"""
    defaults = {
        'crawl_status': 'idle',
        'crawl_mode': None,
        'crawl_progress': 0,
        'crawl_logs': [],
        'crawl_thread': None,
        'results_queue': queue.Queue(),
        'start_time': None,
        'end_time': None,
        'total_records': 0,
        'message_queue': queue.Queue(),
        'log_file_path': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_header():
    """显示页面头部"""
    st.markdown('<h1 class="main-header">🏦 金融监管总局行政处罚信息爬虫</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🌐 专业数据采集 · 智能分析 · 可视化展示")
    
    st.markdown("---")

def show_system_check():
    """显示系统检查"""
    with st.expander("🔧 系统状态检查", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**模块加载状态:**")
            if MODULES_LOADED:
                st.success("✅ 所有核心模块已加载")
            else:
                st.error(f"❌ 模块加载失败: {IMPORT_ERROR}")
                st.info("💡 请确保在项目根目录运行")
        
        with col2:
            st.markdown("**环境检查:**")
            checks = [
                ("Python版本", sys.version.split()[0]),
                ("工作目录", os.path.basename(os.getcwd())),
                ("Excel输出目录", "✅" if os.path.exists("excel_output") else "❌"),
                ("配置文件", "✅" if os.path.exists("config.py") else "❌")
            ]
            
            for name, status in checks:
                if "✅" in str(status) or "❌" not in str(status):
                    st.success(f"{name}: {status}")
                else:
                    st.error(f"{name}: {status}")

def show_control_panel():
    """显示控制面板"""
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        if not MODULES_LOADED:
            st.error("⚠️ 核心模块未加载，功能受限")
            return
        
        # 模式选择
        mode_info = {
            'init': {
                'name': '🚀 初始化模式',
                'desc': '下载2025年全部数据',
                'time': '2-4小时',
                'records': '~1000条'
            },
            'monthly': {
                'name': '📅 月度更新',
                'desc': '获取最近45天新数据',
                'time': '20-40分钟',
                'records': '~100条'
            },
            'daily': {
                'name': '📰 每日更新',
                'desc': '获取昨天发布数据',
                'time': '2-5分钟',
                'records': '~20条'
            },
            'test': {
                'name': '🧪 测试模式',
                'desc': '快速功能测试',
                'time': '5-10分钟',
                'records': '~30条'
            }
        }
        
        selected_mode = st.selectbox(
            "选择运行模式:",
            options=list(mode_info.keys()),
            format_func=lambda x: mode_info[x]['name'],
            help="选择合适的运行模式"
        )
        
        # 显示模式详情
        info = mode_info[selected_mode]
        st.markdown(f"""
        <div class="mode-card">
            <h4>{info['name']}</h4>
            <p>📝 {info['desc']}</p>
            <p>⏱️ 预计时间: {info['time']}</p>
            <p>📊 预计记录: {info['records']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 控制按钮
        is_running = st.session_state.thread_data['status'] == 'running'
        
        if st.button(
            "🚀 开始执行" if not is_running else "⏳ 执行中...",
            disabled=is_running,
            use_container_width=True
        ):
            start_crawl(selected_mode)
        
        if is_running and st.button("⏹️ 停止执行", use_container_width=True):
            stop_crawl()
        
        # 快速操作
        st.markdown("---")
        st.subheader("⚡ 快速操作")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄", help="刷新状态"):
                st.rerun()
        with col2:
            if st.button("📁", help="打开输出目录"):
                try:
                    os.startfile("excel_output")
                except:
                    st.info("请手动打开 excel_output 目录")

def show_status_dashboard():
    """显示状态仪表板"""
    st.subheader("📊 运行状态")
    
    col1, col2, col3, col4 = st.columns(4)
    
    thread_data = st.session_state.thread_data
    
    with col1:
        status_colors = {
            'idle': ('⚪', '就绪'),
            'running': ('🟡', '运行中'),
            'completed': ('🟢', '已完成'),
            'error': ('🔴', '错误')
        }
        icon, text = status_colors[thread_data['status']]
        st.markdown(f"### {icon} {text}")
        st.caption("当前状态")
    
    with col2:
        if thread_data['status'] == 'running':
            progress = thread_data['progress']
            st.metric("执行进度", f"{progress}%")
            st.progress(progress / 100.0)
        else:
            st.metric("执行进度", "待开始")
    
    with col3:
        if thread_data['start_time']:
            if thread_data['end_time']:
                duration = thread_data['end_time'] - thread_data['start_time']
                st.metric("执行时长", f"{duration:.1f}秒")
            else:
                current_duration = time.time() - thread_data['start_time']
                st.metric("执行时长", f"{current_duration:.1f}秒")
        else:
            st.metric("执行时长", "未开始")
    
    with col4:
        st.metric("获取记录", thread_data['total_records'])
    
    # 显示当前任务
    if thread_data['current_task']:
        st.info(f"🔄 {thread_data['current_task']}")

def show_main_tabs():
    """显示主要标签页"""
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 实时监控", "📋 执行日志", "📁 数据文件", "📈 统计分析"])
    
    with tab1:
        show_monitoring_tab()
    
    with tab2:
        show_logs_tab()
    
    with tab3:
        show_files_tab()
    
    with tab4:
        show_analytics_tab()

def show_monitoring_tab():
    """监控标签页"""
    thread_data = st.session_state.thread_data
    
    if thread_data['status'] == 'running':
        st.info("🔄 实时监控运行中...")
        
        # 进度显示
        if thread_data['progress'] > 0:
            st.progress(thread_data['progress'] / 100.0)
            st.text(f"进度: {thread_data['progress']}%")
        
        # 当前任务
        if thread_data['current_task']:
            st.markdown(f"### 📝 当前任务")
            st.code(thread_data['current_task'])
        
        # 最新日志
        if thread_data['logs']:
            st.markdown("### 📝 最新日志")
            recent_logs = thread_data['logs'][-10:]  # 显示最新10条
            
            log_container = st.container()
            with log_container:
                for log in recent_logs:
                    if isinstance(log, dict):
                        timestamp = log.get('time', '')
                        message = log.get('message', str(log))
                        st.code(f"[{timestamp}] {message}")
                    else:
                        st.code(str(log))
        
        # 自动刷新
        time.sleep(2)
        st.rerun()
        
    else:
        st.info("🎯 选择模式并开始执行，这里将显示实时进度")
        
        # 显示当前配置
        if MODULES_LOADED:
            st.markdown("### ⚙️ 当前配置")
            try:
                for mode, config in RUN_MODES.items():
                    with st.expander(f"{mode.upper()} 模式配置"):
                        st.json(config)
            except:
                st.warning("无法加载配置信息")

def show_logs_tab():
    """日志标签页"""
    thread_data = st.session_state.thread_data
    
    if thread_data['logs']:
        st.markdown("### 📋 执行日志")
        
        # 显示日志
        log_text = '\n'.join([
            f"[{log.get('time', '')}] {log.get('message', str(log))}" 
            if isinstance(log, dict) else str(log)
            for log in thread_data['logs']
        ])
        
        st.code(log_text, language="text")
        
        # 下载日志
        if st.download_button(
            "📥 下载日志",
            data=log_text,
            file_name=f"crawl_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        ):
            st.success("日志文件已准备下载")
    else:
        st.info("📌 暂无执行日志")
        
        # 显示历史日志文件
        if os.path.exists("crawl.log"):
            st.markdown("### 📄 历史日志文件")
            if st.button("查看 crawl.log"):
                try:
                    with open("crawl.log", "r", encoding="utf-8") as f:
                        content = f.read()
                        # 只显示最后1000行
                        lines = content.split('\n')
                        if len(lines) > 1000:
                            content = '\n'.join(lines[-1000:])
                        st.code(content, language="text")
                except Exception as e:
                    st.error(f"读取日志文件失败: {e}")

def show_files_tab():
    """文件标签页"""
    excel_dir = Path("excel_output")
    
    if excel_dir.exists():
        excel_files = sorted(excel_dir.glob("*.xlsx"), 
                           key=lambda x: x.stat().st_mtime, reverse=True)
        
        if excel_files:
            st.markdown("### 📊 数据文件")
            
            for i, file_path in enumerate(excel_files[:10]):
                with st.expander(f"📄 {file_path.name}", expanded=(i==0)):
                    file_stat = file_path.stat()
                    file_size = file_stat.st_size / 1024 / 1024
                    mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("文件大小", f"{file_size:.1f} MB")
                    with col2:
                        st.metric("修改时间", mod_time.strftime('%m-%d %H:%M'))
                    
                    # 文件预览
                    try:
                        df = pd.read_excel(file_path, nrows=5)
                        st.markdown("**数据预览:**")
                        st.dataframe(df)
                        
                        # 下载按钮
                        with open(file_path, "rb") as f:
                            st.download_button(
                                "📥 下载文件",
                                data=f.read(),
                                file_name=file_path.name,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    except Exception as e:
                        st.error(f"无法预览文件: {e}")
        else:
            st.info("📌 暂无数据文件")
    else:
        st.warning("📂 输出目录不存在")

def show_analytics_tab():
    """统计分析标签页"""
    excel_dir = Path("excel_output")
    
    if excel_dir.exists():
        excel_files = list(excel_dir.glob("*.xlsx"))
        
        if excel_files:
            # 选择文件进行分析
            selected_file = st.selectbox(
                "选择文件进行分析:",
                excel_files,
                format_func=lambda x: x.name
            )
            
            try:
                df = pd.read_excel(selected_file)
                
                # 基础统计
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("总记录数", len(df))
                with col2:
                    if '类别' in df.columns:
                        st.metric("类别数", df['类别'].nunique())
                with col3:
                    if '发布时间' in df.columns:
                        latest = df['发布时间'].max()
                        st.metric("最新日期", str(latest)[:10] if pd.notna(latest) else "N/A")
                with col4:
                    if '当事人名称' in df.columns:
                        st.metric("机构数", df['当事人名称'].nunique())
                
                st.markdown("---")
                
                # 图表分析
                if '类别' in df.columns:
                    st.markdown("### 📊 类别分布")
                    category_counts = df['类别'].value_counts()
                    
                    fig = px.pie(
                        values=category_counts.values,
                        names=category_counts.index,
                        title="处罚类别分布"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 时间趋势
                if '发布时间' in df.columns:
                    st.markdown("### 📈 时间趋势")
                    df['发布日期'] = pd.to_datetime(df['发布时间']).dt.date
                    daily_counts = df['发布日期'].value_counts().sort_index()
                    
                    fig = px.line(
                        x=daily_counts.index,
                        y=daily_counts.values,
                        title="每日发布数量趋势"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # 数据表格
                st.markdown("### 📋 详细数据")
                st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"分析文件时出错: {e}")
        else:
            st.info("📌 暂无数据文件可供分析")
    else:
        st.info("📌 输出目录不存在")

class CrawlLogHandler(logging.Handler):
    """自定义日志处理器，用于捕获爬虫日志"""
    
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def emit(self, record):
        log_entry = {
            'time': datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
            'level': record.levelname,
            'message': record.getMessage()
        }
        self.logs.append(log_entry)
        
        # 更新线程数据
        if 'thread_data' in st.session_state:
            st.session_state.thread_data['logs'].append(log_entry)
            
            # 解析进度信息
            message = record.getMessage()
            
            # 提取当前任务信息
            if "正在处理" in message:
                st.session_state.thread_data['current_task'] = message
            elif "智能爬取完成" in message:
                # 提取记录数
                if "共获得" in message:
                    try:
                        count = re.search(r'共获得.*?(\d+).*?条', message)
                        if count:
                            st.session_state.thread_data['total_records'] = int(count.group(1))
                    except:
                        pass
            
            # 限制日志数量
            if len(st.session_state.thread_data['logs']) > 500:
                st.session_state.thread_data['logs'] = st.session_state.thread_data['logs'][-250:]

def start_crawl(mode):
    """启动爬取任务"""
    if not MODULES_LOADED:
        st.error("核心模块未加载，无法执行")
        return
    
    # 重置线程数据
    st.session_state.thread_data = {
        'status': 'running',
        'progress': 0,
        'logs': [],
        'total_records': 0,
        'current_task': f'正在启动 {mode.upper()} 模式...',
        'start_time': time.time(),
        'end_time': None,
        'results': None
    }
    
    def crawl_worker():
        try:
            # 设置日志处理器
            log_handler = CrawlLogHandler()
            log_handler.setLevel(logging.INFO)
            
            # 获取所有相关的logger
            loggers = [
                logging.getLogger('utils'),
                logging.getLogger('crawler'),
                logging.getLogger('data_processor'),
                logging.getLogger(),  # root logger
            ]
            
            for logger in loggers:
                logger.addHandler(log_handler)
                logger.setLevel(logging.INFO)
            
            # 更新状态
            st.session_state.thread_data['current_task'] = f'开始执行 {mode.upper()} 模式'
            st.session_state.thread_data['progress'] = 10
            
            # 调用真实爬虫
            success = run_crawl_by_mode(mode)
            
            # 清理日志处理器
            for logger in loggers:
                logger.removeHandler(log_handler)
            
            if success:
                st.session_state.thread_data['status'] = 'completed'
                st.session_state.thread_data['progress'] = 100
                st.session_state.thread_data['current_task'] = '执行完成'
                st.session_state.thread_data['end_time'] = time.time()
            else:
                st.session_state.thread_data['status'] = 'error'
                st.session_state.thread_data['current_task'] = '执行失败'
                
        except Exception as e:
            st.session_state.thread_data['status'] = 'error'
            st.session_state.thread_data['current_task'] = f'执行异常: {str(e)}'
            st.session_state.thread_data['logs'].append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'level': 'ERROR',
                'message': f'执行异常: {str(e)}'
            })
    
    # 启动后台线程
    thread = threading.Thread(target=crawl_worker)
    thread.daemon = True
    thread.start()
    st.session_state.crawl_thread = thread

def stop_crawl():
    """停止爬取任务"""
    st.session_state.thread_data['status'] = 'idle'
    st.session_state.thread_data['current_task'] = '用户手动停止'

def main():
    """主函数"""
    init_session_state()
    
    show_header()
    show_system_check()
    
    # 主界面布局
    show_control_panel()
    show_status_dashboard()
    st.markdown("---")
    show_main_tabs()
    
    # 页脚
    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.info("""
    1. **首次使用**: 建议选择测试模式验证环境
    2. **数据建库**: 使用初始化模式获取完整数据
    3. **定期更新**: 使用月度或每日更新保持数据新鲜度
    4. **问题排查**: 查看执行日志了解详细信息
    """)

if __name__ == "__main__":
    main() 