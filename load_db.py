import pandas as pd
import sqlite3
import config
import os

def load_data():
    print(f"Connecting to {config.DB_NAME}...")
    conn = sqlite3.connect(config.DB_NAME)
    
    print("Loading users.csv...")
    users_df = pd.read_csv("users.csv")
    # Write to SQLite
    users_df.to_sql("users", conn, if_exists="replace", index=False)
    print(f"Loaded {len(users_df)} users.")
    
    print("Loading events.csv...")
    # Load in chunks to manage memory just in case
    chunksize = 100000
    first_chunk = True
    for chunk in pd.read_csv("events.csv", chunksize=chunksize):
        if first_chunk:
            chunk.to_sql("events", conn, if_exists="replace", index=False)
            first_chunk = False
        else:
            chunk.to_sql("events", conn, if_exists="append", index=False)
    
    # Create indexes for performance
    print("Creating indexes...")
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_token ON events(token);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);")
    conn.commit()
    
    # Let's check row count
    cursor.execute("SELECT COUNT(*) FROM events;")
    count = cursor.fetchone()[0]
    print(f"Loaded {count} events into database.")
    
    conn.close()
    print("Database load complete!")

if __name__ == "__main__":
    if not os.path.exists("users.csv") or not os.path.exists("events.csv"):
        print("CSV files not found. Please run generate_data.py first.")
    else:
        load_data()
