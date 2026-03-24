import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306))
    )
    cursor = conn.cursor()
    cursor.execute("SHOW CREATE TABLE BrowsingHistory")
    result = cursor.fetchone()
    if result:
        print("Table BrowsingHistory exists:")
        print(result[1])
    else:
        print("Table BrowsingHistory does not exist!")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
