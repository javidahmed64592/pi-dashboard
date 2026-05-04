"""Unit tests for the pi_dashboard.db.notes_database_manager module."""

import pytest
from sqlalchemy.engine import Engine

from pi_dashboard.db import NotesDatabaseManager
from pi_dashboard.models import DatabaseAction, NoteEntry


class TestNotesDatabaseManager:
    """Tests for the NotesDatabaseManager class."""

    def test_init_creates_database(self, mock_notes_database_manager: NotesDatabaseManager) -> None:
        """Test NotesDatabaseManager initialization creates the database directory and file."""
        assert isinstance(mock_notes_database_manager.engine, Engine)

    def test_perform_note_action_create(
        self, mock_notes_database_manager: NotesDatabaseManager, mock_note_entry_2: NoteEntry
    ) -> None:
        """Test creating a note entry."""
        initial_note_count = len(mock_notes_database_manager.get_all_note_entries())
        note_id = mock_notes_database_manager.perform_note_action(mock_note_entry_2, DatabaseAction.CREATE)
        assert isinstance(note_id, int)
        assert len(mock_notes_database_manager.get_all_note_entries()) == initial_note_count + 1

    def test_perform_note_action_update(
        self, mock_notes_database_manager: NotesDatabaseManager, mock_note_entry_2: NoteEntry
    ) -> None:
        """Test updating a note entry."""
        initial_note = mock_notes_database_manager.get_all_note_entries()[0]
        mock_note_entry_2.id = initial_note.id
        note_id = mock_notes_database_manager.perform_note_action(mock_note_entry_2, DatabaseAction.UPDATE)
        assert isinstance(note_id, int)

        updated_note = mock_notes_database_manager.get_all_note_entries()[0]
        assert updated_note.title == mock_note_entry_2.title
        assert updated_note.content == mock_note_entry_2.content
        assert updated_note.time_updated >= initial_note.time_updated

    def test_perform_note_action_update_not_found(
        self, mock_notes_database_manager: NotesDatabaseManager, mock_note_entry_2: NoteEntry
    ) -> None:
        """Test updating a non-existent note entry."""
        mock_note_entry_2.id = 9999  # Non-existent ID
        with pytest.raises(ValueError, match=f"Note entry with ID {mock_note_entry_2.id} not found for update."):
            mock_notes_database_manager.perform_note_action(mock_note_entry_2, DatabaseAction.UPDATE)

    def test_perform_note_action_delete(self, mock_notes_database_manager: NotesDatabaseManager) -> None:
        """Test deleting a note entry."""
        initial_notes = mock_notes_database_manager.get_all_note_entries()
        note_to_delete = initial_notes[0]
        note_id = mock_notes_database_manager.perform_note_action(note_to_delete, DatabaseAction.DELETE)
        assert isinstance(note_id, int)
        assert len(mock_notes_database_manager.get_all_note_entries()) == len(initial_notes) - 1

    def test_perform_note_action_delete_not_found(
        self, mock_notes_database_manager: NotesDatabaseManager, mock_note_entry_2: NoteEntry
    ) -> None:
        """Test deleting a non-existent note entry."""
        mock_note_entry_2.id = 9999  # Non-existent ID
        with pytest.raises(ValueError, match=f"Note entry with ID {mock_note_entry_2.id} not found for deletion."):
            mock_notes_database_manager.perform_note_action(mock_note_entry_2, DatabaseAction.DELETE)
