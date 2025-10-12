import shutil, datetime, os
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
backend_db = repo_root / 'backend' / 'queue_management.db'

if backend_db.exists():
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = backend_db.parent / f"queue_management.db.bak.{ts}"
    shutil.copy2(backend_db, bak)
    print('Backed up', backend_db, 'to', bak)
else:
    print('No DB file found at', backend_db)

# remove the DB
try:
    if backend_db.exists():
        backend_db.unlink()
        print('Removed', backend_db)
except Exception as e:
    print('Failed to remove DB:', e)

# Recreate tables by calling the project's script
print('Recreating tables using scripts/create_tables.py')
import subprocess
subprocess.check_call(["python", str(repo_root / 'scripts' / 'create_tables.py')])
print('Done')
