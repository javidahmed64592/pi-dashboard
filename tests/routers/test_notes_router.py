"""Unit tests for the pi_dashboard.routers.notes_router module."""

import asyncio
import time
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.routing import APIRoute

from pi_dashboard.models import (
    DatabaseAction,
    NoteEntry,
    NotesActionRequest,
)
from pi_dashboard.routers import NotesRouter


class TestRoutes:
    """Unit tests for route setup in NotesRouter."""

    def test_setup_routes(self, mock_notes_router: NotesRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_notes_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/notes/",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes


class TestGetNotesEndpoint:
    """Integration and unit tests for the /notes endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_get_notes(self, mock_notes_router: NotesRouter, mock_request_object: Request) -> None:
        """Test the /notes method handles valid JSON."""
        response = asyncio.run(mock_notes_router.get_notes(mock_request_object))

        assert response.message == "Retrieved 1 note entries"
        assert len(response.notes) == 1


class TestPerformNoteActionEndpoint:
    """Integration and unit tests for the /notes endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_perform_note_action(
        self,
        mock_notes_router: NotesRouter,
        mock_request_object: Request,
        mock_note_entry_1: NoteEntry,
        mock_note_entry_2: NoteEntry,
    ) -> None:
        """Test the /notes method handles valid JSON."""
        # Create note
        create_response = asyncio.run(
            mock_notes_router.perform_note_action(
                mock_request_object, NotesActionRequest(action=DatabaseAction.CREATE, note=mock_note_entry_2)
            )
        )

        assert create_response.message == "Note entry created successfully"

        created_note_id = create_response.note_id
        assert isinstance(created_note_id, int)

        all_notes = asyncio.run(mock_notes_router.get_notes(mock_request_object)).notes
        created_note = next(note for note in all_notes if note.id == created_note_id)
        assert created_note.id == created_note_id
        assert created_note.title == mock_note_entry_2.title
        assert created_note.content == mock_note_entry_2.content

        created_note_timestamp = created_note.time_created
        assert created_note_timestamp > 0
        assert created_note.time_updated == created_note_timestamp

        created_note.title = mock_note_entry_1.title
        created_note.content = mock_note_entry_1.content

        # Update note
        time.sleep(1)
        update_response = asyncio.run(
            mock_notes_router.perform_note_action(
                mock_request_object, NotesActionRequest(action=DatabaseAction.UPDATE, note=created_note)
            )
        )

        assert update_response.message == "Note entry updated successfully"

        updated_note_id = update_response.note_id
        assert isinstance(updated_note_id, int)
        assert updated_note_id == created_note_id

        all_notes = asyncio.run(mock_notes_router.get_notes(mock_request_object)).notes
        updated_note = next(note for note in all_notes if note.id == updated_note_id)
        assert not updated_note.title == mock_note_entry_2.title
        assert updated_note.title == mock_note_entry_1.title
        assert not updated_note.content == mock_note_entry_2.content
        assert updated_note.content == mock_note_entry_1.content
        assert updated_note.time_updated > created_note_timestamp

        # Delete note
        delete_response = asyncio.run(
            mock_notes_router.perform_note_action(
                mock_request_object, NotesActionRequest(action=DatabaseAction.DELETE, note=updated_note)
            )
        )
        assert delete_response.message == "Note entry deleted successfully"

        deleted_note_id = delete_response.note_id
        assert isinstance(deleted_note_id, int)
        assert deleted_note_id == updated_note_id

        all_notes = asyncio.run(mock_notes_router.get_notes(mock_request_object)).notes
        assert not any(note.id == deleted_note_id for note in all_notes)
