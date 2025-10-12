import sqlite3
from pathlib import Path

root_db = Path('queue_management.db')
backend_db = Path('backend') / 'queue_management.db'

def info(p):
    print('\nDB path:', p)
    if not p.exists():
        print('  (not found)')
        return
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    print('  tables:', [r[0] for r in cur.fetchall()])
    cur.execute("PRAGMA table_info('patient_visits')")
    print('  patient_visits cols:', cur.fetchall())
    conn.close()

info(root_db)
info(backend_db)
