from app.database import get_db_connection


def create_recipe(url: str, title: str | None = None, notes: str | None = None) -> int:
    """Create a new recipe and return its ID."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO recipes (url, title, notes) VALUES (?, ?, ?)",
        (url, title, notes),
    )
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    return recipe_id


def get_all_recipes() -> list[dict]:
    """Get all recipes ordered by most recent first."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, url, title, notes, created_at FROM recipes ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "url": row[1],
            "title": row[2],
            "notes": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]


def get_recipe_by_id(recipe_id: int) -> dict | None:
    """Get a single recipe by ID."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, url, title, notes, created_at FROM recipes WHERE id = ?",
        (recipe_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "id": row[0],
        "url": row[1],
        "title": row[2],
        "notes": row[3],
        "created_at": row[4],
    }


def delete_recipe(recipe_id: int) -> bool:
    """Delete a recipe by ID. Returns True if deleted, False if not found."""
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
