#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎作者文章列表抓取 - 使用示例
"""

import os
from zhihu_author_crawler import ZhihuAuthorCrawler

def example_basic_usage():
    """基础使用示例"""
    print("=" * 80)
    print("示例1: 基础使用 - 获取作者所有文章")
    print("=" * 80)
    
    # 作者URL - 奶爸保险
    author_url = "https://www.zhihu.com/org/nai-ba-bao-25/posts"
    
    # 读取Cookie（如果存在）
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
        print("✓ 已加载Cookie")
    
    # 创建爬虫实例
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    try:
        # 获取所有文章（这里限制为50篇作为示例）
        print(f"正在获取作者文章: {author_url}")
        data = crawler.fetch_author_articles(
            author_url,
            max_articles=50,  # 限制50篇，实际使用时可以去掉这个参数获取所有文章
            delay=1.0  # 请求间隔1秒
        )
        
        if data:
            print(f"\n✅ 获取成功！")
            print(f"作者: {data['author']['name']}")
            print(f"文章数量: {data['total_fetched']}")
            
            # 保存为多种格式
            crawler.save_to_json(data)
            crawler.save_to_txt(data)
            crawler.save_to_csv(data)
            
            return True
        else:
            print("❌ 获取失败")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def example_limited_articles():
    """限量获取示例"""
    print("\n" + "=" * 80)
    print("示例2: 限量获取 - 只获取最新的20篇文章")
    print("=" * 80)
    
    author_url = "https://www.zhihu.com/org/nai-ba-bao-25/posts"
    
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    try:
        # 只获取最新的20篇文章
        data = crawler.fetch_author_articles(
            author_url,
            max_articles=20,
            delay=0.5  # 减少延迟
        )
        
        if data:
            print(f"\n✅ 获取成功！获取了 {data['total_fetched']} 篇文章")
            
            # 显示文章列表
            print("\n最新文章列表:")
            for i, article in enumerate(data['articles'][:10], 1):  # 显示前10篇
                print(f"{i:2d}. {article['title']}")
                print(f"     {article['url']}")
                if article['created_time']:
                    print(f"     发布时间: {article['created_time']}")
                if article['voteup_count'] > 0:
                    print(f"     点赞数: {article['voteup_count']}")
                print()
            
            # 只保存为JSON格式
            json_file = crawler.save_to_json(data, "latest_20_articles.json")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def example_custom_output():
    """自定义输出示例"""
    print("\n" + "=" * 80)
    print("示例3: 自定义输出 - 指定文件名和格式")
    print("=" * 80)
    
    author_url = "https://www.zhihu.com/org/nai-ba-bao-25/posts"
    
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    try:
        # 获取文章
        data = crawler.fetch_author_articles(
            author_url,
            max_articles=10,  # 少量文章用于演示
            delay=0.5
        )
        
        if data:
            print(f"\n✅ 获取成功！")
            
            # 自定义文件名保存
            crawler.save_to_json(data, "naibaobao_articles.json")
            crawler.save_to_txt(data, "naibaobao_articles.txt")
            crawler.save_to_csv(data, "naibaobao_articles.csv")
            
            print("\n📊 数据统计:")
            print(f"作者: {data['author']['name']}")
            print(f"文章总数: {data['total_fetched']}")
            
            # 统计点赞数
            total_likes = sum(article['voteup_count'] for article in data['articles'])
            print(f"总点赞数: {total_likes}")
            
            # 找出最受欢迎的文章
            if data['articles']:
                most_liked = max(data['articles'], key=lambda x: x['voteup_count'])
                print(f"最受欢迎文章: {most_liked['title']} ({most_liked['voteup_count']} 赞)")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def example_multiple_authors():
    """多个作者示例"""
    print("\n" + "=" * 80)
    print("示例4: 批量处理 - 获取多个作者的文章")
    print("=" * 80)
    
    # 多个作者URL（这里只用一个作为示例）
    authors = [
        {
            'name': '奶爸保险',
            'url': 'https://www.zhihu.com/org/nai-ba-bao-25/posts'
        }
        # 可以添加更多作者
        # {
        #     'name': '其他作者',
        #     'url': 'https://www.zhihu.com/people/other-author/posts'
        # }
    ]
    
    cookie = None
    if os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
    
    crawler = ZhihuAuthorCrawler(cookie=cookie)
    
    results = []
    
    for author_info in authors:
        try:
            print(f"\n正在处理: {author_info['name']}")
            
            data = crawler.fetch_author_articles(
                author_info['url'],
                max_articles=5,  # 每个作者只获取5篇作为示例
                delay=1.0
            )
            
            if data:
                # 使用作者名称作为文件名前缀
                safe_name = "".join(c for c in author_info['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
                crawler.save_to_json(data, f"{safe_name}_articles.json")
                
                results.append({
                    'author': author_info['name'],
                    'articles_count': data['total_fetched'],
                    'success': True
                })
                
                print(f"✅ {author_info['name']}: 获取了 {data['total_fetched']} 篇文章")
            else:
                results.append({
                    'author': author_info['name'],
                    'articles_count': 0,
                    'success': False
                })
                print(f"❌ {author_info['name']}: 获取失败")
                
        except Exception as e:
            print(f"❌ {author_info['name']}: {str(e)}")
            results.append({
                'author': author_info['name'],
                'articles_count': 0,
                'success': False
            })
    
    # 总结
    print(f"\n📊 批量处理结果:")
    total_articles = 0
    success_count = 0
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['author']}: {result['articles_count']} 篇文章")
        if result['success']:
            total_articles += result['articles_count']
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(authors)} 个作者成功，共获取 {total_articles} 篇文章")
    
    return success_count > 0


def main():
    """运行所有示例"""
    print("知乎作者文章列表抓取工具 - 使用示例")
    print("=" * 80)
    
    # 检查Cookie
    if not os.path.exists('cookie.txt'):
        print("\n⚠️  警告: 未找到 cookie.txt 文件")
        print("建议先运行: python3 get_cookie_helper.py")
        print("\n没有Cookie可能会遇到访问限制...")
        
        response = input("\n是否继续运行示例？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return
    
    # 运行示例
    examples = [
        ("基础使用", example_basic_usage),
        ("限量获取", example_limited_articles),
        ("自定义输出", example_custom_output),
        ("批量处理", example_multiple_authors),
    ]
    
    for name, func in examples:
        try:
            print(f"\n{'='*20} 运行 {name} {'='*20}")
            success = func()
            if success:
                print(f"✅ {name} 示例运行成功")
            else:
                print(f"❌ {name} 示例运行失败")
        except KeyboardInterrupt:
            print(f"\n⚠️  用户中断了 {name} 示例")
            break
        except Exception as e:
            print(f"❌ {name} 示例出错: {str(e)}")
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("\n💡 提示:")
    print("1. 实际使用时，可以去掉 max_articles 参数获取所有文章")
    print("2. 可以调整 delay 参数控制请求频率")
    print("3. 建议使用有效的Cookie以避免访问限制")
    print("4. 大量数据抓取时请注意遵守网站的使用条款")
    print("=" * 80)


if __name__ == '__main__':
    main()