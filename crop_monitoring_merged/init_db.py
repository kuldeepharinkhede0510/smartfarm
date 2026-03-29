import sqlite3

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # uploads: image-based predictions
    c.execute("""CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                crop_pred TEXT,
                disease_pred TEXT,
                fertilizer TEXT,
                pesticide TEXT,
                advice TEXT,
                timestamp TEXT
                )""")
    # sensor_data: numeric sensor entries (from earlier analyze form)
    c.execute("""CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                moisture REAL,
                pest_level REAL,
                prediction TEXT,
                created_at TEXT
                )""")
    conn.commit()
    conn.close()
    print("Database initialized at", DB_PATH)

if __name__ == "__main__":
    init_db()
