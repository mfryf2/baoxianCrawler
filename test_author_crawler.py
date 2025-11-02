#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知乎作者文章列表抓取功能
"""

import sys
import os
from datetime import datetime

# 测试作者URL
TEST_AUTHOR_URL = "https://www.zhihu.com/org/nai-ba-bao-25/posts"

def test_author_info():
    """测试获取作者信息"""
    print("=" * 70)
    print("测试1: 获取作者信息")
    print("=" * 70)
    
    from zhihu_author_crawler import ZhihuAuthorCrawler
    
    # 读取Cookie（如果存在）
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
        print("✓ 已加载Cookie")
    else:
        print("⚠️  未找到cookie.txt，将不使用Cookie")
    
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    try:
        print(f"\n正在测试作者URL: {TEST_AUTHOR_URL}")
        author_info = crawler._extract_author_info(TEST_AUTHOR_URL)
        
        print(f"\n✅ 获取作者信息成功！")
        print(f"作者名称: {author_info['name']}")
        print(f"作者ID: {author_info['id']}")
        print(f"作者页面: {author_info['url']}")
        print(f"预计文章数: {author_info['total_posts']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False


def test_fetch_limited_articles():
    """测试获取限量文章"""
    print("\n" + "=" * 70)
    print("测试2: 获取前10篇文章")
    print("=" * 70)
    
    from zhihu_author_crawler import ZhihuAuthorCrawler
    
    # 读取Cookie
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    try:
        data = crawler.fetch_author_articles(
            TEST_AUTHOR_URL,
            max_articles=10,  # 只获取前10篇
            delay=0.5  # 减少延迟加快测试
        )
        
        if data:
            print(f"\n✅ 获取文章成功！")
            print(f"作者: {data['author']['name']}")
            print(f"获取文章数: {data['total_fetched']}")
            
            # 显示前3篇文章
            print(f"\n前3篇文章:")
            for i, article in enumerate(data['articles'][:3], 1):
                print(f"{i}. {article['title']}")
                print(f"   URL: {article['url']}")
                if article['created_time']:
                    print(f"   发布时间: {article['created_time']}")
                print()
            
            # 保存测试数据
            output_file = f"test_author_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            crawler.save_to_json(data, output_file)
            
            return True
        else:
            print(f"\n❌ 获取失败")
            return False
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False


def test_save_formats():
    """测试不同保存格式"""
    print("\n" + "=" * 70)
    print("测试3: 测试保存格式")
    print("=" * 70)
    
    from zhihu_author_crawler import ZhihuAuthorCrawler
    
    # 读取Cookie
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    try:
        # 获取少量文章用于测试
        data = crawler.fetch_author_articles(
            TEST_AUTHOR_URL,
            max_articles=5,
            delay=0.5
        )
        
        if not data:
            print("❌ 获取文章失败")
            return False
        
        print(f"\n✅ 获取到 {data['total_fetched']} 篇文章，测试保存格式...")
        
        # 测试保存为不同格式
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        json_file = crawler.save_to_json(data, f"test_format_{timestamp}.json")
        txt_file = crawler.save_to_txt(data, f"test_format_{timestamp}.txt")
        csv_file = crawler.save_to_csv(data, f"test_format_{timestamp}.csv")
        
        # 检查文件是否创建成功
        files_created = []
        for file_path in [json_file, txt_file, csv_file]:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                files_created.append(f"{file_path} ({size} bytes)")
        
        print(f"\n✅ 成功创建 {len(files_created)} 个文件:")
        for file_info in files_created:
            print(f"  - {file_info}")
        
        return len(files_created) == 3
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False


def test_api_url_generation():
    """测试API URL生成"""
    print("\n" + "=" * 70)
    print("测试4: API URL生成")
    print("=" * 70)
    
    from zhihu_author_crawler import ZhihuAuthorCrawler
    
    crawler = ZhihuAuthorCrawler()
    
    test_cases = [
        ("https://www.zhihu.com/org/nai-ba-bao-25/posts", "机构账号"),
        ("https://www.zhihu.com/people/test-user/posts", "个人账号"),
    ]
    
    success_count = 0
    
    for url, desc in test_cases:
        try:
            api_url = crawler._get_api_url(url)
            print(f"✅ {desc}: {url}")
            print(f"   API URL: {api_url}")
            success_count += 1
        except Exception as e:
            print(f"❌ {desc}: {url}")
            print(f"   错误: {str(e)}")
    
    print(f"\n✅ API URL生成测试: {success_count}/{len(test_cases)} 通过")
    return success_count == len(test_cases)


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("知乎作者文章列表抓取工具 - 功能测试")
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
    results.append(("API URL生成", test_api_url_generation()))
    results.append(("获取作者信息", test_author_info()))
    results.append(("获取限量文章", test_fetch_limited_articles()))
    results.append(("保存格式测试", test_save_formats()))
    
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
        print("\n使用示例:")
        print("python3 zhihu_author_crawler.py https://www.zhihu.com/org/nai-ba-bao-25/posts")
    else:
        print("\n⚠️  部分测试失败，请检查Cookie或网络连接")
    
    print("=" * 70)


if __name__ == '__main__':
    main()