#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试EXE模式配置
验证exe模式下的配置是否正常工作
"""

import os
import sys

def test_normal_mode():
    """测试正常模式配置"""
    print("🧪 测试正常模式...")
    
    try:
        from config import SELENIUM_CONFIG, OUTPUT_CONFIG, BASE_URLS
        print(f"✅ 正常模式配置加载成功")
        print(f"   Headless模式: {SELENIUM_CONFIG['headless']}")
        print(f"   输出目录: {OUTPUT_CONFIG.get('excel_output_dir', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ 正常模式配置加载失败: {e}")
        return False

def test_exe_mode():
    """测试EXE模式配置"""
    print("🧪 测试EXE模式...")
    
    # 设置EXE模式环境变量
    os.environ['NFRA_EXE_MODE'] = '1'
    
    try:
        # 重新导入以测试exe配置
        import importlib
        if 'config_exe' in sys.modules:
            importlib.reload(sys.modules['config_exe'])
        
        from config_exe import SELENIUM_CONFIG, OUTPUT_CONFIG, BASE_URLS
        print(f"✅ EXE模式配置加载成功")
        print(f"   Headless模式: {SELENIUM_CONFIG['headless']}")
        print(f"   输出目录: {OUTPUT_CONFIG.get('excel_output_dir', 'N/A')}")
        print(f"   可用类别: {list(BASE_URLS.keys())}")
        return True
    except Exception as e:
        print(f"❌ EXE模式配置加载失败: {e}")
        return False
    finally:
        # 清理环境变量
        if 'NFRA_EXE_MODE' in os.environ:
            del os.environ['NFRA_EXE_MODE']

def test_main_module():
    """测试main模块在exe模式下的导入"""
    print("🧪 测试main模块...")
    
    # 设置EXE模式
    os.environ['NFRA_EXE_MODE'] = '1'
    
    try:
        import importlib
        # 如果已经导入过，需要重新加载
        modules_to_reload = ['main', 'crawler', 'utils', 'setup_driver']
        for module in modules_to_reload:
            if module in sys.modules:
                importlib.reload(sys.modules[module])
        
        import main
        print(f"✅ main模块导入成功")
        print(f"   可用运行模式: {list(main.RUN_MODES.keys())}")
        return True
    except Exception as e:
        print(f"❌ main模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理环境变量
        if 'NFRA_EXE_MODE' in os.environ:
            del os.environ['NFRA_EXE_MODE']

def test_nfra_crawler_exe():
    """测试nfra_crawler_exe启动脚本"""
    print("🧪 测试EXE启动脚本...")
    
    try:
        # 模拟exe环境
        original_frozen = getattr(sys, 'frozen', False)
        sys.frozen = True
        
        # 测试导入
        import nfra_crawler_exe
        print(f"✅ EXE启动脚本导入成功")
        
        # 测试一些关键函数是否存在
        functions_to_check = [
            'print_header', 'print_main_menu', 'show_files', 
            'webdriver_menu', 'custom_crawl'
        ]
        
        for func_name in functions_to_check:
            if hasattr(nfra_crawler_exe, func_name):
                print(f"   ✅ {func_name} 函数存在")
            else:
                print(f"   ❌ {func_name} 函数缺失")
        
        return True
    except Exception as e:
        print(f"❌ EXE启动脚本测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始状态
        if hasattr(sys, 'frozen') and not original_frozen:
            delattr(sys, 'frozen')

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 EXE模式配置测试")
    print("=" * 60)
    
    tests = [
        ("正常模式配置", test_normal_mode),
        ("EXE模式配置", test_exe_mode),
        ("main模块导入", test_main_module),
        ("EXE启动脚本", test_nfra_crawler_exe),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
        print()
    
    print("=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}")
        if success:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 测试通过")
    
    if success_count == len(results):
        print("🎉 所有测试通过！EXE模式配置正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 