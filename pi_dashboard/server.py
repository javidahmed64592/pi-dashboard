"""Pi Dashboard server module."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from python_template_server.constants import ROOT_DIR
from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from pi_dashboard.models import (
    BaseResponse,
    CreateNoteRequest,
    CreateNoteResponse,
    DeleteNoteResponse,
    GetNotesResponse,
    GetSystemInfoResponse,
    GetSystemMetricsHistoryRequest,
    GetSystemMetricsHistoryResponse,
    GetSystemMetricsResponse,
    PiDashboardConfig,
    SystemMetricsHistory,
    SystemMetricsHistoryEntry,
    UpdateNoteRequest,
    UpdateNoteResponse,
)
from pi_dashboard.notes_handler import NotesHandler
from pi_dashboard.system_metrics_handler import (
    get_system_info,
    get_system_metrics,
)

logger = logging.getLogger(__name__)


class PiDashboardServer(TemplateServer):
    """Pi Dashboard FastAPI server."""

    def __init__(self, config: PiDashboardConfig | None = None) -> None:
        """Initialize the PiDashboardServer.

        :param PiDashboardConfig | None config: Optional pre-loaded configuration
        """
        self.config: PiDashboardConfig
        super().__init__(
            package_name="pi_dashboard",
            config=config,
        )

        if not self.data_dir.exists():
            logger.info("Creating data directory at: %s", self.data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_history = SystemMetricsHistory()
        self.notes_handler = NotesHandler(self.data_dir)

    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return ROOT_DIR / "data"

    @staticmethod
    def _current_timestamp_int() -> int:
        """Get the current Unix timestamp as an integer.

        :return int: The current Unix timestamp
        """
        timestamp_str = BaseResponse.current_timestamp()
        return int(datetime.fromisoformat(timestamp_str.rstrip("Z")).timestamp())

    @staticmethod
    def _start_task(task_method: Callable, task_name: str) -> asyncio.Task:
        """Start an asynchronous task.

        :param Callable task_method: The method to run as a task
        :return asyncio.Task: The created asyncio task
        """
        logger.info("Starting task: %s", task_name)
        return asyncio.create_task(task_method())

    @staticmethod
    def _stop_task(task: asyncio.Task, task_name: str) -> None:
        """Stop an asynchronous task.

        :param asyncio.Task task: The task to stop
        """
        logger.info("Stopping task: %s", task_name)
        task.cancel()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None]:
        """Handle application lifespan events."""
        # Startup
        metrics_task = PiDashboardServer._start_task(self._collect_metrics_periodically, "Metrics collection")
        tasks = [metrics_task]
        yield

        # Shutdown
        PiDashboardServer._stop_task(metrics_task, "Metrics collection")

        try:
            for task in tasks:
                await task
        except asyncio.CancelledError:
            pass

    async def _collect_metrics_periodically(self) -> None:
        """Background task to collect metrics at regular intervals."""
        while True:
            try:
                timestamp = PiDashboardServer._current_timestamp_int()

                # Cleanup old entries
                self.metrics_history.cleanup_old_entries(self.config.metrics.max_history_duration, timestamp)

                # Collect current metrics
                metrics = get_system_metrics()

                # Add to history
                entry = SystemMetricsHistoryEntry(metrics=metrics, timestamp=timestamp)
                self.metrics_history.add_entry(entry)

                # Wait for next collection
                await asyncio.sleep(self.config.metrics.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error collecting metrics")
                await asyncio.sleep(self.config.metrics.collection_interval)

    def validate_config(self, config_data: dict) -> PiDashboardConfig:
        """Validate configuration data against the PiDashboardConfig model.

        :param dict config_data: The configuration data to validate
        :return PiDashboardConfig: The validated configuration model
        :raise ValidationError: If the configuration data is invalid
        """
        return PiDashboardConfig.model_validate(config_data)  # type: ignore[no-any-return]

    def setup_routes(self) -> None:
        """Set up API routes."""
        # System routes
        self.add_authenticated_route(
            endpoint="/system/info",
            handler_function=self.get_system_info,
            response_model=GetSystemInfoResponse,
            methods=["GET"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/system/metrics",
            handler_function=self.get_system_metrics,
            response_model=GetSystemMetricsResponse,
            methods=["GET"],
            limited=False,
        )
        self.add_authenticated_route(
            endpoint="/system/metrics/history",
            handler_function=self.get_system_metrics_history,
            response_model=GetSystemMetricsHistoryResponse,
            methods=["POST"],
            limited=False,
        )
        # Notes routes
        self.add_authenticated_route(
            endpoint="/notes",
            handler_function=self.get_notes,
            response_model=GetNotesResponse,
            methods=["GET"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/notes",
            handler_function=self.create_note,
            response_model=CreateNoteResponse,
            methods=["POST"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/notes/{note_id}",
            handler_function=self.update_note,
            response_model=UpdateNoteResponse,
            methods=["PUT"],
            limited=True,
        )
        self.add_authenticated_route(
            endpoint="/notes/{note_id}",
            handler_function=self.delete_note,
            response_model=DeleteNoteResponse,
            methods=["DELETE"],
            limited=True,
        )
        super().setup_routes()

    async def get_system_info(self, request: Request) -> GetSystemInfoResponse:
        """Get system information.

        :return GetSystemInfoResponse: The system information response model
        """
        info = get_system_info()
        return GetSystemInfoResponse(
            code=ResponseCode.OK,
            message="Retrieved system info successfully",
            timestamp=GetSystemInfoResponse.current_timestamp(),
            info=info,
        )

    async def get_system_metrics(self, request: Request) -> GetSystemMetricsResponse:
        """Get system metrics.

        :return GetSystemMetricsResponse: The system metrics response model
        """
        metrics = get_system_metrics()
        return GetSystemMetricsResponse(
            code=ResponseCode.OK,
            message="Retrieved system metrics successfully",
            timestamp=GetSystemMetricsResponse.current_timestamp(),
            metrics=metrics,
        )

    async def get_system_metrics_history(self, request: Request) -> GetSystemMetricsHistoryResponse:
        """Get system metrics history.

        :return GetSystemMetricsHistoryResponse: The system metrics history response model
        """
        metrics_request = GetSystemMetricsHistoryRequest.model_validate(await request.json())
        entries = self.metrics_history.get_entries_since(
            min(metrics_request.last_n_seconds, self.config.metrics.max_history_duration),
            PiDashboardServer._current_timestamp_int(),
        )
        return GetSystemMetricsHistoryResponse(
            code=ResponseCode.OK,
            message="Retrieved system metrics history successfully",
            timestamp=GetSystemMetricsHistoryResponse.current_timestamp(),
            history=SystemMetricsHistory(history=entries),
        )

    async def get_notes(self, request: Request) -> GetNotesResponse:
        """Get all notes.

        :return GetNotesResponse: Response containing all notes
        """
        return GetNotesResponse(
            code=ResponseCode.OK,
            message="Retrieved notes successfully",
            timestamp=GetNotesResponse.current_timestamp(),
            notes=self.notes_handler.get_all_notes(),
        )

    async def create_note(self, request: Request) -> CreateNoteResponse:
        """Create a new note.

        :return CreateNoteResponse: Response containing the created note
        """
        note_request = CreateNoteRequest.model_validate(await request.json())
        current_timestamp = CreateNoteResponse.current_timestamp()
        return CreateNoteResponse(
            code=ResponseCode.OK,
            message="Created note successfully",
            timestamp=current_timestamp,
            note=self.notes_handler.create_note(note_request.title, note_request.content, current_timestamp),
        )

    async def update_note(self, request: Request, note_id: str) -> UpdateNoteResponse:
        """Update an existing note.

        :param str note_id: The UUID of the note to update
        :return UpdateNoteResponse: Response containing the updated note
        :raises HTTPException: If the note is not found (404)
        """
        update_request = UpdateNoteRequest.model_validate(await request.json())
        current_timestamp = UpdateNoteResponse.current_timestamp()
        note = self.notes_handler.update_note(note_id, current_timestamp, update_request.title, update_request.content)
        if note is None:
            raise HTTPException(status_code=ResponseCode.NOT_FOUND, detail=f"Note not found: {note_id}")
        return UpdateNoteResponse(
            code=ResponseCode.OK,
            message="Updated note successfully",
            timestamp=current_timestamp,
            note=note,
        )

    async def delete_note(self, request: Request, note_id: str) -> DeleteNoteResponse:
        """Delete a note.

        :param str note_id: The UUID of the note to delete
        :return DeleteNoteResponse: Response confirming deletion
        :raises HTTPException: If the note is not found (404)
        """
        success = self.notes_handler.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=ResponseCode.NOT_FOUND, detail=f"Note not found: {note_id}")
        return DeleteNoteResponse(
            code=ResponseCode.OK,
            message="Deleted note successfully",
            timestamp=DeleteNoteResponse.current_timestamp(),
        )
