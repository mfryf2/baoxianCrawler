# 数据库配置
DB_CONFIG = {
    'host': '172.105.225.120',
    'user': 'root',
    'password': 'lnmp.org#25295',
    'database': 'wordpress',
    'port': 3306
}

# 爬虫配置
CRAWLER_CONFIG = {
    # 重试次数
    'max_retries': 5,
    # 超时时间（秒）
    'timeout': 20,
    # 批量爬取默认数量
    'default_batch_limit': 10,
    # 请求间隔（秒）
    'request_delay_min': 2,
    'request_delay_max': 5,
}
