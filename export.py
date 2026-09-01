import json
import shutil
import sqlite3
from pathlib import Path

import paths


def export_database(export_name: Path):
    """
    Export the databse to a zip file containing all the images and a JSON representation of the data.
    """

    export_path = Path("exports").resolve()

    # Check if export already exists
    if (export_path / export_name).exists():
        raise ValueError("Export already exists")

    export_path.mkdir(parents=True, exist_ok=True)
    tmp_path = export_path / export_name
    tmp_path.mkdir(exist_ok=True)

    shutil.copytree(paths.IMAGE_FOLDER, tmp_path / "img")

    # Connect to the database and export data
    conn = sqlite3.connect(paths.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = [dict(row) for row in cursor.fetchall()]
    version = int(cursor.execute("PRAGMA user_version").fetchone()[0])
    conn.close()

    with open(tmp_path / "data.json", "w") as f:
        json.dump({"version": version, "items": items}, f, indent=4)

    # Connect and export user data
    conn = sqlite3.connect(paths.USERBASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    version = int(cursor.execute("PRAGMA user_version").fetchone()[0])
    conn.close()

    with open(tmp_path / "users.json", "w") as f:
        json.dump({"version": version, "users": users}, f, indent=4)

    shutil.make_archive(str(export_path / export_name), "zip", tmp_path)
    shutil.rmtree(tmp_path)


if __name__ == "__main__":
    name = input("Enter export name: ")
    export_database(Path(name))
