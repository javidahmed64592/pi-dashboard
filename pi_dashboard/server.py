"""Pi Dashboard server module."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Annotated

from docker.errors import APIError, NotFound
from fastapi import FastAPI, HTTPException, Query, Request
from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from pi_dashboard.db import MetricsDatabaseManager, NotesDatabaseManager
from pi_dashboard.docker_container_handler import DockerContainerHandler
from pi_dashboard.models import (
    DatabaseAction,
    DockerContainerActionResponse,
    DockerContainerListResponse,
    DockerContainerLogsResponse,
    GetSystemInfoResponse,
    GetSystemMetricsHistoryRequest,
    GetSystemMetricsHistoryResponse,
    GetSystemMetricsResponse,
    NotesActionRequest,
    NotesActionResponse,
    NotesListResponse,
    PiDashboardConfig,
)
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
            package_name="pi-dashboard",
            config=config,
        )

        self.metrics_database_manager = MetricsDatabaseManager(db_config=self.config.db)
        self.notes_database_manager = NotesDatabaseManager(db_config=self.config.db)
        self.docker_container_handler = DockerContainerHandler()

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
                # Cleanup old entries
                self.metrics_database_manager.cleanup_old_metrics()

                # Collect current metrics
                metrics = get_system_metrics()

                # Add to history
                self.metrics_database_manager.perform_metrics_action(
                    metrics_entry=metrics, action=DatabaseAction.CREATE
                )

                # Wait for next collection
                await asyncio.sleep(self.config.metrics.collection_interval)
            except asyncio.CancelledError:
                logger.info("Metrics collection task cancelled")
                break
            except Exception:
                logger.exception("Error collecting metrics")
                await asyncio.sleep(self.config.metrics.collection_interval)

    def validate_config(self, config_data: dict) -> PiDashboardConfig:
        """Validate configuration data against the PiDashboardConfig model.

        :param dict config_data: The configuration data to validate
        :return PiDashboardConfig: The validated configuration model
        """
        return PiDashboardConfig.model_validate(config_data)  # type: ignore[no-any-return]

    def setup_routes(self) -> None:
        """Set up API routes."""
        # System routes
        self.add_route(
            endpoint="/system/info",
            handler_function=self.get_system_info,
            response_model=GetSystemInfoResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/system/metrics",
            handler_function=self.get_system_metrics,
            response_model=GetSystemMetricsResponse,
            methods=["GET"],
            limited=False,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/system/metrics/history",
            handler_function=self.get_system_metrics_history,
            response_model=GetSystemMetricsHistoryResponse,
            methods=["POST"],
            limited=False,
            authentication_required=True,
        )

        # Notes routes
        self.add_route(
            endpoint="/notes",
            handler_function=self.get_notes,
            response_model=NotesListResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/notes",
            handler_function=self.perform_note_action,
            response_model=NotesActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )

        # Container routes
        self.add_route(
            endpoint="/containers",
            handler_function=self.list_containers,
            response_model=DockerContainerListResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/refresh",
            handler_function=self.refresh_containers,
            response_model=DockerContainerListResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/start",
            handler_function=self.start_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/stop",
            handler_function=self.stop_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/restart",
            handler_function=self.restart_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/update",
            handler_function=self.update_container,
            response_model=DockerContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/logs",
            handler_function=self.get_container_logs,
            response_model=DockerContainerLogsResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )

    # System routes
    async def get_system_info(self, request: Request) -> GetSystemInfoResponse:
        """Get system information.

        :return GetSystemInfoResponse: The system information response model
        """
        info = get_system_info()
        return GetSystemInfoResponse(
            message="Retrieved system info successfully",
            info=info,
        )

    async def get_system_metrics(self, request: Request) -> GetSystemMetricsResponse:
        """Get system metrics.

        :return GetSystemMetricsResponse: The system metrics response model
        """
        metrics = get_system_metrics()
        return GetSystemMetricsResponse(
            message="Retrieved system metrics successfully",
            metrics=metrics,
        )

    async def get_system_metrics_history(self, request: Request) -> GetSystemMetricsHistoryResponse:
        """Get system metrics history.

        :return GetSystemMetricsHistoryResponse: The system metrics history response model
        """
        metrics_request = GetSystemMetricsHistoryRequest.model_validate(await request.json())
        entries = self.metrics_database_manager.get_metric_entries_since(
            metrics_request.last_n_seconds, metrics_request.max_data_points
        )
        return GetSystemMetricsHistoryResponse(
            message="Retrieved system metrics history successfully",
            history=entries,
        )

    # Notes routes
    async def get_notes(self, request: Request) -> NotesListResponse:
        """Get all note entries.

        :return NotesListResponse: Response containing list of note entries
        """
        try:
            notes = self.notes_database_manager.get_all_note_entries()
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
            note_id = self.notes_database_manager.perform_note_action(note_entry=body.note, action=body.action)
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

    # Container routes
    async def list_containers(self, request: Request) -> DockerContainerListResponse:
        """List all Docker containers.

        :return DockerContainerListResponse: Response containing list of containers
        """
        try:
            containers = self.docker_container_handler.list_containers()
            return DockerContainerListResponse(
                message=f"Retrieved {len(containers)} containers",
                containers=containers,
            )
        except Exception as e:
            logger.exception("Unexpected error while listing containers")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def refresh_containers(self, request: Request) -> DockerContainerListResponse:
        """Refresh container list from Docker daemon.

        :return DockerContainerListResponse: Response containing refreshed list of containers
        """
        try:
            containers = self.docker_container_handler.list_containers()
            return DockerContainerListResponse(
                message=f"Retrieved {len(containers)} containers",
                containers=containers,
            )
        except Exception as e:
            logger.exception("Unexpected error while refreshing containers")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def start_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Start a Docker container.

        :param str container_id: The container ID to start
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self.docker_container_handler.start_container(container_id=container_id)
            return DockerContainerActionResponse(
                message=f"Container {container_name} started successfully",
                container_id=container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while starting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while starting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def stop_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Stop a Docker container.

        :param str container_id: The container ID to stop
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self.docker_container_handler.stop_container(container_id=container_id, timeout=10)
            return DockerContainerActionResponse(
                message=f"Container {container_name} stopped successfully",
                container_id=container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while stopping container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while stopping container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def restart_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Restart a Docker container.

        :param str container_id: The container ID to restart
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self.docker_container_handler.restart_container(container_id=container_id, timeout=10)
            return DockerContainerActionResponse(
                message=f"Container {container_name} restarted successfully",
                container_id=container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while restarting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while restarting container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def update_container(self, request: Request, container_id: str) -> DockerContainerActionResponse:
        """Update a Docker container by pulling latest image and recreating it.

        :param str container_id: The container ID to update
        :return DockerContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name, new_container_id = self.docker_container_handler.update_container(
                container_id=container_id, timeout=10
            )
            return DockerContainerActionResponse(
                message=f"Container {container_name} updated successfully",
                container_id=new_container_id,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail="Container not found",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while updating container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while updating container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def get_container_logs(
        self,
        request: Request,
        container_id: str,
        lines: Annotated[int, Query(ge=1, le=1000)],
    ) -> DockerContainerLogsResponse:
        """Get logs for a Docker container.

        :param str container_id: The container ID
        :param int lines: Number of log lines to retrieve (1-1000)
        :return DockerContainerLogsResponse: Response containing log lines
        """
        try:
            log_lines = self.docker_container_handler.get_container_logs(container_id=container_id, lines=lines)
            return DockerContainerLogsResponse(
                message=f"Retrieved {len(log_lines)} log lines for container {container_id}",
                container_id=container_id,
                logs=log_lines,
            )
        except NotFound as e:
            logger.exception("Container not found: %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.NOT_FOUND,
                detail=f"Container not found: {container_id}",
            ) from e
        except APIError as e:
            logger.exception("Docker API error while fetching logs for container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.SERVICE_UNAVAILABLE,
                detail="Docker API error",
            ) from e
        except Exception as e:
            logger.exception("Unexpected error while fetching logs for container %s", container_id)
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e
