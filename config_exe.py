# -*- coding: utf-8 -*-
"""
EXE版本专用配置文件
针对打包后的exe程序优化
"""

import os
import sys
from pathlib import Path

# 获取exe程序的根目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe
    BASE_DIR = Path(sys.executable).parent
else:
    # 如果是开发环境
    BASE_DIR = Path(__file__).parent

# 基础URL配置（与标准配置保持一致）
BASE_URLS = {
    '总局机关': 'https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4113&itemUrl=ItemListRightList.html&itemName=%E6%80%BB%E5%B1%80%E6%9C%BA%E5%85%B3&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A',
    '监管局本级': 'https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4114&itemUrl=ItemListRightList.html&itemName=%E7%9B%91%E7%AE%A1%E5%B1%80%E6%9C%AC%E7%BA%A7&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A',
    '监管分局本级': 'https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4115&itemUrl=ItemListRightList.html&itemName=%E7%9B%91%E7%AE%A1%E5%88%86%E5%B1%80%E6%9C%AC%E7%BA%A7&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A'
}

# Selenium配置 - EXE版本使用有头模式
SELENIUM_CONFIG = {
    'implicit_wait': 5,
    'page_load_timeout': 20,
    'window_size': (1920, 1080),
    'headless': False,  # EXE版本使用有头模式，让用户看到浏览器操作
}

# WebDriver配置 - 相对于exe程序目录
WEBDRIVER_CONFIG = {
    'local_driver_dir': str(BASE_DIR / 'drivers'),  # 相对于exe目录
    'driver_filename': 'chromedriver.exe',
    'use_local_driver': True,
    'auto_download': True,
    'cache_valid_days': 7,
}

# 爬取配置
CRAWL_CONFIG = {
    'delay_between_requests': 1,      # 请求间隔（秒）
    'delay_between_pages': 1.5,       # 翻页间隔（秒）
    'delay_between_categories': 2,    # 分类间隔（秒）
    'max_retries': 3,                 # 最大重试次数
    'timeout': 15,                    # 请求超时时间（秒）
    'default_max_pages': 5,           # 默认最大页数
    'test_max_pages': 1,              # 测试模式最大页数
    'scheduled_max_pages': 10,        # 定时任务最大页数
    'init_max_pages': 50,             # 初始化模式最大页数
    'monthly_max_pages': 15,          # 月度更新最大页数
}

# 运行模式配置
RUN_MODES = {
    'test': {
        'max_pages_per_category': 1,
        'max_records_per_category': 5,
        'description': '测试模式 - 每类5条记录',
        'update_master': True
    },
    'init': {
        'max_pages_per_category': 50,
        'max_records_per_category': None,
        'description': '初始化模式 - 下载2025年全部数据',
        'update_master': True,
        'target_year': 2025
    },
    'monthly': {
        'max_pages_per_category': 15,
        'max_records_per_category': None,
        'description': '月度更新 - 获取上个月发布的数据',
        'update_master': True,
        'target_mode': 'last_month'
    },
    'daily': {
        'max_pages_per_category': 3,
        'max_records_per_category': None,
        'description': '每日更新 - 获取昨天发布的数据',
        'update_master': True,
        'target_mode': 'yesterday'
    },
    'full': {
        'max_pages_per_category': None,
        'max_records_per_category': None,
        'description': '完整爬取 - 获取所有数据',
        'update_master': True
    }
}

# 输出配置 - 相对于exe程序目录
OUTPUT_CONFIG = {
    'excel_filename': str(BASE_DIR / 'excel_output' / '金融监管总局行政处罚信息.xlsx'),
    'excel_output_dir': str(BASE_DIR / 'excel_output'),
    'text_output_dir': str(BASE_DIR / 'text_output'),
    'backup_dir': str(BASE_DIR / 'backup'),
    'master_file_name': '金融监管总局行政处罚信息_总表.xlsx',
    'encoding': 'utf-8',
    'field_mapping': {
        '序号': 'sequence_number',
        '标题': 'title',
        '当事人名称': 'entity_name', 
        '主要违法违规行为': 'violation_behavior',
        '行政处罚依据': 'punishment_basis',
        '行政处罚内容': 'punishment_content',
        '行政处罚决定书文号': 'decision_document_number',
        '作出决定机关': 'decision_authority',
        '作出决定日期': 'decision_date',
        '类别': 'category',
        '抓取时间': 'crawl_time',
        '详情链接': 'detail_url'
    }
}

# 日志配置 - 相对于exe程序目录  
LOGGING_CONFIG = {
    'level': 'INFO',
    'filename': str(BASE_DIR / 'logs' / 'nfra_crawler.log'),
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 3,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# 确保输出目录存在
def ensure_directories():
    """确保所有必要的目录存在"""
    dirs = [
        BASE_DIR / 'excel_output',
        BASE_DIR / 'text_output', 
        BASE_DIR / 'logs',
        BASE_DIR / 'drivers'
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)

# 初始化时创建目录
ensure_directories()

# 类别简写映射
CATEGORY_MAPPING = {
    # 中文简写
    '总局': '总局机关',
    '机关': '总局机关',
    '总局机关': '总局机关',
    
    '监管局': '监管局本级',
    '局': '监管局本级',
    '监管局本级': '监管局本级',
    
    '监管分局': '监管分局本级',
    '分局': '监管分局本级',
    '监管分局本级': '监管分局本级',
    
    # 英文简写
    'zhongju': '总局机关',
    'jiguan': '总局机关',
    'headquarters': '总局机关',
    
    'jianguanju': '监管局本级',
    'bureau': '监管局本级',
    'local_bureau': '监管局本级',
    
    'fenju': '监管分局本级',
    'subbranch': '监管分局本级',
    'branch': '监管分局本级',
    
    # 数字简写
    '1': '总局机关',
    '2': '监管局本级', 
    '3': '监管分局本级',
}

def get_category_list():
    """获取所有可用类别列表"""
    return list(BASE_URLS.keys())

def parse_categories(categories_str):
    """解析类别参数字符串"""
    if not categories_str:
        return get_category_list()
    
    categories = []
    for cat in categories_str.split(','):
        cat = cat.strip()
        if cat in CATEGORY_MAPPING:
            mapped_cat = CATEGORY_MAPPING[cat]
            if mapped_cat not in categories:
                categories.append(mapped_cat)
        elif cat in BASE_URLS:
            if cat not in categories:
                categories.append(cat)
    
    return categories if categories else get_category_list()

# EXE版本特殊配置
EXE_CONFIG = {
    'show_browser': True,      # 显示浏览器窗口
    'auto_close_browser': False,  # 不自动关闭浏览器，让用户看到结果
    'pause_on_error': True,    # 错误时暂停，等待用户确认
    'detailed_output': True,   # 详细输出信息
} 