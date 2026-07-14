"""
Database connection and session management.

Handles SQLite and PostgreSQL connections.
"""

import logging
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from scalping_bot.database.models import Base
from scalping_bot.config.settings import Settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize database.

        Args:
            settings: Settings object with database config
        """
        self.settings = settings or Settings()
        self.engine = None
        self.SessionLocal = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize database connection."""
        try:
            db_type = self.settings.database.type.lower()

            if db_type == "sqlite":
                # SQLite
                db_url = f"sqlite:///./{self.settings.database.sqlite_db}"
                self.engine = create_engine(
                    db_url,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool,
                )
            elif db_type == "postgresql":
                # PostgreSQL
                db_url = self.settings.database.postgresql_url
                self.engine = create_engine(
                    db_url,
                    pool_size=10,
                    max_overflow=20,
                )
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )

            # Create tables
            Base.metadata.create_all(bind=self.engine)
            logger.info(f"Database initialized: {db_type}")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def get_session(self) -> Session:
        """Get database session.

        Returns:
            SQLAlchemy session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    def health_check(self) -> bool:
        """Check database health.

        Returns:
            True if database is healthy
        """
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def __enter__(self) -> "Database":
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
