"""Unit tests for the pi_dashboard.server module."""

import asyncio
import time
from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request, Security
from fastapi.routing import APIRoute
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient
from python_template_server.models import ResponseCode

from pi_dashboard.db import NotesDatabaseManager
from pi_dashboard.docker_container_handler import DockerContainerHandler
from pi_dashboard.models import (
    DatabaseAction,
    GetSystemMetricsHistoryRequest,
    NoteEntry,
    NotesActionRequest,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
    SystemMetricsHistory,
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
def mock_get_system_info(
    mock_system_info: SystemInfo,
) -> Generator[MagicMock]:
    """Mock the get_system_info function."""
    with patch("pi_dashboard.server.get_system_info") as mock_info:
        mock_info.return_value = mock_system_info
        yield mock_info


@pytest.fixture
def mock_get_system_metrics(mock_system_metrics: SystemMetrics) -> Generator[MagicMock]:
    """Mock the get_system_metrics function."""
    with patch("pi_dashboard.server.get_system_metrics") as mock_metrics:
        mock_metrics.return_value = mock_system_metrics
        yield mock_metrics


@pytest.fixture
def mock_server(
    mock_pi_dashboard_config: PiDashboardConfig,
    mock_notes_database_manager: NotesDatabaseManager,
    mock_get_system_info: MagicMock,
    mock_get_system_metrics: MagicMock,
    mock_system_metrics_history: SystemMetricsHistory,
    mock_docker_container_handler: DockerContainerHandler,
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
        patch("pi_dashboard.server.NotesDatabaseManager", return_value=mock_notes_database_manager),
        patch("pi_dashboard.server.SystemMetricsHistory", return_value=mock_system_metrics_history),
        patch("pi_dashboard.server.DockerContainerHandler", return_value=mock_docker_container_handler),
    ):
        server = PiDashboardServer(config=mock_pi_dashboard_config)
        yield server


@pytest.fixture
def mock_client(mock_server: PiDashboardServer) -> TestClient:
    """Provide a TestClient for the mock server."""
    return TestClient(mock_server.app)


class TestPiDashboardServer:
    """Unit tests for the PiDashboardServer class."""

    def test_init(self, mock_server: PiDashboardServer, mock_system_metrics_history: SystemMetricsHistory) -> None:
        """Test PiDashboardServer initialization."""
        assert isinstance(mock_server.config, PiDashboardConfig)
        assert mock_server.metrics_history == mock_system_metrics_history

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
            "/system/info",
            "/system/metrics",
            "/system/metrics/history",
            "/notes",
            "/containers",
            "/containers/refresh",
            "/containers/{container_id}/start",
            "/containers/{container_id}/stop",
            "/containers/{container_id}/restart",
            "/containers/{container_id}/update",
            "/containers/{container_id}/logs",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes, f"Expected endpoint {endpoint} not found in routes"


# System routes
class TestGetSystemInfoEndpoint:
    """Integration and unit tests for the /system/info endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_system_info(
        self, mock_server: PiDashboardServer, mock_request_object: Request, mock_system_info: SystemInfo
    ) -> None:
        """Test the /system/info method handles valid JSON."""
        response = asyncio.run(mock_server.get_system_info(mock_request_object))

        assert response.message == "Retrieved system info successfully"
        assert response.info == mock_system_info

    def test_get_system_info_endpoint(self, mock_client: TestClient) -> None:
        """Test /system/info endpoint returns 200."""
        response = mock_client.get("/system/info")
        assert response.status_code == ResponseCode.OK


class TestGetSystemMetricsEndpoint:
    """Integration and unit tests for the /system/metrics endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_system_metrics(
        self, mock_server: PiDashboardServer, mock_request_object: Request, mock_system_metrics: SystemMetrics
    ) -> None:
        """Test the /system/metrics method handles valid JSON."""
        response = asyncio.run(mock_server.get_system_metrics(mock_request_object))
        assert response.message == "Retrieved system metrics successfully"
        assert response.metrics == mock_system_metrics

    def test_get_system_metrics_endpoint(self, mock_client: TestClient) -> None:
        """Test /system/metrics endpoint returns 200."""
        response = mock_client.get("/system/metrics")
        assert response.status_code == ResponseCode.OK


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
        mock_server: PiDashboardServer,
        mock_request_object: Request,
        mock_system_metrics_history: SystemMetricsHistory,
    ) -> None:
        """Test the /system/metrics/history method handles valid JSON."""
        response = asyncio.run(mock_server.get_system_metrics_history(mock_request_object))
        assert response.message == "Retrieved system metrics history successfully"
        assert response.history == mock_system_metrics_history

    def test_get_system_metrics_history_endpoint(
        self, mock_client: TestClient, mock_request_body: GetSystemMetricsHistoryRequest
    ) -> None:
        """Test /system/metrics/history endpoint returns 200."""
        response = mock_client.post("/system/metrics/history", json=mock_request_body.model_dump())
        assert response.status_code == ResponseCode.OK


# Note routes
class TestGetNotesEndpoint:
    """Integration and unit tests for the /notes endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_get_notes(self, mock_server: PiDashboardServer, mock_request_object: Request) -> None:
        """Test the /notes method handles valid JSON."""
        response = asyncio.run(mock_server.get_notes(mock_request_object))

        assert response.message == "Retrieved 1 note entries"
        assert len(response.notes) == 1

    def test_get_notes_endpoint(self, mock_client: TestClient) -> None:
        """Test /notes endpoint returns 200."""
        response = mock_client.get("/notes")
        assert response.status_code == ResponseCode.OK


class TestPerformNoteActionEndpoint:
    """Integration and unit tests for the /notes endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_perform_note_action(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: Request,
        mock_note_entry_1: NoteEntry,
        mock_note_entry_2: NoteEntry,
    ) -> None:
        """Test the /notes method handles valid JSON."""
        # Create note
        create_response = asyncio.run(
            mock_server.perform_note_action(
                mock_request_object, NotesActionRequest(action=DatabaseAction.CREATE, note=mock_note_entry_2)
            )
        )

        assert create_response.message == "Note entry created successfully"

        created_note_id = create_response.note_id
        assert isinstance(created_note_id, int)

        all_notes = asyncio.run(mock_server.get_notes(mock_request_object)).notes
        created_note = next(note for note in all_notes if note.id == created_note_id)
        assert created_note.id == created_note_id
        assert created_note.title == mock_note_entry_2.title
        assert created_note.content == mock_note_entry_2.content

        created_note_timestamp = created_note.time_created
        assert created_note_timestamp > 0
        assert created_note.time_updated == created_note_timestamp

        created_note.title = mock_note_entry_1.title
        created_note.content = mock_note_entry_1.content

        # Update note
        time.sleep(1)
        update_response = asyncio.run(
            mock_server.perform_note_action(
                mock_request_object, NotesActionRequest(action=DatabaseAction.UPDATE, note=created_note)
            )
        )

        assert update_response.message == "Note entry updated successfully"

        updated_note_id = update_response.note_id
        assert isinstance(updated_note_id, int)
        assert updated_note_id == created_note_id

        all_notes = asyncio.run(mock_server.get_notes(mock_request_object)).notes
        updated_note = next(note for note in all_notes if note.id == updated_note_id)
        assert not updated_note.title == mock_note_entry_2.title
        assert updated_note.title == mock_note_entry_1.title
        assert not updated_note.content == mock_note_entry_2.content
        assert updated_note.content == mock_note_entry_1.content
        assert updated_note.time_updated > created_note_timestamp

        # Delete note
        delete_response = asyncio.run(
            mock_server.perform_note_action(
                mock_request_object, NotesActionRequest(action=DatabaseAction.DELETE, note=updated_note)
            )
        )
        assert delete_response.message == "Note entry deleted successfully"

        deleted_note_id = delete_response.note_id
        assert isinstance(deleted_note_id, int)
        assert deleted_note_id == updated_note_id

        all_notes = asyncio.run(mock_server.get_notes(mock_request_object)).notes
        assert not any(note.id == deleted_note_id for note in all_notes)

    def test_perform_note_action_endpoint(self, mock_client: TestClient, mock_note_entry_2: NoteEntry) -> None:
        """Test /notes endpoint returns 200."""
        # Create note
        create_response = mock_client.post(
            "/notes", json=NotesActionRequest(action=DatabaseAction.CREATE, note=mock_note_entry_2).model_dump()
        )
        assert create_response.status_code == ResponseCode.OK

        # Update note
        mock_note_entry_2.id = create_response.json()["note_id"]
        update_response = mock_client.post(
            "/notes", json=NotesActionRequest(action=DatabaseAction.UPDATE, note=mock_note_entry_2).model_dump()
        )
        assert update_response.status_code == ResponseCode.OK

        # Delete note
        delete_response = mock_client.post(
            "/notes", json=NotesActionRequest(action=DatabaseAction.DELETE, note=mock_note_entry_2).model_dump()
        )
        assert delete_response.status_code == ResponseCode.OK


# Container routes
class TestListContainersEndpoint:
    """Integration and unit tests for the /containers endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_list_containers(self, mock_server: PiDashboardServer, mock_request_object: Request) -> None:
        """Test the /containers method handles valid JSON."""
        response = asyncio.run(mock_server.list_containers(mock_request_object))

        assert response.message == "Retrieved 1 containers"
        assert len(response.containers) == 1

    def test_list_containers_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers endpoint returns 200."""
        response = mock_client.get("/containers")
        assert response.status_code == ResponseCode.OK


class TestRefreshContainersEndpoint:
    """Integration and unit tests for the /containers/refresh endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_refresh_containers(self, mock_server: PiDashboardServer, mock_request_object: Request) -> None:
        """Test the /containers/refresh method handles valid JSON."""
        response = asyncio.run(mock_server.refresh_containers(mock_request_object))

        assert response.message == "Retrieved 1 containers"
        assert len(response.containers) == 1

    def test_refresh_containers_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers/refresh endpoint returns 200."""
        response = mock_client.post("/containers/refresh")
        assert response.status_code == ResponseCode.OK


class TestStartContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/start endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_start_container(self, mock_server: PiDashboardServer, mock_request_object: Request) -> None:
        """Test the /containers/{container_id}/start method handles valid JSON."""
        container_id = "container_short_id"
        response = asyncio.run(mock_server.start_container(mock_request_object, container_id))

        assert response.message == "Container test-container started successfully"
        assert response.container_id == container_id

    def test_start_container_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers/{container_id}/start endpoint returns 200 and starts container."""
        response = mock_client.post("/containers/container_short_id/start")
        assert response.status_code == ResponseCode.OK


class TestStopContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/stop endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_stop_container(self, mock_server: PiDashboardServer, mock_request_object: Request) -> None:
        """Test the /containers/{container_id}/stop method handles valid JSON."""
        container_id = "container_short_id"
        response = asyncio.run(mock_server.stop_container(mock_request_object, container_id))

        assert response.message == "Container test-container stopped successfully"
        assert response.container_id == container_id

    def test_stop_container_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers/{container_id}/stop endpoint returns 200 and stops container."""
        response = mock_client.post("/containers/container_short_id/stop")
        assert response.status_code == ResponseCode.OK


class TestRestartContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/restart endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_restart_container(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: Request,
    ) -> None:
        """Test the /containers/{container_id}/restart method handles valid JSON and returns a model reply."""
        container_id = "container_short_id"
        response = asyncio.run(mock_server.restart_container(mock_request_object, container_id))

        assert response.message == "Container test-container restarted successfully"
        assert response.container_id == container_id

    def test_restart_container_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers/{container_id}/restart endpoint returns 200 and restarts container."""
        response = mock_client.post("/containers/container_short_id/restart")
        assert response.status_code == ResponseCode.OK


class TestUpdateContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/update endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_update_container(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: Request,
    ) -> None:
        """Test the /containers/{container_id}/update method handles valid JSON."""
        response = asyncio.run(mock_server.update_container(mock_request_object, "container_short_id"))

        assert response.message == "Container test-container updated successfully"
        assert response.container_id == "new_container_short_id"

    def test_update_container_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers/{container_id}/update endpoint returns 200 and updates container."""
        response = mock_client.post("/containers/container_short_id/update")
        assert response.status_code == ResponseCode.OK


class TestGetContainerLogsEndpoint:
    """Integration and unit tests for the /containers/{container_id}/logs endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> Request:
        """Provide a mock request object for testing."""
        return MagicMock(spec=Request)

    def test_get_container_logs(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: Request,
    ) -> None:
        """Test the /containers/{container_id}/logs method returns log lines."""
        container_id = "container_short_id"
        response = asyncio.run(mock_server.get_container_logs(mock_request_object, container_id, lines=100))

        assert response.message == f"Retrieved {len(response.logs)} log lines for container {container_id}"
        assert response.container_id == container_id
        assert response.logs == ["log line 1", "log line 2", "log line 3"]

    def test_get_container_logs_endpoint(self, mock_client: TestClient) -> None:
        """Test /containers/{container_id}/logs endpoint returns 200."""
        response = mock_client.get("/containers/container_short_id/logs?lines=100")
        assert response.status_code == ResponseCode.OK
