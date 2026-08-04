import sqlite3
import paths


def _table_exists(table_name: str) -> bool:
    try:
        conn = sqlite3.connect(paths.USERBASE_PATH)
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
    if not paths.USERBASE_PATH.exists():
        return None

    conn = sqlite3.connect(paths.USERBASE_PATH)
    return int(conn.execute("PRAGMA user_version;").fetchone()[0])


def _update_database_version(version: int):
    if not isinstance(version, int):
        raise ValueError("Version must be int.")

    conn = sqlite3.connect(paths.USERBASE_PATH)
    conn.execute(f"PRAGMA user_version = {version};")


# ====================
#    Incrementers
# ====================


def _nonetov0():
    users_conn = sqlite3.connect(paths.USERBASE_PATH)
    c = users_conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        permissions TEXT NOT NULL
    );
    """)
    users_conn.commit()
    users_conn.close()

    _update_database_version(0)


def _v0tov1():
    users_conn = sqlite3.connect(paths.USERBASE_PATH)
    c = users_conn.cursor()
    # rename permissions column to role and set default value to "viewer"
    c.execute("ALTER TABLE users RENAME COLUMN permissions TO role;")
    c.execute("UPDATE users SET role = 'admin';")
    users_conn.commit()
    users_conn.close()

    _update_database_version(1)


def _increment():
    """
    Increment the database version. Returns the database version after the upgrade.
    """
    version = _get_database_version()
    if version == None:
        _nonetov0()
    elif version == 0:
        _v0tov1()
    else:
        raise ValueError(f"Unknown database version {version}.")
    return _get_database_version()


# IMPORTANT! When creating a new version n of the database:
# 1. Create a _v[n-1]tov[n] function
# 2. Set the below variable to n
NEWEST_DATABASE_VERSION = 1


def migrate():
    """
    Migrate the user database schema to the latest version.
    """

    initial_database_version = _get_database_version()

    if _get_database_version() == NEWEST_DATABASE_VERSION:
        print(
            f"User database up to date (v{_get_database_version()}), no migration needed."
        )
        return

    version = _increment()
    print("Updated user database to version", version)
    while version < NEWEST_DATABASE_VERSION:
        version = _increment()
        print("Updated user database to version", version)

    if initial_database_version is None:
        import auth

        auth.create_user("admin", "password", "admin")


def is_up_to_date() -> bool:
    """
    Check if the user database is up to date.
    """
    return _get_database_version() == NEWEST_DATABASE_VERSION
