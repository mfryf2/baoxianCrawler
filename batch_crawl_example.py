#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量抓取示例
演示如何批量抓取多篇知乎文章
"""

import time
import sys

# 文章URL列表
urls = [
    "https://zhuanlan.zhihu.com/p/1967253690982335635",
    # 在这里添加更多URL
]

def batch_crawl_with_playwright():
    """使用Playwright批量抓取"""
    try:
        from zhihu_crawler_playwright import ZhihuArticleCrawlerPlaywright
    except ImportError:
        print("✗ 错误: 未安装playwright")
        print("请运行: pip3 install playwright && python3 -m playwright install chromium")
        sys.exit(1)
    
    crawler = ZhihuArticleCrawlerPlaywright(headless=True)
    
    try:
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 正在抓取...")
            try:
                output_file = f"article_{i}.html"
                crawler.save_to_html(url, output_file)
                print(f"✓ 成功保存到: {output_file}")
            except Exception as e:
                print(f"✗ 失败: {e}")
            
            # 添加延迟，避免请求过快
            if i < len(urls):
                wait_time = 3
                print(f"等待 {wait_time} 秒...")
                time.sleep(wait_time)
    
    finally:
        crawler.close()
    
    print("\n批量抓取完成!")


def batch_crawl_with_requests(cookie=None):
    """使用requests批量抓取（需要Cookie）"""
    from zhihu_crawler import ZhihuArticleCrawler
    
    crawler = ZhihuArticleCrawler(cookie=cookie)
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 正在抓取...")
        try:
            output_file = f"article_{i}.html"
            crawler.save_to_html(url, output_file)
            print(f"✓ 成功保存到: {output_file}")
        except Exception as e:
            print(f"✗ 失败: {e}")
        
        # 添加延迟
        if i < len(urls):
            wait_time = 2
            print(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)
    
    print("\n批量抓取完成!")


if __name__ == '__main__':
    print("=" * 60)
    print("知乎文章批量抓取工具")
    print("=" * 60)
    print(f"\n共 {len(urls)} 篇文章待抓取\n")
    
    print("请选择抓取方式:")
    print("1. Playwright版本（推荐，更稳定）")
    print("2. Requests版本（需要Cookie）")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == '1':
        batch_crawl_with_playwright()
    elif choice == '2':
        cookie = input("请输入Cookie（可选，直接回车跳过）: ").strip()
        batch_crawl_with_requests(cookie if cookie else None)
    else:
        print("无效选项")
        sys.exit(1)
