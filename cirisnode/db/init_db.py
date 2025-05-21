import sqlite3

def initialize_database():
    """
    Initialize the database by executing the schema.sql file.
    """
    db_path = "cirisnode.db"
    schema_path = "schema.sql"

    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Read and execute the schema.sql file
    with open(schema_path, "r") as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)

    # Commit changes and close the connection
    connection.commit()
    connection.close()

    print(f"Database initialized successfully at {db_path}")

if __name__ == "__main__":
    initialize_database()
