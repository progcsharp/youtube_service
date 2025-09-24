from datetime import datetime
import uuid

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, Integer, BigInteger, DateTime, JSON, ForeignKey, MetaData, ARRAY


from .utils import conventions


meta = MetaData(naming_convention=conventions)
Base = declarative_base(metadata=meta)


class Channel(Base):
    __tablename__ = 'channel'

    channel_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    etag = Column(String(100))
    description = Column(Text)
    custom_url = Column(String(100))
    youtube_channel_id = Column(String(50), unique=True, nullable=False)
    published_at = Column(DateTime(timezone=True))
    country_code = Column(String(2))
    thumbnail_url = Column(String(500))
    subscriber_count = Column(BigInteger, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(BigInteger, default=0)
    privacy_status = Column(String(20), default='public')
    credentials = Column(JSON)
    last_synced_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    posts = relationship("Post", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Channel {self.title} ({self.youtube_channel_id})>"


class Post(Base):
    __tablename__ = 'post'

    post_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey('channel.channel_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    youtube_video_id = Column(String(20), unique=True, nullable=False)
    tags = Column(ARRAY(String(500)))
    published_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    privacy_status = Column(String(20), default='public')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    channel = relationship("Channel", back_populates="posts")
    statistics = relationship("Statistic", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post {self.title} ({self.youtube_video_id})>"


class Statistic(Base):
    __tablename__ = 'statistic'

    stats_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey('post.post_id', ondelete='CASCADE'), nullable=False)
    capture_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    view_count = Column(BigInteger, default=0)
    like_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Отношения
    post = relationship("Post", back_populates="statistics")

    def __repr__(self):
        return f"<Statistic for post {self.post_id} at {self.capture_date}>"

