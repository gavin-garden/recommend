# -*- coding: utf-8 -*-
"""
youtube 视频第一版推荐算法

召回环节通过比较标签相似度以及热门视频
排序环境通过视频播放量进行排序
"""
import operator
import random
from math import log10
from recommend.models import (
    es_client,
    redis_client,
    video_model,
    cache_region,
)
from recommend.const import (
    video_index,
    video_type,
    hot_video_key,
    Operation,
)
from recommend.algorithm.video import (
    stop_words_set,
    get_video,
    get_videos,
)


video_operation_score = {
    Operation.watch: 0.1,
    Operation.collect: 0.2,
    Operation.share: 0.3,
    Operation.star: 0.2,
}


class VideoAlgorithmV1(object):

    def __init__(self):
        self.hot_videos = {}
        self._load_hot_videos()

    def _load_hot_videos(self):
        """加载热门视频"""
        if redis_client.exists(hot_video_key):
            videos = redis_client.zrangebyscore(
                hot_video_key, '-inf', '+inf', withscores=True)
            for key, value in videos:
                self.hot_videos[key.decode('utf8')] = value
        else:
            self.hot_videos.update(self._get_hot_videos(size=700))
            self.hot_videos.update(self._get_hot_videos(tag='india', size=200))
            self.hot_videos.update(self._get_hot_videos(tag='bollywood', size=500))
            self.hot_videos.update(self._get_hot_videos(tag='series', size=200))

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
            if view_count < 20000000:  # 热门视频的标准是观看数必须超过两千万
                continue
            video_map[id_] = log10(view_count)
        return video_map

    @staticmethod
    def _get_video_tag(video_id):
        """从es中找到视频, 并计算视频的标签向量

        Args:
            video_id (str): 视频id
        """
        source = get_video(video_id)
        video_tag = source.get('tag', [])

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
        return tags

    @staticmethod
    def _query_videos_by_tag(tags, size=100):
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

    @cache_region.cache_on_arguments(expiration_time=3600)
    def get_similar_videos(self, video_id, size=10):
        """根据标签获取相似的视频(如果没有,则返回热门视频)

        Args:
            video_id (str): 视频id
            size (int): 数量
        """
        try:
            tags = self._get_video_tag(video_id)
        except:
            # 从youtube爬到视频信息出异常
            tags = None

        video_map = None
        if tags:
            video_map = self._query_videos_by_tag(tags, size)
        if video_map:
            video_ids = list(video_map.keys())
        else:
            video_ids = random.sample(self.hot_videos.keys(), size)

        if video_id in video_ids:
            video_ids.remove(video_id)
        videos = get_videos(video_ids)
        return videos

    def update_recommend_list(self, device, video, operation):
        """针对用户操作视频的行为更新推荐列表

        Args:
            device (str): 设备id
            video (str): 视频id
            operation (int): 操作类型
        """
        device_key = 'device|{}|recommend'.format(device)
        recommend_list = redis_client.zrangebyscore(
            device_key, '-inf', '+inf', withscores=True)
        if not recommend_list:
            return
        recommend_map = {key.decode('uft8'): value for key, value in recommend_list}

        try:
            tags = self._get_video_tag(video)
        except:
            tags = None
        # 视频没有标签 不推荐数据
        if not tags:
            return

        video_map = self._query_videos_by_tag(tags, 100)
        if not video_map:
            return

        video_records = video_model.VideoBehavior.query_by_device(device)
        recent_videos = {x.video for x in video_records}
        recent_videos.add(video)

        for key, value in video_map.items():
            if key in recommend_map:
                recommend_map[key] += video_operation_score[operation] * log10(value)
            else:
                recommend_map[key] = value

        recommend_list = sorted(recommend_map, operator.itemgetter(1), reverse=True)
        count = 0
        zset_args = []
        for key, value in recommend_list:
            if count > 1000:
                break

            if key in recent_videos:
                continue

            zset_args.append(value)
            zset_args.append(key)
            count += 1

        redis_client.delete(device_key)
        redis_client.zadd(device_key, *zset_args)

    def get_recommend_videos(self, device, size):
        """获取推荐视频数据

        Args:
            device (str): 设备id
            size (int): 个数
        """
        device_key = 'device|{}|recommend'.format(device)
        recommend_list = redis_client.zrange(device_key, 0, size, desc=True)

        # 推荐列表为空
        if not recommend_list:
            video_ids = random.sample(self.hot_videos.keys(), size + 500)
            recommend_videos = video_ids[:size]
            zset_args = []
            for video in video_ids[size:]:
                zset_args.append(1.0)
                zset_args.append(video)
            redis_client.zadd(device_key, *zset_args)
        else:
            recommend_videos = recommend_list
            redis_client.zrem(device_key, *recommend_videos)

        videos = get_videos(recommend_videos)
        return videos


algorithm = VideoAlgorithmV1()
