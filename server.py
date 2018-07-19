# -*- coding: utf8 -*-
"""用户接口"""
import random
import ujson
from flask import jsonify
from webargs import fields

from recommend import (
    flask_app,
    tasks,
)
from recommend.const import ReturnCode
from recommend.tools.args import parser
from recommend.models import redis_client
from recommend.algorithm.video import (
    v1,
    get_videos,
)


@flask_app.route('/recommend/video/guess-like', methods=['GET'])
@parser.use_args({
    'id': fields.Str(required=True, location='query'),
})
def video_guess_like(args):
    video_id = args['id']

    redis_key = 'video|{}'.format(video_id)
    cache = redis_client.get(redis_key)
    if cache:
        return jsonify({
            "ret": ReturnCode.success,
            "msg": "ok",
            "data": ujson.loads(cache),
        })

    try:
        tags = v1.algorithm.get_video_tag(video_id)
    except:
        # 从youtube爬到视频信息出异常
        tags = None

    video_map = None
    if tags:
        video_map = v1.algorithm.query_videos_by_tag(tags, 11)
    if video_map:
        video_ids = list(video_map.keys())
    else:
        video_ids = random.sample(v1.algorithm.hot_videos.keys(), 11)

    if video_id in video_ids:
        video_ids.remove(video_id)
    else:
        video_ids = video_ids[:-1]
    videos = get_videos(video_ids)
    redis_client.set(redis_key, ujson.dumps(videos), ex=3600)
    return jsonify({
        "ret": ReturnCode.success,
        "msg": "ok",
        "data": videos,
    })


@flask_app.route('/recommend/device/video/behavior', methods=['POST'])
@parser.use_args({
    'device': fields.Str(required=True, location='json'),
    'video_id': fields.Str(required=True, location='json'),
    'operation': fields.Int(required=True, location='json'),
})
def device_video_behavior(args):
    device = args['device']
    video_id = args['id']
    operation = args['operation']
    tasks.update_video_recommendation.delay(device, video_id, operation)
    return jsonify({
        "ret": ReturnCode.success,
        "msg": "ok",
    })


@flask_app.route('/recommend/device/video/recommend', methods=['POST'])
@parser.use_args({
    'device': fields.Str(required=True, location='query'),
    'size': fields.Str(location='query'),
})
def device_video_recommend(args):
    device = args['device']
    size = args.get('size', 10)
    return jsonify({
        "ret": ReturnCode.success,
        "msg": "ok",
    })

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=30001)
