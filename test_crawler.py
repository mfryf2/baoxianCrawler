#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的爬虫功能
"""

import sys
import os

# 测试URL
TEST_URL = "https://zhuanlan.zhihu.com/p/1967253690982335635"
TEST_URL = "https://zhuanlan.zhihu.com/p/1967233914323072372"

def test_basic():
    """测试基础功能"""
    print("=" * 70)
    print("测试1: 基础功能测试")
    print("=" * 70)
    
    from zhihu_crawler import ZhihuArticleCrawler
    
    # 读取Cookie（如果存在）
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
        print("✓ 已加载Cookie")
    else:
        print("⚠️  未找到cookie.txt，将不使用Cookie")
    
    crawler = ZhihuArticleCrawler(cookie=cookie)
    
    try:
        print(f"\n正在测试URL: {TEST_URL}")
        title, content, author, publish_time = crawler.fetch_article(TEST_URL)
        
        print(f"\n✅ 抓取成功！")
        print(f"标题: {title}")
        print(f"作者: {author or '未知'}")
        print(f"发布时间: {publish_time or '未知'}")
        print(f"内容长度: {len(str(content))} 字符")
        
        # 保存测试
        output_file = "test_output.html"
        crawler.save_to_html(TEST_URL, output_file)
        print(f"\n✅ 已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False


def test_batch():
    """测试批量抓取"""
    print("\n" + "=" * 70)
    print("测试2: 批量抓取测试")
    print("=" * 70)
    
    from zhihu_crawler import ZhihuArticleCrawler
    
    # 创建测试URL文件
    test_urls = [TEST_URL]
    urls_file = "test_urls.txt"
    
    with open(urls_file, 'w', encoding='utf-8') as f:
        for url in test_urls:
            f.write(url + '\n')
    
    print(f"✓ 已创建测试URL文件: {urls_file}")
    
    # 读取Cookie
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuArticleCrawler(cookie=cookie, use_pool=True, pool_size=3)
    
    try:
        results = crawler.batch_crawl(
            urls_file,
            output_dir='test_output',
            max_workers=2,
            delay=1.0
        )
        
        print(f"\n✅ 批量抓取测试完成")
        print(f"成功: {len(results['success'])}")
        print(f"失败: {len(results['failed'])}")
        
        return len(results['success']) > 0
        
    except Exception as e:
        print(f"\n❌ 批量测试失败: {str(e)}")
        return False


def test_performance():
    """测试性能统计"""
    print("\n" + "=" * 70)
    print("测试3: 性能统计测试")
    print("=" * 70)
    
    from zhihu_crawler import ZhihuArticleCrawler
    import time
    
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuArticleCrawler(cookie=cookie)
    
    try:
        start = time.time()
        crawler.fetch_article(TEST_URL)
        elapsed = time.time() - start
        
        stats = crawler.get_stats()
        
        print(f"\n✅ 性能统计:")
        print(f"抓取时间: {elapsed:.2f} 秒")
        print(f"成功次数: {stats['success']}")
        print(f"失败次数: {stats['failed']}")
        
        if stats['success'] > 0:
            avg_time = stats['total_time'] / stats['success']
            print(f"平均时间: {avg_time:.2f} 秒")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 性能测试失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("知乎爬虫优化版 - 功能测试")
    print("=" * 70)
    
    # 检查Cookie
    if not os.path.exists('cookie.txt'):
        print("\n⚠️  警告: 未找到 cookie.txt 文件")
        print("建议先运行: python3 get_cookie_helper.py -v")
        print("\n继续测试可能会遇到403错误...")
        
        response = input("\n是否继续测试？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return
    
    results = []
    
    # 运行测试
    results.append(("基础功能", test_basic()))
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查Cookie或网络连接")
    
    print("=" * 70)


if __name__ == '__main__':
    main()
