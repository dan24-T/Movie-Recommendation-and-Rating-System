import sqlite3

def add_timestamp_column():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Add the `timestamp` column to the `reviews` table
    try:
        cur.execute("ALTER TABLE reviews ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        print("Column `timestamp` added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_timestamp_column()
