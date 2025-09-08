import time
import requests
from datetime import datetime
from .db import SessionLocal, init_db
from .models import FbPost
from . import config

GRAPH_URL = "https://graph.facebook.com/v23.0"

def run_once():
    if not (config.FB_PAGE_ACCESS_TOKEN and config.FB_PAGE_ID):
        print("FB_PAGE_ACCESS_TOKEN o FB_PAGE_ID no configurado; omitiendo ingesta de Facebook.")
        return

    fields = "id,message,created_time,permalink_url,shares,comments.summary(true),reactions.summary(true)"
    url = f"{GRAPH_URL}/{config.FB_PAGE_ID}/posts"
    params = {"fields": fields, "limit": 50, "access_token": config.FB_PAGE_ACCESS_TOKEN}
    new_count = 0
    with SessionLocal() as db:
        init_db()
        while True:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code in (429, 613):  # rate limit
                print("[FB] Rate limit, esperando 60s...")
                time.sleep(60)
                continue
            r.raise_for_status()
            data = r.json()
            for item in data.get("data", []):
                post_id = item["id"]
                message = item.get("message")
                created_time = datetime.fromisoformat(item["created_time"].replace("Z","+00:00"))
                permalink_url = item.get("permalink_url")
                shares = item.get("shares", {}).get("count", 0)
                comments = item.get("comments", {}).get("summary", {}).get("total_count", 0)
                reactions = item.get("reactions", {}).get("summary", {}).get("total_count", 0)
                if not db.get(FbPost, post_id):
                    fb = FbPost(
                        id=post_id,
                        message=message,
                        created_time=created_time,
                        permalink_url=permalink_url,
                        shares=shares,
                        comments=comments,
                        reactions=reactions,
                        raw=item
                    )
                    db.add(fb)
                    new_count += 1
            db.commit()
            next_url = data.get("paging", {}).get("next")
            if not next_url:
                break
            url = next_url
            params = {}
            time.sleep(1)
    print(f"[FB] Guardados nuevos: {new_count}")

if __name__ == "__main__":
    run_once()
