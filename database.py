import sqlite3
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError
from fastapi import UploadFile
from pillow_heif import register_heif_opener
import os

import paths
import search as searching
import settings

register_heif_opener()


def _connect_for_write():
    # Use WAL for better concurrency and BEGIN IMMEDIATE to acquire write lock quickly.
    conn = sqlite3.connect(paths.DATABASE_PATH, timeout=30, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("BEGIN IMMEDIATE;")
    return conn


def _connect_for_read():
    conn = sqlite3.connect(paths.DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def verify_placement_code_syntax(placement_code: str) -> bool:
    if placement_code == "":
        return True

    parts = placement_code.split("-")
    for part in parts:
        is_valid = (
            part.isalnum() and part.isupper() and part.isascii()
        ) or part.isdigit()
        if not is_valid:
            return False

    return True


def get_parent_code(placement_code: str) -> str | None:
    if placement_code == "":
        return None

    parts = placement_code.split("-")
    if len(parts) == 1:
        return ""

    parent_code = "-".join(parts[:-1])
    return parent_code


def map_image_path(placement_code: str) -> Path:
    return paths.MAP_IMAGE_FOLDER / (placement_code + ".webp")


def description_image_path(placement_code: str) -> Path:
    return paths.DESCRIPTION_IMAGE_FOLDER / (placement_code + ".webp")


def construct_full(
    placement_code: str,
) -> None | dict[str, str | None]:
    if not isinstance(placement_code, str):
        return None

    conn = _connect_for_read()
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE placement_code = ?", (placement_code,))
    item = c.fetchone()
    conn.close()

    if not item:
        return None

    result = dict(item)
    result["has_map_image"] = has_map_image(placement_code)
    result["has_description_image"] = has_description_image(placement_code)

    return result


def construct(placement_code: str, columns: list[str]) -> None | dict[str, str | None]:
    if not isinstance(placement_code, str):
        return None

    conn = _connect_for_read()
    c = conn.cursor()
    db_colums = set(columns) - {"has_map_image", "has_description_image"}
    c.execute(
        "SELECT " + ", ".join(db_colums) + " FROM items WHERE placement_code = ?",
        (placement_code,),
    )
    item = c.fetchone()
    conn.close()

    if not item:
        return None

    result = {col: item[col] for col in columns if col in item.keys()}
    if "has_map_image" in columns:
        result["has_map_image"] = has_map_image(placement_code)
    if "has_description_image" in columns:
        result["has_description_image"] = has_description_image(placement_code)

    return result


def construct_multiple(
    placement_codes: list[str], columns: list[str]
) -> list[dict[str, str | None]]:
    conn = _connect_for_read()
    c = conn.cursor()
    db_colums = set(columns) - {"has_map_image", "has_description_image"}
    query = (
        "SELECT " + ", ".join(db_colums) + " FROM items WHERE placement_code IN ({seq})"
    ).format(seq=",".join(["?"] * len(placement_codes)))
    c.execute(query, placement_codes)
    items = c.fetchall()
    conn.close()

    # Map for fast lookup
    item_map = {item["placement_code"]: item for item in items}

    results = []
    for code in placement_codes:
        if code in item_map:
            item = item_map[code]
            result = {col: item[col] for col in item.keys()}
            result["has_map_image"] = has_map_image(code)
            result["has_description_image"] = has_description_image(code)
            results.append(result)

    return results


def construct_multiple_full(
    placement_codes: list[str],
) -> list[dict[str, str | None]]:
    conn = _connect_for_read()
    c = conn.cursor()

    # Get all column names from the table
    c.execute("PRAGMA table_info(items)")
    columns_info = c.fetchall()
    conn.close()

    db_columns = [col["name"] for col in columns_info]

    # Include computed columns
    all_columns = db_columns + ["has_map_image", "has_description_image"]

    return construct_multiple(placement_codes, all_columns)


def remove_root_and_None(
    items: list[dict[str, str | None] | None],
) -> list[dict[str, str | None]]:
    new_items: list[dict[str, str | None]] = []
    for item in items:
        if item is None:
            continue
        if item["placement_code"] == "":
            continue
        new_items.append(item)
    return new_items


def add(
    placement_code: str,
    name: str,
    description: str | None,
    keywords: str | None,
    children_arrangement: str | None,
    self_alignment: str | None,
    color: str | None,
):
    if not verify_placement_code_syntax(placement_code):
        raise ValueError("Invalid placement code syntax")

    conn = _connect_for_write()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO items (placement_code, name, description, keywords, children_arrangement, self_alignment, color) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                placement_code,
                name,
                description,
                keywords,
                children_arrangement,
                self_alignment,
                color,
            ),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Removes an inholder and all its children
def remove(placement_code: str):
    conn = _connect_for_write()
    try:
        c = conn.cursor()
        c.execute(
            "DELETE FROM items WHERE placement_code LIKE ?", (placement_code + "%",)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update(
    placement_code: str,
    name: str | None,
    description: str | None,
    keywords: str | None,
    children_arrangement: str | None,
    self_alignment: str | None,
    color: str | None,
):
    conn = _connect_for_write()
    try:
        c = conn.cursor()
        if name is not None:
            c.execute(
                "UPDATE items SET name = ? WHERE placement_code = ?",
                (name, placement_code),
            )
        if description is not None:
            c.execute(
                "UPDATE items SET description = ? WHERE placement_code = ?",
                (description, placement_code),
            )
        if keywords is not None:
            c.execute(
                "UPDATE items SET keywords = ? WHERE placement_code = ?",
                (keywords, placement_code),
            )
        if children_arrangement is not None:
            c.execute(
                "UPDATE items SET children_arrangement = ? WHERE placement_code = ?",
                (children_arrangement, placement_code),
            )
        if self_alignment is not None:
            c.execute(
                "UPDATE items SET self_alignment = ? WHERE placement_code = ?",
                (self_alignment, placement_code),
            )
        if color is not None:
            c.execute(
                "UPDATE items SET color = ? WHERE placement_code = ?",
                (color, placement_code),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_placement_code(
    old_placement_code: str,
    new_placement_code: str,
):
    # Perform the rename for the root + all descendants inside one transaction
    conn = _connect_for_write()
    try:
        c = conn.cursor()
        c.execute(
            "SELECT placement_code FROM items WHERE placement_code LIKE ?",
            (old_placement_code + "-%",),
        )
        rows = c.fetchall()
        children = [r[0] for r in rows]

        # Update root
        c.execute(
            "UPDATE items SET placement_code = ? WHERE placement_code = ?",
            (new_placement_code, old_placement_code),
        )

        # Update descendants; sort by length to update parents before deeper nodes
        for child in sorted(children, key=len):
            new_child_code = new_placement_code + child[len(old_placement_code) :]
            c.execute(
                "UPDATE items SET placement_code = ? WHERE placement_code = ?",
                (new_child_code, child),
            )

        conn.commit()

        os.replace(
            map_image_path(old_placement_code), map_image_path(new_placement_code)
        )
        os.replace(
            description_image_path(old_placement_code),
            description_image_path(new_placement_code),
        )

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def exists(placement_code: str) -> bool:
    return get(placement_code) is not None


def get(placement_code: str) -> None | dict[str, str | None]:
    return construct_full(placement_code)


def get_root() -> dict[str, str | None]:
    data = construct_full("")
    if data is None:
        raise ValueError("Root item not found in database")
    return data


async def _save_image_as_webp(dest_path: Path, file: UploadFile):

    if not str(dest_path).endswith(".webp"):
        dest_path = dest_path.with_suffix(".webp")

    content = await file.read()

    # Delete old image if exists
    dest_path.unlink(missing_ok=True)

    try:
        dest_path.write_bytes(content)
        # with Image.open(BytesIO(content)) as img:
        #    img = ImageOps.exif_transpose(img)
        #    has_alpha = "A" in img.getbands() or "transparency" in img.info
        #    save_img = img.convert("RGBA") if has_alpha else img.convert("RGB")
        # s    save_img.save(dest_path, format="webp", quality=settings.IMAGE_QUALITY)
    except UnidentifiedImageError:
        raise ValueError("Unsupported image format")
    except OSError:
        raise ValueError("Corrupted image file")
    except Exception as e:
        raise ValueError("Error processing image file: " + str(e))


async def set_map_image(placement_code: str, file: UploadFile):
    path = map_image_path(placement_code)
    await _save_image_as_webp(path, file)


async def set_description_image(placement_code: str, file: UploadFile):
    path = description_image_path(placement_code)
    await _save_image_as_webp(path, file)


def has_map_image(placement_code: str) -> bool:
    path = map_image_path(placement_code)
    return path.exists()


def has_description_image(placement_code: str) -> bool:
    path = description_image_path(placement_code)
    return path.exists()


def get_all(columns: list[str] | None = None) -> list[dict[str, str | None]]:
    conn = _connect_for_read()
    c = conn.cursor()
    if columns is not None:
        c.execute("SELECT " + ", ".join(columns) + " FROM items")
    else:
        c.execute("SELECT * FROM items")
    rows = c.fetchall()
    conn.close()

    return remove_root_and_None([construct_full(row[0]) for row in rows])


# If max_results is None, all matches are returned
# skip_number: number of initial results to skip
# returns tuple[total matches, list of placement codes of the matches]
def search(
    query: str, only_leaves: bool, max_results: int | None, skip_number: int = 0
) -> tuple[int, list[str]]:

    matches = searching.search(query, only_leaves, max_results, skip_number)

    # Remove root
    matches = (matches[0], [match for match in matches[1] if not match == ""])

    return matches


def get_siblings(placement_code: str):
    parent = "-".join(placement_code.split("-")[:-1])

    conn = _connect_for_read()
    c = conn.cursor()
    c.execute(
        """
        SELECT *
        FROM items
        WHERE placement_code LIKE ? || '%'
        """,
        (parent,),
    )

    matches = c.fetchall()
    conn.close()

    results = remove_root_and_None([construct_full(row[0]) for row in matches])

    # Remove the current
    results = [res for res in results if res["placement_code"] != placement_code]

    # Filter by depth in the hierarchy
    results = [
        res
        for res in results
        if len(res["placement_code"].split("-")) == len(placement_code.split("-"))
    ]

    return results


# returns a list of placement_codes
def get_children(placement_code: str) -> list[str]:
    if placement_code == "":
        children_codes = [child["placement_code"] for child in get_all()]
    else:
        conn = _connect_for_read()
        c = conn.cursor()
        c.execute(
            """
            SELECT placement_code
            FROM items
            WHERE placement_code LIKE ?
            """,
            (placement_code + "-%",),
        )
        children = c.fetchall()
        conn.close()

        children_codes = [r[0] for r in children]

    for index in range(len(children_codes) - 1, -1, -1):
        target_dash_count = placement_code.count("-") + 1 if placement_code != "" else 0
        if not children_codes[index].count("-") == target_dash_count:
            # Not a direct child
            del children_codes[index]

    return [code for code in children_codes if not code is None and code != ""]


# Returns false if not leaf, or non-existant, else Trye
def is_leaf(placement_code: str) -> bool:
    return len(get_children(placement_code)) == 0
