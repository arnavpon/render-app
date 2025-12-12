from app.database import get_db_connection


# Cuisine functions
def get_or_create_cuisine(name: str) -> int:
    """Get cuisine ID by name, or create if not exists. Name stored lowercase."""
    name_lower = name.strip().lower()
    conn = get_db_connection()
    cursor = conn.execute("SELECT id FROM cuisines WHERE name = ?", (name_lower,))
    row = cursor.fetchone()
    if row:
        cuisine_id = row[0]
    else:
        cursor = conn.execute("INSERT INTO cuisines (name) VALUES (?)", (name_lower,))
        conn.commit()
        cuisine_id = cursor.lastrowid
    conn.close()
    return cuisine_id


def get_all_cuisines() -> list[dict]:
    """Get all cuisines ordered alphabetically."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT id, name FROM cuisines ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]


# Tag functions
def get_or_create_tag(name: str) -> int:
    """Get tag ID by name, or create if not exists. Name stored lowercase."""
    name_lower = name.strip().lower()
    conn = get_db_connection()
    cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (name_lower,))
    row = cursor.fetchone()
    if row:
        tag_id = row[0]
    else:
        cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name_lower,))
        conn.commit()
        tag_id = cursor.lastrowid
    conn.close()
    return tag_id


def get_all_tags() -> list[dict]:
    """Get all tags ordered alphabetically."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT id, name FROM tags ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in rows]


def get_tags_for_recipe(recipe_id: int) -> list[str]:
    """Get all tag names for a recipe."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT t.name FROM tags t
        JOIN recipe_tags rt ON t.id = rt.tag_id
        WHERE rt.recipe_id = ?
        ORDER BY t.name ASC
        """,
        (recipe_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


# URL functions
def get_urls_for_recipe(recipe_id: int) -> list[dict]:
    """Get all URLs for a recipe."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, url, label FROM recipe_urls WHERE recipe_id = ? ORDER BY created_at ASC",
        (recipe_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "url": row[1], "label": row[2]} for row in rows]


def add_url_to_recipe(recipe_id: int, url: str, label: str | None = None) -> int:
    """Add a URL to a recipe. Returns the URL ID."""
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO recipe_urls (recipe_id, url, label) VALUES (?, ?, ?)",
        (recipe_id, url.strip(), label.strip() if label else None),
    )
    conn.commit()
    url_id = cursor.lastrowid
    conn.close()
    return url_id


def update_url(url_id: int, url: str, label: str | None = None) -> bool:
    """Update a URL. Returns True if updated."""
    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE recipe_urls SET url = ?, label = ? WHERE id = ?",
        (url.strip(), label.strip() if label else None, url_id),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_url(url_id: int) -> bool:
    """Delete a URL. Returns True if deleted."""
    conn = get_db_connection()
    cursor = conn.execute("DELETE FROM recipe_urls WHERE id = ?", (url_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# Recipe functions
def create_recipe(
    name: str,
    cuisine_id: int,
    urls: list[dict] | None = None,
    tags: list[str] | None = None,
    notes: str | None = None,
) -> int:
    """Create a new recipe and return its ID.

    urls should be a list of dicts with 'url' and optional 'label' keys.
    """
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO recipes (name, cuisine_id, notes) VALUES (?, ?, ?)",
        (name.strip(), cuisine_id, notes),
    )
    conn.commit()
    recipe_id = cursor.lastrowid

    # Add URLs if provided
    if urls:
        for url_data in urls:
            url = url_data.get("url", "").strip()
            label = url_data.get("label", "").strip() or None
            if url:
                conn.execute(
                    "INSERT INTO recipe_urls (recipe_id, url, label) VALUES (?, ?, ?)",
                    (recipe_id, url, label),
                )
        conn.commit()

    # Add tags if provided
    if tags:
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                tag_id = get_or_create_tag(tag_name)
                conn.execute(
                    "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)",
                    (recipe_id, tag_id),
                )
        conn.commit()

    conn.close()
    return recipe_id


def get_all_recipes(search_query: str | None = None) -> list[dict]:
    """Get all recipes ordered by cuisine name, then recipe name.

    If search_query is provided, filter by name or tags (case-insensitive).
    """
    conn = get_db_connection()

    if search_query:
        search_term = f"%{search_query.lower()}%"
        cursor = conn.execute(
            """
            SELECT DISTINCT r.id, r.name, r.notes, r.created_at, c.name as cuisine_name, c.id as cuisine_id
            FROM recipes r
            JOIN cuisines c ON r.cuisine_id = c.id
            LEFT JOIN recipe_tags rt ON r.id = rt.recipe_id
            LEFT JOIN tags t ON rt.tag_id = t.id
            WHERE LOWER(r.name) LIKE ? OR LOWER(t.name) LIKE ?
            ORDER BY c.name ASC, r.name ASC
            """,
            (search_term, search_term),
        )
    else:
        cursor = conn.execute(
            """
            SELECT r.id, r.name, r.notes, r.created_at, c.name as cuisine_name, c.id as cuisine_id
            FROM recipes r
            JOIN cuisines c ON r.cuisine_id = c.id
            ORDER BY c.name ASC, r.name ASC
            """
        )
    rows = cursor.fetchall()
    conn.close()

    recipes = []
    for row in rows:
        recipe_id = row[0]
        urls = get_urls_for_recipe(recipe_id)
        tags = get_tags_for_recipe(recipe_id)
        recipes.append({
            "id": recipe_id,
            "name": row[1],
            "notes": row[2],
            "created_at": row[3],
            "cuisine": row[4],
            "cuisine_id": row[5],
            "urls": urls,
            "tags": tags,
        })
    return recipes


def get_recipe_by_id(recipe_id: int) -> dict | None:
    """Get a single recipe by ID."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT r.id, r.name, r.notes, r.created_at, c.name as cuisine_name, c.id as cuisine_id
        FROM recipes r
        JOIN cuisines c ON r.cuisine_id = c.id
        WHERE r.id = ?
        """,
        (recipe_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    urls = get_urls_for_recipe(recipe_id)
    tags = get_tags_for_recipe(recipe_id)
    return {
        "id": row[0],
        "name": row[1],
        "notes": row[2],
        "created_at": row[3],
        "cuisine": row[4],
        "cuisine_id": row[5],
        "urls": urls,
        "tags": tags,
    }


def update_recipe(
    recipe_id: int,
    name: str | None = None,
    cuisine_id: int | None = None,
    notes: str | None = None,
) -> bool:
    """Update a recipe's basic fields. Returns True if updated."""
    conn = get_db_connection()

    updates = []
    params = []

    if name is not None:
        updates.append("name = ?")
        params.append(name.strip())
    if cuisine_id is not None:
        updates.append("cuisine_id = ?")
        params.append(cuisine_id)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes.strip() if notes else None)

    if not updates:
        conn.close()
        return False

    params.append(recipe_id)
    cursor = conn.execute(
        f"UPDATE recipes SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def update_recipe_name(recipe_id: int, new_name: str) -> bool:
    """Update a recipe's name. Returns True if updated."""
    return update_recipe(recipe_id, name=new_name)


def update_recipe_tags(recipe_id: int, tags: list[str]) -> None:
    """Replace all tags for a recipe with new ones."""
    conn = get_db_connection()
    # Remove existing tags
    conn.execute("DELETE FROM recipe_tags WHERE recipe_id = ?", (recipe_id,))
    # Add new tags
    for tag_name in tags:
        tag_name = tag_name.strip()
        if tag_name:
            tag_id = get_or_create_tag(tag_name)
            conn.execute(
                "INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)",
                (recipe_id, tag_id),
            )
    conn.commit()
    conn.close()


def delete_recipe(recipe_id: int) -> bool:
    """Delete a recipe by ID. Returns True if deleted, False if not found."""
    conn = get_db_connection()
    # Delete related data first (cascade should handle this but being explicit)
    conn.execute("DELETE FROM recipe_tags WHERE recipe_id = ?", (recipe_id,))
    conn.execute("DELETE FROM recipe_urls WHERE recipe_id = ?", (recipe_id,))
    cursor = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
