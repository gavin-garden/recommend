# -*- coding: utf-8 -*-
"""常量定义"""

video_index = 'resources'
video_type = 'doc'

hot_video_key = 'hot_video_zset'


class ReturnCode(object):
    """返回码"""
    success = 0


class Operation(object):
    """操作类型"""
    watch = 1
    collect = 2
    share = 3
    star = 4
