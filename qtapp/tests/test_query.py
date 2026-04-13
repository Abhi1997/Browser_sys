import os
import sys
from dotenv import load_dotenv
load_dotenv()
from authentication import Authentication

auth = Authentication()
try:
    conn = auth._get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, url, page_title FROM BrowsingHistory ORDER BY visited_at DESC LIMIT 5")
    rows = cursor.fetchall()
    print(f"Total rows fetched: {len(rows)}")
    for row in rows:
        print(row)
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Caught exception: {e}")
