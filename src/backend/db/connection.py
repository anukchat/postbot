from contextlib import contextmanager
import time
from typing import Generator
import backoff
from postgrest.exceptions import APIError
from supabase import create_client, Client
import os
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_KEY")
            self.pool = []
            self.max_connections = 10
            self.min_connections = 2
            self._initialize_pool()
            self.initialized = True

    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.min_connections):
            client = create_client(self.url, self.key)
            self.pool.append(client)

    @backoff.on_exception(
        backoff.expo,
        (APIError, Exception),
        max_tries=3,
        max_time=30
    )
    def get_connection(self) -> Client:
        """Get a connection with retry mechanism"""
        if not self.pool:
            client = create_client(self.url, self.key)
            return client
        return self.pool.pop()

    def release_connection(self, connection: Client):
        """Return connection to pool"""
        if len(self.pool) < self.max_connections:
            self.pool.append(connection)

    @contextmanager
    def connection(self) -> Generator[Client, None, None]:
        """Context manager for database connections"""
        connection = self.get_connection()
        try:
            yield connection
        finally:
            self.release_connection(connection)

    @contextmanager
    def transaction(self):
        """Context manager for database operations"""
        conn = self.get_connection()
        try:
            yield conn
        except Exception as e:
            # Log the error
            logger.error(f"Transaction failed: {str(e)}")
            raise e
        finally:
            self.release_connection(conn)

def db_retry(retries=3, delay=1):
    """Decorator for database operations with retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < retries - 1:
                        time.sleep(delay * (attempt + 1))
                    logger.error(f"Database operation failed: {str(e)}, attempt {attempt + 1}/{retries}")
            raise last_error
        return wrapper
    return decorator
