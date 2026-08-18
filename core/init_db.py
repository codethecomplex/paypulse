from core.database import create_tables
from models import Employee

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")