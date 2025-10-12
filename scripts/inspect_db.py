import sqlite3
from pathlib import Path
p = Path('backend') / 'queue_management.db'
print('DB exists:', p.exists(), 'path=', p)
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('tables:', cur.fetchall())
try:
    cur.execute("PRAGMA table_info('patient_visits')")
    print('patient_visits cols:', cur.fetchall())
except Exception as e:
    print('pragma error', e)
conn.close()
