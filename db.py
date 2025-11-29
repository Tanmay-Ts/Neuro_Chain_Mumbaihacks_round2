from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Setup SQLite Database
DB_NAME = "neurochain.db"
engine = create_engine(f"sqlite:///{DB_NAME}", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Creates tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()