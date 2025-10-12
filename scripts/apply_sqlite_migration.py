import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / 'backend' / 'queue_management.db'
print('DB path:', db_path)
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("PRAGMA table_info('patient_visits')")
cols = [r[1] for r in cur.fetchall()]
print('Existing columns:', cols)

if 'department_id' not in cols:
    print('Adding department_id column to patient_visits')
    cur.execute('ALTER TABLE patient_visits ADD COLUMN department_id INTEGER')
    conn.commit()
    print('Column added')
else:
    print('department_id already exists')

conn.close()
