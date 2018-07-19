# -*- coding: utf-8 -*-
"""celery 任务"""
from recommend import celery_app
from recommend.models.video_model import VideoBehavior
from recommend.algorithm.video.v1 import algorithm


@celery_app.task
def update_video_recommendation(device, video_id, operation):
    """根据用户行为更新推荐内容

    Args:
        device (str): 设备id
        video_id (str): 视频id
        operation (int): 操作类型
    """
    # todo add dogpile cache
    algorithm.update_recommend_list(device, video_id, operation)
    VideoBehavior.add(device, video_id, operation)

