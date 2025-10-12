import shutil, datetime, os
root_db = 'queue_management.db'
if not os.path.exists(root_db):
    print('No repo-root DB found at', root_db)
else:
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f'{root_db}.bak.{ts}'
    shutil.copy2(root_db, bak)
    print('Backed up', root_db, 'to', bak)
