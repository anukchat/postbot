import os
import logging
from contextlib import contextmanager
from typing import Generator
import backoff
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            dsn = os.getenv("SUPABASE_POSTGRES_DSN", "")
            self.engine = create_engine(
                dsn,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=300,
            )
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            self.initialized = True

    @backoff.on_exception(
        backoff.expo,
        SQLAlchemyError,
        max_tries=3,
        max_time=30
    )
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Session context manager with automatic cleanup"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        with self.session() as session:
            with session.begin():
                yield session

def db_retry(retries=3, delay=1):
    """Decorator for database operations with retry logic"""
    def decorator(func):
        @wraps(func)
        @backoff.on_exception(
            backoff.expo,
            SQLAlchemyError,
            max_tries=retries,
            max_time=delay * retries
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
