"""Unit tests for the pi_dashboard.server module."""

from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import MagicMock, patch

import pytest

from pi_dashboard.db import MetricsDatabaseManager, NotesDatabaseManager
from pi_dashboard.docker_container_handler import DockerContainerHandler
from pi_dashboard.models import (
    PiDashboardConfig,
)
from pi_dashboard.routers import ContainerRouter, NotesRouter, SystemRouter
from pi_dashboard.server import PiDashboardServer


@pytest.fixture(autouse=True)
def mock_package_metadata() -> Generator[MagicMock]:
    """Mock importlib.metadata.metadata to return a mock PackageMetadata."""
    with patch("python_template_server.template_server.metadata") as mock_metadata:
        mock_pkg_metadata = MagicMock(spec=PackageMetadata)
        metadata_dict = {
            "Name": "pi-dashboard",
            "Version": "0.1.0",
            "Summary": "A FastAPI-based Raspberry Pi dashboard.",
        }
        mock_pkg_metadata.__getitem__.side_effect = lambda key: metadata_dict[key]
        mock_metadata.return_value = mock_pkg_metadata
        yield mock_metadata


@pytest.fixture
def mock_server(
    mock_pi_dashboard_config: PiDashboardConfig,
    mock_metrics_database_manager: MetricsDatabaseManager,
    mock_notes_database_manager: NotesDatabaseManager,
    mock_docker_container_handler: DockerContainerHandler,
    mock_container_router: ContainerRouter,
    mock_notes_router: NotesRouter,
    mock_system_router: SystemRouter,
) -> Generator[PiDashboardServer]:
    """Provide a PiDashboardServer instance for testing."""
    with (
        patch("pi_dashboard.server.PiDashboardConfig.save_to_file"),
        patch("pi_dashboard.server.MetricsDatabaseManager", return_value=mock_metrics_database_manager),
        patch("pi_dashboard.server.NotesDatabaseManager", return_value=mock_notes_database_manager),
        patch("pi_dashboard.server.DockerContainerHandler", return_value=mock_docker_container_handler),
        patch(
            "pi_dashboard.server.ContainerRouter",
            return_value=mock_container_router,
            autospec=True,
        ),
        patch(
            "pi_dashboard.server.NotesRouter",
            return_value=mock_notes_router,
            autospec=True,
        ),
        patch(
            "pi_dashboard.server.SystemRouter",
            return_value=mock_system_router,
            autospec=True,
        ),
    ):
        server = PiDashboardServer(config=mock_pi_dashboard_config)
        yield server


class TestPiDashboardServer:
    """Unit tests for the PiDashboardServer class."""

    def test_init(
        self,
        mock_server: PiDashboardServer,
        mock_container_router: ContainerRouter,
        mock_notes_router: NotesRouter,
        mock_system_router: SystemRouter,
    ) -> None:
        """Test PiDashboardServer initialization."""
        assert isinstance(mock_server.config, PiDashboardConfig)
        for route in [
            *mock_container_router.router.routes,
            *mock_notes_router.router.routes,
            *mock_system_router.router.routes,
        ]:
            assert route in mock_server.app.routes

    def test_validate_config(self, mock_server: PiDashboardServer, mock_pi_dashboard_config: PiDashboardConfig) -> None:
        """Test configuration validation."""
        config_dict = mock_pi_dashboard_config.model_dump()
        validated_config = mock_server.validate_config(config_dict)
        assert validated_config == mock_pi_dashboard_config

    def test_validate_config_invalid_returns_default(self, mock_server: PiDashboardServer) -> None:
        """Test invalid configuration returns default configuration."""
        invalid_config = {"model": None}
        validated_config = mock_server.validate_config(invalid_config)
        assert isinstance(validated_config, PiDashboardConfig)
