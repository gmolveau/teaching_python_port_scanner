"""Minimalist SQLite database migration tool."""

import argparse
import os
import sqlite3
from datetime import datetime

# Configuration
DB_PATH = "db.sqlite"
MIGRATIONS_DIR = "migrations"


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_migrations_table(conn):
    """Create the migrator_version table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS migrator_version (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    """)
    conn.commit()


def get_current_version(conn):
    """Return the current migration version, or None if no migration has been applied."""
    cursor = conn.execute("SELECT version FROM migrator_version")
    row = cursor.fetchone()
    return row[0] if row else None


def get_available_migrations():
    """
    Read the migrations/ directory and return the sorted list of .sql files.
    Each file must start with a version number (e.g.: 001_create_users.sql).
    """
    if not os.path.isdir(MIGRATIONS_DIR):
        raise Exception(f"Error: folder '{MIGRATIONS_DIR}/' does not exist.")

    files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql"))
    return files


def parse_migration(filepath):
    """
    Parse a migration file and separate the UP and DOWN sections.

    Expected format:
        -- UP
        <SQL to apply>

        -- DOWN
        <SQL to rollback>
    """
    with open(filepath) as f:
        content = f.read()

    if "-- UP" not in content:
        raise Exception(
            f"Erreur: bad migration file {filepath} - does not contain '-- UP'"
        )

    if "-- DOWN" not in content:
        raise Exception(
            f"Erreur: bad migration file {filepath} - does not contain '-- DOWN'"
        )

    # Split content into UP and DOWN sections
    parts = content.split("-- DOWN")
    up_section = parts[0].split("-- UP")[1].strip()
    down_section = parts[1].strip()

    return up_section, down_section


def extract_version(filename):
    """Extract the version number from the filename (e.g.: '001' from '001_create_users.sql')."""
    return filename.split("_")[0]


# ---- Commands ----


def cmd_status():
    """Display the current migration status."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        current = get_current_version(conn)
        available = get_available_migrations()

    if not available:
        print("No migration found.")
        return

    ver_width = max(len("Version"), max(len(extract_version(f)) for f in available))
    file_width = max(len("File"), max(len(f) for f in available))

    print(f"{'Version':<{ver_width}}  {'File':<{file_width}}  {'Status'}")
    print("-" * (ver_width + file_width + 2 + 2 + len("pending")))

    for filename in available:
        version = extract_version(filename)
        if current is not None and version <= current:
            statut = "applied"
        else:
            statut = "pending"
        print(f"{version:<{ver_width}}  {filename:<{file_width}}  {statut}")


def cmd_up():
    """Apply all pending migrations, in order."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        current = get_current_version(conn)
        available = get_available_migrations()

        pending = [
            f for f in available if current is None or extract_version(f) > current
        ]

        if not pending:
            print("No pending migration.")
            return

        for filename in pending:
            version = extract_version(filename)
            filepath = os.path.join(MIGRATIONS_DIR, filename)
            up_sql, _ = parse_migration(filepath)

            print(f"Applying {filename}...")
            conn.executescript(up_sql)
            conn.execute("DELETE FROM migrator_version")
            conn.execute(
                "INSERT INTO migrator_version (version, applied_at) VALUES (?, ?)",
                (version, datetime.now().isoformat()),
            )
            conn.commit()
            print("\t-> OK")

    print(f"\n{len(pending)} migration{'s' if len(pending) > 1 else ''} applied.")


def cmd_down():
    """Rollback the last applied migration."""
    with get_connection() as conn:
        ensure_migrations_table(conn)
        current = get_current_version(conn)

        if current is None:
            print("No migration to revert.")
            return

        # Find the corresponding file
        available = get_available_migrations()
        filename = None
        for f in available:
            if extract_version(f) == current:
                filename = f
                break

        if not filename:
            raise Exception(
                f"Erreur: fichier de migration introuvable pour la version {current}"
            )

        filepath = os.path.join(MIGRATIONS_DIR, filename)
        _, down_sql = parse_migration(filepath)

        print(f"Rollback {filename}...")
        conn.executescript(down_sql)

        # Set version to the previous migration, or clear if this was the first
        applied = [f for f in available if extract_version(f) < current]
        conn.execute("DELETE FROM migrator_version")
        if applied:
            prev_version = extract_version(applied[-1])
            conn.execute(
                "INSERT INTO migrator_version (version, applied_at) VALUES (?, ?)",
                (prev_version, datetime.now().isoformat()),
            )
        conn.commit()
        print("\t-> OK")


def cmd_create(name):
    """Create a new migration file with the correct version number."""
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

    print(f"Migration created: {filepath}")


# ---- CLI ----


def cli():
    parser = argparse.ArgumentParser(
        description="Outil minimaliste de migration SQLite"
    )
    base_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser(
        "status",
        description="Voir l'état des migrations",
        help="Voir l'état des migrations",
        parents=[base_parser],
    )
    up_parser = subparsers.add_parser(
        "up",
        description="Appliquer les migrations",
        help="Appliquer toutes les migrations en attente",
        parents=[base_parser],
    )
    down_parser = subparsers.add_parser(
        "down",
        description="Annuler une migration",
        help="Annuler la dernière migration appliquée",
        parents=[base_parser],
    )

    create_parser = subparsers.add_parser(
        "create",
        description="Créer une migration",
        help="Créer un nouveau fichier de migration",
    )
    create_parser.add_argument(
        "name", help="Nom de la migration (ex: create_sessions_table)"
    )

    args = parser.parse_args()
    if args.command is None:
        parser.error("a command is required")
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
        raise argparse.ArgumentError("Unknown command. Use -h for help.")


if __name__ == "__main__":
    main()
