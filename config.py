"""
配置文件 - 金融监管总局行政处罚爬虫
"""

# 基础URL配置
BASE_URLS = {
    '总局机关': 'https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4113&itemUrl=ItemListRightList.html&itemName=%E6%80%BB%E5%B1%80%E6%9C%BA%E5%85%B3&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A',
    '监管局本级': 'https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4114&itemUrl=ItemListRightList.html&itemName=%E7%9B%91%E7%AE%A1%E5%B1%80%E6%9C%AC%E7%BA%A7&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A',
    '监管分局本级': 'https://www.nfra.gov.cn/cn/view/pages/ItemList.html?itemPId=923&itemId=4115&itemUrl=ItemListRightList.html&itemName=%E7%9B%91%E7%AE%A1%E5%88%86%E5%B1%80%E6%9C%AC%E7%BA%A7&itemsubPId=931&itemsubPName=%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A'
}

# 详情页面URL模板
DETAIL_URL_TEMPLATE = 'https://www.nfra.gov.cn/cn/view/pages/ItemDetail.html'

# Selenium配置
SELENIUM_CONFIG = {
    'implicit_wait': 5,  # 减少隐式等待时间从10到5秒
    'page_load_timeout': 20,  # 减少页面加载超时从30到20秒
    'window_size': (1920, 1080),  # 浏览器窗口大小
    'headless': True,  # 启用无头模式，提升性能
}

# WebDriver配置
WEBDRIVER_CONFIG = {
    'local_driver_dir': 'drivers',  # 本地driver存储目录
    'driver_filename': 'chromedriver.exe',  # driver文件名
    'use_local_driver': True,  # 优先使用本地driver
    'auto_download': True,  # 自动下载driver（如果本地不存在）
    'cache_valid_days': 7,  # driver缓存有效期（天）
}

# 爬取配置
CRAWL_CONFIG = {
    'delay_between_requests': 1,  # 减少请求间隔从2到1秒
    'delay_between_pages': 1.5,   # 减少翻页间隔从3到1.5秒
    'delay_between_categories': 2, # 减少分类间隔从5到2秒
    'max_retries': 3,  # 最大重试次数
    'timeout': 15,  # 减少请求超时时间从30到15秒
    'default_max_pages': 5,  # 默认最大页数
    'test_max_pages': 1,     # 测试模式最大页数
    'scheduled_max_pages': 10, # 定时任务最大页数
    'init_max_pages': 50,    # 初始化模式最大页数（获取2025年全部数据）
    'monthly_max_pages': 15, # 月度更新最大页数（获取最近的数据）
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
        'max_records_per_category': None,  # 不限制记录数
        'description': '初始化模式 - 下载2025年全部数据',
        'update_master': True,
        'target_year': 2025
    },
    'monthly': {
        'max_pages_per_category': 15,  # 月度更新最大页数（增加到15页）
        'max_records_per_category': None,
        'description': '月度更新 - 获取上个月发布的数据',
        'update_master': True,
        'target_mode': 'last_month'  # 获取上个月的数据
    },
    'daily': {
        'max_pages_per_category': 3,  # 每日更新最大页数（较少页数）
        'max_records_per_category': None,
        'description': '每日更新 - 获取昨天发布的数据',
        'update_master': True,
        'target_mode': 'yesterday'  # 获取昨天的数据
    },
    'full': {
        'max_pages_per_category': None,  # 不限制页数
        'max_records_per_category': None,
        'description': '完整爬取 - 获取所有数据',
        'update_master': True
    }
}

# 输出文件配置
OUTPUT_CONFIG = {
    'excel_filename': 'excel_output/金融监管总局行政处罚信息.xlsx',
    'text_output_dir': 'text_output',
    'backup_dir': 'backup',
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

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'crawl.log',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,  # 保留5个日志备份
}

# 定时任务配置
SCHEDULE_CONFIG = {
    'update_time': '09:00',  # 每天更新时间
    'check_interval': 1,  # 检查间隔（天）
    'auto_backup': True,  # 自动备份
    'max_pages_scheduled': 10,  # 定时任务最大页数
}

# 数据处理配置
DATA_PROCESSING_CONFIG = {
    'enable_data_cleaning': True,  # 启用数据清理
    'enable_duplicate_check': True,  # 启用重复检查
    'enable_quality_validation': True,  # 启用质量验证
    'standardize_amounts': True,  # 标准化金额格式
    'include_summary_sheet': True,  # 包含汇总表
}

# 网络配置
NETWORK_CONFIG = {
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ],
    'connection_timeout': 30,
    'read_timeout': 30,
} 