"""Pi Dashboard server module."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated

from docker.errors import APIError, NotFound
from fastapi import FastAPI, HTTPException, Query, Request
from python_template_server.constants import ROOT_DIR
from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from pi_dashboard.container_handler import ContainerHandler
from pi_dashboard.models import (
    BaseResponse,
    ContainerActionResponse,
    ContainerListResponse,
    ContainerLogsResponse,
    GetSystemInfoResponse,
    GetSystemMetricsHistoryRequest,
    GetSystemMetricsHistoryResponse,
    GetSystemMetricsResponse,
    PiDashboardConfig,
    SystemMetricsHistory,
    SystemMetricsHistoryEntry,
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

        if not self.data_dir.exists():
            logger.info("Creating data directory at: %s", self.data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_history = SystemMetricsHistory()
        self.container_handler = ContainerHandler()

    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return ROOT_DIR / "data"  # type: ignore[no-any-return]

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
        # Container routes
        self.add_route(
            endpoint="/containers",
            handler_function=self.list_containers,
            response_model=ContainerListResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/refresh",
            handler_function=self.refresh_containers,
            response_model=ContainerListResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/start",
            handler_function=self.start_container,
            response_model=ContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/stop",
            handler_function=self.stop_container,
            response_model=ContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/restart",
            handler_function=self.restart_container,
            response_model=ContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/update",
            handler_function=self.update_container,
            response_model=ContainerActionResponse,
            methods=["POST"],
            limited=True,
            authentication_required=True,
        )
        self.add_route(
            endpoint="/containers/{container_id}/logs",
            handler_function=self.get_container_logs,
            response_model=ContainerLogsResponse,
            methods=["GET"],
            limited=True,
            authentication_required=True,
        )

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
        entries = self.metrics_history.get_entries_since(
            min(metrics_request.last_n_seconds, self.config.metrics.max_history_duration),
            PiDashboardServer._current_timestamp_int(),
            metrics_request.max_data_points,
        )
        return GetSystemMetricsHistoryResponse(
            message="Retrieved system metrics history successfully",
            history=SystemMetricsHistory(history=entries),
        )

    async def list_containers(self, request: Request) -> ContainerListResponse:
        """List all Docker containers.

        :return ContainerListResponse: Response containing list of containers
        """
        try:
            containers = self.container_handler.list_containers()
            return ContainerListResponse(
                message=f"Retrieved {len(containers)} containers",
                containers=containers,
            )
        except Exception as e:
            logger.exception("Unexpected error while listing containers")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def refresh_containers(self, request: Request) -> ContainerListResponse:
        """Refresh container list from Docker daemon.

        :return ContainerListResponse: Response containing refreshed list of containers
        """
        try:
            containers = self.container_handler.list_containers()
            return ContainerListResponse(
                message=f"Retrieved {len(containers)} containers",
                containers=containers,
            )
        except Exception as e:
            logger.exception("Unexpected error while listing containers")
            raise HTTPException(
                status_code=ResponseCode.INTERNAL_SERVER_ERROR,
                detail="Unexpected error",
            ) from e

    async def start_container(self, request: Request, container_id: str) -> ContainerActionResponse:
        """Start a Docker container.

        :param str container_id: The container ID to start
        :return ContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self.container_handler.start_container(container_id=container_id)
            return ContainerActionResponse(
                message=f"Container {container_name} started successfully",
                container_id=container_id,
                action="start",
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

    async def stop_container(self, request: Request, container_id: str) -> ContainerActionResponse:
        """Stop a Docker container.

        :param str container_id: The container ID to stop
        :return ContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self.container_handler.stop_container(container_id=container_id, timeout=10)
            return ContainerActionResponse(
                message=f"Container {container_name} stopped successfully",
                container_id=container_id,
                action="stop",
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

    async def restart_container(self, request: Request, container_id: str) -> ContainerActionResponse:
        """Restart a Docker container.

        :param str container_id: The container ID to restart
        :return ContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name = self.container_handler.restart_container(container_id=container_id, timeout=10)
            return ContainerActionResponse(
                message=f"Container {container_name} restarted successfully",
                container_id=container_id,
                action="restart",
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

    async def update_container(self, request: Request, container_id: str) -> ContainerActionResponse:
        """Update a Docker container by pulling latest image and recreating it.

        :param str container_id: The container ID to update
        :return ContainerActionResponse: Response indicating success or failure
        """
        try:
            container_name, new_container_id = self.container_handler.update_container(
                container_id=container_id, timeout=10
            )
            return ContainerActionResponse(
                message=f"Container {container_name} updated successfully",
                container_id=new_container_id,
                action="update",
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
    ) -> ContainerLogsResponse:
        """Get logs for a Docker container.

        :param str container_id: The container ID
        :param int lines: Number of log lines to retrieve (1-1000)
        :return ContainerLogsResponse: Response containing log lines
        """
        try:
            log_lines = self.container_handler.get_container_logs(container_id=container_id, lines=lines)
            return ContainerLogsResponse(
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
