import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS youtube_channels (
            id SERIAL PRIMARY KEY,
            channel_id TEXT UNIQUE,
            title TEXT,
            category TEXT,
            subscriber_count BIGINT,
            view_count BIGINT,
            video_count BIGINT,
            last_updated TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
