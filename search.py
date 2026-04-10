from rapidfuzz import fuzz
import database
import sqlite3
import paths


def to_fts_query(text: str) -> str:
    return " ".join(f"{word}*" for word in text.split())


# returns tuple: (total matches, list[the placement codes of the matches])
# max_results: maximum number of results to return. None returns all matches.
def search(
    query: str,
    only_leaves: bool,
    max_results: int | None,
    skip_number: int,
) -> tuple[int, list[str]]:
    only_leaves = only_leaves or False
    max_results = max_results or None
    skip_number = skip_number or 0

    def is_ok(placement_code: str) -> bool:
        ok = True
        if only_leaves and not database.is_leaf(placement_code):
            ok = False
        return ok

    if not query.strip() == "":
        conn = sqlite3.connect(paths.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        try:
            c.execute(
                """
                SELECT i.*, bm25(items_fts, 0.5, 0.1, 1.5, 1.0) AS score
                FROM items_fts
                JOIN items i ON i.rowid = items_fts.rowid
                WHERE items_fts MATCH ?
                ORDER BY score;
                """,
                (to_fts_query(query),),
            )
            candidates = c.fetchall()
        except sqlite3.OperationalError:
            # Syntax error, use backup search instead
            candidates = []

        if len(candidates) < 5:
            # TODO: Limit the number of results?
            c.execute(
                """
                SELECT placement_code, name, description, keywords FROM ITEMS;
                """
            )
            candidates = c.fetchall()
        conn.close()
    else:
        candidates = database.get_all(
            ["placement_code", "name", "description", "keywords"]
        )

    candidates = [c for c in candidates if is_ok(c["placement_code"])]

    if not query.strip() == "":
        results: list[tuple[float, str]] = []
        for row in candidates:
            score = max(
                1 * fuzz.partial_ratio(query, row["placement_code"]),
                5 * fuzz.ratio(query, row["name"]),
                2 * fuzz.partial_ratio(query, row["description"] or ""),
                4 * fuzz.partial_ratio(query, row["keywords"] or ""),
            )
            results.append((score, row["placement_code"]))
        results.sort(reverse=True, key=lambda x: x[0])
    else:
        results = [(0, c["placement_code"]) for c in candidates]
        results.sort(key=lambda x: x[1])

    # Apply skip and max_results
    if max_results is not None:
        results = results[skip_number : skip_number + max_results]
    else:
        results = results[skip_number:]
    return (len(candidates), [r[1] for r in results])
