#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融监管总局行政处罚信息爬虫 - 主程序
提供命令行接口，支持测试、正式爬取、数据分析、定时任务等功能
"""

import argparse
import sys
import schedule
import time
from datetime import datetime, timedelta
import logging
from calendar import monthrange

from crawler import NFRACrawler
from data_processor import DataProcessor, process_and_save_data
from utils import setup_logging, load_existing_data, merge_data
from config import SCHEDULE_CONFIG, OUTPUT_CONFIG, SELENIUM_CONFIG, RUN_MODES


def run_crawl_by_mode(mode: str) -> bool:
    """根据模式执行爬取任务"""
    logger = setup_logging()
    
    if mode not in RUN_MODES:
        logger.error(f"不支持的运行模式: {mode}")
        return False
    
    mode_config = RUN_MODES[mode]
    logger.info(f"开始执行 {mode_config['description']}...")
    
    try:
        crawler = NFRACrawler(headless=SELENIUM_CONFIG['headless'])
        
        # 执行爬取
        if mode == 'init':
            # 初始化模式：智能获取2025年的所有数据
            logger.info("初始化模式：智能获取2025年全部行政处罚信息...")
            
            # 使用智能爬取方法，按年份过滤
            filtered_data = crawler.crawl_all_smart_by_year(
                target_year=2025,
                max_pages_per_category=mode_config['max_pages_per_category'],
                max_records_per_category=mode_config['max_records_per_category']
            )
            
            total_records = sum(len(records) for records in filtered_data.values())
            logger.info(f"智能爬取完成，2025年共获得: {total_records} 条")
            
        elif mode == 'monthly':
            # 月度更新模式：智能获取上个月的数据
            last_year, last_month = get_last_month()
            logger.info(f"月度更新模式：智能获取{last_year}年{last_month}月发布的数据...")
            
            # 使用智能爬取方法，直接获取目标月份的数据
            filtered_data = crawler.crawl_all_smart(
                target_year=last_year,
                target_month=last_month,
                max_pages_per_category=mode_config['max_pages_per_category'],
                max_records_per_category=mode_config['max_records_per_category']
            )
            
            total_records = sum(len(records) for records in filtered_data.values())
            logger.info(f"智能爬取完成，{last_year}年{last_month}月共获得: {total_records} 条")
            
        elif mode == 'daily':
            # 每日更新模式：智能获取昨天的数据
            yesterday = datetime.now() - timedelta(days=1)
            target_year, target_month, target_day = yesterday.year, yesterday.month, yesterday.day
            logger.info(f"每日更新模式：智能获取{target_year}年{target_month}月{target_day}日发布的数据...")
            
            # 使用智能爬取方法，获取昨天的数据
            filtered_data = crawler.crawl_all_smart_by_date(
                target_year=target_year,
                target_month=target_month,
                target_day=target_day,
                max_pages_per_category=mode_config['max_pages_per_category'],
                max_records_per_category=mode_config['max_records_per_category']
            )
            
            total_records = sum(len(records) for records in filtered_data.values())
            logger.info(f"智能爬取完成，{target_year}年{target_month}月{target_day}日共获得: {total_records} 条")
            
        else:
            # 其他模式
            data = crawler.crawl_all(
                max_pages_per_category=mode_config['max_pages_per_category'],
                max_records_per_category=mode_config['max_records_per_category']
            )
            filtered_data = data
        
        if filtered_data:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'excel_output/{mode}模式_{timestamp}.xlsx'
            
            # 处理和保存数据
            success = process_and_save_data(
                filtered_data, 
                filename, 
                include_text_export=(mode == 'test')
            )
            
            if success:
                total_records = sum(len(records) for records in filtered_data.values())
                logger.info(f"{mode_config['description']}完成！")
                logger.info(f"获得 {total_records} 条记录，保存至: {filename}")
                
                # 显示分类统计
                for category, records in filtered_data.items():
                    logger.info(f"  {category}: {len(records)} 条")
                
                return True
            else:
                logger.error("数据处理失败")
                return False
        else:
            logger.warning("未获取到数据")
            return False
            
    except Exception as e:
        logger.error(f"{mode_config['description']}失败: {e}")
        return False


def filter_data_by_year(data: dict, target_year: int) -> dict:
    """过滤指定年份的数据"""
    logger = logging.getLogger(__name__)
    filtered_data = {}
    
    for category, records in data.items():
        filtered_records = []
        
        for record in records:
            # 检查发布时间或抓取时间
            publish_time = record.get('发布时间', '')
            crawl_time = record.get('抓取时间', '')
            
            # 尝试从发布时间判断年份
            if publish_time and str(target_year) in str(publish_time):
                filtered_records.append(record)
            # 如果发布时间不明确，检查抓取时间
            elif crawl_time and str(target_year) in str(crawl_time):
                filtered_records.append(record)
            # 如果都没有明确时间，保留记录（避免漏掉）
            elif not publish_time and not crawl_time:
                filtered_records.append(record)
        
        if filtered_records:
            filtered_data[category] = filtered_records
            logger.info(f"{category}: 过滤到 {len(filtered_records)} 条{target_year}年记录")
    
    return filtered_data


def filter_data_by_month(data: dict, target_year: int, target_month: int) -> dict:
    """过滤指定年月的数据"""
    logger = logging.getLogger(__name__)
    filtered_data = {}
    
    # 构建目标月份的日期范围
    # 获取目标月份的第一天和最后一天
    first_day = f"{target_year}-{target_month:02d}-01"
    last_day_num = monthrange(target_year, target_month)[1]
    last_day = f"{target_year}-{target_month:02d}-{last_day_num:02d}"
    
    logger.info(f"过滤 {target_year}年{target_month}月 ({first_day} 至 {last_day}) 的数据")
    
    for category, records in data.items():
        filtered_records = []
        
        for record in records:
            # 检查发布时间
            publish_time = record.get('发布时间', '')
            crawl_time = record.get('抓取时间', '')
            
            # 优先使用发布时间
            time_to_check = publish_time or crawl_time
            
            if time_to_check:
                try:
                    # 尝试解析时间
                    if isinstance(time_to_check, str):
                        # 处理多种时间格式
                        parsed_time = None
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                            try:
                                parsed_time = datetime.strptime(time_to_check, fmt)
                                break
                            except ValueError:
                                continue
                        
                        if parsed_time:
                            # 检查是否在目标月份内
                            if (parsed_time.year == target_year and 
                                parsed_time.month == target_month):
                                filtered_records.append(record)
                        else:
                            # 如果解析失败，尝试字符串匹配
                            month_str = f"{target_year}-{target_month:02d}"
                            if month_str in str(time_to_check):
                                filtered_records.append(record)
                    else:
                        # 如果是datetime对象
                        if (time_to_check.year == target_year and 
                            time_to_check.month == target_month):
                            filtered_records.append(record)
                except Exception as e:
                    logger.debug(f"时间解析失败: {time_to_check}, 错误: {e}")
                    # 解析失败时，尝试字符串匹配作为后备
                    month_str = f"{target_year}-{target_month:02d}"
                    if month_str in str(time_to_check):
                        filtered_records.append(record)
            else:
                # 如果没有时间信息，不包含该记录
                logger.debug("记录缺少时间信息，跳过")
        
        if filtered_records:
            filtered_data[category] = filtered_records
            logger.info(f"{category}: 过滤到 {len(filtered_records)} 条{target_year}年{target_month}月记录")
    
    return filtered_data


def get_last_month() -> tuple:
    """获取上个月的年份和月份"""
    today = datetime.now()
    if today.month == 1:
        return today.year - 1, 12
    else:
        return today.year, today.month - 1


def filter_data_by_days(data: dict, days: int) -> dict:
    """过滤最近N天的数据"""
    logger = logging.getLogger(__name__)
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_data = {}
    
    for category, records in data.items():
        filtered_records = []
        
        for record in records:
            # 检查发布时间
            publish_time = record.get('发布时间', '')
            if publish_time:
                try:
                    # 尝试解析时间
                    if isinstance(publish_time, str):
                        # 处理多种时间格式
                        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                            try:
                                parsed_time = datetime.strptime(publish_time, fmt)
                                if parsed_time >= cutoff_date:
                                    filtered_records.append(record)
                                break
                            except ValueError:
                                continue
                    else:
                        # 如果是datetime对象
                        if publish_time >= cutoff_date:
                            filtered_records.append(record)
                except Exception:
                    # 如果时间解析失败，保留记录（避免漏掉）
                    filtered_records.append(record)
            else:
                # 如果没有发布时间，保留记录
                filtered_records.append(record)
        
        if filtered_records:
            filtered_data[category] = filtered_records
            logger.info(f"{category}: 过滤到 {len(filtered_records)} 条最近{days}天记录")
    
    return filtered_data


def run_test_crawl():
    """执行测试爬取"""
    return run_crawl_by_mode('test')


def run_init_crawl():
    """执行初始化爬取 - 下载2025年全部数据"""
    return run_crawl_by_mode('init')


def run_monthly_update():
    """执行月度更新 - 获取最新数据"""
    return run_crawl_by_mode('monthly')


def run_daily_update():
    """执行每日更新 - 获取昨天发布的数据"""
    return run_crawl_by_mode('daily')


def run_full_crawl():
    """执行完整爬取 - 获取所有数据"""
    return run_crawl_by_mode('full')


def run_scheduled_crawl():
    """运行定时爬取"""
    logger = setup_logging()
    logger.info("启动定时爬取服务")
    logger.info(f"计划执行时间: 每天 {SCHEDULE_CONFIG['update_time']}")
    
    # 设置定时任务
    schedule.every().day.at(SCHEDULE_CONFIG['update_time']).do(
        lambda: run_crawl_by_mode('full')  # 定时任务爬取更多页面
    )
    
    logger.info("定时任务已设置，等待执行...")
    logger.info("按 Ctrl+C 停止服务")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("用户中断，停止定时任务")
    except Exception as e:
        logger.error(f"定时任务执行错误: {e}")


def run_data_analysis():
    """运行数据分析"""
    logger = setup_logging()
    logger.info("开始数据分析...")
    
    try:
        # 加载现有数据
        existing_data = load_existing_data()
        
        if not any(existing_data.values()):
            logger.warning("没有找到现有数据，请先运行爬取任务")
            return False
        
        # 创建数据处理器
        processor = DataProcessor()
        
        # 数据质量分析
        quality_report = processor.validate_data_quality(existing_data)
        
        logger.info("=" * 40)
        logger.info("数据质量分析报告")
        logger.info("=" * 40)
        logger.info(f"总计记录数: {quality_report['total_records']}")
        
        for category, stats in quality_report['categories'].items():
            logger.info(f"\n{category}:")
            logger.info(f"  总记录数: {stats['total']}")
            logger.info(f"  有效记录: {stats['valid_records']}")
            logger.info(f"  缺少当事人: {stats['missing_name']}")
            logger.info(f"  缺少处罚内容: {stats['missing_punishment']}")
            logger.info(f"  缺少决定机关: {stats['missing_authority']}")
        
        if quality_report['issues']:
            logger.info(f"\n发现的问题:")
            for issue in quality_report['issues']:
                logger.info(f"  - {issue}")
        
        # 生成分析报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_filename = f'excel_output/数据分析报告_{timestamp}.xlsx'
        
        success = processor.generate_excel_report(existing_data, analysis_filename)
        
        if success:
            logger.info(f"\n分析报告已生成: {analysis_filename}")
            return True
        else:
            logger.error("生成分析报告失败")
            return False
            
    except Exception as e:
        logger.error(f"数据分析失败: {e}")
        return False


def main():
    """主函数 - 命令行界面"""
    parser = argparse.ArgumentParser(description='金融监管总局行政处罚信息爬虫')
    parser.add_argument('command', 
                       choices=['test', 'init', 'monthly', 'daily', 'run', 'analysis', 'schedule'], 
                       help='执行命令')
    parser.add_argument('--pages', type=int, default=5, help='每个分类爬取的最大页数')
    parser.add_argument('--text', action='store_true', help='同时导出文本文件')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'test':
            print("测试模式（爬取第一页数据）...")
            success = run_test_crawl()
            
        elif args.command == 'init':
            print("初始化模式（下载2025年全部数据）...")
            print("⚠️  注意：此模式将爬取大量数据，可能需要较长时间！")
            confirm = input("确认继续？(y/N): ")
            if confirm.lower() == 'y':
                success = run_init_crawl()
            else:
                print("已取消初始化。")
                return
                
        elif args.command == 'monthly':
            print("月度更新模式（获取最新数据）...")
            success = run_monthly_update()
            
        elif args.command == 'daily':
            print("每日更新模式（获取昨天发布的数据）...")
            success = run_daily_update()
            
        elif args.command == 'run':
            print("完整爬取模式...")
            if args.text:
                print("同时导出文本文件...")
            
            success = run_full_crawl()
            
        elif args.command == 'analysis':
            print("数据分析模式...")
            success = run_data_analysis()
            
        elif args.command == 'schedule':
            print("启动定时任务...")
            run_scheduled_crawl()
            return  # 定时任务不需要success检查
            
        else:
            parser.print_help()
            return
        
        if success:
            print("任务执行成功！")
        else:
            print("任务执行失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        sys.exit(1)


def print_help():
    """打印帮助信息"""
    print("""
金融监管总局行政处罚信息爬虫

使用方法:
    python main.py run [页数] [--text]     执行单次爬取
    python main.py test                    测试模式（爬取第一页）
    python main.py schedule                启动定时爬取服务
    python main.py analysis                分析现有数据
    python main.py env                     检查运行环境

参数说明:
    [页数]        每个分类爬取的页数，默认5页
    --text        同时导出文本文件

示例:
    python main.py run                     爬取5页数据
    python main.py run 10                  爬取10页数据
    python main.py run 3 --text           爬取3页数据并导出文本

说明:
    - 爬取的数据保存到Excel文件中，按分类整理
    - 支持增量更新，避免重复数据
    - 自动备份历史数据
    - 详细日志记录在 crawl.log 文件中
    - 包含数据质量检查和分析功能
    """)


if __name__ == "__main__":
    main() 