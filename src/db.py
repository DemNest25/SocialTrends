from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from . import config

# Motor de conexión
engine = create_engine(config.POSTGRES_URL, echo=False)

# Sesión
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base para modelos
Base = declarative_base()

def init_db():
    """Crear todas las tablas si no existen"""
    Base.metadata.create_all(bind=engine)
