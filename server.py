# -*- coding: utf8 -*-
"""用户接口"""
import random
from flask import jsonify
from webargs import fields

from recommend import flask_app
from recommend.const import ReturnCode
from recommend.tools.args import parser

from recommend.algorithm.video import (
    get_videos,
    v1,
)


@flask_app.route('/recommend/video/guess', methods=['GET'])
@parser.use_args({
    'id': fields.Str(required=True, location='query'),
    'size': fields.Int(location='query')
})
def video_guess_like(args):
    video_id = args['id']
    size = args.get('size', 10)

    try:
        tags = v1.algorithm.get_video_tag(video_id)
    except:
        # 从youtube爬到视频信息出异常
        tags = None

    video_map = None
    if tags:
        video_map = v1.algorithm.query_videos_by_tag(tags, size)
    if video_map:
        video_ids = list(video_map.keys())
    else:
        video_ids = random.sample(v1.algorithm.hot_videos.keys(), size)

    videos = get_videos(video_ids)
    return jsonify({
        "ret": ReturnCode.success,
        "msg": "ok",
        "data": videos,
    })

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=30001)
