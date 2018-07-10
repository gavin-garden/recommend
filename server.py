# -*- coding: utf8 -*-
"""用户接口"""
from flask import jsonify
from webargs import fields

from recommend import flask_app
from recommend.const import ReturnCode
from recommend.tools.args import parser


@flask_app.route('/recommend/video', methods=['GET'])
@parser.use_args({
    'id': fields.Str(required=True, location='query'),
    'size': fields.Int(location='query')
})
def recommend_video(args):
    video_id = args['id']
    size = args.get('size', 10)
    return jsonify({
        "ret": ReturnCode.success,
        "msg": "ok",
    })
