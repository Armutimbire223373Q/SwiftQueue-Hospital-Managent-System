import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.database import create_tables

print('Creating tables...')
create_tables()
print('Tables created')
