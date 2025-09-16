import time
from sqlalchemy.orm import Session
from .db import engine, Base, SessionLocal
from .models import Tweet
from .config import X_BEARER_TOKEN, X_KEYWORDS
import tweepy

# Inicializar Twitter client
client = tweepy.Client(bearer_token=X_BEARER_TOKEN, wait_on_rate_limit=True)

def init_db():
    """Crear tablas si no existen"""
    Base.metadata.create_all(bind=engine)

def run_once():
    """Ejecuta una ronda de ingestión de tweets"""
    init_db()
    with SessionLocal() as session:
        if not X_KEYWORDS:
            print("No hay keywords configuradas 😅")
            return

        for keyword in X_KEYWORDS:
            query = f"({keyword}) lang:es -is:retweet"
            print(f"[X] Buscando: {query}")
            
            tweets_data = []
            try:
                tweets = client.search_recent_tweets(
                    query=query,
                    max_results=20,  # reducir para no alcanzar límite
                    tweet_fields=['id', 'text', 'author_id', 'created_at', 'lang', 'public_metrics']
                )
                if tweets.data:
                    tweets_data = tweets.data
                else:
                    print(f"[!] No se encontraron tweets para '{keyword}'")
            except tweepy.TooManyRequests as e:
                print(f"Rate limit exceeded. Sleeping for {e.retry_after} segundos...")
                time.sleep(e.retry_after + 1)
            except Exception as e:
                print(f"[!] Error buscando tweets: {e}")

            # Guardar tweets que sí llegaron
            new_count = 0
            for tw in tweets_data:
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
                    raw=tw.data,
                    keyword=keyword
                )
                session.add(t)
                new_count += 1

            session.commit()
            print(f"[X] Guardados nuevos: {new_count} para '{keyword}'")

if __name__ == "__main__":
    run_once()
