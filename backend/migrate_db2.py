import sqlite3

def migrate():
    conn = sqlite3.connect('printers.db')
    c = conn.cursor()
    
    # Try to add columns to printers
    try:
        c.execute('ALTER TABLE printers ADD COLUMN last_toner_install_date VARCHAR')
    except sqlite3.OperationalError as e:
        print("printers.last_toner_install_date already exists or error:", e)

    # Try to add columns to printer_history
    try:
        c.execute('ALTER TABLE printer_history ADD COLUMN toner_changed BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError as e:
        print("printer_history.toner_changed already exists or error:", e)

    # Create notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            printer_id INTEGER,
            message VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read BOOLEAN DEFAULT 0,
            FOREIGN KEY(printer_id) REFERENCES printers(id)
        )
    ''')
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
