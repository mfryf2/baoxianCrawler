#!/bin/bash
# 知乎文章抓取工具 - 完整使用示例

echo "=========================================="
echo "知乎文章抓取工具 - 使用示例"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 步骤1: 获取Cookie
echo -e "${YELLOW}步骤1: 获取Cookie${NC}"
echo "运行以下命令查看如何获取Cookie："
echo "  python3 get_cookie_helper.py"
echo ""
echo "或使用交互式验证："
echo "  python3 get_cookie_helper.py -v"
echo ""
read -p "按回车继续..."
echo ""

# 步骤2: 单篇抓取示例
echo -e "${YELLOW}步骤2: 单篇抓取示例${NC}"
echo "命令："
echo '  python3 zhihu_crawler.py "https://zhuanlan.zhihu.com/p/1967253690982335635" --cookie "你的Cookie"'
echo ""
read -p "是否执行单篇抓取测试？(y/n): " choice
if [ "$choice" = "y" ]; then
    if [ -f "cookie.txt" ]; then
        COOKIE=$(cat cookie.txt)
        python3 zhihu_crawler.py "https://zhuanlan.zhihu.com/p/1967253690982335635" --cookie "$COOKIE"
    else
        echo -e "${RED}错误: 未找到 cookie.txt 文件${NC}"
        echo "请先运行: python3 get_cookie_helper.py -v"
    fi
fi
echo ""

# 步骤3: 创建URL列表
echo -e "${YELLOW}步骤3: 创建URL列表${NC}"
echo "创建 urls.txt 文件，每行一个URL："
cat > urls_demo.txt << 'EOF'
# 知乎文章URL列表
https://zhuanlan.zhihu.com/p/1967253690982335635
# 在下面添加更多URL
EOF

echo -e "${GREEN}✓ 已创建示例文件: urls_demo.txt${NC}"
echo ""

# 步骤4: 批量抓取示例
echo -e "${YELLOW}步骤4: 批量抓取示例${NC}"
echo "基础批量抓取："
echo '  python3 zhihu_crawler.py --batch urls.txt --cookie "你的Cookie"'
echo ""
echo "高性能配置："
echo '  python3 zhihu_crawler.py --batch urls.txt \'
echo '      --cookie "你的Cookie" \'
echo '      --workers 10 \'
echo '      --delay 0.5 \'
echo '      --output-dir articles'
echo ""
read -p "是否执行批量抓取测试？(y/n): " choice
if [ "$choice" = "y" ]; then
    if [ -f "cookie.txt" ]; then
        COOKIE=$(cat cookie.txt)
        python3 zhihu_crawler.py --batch urls_demo.txt \
            --cookie "$COOKIE" \
            --workers 2 \
            --delay 1.0 \
            --output-dir demo_output
    else
        echo -e "${RED}错误: 未找到 cookie.txt 文件${NC}"
    fi
fi
echo ""

# 步骤5: 查看结果
echo -e "${YELLOW}步骤5: 查看结果${NC}"
echo "抓取的文章保存在："
echo "  - 单篇: 当前目录"
echo "  - 批量: demo_output/ 目录"
echo ""
echo "失败的URL保存在:"
echo "  demo_output/failed_urls.txt"
echo ""

# 步骤6: 高级用法
echo -e "${YELLOW}步骤6: 高级用法${NC}"
echo ""
echo "1. 测试功能："
echo "   python3 test_crawler.py"
echo ""
echo "2. 不同性能配置："
echo "   # 保守模式（最稳定）"
echo "   python3 zhihu_crawler.py --batch urls.txt --workers 3 --delay 2.0"
echo ""
echo "   # 推荐模式（平衡）"
echo "   python3 zhihu_crawler.py --batch urls.txt --workers 5 --delay 1.0"
echo ""
echo "   # 高速模式（需要好的Cookie）"
echo "   python3 zhihu_crawler.py --batch urls.txt --workers 10 --delay 0.5"
echo ""

echo "=========================================="
echo -e "${GREEN}示例完成！${NC}"
echo "=========================================="
echo ""
echo "更多信息请查看："
echo "  - README.md - 完整文档"
echo "  - 高性能批量抓取指南.md - 性能优化指南"
echo "  - 快速开始.md - 快速入门"
echo ""
