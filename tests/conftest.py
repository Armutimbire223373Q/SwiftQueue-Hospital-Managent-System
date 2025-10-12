import os
import tempfile
import shutil
import atexit

# Create a temporary directory for the test DB and set the environment variable at import time
# so the application picks it up when imported by tests.
_TMP_DB_DIR = tempfile.mkdtemp(prefix='pytest_db_')
_DB_PATH = os.path.join(_TMP_DB_DIR, 'test_queue_management.db')
_DB_URL = f"sqlite:///{_DB_PATH}"
os.environ['SQLALCHEMY_DATABASE_URL'] = _DB_URL


def _cleanup_temp_db():
    try:
        if os.path.exists(_DB_PATH):
            os.remove(_DB_PATH)
    except Exception:
        pass
    try:
        if os.path.exists(_TMP_DB_DIR):
            shutil.rmtree(_TMP_DB_DIR)
    except Exception:
        pass


atexit.register(_cleanup_temp_db)
