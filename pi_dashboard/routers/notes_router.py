"""Notes router for Pi Dashboard."""

import logging

from fastapi import HTTPException, Request
from python_template_server.models import ResponseCode
from python_template_server.routers import BaseRouter

from pi_dashboard.db.notes_database_manager import NotesDatabaseManager
from pi_dashboard.models import NotesActionRequest, NotesActionResponse, NotesListResponse

logger = logging.getLogger(__name__)


class NotesRouter(BaseRouter):
    """Router for the notes endpoints."""

    def configure_router(self, db: NotesDatabaseManager) -> None:
        """Configure the router with necessary dependencies."""
        self._db = db

    def setup_routes(self) -> None:
        """Set up the API routes for the notes endpoints."""
        self.add_route(
            endpoint="/",
            handler_function=self.get_notes,
            response_model=NotesListResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/",
            handler_function=self.perform_note_action,
            response_model=NotesActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )

    async def get_notes(self, request: Request) -> NotesListResponse:
        """Get all note entries.

        :return NotesListResponse: Response containing list of note entries
        """
        try:
            notes = self._db.get_all_note_entries()
            return NotesListResponse(
                message=f"Retrieved {len(notes)} note entries",
                notes=notes,
            )
        except Exception as e:
            logger.exception("Unexpected error while retrieving notes")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def perform_note_action(self, request: Request, body: NotesActionRequest) -> NotesActionResponse:
        """Perform a note action (create/update/delete).

        :param NotesActionRequest body: The note action request containing the action and note entry data
        :return NotesActionResponse: Response indicating success or failure of the note action
        """
        try:
            note_id = self._db.perform_note_action(note_entry=body.note, action=body.action)
            return NotesActionResponse(
                message=f"Note entry {body.action.value}d successfully",
                note_id=note_id,
            )
        except ValueError as e:
            logger.exception("Note entry not found for action %s", body.action.value)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=str(e),
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while performing note action %s", body.action.value)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e
