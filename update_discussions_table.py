import sqlite3

def update_discussions_table():
    conn = sqlite3.connect('instance/annuaire.db')
    cursor = conn.cursor()

    # Check if auteur_id column exists
    cursor.execute("PRAGMA table_info(discussions)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'auteur_id' not in columns:
        print("Adding auteur_id column to discussions table...")
        cursor.execute("ALTER TABLE discussions ADD COLUMN auteur_id INTEGER REFERENCES users(id)")

    if 'date_creation' not in columns:
        print("Adding date_creation column to discussions table...")
        cursor.execute("ALTER TABLE discussions ADD COLUMN date_creation DATETIME DEFAULT CURRENT_TIMESTAMP")

    conn.commit()
    conn.close()
    print("Database schema updated successfully!")

if __name__ == "__main__":
    update_discussions_table()
