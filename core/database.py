from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Find the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Create the data folder if it does not already exist
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Location of our SQLite database
DATABASE_PATH = DATA_DIR / "payroll.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# Create the database connection engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Create database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Parent class for future database tables
class Base(DeclarativeBase):
    pass


def create_tables() -> None:
    """Create every database table that does not already exist."""
    Base.metadata.create_all(bind=engine)