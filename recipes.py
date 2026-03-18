"""
Recipe Collection App
A CLI app using SQLite to store, retrieve, update, and delete recipes.
"""

import sqlite3
import os

DB_FILE = "recipes.db"


# ─────────────────────────────────────────────
#  Database setup
# ─────────────────────────────────────────────

def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def initialize_db():
    """Create the recipes table if it doesn't already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                category    TEXT    NOT NULL,
                ingredients TEXT    NOT NULL,
                instructions TEXT   NOT NULL,
                prep_time   INTEGER,          -- minutes
                rating      INTEGER CHECK(rating BETWEEN 1 AND 10),
                notes       TEXT
            )
        """)
        conn.commit()


# ─────────────────────────────────────────────
#  CRUD helpers
# ─────────────────────────────────────────────

def create_recipe(name, category, ingredients, instructions,
                  prep_time=None, rating=None, notes=None):
    """Insert a new recipe and return its id."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO recipes (name, category, ingredients, instructions,
                                 prep_time, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, category, ingredients, instructions, prep_time, rating, notes))
        conn.commit()
        return cursor.lastrowid


def read_all_recipes():
    """Return every recipe, sorted by name."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()


def read_recipes_filtered(sort_by="name", category=None, min_rating=None):
    """
    Return recipes with optional filtering/sorting.
    sort_by: 'name' | 'rating' | 'prep_time'
    category: filter to a specific category (case-insensitive)
    min_rating: only show recipes with rating >= this value
    """
    valid_sorts = {"name", "rating", "prep_time"}
    if sort_by not in valid_sorts:
        sort_by = "name"

    query = "SELECT * FROM recipes WHERE 1=1"
    params = []

    if category:
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)

    if min_rating is not None:
        query += " AND rating >= ?"
        params.append(min_rating)

    query += f" ORDER BY {sort_by}"

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def read_recipe_by_id(recipe_id):
    """Return a single recipe by id, or None if not found."""
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()


def update_recipe(recipe_id, **fields):
    """
    Update one or more fields of an existing recipe.
    Only the fields passed as keyword arguments are changed.
    """
    allowed = {"name", "category", "ingredients", "instructions",
               "prep_time", "rating", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return 0

    set_clause = ", ".join(f"{col} = ?" for col in updates)
    values = list(updates.values()) + [recipe_id]

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE recipes SET {set_clause} WHERE id = ?", values
        )
        conn.commit()
        return cursor.rowcount


def delete_recipe(recipe_id):
    """Delete a recipe by id. Returns number of rows deleted."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        conn.commit()
        return cursor.rowcount


# ─────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────

def print_recipe_row(r):
    """Print a compact one-line summary of a recipe."""
    stars = ("★" * (r["rating"] or 0)).ljust(5)
    prep  = f"{r['prep_time']} min" if r["prep_time"] else "  —  "
    print(f"  [{r['id']:>3}]  {r['name']:<30}  {r['category']:<15}  "
          f"{stars}  {prep}")


def print_recipe_detail(r):
    """Print the full details of a recipe."""
    line = "─" * 60
    print(f"\n{line}")
    print(f"  ID       : {r['id']}")
    print(f"  Name     : {r['name']}")
    print(f"  Category : {r['category']}")
    print(f"  Prep     : {r['prep_time']} min" if r["prep_time"] else "  Prep     : —")
    print(f"  Rating   : {'★' * (r['rating'] or 0)} ({r['rating'] or 'unrated'})")
    print(f"\n  Ingredients:\n    {r['ingredients']}")
    print(f"\n  Instructions:\n    {r['instructions']}")
    if r["notes"]:
        print(f"\n  Notes:\n    {r['notes']}")
    print(line)


def print_recipe_table(rows):
    """Print a list of recipes as a table."""
    if not rows:
        print("  (no recipes found)")
        return
    print(f"\n  {'ID':>4}  {'Name':<30}  {'Category':<15}  {'Rating':<6}  Prep")
    print("  " + "─" * 66)
    for r in rows:
        print_recipe_row(r)
    print(f"\n  {len(rows)} recipe(s) found.")


def prompt(message, required=True):
    """Prompt the user for input, optionally marking it required."""
    while True:
        value = input(f"  {message}: ").strip()
        if value:
            return value
        if not required:
            return None
        print("  (this field is required — please enter a value)")


def prompt_int(message, required=False, min_val=None, max_val=None):
    """Prompt for an integer, with optional range validation."""
    while True:
        raw = input(f"  {message}: ").strip()
        if not raw:
            if required:
                print("  (required — please enter a number)")
                continue
            return None
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"  (must be at least {min_val})")
                continue
            if max_val is not None and val > max_val:
                print(f"  (must be at most {max_val})")
                continue
            return val
        except ValueError:
            print("  (please enter a whole number)")


def confirm(message):
    """Ask yes/no; returns True for 'y'."""
    return input(f"  {message} [y/N]: ").strip().lower() == "y"



def action_add():
    """Collect input and create a new recipe."""
    print("\n── Add New Recipe ─────────────────────────────")
    name         = prompt("Recipe name")
    category     = prompt("Category (e.g. Breakfast, Dinner, Dessert, Snack)")
    ingredients  = prompt("Ingredients (comma-separated or describe freely)")
    instructions = prompt("Instructions")
    prep_time    = prompt_int("Prep time in minutes (press Enter to skip)", min_val=0)
    rating       = prompt_int("Your rating 1-10 (press Enter to skip)", min_val=1, max_val=5)
    notes        = prompt("Any notes? (press Enter to skip)", required=False)

    rid = create_recipe(name, category, ingredients, instructions,
                        prep_time, rating, notes)
    print(f"\n  ✓ Recipe '{name}' saved with ID {rid}.")


def action_view_all():
    """Show all recipes."""
    print("\n── All Recipes ────────────────────────────────")
    rows = read_all_recipes()
    print_recipe_table(rows)


def action_search():
    """Filter/sort recipes by category, rating, or sort order."""
    print("\n── Search / Filter Recipes ────────────────────")
    print("  Sort by: (1) Name  (2) Rating  (3) Prep Time")
    sort_choice = input("  Choose sort [1]: ").strip() or "1"
    sort_map = {"1": "name", "2": "rating", "3": "prep_time"}
    sort_by = sort_map.get(sort_choice, "name")

    category   = prompt("Filter by category (press Enter to skip)", required=False)
    min_rating = prompt_int("Minimum rating 1-5 (press Enter to skip)", min_val=1, max_val=5)

    rows = read_recipes_filtered(sort_by=sort_by, category=category,
                                 min_rating=min_rating)
    print_recipe_table(rows)


def action_view_detail():
    """Show full details of one recipe."""
    print("\n── View Recipe Detail ─────────────────────────")
    rid = prompt_int("Enter recipe ID", required=True, min_val=1)
    recipe = read_recipe_by_id(rid)
    if recipe:
        print_recipe_detail(recipe)
    else:
        print(f"  No recipe found with ID {rid}.")


def action_update():
    """Update fields of an existing recipe."""
    print("\n── Update Recipe ───────────────────────────────")
    rid = prompt_int("Enter recipe ID to update", required=True, min_val=1)
    recipe = read_recipe_by_id(rid)
    if not recipe:
        print(f"  No recipe found with ID {rid}.")
        return

    print(f"\n  Updating: {recipe['name']}")
    print("  (press Enter to keep the current value)\n")

    fields = {}

    val = input(f"  Name [{recipe['name']}]: ").strip()
    if val:
        fields["name"] = val

    val = input(f"  Category [{recipe['category']}]: ").strip()
    if val:
        fields["category"] = val

    val = input(f"  Ingredients (current: {recipe['ingredients'][:40]}…): ").strip()
    if val:
        fields["ingredients"] = val

    val = input(f"  Instructions (press Enter to skip): ").strip()
    if val:
        fields["instructions"] = val

    val = input(f"  Prep time [{recipe['prep_time']} min]: ").strip()
    if val:
        try:
            fields["prep_time"] = int(val)
        except ValueError:
            print("  (invalid number — prep time unchanged)")

    val = input(f"  Rating [{recipe['rating']}]: ").strip()
    if val:
        try:
            r = int(val)
            if 1 <= r <= 5:
                fields["rating"] = r
            else:
                print("  (rating must be 1-5 — unchanged)")
        except ValueError:
            print("  (invalid number — rating unchanged)")

    val = input(f"  Notes [{recipe['notes'] or '—'}]: ").strip()
    if val:
        fields["notes"] = val

    if not fields:
        print("  No changes made.")
        return

    rows_changed = update_recipe(rid, **fields)
    if rows_changed:
        print(f"\n  ✓ Recipe {rid} updated successfully.")
    else:
        print("  Update failed — please check the ID.")


def action_delete():
    """Delete a recipe after confirmation."""
    print("\n── Delete Recipe ───────────────────────────────")
    rid = prompt_int("Enter recipe ID to delete", required=True, min_val=1)
    recipe = read_recipe_by_id(rid)
    if not recipe:
        print(f"  No recipe found with ID {rid}.")
        return

    print(f"\n  You are about to delete: '{recipe['name']}'")
    if confirm("Are you sure?"):
        delete_recipe(rid)
        print(f"  ✓ Recipe '{recipe['name']}' deleted.")
    else:
        print("  Cancelled.")



MENU = """
╔══════════════════════════════════════╗
║       Recipe Collection              ║
╠══════════════════════════════════════╣
║  1. Add a new recipe                 ║
║  2. View all recipes                 ║
║  3. Search / filter recipes          ║
║  4. View recipe details              ║
║  5. Update a recipe                  ║
║  6. Delete a recipe                  ║
║  0. Quit                             ║
╚══════════════════════════════════════╝
"""

ACTIONS = {
    "1": action_add,
    "2": action_view_all,
    "3": action_search,
    "4": action_view_detail,
    "5": action_update,
    "6": action_delete,
}


def main():
    initialize_db()


    while True:
        print(MENU)
        choice = input("  Your choice: ").strip()

        if choice == "0":
            print("\n  Goodbye! Happy cooking \n")
            break
        elif choice in ACTIONS:
            ACTIONS[choice]()
            input("\n  Press Enter to return to the menu...")
        else:
            print("  Invalid choice — please enter a number from the menu.")


if __name__ == "__main__":
    main()