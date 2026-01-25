"""Tests for notes handler."""

from pi_dashboard.models import Note, NotesCollection
from pi_dashboard.notes_handler import NotesHandler


class TestNotesHandler:
    """Tests for the NotesHandler class."""

    def test_get_all_notes(self, mock_notes_handler: NotesHandler, mock_notes_collection: NotesCollection) -> None:
        """Test retrieving all notes."""
        notes = mock_notes_handler.get_all_notes()
        assert notes == mock_notes_collection.notes

    def test_get_note_by_id(self, mock_notes_handler: NotesHandler, mock_note: Note) -> None:
        """Test retrieving a note by ID."""
        note = mock_notes_handler.get_note_by_id(mock_note.id)
        assert note == mock_note

    def test_create_note(self, mock_notes_handler: NotesHandler) -> None:
        """Test creating a new note."""
        title = "New Note"
        content = "This is a new note."
        current_timestamp = "2026-01-01T12:00:00Z"

        note = mock_notes_handler.create_note(
            title=title,
            content=content,
            current_timestamp=current_timestamp,
        )

        assert isinstance(note.id, str)
        assert note.title == title
        assert note.content == content
        assert note.created_at == current_timestamp
        assert note.updated_at == current_timestamp

    def test_update_note(self, mock_notes_handler: NotesHandler, mock_note: Note) -> None:
        """Test updating an existing note."""
        new_title = "Updated Note Title"
        new_content = "This is the updated content."
        current_timestamp = "2026-01-01T13:00:00Z"

        updated_note = mock_notes_handler.update_note(
            note_id=mock_note.id,
            current_timestamp=current_timestamp,
            title=new_title,
            content=new_content,
        )

        assert updated_note is not None
        assert updated_note.id == mock_note.id
        assert updated_note.title == new_title
        assert updated_note.content == new_content
        assert updated_note.updated_at == current_timestamp

    def test_delete_note(self, mock_notes_handler: NotesHandler, mock_note: Note) -> None:
        """Test deleting a note."""
        success = mock_notes_handler.delete_note(mock_note.id)
        assert success is True

        # Verify the note is no longer retrievable
        deleted_note = mock_notes_handler.get_note_by_id(mock_note.id)
        assert deleted_note is None
