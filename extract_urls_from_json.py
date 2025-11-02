#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从作者文章JSON文件中提取URL列表
用于后续批量抓取文章内容
"""

import json
import sys
import os
from datetime import datetime


def extract_urls_from_json(json_file, output_file=None, max_urls=None):
    """
    从JSON文件中提取文章URL
    
    Args:
        json_file: JSON文件路径
        output_file: 输出文件路径
        max_urls: 最大URL数量限制
        
    Returns:
        list: URL列表
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'articles' not in data:
            print(f"❌ JSON文件格式错误，未找到articles字段")
            return []
        
        articles = data['articles']
        urls = []
        
        for article in articles:
            if 'url' in article and article['url']:
                url = article['url']
                # 确保URL是完整的
                if url.startswith('http://'):
                    url = url.replace('http://', 'https://')
                elif not url.startswith('https://'):
                    url = 'https://www.zhihu.com' + url
                
                urls.append(url)
                
                if max_urls and len(urls) >= max_urls:
                    break
        
        # 保存URL列表
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            author_name = data.get('author', {}).get('name', 'unknown')
            safe_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name[:20]  # 限制文件名长度
            output_file = f"{safe_name}_urls_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        
        print(f"✅ 成功提取 {len(urls)} 个URL")
        print(f"✅ 已保存到: {output_file}")
        
        # 显示统计信息
        if 'author' in data:
            author_info = data['author']
            print(f"\n📊 统计信息:")
            print(f"作者: {author_info.get('name', '未知')}")
            print(f"总文章数: {data.get('total_fetched', 0)}")
            print(f"提取URL数: {len(urls)}")
        
        return urls
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {json_file}")
        return []
    except json.JSONDecodeError:
        print(f"❌ JSON文件格式错误: {json_file}")
        return []
    except Exception as e:
        print(f"❌ 处理文件时出错: {str(e)}")
        return []


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("从作者文章JSON文件中提取URL列表")
        print("=" * 70)
        print("\n使用方法:")
        print("  python3 extract_urls_from_json.py <JSON文件> [选项]")
        print("\n选项:")
        print("  --output FILE      输出文件名")
        print("  --max-urls N       最大URL数量限制")
        print("\n示例:")
        print("  # 提取所有URL")
        print("  python3 extract_urls_from_json.py author_articles.json")
        print("\n  # 限制提取100个URL")
        print("  python3 extract_urls_from_json.py author_articles.json --max-urls 100")
        print("\n  # 指定输出文件")
        print("  python3 extract_urls_from_json.py author_articles.json --output urls.txt")
        print("\n后续使用:")
        print("  # 批量抓取文章内容")
        print("  python3 zhihu_crawler.py --batch extracted_urls.txt --cookie \"你的Cookie\"")
        print("=" * 70)
        sys.exit(1)
    
    # 解析参数
    json_file = sys.argv[1]
    output_file = None
    max_urls = None
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--output':
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print("✗ 错误: --output 需要提供文件名")
                sys.exit(1)
        elif arg == '--max-urls':
            if i + 1 < len(sys.argv):
                max_urls = int(sys.argv[i + 1])
                i += 2
            else:
                print("✗ 错误: --max-urls 需要提供数量")
                sys.exit(1)
        else:
            print(f"✗ 错误: 未知选项 {arg}")
            sys.exit(1)
    
    # 检查文件是否存在
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        sys.exit(1)
    
    try:
        print("=" * 70)
        print("提取URL列表")
        print("=" * 70)
        
        urls = extract_urls_from_json(json_file, output_file, max_urls)
        
        if urls:
            print(f"\n🎉 提取完成！")
            print(f"\n💡 下一步:")
            print(f"python3 zhihu_crawler.py --batch {output_file or 'extracted_urls.txt'} --cookie \"你的Cookie\"")
        else:
            print("❌ 未提取到任何URL")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()