import os
from dotenv import load_dotenv

load_dotenv()

# URL de la base de datos
_database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
if _database_url and _database_url.startswith("postgres://"):
    _database_url = _database_url.replace("postgres://", "postgresql+psycopg2://", 1)

POSTGRES_URL = _database_url or "postgresql+psycopg2://postgres:postgres@localhost:5432/socialtrends"

# Tokens
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

# Keywords fijas para Render / prueba
X_KEYWORDS = [s.strip() for s in os.getenv("X_KEYWORDS", "python,ia,tendencias").split(",") if s.strip()]

# Intervalo de ingestión en minutos
INGEST_INTERVAL_MIN = int(os.getenv("INGEST_INTERVAL_MIN", "10"))
