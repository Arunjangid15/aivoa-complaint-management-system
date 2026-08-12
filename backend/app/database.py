"""
Database connection setup.
Works with either Postgres or MySQL — just change DATABASE_URL in .env

Postgres example:
    DATABASE_URL=postgresql://user:password@localhost:5432/aivoa_complaints

MySQL example:
    DATABASE_URL=mysql+pymysql://user:password@localhost:3306/aivoa_complaints
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aivoa_complaints"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
