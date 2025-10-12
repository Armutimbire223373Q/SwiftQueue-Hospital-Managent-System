from pathlib import Path
import sys
sys.path.insert(0, str(Path('.').resolve() / 'backend'))
from app import database
print('Engine URL =', database.engine.url)
# Import models
import app.models.workflow_models as wm
print('Imported workflow_models, PatientVisit attrs present?')
print('Has attribute department_id in class dict:', 'department_id' in wm.PatientVisit.__dict__)

Base = database.Base
if 'patient_visits' in Base.metadata.tables:
    cols = list(Base.metadata.tables['patient_visits'].c.keys())
    print('Base.metadata patient_visits columns:', cols)
    for c in Base.metadata.tables['patient_visits'].c:
        print('  -', c.name, type(c.type), c)
else:
    print('patient_visits not in Base.metadata.tables')
