from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from .db import Base
from datetime import datetime

class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    author_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lang = Column(String(10))
    retweet_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    quote_count = Column(Integer, default=0)
    raw = Column(JSON)   # guarda el JSON completo del tweet
    keyword = Column(String, index=True)  # opcional: para relacionar tweet con keyword usada

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
