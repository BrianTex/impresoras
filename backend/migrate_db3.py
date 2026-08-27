import sqlite3

def migrate():
    conn = sqlite3.connect('printers.db')
    c = conn.cursor()
    cols = [
        ("last_status", "VARCHAR DEFAULT 'Offline'"),
        ("last_checked_at", "DATETIME"),
        ("serial", "VARCHAR DEFAULT 'N/A'"),
        ("location", "VARCHAR DEFAULT 'N/A'"),
        ("page_count", "INTEGER DEFAULT 0"),
        ("copied_count", "INTEGER DEFAULT 0"),
        ("printed_count", "INTEGER DEFAULT 0"),
        ("two_sided_copied_count", "INTEGER DEFAULT 0"),
        ("two_sided_printed_count", "INTEGER DEFAULT 0"),
        ("toner_percent", "FLOAT DEFAULT 0"),
        ("daily_total", "INTEGER DEFAULT 0"),
        ("daily_copied", "INTEGER DEFAULT 0"),
        ("daily_printed", "INTEGER DEFAULT 0"),
        ("daily_two_sided_copied", "INTEGER DEFAULT 0"),
        ("daily_two_sided_printed", "INTEGER DEFAULT 0"),
        ("daily_toner_drop", "FLOAT DEFAULT 0.0"),
    ]
    for name, sqltype in cols:
        try:
            c.execute(f'ALTER TABLE printers ADD COLUMN {name} {sqltype}')
        except sqlite3.OperationalError as e:
            print(f"printers.{name} ya existe o error:", e)
    conn.commit()
    conn.close()
    print("Migración completa.")

if __name__ == '__main__':
    migrate()
