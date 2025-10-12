import requests
import json

UPLOAD_URL = 'http://127.0.0.1:8000/api/uploads'
IMPORT_URL = 'http://127.0.0.1:8000/api/uploads/import'

# prepare a small CSV
csv_content = """patient_id,name,dob,diagnosis
P-1001,John Doe,1980-01-01,Flu
,Jane Smith,1990-05-05,Cold
"""
with open('test_upload.csv', 'w', encoding='utf-8') as f:
    f.write(csv_content)

# mapping: none (use headers)
files = {'file': ('test_upload.csv', open('test_upload.csv', 'rb'), 'text/csv')}
resp = requests.post(UPLOAD_URL, files=files)
print('UPLOAD status', resp.status_code)
print(resp.json())

# import with dry_run
data = {'filename': 'test_upload.csv', 'dry_run': 'true'}
resp2 = requests.post(IMPORT_URL, data=data)
print('IMPORT status', resp2.status_code)
print(resp2.json())
