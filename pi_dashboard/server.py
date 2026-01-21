"""Pi Dashboard server module."""

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from python_template_server.models import ResponseCode
from python_template_server.template_server import TemplateServer

from pi_dashboard.models import (
    BaseResponse,
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
            package_name="pi_dashboard",
            config=config,
        )

        self.metrics_history = SystemMetricsHistory()

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
        self.add_authenticated_route(
            endpoint="/system/info",
            handler_function=self.get_system_info,
            response_model=GetSystemInfoResponse,
            methods=["GET"],
            limited=False,
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
