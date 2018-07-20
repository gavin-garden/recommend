# -*- coding: utf-8 -*-
"""参数配置"""

ES_HOSTS = ['xxxxxx']
MYSQL_URL = 'xxxxxx'
REDIS_URL = 'xxxxx'
CACHE_ARGUMENTS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'redis_expiration_time': 60*60*2,   # 2 hours
    'distributed_lock': True
}
