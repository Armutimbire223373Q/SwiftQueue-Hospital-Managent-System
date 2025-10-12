import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
import io
from app.models.workflow_models import Patient, PatientVisit

client = TestClient(app)

# Ensure tables exist
Base.metadata.create_all(bind=engine)

csv_content = """patient_id,name,dob,diagnosis
P-2001,Alice Alpha,1975-02-02,Hypertension
,P-2002,1988-03-03,Diabetes
"""
file_bytes = io.BytesIO(csv_content.encode('utf-8'))
files = {'file': ('test_real_import.csv', file_bytes, 'text/csv')}
resp = client.post('/api/uploads/', files=files)
print('UPLOAD status', resp.status_code)
print(resp.json())

# import with dry_run = false
resp2 = client.post('/api/uploads/import', data={'filename': 'test_real_import.csv', 'dry_run': 'false'})
print('IMPORT status', resp2.status_code)
print(resp2.json())

# Check DB
session = SessionLocal()
patients = session.query(Patient).filter(Patient.patient_id.like('P-%')).all()
visits = session.query(PatientVisit).all()
print('Patients in DB:', [(p.id, p.patient_id, p.name) for p in patients])
print('Visits in DB:', [(v.id, v.visit_id, v.patient_id) for v in visits])
session.close()
