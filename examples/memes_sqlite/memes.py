import sqlite3

DB_PATH = "memes.sqlite"


def get_connection():
    return sqlite3.connect(DB_PATH)


# --- INSERT ---


def add_meme(name, url):
    """Ajoute un meme dans la base de donnees."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO meme (name, url) VALUES (?, ?)", (name, url))
        conn.commit()


def add_meme_safe(name, url):
    """Ajoute un meme avec gestion d'erreur si le nom existe deja."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO meme (name, url) VALUES (?, ?)", (name, url))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        print("Ce meme existe deja")
        return False


# --- SELECT ---


def get_meme_url(name):
    """Recupere l'URL d'un meme par son nom."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM meme WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result[0] if result else None


def meme_exists(name):
    """Verifie si un meme existe dans la base."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM meme WHERE name = ?", (name,))
        return cursor.fetchone() is not None


def get_all_memes():
    """Recupere tous les memes de la base."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, url FROM meme")
        return cursor.fetchall()


# --- Exemple d'utilisation ---

if __name__ == "__main__":
    # Ajouter quelques memes
    add_meme_safe("doge", "https://example.com/doge.jpg")
    add_meme_safe("grumpy-cat", "https://example.com/grumpy.jpg")
    add_meme_safe("success-kid", "https://example.com/success.jpg")

    # Verifier si un meme existe
    print(f"doge existe: {meme_exists('doge')}")
    print(f"nyan-cat existe: {meme_exists('nyan-cat')}")

    # Recuperer l'URL d'un meme
    url = get_meme_url("doge")
    print(f"URL de doge: {url}")

    # Lister tous les memes
    print("\nTous les memes:")
    for meme in get_all_memes():
        print(f"\tID: {meme[0]}, Name: {meme[1]}, URL: {meme[2]}")
