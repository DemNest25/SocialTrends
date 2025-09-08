from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from . import config

# Motor de conexión a la base de datos
engine = create_engine(config.POSTGRES_URL, echo=False)

# Sesión para interactuar con la base de datos
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base para declarar los modelos
Base = declarative_base()

# Modelo Tweet
class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    author_id = Column(String)
    created_at = Column(DateTime)
    lang = Column(String)
    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)
    quote_count = Column(Integer)
    raw = Column(Text)
    keyword = Column(String)

def init_db():
    """
    Crea todas las tablas definidas en los modelos
    si no existen aún.
    """
    Base.metadata.create_all(bind=engine)
