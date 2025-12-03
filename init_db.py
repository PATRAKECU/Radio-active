import sqlite3

def create_db():
    conn = sqlite3.connect("radioactive.db")
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()

if __name__ == "__main__":
    create_db()
    print("Database successfully created.")