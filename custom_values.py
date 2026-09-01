import sqlite3

import paths

"""
This database maps custom value IDs to their types.
For example, an ID might be "filament_color" and its type might be "color".
"""


def get_all_types() -> dict[str, str]:
    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    c = conn.cursor()
    c.execute("SELECT id, type FROM ids")
    result = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return result


def get_type(id: str) -> str | None:
    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    c = conn.cursor()
    c.execute("SELECT type FROM ids WHERE id=?", (id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def set_type(id: str, type: str) -> None:
    conn = sqlite3.connect(paths.CUSTOM_VALUE_TYPES)
    c = conn.cursor()
    c.execute("UPDATE ids SET type=? WHERE id=?", (type, id))
    conn.commit()
    conn.close()
