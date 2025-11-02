#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookie获取辅助工具
帮助用户从浏览器中提取知乎Cookie
"""

import sys
import os


def print_instructions():
    """打印获取Cookie的详细说明"""
    print("=" * 70)
    print("知乎Cookie获取指南")
    print("=" * 70)
    print()
    
    print("【方法一：Chrome浏览器】")
    print("-" * 70)
    print("1. 打开Chrome浏览器，访问 https://www.zhihu.com")
    print("2. 登录你的知乎账号")
    print("3. 按 F12 键打开开发者工具")
    print("4. 点击顶部的 'Network'（网络）标签")
    print("5. 刷新页面（F5 或 Cmd+R）")
    print("6. 在左侧列表中点击任意请求（通常是第一个）")
    print("7. 在右侧找到 'Request Headers'（请求头）")
    print("8. 找到 'Cookie:' 这一行")
    print("9. 复制整个Cookie值（从 _zap 开始到最后）")
    print()
    
    print("【方法二：Safari浏览器】")
    print("-" * 70)
    print("1. 打开Safari，访问 https://www.zhihu.com 并登录")
    print("2. 菜单栏 → 开发 → 显示Web检查器（如果没有'开发'菜单，")
    print("   先到 偏好设置 → 高级 → 勾选'在菜单栏中显示开发菜单'）")
    print("3. 点击 '网络' 标签")
    print("4. 刷新页面")
    print("5. 点击任意请求，查看请求头中的Cookie")
    print()
    
    print("【方法三：Firefox浏览器】")
    print("-" * 70)
    print("1. 打开Firefox，访问 https://www.zhihu.com 并登录")
    print("2. 按 F12 打开开发者工具")
    print("3. 点击 '网络' 标签")
    print("4. 刷新页面")
    print("5. 点击任意请求，在右侧找到 'Cookie' 请求头")
    print()
    
    print("【Cookie示例】")
    print("-" * 70)
    print("_zap=xxx; d_c0=xxx; __snaker__id=xxx; _xsrf=xxx; ...")
    print()
    
    print("【重要提示】")
    print("-" * 70)
    print("⚠️  Cookie包含你的登录凭证，请勿分享给他人！")
    print("⚠️  Cookie会过期，如果抓取失败，请重新获取")
    print("⚠️  完整的Cookie通常很长（几百到几千字符）")
    print()
    
    print("【使用Cookie】")
    print("-" * 70)
    print("获取Cookie后，使用以下命令：")
    print()
    print("  # 单篇抓取")
    print("  python3 zhihu_crawler.py URL --cookie '你的Cookie'")
    print()
    print("  # 批量抓取")
    print("  python3 zhihu_crawler.py --batch urls.txt --cookie '你的Cookie'")
    print()
    print("=" * 70)


def validate_cookie(cookie):
    """
    验证Cookie格式
    
    Args:
        cookie: Cookie字符串
        
    Returns:
        tuple: (is_valid, message)
    """
    if not cookie or len(cookie.strip()) == 0:
        return False, "Cookie为空"
    
    cookie = cookie.strip()
    
    # 检查长度
    if len(cookie) < 50:
        return False, "Cookie太短，可能不完整"
    
    # 检查是否包含关键字段
    required_fields = ['d_c0']
    missing_fields = [field for field in required_fields if field not in cookie]
    
    if missing_fields:
        return False, f"Cookie缺少关键字段: {', '.join(missing_fields)}"
    
    # 检查格式
    if '=' not in cookie:
        return False, "Cookie格式不正确，应包含 key=value 格式"
    
    return True, "Cookie格式正确"


def interactive_mode():
    """交互式获取和验证Cookie"""
    print("\n" + "=" * 70)
    print("Cookie验证工具")
    print("=" * 70)
    print()
    print("请粘贴你的Cookie（粘贴后按回车）：")
    print("（提示：Cookie通常很长，可能需要滚动查看）")
    print()
    
    try:
        cookie = input("> ").strip()
        
        if not cookie:
            print("\n❌ 未输入Cookie")
            return
        
        print("\n正在验证...")
        is_valid, message = validate_cookie(cookie)
        
        if is_valid:
            print(f"\n✅ {message}")
            print(f"\nCookie长度: {len(cookie)} 字符")
            
            # 显示Cookie的前后部分
            preview_len = 50
            if len(cookie) > preview_len * 2:
                preview = f"{cookie[:preview_len]}...{cookie[-preview_len:]}"
            else:
                preview = cookie
            
            print(f"Cookie预览: {preview}")
            
            # 保存到文件
            save = input("\n是否保存到文件？(y/n): ").strip().lower()
            if save == 'y':
                filename = 'cookie.txt'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(cookie)
                print(f"\n✅ Cookie已保存到: {filename}")
                print("\n使用方法:")
                print(f"  python3 zhihu_crawler.py URL --cookie \"$(cat {filename})\"")
        else:
            print(f"\n❌ {message}")
            print("\n请检查：")
            print("1. 是否复制了完整的Cookie")
            print("2. 是否在登录状态下获取的Cookie")
            print("3. Cookie中是否包含 d_c0 等关键字段")
    
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print_instructions()
        elif sys.argv[1] in ['-v', '--validate', 'validate']:
            interactive_mode()
        else:
            print("未知选项")
            print("\n使用方法:")
            print("  python3 get_cookie_helper.py          # 显示获取说明")
            print("  python3 get_cookie_helper.py -v       # 验证Cookie")
    else:
        print_instructions()
        print("\n💡 提示：运行 'python3 get_cookie_helper.py -v' 可以验证你的Cookie")


if __name__ == '__main__':
    main()
