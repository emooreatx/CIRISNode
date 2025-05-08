import sqlite3
import os

def init_db():
    db_path = 'cirisnode/db/active_tasks.db'
    schema_path = 'cirisnode/db/schema.sql'
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute the schema
    with open(schema_path, 'r') as schema_file:
        schema = schema_file.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    init_db()
