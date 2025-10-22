import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Allow overriding the DB URL via environment variable for tests and deployments
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./queue_management.db")

# SQLite specific: disable same-thread check for SQLAlchemy usage across threads
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    # Import models so they are registered on the Base metadata before creating tables
    try:
        # import here to avoid circular imports at module import time
        import app.models.workflow_models  # noqa: F401
    except Exception:
        pass
    
    # Use checkfirst=True to avoid recreating existing indexes
    Base.metadata.create_all(bind=engine, checkfirst=True)

