"""Pi Dashboard server module."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from python_template_server.template_server import BaseRouter, TemplateServer

from pi_dashboard.db import MetricsDatabaseManager, NotesDatabaseManager
from pi_dashboard.docker_container_handler import DockerContainerHandler
from pi_dashboard.models import (
    DatabaseAction,
    PiDashboardConfig,
)
from pi_dashboard.routers import ContainerRouter, NotesRouter, SystemRouter
from pi_dashboard.system_metrics_handler import (
    get_system_metrics,
)

logger = logging.getLogger(__name__)

CONTAINER_ROUTER = ContainerRouter(prefix="/containers")
NOTES_ROUTER = NotesRouter(prefix="/notes")
SYSTEM_ROUTER = SystemRouter(prefix="/system")


class PiDashboardServer(TemplateServer):
    """Pi Dashboard FastAPI server."""

    def __init__(self, config: PiDashboardConfig | None = None) -> None:
        """Initialize the PiDashboardServer.

        :param PiDashboardConfig | None config: Optional pre-loaded configuration
        """
        self.metrics_database_manager = MetricsDatabaseManager()
        self.notes_database_manager = NotesDatabaseManager()
        self.docker_container_handler = DockerContainerHandler()
        self.config: PiDashboardConfig
        super().__init__(
            package_name="pi-dashboard",
            config=config,
        )

        self.metrics_database_manager.configure(db_config=self.config.db)
        self.notes_database_manager.configure(db_config=self.config.db)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None]:
        """Handle application lifespan events."""
        # Startup
        logger.info("Starting task: Metrics collection")
        metrics_task = asyncio.create_task(self._collect_metrics_periodically())
        tasks = [metrics_task]
        yield

        # Shutdown
        logger.info("Stopping task: Metrics collection")
        metrics_task.cancel()

        try:
            for task in tasks:
                await task
        except asyncio.CancelledError:
            pass

    async def _collect_metrics_periodically(self) -> None:
        """Background task to collect metrics at regular intervals."""
        while True:
            try:
                self.metrics_database_manager.cleanup_old_system_metrics()
                metrics = get_system_metrics()

                self.metrics_database_manager.perform_system_metrics_action(
                    system_metrics=metrics, action=DatabaseAction.CREATE
                )

                await asyncio.sleep(self.config.metrics.collection_interval)
            except asyncio.CancelledError:
                logger.info("Metrics collection task cancelled")
                break
            except Exception:
                logger.exception("Error collecting metrics")
                await asyncio.sleep(self.config.metrics.collection_interval)

    @property
    def routers(self) -> list[BaseRouter]:
        """Define the API routers for the server.

        :return list[BaseRouter]: List of API routers
        """
        CONTAINER_ROUTER.configure_router(container_handler=self.docker_container_handler)
        NOTES_ROUTER.configure_router(db=self.notes_database_manager)
        SYSTEM_ROUTER.configure_router(db=self.metrics_database_manager)
        return [CONTAINER_ROUTER, NOTES_ROUTER, SYSTEM_ROUTER]

    def validate_config(self, config_data: dict) -> PiDashboardConfig:
        """Validate configuration data against the PiDashboardConfig model.

        :param dict config_data: The configuration data to validate
        :return PiDashboardConfig: The validated configuration model
        """
        return PiDashboardConfig.model_validate(config_data)  # type: ignore[no-any-return]
