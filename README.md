# 知乎文章抓取工具

一个用于抓取知乎文章内容的Python工具，支持单篇文章抓取和作者文章列表批量获取。只抓取文章主体内容，不包括侧边栏等无关元素。

## 快速开始

由于知乎有反爬虫机制，推荐使用以下方法之一：

**最简单的方法（无需编程）：**
1. 在浏览器中打开知乎文章
2. 右键 -> "另存为" -> 保存完整网页
3. 运行：`python3 extract_from_saved.py saved_page.html`

**高性能批量抓取（推荐）：**
```bash
# 1. 获取Cookie
python3 get_cookie_helper.py -v

# 2. 批量抓取文章
python3 zhihu_crawler.py --batch urls.txt --cookie "你的Cookie" --workers 5

# 3. 获取作者所有文章列表（新功能！）
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts"

# 单篇抓取
python3 zhihu_crawler.py "URL" --cookie "你的Cookie"
```

## 可用工具

本项目提供多个工具脚本：

### 核心抓取工具

1. **zhihu_crawler.py** - 🔥 高性能优化版（推荐批量使用）
   - ✅ 支持批量并发抓取
   - ✅ 智能重试机制
   - ✅ 连接池优化
   - ✅ 详细统计信息

2. **zhihu_author_crawler.py** - 🆕 作者文章列表抓取工具（新功能！）
   - ✅ 获取作者所有文章标题和URL
   - ✅ 支持机构账号和个人账号
   - ✅ 多种输出格式（JSON、TXT、CSV）
   - ✅ 智能分页获取
   
3. **extract_from_saved.py** - 从已保存的网页提取内容（最简单）
4. **zhihu_crawler_playwright.py** - 使用Playwright自动抓取（最稳定）
5. **zhihu_crawler_selenium.py** - 使用Selenium抓取（备选）

### 辅助工具

6. **get_cookie_helper.py** - Cookie获取和验证工具
7. **test_crawler.py** - 文章抓取功能测试脚本
8. **test_author_crawler.py** - 作者抓取功能测试脚本
9. **author_crawler_example.py** - 作者抓取使用示例
10. **extract_urls_from_json.py** - 从JSON文件提取URL列表
11. **complete_workflow_example.py** - 完整工作流程演示
12. **AUTHOR_CRAWLER_GUIDE.md** - 作者抓取工具详细指南

## 功能特点

- 只抓取文章主体内容，过滤侧边栏
- 保留文章格式、图片、代码块等
- 输出为格式化的HTML文件
- 支持多种抓取方式
- ✨ **HTML自动优化** - 移除冗余CSS，文件体积减少80%以上

## HTML优化说明

🎉 **新特性：自动HTML优化**

zhihu_crawler.py 已集成 HTML 优化功能，自动清理知乎生成的冗余CSS和属性：

**优化内容：**
- ✅ 移除所有 `<style data-emotion-css>` 标签
- ✅ 移除无用的 `class="css-xxxxx"` 属性  
- ✅ 清理 `data-*` 元数据属性
- ✅ 保留所有文章内容完整性

**优化效果：**
| 指标 | 优化前 | 优化后 | 改进 |
|------|-------|-------|------|
| 文件体积 | 72KB | 13KB | ⬇️ 82% |
| 可读性 | 难以阅读 | 清晰美观 | ⬆️ |
| 兼容性 | ✓ | ✓ | ✓ |

**验证优化效果：**
```bash
# 对比优化前后的文件
python3 compare_files.py test_output.html test_compressed.html
```

详见 `OPTIMIZATION_SUMMARY.md` 获取完整技术细节。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 详细使用方法

### 方法0: 从已保存的网页提取（最简单，无需处理反爬虫）

```bash
python3 extract_from_saved.py <已保存的HTML文件> [输出文件名]
```

步骤：
1. 在浏览器中打开知乎文章
2. 右键 -> "另存为" -> 选择"网页，完整"
3. 运行脚本提取文章内容

示例：
```bash
python3 extract_from_saved.py saved_page.html
python3 extract_from_saved.py saved_page.html article.html
```

### 方法1: 高性能批量抓取（🔥 推荐）

**新特性：**
- ✅ 支持并发抓取（可配置1-20个并发）
- ✅ 智能重试机制（自动重试失败请求）
- ✅ 连接池优化（HTTP连接复用）
- ✅ 详细统计信息（成功率、速度等）
- ✅ User-Agent轮换（降低被识别风险）

**单篇抓取：**
```bash
# 基础用法（需要Cookie）
python3 zhihu_crawler.py "URL" --cookie "你的Cookie"

# 指定输出文件
python3 zhihu_crawler.py "URL" output.html --cookie "你的Cookie"
```

**批量抓取：**
```bash
# 1. 创建URL列表文件 urls.txt（每行一个URL）

# 2. 批量抓取（默认5个并发）
python3 zhihu_crawler.py --batch urls.txt --cookie "你的Cookie"

# 3. 高性能配置
python3 zhihu_crawler.py --batch urls.txt \
    --cookie "你的Cookie" \
    --workers 10 \
    --delay 0.5 \
    --output-dir articles
```

**性能参考（抓取100篇文章）：**
- 保守模式：`--workers 3 --delay 2.0` → 约67秒
- 推荐模式：`--workers 5 --delay 1.0` → 约20秒  
- 高速模式：`--workers 10 --delay 0.5` → 约10秒

**获取Cookie（重要！）：**
```bash
# 使用辅助工具
python3 get_cookie_helper.py        # 查看详细说明
python3 get_cookie_helper.py -v     # 交互式验证Cookie
```

**手动获取Cookie：**
1. 浏览器打开 https://www.zhihu.com 并登录
2. 按F12打开开发者工具，切换到Network标签
3. 刷新页面，找到文章请求
4. 在请求头中找到Cookie值并复制

### 方法2: 使用Playwright版本（推荐，最稳定）

```bash
python zhihu_crawler_playwright.py <知乎文章URL> [输出文件名]
```

示例：
```bash
python zhihu_crawler_playwright.py https://zhuanlan.zhihu.com/p/1967253690982335635
```

**首次使用需要安装浏览器：**
```bash
pip install playwright
playwright install chromium
```

### 方法3: 使用Selenium版本（备选方案）

```bash
python zhihu_crawler_selenium.py <知乎文章URL> [输出文件名]
```

**注意：** Selenium版本需要安装Chrome浏览器和ChromeDriver

### 方法4: 获取作者所有文章列表（🆕 新功能）

**功能说明：**
- 获取知乎作者（个人或机构）的所有文章标题和URL
- 支持大量文章的分页获取（如4693篇文章）
- 多种输出格式：JSON、TXT、CSV
- 可用于后续批量抓取或数据分析

**基础用法：**
```bash
# 获取作者所有文章
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts"

# 限制获取数量
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts" --max-articles 100

# 指定输出格式
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts" --format json

# 使用Cookie（推荐）
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts" --cookie "你的Cookie"
```

**高级选项：**
```bash
# 完整参数示例
python3 zhihu_author_crawler.py "作者URL" \
    --max-articles 1000 \
    --delay 1.0 \
    --format all \
    --output "author_name" \
    --cookie "你的Cookie"
```

**支持的作者URL格式：**
- 机构账号：`https://www.zhihu.com/org/机构ID/posts`
- 个人账号：`https://www.zhihu.com/people/用户ID/posts`

**输出文件说明：**
- **JSON格式**：包含完整的文章信息（标题、URL、发布时间、点赞数等）
- **TXT格式**：人类可读的文本格式，便于查看
- **CSV格式**：表格格式，便于导入Excel或数据库

**典型工作流程：**
```bash
# 1. 获取作者文章列表
python3 zhihu_author_crawler.py "https://www.zhihu.com/org/nai-ba-bao-25/posts" --format csv

# 2. 从CSV中提取URL创建批量抓取文件
# （可以用Excel或脚本处理CSV文件）

# 3. 批量抓取文章内容
python3 zhihu_crawler.py --batch extracted_urls.txt --cookie "你的Cookie"
```

**测试新功能：**
```bash
# 运行测试脚本
python3 test_author_crawler.py

# 查看使用示例
python3 author_crawler_example.py
```

## 输出格式

生成的HTML文件包含：
- 文章标题
- 作者信息（如果有）
- 发布时间（如果有）
- 原文链接
- 文章主体内容（带样式）

输出的HTML文件已经过美化，可以直接在浏览器中打开查看。

## 工具对比

| 工具 | 速度 | 易用性 | 稳定性 | 依赖 | 推荐场景 |
|------|------|--------|--------|------|---------|
| extract_from_saved | 最快 | 最简单 | 100% | 无 | **日常使用** |
| Playwright版本 | 中等 | 简单 | 最稳定 | 需要浏览器 | **自动化** |
| requests版本 | 快 | 简单 | 低 | 少 | 测试/有Cookie时 |
| Selenium版本 | 较慢 | 较复杂 | 稳定 | Chrome | 备选 |

## 常见问题

### Q: 遇到403错误怎么办？
A: 
1. 先尝试使用Selenium版本
2. 或者在requests版本中提供Cookie参数

### Q: 为什么抓取的内容不完整？
A: 知乎的某些内容可能是动态加载的，建议使用Selenium版本

### Q: 可以批量抓取吗？
A: 可以编写脚本循环调用，但请注意：
   - 添加适当的延迟避免被封IP
   - 遵守知乎的robots.txt规则
   - 仅用于个人学习研究

## 免责声明

本工具仅供学习和研究使用，请遵守知乎的服务条款和相关法律法规。不得用于商业用途或大规模爬取。
