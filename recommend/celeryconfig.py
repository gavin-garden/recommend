# -*- coding: utf8 -*-
"""celery配置"""
from recommend.configure import REDIS_URL

broker_url = REDIS_URL

imports = (
    'recommend.tasks',
)

task_serializer = 'pickle'
accept_content = ['pickle', 'json']
