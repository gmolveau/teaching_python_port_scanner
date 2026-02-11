from src.db import get_connection


def user_exists(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result is not None


def add_user(username, password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()


def get_user_by_username(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if not result:
            return None
        return {"id": result[0], "password": result[1]}


def get_user_by_id(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result:
            return None
        return {"id": result[0], "username": result[1]}
