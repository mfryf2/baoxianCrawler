#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流程演示：从获取作者文章列表到批量抓取文章内容
"""

import os
import sys
import time
import subprocess
from datetime import datetime


def run_command(command, description=""):
    """运行命令并显示结果"""
    if description:
        print(f"\n{'='*60}")
        print(f"步骤: {description}")
        print(f"{'='*60}")
        print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 命令执行失败: {str(e)}")
        return False


def complete_workflow_demo():
    """完整工作流程演示"""
    print("🎯 知乎作者文章抓取完整工作流程演示")
    print("=" * 80)
    
    # 配置参数
    author_url = "https://www.zhihu.com/org/nai-ba-bao-25/posts"
    max_articles = 5  # 演示用，实际可以设置更大
    max_crawl = 3     # 演示抓取前3篇文章
    
    print(f"目标作者: {author_url}")
    print(f"获取文章数: {max_articles}")
    print(f"抓取文章数: {max_crawl}")
    
    # 检查Cookie
    if not os.path.exists('cookie.txt'):
        print("\n⚠️  警告: 未找到 cookie.txt 文件")
        print("建议先运行: python3 get_cookie_helper.py")
        
        response = input("\n是否继续演示？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return False
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 步骤1: 获取作者文章列表
    step1_success = run_command(
        f'python3 zhihu_author_crawler.py "{author_url}" --max-articles {max_articles} --format json --output demo_{timestamp}',
        "1. 获取作者文章列表"
    )
    
    if not step1_success:
        print("❌ 步骤1失败，无法继续")
        return False
    
    # 查找生成的JSON文件
    json_file = f"demo_{timestamp}.json"
    if not os.path.exists(json_file):
        print(f"❌ 未找到生成的JSON文件: {json_file}")
        return False
    
    time.sleep(1)
    
    # 步骤2: 从JSON提取URL列表
    step2_success = run_command(
        f'python3 extract_urls_from_json.py {json_file} --output demo_urls_{timestamp}.txt --max-urls {max_crawl}',
        "2. 提取文章URL列表"
    )
    
    if not step2_success:
        print("❌ 步骤2失败，无法继续")
        return False
    
    urls_file = f"demo_urls_{timestamp}.txt"
    if not os.path.exists(urls_file):
        print(f"❌ 未找到生成的URL文件: {urls_file}")
        return False
    
    time.sleep(1)
    
    # 步骤3: 批量抓取文章内容
    cookie_param = ""
    if os.path.exists('cookie.txt'):
        cookie_param = "--cookie $(cat cookie.txt)"
    
    step3_success = run_command(
        f'python3 zhihu_crawler.py --batch {urls_file} --output-dir demo_articles_{timestamp} --workers 2 --delay 1.0 {cookie_param}',
        "3. 批量抓取文章内容"
    )
    
    # 步骤4: 显示结果总结
    print(f"\n{'='*60}")
    print("4. 工作流程总结")
    print(f"{'='*60}")
    
    # 统计生成的文件
    generated_files = []
    
    # JSON文件
    if os.path.exists(json_file):
        size = os.path.getsize(json_file)
        generated_files.append(f"📄 {json_file} ({size} bytes) - 文章列表数据")
    
    # URL文件
    if os.path.exists(urls_file):
        with open(urls_file, 'r', encoding='utf-8') as f:
            url_count = len(f.readlines())
        generated_files.append(f"🔗 {urls_file} ({url_count} URLs) - 文章链接列表")
    
    # 文章目录
    articles_dir = f"demo_articles_{timestamp}"
    if os.path.exists(articles_dir):
        article_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]
        generated_files.append(f"📁 {articles_dir}/ ({len(article_files)} 篇文章) - 抓取的文章内容")
    
    if generated_files:
        print("✅ 生成的文件:")
        for file_info in generated_files:
            print(f"  {file_info}")
    else:
        print("❌ 未生成任何文件")
    
    # 显示使用建议
    print(f"\n💡 后续操作建议:")
    print(f"1. 查看文章列表: cat {json_file}")
    print(f"2. 查看URL列表: cat {urls_file}")
    if os.path.exists(articles_dir):
        print(f"3. 查看抓取的文章: ls {articles_dir}/")
        print(f"4. 在浏览器中打开文章: open {articles_dir}/*.html")
    
    # 清理选项
    print(f"\n🧹 清理演示文件:")
    print(f"rm -f demo_{timestamp}.* && rm -rf demo_articles_{timestamp}/")
    
    return True


def main():
    """主函数"""
    print("知乎作者文章抓取 - 完整工作流程演示")
    print("=" * 80)
    print("\n这个演示将展示完整的工作流程:")
    print("1. 获取作者文章列表")
    print("2. 提取文章URL")
    print("3. 批量抓取文章内容")
    print("4. 查看结果")
    
    response = input("\n是否开始演示？(y/n): ").strip().lower()
    if response != 'y':
        print("已取消")
        return
    
    try:
        success = complete_workflow_demo()
        
        if success:
            print(f"\n🎉 工作流程演示完成！")
            print(f"\n📚 更多使用方法:")
            print(f"- 查看详细指南: cat AUTHOR_CRAWLER_GUIDE.md")
            print(f"- 运行测试: python3 test_author_crawler.py")
            print(f"- 查看示例: python3 author_crawler_example.py")
        else:
            print(f"\n⚠️  演示过程中遇到问题，请检查错误信息")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {str(e)}")


if __name__ == '__main__':
    main()