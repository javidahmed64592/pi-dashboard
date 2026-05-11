"""Unit tests for the pi_dashboard.routers.container_router module."""

import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.routing import APIRoute

from pi_dashboard.routers import ContainerRouter


class TestRoutes:
    """Unit tests for route setup in ContainerRouter."""

    def test_setup_routes(self, mock_container_router: ContainerRouter) -> None:
        """Test that routes are set up correctly."""
        api_routes = [route for route in mock_container_router.router.routes if isinstance(route, APIRoute)]
        routes = [route.path for route in api_routes]
        expected_endpoints = [
            "/containers/",
            "/containers/refresh",
            "/containers/{container_id}/start",
            "/containers/{container_id}/stop",
            "/containers/{container_id}/restart",
            "/containers/{container_id}/update",
            "/containers/{container_id}/logs",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes


class TestListContainersEndpoint:
    """Integration and unit tests for the /containers endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_list_containers(self, mock_container_router: ContainerRouter, mock_request_object: Request) -> None:
        """Test the /containers method handles valid JSON."""
        response = asyncio.run(mock_container_router.list_containers(mock_request_object))

        assert response.message == "Retrieved 1 containers"
        assert len(response.containers) == 1


class TestRefreshContainersEndpoint:
    """Integration and unit tests for the /containers/refresh endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_refresh_containers(self, mock_container_router: ContainerRouter, mock_request_object: Request) -> None:
        """Test the /containers/refresh method handles valid JSON."""
        response = asyncio.run(mock_container_router.refresh_containers(mock_request_object))

        assert response.message == "Retrieved 1 containers"
        assert len(response.containers) == 1


class TestStartContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/start endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_start_container(self, mock_container_router: ContainerRouter, mock_request_object: Request) -> None:
        """Test the /containers/{container_id}/start method handles valid JSON."""
        container_id = "container_short_id"
        response = asyncio.run(mock_container_router.start_container(mock_request_object, container_id))

        assert response.message == "Container test-container started successfully"
        assert response.container_id == container_id


class TestStopContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/stop endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_stop_container(self, mock_container_router: ContainerRouter, mock_request_object: Request) -> None:
        """Test the /containers/{container_id}/stop method handles valid JSON."""
        container_id = "container_short_id"
        response = asyncio.run(mock_container_router.stop_container(mock_request_object, container_id))

        assert response.message == "Container test-container stopped successfully"
        assert response.container_id == container_id


class TestRestartContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/restart endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_restart_container(
        self,
        mock_container_router: ContainerRouter,
        mock_request_object: Request,
    ) -> None:
        """Test the /containers/{container_id}/restart method handles valid JSON and returns a model reply."""
        container_id = "container_short_id"
        response = asyncio.run(mock_container_router.restart_container(mock_request_object, container_id))

        assert response.message == "Container test-container restarted successfully"
        assert response.container_id == container_id


class TestUpdateContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/update endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_update_container(
        self,
        mock_container_router: ContainerRouter,
        mock_request_object: Request,
    ) -> None:
        """Test the /containers/{container_id}/update method handles valid JSON."""
        response = asyncio.run(mock_container_router.update_container(mock_request_object, "container_short_id"))

        assert response.message == "Container test-container updated successfully"
        assert response.container_id == "new_container_short_id"


class TestGetContainerLogsEndpoint:
    """Integration and unit tests for the /containers/{container_id}/logs endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_get_container_logs(
        self,
        mock_container_router: ContainerRouter,
        mock_request_object: Request,
    ) -> None:
        """Test the /containers/{container_id}/logs method returns log lines."""
        container_id = "container_short_id"
        response = asyncio.run(mock_container_router.get_container_logs(mock_request_object, container_id, lines=100))

        assert response.message == f"Retrieved {len(response.logs)} log lines for container {container_id}"
        assert response.container_id == container_id
        assert response.logs == ["log line 1", "log line 2", "log line 3"]
