from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from . import config

# Motor de conexión a la base de datos
engine = create_engine(config.POSTGRES_URL)

# Sesión para interactuar con la base de datos
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base para declarar los modelos
Base = declarative_base()

def init_db():
    """
    Crea todas las tablas definidas en models.py
    si no existen aún.
    """
    from . import models  # importa los modelos
    Base.metadata.create_all(bind=engine)
