import os
import time
from datetime import datetime
from sqlalchemy.orm import Session
from src.db import engine, Base, Tweet
import tweepy  # asegúrate de tener tweepy instalado

# Config
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
X_KEYWORDS = os.environ.get("X_KEYWORDS", "python,IA,tecnologia").split(",")
INGEST_INTERVAL_MIN = int(os.environ.get("INGEST_INTERVAL_MIN", 10))

# Inicializar Twitter client
client = tweepy.Client(bearer_token=X_BEARER_TOKEN, wait_on_rate_limit=True)

def init_db():
    """Crear tablas si no existen"""
    Base.metadata.create_all(bind=engine)

def run_once():
    """Ejecuta una ronda de ingestión de tweets"""
    init_db()
    with Session(engine) as session:
        for keyword in X_KEYWORDS:
            query = f"({keyword}) lang:es -is:retweet"
            print(f"[X] Buscando: {query}")
            try:
                tweets = client.search_recent_tweets(query=query, max_results=100,
                                                     tweet_fields=['id', 'text', 'author_id', 'created_at', 'lang', 'public_metrics'])
            except tweepy.TooManyRequests as e:
                # Rate limit excedido
                print(f"Rate limit exceeded. Sleeping for {e.retry_after} seconds.")
                time.sleep(e.retry_after + 1)
                continue

            if not tweets.data:
                continue

            for tw in tweets.data:
                # Revisar si ya existe
                if session.get(Tweet, tw.id):
                    continue

                t = Tweet(
                    id=tw.id,
                    text=tw.text,
                    author_id=tw.author_id,
                    created_at=tw.created_at,
                    lang=tw.lang,
                    retweet_count=tw.public_metrics.get("retweet_count", 0),
                    reply_count=tw.public_metrics.get("reply_count", 0),
                    like_count=tw.public_metrics.get("like_count", 0),
                    quote_count=tw.public_metrics.get("quote_count", 0),
                    raw=str(tw),
                    keyword=keyword  # <-- Guardamos la keyword correcta
                )
                session.add(t)
            session.commit()

def run_loop():
    """Loop infinito cada INGEST_INTERVAL_MIN"""
    while True:
        print(f"[{datetime.now()}] Iniciando ingestión...")
        run_once()
        print(f"[{datetime.now()}] Dormir {INGEST_INTERVAL_MIN} minutos...")
        time.sleep(INGEST_INTERVAL_MIN * 60)

if __name__ == "__main__":
    run_loop()
