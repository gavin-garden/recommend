# -*- coding: utf-8 -*-
"""
youtube 视频第一版推荐算法

召回环节通过比较标签相似度以及热门视频
排序环境通过视频播放量进行排序
"""
from recommend import (
    es_client,
    redis_client,
)
from recommend.const import (
    video_index,
    video_type,
    hot_video_key,
)
from recommend.algorithm.video import stop_words_set


class VideoAlgorithmV1(object):

    def __init__(self):
        self.hot_videos = {}

    def _load_hot_videos(self):
        """加载热门视频"""
        if redis_client.exists(hot_video_key):
            videos = redis_client.zrangebyscore(
                hot_video_key, '-inf', '+inf', withscores=True)
        else:
            self.hot_videos.update(self._get_hot_videos(size=1000))
            self.hot_videos.update(self._get_hot_videos(tag='india', size=300))
            self.hot_videos.update(self._get_hot_videos(tag='indian', size=300))
            self.hot_videos.update(self._get_hot_videos(tag='bollywood', size=300))
            self.hot_videos.update(self._get_hot_videos(tag='series', size=300))

            zset_args = []
            for key, value in self.hot_videos.items():
                zset_args.append(value)
                zset_args.append(key)
            redis_client.zadd(hot_video_key, *zset_args)

    @staticmethod
    def _get_hot_videos(tag=None, size=100):
        """找到制定标签的热门视频

        Args:
            tag (str): 标签
            size (int): 个数
        """
        query = {
            'size': size,
            'query': {
                'bool': {
                    'must': [
                        {'term': {'type': 'mv'}},
                    ]
                }
            },
            '_source': ['hot'],
            'sort': [{"hot": {"order": "desc"}}]
        }
        if tag:
            query['query']['bool']['must'].append({'term': {'tag': tag}})

        query_result = es_client.search(video_index, video_type, body=query)
        hits = query_result['hits']['hits']

        video_map = {}
        for item in hits:
            id_ = item['_id']
            view_count = item['_source']['hot']
            if view_count < 10000000:  # 热门视频的标准是观看数必须超过一千万
                continue
            video_map[id_] = view_count
        return video_map


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


def query_videos_by_tag(tags, size=100):
    """根据标签在es中查询视频

    Args:
        tags (set): 标签集合
        size (int): 视频个数
    """
    if not tags:
        return

    query = {
        'size': size,
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
