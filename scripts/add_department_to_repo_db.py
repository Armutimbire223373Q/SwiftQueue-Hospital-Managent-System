import sqlite3
from pathlib import Path

p = Path('queue_management.db')
print('Target DB:', p.resolve())
if not p.exists():
    print('DB not found; aborting')
    raise SystemExit(1)

conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("PRAGMA table_info('patient_visits')")
cols = [r[1] for r in cur.fetchall()]
print('Existing columns:', cols)
if 'department_id' not in cols:
    print('Adding department_id column to patient_visits')
    cur.execute('ALTER TABLE patient_visits ADD COLUMN department_id INTEGER')
    conn.commit()
    print('Added column')
else:
    print('department_id already present')

cur.execute("PRAGMA table_info('patient_visits')")
print('After change, cols:', cur.fetchall())
conn.close()
