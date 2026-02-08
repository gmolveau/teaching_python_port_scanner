"""Outil minimaliste de migration de base de données SQLite."""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

# Configuration
DB_PATH = "db.sqlite"
MIGRATIONS_DIR = "migrations"


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_migrations_table(conn):
    """Crée la table schema_migrations si elle n'existe pas."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    """)
    conn.commit()


def get_applied_migrations(conn):
    """Retourne la liste des versions de migrations déjà appliquées, triées."""
    cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY version")
    return [row[0] for row in cursor.fetchall()]


def get_available_migrations():
    """
    Lit le dossier migrations/ et retourne la liste des fichiers .sql triés.
    Chaque fichier doit commencer par un numéro de version (ex: 001_create_users.sql).
    """
    if not os.path.isdir(MIGRATIONS_DIR):
        print(f"Erreur: le dossier '{MIGRATIONS_DIR}/' n'existe pas.")
        sys.exit(1)

    files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql"))
    return files


def parse_migration(filepath):
    """
    Parse un fichier de migration et sépare les sections UP et DOWN.

    Le format attendu est :
        -- UP
        <SQL pour appliquer>

        -- DOWN
        <SQL pour annuler>
    """
    with open(filepath) as f:
        content = f.read()

    if "-- UP" not in content:
        print(f"Erreur: le fichier {filepath} ne contient pas de section '-- UP'")
        sys.exit(1)

    if "-- DOWN" not in content:
        print(f"Erreur: le fichier {filepath} ne contient pas de section '-- DOWN'")
        sys.exit(1)

    # Séparer le contenu en sections UP et DOWN
    parts = content.split("-- DOWN")
    up_section = parts[0].split("-- UP")[1].strip()
    down_section = parts[1].strip()

    return up_section, down_section


def extract_version(filename):
    """Extrait le numéro de version du nom de fichier (ex: '001' de '001_create_users.sql')."""
    return filename.split("_")[0]


# ---- Commandes ----


def cmd_status():
    """Affiche l'état actuel des migrations."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)
        available = get_available_migrations()

    if not available:
        print("Aucun fichier de migration trouvé.")
        return

    print(f"{'Version':<10} {'Fichier':<45} {'Statut'}")
    print("-" * 70)

    for filename in available:
        version = extract_version(filename)
        if version in applied:
            statut = "appliquée"
        else:
            statut = "en attente"
        print(f"{version:<10} {filename:<45} {statut}")


def cmd_up():
    """Applique toutes les migrations en attente, dans l'ordre."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)
        available = get_available_migrations()

        pending = [f for f in available if extract_version(f) not in applied]

        if not pending:
            print("Aucune migration en attente.")
            return

        for filename in pending:
            version = extract_version(filename)
            filepath = os.path.join(MIGRATIONS_DIR, filename)
            up_sql, _ = parse_migration(filepath)

            print(f"Applying {filename}...")
            conn.executescript(up_sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (version, datetime.now().isoformat()),
            )
            conn.commit()
            print(f"  -> OK")

    print(f"\n{len(pending)} migration(s) appliquée(s).")


def cmd_down():
    """Annule la dernière migration appliquée."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)

        if not applied:
            print("Aucune migration à annuler.")
            return

        last_version = applied[-1]

        # Trouver le fichier correspondant
        available = get_available_migrations()
        filename = None
        for f in available:
            if extract_version(f) == last_version:
                filename = f
                break

        if not filename:
            print(f"Erreur: fichier de migration introuvable pour la version {last_version}")
            sys.exit(1)

        filepath = os.path.join(MIGRATIONS_DIR, filename)
        _, down_sql = parse_migration(filepath)

        print(f"Rollback {filename}...")
        conn.executescript(down_sql)
        conn.execute("DELETE FROM schema_migrations WHERE version = ?", (last_version,))
        conn.commit()
        print(f"  -> OK")


def cmd_create(name):
    """Crée un nouveau fichier de migration avec le bon numéro de version."""
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)

    available = get_available_migrations()
    if available:
        last_version = int(extract_version(available[-1]))
        new_version = last_version + 1
    else:
        new_version = 1

    filename = f"{new_version:03d}_{name}.sql"
    filepath = os.path.join(MIGRATIONS_DIR, filename)

    with open(filepath, "w") as f:
        f.write("-- UP\n\n\n-- DOWN\n\n")

    print(f"Migration créée: {filepath}")


# ---- CLI ----


def cli():
    parser = argparse.ArgumentParser(description="Outil minimaliste de migration SQLite")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", description="Voir l'état des migrations", help="Voir l'état des migrations")
    subparsers.add_parser("up", description="Appliquer les migrations", help="Appliquer toutes les migrations en attente")
    subparsers.add_parser("down", description="Annuler une migration", help="Annuler la dernière migration appliquée")

    create_parser = subparsers.add_parser("create", description="Créer une migration", help="Créer un nouveau fichier de migration")
    create_parser.add_argument("name", help="Nom de la migration (ex: create_sessions_table)")

    args = parser.parse_args()
    return args


def main():
    args = cli()

    if args.command == "status":
        cmd_status()
    elif args.command == "up":
        cmd_up()
    elif args.command == "down":
        cmd_down()
    elif args.command == "create":
        cmd_create(args.name)
    else:
        print("Commande inconnue. Utilisez -h pour l'aide.")
        sys.exit(1)


if __name__ == "__main__":
    main()
