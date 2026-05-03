"""SQLModel database module."""

import logging
from pathlib import Path

from sqlmodel import Field, SQLModel, create_engine

from pi_dashboard.models import DatabaseConfig

logger = logging.getLogger(__name__)


# Database table models
class NoteEntryDB(SQLModel, table=True):
    """Notes table."""

    __tablename__ = "notes"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(..., description="Title of the note entry")
    content: str = Field(..., description="Content of the note entry")
    time_created: int = Field(..., description="Unix timestamp when the note was created")
    time_updated: int = Field(..., description="Unix timestamp when the note was last updated")


# Database manager class
class DatabaseManager:
    """Manager class for database operations."""

    def __init__(self, db_config: DatabaseConfig) -> None:
        """Initialize the database manager."""
        self.db_config = db_config
        logger.info("Using database directory: %s", self.db_config.db_directory)
        Path(self.db_config.db_directory).mkdir(parents=True, exist_ok=True)

        logger.info("Initializing database with URL: %s", self.db_config.db_url)
        self.engine = create_engine(self.db_config.db_url, echo=False)
        SQLModel.metadata.create_all(self.engine)
