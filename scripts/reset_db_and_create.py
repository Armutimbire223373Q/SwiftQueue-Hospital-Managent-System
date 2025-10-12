import sys
from pathlib import Path
import os

backend_dir = Path(__file__).resolve().parents[1] / 'backend'
db_path = backend_dir / 'queue_management.db'
if db_path.exists():
    print('Removing existing DB at', db_path)
    try:
        os.remove(db_path)
    except Exception as e:
        print('Failed to remove DB:', e)

sys.path.insert(0, str(backend_dir))
# import models and create tables
import app.models.workflow_models as wm  # noqa: F401
from app.database import create_tables

print('Creating tables...')
create_tables()
print('Done. Listing tables:')
import sqlite3
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cur.fetchall())
cur.execute("PRAGMA table_info('patient_visits')")
print('patient_visits cols:', cur.fetchall())
conn.close()
