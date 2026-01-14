# Guide SQLite avec Python

SQLite est une base de donnees. En python il existe le module `sqlite3` pour interagir avec une base de donnees sqlite.

Prenons pour exemple la gestion de `memes`.

Voici plusieurs snippets de code pour vous aider à mieux appréhender sqlite + python.

## Connexion à la base de donnees

```python
import sqlite3

# Connexion (cela cree le fichier s'il n'existe pas)
conn = sqlite3.connect(<chemin vers la db>)

# Curseur pour executer des requetes
cursor = conn.cursor()

# ... operations ...
# cursor.execute(...) par exemple

# Fermer la connexion
conn.close()
```

## Creer une table

```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS meme (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT NOT NULL
    )
""")
conn.commit()
```

## INSERT - Inserer des donnees

### Insertion simple

```python
cursor.execute(
    "INSERT INTO meme (name, url) VALUES (?, ?)",
    ("doge", "https://example.com/doge.jpg")
)
conn.commit()
```

> **Important** : Utilisez toujours `?` comme placeholder pour eviter les injections SQL.
> Ne jamais faire de concatenation de strings ou template ou autre comme : `f"INSERT INTO meme VALUES ('{name}', '{url}')"`

### Insertion avec gestion d'erreur

```python
try:
    cursor.execute(
        "INSERT INTO meme (name, url) VALUES (?, ?)",
        ("doge", "https://example.com/doge.jpg")
    )
    conn.commit()
except sqlite3.IntegrityError:
    print("Ce meme existe deja")
```

## SELECT - Recuperer des donnees

### Recuperer une seule ligne

```python
cursor.execute("SELECT url FROM meme WHERE name = ?", ("doge",))
result = cursor.fetchone()

if result:
    url = result[0]
    print(f"URL: {url}")
else:
    print("Meme non trouve")
```

### Recuperer toutes les lignes

```python
cursor.execute("SELECT id, name, url FROM meme")
rows = cursor.fetchall()

for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, URL: {row[2]}")
```

### Verifier si un enregistrement existe

```python
cursor.execute("SELECT 1 FROM meme WHERE name = ?", ("doge",))
exists = cursor.fetchone() is not None
print(f"Le meme existe: {exists}")
```

## Exemple complet

Cet exemple utilise un context manager (`with`) pour garantir que la connexion est fermée automatiquement, même en cas d'erreur.

```python
import sqlite3

DB_PATH = "db.sqlite"

def get_connection():
    return sqlite3.connect(DB_PATH)

def add_meme(name, url):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO meme (name, url) VALUES (?, ?)",
            (name, url)
        )
        conn.commit()

def get_meme_url(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url FROM meme WHERE name = ?",
            (name,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def meme_exists(name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM meme WHERE name = ?",
            (name,)
        )
        return cursor.fetchone() is not None
```

## Ressources

- [Documentation officielle sqlite3](https://docs.python.org/3/library/sqlite3.html)
