"""Unit tests for the pi_dashboard.server module."""

from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Security
from fastapi.routing import APIRoute
from fastapi.security import APIKeyHeader

from pi_dashboard.models import (
    PiDashboardConfig,
)
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
) -> Generator[PiDashboardServer]:
    """Provide a PiDashboardServer instance for testing."""

    async def fake_verify_api_key(
        api_key: str | None = Security(APIKeyHeader(name="X-API-Key", auto_error=False)),
    ) -> None:
        """Fake verify API key that accepts the security header and always succeeds in tests."""
        return

    with (
        patch.object(PiDashboardServer, "_verify_api_key", new=fake_verify_api_key),
        patch("pi_dashboard.server.PiDashboardConfig.save_to_file"),
    ):
        server = PiDashboardServer(config=mock_pi_dashboard_config)
        yield server


class TestPiDashboardServer:
    """Unit tests for the PiDashboardServer class."""

    def test_init(self, mock_server: PiDashboardServer) -> None:
        """Test PiDashboardServer initialization."""
        assert isinstance(mock_server.config, PiDashboardConfig)

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


class TestPiDashboardServerRoutes:
    """Integration tests for the routes in PiDashboardServer."""

    def test_setup_routes(self, mock_server: PiDashboardServer) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_server.app.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/health",
            "/login",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes, f"Expected endpoint {endpoint} not found in routes"
