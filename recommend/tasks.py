# -*- coding: utf-8 -*-
"""celery 任务"""
from recommend import celery_app
from recommend.models import (
    video_model,
    cache_region,
)
from recommend.algorithm.video.v1 import algorithm


@celery_app.task
@cache_region.cache_on_arguments(expiration_time=300)
def update_video_recommendation(device, video_id, operation):
    """根据用户行为更新推荐内容

    Args:
        device (str): 设备id
        video_id (str): 视频id
        operation (int): 操作类型
    """
    algorithm.update_recommend_list(device, video_id, operation)
    video_model.VideoBehavior.add(device, video_id, operation)
