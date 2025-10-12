from alembic import command
from alembic.config import Config
from pathlib import Path

cfg = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
command.upgrade(cfg, 'head')
print('Alembic migrations applied')
