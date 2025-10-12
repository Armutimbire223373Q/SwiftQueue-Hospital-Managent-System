import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.database import Base, engine
import sqlite3

print('Dropping all tables...')
Base.metadata.drop_all(bind=engine)
print('Creating all tables...')
Base.metadata.create_all(bind=engine)

# inspect patient_visits
from urllib.parse import urlparse
url = str(engine.url)
if url.startswith('sqlite'):
    db_path = url.split('sqlite:///')[-1]
    print('DB path:', db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info('patient_visits')")
    print('patient_visits cols after recreate:', cur.fetchall())
    conn.close()
else:
    print('Non-sqlite DB; cannot inspect')
