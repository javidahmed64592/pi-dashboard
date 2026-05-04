"""SQLModel database module."""

import logging
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, col, create_engine, select

from pi_dashboard.models import DatabaseConfig, NoteAction, NoteEntry, current_timestamp_int

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

    @classmethod
    def from_note_entry(cls, note_entry: NoteEntry) -> "NoteEntryDB":
        """Create a NoteEntryDB instance from a NoteEntry."""
        return cls(
            id=note_entry.id,
            title=note_entry.title,
            content=note_entry.content,
            time_created=note_entry.time_created,
            time_updated=note_entry.time_updated,
        )

    def to_note_entry(self) -> NoteEntry:
        """Convert the database model to a NoteEntry."""
        return NoteEntry(
            id=self.id,
            title=self.title,
            content=self.content,
            time_created=self.time_created,
            time_updated=self.time_updated,
        )

    def update_from_note_entry(self, note_entry: NoteEntry) -> None:
        """Update the database model fields from a NoteEntry."""
        self.title = note_entry.title
        self.content = note_entry.content
        self.time_updated = current_timestamp_int()


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

    def _get_all_note_entries(self, session: Session) -> list[NoteEntry]:
        """Retrieve all note entries from the database."""
        statement = select(NoteEntryDB).order_by(col(NoteEntryDB.time_updated).desc())
        note_entries_db = session.exec(statement).all()
        return [note_db.to_note_entry() for note_db in note_entries_db]

    def _get_note_entry_by_id(self, session: Session, note_id: int) -> NoteEntryDB | None:
        """Retrieve a NoteEntryDB by its ID."""
        statement = select(NoteEntryDB).where(NoteEntryDB.id == note_id)
        return session.exec(statement).first()

    def _create_note_entry(self, session: Session, note_entry: NoteEntry) -> int:
        """Add a new note entry to the database."""
        timestamp = current_timestamp_int()
        note_entry.time_created = timestamp
        note_entry.time_updated = timestamp
        note_db = NoteEntryDB.from_note_entry(note_entry)
        session.add(note_db)
        session.commit()
        session.refresh(note_db)
        return note_db.id

    def _update_note_entry(self, session: Session, note_entry: NoteEntry, note_db: NoteEntryDB) -> int:
        """Update an existing note entry in the database."""
        note_db.update_from_note_entry(note_entry)
        session.add(note_db)
        session.commit()
        session.refresh(note_db)
        return note_db.id

    def _delete_note_entry(self, session: Session, note_db: NoteEntryDB) -> int:
        """Delete a note entry from the database."""
        session.delete(note_db)
        session.commit()
        return note_db.id

    def get_all_note_entries(self) -> list[NoteEntry]:
        """Public method to retrieve all note entries."""
        with Session(self.engine) as session:
            return self._get_all_note_entries(session)

    def perform_note_action(self, note_entry: NoteEntry, action: NoteAction) -> int:
        """Perform a note action (create/update/delete) on the database."""
        with Session(self.engine) as session:
            match action:
                case NoteAction.CREATE:
                    return self._create_note_entry(session, note_entry)
                case NoteAction.UPDATE:
                    if not (note_db := self._get_note_entry_by_id(session, note_entry.id)):
                        error_msg = f"Note entry with ID {note_entry.id} not found for update."
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    return self._update_note_entry(session, note_entry, note_db)
                case NoteAction.DELETE:
                    if not (note_db := self._get_note_entry_by_id(session, note_entry.id)):
                        error_msg = f"Note entry with ID {note_entry.id} not found for deletion."
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    return self._delete_note_entry(session, note_db)
