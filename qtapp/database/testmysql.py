# testmysql.py
import mysql.connector  # <- This was missing

# Connect to Hostinger MySQL
conn = mysql.connector.connect(
    host="srv1882.hstgr.io",
    user="u976383844_abhi097",
    password="!nN0v@tion113",
    database="u976383844_dces"
)

cursor = conn.cursor()

# Insert a test user
cursor.execute("""
    INSERT INTO Users (username, gmail, password_hash, role, is_active, created_at)
    VALUES ('testuser', 'test@example.com', 'abc123', 'student', 1, NOW())
""")

conn.commit()

# Fetch the inserted user
cursor.execute("SELECT * FROM Users WHERE username='testuser'")
print(cursor.fetchall())

# Close connection
conn.close()
