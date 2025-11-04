#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间解析功能
"""

from zhihu_crawler import ZhihuArticleCrawler
from datetime import datetime


def test_time_parsing():
    """测试各种时间格式的解析"""
    
    # 创建爬虫实例
    crawler = ZhihuArticleCrawler()
    
    # 测试用例
    test_cases = [
        # (输入, 预期输出)
        ("发布于 2024-12-27 10:59・广东 (无法解析具体时间)", datetime(2024, 12, 27, 10, 59)),
        ("2024-11-03T12:34:56", datetime(2024, 11, 3, 12, 34, 56)),
        ("2024-11-03 12:34:56", datetime(2024, 11, 3, 12, 34, 56)),
        ("2024-11-03 12:34", datetime(2024, 11, 3, 12, 34)),
        ("发布于 2024-01-15 08:30", datetime(2024, 1, 15, 8, 30)),
        ("2024年12月27日 10:59", datetime(2024, 12, 27, 10, 59)),
        (None, None),
        ("", None),
    ]
    
    print("=" * 70)
    print("时间解析功能测试")
    print("=" * 70 + "\n")
    
    passed = 0
    failed = 0
    
    for input_text, expected_output in test_cases:
        result = crawler._parse_publish_time(input_text)
        
        # 检查结果
        if result == expected_output:
            status = "✅ 通过"
            passed += 1
        else:
            status = "❌ 失败"
            failed += 1
        
        print(f"输入: {repr(input_text)}")
        print(f"预期: {expected_output}")
        print(f"实际: {result}")
        print(f"状态: {status}\n")
    
    # 总结
    print("=" * 70)
    print(f"测试总结: {passed} 通过, {failed} 失败")
    print(f"通过率: {passed}/{passed+failed} = {100*passed/(passed+failed):.1f}%")
    print("=" * 70)


if __name__ == '__main__':
    test_time_parsing()

