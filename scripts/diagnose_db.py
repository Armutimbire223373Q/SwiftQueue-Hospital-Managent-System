import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from app import database
print('SQLALCHEMY_DATABASE_URL =', database.SQLALCHEMY_DATABASE_URL)
print('Engine URL =', database.engine.url)

# Import models explicitly
try:
    import app.models.workflow_models as wm
    print('Imported app.models.workflow_models')
except Exception as e:
    print('Failed to import models:', e)

Base = database.Base
print('Registered tables in Base.metadata BEFORE create_all:', list(Base.metadata.tables.keys()))

print('Calling Base.metadata.create_all(bind=engine)')
Base.metadata.create_all(bind=database.engine)

print('Registered tables in Base.metadata AFTER create_all:', list(Base.metadata.tables.keys()))

# Inspect sqlite_master
import sqlite3
from urllib.parse import urlparse
url = str(database.engine.url)
if url.startswith('sqlite'):
    db_path = url.split('sqlite:///')[-1]
    print('DB path resolved:', db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('sqlite_master tables:', cur.fetchall())
    try:
        cur.execute("PRAGMA table_info('patient_visits')")
        print('patient_visits cols:', cur.fetchall())
    except Exception as e:
        print('PRAGMA error:', e)
    conn.close()
else:
    print('Non-sqlite DB, skipping sqlite inspection')
