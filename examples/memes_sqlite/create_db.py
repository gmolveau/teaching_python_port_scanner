import sqlite3

DB_PATH = "memes.sqlite"


def create_database():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meme (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL
            )
        """)
        conn.commit()
    print(f"'{DB_PATH}' created")


if __name__ == "__main__":
    create_database()
