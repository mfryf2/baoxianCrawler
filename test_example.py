#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试示例 - 演示如何使用爬虫工具
"""

from zhihu_crawler import ZhihuArticleCrawler

# 测试URL
test_url = "https://zhuanlan.zhihu.com/p/1967253690982335635"

print("=" * 60)
print("知乎文章抓取工具 - 测试示例")
print("=" * 60)
print()

print("测试URL:", test_url)
print()

print("方法1: 使用requests版本（可能遇到403错误）")
print("-" * 60)
try:
    crawler = ZhihuArticleCrawler()
    crawler.save_to_html(test_url, "test_output_requests.html")
    print("✓ 成功!")
except Exception as e:
    print(f"✗ 失败: {e}")
    print()
    print("提示: 如果遇到403错误，请使用以下方法之一:")
    print("1. 使用 extract_from_saved.py（手动保存网页后提取）")
    print("2. 使用 zhihu_crawler_playwright.py（需要先安装playwright）")
    print("3. 提供Cookie参数")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
