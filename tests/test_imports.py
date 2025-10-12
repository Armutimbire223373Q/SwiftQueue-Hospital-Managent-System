import io
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models.workflow_models import Patient, PatientVisit


client = TestClient(app)


def setup_module(module):
    # ensure tables exist and start from a known state
    # reset the DB so tests are deterministic: drop all tables then recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    # keep DB state as-is (tests rely on isolation via counts)
    pass


def test_atomic_import_rolls_back_on_failure():
    # snapshot counts
    session = SessionLocal()
    patients_before = session.query(Patient).count()
    visits_before = session.query(PatientVisit).count()
    session.close()

    csv_content = """patient_id,name,dob,diagnosis
P-TST1,Atomic Test,1990-01-01,Test
,Bad Row,1980-02-02,MissingID
"""
    files = {'file': ('atomic.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
    resp = client.post('/api/uploads/', files=files)
    assert resp.status_code == 200

    resp2 = client.post('/api/uploads/import', data={'filename': 'atomic.csv', 'dry_run': 'false'})
    assert resp2.status_code == 400

    session = SessionLocal()
    patients_after = session.query(Patient).count()
    visits_after = session.query(PatientVisit).count()
    session.close()

    assert patients_after == patients_before
    assert visits_after == visits_before


def test_real_import_inserts_rows_when_valid():
    session = SessionLocal()
    patients_before = session.query(Patient).count()
    visits_before = session.query(PatientVisit).count()
    session.close()

    csv_content = """patient_id,name,dob,diagnosis
P-TST2,Real Test,1991-02-02,OK
"""
    files = {'file': ('real.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv')}
    resp = client.post('/api/uploads/', files=files)
    assert resp.status_code == 200

    resp2 = client.post('/api/uploads/import', data={'filename': 'real.csv', 'dry_run': 'false'})
    # if validation fails, endpoint returns 400; otherwise 200
    assert resp2.status_code in (200, 201)

    session = SessionLocal()
    patients_after = session.query(Patient).count()
    visits_after = session.query(PatientVisit).count()
    session.close()

    assert patients_after >= patients_before + 1
    assert visits_after >= visits_before + 1
