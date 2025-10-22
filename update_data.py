import os
import requests
from dotenv import load_dotenv
from db import get_conn, create_table

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

CHANNELS = [
    {"id": "UC_x5XG1OV2P6uZZ5FSM9Ttw", "category": "기술"},  # Google Developers
    {"id": "UCsBjURrPoezykLs9EqgamOA", "category": "교육"},  # Fireship
    {"id": "UCVHFbqXqoYvEWM1Ddxl0QDg", "category": "게임"},  # PlayStation
]

def get_channel_data(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={API_KEY}"
    res = requests.get(url)
    data = res.json()

    if "items" not in data or len(data["items"]) == 0:
        print(f"❌ 채널 데이터를 불러오지 못했습니다: {channel_id}")
        return None

    item = data["items"][0]
    return {
        "channel_id": channel_id,
        "title": item["snippet"]["title"],
        "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
        "view_count": int(item["statistics"].get("viewCount", 0)),
        "video_count": int(item["statistics"].get("videoCount", 0))
    }

def update_channel_info(channel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO youtube_channels (channel_id, title, category, subscriber_count, view_count, video_count)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (channel_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            category = EXCLUDED.category,
            subscriber_count = EXCLUDED.subscriber_count,
            view_count = EXCLUDED.view_count,
            video_count = EXCLUDED.video_count,
            last_updated = NOW();
    """, (
        channel["channel_id"],
        channel["title"],
        channel["category"],
        channel["subscriber_count"],
        channel["view_count"],
        channel["video_count"]
    ))
    conn.commit()
    cur.close()
    conn.close()

def update_all_channels():
    create_table()
    for c in CHANNELS:
        data = get_channel_data(c["id"])
        if data:
            data["category"] = c["category"]
            update_channel_info(data)
            print(f"✅ 업데이트 완료: {data['title']}")
        else:
            print(f"⚠️ 실패: {c['id']}")

if __name__ == "__main__":
    update_all_channels()
