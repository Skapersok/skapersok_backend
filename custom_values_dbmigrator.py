import sqlite3

import paths


def _table_exists(table_name: str) -> bool:
    try:
        conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
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


def proper_database() -> bool:
    return paths.CUSTOM_VALUE_TYPES.exists() and _table_exists("ids")


def create_database() -> None:
    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ids (
            id TEXT PRIMARY KEY,
            type TEXT
        )
        """)
    conn.commit()
    conn.close()


def _get_database_version() -> int | None:
    if not paths.CUSTOM_VALUE_TYPES.exists():
        return None

    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    return int(conn.execute("PRAGMA user_version;").fetchone()[0])


def _update_database_version(version: int):
    if not isinstance(version, int):
        raise ValueError("Version must be int.")

    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    conn.execute(f"PRAGMA user_version = {version};")


# ====================
#    Incrementers
# ====================


def _nonetov0():
    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ids (
            id TEXT PRIMARY KEY,
            type TEXT
        )
        """)
    conn.commit()
    conn.close()

    _update_database_version(0)


def _increment():
    """
    Increment the database version. Returns the database version after the upgrade.
    """
    version = _get_database_version()
    if version == None:
        _nonetov0()
    else:
        raise ValueError(f"Unknown database version {version}.")
    return _get_database_version()


# IMPORTANT! When creating a new version n of the database:
# 1. Create a _v[n-1]tov[n] function
# 2. Set the below variable to n
NEWEST_DATABASE_VERSION = 0


def migrate():
    """
    Migrate the custom values database schema to the latest version.
    """

    if _get_database_version() == NEWEST_DATABASE_VERSION:
        print(
            f"Custom values database up to date (v{_get_database_version()}), no migration needed."
        )
        return

    version = _increment()
    print("Updated custom values database to version", version)
    while version < NEWEST_DATABASE_VERSION:
        version = _increment()
        print("Updated custom values database to version", version)


def is_up_to_date() -> bool:
    """
    Check if the custom values database is up to date.
    """
    return _get_database_version() == NEWEST_DATABASE_VERSION
