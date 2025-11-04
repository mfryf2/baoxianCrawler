#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知乎作者文章列表抓取工具
获取指定作者的所有文章标题和URL，并写入数据库
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
import sys
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
import pymysql
from pymysql.cursors import DictCursor


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, host='172.105.225.120', user='root', password='lnmp.org#25295', 
                 database='wordpress', port=3306):
        """
        初始化数据库连接
        
        Args:
            host: 数据库主机
            user: 数据库用户
            password: 数据库密码
            database: 数据库名
            port: 数据库端口
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4'
            )
            print("✓ 数据库连接成功")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("✓ 数据库连接已关闭")
    
    def insert_article(self, article, author_info):
        """
        插入文章到数据库
        
        Args:
            article: 文章信息字典
            author_info: 作者信息字典
            
        Returns:
            bool: 插入是否成功
        """
        if not self.connection:
            print("❌ 数据库未连接")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # 检查URL是否已存在
                check_sql = "SELECT id FROM baoxianblog WHERE src_url = %s"
                cursor.execute(check_sql, (article['url'],))
                if cursor.fetchone():
                    print(f"⚠️  URL已存在，跳过: {article['url']}")
                    return False
                
                # 准备插入数据
                insert_sql = """
                    INSERT INTO baoxianblog 
                    (src_url, src_title, src_content, published_user, src_user, 
                     create_time, src_published_time, like_count, collect_count, 
                     from_source, isPublish)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # 使用摘要作为内容，如果没有则使用空字符串
                content = article.get('excerpt', '')[:500] if article.get('excerpt') else ''
                
                # 获取发布时间
                published_time = article.get('created_time', '')
                
                values = (
                    article['url'],
                    article['title'],
                    content,
                    author_info['name'],
                    author_info['name'],
                    datetime.now(),
                    published_time if published_time else None,
                    article.get('voteup_count', -1),
                    -1,  # collect_count 默认为-1
                    'zhihu',
                    0  # isPublish 默认为0（未发布）
                )
                
                cursor.execute(insert_sql, values)
                self.connection.commit()
                print(f"✓ 成功保存: {article['title'][:50]}")
                return True
                
        except Exception as e:
            print(f"❌ 插入数据库失败: {str(e)}")
            self.connection.rollback()
            return False
    
    def insert_articles_batch(self, articles, author_info):
        """
        批量插入文章到数据库
        
        Args:
            articles: 文章列表
            author_info: 作者信息字典
            
        Returns:
            dict: 包含成功和失败计数的统计信息
        """
        if not self.connection:
            print("❌ 数据库未连接")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        try:
            with self.connection.cursor() as cursor:
                for i, article in enumerate(articles, 1):
                    try:
                        # 检查URL是否已存在
                        check_sql = "SELECT id FROM baoxianblog WHERE src_url = %s"
                        cursor.execute(check_sql, (article['url'],))
                        if cursor.fetchone():
                            stats['skipped'] += 1
                            continue
                        
                        # 准备插入数据
                        insert_sql = """
                            INSERT INTO baoxianblog 
                            (src_url, src_title, src_content, published_user, src_user, 
                             create_time, src_published_time, like_count, collect_count, 
                             from_source, isPublish)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # 使用摘要作为内容
                        content = article.get('excerpt', '')[:500] if article.get('excerpt') else ''
                        published_time = article.get('created_time', '')
                        
                        values = (
                            article['url'],
                            article['title'],
                            content,
                            author_info['name'],
                            author_info['name'],
                            datetime.now(),
                            published_time if published_time else None,
                            article.get('voteup_count', -1),
                            -1,  # collect_count 默认为-1
                            'zhihu',
                            0
                        )
                        
                        cursor.execute(insert_sql, values)
                        stats['success'] += 1
                        
                        if i % 10 == 0:
                            self.connection.commit()
                            print(f"  已处理 {i}/{len(articles)} 篇文章...")
                    
                    except Exception as e:
                        stats['failed'] += 1
                        print(f"⚠️  处理第 {i} 篇文章失败: {str(e)}")
                        continue
                
                # 最后提交一次
                self.connection.commit()
        
        except Exception as e:
            print(f"❌ 批量插入失败: {str(e)}")
            self.connection.rollback()
        
        return stats


class ZhihuAuthorCrawler:
    def __init__(self, cookie=None, db_manager=None):
        """
        初始化作者爬虫
        
        Args:
            cookie: 可选的cookie字符串，用于绕过登录限制
            db_manager: 可选的数据库管理器
        """
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
        self.db_manager = db_manager
        
        # API相关的headers
        self.api_headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.zhihu.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'x-requested-with': 'fetch',
        }
    
    def _get_headers(self, is_api=False):
        """获取请求头"""
        if is_api:
            headers = self.api_headers.copy()
        else:
            headers = self.base_headers.copy()
        
        headers['User-Agent'] = random.choice(self.user_agents)
        
        if self.cookie:
            headers['Cookie'] = self.cookie
        
        return headers
    
    def _make_request(self, url, max_retries=5, is_api=False):
        """
        发送HTTP请求，带智能重试
        
        Args:
            url: 目标URL
            max_retries: 最大重试次数
            is_api: 是否是API请求
            
        Returns:
            requests.Response: 响应对象
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️  等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                
                headers = self._get_headers(is_api=is_api)
                
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=20,
                    allow_redirects=True
                )
                
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
    
    def _extract_author_info(self, author_url):
        """
        从作者页面URL提取作者信息
        
        Args:
            author_url: 作者页面URL
            
        Returns:
            dict: 包含作者信息的字典
        """
        print(f"正在获取作者信息: {author_url}")
        
        response = self._make_request(author_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取作者名称
        author_name = "未知作者"
        name_selectors = [
            ('h1', {'class': 'ProfileHeader-title'}),
            ('span', {'class': 'ProfileHeader-name'}),
            ('h1', {}),
        ]
        
        for tag, attrs in name_selectors:
            name_element = soup.find(tag, attrs)
            if name_element:
                author_name = name_element.get_text().strip()
                break
        
        # 提取作者ID（从URL中）
        author_id = ""
        if '/org/' in author_url:
            # 机构账号
            match = re.search(r'/org/([^/]+)', author_url)
            if match:
                author_id = match.group(1)
        else:
            # 个人账号
            match = re.search(r'/people/([^/]+)', author_url)
            if match:
                author_id = match.group(1)
        
        # 尝试从页面中提取文章总数
        total_posts = 0
        post_count_patterns = [
            r'(\d+)\s*篇文章',
            r'(\d+)\s*个回答',
            r'发表了\s*(\d+)\s*篇文章',
        ]
        
        page_text = soup.get_text()
        for pattern in post_count_patterns:
            match = re.search(pattern, page_text)
            if match:
                total_posts = int(match.group(1))
                break
        
        return {
            'name': author_name,
            'id': author_id,
            'url': author_url,
            'total_posts': total_posts
        }
    
    def _get_api_url(self, author_url):
        """
        根据作者页面URL构建API URL
        
        Args:
            author_url: 作者页面URL
            
        Returns:
            str: API URL
        """
        if '/org/' in author_url:
            # 机构账号 - 尝试多种可能的API端点
            match = re.search(r'/org/([^/]+)', author_url)
            if match:
                org_id = match.group(1)
                # 返回多个可能的API URL供尝试
                return [
                    f"https://www.zhihu.com/api/v4/members/{org_id}/articles",
                    f"https://zhuanlan.zhihu.com/api/columns/{org_id}/articles",
                    f"https://www.zhihu.com/api/v4/org/{org_id}/articles"
                ]
        else:
            # 个人账号
            match = re.search(r'/people/([^/]+)', author_url)
            if match:
                user_id = match.group(1)
                return [
                    f"https://www.zhihu.com/api/v4/members/{user_id}/articles",
                    f"https://zhuanlan.zhihu.com/api/columns/{user_id}/articles"
                ]
        
        raise Exception("无法识别的作者URL格式")
    
    def fetch_author_articles(self, author_url, max_articles=None, delay=1.0):
        """
        获取作者的所有文章
        
        Args:
            author_url: 作者页面URL
            max_articles: 最大文章数量限制，None表示获取所有
            delay: 请求间隔时间（秒）
            
        Returns:
            dict: 包含作者信息和文章列表的字典
        """
        # 获取作者信息
        author_info = self._extract_author_info(author_url)
        print(f"✓ 作者: {author_info['name']}")
        if author_info['total_posts'] > 0:
            print(f"✓ 预计文章数: {author_info['total_posts']}")
        
        # 构建API URL列表
        try:
            api_urls = self._get_api_url(author_url)
        except Exception as e:
            print(f"❌ {str(e)}")
            return None
        
        articles = []
        offset = 0
        limit = 20  # 每页文章数
        page = 1
        working_api_url = None
        
        print(f"\n开始获取文章列表...")
        
        # 首先找到可用的API端点
        if not working_api_url:
            print("正在寻找可用的API端点...")
            for api_url in api_urls:
                try:
                    params = {
                        'limit': 5,  # 测试时只获取少量数据
                        'offset': 0,
                        'sort_by': 'created'
                    }
                    test_url = api_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
                    print(f"  尝试: {api_url}")
                    
                    response = self._make_request(test_url, is_api=True)
                    data = response.json()
                    
                    if 'data' in data and isinstance(data['data'], list):
                        working_api_url = api_url
                        print(f"  ✅ 找到可用API: {api_url}")
                        break
                    else:
                        print(f"  ❌ API响应格式不正确")
                        
                except Exception as e:
                    print(f"  ❌ API不可用: {str(e)}")
                    continue
            
            if not working_api_url:
                print("❌ 未找到可用的API端点，尝试从页面HTML解析...")
                return self._parse_from_html(author_url, author_info, max_articles)
        
        while True:
            try:
                # 构建分页API URL
                params = {
                    'limit': limit,
                    'offset': offset,
                    'sort_by': 'created'
                }
                
                current_url = working_api_url + '?' + '&'.join([f"{k}={v}" for k, v in params.items()])
                
                print(f"正在获取第 {page} 页 (已获取 {len(articles)} 篇)...")
                
                response = self._make_request(current_url, is_api=True)
                
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    print("❌ API响应不是有效的JSON格式")
                    break
                
                # 检查API响应格式
                if 'data' not in data:
                    print("❌ API响应格式异常")
                    break
                
                page_articles = data['data']
                
                if not page_articles:
                    print("✓ 已获取所有文章")
                    break
                
                # 处理当前页的文章
                for article in page_articles:
                    try:
                        article_info = {
                            'title': article.get('title', '无标题'),
                            'url': article.get('url', ''),
                            'id': article.get('id', ''),
                            'created_time': article.get('created_time', ''),
                            'updated_time': article.get('updated_time', ''),
                            'excerpt': article.get('excerpt', ''),
                            'voteup_count': article.get('voteup_count', 0),
                            'comment_count': article.get('comment_count', 0),
                        }
                        
                        # 格式化时间
                        if article_info['created_time']:
                            try:
                                timestamp = int(article_info['created_time'])
                                article_info['created_time'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                        
                        articles.append(article_info)
                        
                        # 检查是否达到最大数量限制
                        if max_articles and len(articles) >= max_articles:
                            print(f"✓ 已达到最大文章数量限制: {max_articles}")
                            break
                            
                    except Exception as e:
                        print(f"⚠️  处理文章信息时出错: {str(e)}")
                        continue
                
                # 检查是否还有更多文章
                if len(page_articles) < limit:
                    print("✓ 已获取所有文章")
                    break
                
                # 检查是否达到最大数量限制
                if max_articles and len(articles) >= max_articles:
                    break
                
                # 准备下一页
                offset += limit
                page += 1
                
                # 添加延迟避免请求过快
                if delay > 0:
                    time.sleep(delay)
                
            except KeyboardInterrupt:
                print("\n⚠️  用户中断，保存已获取的文章...")
                break
            except Exception as e:
                print(f"❌ 获取第 {page} 页时出错: {str(e)}")
                break
        
        result = {
            'author': author_info,
            'articles': articles,
            'total_fetched': len(articles),
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"\n✅ 获取完成！共获取 {len(articles)} 篇文章")
        
        # 如果提供了数据库管理器，将数据保存到数据库
        if self.db_manager and articles:
            print("\n" + "=" * 80)
            print("开始将数据保存到数据库...")
            print("=" * 80)
            
            stats = self.db_manager.insert_articles_batch(articles, author_info)
            result['db_stats'] = stats
            
            print(f"\n数据库保存统计:")
            print(f"  成功: {stats['success']} 篇")
            print(f"  失败: {stats['failed']} 篇")
            print(f"  跳过: {stats['skipped']} 篇 (已存在)")
        
        return result
    
    def _parse_from_html(self, author_url, author_info, max_articles=None):
        """
        从页面HTML解析文章列表（备用方案）
        
        Args:
            author_url: 作者页面URL
            author_info: 作者信息
            max_articles: 最大文章数量限制
            
        Returns:
            dict: 包含作者信息和文章列表的字典
        """
        print("使用HTML解析方法获取文章列表...")
        
        articles = []
        page = 1
        
        try:
            # 获取第一页
            response = self._make_request(author_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找文章链接的多种选择器
            article_selectors = [
                'a[href*="/p/"]',  # 专栏文章
                'a[href*="/answer/"]',  # 回答
                '.ContentItem-title a',  # 内容项标题
                '.Post-Title a',  # 文章标题
                '.ArticleItem-title a',  # 文章项标题
            ]
            
            found_articles = []
            
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"  找到 {len(elements)} 个链接 (选择器: {selector})")
                    found_articles.extend(elements)
            
            # 去重并处理文章链接
            seen_urls = set()
            
            for element in found_articles:
                try:
                    href = element.get('href', '')
                    if not href:
                        continue
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        full_url = 'https://www.zhihu.com' + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # 只处理文章URL，跳过其他类型
                    if '/p/' not in full_url and '/answer/' not in full_url:
                        continue
                    
                    if full_url in seen_urls:
                        continue
                    
                    seen_urls.add(full_url)
                    
                    # 提取标题
                    title = element.get_text().strip()
                    if not title or len(title) < 3:
                        # 尝试从父元素获取标题
                        parent = element.parent
                        if parent:
                            title = parent.get_text().strip()
                    
                    if title and len(title) >= 3:
                        article_info = {
                            'title': title,
                            'url': full_url,
                            'id': self._extract_id_from_url(full_url),
                            'created_time': '',
                            'updated_time': '',
                            'excerpt': '',
                            'voteup_count': 0,
                            'comment_count': 0,
                        }
                        
                        articles.append(article_info)
                        
                        # 检查是否达到最大数量限制
                        if max_articles and len(articles) >= max_articles:
                            break
                            
                except Exception as e:
                    print(f"⚠️  处理文章链接时出错: {str(e)}")
                    continue
            
            print(f"✅ 从HTML解析获取到 {len(articles)} 篇文章")
            
            # 尝试获取更多页面（如果有分页）
            if len(articles) < (max_articles or 100):
                print("尝试获取更多页面...")
                # 这里可以添加分页逻辑，但知乎的分页通常是动态加载的
                # 所以HTML解析方法主要获取第一页的内容
            
        except Exception as e:
            print(f"❌ HTML解析失败: {str(e)}")
        
        result = {
            'author': author_info,
            'articles': articles,
            'total_fetched': len(articles),
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    
    def _extract_id_from_url(self, url):
        """从URL中提取文章ID"""
        try:
            if '/p/' in url:
                match = re.search(r'/p/(\d+)', url)
                if match:
                    return match.group(1)
            elif '/answer/' in url:
                match = re.search(r'/answer/(\d+)', url)
                if match:
                    return match.group(1)
        except:
            pass
        return ''
    
    def save_to_json(self, data, output_file=None):
        """
        保存数据到JSON文件
        
        Args:
            data: 要保存的数据
            output_file: 输出文件名
            
        Returns:
            str: 输出文件路径
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            author_name = data['author']['name']
            safe_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name[:30]  # 限制文件名长度
            output_file = f"{safe_name}_articles_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 数据已保存到: {output_file}")
        return output_file
    
    def save_to_txt(self, data, output_file=None):
        """
        保存数据到文本文件
        
        Args:
            data: 要保存的数据
            output_file: 输出文件名
            
        Returns:
            str: 输出文件路径
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            author_name = data['author']['name']
            safe_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name[:30]  # 限制文件名长度
            output_file = f"{safe_name}_articles_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入作者信息
            f.write("=" * 80 + "\n")
            f.write(f"作者信息\n")
            f.write("=" * 80 + "\n")
            f.write(f"作者名称: {data['author']['name']}\n")
            f.write(f"作者ID: {data['author']['id']}\n")
            f.write(f"作者页面: {data['author']['url']}\n")
            f.write(f"获取时间: {data['fetch_time']}\n")
            f.write(f"文章总数: {data['total_fetched']}\n")
            f.write("\n")
            
            # 写入文章列表
            f.write("=" * 80 + "\n")
            f.write(f"文章列表 (共 {len(data['articles'])} 篇)\n")
            f.write("=" * 80 + "\n")
            
            for i, article in enumerate(data['articles'], 1):
                f.write(f"\n{i:4d}. {article['title']}\n")
                f.write(f"      URL: {article['url']}\n")
                if article['created_time']:
                    f.write(f"      发布时间: {article['created_time']}\n")
                if article['voteup_count'] > 0:
                    f.write(f"      点赞数: {article['voteup_count']}\n")
                if article['comment_count'] > 0:
                    f.write(f"      评论数: {article['comment_count']}\n")
                if article['excerpt']:
                    excerpt = article['excerpt'][:100] + "..." if len(article['excerpt']) > 100 else article['excerpt']
                    f.write(f"      摘要: {excerpt}\n")
        
        print(f"✓ 文本文件已保存到: {output_file}")
        return output_file
    
    def save_to_csv(self, data, output_file=None):
        """
        保存数据到CSV文件
        
        Args:
            data: 要保存的数据
            output_file: 输出文件名
            
        Returns:
            str: 输出文件路径
        """
        import csv
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            author_name = data['author']['name']
            safe_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name[:30]  # 限制文件名长度
            output_file = f"{safe_name}_articles_{timestamp}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                '序号', '标题', 'URL', '文章ID', '发布时间', 
                '点赞数', '评论数', '摘要'
            ])
            
            # 写入文章数据
            for i, article in enumerate(data['articles'], 1):
                writer.writerow([
                    i,
                    article['title'],
                    article['url'],
                    article['id'],
                    article['created_time'],
                    article['voteup_count'],
                    article['comment_count'],
                    article['excerpt']
                ])
        
        print(f"✓ CSV文件已保存到: {output_file}")
        return output_file


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 80)
        print("知乎作者文章列表抓取工具")
        print("=" * 80)
        print("\n使用方法:")
        print("  python3 zhihu_author_crawler.py <作者URL> [选项]")
        print("\n选项:")
        print("  --max-articles N    最大文章数量限制")
        print("  --delay N          请求间隔时间（秒，默认1.0）")
        print("  --format FORMAT    输出格式: json, txt, csv, all（默认all）")
        print("  --output FILE      输出文件名前缀")
        print("  --cookie COOKIE    Cookie字符串")
        print("\n示例:")
        print("  # 获取所有文章")
        print("  python3 zhihu_author_crawler.py https://www.zhihu.com/org/nai-ba-bao-25/posts")
        print("\n  # 限制获取100篇文章")
        print("  python3 zhihu_author_crawler.py https://www.zhihu.com/org/nai-ba-bao-25/posts --max-articles 100")
        print("\n  # 只保存为JSON格式")
        print("  python3 zhihu_author_crawler.py https://www.zhihu.com/org/nai-ba-bao-25/posts --format json")
        print("\n  # 使用Cookie")
        print("  python3 zhihu_author_crawler.py https://www.zhihu.com/org/nai-ba-bao-25/posts --cookie 'xxx'")
        print("\n支持的URL格式:")
        print("  - 机构账号: https://www.zhihu.com/org/机构ID/posts")
        print("  - 个人账号: https://www.zhihu.com/people/用户ID/posts")
        print("=" * 80)
        sys.exit(1)
    
    # 解析参数
    author_url = sys.argv[1]
    max_articles = None
    delay = 1.0
    output_format = 'all'
    output_prefix = None
    cookie = None
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--max-articles':
            if i + 1 < len(sys.argv):
                max_articles = int(sys.argv[i + 1])
                i += 2
            else:
                print("✗ 错误: --max-articles 需要提供数量")
                sys.exit(1)
        elif arg == '--delay':
            if i + 1 < len(sys.argv):
                delay = float(sys.argv[i + 1])
                i += 2
            else:
                print("✗ 错误: --delay 需要提供时间")
                sys.exit(1)
        elif arg == '--format':
            if i + 1 < len(sys.argv):
                output_format = sys.argv[i + 1]
                if output_format not in ['json', 'txt', 'csv', 'all']:
                    print("✗ 错误: 格式必须是 json, txt, csv 或 all")
                    sys.exit(1)
                i += 2
            else:
                print("✗ 错误: --format 需要提供格式")
                sys.exit(1)
        elif arg == '--output':
            if i + 1 < len(sys.argv):
                output_prefix = sys.argv[i + 1]
                i += 2
            else:
                print("✗ 错误: --output 需要提供文件名前缀")
                sys.exit(1)
        elif arg == '--cookie':
            if i + 1 < len(sys.argv):
                cookie = sys.argv[i + 1]
                i += 2
            else:
                print("✗ 错误: --cookie 需要提供Cookie值")
                sys.exit(1)
        else:
            print(f"✗ 错误: 未知选项 {arg}")
            sys.exit(1)
    
    # 检查Cookie
    if not cookie and os.path.exists('cookie.txt'):
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
        print("✓ 已从 cookie.txt 加载Cookie")
    
    if not cookie:
        print("⚠️  警告: 未提供Cookie，可能会遇到访问限制")
        print("建议先运行: python3 get_cookie_helper.py")
    
    # 创建数据库管理器实例
    db_manager = DatabaseManager()
    if not db_manager.connect():
        print("❌ 无法连接数据库，退出程序。")
        sys.exit(1)
    
    # 创建爬虫实例
    crawler = ZhihuAuthorCrawler(cookie=cookie, db_manager=db_manager)
    
    try:
        print("=" * 80)
        print("开始抓取作者文章列表")
        print("=" * 80)
        
        # 获取文章数据
        data = crawler.fetch_author_articles(
            author_url, 
            max_articles=max_articles, 
            delay=delay
        )
        
        if not data:
            print("❌ 获取失败")
            sys.exit(1)
        
        print("\n" + "=" * 80)
        print("保存数据")
        print("=" * 80)
        
        # 保存数据
        if output_format == 'all':
            crawler.save_to_json(data, f"{output_prefix}.json" if output_prefix else None)
            crawler.save_to_txt(data, f"{output_prefix}.txt" if output_prefix else None)
            crawler.save_to_csv(data, f"{output_prefix}.csv" if output_prefix else None)
        elif output_format == 'json':
            crawler.save_to_json(data, f"{output_prefix}.json" if output_prefix else None)
        elif output_format == 'txt':
            crawler.save_to_txt(data, f"{output_prefix}.txt" if output_prefix else None)
        elif output_format == 'csv':
            crawler.save_to_csv(data, f"{output_prefix}.csv" if output_prefix else None)
        
        print(f"\n🎉 任务完成！共获取 {data['total_fetched']} 篇文章")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        if '403' in str(e) or 'Cookie' in str(e):
            print("\n💡 提示: 需要提供有效的Cookie")
            print("   运行 'python3 get_cookie_helper.py' 查看如何获取Cookie")
        sys.exit(1)
    finally:
        db_manager.disconnect()


if __name__ == '__main__':
    main()