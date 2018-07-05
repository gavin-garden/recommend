# -*- coding: utf8 -*-
import os
import yaml
import logging
import logging.config

from redis import StrictRedis
from elasticsearch import Elasticsearch
from recommend.configure import (
    REDIS_URL,
    ES_HOSTS,
)

current_dir = os.path.dirname(__file__)
logging_path = os.path.join(current_dir, 'logging.yaml')
with open(logging_path, 'r') as f:
    logging.config.dictConfig(yaml.load(f))

logger = logging.getLogger('recommend.console')

redis_client = StrictRedis.from_url(REDIS_URL)
es_client = Elasticsearch(ES_HOSTS)
