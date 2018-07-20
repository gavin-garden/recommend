# -*- coding: utf8 -*-
"""中间件"""
import os
import time
import logging

import requests
from flask import (
    request,
    g,
)
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
)
from werkzeug.contrib.fixers import ProxyFix

logger = logging.getLogger('recommend.file')


class MonitorMiddleware(object):

    def __init__(self, flask_app, metric_url):
        self.metric_url = metric_url
        self.process_id = str(os.getpid())
        self.instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text

        flask_app.add_url_rule(metric_url, view_func=metrics, methods=['GET'])

        self.wsgi_app = ProxyFix(flask_app.wsgi_app)

        self.req_counter = Counter(
            'recommend_requests_total',
            'Total request counts',
            ['method', 'endpoint', 'instance', 'process'])
        self.err_counter = Counter(
            'recommend_error_total',
            'Total error counts',
            ['method', 'endpoint', 'instance', 'process'])
        self.resp_latency = Histogram(
            'recommend_response_latency_millisecond',
            'Response latency (millisecond)',
            ['method', 'endpoint', 'instance', 'process'],
            buckets=(10, 20, 30, 50, 80, 100, 200, 300, 500, 1000, 2000, 3000))

    def _label(self):
        return {
            'method': request.method,
            'endpoint': request.url_rule.rule,
            'instance': self.instance_id,
            'process': self.process_id,
        }

    def log_response(self, response):
        label = self._label()
        if label['endpoint'] == self.metric_url:
            return

        time_used = int((time.time() - g.start_time) * 1000)
        logger.info('{} {} {}'.format(
            response.status_code, label['endpoint'], time_used))
        self.req_counter.labels(**label).inc()
        self.resp_latency.labels(**label).observe(time_used)

    def log_exception(self, e):
        logger.exception(e)
        self.err_counter.labels(**self._label()).inc()


def metrics():
    data = generate_latest()
    return data, 200, {'Content-Type': 'text/plain; charset=utf-8'}
