# -*- coding: utf-8 -*-
"""celery 任务"""
import re
from urllib.parse import (
    urljoin,
)
import ujson
import requests
from recommend import (
    celery_app,
    celery_logger,
)
from recommend.models import (
    es_client,
    redis_client,
)
from recommend.models.youtuble import YoutubePopular
from recommend.models.imdb import IMDBVideo
from recommend.models.torrent import Torrent
from recommend.service import (
    youtube,
    imdb,
    indiantimes,
    hungama,
    es_doc,
    es_type,
    gaana,
    torrent,
    song_doc,
    song_type,
)


@celery_app.task
def download_torrent(infohash):
    """下载种子文件以加速下载

    Args:
        infohash (str): 种子hash
    """
    if Torrent.get(infohash):
        return

    if torrent.download_torrent(infohash):
        return

    celery_logger.info('unsupported: {}'.format(infohash))
