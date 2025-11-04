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
import pymysql
from pymysql.cursors import DictCursor


class ZhihuArticleCrawler:
    def __init__(self, cookie=None, db_config=None):
        """
        初始化爬虫
        
        Args:
            cookie: 可选的cookie字符串，用于绕过登录限制
            db_config: 数据库配置字典 (host, user, password, database, port)
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
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        
        self.cookie = cookie
        self.session = requests.Session()
        self.db_config = db_config
    
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
    
    def _clean_html_content(self, html_element):
        """
        清理HTML内容，移除无效的CSS和冗余样式
        
        Args:
            html_element: BeautifulSoup元素
            
        Returns:
            str: 清理后的HTML字符串
        """
        # 移除所有style标签（特别是emotion-css标签）
        for style_tag in html_element.find_all('style'):
            style_tag.decompose()
        
        # 移除所有data-emotion-css属性和其他无用属性
        for element in html_element.find_all(True):  # True表示所有元素
            # 移除无用的属性
            attrs_to_remove = [
                'data-emotion-css',
                'class',  # 移除emotion生成的类名
                'data-pid',
                'data-draft-type',
                'data-first-child',
                'data-search-entity',
                'data-caption',
                'data-original',
                'data-original-token',
                'data-rawheight',
                'data-rawwidth',
                'data-size',
                'eeimg',
            ]
            
            for attr in attrs_to_remove:
                if element.has_attr(attr):
                    del element[attr]
        
        # 返回清理后的HTML字符串
        return str(html_element)
    
    def _extract_like_count(self, soup):
        """
        提取文章的赞同数（点赞数）
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            int: 赞同数，如果无法提取则返回-1
        """
        try:
            # 尝试多种方式提取赞同数
            selectors = [
                {'tag': 'button', 'attrs': {'aria-label': re.compile(r'.*赞同.*')}},
                {'tag': 'div', 'attrs': {'class': re.compile(r'.*like.*|.*VoteButton.*')}},
                {'tag': 'span', 'attrs': {'class': re.compile(r'.*count.*|.*number.*')}},
            ]
            
            for selector in selectors:
                elements = soup.find_all(selector['tag'], selector['attrs'])
                for element in elements:
                    text = element.get_text().strip()
                    # 提取数字
                    numbers = re.findall(r'\d+', text)
                    if numbers:
                        return int(numbers[0])
            
            # 尝试从页面源码中提取
            page_text = soup.get_text()
            match = re.search(r'赞同\s*(\d+)', page_text)
            if match:
                return int(match.group(1))
                
        except Exception as e:
            print(f"⚠️  提取赞同数失败: {str(e)}")
        
        return -1
    
    def fetch_article(self, url):
        """
        抓取知乎文章
        
        Args:
            url: 知乎文章URL
            
        Returns:
            dict: 文章信息字典，包含 title, content, author, publish_time, like_count
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
            found_element = soup.find(tag, attrs)
            if found_element:
                content_text = found_element.get_text().strip()
                if len(content_text) > 100:
                    article_content = found_element
                    break
        
        if not article_content:
            raise Exception("未找到文章内容，可能需要登录或Cookie")
        
        # 清理内容中的CSS和无用属性
        article_content = BeautifulSoup(self._clean_html_content(article_content), 'html.parser')
        
        # 提取作者信息 - 改进的多种方式
        author_name = ''
        
        # 策略 1: 从 Meta itemprop 标签提取
        if not author_name:
            try:
                author_meta = soup.find('meta', {'itemprop': 'name'})
                if author_meta and author_meta.get('content'):
                    author_name = author_meta['content'].strip()
            except:
                pass
        
        # 策略 2: 从 UserLink-link 类的链接中提取
        if not author_name:
            try:
                author_link = soup.find('a', {'class': 'UserLink-link'})
                if author_link:
                    author_name = author_link.get_text().strip()
            except:
                pass
        
        # 策略 3: 从 Post-Author 区域中查找
        if not author_name:
            try:
                post_author = soup.find('div', {'class': 'Post-Author'})
                if post_author:
                    # 尝试从链接中提取
                    author_link = post_author.find('a', {'class': 'UserLink-link'})
                    if author_link:
                        author_name = author_link.get_text().strip()
                    
                    # 如果没有找到，尝试从 Meta 标签提取
                    if not author_name:
                        meta_name = post_author.find('meta', {'itemprop': 'name'})
                        if meta_name and meta_name.get('content'):
                            author_name = meta_name['content'].strip()
            except:
                pass
        
        # 策略 4: 从 AuthorInfo 中提取
        if not author_name:
            author_selectors = [
                ('div', {'class': 'AuthorInfo'}),
                ('div', {'class': 'author-info'}),
                ('span', {'class': re.compile(r'.*author.*', re.I)}),
            ]
            
            for tag, attrs in author_selectors:
                author_info = soup.find(tag, attrs)
                if author_info:
                    # 尝试从链接中提取
                    author_link = author_info.find('a', {'class': 'UserLink-link'})
                    if not author_link:
                        author_link = author_info.find('a')
                    if author_link:
                        author_name = author_link.get_text().strip()
                        if author_name:
                            break
        
        # 提取发布时间 - 改进的多种方式
        publish_time_text = ''
        time_selectors = [
            ('div', {'class': 'ContentItem-time'}),
            ('div', {'class': 'publish-time'}),
            ('time', {}),
            ('meta', {'property': 'article:published_time'}),  # 新增：从 meta 标签
            ('span', {'class': re.compile(r'.*time.*|.*date.*', re.I)}),  # 新增：正则匹配
        ]
        
        for tag, attrs in time_selectors:
            if tag == 'meta':
                # meta 标签使用 content 属性
                time_elem = soup.find(tag, attrs)
                if time_elem and time_elem.get('content'):
                    publish_time_text = time_elem['content'].strip()
                    break
            else:
                publish_time = soup.find(tag, attrs)
                if publish_time:
                    publish_time_text = publish_time.get_text().strip()
                    break
        
        # 提取赞同数
        like_count = self._extract_like_count(soup)
        
        return {
            'title': title_text,
            'content': article_content,
            'author': author_name,
            'publish_time': publish_time_text,
            'like_count': like_count
        }
    
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
        
        article_info = self.fetch_article(url)
        title = article_info['title']
        content = article_info['content']
        author = article_info['author']
        publish_time = article_info['publish_time']
        
        print(f"✓ 文章标题: {title}")
        if author:
            print(f"✓ 作者: {author}")
        if publish_time:
            print(f"✓ 发布时间: {publish_time}")
        if article_info['like_count'] >= 0:
            print(f"✓ 赞同数: {article_info['like_count']}")
        
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
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            color: #1a1a1a;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }}
        h1 {{
            font-size: 28px;
        }}
        h2 {{
            font-size: 24px;
        }}
        h3 {{
            font-size: 20px;
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
            word-break: break-word;
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
        .article-content ul, .article-content ol {{
            margin: 15px 0;
            padding-left: 2em;
        }}
        .article-content li {{
            margin: 8px 0;
        }}
        .article-content pre {{
            background: #f6f6f6;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 14px;
        }}
        .article-content code {{
            background: #f6f6f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
            font-size: 0.95em;
        }}
        .article-content pre code {{
            background: none;
            padding: 0;
        }}
        .article-content blockquote {{
            border-left: 3px solid #ddd;
            padding-left: 15px;
            color: #666;
            margin: 15px 0;
        }}
        .article-content table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        .article-content table td, .article-content table th {{
            border: 1px solid #ddd;
            padding: 10px;
        }}
        .article-content table th {{
            background: #f6f6f6;
            font-weight: 600;
        }}
        .article-content hr {{
            margin: 30px 0;
            border: none;
            border-top: 1px solid #ddd;
        }}
        a {{
            color: #09408e;
            text-decoration: none;
            border-bottom: 1px solid #81858f;
        }}
        a:hover {{
            border-bottom-color: #09408e;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="meta-info">
        {f'<div>作者: {author}</div>' if author else ''}
        {f'<div>发布时间: {publish_time}</div>' if publish_time else ''}
        {f'<div>赞同数: {article_info["like_count"]}</div>' if article_info['like_count'] >= 0 else ''}
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
    
    def _parse_publish_time(self, time_text):
        """
        解析发布时间，支持多种格式
        
        Args:
            time_text: 原始时间文本
            
        Returns:
            datetime: 解析后的时间对象，或None
        """
        if not time_text:
            return None
        
        # 清理文本
        time_text = time_text.strip()
        
        # 尝试多种解析方式
        patterns = [
            # ISO 格式: 2024-11-03T12:34:56
            (r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', '%Y-%m-%dT%H:%M:%S'),
            # 标准格式: 2024-11-03 12:34:56 或 2024-11-03 12:34
            (r'(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?', None),  # 处理可选秒数
            # 知乎格式: 发布于 2024-12-27 10:59・广东 (无法解析具体时间)
            (r'发布于\s+(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})', '%Y-%m-%d %H:%M'),
            # 中文日期格式: 2024年12月27日 10:59
            (r'(\d{4})年(\d{2})月(\d{2})日\s+(\d{2}):(\d{2})', None),  # 需要特殊处理
            # 相对时间: 某时间前 (这种情况无法精准解析)
        ]
        
        for pattern, format_str in patterns:
            match = re.search(pattern, time_text)
            if match:
                try:
                    if format_str:
                        # 直接使用指定的格式
                        return datetime.strptime(match.group(0), format_str)
                    else:
                        # 需要特殊处理的格式
                        if '年' in time_text:
                            # 中文日期格式
                            year, month, day, hour, minute = match.groups()
                            return datetime(int(year), int(month), int(day), int(hour), int(minute))
                        else:
                            # 标准格式但可能没有秒数
                            groups = match.groups()
                            year, month, day, hour, minute = groups[:5]
                            second = int(groups[5]) if groups[5] else 0
                            return datetime(int(year), int(month), int(day), int(hour), int(minute), second)
                except Exception as e:
                    print(f"⚠️  解析时间格式失败: {str(e)}")
                    continue
        
        return None
    
    def _get_db_connection(self):
        """获取数据库连接"""
        if not self.db_config:
            raise Exception("未配置数据库信息")
        
        return pymysql.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            port=self.db_config.get('port', 3306),
            charset='utf8mb4'
        )
    
    def fetch_urls_from_db(self, limit=10):
        """
        从数据库获取文章URL列表
        
        Args:
            limit: 获取的文章数量
            
        Returns:
            list: URL列表，每个元素包含 (id, src_url)
        """
        try:
            connection = self._get_db_connection()
            cursor = connection.cursor(DictCursor)
            
            # 查询未爬取的文章（src_url不为空，且还未有src_content的）
            sql = "SELECT id, src_url FROM baoxianblog WHERE src_url IS NOT NULL AND src_url LIKE %s AND (src_content IS NULL OR src_content = '') LIMIT %s"
            
            cursor.execute(sql, ('%zhihu%', limit))
            results = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            print(f"✓ 从数据库获取了 {len(results)} 篇文章URL")
            return results
            
        except Exception as e:
            print(f"✗ 数据库查询失败: {str(e)}")
            raise
    
    def save_article_to_db(self, article_id, url, article_info):
        """
        将抓取的文章信息保存到数据库
        
        Args:
            article_id: 数据库中的文章ID
            url: 原始URL
            article_info: 抓取的文章信息字典
            
        Returns:
            bool: 是否保存成功
        """
        try:
            connection = self._get_db_connection()
            cursor = connection.cursor()
            
            # 获取HTML内容
            content_html = str(article_info['content'])
            content_size = len(content_html)
            
            # 解析发布时间 - 使用改进的时间解析器
            publish_time = None
            original_time_text = article_info['publish_time']
            
            if article_info['publish_time']:
                publish_time = self._parse_publish_time(article_info['publish_time'])
            
            # 准备更新数据
            update_query = """
            UPDATE baoxianblog 
            SET 
                src_title = %s,
                src_content = %s,
                dst_title = %s,
                dst_content = %s,
                src_user = %s,
                like_count = %s,
                src_published_time = %s,
                update_time = NOW(),
                from_source = 'zhihu'
            WHERE id = %s
            """
            
            cursor.execute(update_query, (
                article_info['title'],           # src_title - 来源标题
                content_html,                     # src_content - 来源内容（原文正文HTML）
                article_info['title'],           # dst_title - 目标标题
                content_html,                     # dst_content - 目标内容
                article_info['author'],           # src_user - 原文作者
                article_info['like_count'],       # like_count - 赞同数
                publish_time,                     # src_published_time - 原文发布时间
                article_id                        # id
            ))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # 输出详细的保存信息
            print(f"✓ 文章已保存到数据库 (ID: {article_id})")
            print(f"  ├─ 标题: {article_info['title'][:60]}{'...' if len(article_info['title']) > 60 else ''}")
            print(f"  ├─ 作者: {article_info['author'] or '（未找到）'}")
            print(f"  ├─ 赞同数: {article_info['like_count']}")
            
            if original_time_text:
                time_display = original_time_text[:50]  # 只显示前50个字符
                if publish_time:
                    time_display += f" → {publish_time.strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    time_display += " (无法解析具体时间)"
                print(f"  ├─ 发布时间: {time_display}")
            else:
                print(f"  ├─ 发布时间: （未找到）")
            
            print(f"  └─ 内容大小: {content_size} 字符")
            
            return True
            
        except Exception as e:
            print(f"✗ 保存到数据库失败: {str(e)}")
            return False
    
    def batch_crawl_and_save(self, limit=10):
        """
        批量抓取文章并保存到数据库
        
        Args:
            limit: 抓取的文章数量
        """
        print(f"\n{'='*70}")
        print(f"开始批量抓取知乎文章 (限制: {limit} 篇)")
        print(f"{'='*70}\n")
        
        # 从数据库获取URL列表
        articles = self.fetch_urls_from_db(limit)
        
        if not articles:
            print("✗ 没有可抓取的文章")
            return
        
        success_count = 0
        failed_count = 0
        
        for index, article in enumerate(articles, 1):
            article_id = article['id']
            url = article['src_url']
            
            print(f"\n[{index}/{len(articles)}] 正在处理: {url}")
            
            try:
                # 抓取文章
                article_info = self.fetch_article(url)
                
                # 保存到数据库
                if self.save_article_to_db(article_id, url, article_info):
                    success_count += 1
                else:
                    failed_count += 1
                
                # 随机延迟，避免被反爬虫拦截
                if index < len(articles):
                    delay = random.uniform(2, 5)
                    print(f"⏳ 等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  用户中断")
                break
            except Exception as e:
                print(f"✗ 抓取失败: {str(e)}")
                failed_count += 1
                # 失败后也延迟一下
                time.sleep(2)
        
        # 输出统计信息
        print(f"\n{'='*70}")
        print(f"抓取完成!")
        print(f"成功: {success_count} 篇")
        print(f"失败: {failed_count} 篇")
        print(f"总计: {len(articles)} 篇")
        print(f"{'='*70}\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 70)
        print("知乎文章抓取工具 - 升级版（支持数据库）")
        print("=" * 70)
        print("\n使用方法:")
        print("  # 单篇抓取模式")
        print("  python3 zhihu_crawler.py <URL> [输出文件] [--cookie COOKIE]")
        print("\n  # 批量抓取模式（从数据库）")
        print("  python3 zhihu_crawler.py --batch [数量] [--cookie COOKIE]")
        print("\n提示:")
        print("  - 可将 Cookie 保存到 cookie.txt 文件，程序会自动读取")
        print("  - 或使用 --cookie 参数指定 Cookie")
        print("\n示例:")
        print("  # 基础抓取")
        print("  python3 zhihu_crawler.py https://zhuanlan.zhihu.com/p/123456")
        print("\n  # 指定输出文件")
        print("  python3 zhihu_crawler.py https://zhuanlan.zhihu.com/p/123456 output.html")
        print("\n  # 使用命令行指定Cookie")
        print("  python3 zhihu_crawler.py https://zhuanlan.zhihu.com/p/123456 --cookie 'xxx'")
        print("\n  # 批量抓取10篇文章到数据库")
        print("  python3 zhihu_crawler.py --batch 10")
        print("\n获取Cookie的方法:")
        print("  1. 在浏览器中打开知乎并登录")
        print("  2. 按F12打开开发者工具，切换到Network标签")
        print("  3. 刷新页面，找到文章请求，复制Cookie值")
        print("  4. 保存到 cookie.txt 或使用 --cookie 参数")
        print("=" * 70)
        sys.exit(1)
    
    # 解析参数
    url = None
    output_file = None
    cookie = None
    batch_mode = False
    batch_limit = 10
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--batch':
            batch_mode = True
            if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith('--'):
                try:
                    batch_limit = int(sys.argv[i + 1])
                    i += 2
                    continue
                except ValueError:
                    pass
            i += 1
        elif arg == '--cookie':
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
    
    # 如果没有提供 Cookie，尝试从 cookie.txt 读取
    if not cookie:
        cookie_file = 'cookie.txt'
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_content = f.read().strip()
                    if cookie_content:
                        cookie = cookie_content
                        print(f"✓ 已从 {cookie_file} 读取 Cookie")
                    else:
                        print(f"⚠️  {cookie_file} 为空，请添加有效的 Cookie")
            except Exception as e:
                print(f"⚠️  读取 {cookie_file} 失败: {str(e)}")
        else:
            print(f"⚠️  未找到 {cookie_file}，请提供 --cookie 参数或创建 cookie.txt 文件")
    
    # 批量模式
    if batch_mode:
        db_config = {
            'host': '172.105.225.120',
            'user': 'root',
            'password': 'lnmp.org#25295',
            'database': 'wordpress',
            'port': 3306
        }
        
        crawler = ZhihuArticleCrawler(cookie=cookie, db_config=db_config)
        
        try:
            crawler.batch_crawl_and_save(batch_limit)
            print("\n✅ 批量抓取完成！")
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断")
            sys.exit(130)
        except Exception as e:
            print(f"\n✗ 错误: {str(e)}")
            sys.exit(1)
    
    # 单篇模式
    else:
        if not url:
            print("✗ 错误: 请提供URL")
            sys.exit(1)
        
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
                print("   请在 cookie.txt 中添加 Cookie 或使用 --cookie 参数")
            sys.exit(1)


if __name__ == '__main__':
    main()
