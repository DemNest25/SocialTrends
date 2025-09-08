import keyword
import time
import tweepy
from datetime import datetime, timezone

from .db import SessionLocal, init_db
from .models import Tweet
from . import config


def run_once():
    if not config.X_BEARER_TOKEN:
        print("X_BEARER_TOKEN no configurado; omitiendo ingesta de X.")
        return
    
    client = tweepy.Client(bearer_token=config.X_BEARER_TOKEN, wait_on_rate_limit=True)

    with SessionLocal() as db:
        init_db()  # asegura que las tablas existan

        for kw in config.X_KEYWORDS:
            query = f'({kw}) lang:es -is:retweet'
            print(f"[X]Buscando: {query}")
            paginator = tweepy.Paginator(
                client.search_recent_tweets,
                query=query,
                tweet_fields=["id", "text", "created_at", "author_id", "lang", "public_metrics"],
                max_results=10
            )

            new_count = 0
            for page in paginator:
                if not page.data:
                    continue

                for t in page.data:
                    pm = getattr(t, "public_metrics", {}) or {}
                    tw = Tweet(
                        id=int(t.id),
                        text=t.text,
                        author_id=str(getattr(t, "author_id", "")),
                        created_at=getattr(t, "created_at", datetime.now(timezone.utc)),
                        lang=getattr(t, "lang", None),
                        retweet_count=pm.get("retweet_count", 0),
                        reply_count=pm.get("reply_count", 0),
                        like_count=pm.get("like_count", 0),
                        quote_count=pm.get("quote_count", 0),
                        raw=t.data,
                        keyword=keyword
                    )
                    if not db.get(Tweet, tw.id):
                        db.add(tw)
                        new_count += 1

                db.commit()
                time.sleep(1)  # para no abusar de la API

            print(f"[X] Guardados nuevos: {new_count} para '{kw}'")


if __name__ == "__main__":
    run_once()
