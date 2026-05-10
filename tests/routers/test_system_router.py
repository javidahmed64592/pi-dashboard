"""Unit tests for the pi_dashboard.routers.system_router module."""

import asyncio
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request
from fastapi.routing import APIRoute

from pi_dashboard.models import (
    GetSystemMetricsHistoryRequest,
    SystemInfo,
    SystemMetrics,
)
from pi_dashboard.routers import SystemRouter


@pytest.fixture(autouse=True)
def mock_get_system_info(
    mock_system_info: SystemInfo,
) -> Generator[MagicMock]:
    """Mock the get_system_info function."""
    with patch("pi_dashboard.routers.system_router.get_system_info") as mock_info:
        mock_info.return_value = mock_system_info
        yield mock_info


@pytest.fixture(autouse=True)
def mock_get_system_metrics(mock_system_metrics: SystemMetrics) -> Generator[MagicMock]:
    """Mock the get_system_metrics function."""
    with patch("pi_dashboard.routers.system_router.get_system_metrics") as mock_metrics:
        mock_metrics.return_value = mock_system_metrics
        yield mock_metrics


class TestRoutes:
    """Unit tests for route setup in SystemRouter."""

    def test_setup_routes(self, mock_system_router: SystemRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_system_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/system/info",
            "/system/metrics",
            "/system/metrics/history",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes


class TestGetSystemInfoEndpoint:
    """Integration and unit tests for the /system/info endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_system_info(
        self, mock_system_router: SystemRouter, mock_request_object: Request, mock_system_info: SystemInfo
    ) -> None:
        """Test the /system/info method handles valid JSON."""
        response = asyncio.run(mock_system_router.get_system_info(mock_request_object))

        assert response.message == "Retrieved system info successfully"
        assert response.info == mock_system_info


class TestGetSystemMetricsEndpoint:
    """Integration and unit tests for the /system/metrics endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_system_metrics(
        self, mock_system_router: SystemRouter, mock_request_object: Request, mock_system_metrics: SystemMetrics
    ) -> None:
        """Test the /system/metrics method handles valid JSON."""
        response = asyncio.run(mock_system_router.get_system_metrics(mock_request_object))
        assert response.message == "Retrieved system metrics successfully"
        assert response.metrics == mock_system_metrics


class TestGetSystemMetricsHistoryEndpoint:
    """Integration and unit tests for the /system/metrics/history endpoint."""

    @pytest.fixture
    def mock_request_body(self) -> GetSystemMetricsHistoryRequest:
        """Provide a mock request body for system metrics history."""
        return GetSystemMetricsHistoryRequest(last_n_seconds=300, max_data_points=1500)

    @pytest.fixture
    def mock_request_object(self, mock_request_body: GetSystemMetricsHistoryRequest) -> Request:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_request_body.model_dump())
        return request

    def test_get_system_metrics_history(
        self,
        mock_system_router: SystemRouter,
        mock_request_object: Request,
        mock_request_body: GetSystemMetricsHistoryRequest,
    ) -> None:
        """Test the /system/metrics/history method handles valid JSON."""
        response = asyncio.run(mock_system_router.get_system_metrics_history(mock_request_object, mock_request_body))
        assert response.message == "Retrieved system metrics history successfully"
        assert len(response.history) > 0
