import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
try:
    import importlib
    m = importlib.import_module('app.models.workflow_models')
    print('Imported module:', m)
    print('Has Patient:', hasattr(m, 'Patient'))
    print('Has PatientVisit:', hasattr(m, 'PatientVisit'))
except Exception as e:
    import traceback
    traceback.print_exc()
