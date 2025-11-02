# 知乎作者文章列表抓取工具使用指南

## 🎯 功能概述

这个工具可以帮你获取知乎作者（个人或机构）的所有文章标题、URL和基本信息，支持大量文章的批量获取。

## 🚀 快速开始

### 基础用法
```bash
# 获取作者所有文章（默认保存为JSON、TXT、CSV三种格式）
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts"
```

### 常用选项
```bash
# 限制获取数量（推荐先测试）
python3 zhihu_author_crawler.py "作者URL" --max-articles 100

# 指定输出格式
python3 zhihu_author_crawler.py "作者URL" --format json

# 使用Cookie（推荐，避免访问限制）
python3 zhihu_author_crawler.py "作者URL" --cookie "你的Cookie"

# 调整请求间隔（避免被限制）
python3 zhihu_author_crawler.py "作者URL" --delay 2.0
```

## 📋 支持的URL格式

- **机构账号**: `https://www.zhihu.com/org/机构ID/posts`
- **个人账号**: `https://www.zhihu.com/people/用户ID/posts`

### 如何找到作者URL？
1. 打开知乎，搜索或访问目标作者主页
2. 点击"文章"或"专栏"标签
3. 复制浏览器地址栏中的URL

## 📊 输出格式说明

### JSON格式 (推荐用于程序处理)
```json
{
  "author": {
    "name": "作者名称",
    "id": "作者ID",
    "url": "作者页面URL",
    "total_posts": 文章总数
  },
  "articles": [
    {
      "title": "文章标题",
      "url": "文章URL",
      "id": "文章ID",
      "created_time": "发布时间",
      "excerpt": "文章摘要",
      "voteup_count": 点赞数,
      "comment_count": 评论数
    }
  ],
  "total_fetched": 获取到的文章数,
  "fetch_time": "获取时间"
}
```

### TXT格式 (人类可读)
```
================================================================================
作者信息
================================================================================
作者名称: 奶爸保​
作者ID: nai-ba-bao-25
获取时间: 2025-11-02 18:26:01
文章总数: 10

================================================================================
文章列表 (共 10 篇)
================================================================================

   1. 文章标题
      URL: 文章链接
      发布时间: 2025-01-01
      点赞数: 100
      摘要: 文章摘要...
```

### CSV格式 (便于Excel处理)
| 序号 | 标题 | URL | 文章ID | 发布时间 | 点赞数 | 评论数 | 摘要 |
|------|------|-----|--------|----------|--------|--------|------|

## 🛠️ 高级用法

### 1. 批量处理多个作者
```bash
# 创建作者列表文件 authors.txt
# 每行一个作者URL

# 使用脚本批量处理
for url in $(cat authors.txt); do
    python3 zhihu_author_crawler.py "$url" --max-articles 50
    sleep 5  # 避免请求过快
done
```

### 2. 结合文章抓取工具
```bash
# 1. 获取文章列表
python3 zhihu_author_crawler.py "作者URL" --format csv

# 2. 从CSV提取URL（可用Excel或脚本）
# 假设提取到 article_urls.txt

# 3. 批量抓取文章内容
python3 zhihu_crawler.py --batch article_urls.txt --cookie "你的Cookie"
```

### 3. 数据分析示例
```python
import json
import pandas as pd

# 读取JSON数据
with open('author_articles.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转换为DataFrame
df = pd.DataFrame(data['articles'])

# 分析
print(f"总文章数: {len(df)}")
print(f"平均点赞数: {df['voteup_count'].mean():.1f}")
print(f"最受欢迎文章: {df.loc[df['voteup_count'].idxmax(), 'title']}")
```

## ⚙️ 参数详解

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--max-articles` | 最大文章数量限制 | 无限制 | `--max-articles 100` |
| `--delay` | 请求间隔时间（秒） | 1.0 | `--delay 2.0` |
| `--format` | 输出格式 | all | `--format json` |
| `--output` | 输出文件名前缀 | 自动生成 | `--output author_name` |
| `--cookie` | Cookie字符串 | 从cookie.txt读取 | `--cookie "xxx"` |

### 输出格式选项
- `json`: 只保存JSON格式
- `txt`: 只保存文本格式  
- `csv`: 只保存CSV格式
- `all`: 保存所有格式（默认）

## 🔧 故障排除

### 1. 遇到403错误
```bash
# 解决方案：使用Cookie
python3 get_cookie_helper.py  # 获取Cookie
python3 zhihu_author_crawler.py "URL" --cookie "你的Cookie"
```

### 2. 获取文章数量为0
- 检查URL格式是否正确
- 确认作者确实发布了文章
- 尝试使用Cookie

### 3. 请求过快被限制
```bash
# 增加延迟时间
python3 zhihu_author_crawler.py "URL" --delay 3.0
```

### 4. API不可用时的备用方案
工具会自动尝试多个API端点，如果都不可用，会切换到HTML解析模式（功能有限但更稳定）。

## 📝 使用建议

1. **首次使用**: 建议先用 `--max-articles 10` 测试
2. **大量抓取**: 使用 `--delay 2.0` 避免被限制
3. **数据分析**: 推荐使用JSON格式
4. **人工查看**: 推荐使用TXT格式
5. **Excel处理**: 推荐使用CSV格式

## 🎯 典型使用场景

### 场景1: 内容分析师
```bash
# 分析某个领域专家的文章产出
python3 zhihu_author_crawler.py "专家URL" --format json
# 然后用Python分析JSON数据
```

### 场景2: 内容运营
```bash
# 获取竞品账号的文章列表
python3 zhihu_author_crawler.py "竞品URL" --format csv
# 用Excel分析标题规律和发布频率
```

### 场景3: 学术研究
```bash
# 收集某个机构的所有文章
python3 zhihu_author_crawler.py "机构URL" --max-articles 1000 --delay 2.0
# 后续批量下载文章内容进行文本分析
```

## ⚠️ 注意事项

1. **遵守使用条款**: 仅用于个人学习研究，不得商业使用
2. **控制频率**: 避免过于频繁的请求
3. **数据准确性**: 部分数据（如发布时间）可能不完整
4. **Cookie有效期**: Cookie会过期，需要定期更新

## 🔗 相关工具

- `zhihu_crawler.py`: 单篇文章内容抓取
- `get_cookie_helper.py`: Cookie获取辅助工具
- `test_author_crawler.py`: 功能测试脚本
- `author_crawler_example.py`: 使用示例脚本