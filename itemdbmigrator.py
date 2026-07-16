import sqlite3

import paths


def _table_exists(table_name: str) -> bool:
    try:
        conn = sqlite3.connect(paths.DATABASE_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        result = c.fetchone()
        conn.close()
        return result is not None
    except:
        return False


def _get_database_version() -> int | None:
    if not paths.DATABASE_PATH.exists():
        return None
    conn = sqlite3.connect(paths.DATABASE_PATH)
    return int(conn.execute("PRAGMA user_version;").fetchone()[0])


def _update_database_version(version: int):
    if not isinstance(version, int):
        raise ValueError("Version must be int.")

    conn = sqlite3.connect(paths.DATABASE_PATH)
    conn.execute(f"PRAGMA user_version = {version};")


# ====================
#    Incrementers
# ====================


def _nonetov0():
    paths.ensure_exists()

    conn = sqlite3.connect(paths.DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            placement_code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            keywords TEXT,
            children_arrangement TEXT,
            self_alignment TEXT,
            color TEXT
        );
    """)
    c.execute(
        "INSERT INTO items (placement_code, name) VALUES (?, ?)",
        (
            "",
            "Unnamed Server :(",
        ),
    )
    conn.commit()
    conn.close()

    _update_database_version(0)


def _v0tov1():
    """
    Rename the "inholders" table to "items" and fill in empty values for children_arrangement, self_alignment, and color.
    """

    # inholders -> items
    if _table_exists("inholders") and not _table_exists("items"):
        conn = sqlite3.connect(paths.DATABASE_PATH)
        c = conn.cursor()
        c.execute("ALTER TABLE inholders RENAME TO items;")
        conn.commit()
        conn.close()

    # Fill empty items
    conn = sqlite3.connect(paths.DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE items SET children_arrangement = '{\"type\": \"cloud\"}' WHERE children_arrangement IS NULL OR children_arrangement = '{}';"
    )
    c.execute(
        "UPDATE items SET self_alignment = '{\"type\": \"cloud_child\"}' WHERE self_alignment IS NULL OR self_alignment = '{}';"
    )
    c.execute("UPDATE items SET color = '#FFFFFF' WHERE color IS NULL;")
    conn.commit()
    conn.close()

    _update_database_version(1)


def _v1tov2():
    """
    Add a full-text search table for items.
    """

    conn = sqlite3.connect(paths.DATABASE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
            placement_code,
            name,
            description,
            keywords,
            content='items',
            content_rowid='rowid'
        );
        """)

    # Populate table
    c.execute("""
        INSERT INTO items_fts(rowid, placement_code, name, description, keywords)
        SELECT rowid, placement_code, name, description, keywords
        FROM items;
        """)

    # Create triggers
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
            INSERT INTO items_fts(rowid, placement_code, name, description, keywords)
            VALUES (new.rowid, new.placement_code, new.name, new.description, new.keywords);
        END;
        """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
            INSERT INTO items_fts(items_fts, rowid, placement_code, name, description, keywords)
            VALUES('delete', old.rowid, old.placement_code, old.name, old.description, old.keywords);
        END;
    """)
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
            INSERT INTO items_fts(items_fts, rowid, placement_code, name, description, keywords)
            VALUES('delete', old.rowid, old.placement_code, old.name, old.description, old.keywords);

            INSERT INTO items_fts(rowid, placement_code, name, description, keywords)
            VALUES (new.rowid, new.placement_code, new.name, new.description, new.keywords);
        END;
        """)
    conn.commit()
    conn.close()

    _update_database_version(2)


def _v2tov3():
    """
    Add the custom_values column to the database.
    """
    conn = sqlite3.connect(paths.DATABASE_PATH)
    c = conn.cursor()

    c.execute("""
        ALTER TABLE items ADD COLUMN custom_values TEXT;
    """)

    c.execute("""
        UPDATE items SET custom_values = '{}';
    """)

    conn.commit()
    conn.close()

    _update_database_version(3)


def _increment():
    """
    Increment the database version. Returns the database version after the upgrade.
    """
    version = _get_database_version()
    if version == None:
        _nonetov0()
    if version == 0:
        _v0tov1()
    elif version == 1:
        _v1tov2()
    elif version == 2:
        _v2tov3()
    return _get_database_version()


# IMPORTANT! When creating a new version n of the database:
# 1. Create a _v[n-1]tov[n] function
# 2. Set the below variable to n
NEWEST_DATABASE_VERSION = 3


def migrate():
    """
    Migrate the database schema to the latest version.
    """

    if _get_database_version() == NEWEST_DATABASE_VERSION:
        print(f"Database up to date (v{_get_database_version()}), no migration needed.")
        return

    version = _increment()
    print("Updated database to version", version)
    while version < NEWEST_DATABASE_VERSION:
        version = _increment()
        print("Updated database to version", version)


def is_up_to_date() -> bool:
    """
    Check if the database is up to date.
    """
    return _get_database_version() == NEWEST_DATABASE_VERSION
