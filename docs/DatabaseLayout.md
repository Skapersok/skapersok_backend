# Database layout

The backend stores its state in SQLite databases and in a small number of directories under the data/ tree.

## Persistent files

- data/data/database.db: contains the item hierarchy
- data/data/users.db: contains user accounts and roles
- data/data/img/mapimgs/: map images as image files
- data/data/img/descimgs/: description images as image files
- data/backups/: zip archives created by the backup system
- config/.env: runtime settings

## Item database schema

The main items table contains these columns:

| Column | Type | Description |
| --- | --- | --- |
| placement_code | TEXT PRIMARY KEY | Unique identifier for the item. The root uses an empty string. |
| name | TEXT NOT NULL | Human-readable item name. |
| description | TEXT | Optional description text. |
| keywords | TEXT | Optional search keywords. |
| children_arrangement | TEXT | Layout hint for children. See Gridsystem.md. |
| self_alignment | TEXT | Layout hint for the item itself. See Gridsystem.md. |
| color | TEXT | Optional color value. |

The database also includes an FTS5 virtual table named items_fts for full-text search.

## User database schema

The users table contains:

| Column | Type | Description |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | Internal numeric user id. |
| username | TEXT UNIQUE | Login username. |
| password_hash | TEXT | Argon2 password hash. |
| role | TEXT | Role such as admin, maintainer, editor, or viewer. |

## Image storage

Images are stored as files rather than in the database. The backend writes uploaded images into the corresponding map or description image folders and serves them through the image endpoints.
