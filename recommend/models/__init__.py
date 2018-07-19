# -*- coding: utf-8 -*-
"""数据库连接"""
from redis import StrictRedis
from elasticsearch import Elasticsearch
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from recommend.configure import (
    MYSQL_URL,
    REDIS_URL,
    ES_HOSTS,
)


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise

BaseModel = declarative_base()
db_engine = create_engine(MYSQL_URL, pool_size=100, pool_recycle=3600)
event.listen(db_engine, 'checkout', checkout_listener)
DBSession = sessionmaker(bind=db_engine, expire_on_commit=False)

redis_client = StrictRedis.from_url(REDIS_URL)
es_client = Elasticsearch(ES_HOSTS)
