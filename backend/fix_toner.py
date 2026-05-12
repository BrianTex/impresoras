import sqlite3

def fix_db():
    conn = sqlite3.connect('printers.db')
    c = conn.cursor()
    # Reset all toner_changed to 0, they will be recreated correctly by the new code
    c.execute('UPDATE printer_history SET toner_changed = 0')
    conn.commit()
    conn.close()
    print("Fixed.")

if __name__ == "__main__":
    fix_db()
