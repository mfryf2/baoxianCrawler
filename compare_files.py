#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比优化前后文件大小和内容的脚本
"""

import os
import sys
from pathlib import Path

def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

def get_file_stats(filepath):
    """获取文件统计信息"""
    if not os.path.exists(filepath):
        return None
    
    size = os.path.getsize(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = len(f.readlines())
    
    return {
        'size': size,
        'lines': lines,
        'formatted_size': format_size(size)
    }

def compare_files(file1, file2):
    """对比两个文件"""
    print("=" * 70)
    print("知乎文章爬虫优化效果对比")
    print("=" * 70)
    print()
    
    stats1 = get_file_stats(file1)
    stats2 = get_file_stats(file2)
    
    if not stats1:
        print(f"❌ 文件不存在: {file1}")
        return False
    
    if not stats2:
        print(f"❌ 文件不存在: {file2}")
        return False
    
    # 计算优化效果
    size_reduction = stats1['size'] - stats2['size']
    reduction_percent = (size_reduction / stats1['size']) * 100 if stats1['size'] > 0 else 0
    
    print(f"📊 文件对比统计")
    print("-" * 70)
    print(f"优化前文件: {file1}")
    print(f"  体积: {stats1['formatted_size']} ({stats1['size']} 字节)")
    print(f"  行数: {stats1['lines']} 行")
    print()
    print(f"优化后文件: {file2}")
    print(f"  体积: {stats2['formatted_size']} ({stats2['size']} 字节)")
    print(f"  行数: {stats2['lines']} 行")
    print()
    print(f"✨ 优化效果")
    print("-" * 70)
    print(f"  减少体积: {format_size(size_reduction)} ({reduction_percent:.1f}%)")
    print(f"  体积比例: {stats2['size'] / stats1['size'] * 100:.1f}%")
    print()
    
    # 分析文件内容
    with open(file1, 'r', encoding='utf-8') as f:
        content1 = f.read()
    
    with open(file2, 'r', encoding='utf-8') as f:
        content2 = f.read()
    
    # 计算包含的特定元素数
    emotion_css_count = content1.count('data-emotion-css')
    data_pid_count = content1.count('data-pid')
    css_class_count = content1.count('class="css-')
    
    print(f"🔍 移除的冗余内容")
    print("-" * 70)
    print(f"  Emotion CSS标签: {emotion_css_count} 个")
    print(f"  data-pid属性: {data_pid_count} 个")
    print(f"  css-xxxx类名: {css_class_count} 个")
    print()
    
    print(f"✅ 优化完成！")
    print("=" * 70)
    return True

if __name__ == '__main__':
    # 默认文件
    file_before = 'test_output.html'
    file_after = 'test_compressed.html'
    
    # 支持命令行参数
    if len(sys.argv) > 2:
        file_before = sys.argv[1]
        file_after = sys.argv[2]
    
    compare_files(file_before, file_after)
