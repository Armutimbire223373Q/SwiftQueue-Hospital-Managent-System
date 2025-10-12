import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

# Import models so SQLAlchemy Base metadata includes them
import app.models.workflow_models as wm  # noqa: F401
from app.database import create_tables

print('Import complete, creating tables...')
create_tables()
print('Tables created (or already existed)')
