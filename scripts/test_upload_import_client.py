from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

csv_content = """patient_id,name,dob,diagnosis
P-1001,John Doe,1980-01-01,Flu
,Jane Smith,1990-05-05,Cold
"""
file_tuple = ('file', ('test_upload.csv', io.BytesIO(csv_content.encode('utf-8')), 'text/csv'))
resp = client.post('/api/uploads', files={'file': file_tuple[1]})
print('UPLOAD status', resp.status_code)
print(resp.json())

# import with dry_run
resp2 = client.post('/api/uploads/import', data={'filename': 'test_upload.csv', 'dry_run': 'true'})
print('IMPORT status', resp2.status_code)
print(resp2.json())
