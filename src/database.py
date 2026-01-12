"""
Database connection and session management
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from models import Base


# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/diablo4_items'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv('SQL_ECHO', 'false').lower() == 'true',
    pool_pre_ping=True,  # Verify connections before using
    poolclass=NullPool if os.getenv('DB_POOL', 'true') == 'false' else None
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_db():
    """Drop all database tables (USE WITH CAUTION!)"""
    response = input("Are you sure you want to drop all tables? (yes/no): ")
    if response.lower() == 'yes':
        Base.metadata.drop_all(bind=engine)
        print("Database tables dropped")
    else:
        print("Operation cancelled")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Database session context manager

    Usage:
        with get_db() as db:
            items = db.query(ItemInstance).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session (caller responsible for closing)

    Usage:
        db = get_db_session()
        try:
            items = db.query(ItemInstance).all()
            db.commit()
        finally:
            db.close()
    """
    return SessionLocal()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init':
            init_db()
        elif command == 'drop':
            drop_db()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python database.py [init|drop]")
    else:
        print("Usage: python database.py [init|drop]")
