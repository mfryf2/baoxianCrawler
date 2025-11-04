#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎文章抓取工具 - 使用示例脚本
演示如何使用升级后的工具
"""

from zhihu_crawler import ZhihuArticleCrawler
from config import DB_CONFIG, CRAWLER_CONFIG


def example1_single_article():
    """示例 1：单篇文章抓取并保存为 HTML"""
    print("=" * 70)
    print("示例 1：单篇文章抓取")
    print("=" * 70)
    
    # 创建爬虫实例（不使用 Cookie）
    crawler = ZhihuArticleCrawler()
    
    # 知乎文章 URL
    url = "https://zhuanlan.zhihu.com/p/123456"  # 替换为实际 URL
    
    try:
        # 抓取并保存为 HTML
        output_file = crawler.save_to_html(url)
        print(f"\n✅ 成功！HTML 文件已保存到: {output_file}")
    except Exception as e:
        print(f"\n❌ 抓取失败: {e}")


def example2_single_article_with_cookie():
    """示例 2：使用 Cookie 抓取单篇文章"""
    print("=" * 70)
    print("示例 2：使用 Cookie 抓取单篇文章")
    print("=" * 70)
    
    # 获取 Cookie（从浏览器开发者工具复制）
    cookie = "your_cookie_here"  # 替换为实际 Cookie
    
    # 创建爬虫实例
    crawler = ZhihuArticleCrawler(cookie=cookie)
    
    url = "https://zhuanlan.zhihu.com/p/123456"  # 替换为实际 URL
    
    try:
        output_file = crawler.save_to_html(url)
        print(f"\n✅ 成功！HTML 文件已保存到: {output_file}")
    except Exception as e:
        print(f"\n❌ 抓取失败: {e}")


def example3_batch_crawl():
    """示例 3：从数据库批量抓取文章"""
    print("=" * 70)
    print("示例 3：从数据库批量抓取文章")
    print("=" * 70)
    
    # 获取 Cookie
    cookie = "your_cookie_here"  # 替换为实际 Cookie
    
    # 创建爬虫实例，传入数据库配置
    crawler = ZhihuArticleCrawler(
        cookie=cookie,
        db_config=DB_CONFIG
    )
    
    try:
        # 批量抓取 10 篇文章
        crawler.batch_crawl_and_save(limit=10)
        print("\n✅ 批量抓取完成！")
    except Exception as e:
        print(f"\n❌ 批量抓取失败: {e}")


def example4_batch_crawl_custom_limit():
    """示例 4：批量抓取指定数量的文章"""
    print("=" * 70)
    print("示例 4：批量抓取自定义数量的文章")
    print("=" * 70)
    
    cookie = "your_cookie_here"  # 替换为实际 Cookie
    
    crawler = ZhihuArticleCrawler(
        cookie=cookie,
        db_config=DB_CONFIG
    )
    
    try:
        # 批量抓取 20 篇文章
        crawler.batch_crawl_and_save(limit=20)
        print("\n✅ 批量抓取完成！")
    except Exception as e:
        print(f"\n❌ 批量抓取失败: {e}")


def example5_fetch_article_info():
    """示例 5：仅提取文章信息而不保存"""
    print("=" * 70)
    print("示例 5：仅提取文章信息")
    print("=" * 70)
    
    cookie = "your_cookie_here"  # 替换为实际 Cookie
    
    crawler = ZhihuArticleCrawler(cookie=cookie)
    
    url = "https://zhuanlan.zhihu.com/p/123456"  # 替换为实际 URL
    
    try:
        # 获取文章信息
        article_info = crawler.fetch_article(url)
        
        print(f"\n✅ 文章信息提取成功:")
        print(f"  - 标题: {article_info['title']}")
        print(f"  - 作者: {article_info['author']}")
        print(f"  - 发布时间: {article_info['publish_time']}")
        print(f"  - 赞同数: {article_info['like_count']}")
        print(f"  - 内容长度: {len(str(article_info['content']))} 字符")
        
    except Exception as e:
        print(f"\n❌ 提取失败: {e}")


if __name__ == '__main__':
    print("\n知乎文章抓取工具 - 使用示例\n")
    
    # 注意：这些是示例，实际使用时需要替换 URL 和 Cookie
    print("可用的示例函数:")
    print("  1. example1_single_article() - 单篇文章抓取")
    print("  2. example2_single_article_with_cookie() - 使用 Cookie 抓取")
    print("  3. example3_batch_crawl() - 批量抓取 10 篇")
    print("  4. example4_batch_crawl_custom_limit() - 批量抓取自定义数量")
    print("  5. example5_fetch_article_info() - 仅提取文章信息")
    print("\n在编辑此文件时，将 'your_cookie_here' 和 URL 替换为实际值，")
    print("然后调用相应的函数。\n")
