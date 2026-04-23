import mysql.connector

try:
    print("Connecting to Hostinger DB...")
    # Import db credentials if possible, or use standard Hostinger setup if hardcoded or env based
    from authentication import Authentication
    class DummyApp:
        pass
    auth = Authentication(DummyApp())
    conn = auth._get_conn()
    cursor = conn.cursor()
    print("Connected.")
    
    queries = [
        "ALTER TABLE Students MODIFY COLUMN assigned_mode ENUM('cached', 'study', 'restricted', 'free', 'exam') DEFAULT 'restricted'",
        "ALTER TABLE ModeHistory MODIFY COLUMN old_mode ENUM('cached', 'study', 'restricted', 'free', 'exam')",
        "ALTER TABLE ModeHistory MODIFY COLUMN new_mode ENUM('cached', 'study', 'restricted', 'free', 'exam') NOT NULL",
        "ALTER TABLE WhitelistDomains MODIFY COLUMN mode ENUM('cached', 'study', 'restricted', 'free', 'exam') NOT NULL",
        "ALTER TABLE BlacklistDomains MODIFY COLUMN mode ENUM('cached', 'study', 'restricted', 'free', 'exam') NOT NULL",
        "ALTER TABLE ActivityLogs MODIFY COLUMN mode ENUM('cached', 'study', 'restricted', 'free', 'exam') NOT NULL",
        "ALTER TABLE Violations MODIFY COLUMN current_mode ENUM('cached', 'study', 'restricted', 'free', 'exam')"
    ]
    
    for q in queries:
        print(f"Executing: {q}")
        cursor.execute(q)
        print("Success.")
        
    conn.commit()
    cursor.close()
    conn.close()
    print("All migrations completed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
