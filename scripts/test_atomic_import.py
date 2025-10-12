import sys
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models.workflow_models import Patient, PatientVisit
import io

client = TestClient(app)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Snapshot counts before
session = SessionLocal()
patients_before = session.query(Patient).count()
visits_before = session.query(PatientVisit).count()
session.close()

# CSV with one valid row and one invalid row (missing patient_id)
csv_content = """patient_id,name,dob,diagnosis
P-9001,Valid Person,1990-01-01,Cold
,MissingID,1980-01-02,Flu
"""
file_bytes = io.BytesIO(csv_content.encode('utf-8'))
files = {'file': ('test_atomic_import.csv', file_bytes, 'text/csv')}
resp = client.post('/api/uploads/', files=files)
print('UPLOAD status', resp.status_code)
print(resp.json())

# Now attempt import with dry_run=false; expect 400 and no rows persisted
resp2 = client.post('/api/uploads/import', data={'filename': 'test_atomic_import.csv', 'dry_run': 'false'})
print('IMPORT status', resp2.status_code)
print(resp2.json())

# Check DB counts after
session = SessionLocal()
patients_after = session.query(Patient).count()
visits_after = session.query(PatientVisit).count()
session.close()

print('patients_before', patients_before, 'patients_after', patients_after)
print('visits_before', visits_before, 'visits_after', visits_after)

if resp2.status_code == 400 and patients_before == patients_after and visits_before == visits_after:
	print('Atomic import behavior confirmed: no rows persisted on failure')
else:
	print('Atomic import FAILED: counts changed or unexpected status')
