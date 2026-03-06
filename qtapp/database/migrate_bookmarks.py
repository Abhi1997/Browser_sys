import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import authentication
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from authentication import Authentication

def migrate():
    load_dotenv()
    auth = Authentication()
    
    # SQL to create the table
    sql = """
    CREATE TABLE IF NOT EXISTS Bookmarks (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        url VARCHAR(2048) NOT NULL,
        title VARCHAR(512) DEFAULT NULL,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_added (user_id, added_at),
        INDEX idx_user_id (user_id),
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    );
    """
    
    try:
        conn = auth._get_conn()
        cursor = conn.cursor()
        print("Applying Bookmarks table migration...")
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        print("Success: Bookmarks table created or already exists.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
