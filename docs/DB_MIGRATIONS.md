# Database migrations (Alembic)

This project now includes a minimal Alembic configuration to manage schema changes for the SQLite development DB (`queue_management.db`).

Quick commands (run from repo root):

- Install dev dependencies (if not already):

```powershell
py -3 -m pip install -r backend/requirements.txt
```

- Apply migrations (upgrade to head):

```powershell
py -3 scripts\run_migrations.py
```

- Create a new migration (manual flow):
  - Edit `alembic/versions/` to add a new revision file, or use `alembic revision --autogenerate -m "msg"` after configuring alembic.

Notes:
- The included Alembic setup is minimal and intended for development. For production, adapt the `alembic.ini` sqlalchemy.url to point at your production DB and review migration scripts carefully before applying.
- Alembic may not be able to perform column drops on SQLite; complex schema changes may require manual steps.
