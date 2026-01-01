#!/usr/bin/env python3
"""
Seed Reference Data Script

This script seeds the database with required reference data.
Can be run standalone or imported as a module.

Usage:
    python seed_database.py
    python seed_database.py --env local
    python seed_database.py --database-url "postgresql://..."
"""

import os
import sys
from pathlib import Path
import argparse
from typing import Optional
import psycopg2
from psycopg2 import sql
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

SEED_DATA = {
    "generation_limits": [
        {"tier": "free", "max_generations": 5},
        {"tier": "basic", "max_generations": 20},
        {"tier": "premium", "max_generations": 1000},
    ],
    "source_types": [
        {"source_type_id": "9adce6f3-b254-47f5-8a7a-96fe8604488e", "name": "twitter"},
        {"source_type_id": "27c67d4f-d400-4883-9131-6c3d510ed11a", "name": "web_url"},
        {"source_type_id": "ec5df507-74f0-478f-9a8f-46420423dacb", "name": "topic"},
        {"source_type_id": "eac4b028-3064-44a9-8773-62dade8bd0ea", "name": "reddit"},
    ],
}


def get_database_url(env: Optional[str] = None) -> str:
    """Get database URL from environment or .env file."""
    if env:
        env_file = f".env.{env}"
    else:
        env_file = ".env.local" if os.path.exists(".env.local") else ".env"
    
    # Try to get from environment first
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # Try to get from .env file
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("DATABASE_URL"):
                    # Remove quotes if present
                    db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return db_url
    
    raise ValueError(f"DATABASE_URL not found in environment or {env_file}")


def seed_generation_limits(cursor):
    """Seed generation_limits table."""
    logger.info("Seeding generation_limits...")
    for limit in SEED_DATA["generation_limits"]:
        cursor.execute(
            """
            INSERT INTO generation_limits (tier, max_generations)
            VALUES (%(tier)s, %(max_generations)s)
            ON CONFLICT (tier) DO UPDATE
            SET max_generations = EXCLUDED.max_generations
            """,
            limit
        )
    cursor.execute("SELECT COUNT(*) FROM generation_limits")
    count = cursor.fetchone()[0]
    logger.info(f"  ✓ {count} generation limit tiers")


def seed_source_types(cursor):
    """Seed source_types table."""
    logger.info("Seeding source_types...")
    for source_type in SEED_DATA["source_types"]:
        cursor.execute(
            """
            INSERT INTO source_types (source_type_id, name, created_at)
            VALUES (%(source_type_id)s, %(name)s, NOW())
            ON CONFLICT (source_type_id) DO NOTHING
            """,
            source_type
        )
    cursor.execute("SELECT COUNT(*) FROM source_types")
    count = cursor.fetchone()[0]
    logger.info(f"  ✓ {count} source types")


def seed_database(database_url: str):
    """Seed the database with reference data."""
    # Redact password from connection string for logging
    safe_url = database_url.split('@')[1] if '@' in database_url else database_url
    logger.info(f"\n🌱 Seeding database...")
    logger.info(f"Database: {safe_url}\n")
    
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        try:
            seed_generation_limits(cursor)
            seed_source_types(cursor)
            
            conn.commit()
            logger.info("\n✅ Database seeded successfully!")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"\n❌ Error seeding database: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
            
    except psycopg2.Error as e:
        logger.error(f"❌ Database connection error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Seed database with reference data")
    parser.add_argument(
        "--env",
        choices=["local", "production"],
        help="Environment (uses .env.{env} file)"
    )
    parser.add_argument(
        "--database-url",
        help="Database URL (overrides .env files)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.database_url:
            database_url = args.database_url
        else:
            database_url = get_database_url(args.env)
        
        seed_database(database_url)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
