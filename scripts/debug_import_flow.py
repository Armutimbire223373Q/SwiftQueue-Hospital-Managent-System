import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.workflow_models import Patient, PatientVisit


def run():
    client = TestClient(app)
    session = SessionLocal()
    before_p = session.query(Patient).count()
    before_v = session.query(PatientVisit).count()
    session.close()
    print('before patients, visits:', before_p, before_v)

    csv_content = """patient_id,name,dob,diagnosis
P-DBG1,Debug Test,1992-03-03,OK
"""
    files = {'file': ('dbg.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
    resp = client.post('/api/uploads/', files=files)
    print('upload status:', resp.status_code, resp.json())

    resp2 = client.post('/api/uploads/import', data={'filename': 'dbg.csv', 'dry_run': 'false'})
    print('import status:', resp2.status_code)
    try:
        print('import json:', resp2.json())
    except Exception as e:
        print('import json parse error:', e)

    session = SessionLocal()
    after_p = session.query(Patient).count()
    after_v = session.query(PatientVisit).count()
    print('after patients, visits:', after_p, after_v)
    # print recent patients
    for p in session.query(Patient).order_by(Patient.id.desc()).limit(5):
        print('patient:', p.id, p.patient_id, p.name)
    for v in session.query(PatientVisit).order_by(PatientVisit.id.desc()).limit(5):
        print('visit:', v.id, v.visit_id, v.patient_id)
    session.close()


if __name__ == '__main__':
    run()
