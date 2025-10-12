import sqlite3
from pathlib import Path
p = Path('backend') / 'queue_management.db'
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='patient_visits'")
print(cur.fetchall())
conn.close()
