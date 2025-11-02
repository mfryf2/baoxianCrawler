#!/bin/bash
# 简单的批量抓取脚本
# 使用循环方式批量抓取知乎文章

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0;' # No Color

echo "========================================"
echo "知乎文章批量抓取脚本（简单版）"
echo "========================================"
echo ""

# 检查Cookie文件
if [ ! -f "cookie.txt" ]; then
    echo -e "${RED}错误: 未找到 cookie.txt 文件${NC}"
    echo "请先运行: python3 get_cookie_helper.py -v"
    exit 1
fi

# 读取Cookie
COOKIE=$(cat cookie.txt)
echo -e "${GREEN}✓ 已加载Cookie${NC}"

# 检查URL文件
URL_FILE="urls.txt"
if [ ! -f "$URL_FILE" ]; then
    echo -e "${YELLOW}未找到 urls.txt，使用示例URL${NC}"
    URL_FILE="urls_example.txt"
fi

# 创建输出目录
OUTPUT_DIR="articles"
mkdir -p "$OUTPUT_DIR"
echo -e "${GREEN}✓ 输出目录: $OUTPUT_DIR${NC}"
echo ""

# 统计
TOTAL=0
SUCCESS=0
FAILED=0

# 读取URL列表并抓取
while IFS= read -r url; do
    # 跳过注释和空行
    [[ "$url" =~ ^#.*$ ]] && continue
    [[ -z "$url" ]] && continue
    
    TOTAL=$((TOTAL + 1))
    
    echo "----------------------------------------"
    echo -e "${YELLOW}[$TOTAL] 抓取: $url${NC}"
    
    # 生成输出文件名
    OUTPUT_FILE="$OUTPUT_DIR/article_$(printf "%04d" $TOTAL).html"
    
    # 执行抓取
    if python3 zhihu_crawler.py "$url" "$OUTPUT_FILE" --cookie "$COOKIE" 2>&1 | grep -q "✅ 抓取成功"; then
        SUCCESS=$((SUCCESS + 1))
        echo -e "${GREEN}✓ 成功${NC}"
    else
        FAILED=$((FAILED + 1))
        echo -e "${RED}✗ 失败${NC}"
        # 记录失败的URL
        echo "$url" >> "$OUTPUT_DIR/failed_urls.txt"
    fi
    
    # 添加延迟避免请求过快
    if [ $TOTAL -lt $(wc -l < "$URL_FILE") ]; then
        DELAY=2
        echo "等待 $DELAY 秒..."
        sleep $DELAY
    fi
    
done < "$URL_FILE"

# 打印统计信息
echo ""
echo "========================================"
echo "批量抓取完成"
echo "========================================"
echo "总数: $TOTAL"
echo -e "${GREEN}成功: $SUCCESS${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo "输出目录: $OUTPUT_DIR"

if [ $FAILED -gt 0 ]; then
    echo -e "${YELLOW}失败URL已保存到: $OUTPUT_DIR/failed_urls.txt${NC}"
fi

echo "========================================"
