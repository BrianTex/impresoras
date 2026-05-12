import sqlite3

def migrate():
    conn = sqlite3.connect('printers.db')
    c = conn.cursor()
    
    # Try to add columns to daily_logs
    try:
        c.execute('ALTER TABLE daily_logs ADD COLUMN two_sided_copied_pages INTEGER DEFAULT 0')
    except sqlite3.OperationalError as e:
        print("daily_logs.two_sided_copied_pages already exists or error:", e)
        
    try:
        c.execute('ALTER TABLE daily_logs ADD COLUMN two_sided_printed_pages INTEGER DEFAULT 0')
    except sqlite3.OperationalError as e:
        print("daily_logs.two_sided_printed_pages already exists or error:", e)
        
    # Try to add columns to printer_history
    try:
        c.execute('ALTER TABLE printer_history ADD COLUMN daily_two_sided_copied INTEGER DEFAULT 0')
    except sqlite3.OperationalError as e:
        print("printer_history.daily_two_sided_copied already exists or error:", e)
        
    try:
        c.execute('ALTER TABLE printer_history ADD COLUMN daily_two_sided_printed INTEGER DEFAULT 0')
    except sqlite3.OperationalError as e:
        print("printer_history.daily_two_sided_printed already exists or error:", e)
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
