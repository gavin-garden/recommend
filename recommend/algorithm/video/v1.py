# -*- coding: utf-8 -*-
"""
youtube 视频第一版推荐算法

召回环节通过比较标签相似度
排序环境通过视频播放量进行排序
"""
from recommend import es_client
from recommend.const import (
    video_index,
    video_type,
)
from recommend.algorithm import stop_words_set


def get_video_tag(video_id):
    """从es中找到视频, 并计算视频的标签向量

    Args:
        video_id (str): 视频id
    """
    video = es_client.get(video_index, video_type, id=video_id)
    source = video['_source']
    video_tag = source.get('tag', [])
    view_count = source.get('hot', 0)

    tags = set()
    for item in video_tag:
        words = item.split()
        for word in words:
            w = word.lower()
            if w in stop_words_set:
                continue
            if len(w) < 3:
                continue
            if w.isalpha():
                tags.add(w)
    return view_count, tags


def query_video_by_tag(tags):
    """根据标签在es中查询视频

    Args:
        tags (set): 标签集合
    """
    if not tags:
        return

    query = {
        'size': 100,
        'query': {
            'bool': {
                'must': [
                    {'term': {'type': 'mv'}},
                    {
                        'bool': {
                            'should': [{'term': {'tag': x}} for x in tags]
                        }
                    }
                ]
            }
        },
        '_source': ['hot'],
        'min_score': 20.0
    }
    query_result = es_client.search(video_index, video_type, body=query)
    hits = query_result['hits']['hits']

    video_map = {}
    for item in hits:
        id_ = item['_id']
        score_ = item['_score']
        video_map[id_] = score_
    return video_map
