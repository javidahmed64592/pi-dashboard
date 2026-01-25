"""Notes handler module for managing note storage and operations."""

import json
import logging
from pathlib import Path

from pi_dashboard.models import Note, NotesCollection

logger = logging.getLogger(__name__)


class NotesHandler:
    """Handler for managing notes with persistent storage."""

    def __init__(self, data_dir: Path) -> None:
        """Initialize the NotesHandler.

        :param Path data_dir: Directory where notes.json will be stored
        """
        self.data_dir = data_dir
        self.notes_file = data_dir / "notes.json"
        self.collection = NotesCollection()
        self._load_or_create_notes_file()

    def _load_or_create_notes_file(self) -> None:
        """Load existing notes file or create a new one."""
        if not self.notes_file.exists():
            logger.info("Creating notes file at: %s", self.notes_file)
            self._write_notes()
        else:
            # Load existing notes
            try:
                with self.notes_file.open(encoding="utf-8") as f:
                    data = json.load(f)
                self.collection = NotesCollection.model_validate(data)
                logger.info("Loaded existing notes file from: %s", self.notes_file)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("Corrupted notes file, reinitializing: %s", e)
                self.collection = NotesCollection()
                self._write_notes()

    def _write_notes(self) -> None:
        """Write notes to the JSON file using atomic write operation."""
        temp_file = self.notes_file.with_suffix(".tmp")
        try:
            # Write to temporary file first
            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(self.collection.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
            # Atomic rename
            temp_file.replace(self.notes_file)
        except Exception:
            logger.exception("Failed to write notes file")
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
            raise

    def get_all_notes(self) -> list[Note]:
        """Get all notes.

        :return list[Note]: List of all notes
        """
        return self.collection.notes

    def get_note_by_id(self, note_id: str) -> Note | None:
        """Get a specific note by ID.

        :param str note_id: The UUID of the note to retrieve
        :return Note | None: The note if found, None otherwise
        """
        return self.collection.get_note_by_id(note_id)

    def create_note(self, title: str, content: str, current_timestamp: str) -> Note:
        """Create a new note.

        :param str title: The title of the note
        :param str content: The content of the note
        :param str current_timestamp: The current timestamp for created_at and updated_at
        :return Note: The created note with generated ID and timestamps
        """
        note = self.collection.add_note(title, content, current_timestamp)
        self._write_notes()
        logger.info("Created note: %s (ID: %s)", title, note.id)
        return note

    def update_note(
        self, note_id: str, current_timestamp: str, title: str | None = None, content: str | None = None
    ) -> Note | None:
        """Update an existing note.

        :param str note_id: The UUID of the note to update
        :param str current_timestamp: The current timestamp for updated_at
        :param str | None title: The new title (if provided)
        :param str | None content: The new content (if provided)
        :return Note | None: The updated note if found, None otherwise
        """
        note = self.collection.update_note(note_id, current_timestamp, title, content)
        if note is not None:
            self._write_notes()
            logger.info("Updated note: %s (ID: %s)", note.title, note_id)
        return note

    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID.

        :param str note_id: The UUID of the note to delete
        :return bool: True if the note was deleted, False if not found
        """
        success = self.collection.delete_note(note_id)
        if success:
            self._write_notes()
            logger.info("Deleted note: %s", note_id)
        return success
