"""
工具函数模块
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from config import LOG_CONFIG, OUTPUT_CONFIG


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOG_CONFIG['filename'], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def ensure_directory(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def backup_file(filename: str) -> bool:
    """备份文件"""
    try:
        backup_folder = OUTPUT_CONFIG['backup_folder']
        ensure_directory(backup_folder)
        
        if os.path.exists(filename):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}.xlsx"
            backup_path = os.path.join(backup_folder, backup_name)
            
            import shutil
            shutil.copy2(filename, backup_path)
            return True
    except Exception as e:
        logging.error(f"备份文件失败: {e}")
        return False


def save_to_excel(data_dict: Dict[str, List[Dict]], filename: str = None) -> bool:
    """保存数据到Excel文件"""
    try:
        if filename is None:
            filename = OUTPUT_CONFIG['excel_filename']
        
        # 备份现有文件
        backup_file(filename)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, data in data_dict.items():
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # 创建空的DataFrame
                    df = pd.DataFrame()
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logging.info(f"数据已保存到: {filename}")
        return True
    except Exception as e:
        logging.error(f"保存Excel文件失败: {e}")
        return False


def load_existing_data(filename: str = None) -> Dict[str, List[Dict]]:
    """加载现有数据"""
    if filename is None:
        filename = OUTPUT_CONFIG['excel_filename']
    
    data_dict = {}
    
    try:
        if os.path.exists(filename):
            for sheet_name in OUTPUT_CONFIG['sheet_names']:
                try:
                    df = pd.read_excel(filename, sheet_name=sheet_name)
                    data_dict[sheet_name] = df.to_dict('records')
                except Exception:
                    data_dict[sheet_name] = []
        else:
            # 文件不存在，初始化空数据
            for sheet_name in OUTPUT_CONFIG['sheet_names']:
                data_dict[sheet_name] = []
    except Exception as e:
        logging.error(f"加载现有数据失败: {e}")
        # 返回空数据结构
        for sheet_name in OUTPUT_CONFIG['sheet_names']:
            data_dict[sheet_name] = []
    
    return data_dict


def format_date(date_str: str) -> str:
    """格式化日期字符串"""
    try:
        if not date_str:
            return ""
        # 尝试解析常见的日期格式
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


def clean_text(text: str) -> str:
    """清理文本内容"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = ' '.join(text.split())
    
    # 移除常见的HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    
    return text.strip()


def get_current_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def merge_data(existing_data: List[Dict], new_data: List[Dict], key_field: str = '序号') -> List[Dict]:
    """合并数据，避免重复"""
    if not existing_data:
        return new_data
    
    if not new_data:
        return existing_data
    
    # 创建现有数据的键值集合
    existing_keys = {item.get(key_field) for item in existing_data if item.get(key_field)}
    
    # 过滤新数据中已存在的项
    filtered_new_data = [
        item for item in new_data 
        if item.get(key_field) not in existing_keys
    ]
    
    # 合并数据
    merged_data = existing_data + filtered_new_data
    
    return merged_data 