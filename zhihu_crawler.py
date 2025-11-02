#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎文章抓取工具 - 单篇抓取版
只抓取文章主体内容，不包括侧边栏
"""

import requests
from bs4 import BeautifulSoup
import sys
import os
from datetime import datetime
import time
import json
import re
import random


class ZhihuArticleCrawler:
    def __init__(self, cookie=None):
        """
        初始化爬虫
        
        Args:
            cookie: 可选的cookie字符串，用于绕过登录限制
        """
        # 多个User-Agent轮换使用
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        self.cookie = cookie
        self.session = requests.Session()
    
    def _get_headers(self):
        """获取请求头"""
        headers = self.base_headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        headers['Referer'] = 'https://www.zhihu.com/'
        
        if self.cookie:
            headers['Cookie'] = self.cookie
        
        return headers
    
    def _make_request(self, url, max_retries=5):
        """
        发送HTTP请求，带智能重试
        
        Args:
            url: 目标URL
            max_retries: 最大重试次数
            
        Returns:
            requests.Response: 响应对象
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # 指数退避 + 随机抖动
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️  等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                
                headers = self._get_headers()
                
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=20,
                    allow_redirects=True
                )
                
                # 检查是否被反爬虫拦截
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        print(f"⚠️  遇到403错误，尝试更换User-Agent重试 ({attempt + 1}/{max_retries})")
                        continue
                    else:
                        raise Exception("403 Forbidden - 需要提供有效的Cookie")
                
                if response.status_code == 429:
                    wait_time = 5 + random.uniform(0, 5)
                    print(f"⚠️  请求过快，等待 {wait_time:.1f} 秒...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                # 检查是否是验证页面
                if 'zh-zse-ck' in response.text or len(response.text) < 1000:
                    if attempt < max_retries - 1:
                        print(f"⚠️  检测到验证页面，重试中 ({attempt + 1}/{max_retries})")
                        time.sleep(3)
                        continue
                    else:
                        raise Exception("遇到验证页面，请提供有效的Cookie")
                
                return response
                
            except requests.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️  请求超时，重试中 ({attempt + 1}/{max_retries})")
                    continue
                else:
                    raise Exception("请求超时")
            
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  请求失败: {str(e)}, 重试中 ({attempt + 1}/{max_retries})")
                    continue
                else:
                    raise Exception(f"网络请求失败: {str(e)}")
        
        raise Exception("达到最大重试次数")
    
    def fetch_article(self, url):
        """
        抓取知乎文章
        
        Args:
            url: 知乎文章URL
            
        Returns:
            tuple: (title, content_html, author, publish_time) 文章信息
        """
        response = self._make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取文章标题 - 多种方式尝试
        title = None
        title_selectors = [
            ('h1', {'class': 'Post-Title'}),
            ('h1', {'class': 'ArticleTitle'}),
            ('h1', {}),
            ('title', {})
        ]
        
        for tag, attrs in title_selectors:
            title = soup.find(tag, attrs)
            if title:
                break
        
        title_text = title.get_text().strip() if title else '未知标题'
        # 清理标题中的特殊字符
        title_text = re.sub(r'\s+', ' ', title_text)
        
        # 提取文章主体内容 - 多种选择器
        article_content = None
        content_selectors = [
            ('div', {'class': 'Post-RichTextContainer'}),
            ('div', {'class': 'RichText'}),
            ('div', {'class': 'Post-RichText'}),
            ('article', {'class': 'Post-Main'}),
            ('article', {}),
            ('div', {'class': 'content'}),
        ]
        
        for tag, attrs in content_selectors:
            article_content = soup.find(tag, attrs)
            if article_content and len(article_content.get_text().strip()) > 100:
                break
        
        if not article_content:
            raise Exception("未找到文章内容，可能需要登录或Cookie")
        
        # 提取作者信息
        author_name = ''
        author_selectors = [
            ('div', {'class': 'AuthorInfo'}),
            ('div', {'class': 'author-info'}),
            ('a', {'class': 'UserLink'}),
        ]
        
        for tag, attrs in author_selectors:
            author_info = soup.find(tag, attrs)
            if author_info:
                author_link = author_info.find('a', class_='UserLink')
                if not author_link:
                    author_link = author_info.find('a')
                if author_link:
                    author_name = author_link.get_text().strip()
                    break
        
        # 提取发布时间
        publish_time_text = ''
        time_selectors = [
            ('div', {'class': 'ContentItem-time'}),
            ('div', {'class': 'publish-time'}),
            ('time', {}),
        ]
        
        for tag, attrs in time_selectors:
            publish_time = soup.find(tag, attrs)
            if publish_time:
                publish_time_text = publish_time.get_text().strip()
                break
        
        return title_text, article_content, author_name, publish_time_text
    
    def save_to_html(self, url, output_file=None):
        """
        抓取文章并保存为HTML文件
        
        Args:
            url: 知乎文章URL
            output_file: 输出文件名，如果为None则自动生成
            
        Returns:
            str: 输出文件路径
        """
        print(f"正在抓取: {url}")
        
        title, content, author, publish_time = self.fetch_article(url)
        
        print(f"✓ 文章标题: {title}")
        if author:
            print(f"✓ 作者: {author}")
        if publish_time:
            print(f"✓ 发布时间: {publish_time}")
        
        # 生成输出文件名
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:50]  # 限制文件名长度
            output_file = f"{safe_title}_{timestamp}.html"
        
        # 构建完整的HTML文档
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #1a1a1a;
        }}
        .meta-info {{
            color: #8590a6;
            font-size: 14px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e5e5;
        }}
        .article-content {{
            font-size: 16px;
            color: #1a1a1a;
        }}
        .article-content img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px 0;
        }}
        .article-content p {{
            margin: 15px 0;
        }}
        .article-content pre {{
            background: #f6f6f6;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .article-content code {{
            background: #f6f6f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }}
        .article-content blockquote {{
            border-left: 3px solid #ddd;
            padding-left: 15px;
            color: #666;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta-info">
        {f'<div>作者: {author}</div>' if author else ''}
        {f'<div>发布时间: {publish_time}</div>' if publish_time else ''}
        <div>原文链接: <a href="{url}">{url}</a></div>
    </div>
    <div class="article-content">
        {content}
    </div>
</body>
</html>"""
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"✓ 文章已保存到: {output_file}")
        return output_file


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("知乎文章抓取工具 - 单篇抓取版")
        print("=" * 70)
        print("\n使用方法:")
        print("  python3 zhihu_crawler.py <URL> [输出文件] [--cookie COOKIE]")
        print("\n示例:")
        print("  # 基础抓取")
        print("  python3 zhihu_crawler.py https://zhuanlan.zhihu.com/p/123456")
        print("\n  # 指定输出文件")
        print("  python3 zhihu_crawler.py https://zhuanlan.zhihu.com/p/123456 output.html")
        print("\n  # 使用Cookie（推荐）")
        print("  python3 zhihu_crawler.py https://zhuanlan.zhihu.com/p/123456 --cookie 'xxx'")
        print("\n获取Cookie的方法:")
        print("  1. 在浏览器中打开知乎并登录")
        print("  2. 按F12打开开发者工具，切换到Network标签")
        print("  3. 刷新页面，找到文章请求，复制Cookie值")
        print("  4. 或运行: python3 get_cookie_helper.py")
        print("=" * 70)
        sys.exit(1)
    
    # 解析参数
    url = None
    output_file = None
    cookie = None
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--cookie':
            if i + 1 < len(sys.argv):
                cookie = sys.argv[i + 1]
                i += 2
            else:
                print("✗ 错误: --cookie 需要提供Cookie值")
                sys.exit(1)
        elif arg.startswith('--'):
            print(f"✗ 错误: 未知选项 {arg}")
            sys.exit(1)
        else:
            if not url:
                url = arg
            elif not output_file:
                output_file = arg
            i += 1
    
    if not url:
        print("✗ 错误: 请提供URL")
        sys.exit(1)
    
    # 创建爬虫实例
    crawler = ZhihuArticleCrawler(cookie=cookie)
    
    try:
        crawler.save_to_html(url, output_file)
        print("\n✅ 抓取成功！")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ 错误: {str(e)}")
        if '403' in str(e) or 'Cookie' in str(e):
            print("\n💡 提示: 需要提供有效的Cookie")
            print("   运行 'python3 get_cookie_helper.py' 查看如何获取Cookie")
        sys.exit(1)


if __name__ == '__main__':
    main()
