# -*- coding: utf8 -*-
import os
import time
import yaml
import logging
import logging.config

from redis import StrictRedis
from elasticsearch import Elasticsearch
from flask import (
    Flask,
    g,
    jsonify
)
from celery import Celery
from recommend.configure import (
    REDIS_URL,
    ES_HOSTS,
)
from recommend.tools.trace import MonitorMiddleware

current_dir = os.path.dirname(__file__)
logging_path = os.path.join(current_dir, 'logging.yaml')
with open(logging_path, 'r') as f:
    logging.config.dictConfig(yaml.load(f))

logger = logging.getLogger('recommend.console')

redis_client = StrictRedis.from_url(REDIS_URL)
es_client = Elasticsearch(ES_HOSTS)

celery_app = Celery("recommend")
celery_app.config_from_object("recommend.celeryconfig")

flask_app = Flask("recommend")
middleware = MonitorMiddleware(flask_app, '/recommend/metrics')


@flask_app.before_request
def before_request():
    g.start_time = time.time()


@flask_app.errorhandler(Exception)
def handle_exception(e):
    middleware.log_exception(e)
    return jsonify({'ret': '-1', 'msg': 'unknown error'}), 500


@flask_app.after_request
def after_request(resp):
    middleware.log_response(resp)
    return resp
