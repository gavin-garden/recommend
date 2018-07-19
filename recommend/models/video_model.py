# -*- coding: utf-8 -*-
"""用户操作视频的行为"""
import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    SmallInteger,
)
from recommend.models import (
    DBSession,
    BaseModel,
)


class VideoBehavior(BaseModel):

    __tablename__ = 'video_behavior'

    id = Column(Integer, primary_key=True)
    device = Column(String(32), nullable=False)
    video = Column(String(16), nullable=False)
    operation = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    @classmethod
    def add(cls, device, video, operation):
        record = cls(
            device=device,
            video=video,
            operation=operation,
        )
        session = DBSession()
        session.add(record)
        session.commit()
        return record

    @classmethod
    def query_by_device(cls, device):
        begin = datetime.datetime.now() - datetime.timedelta(days=90)
        session = DBSession()
        records = session.query(cls).\
            filter(cls.device == device).\
            filter(cls.created_at > begin).\
            order_by(cls.created_at.desc()).\
            limit(100).all()
        session.commit()
        return records
