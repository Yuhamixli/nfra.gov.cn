"""
测试增强后的表格解析功能
"""

from crawler import NFRACrawler
from utils import setup_logging
import json

def test_enhanced_parsing():
    """测试增强后的解析功能"""
    logger = setup_logging()
    
    # 测试数据 - 使用您提供的HTML片段
    test_html = """
    <div>
    对复星联合健康保险股份有限公司合计罚款158万元。其中，总公司38万元，分支机构120万元。
    对项开宝警告并罚款1万元
    对陈雄斌警告并罚款2万元
    对刘益成警告并罚款1万元
    对尹志军警告并罚款1万元
    对代强警告并罚款1万元
    对潘麟警告并罚款7万元
    对胡峻警告并罚款1万元
    对李正警告并罚款1万元
    对王利钿警告并罚款1万元
    对廖志洪警告并罚款1万元
    对彭裕群警告并罚款1万元
    对吕志坚警告并罚款1万元
    
    根据《保险法》第一百六十一条、第一百七十一条等规定，依据《保险公司管理规定》进行处罚。
    </div>
    """
    
    logger.info("开始测试增强后的解析功能")
    
    crawler = NFRACrawler()
    
    # 测试从文本中提取行政处罚依据
    logger.info("=== 测试行政处罚依据提取 ===")
    basis = crawler.extract_punishment_basis_from_text(test_html)
    logger.info(f"提取到的行政处罚依据: {basis}")
    
    # 测试从文本中提取处罚内容
    logger.info("=== 测试行政处罚内容提取 ===")
    content = crawler.extract_punishment_content_from_text(test_html)
    logger.info(f"提取到的行政处罚内容: {content}")
    
    # 组合结果
    result = {
        '行政处罚依据': basis,
        '行政处罚内容': content
    }
    
    logger.info("=== 最终解析结果 ===")
    print("\n完整的解析结果:")
    print(f"行政处罚依据: {result['行政处罚依据']}")
    print(f"行政处罚内容: {result['行政处罚内容']}")
    print("\nJSON格式:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result

def test_real_page():
    """测试真实页面的解析"""
    logger = setup_logging()
    
    logger.info("开始测试真实页面解析")
    
    crawler = NFRACrawler(headless=False)  # 非无头模式便于观察
    
    if not crawler.setup_driver():
        logger.error("无法初始化WebDriver")
        return
    
    try:
        # 测试一个具体的处罚信息页面
        test_url = "https://www.nfra.gov.cn/nfra/pages/ItemDetail.do?docId=1137316&generaltype=1"
        
        logger.info(f"正在测试页面: {test_url}")
        
        if crawler.load_page_with_retry(test_url, max_retries=2):
            logger.info("页面加载成功，开始解析...")
            
            detail_data = crawler.get_punishment_detail(test_url)
            
            logger.info("=== 真实页面解析结果 ===")
            print(json.dumps(detail_data, ensure_ascii=False, indent=2))
            
            # 特别关注这两个字段
            if '行政处罚依据' in detail_data:
                logger.info(f"✓ 成功提取行政处罚依据: {detail_data['行政处罚依据'][:100]}...")
            else:
                logger.warning("✗ 未能提取行政处罚依据")
                
            if '行政处罚内容' in detail_data:
                logger.info(f"✓ 成功提取行政处罚内容: {detail_data['行政处罚内容'][:100]}...")
            else:
                logger.warning("✗ 未能提取行政处罚内容")
        else:
            logger.error("页面加载失败")
            
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    finally:
        crawler.close_driver()

if __name__ == "__main__":
    print("=" * 50)
    print("测试1: 文本解析功能")
    print("=" * 50)
    test_enhanced_parsing()
    
    print("\n" + "=" * 50)
    print("测试2: 真实页面解析（需要网络连接）")
    print("=" * 50)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--real":
        test_real_page()
    else:
        print("如需测试真实页面，请运行: python test_enhanced_parsing.py --real") 