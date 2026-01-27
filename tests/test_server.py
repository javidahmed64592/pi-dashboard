"""Unit tests for the pi_dashboard.server module."""

import asyncio
from collections.abc import Generator
from importlib.metadata import PackageMetadata
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import Request, Security
from fastapi.routing import APIRoute
from fastapi.security import APIKeyHeader
from fastapi.testclient import TestClient
from python_template_server.models import ResponseCode

from pi_dashboard.container_handler import ContainerHandler
from pi_dashboard.models import (
    CreateNoteRequest,
    DockerContainer,
    GetSystemMetricsHistoryRequest,
    Note,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
    SystemMetricsHistory,
    UpdateNoteRequest,
    UpdateWeatherLocationRequest,
    WeatherConfig,
    WeatherData,
)
from pi_dashboard.notes_handler import NotesHandler
from pi_dashboard.server import PiDashboardServer
from pi_dashboard.weather_handler import WeatherHandler


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
def mock_weather_handler(mock_weather_data: WeatherData) -> Generator[MagicMock]:
    """Mock the WeatherHandler class."""
    with patch("pi_dashboard.server.WeatherHandler") as mock_handler_class:
        mock_handler_instance = MagicMock(spec=WeatherHandler)
        mock_handler_instance.get_weather = AsyncMock(return_value=mock_weather_data)
        mock_handler_class.return_value = mock_handler_instance
        mock_handler_class.geocode_location = AsyncMock(return_value=(51.5074, -0.1278))
        yield mock_handler_class


@pytest.fixture
def mock_server(
    mock_pi_dashboard_config: PiDashboardConfig,
    mock_get_system_info: MagicMock,
    mock_get_system_metrics: MagicMock,
    mock_system_metrics_history: SystemMetricsHistory,
    mock_notes_handler: NotesHandler,
    mock_weather_handler: MagicMock,
    mock_container_handler: ContainerHandler,
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
        patch("pi_dashboard.server.SystemMetricsHistory", return_value=mock_system_metrics_history),
        patch("pi_dashboard.server.NotesHandler", return_value=mock_notes_handler),
        patch("pi_dashboard.server.ContainerHandler", return_value=mock_container_handler),
    ):
        server = PiDashboardServer(config=mock_pi_dashboard_config)
        yield server


class TestPiDashboardServer:
    """Unit tests for the PiDashboardServer class."""

    def test_init(self, mock_server: PiDashboardServer, mock_system_metrics_history: SystemMetricsHistory) -> None:
        """Test PiDashboardServer initialization."""
        assert isinstance(mock_server.config, PiDashboardConfig)
        assert mock_server.metrics_history == mock_system_metrics_history

    def test_data_dir(self, mock_server: PiDashboardServer) -> None:
        """Test data directory property."""
        expected_path = mock_server.data_dir
        assert expected_path.exists()
        assert expected_path.is_dir()

    def test_current_timestamp_int(self, mock_server: PiDashboardServer) -> None:
        """Test current timestamp integer retrieval."""
        assert isinstance(mock_server._current_timestamp_int(), int)

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
            "/notes/{note_id}",
            "/weather",
            "/weather/location",
            "/containers",
            "/containers/refresh",
            "/containers/{container_id}/start",
            "/containers/{container_id}/stop",
            "/containers/{container_id}/restart",
            "/containers/{container_id}/update",
        ]
        for endpoint in expected_endpoints:
            assert endpoint in routes, f"Expected endpoint {endpoint} not found in routes"


class TestGetSystemInfoEndpoint:
    """Integration and unit tests for the /system/info endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_system_info(
        self, mock_server: PiDashboardServer, mock_request_object: MagicMock, mock_system_info: SystemInfo
    ) -> None:
        """Test the /system/info method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.get_system_info(mock_request_object))

        assert response.message == "Retrieved system info successfully"
        assert isinstance(response.timestamp, str)
        assert response.info == mock_system_info

    def test_get_system_info_endpoint(self, mock_server: PiDashboardServer, mock_system_info: SystemInfo) -> None:
        """Test /system/info endpoint returns 200 and includes system info."""
        app = mock_server.app
        client = TestClient(app)

        response = client.get("/system/info")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Retrieved system info successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["info"] == mock_system_info.model_dump()


class TestGetSystemMetricsEndpoint:
    """Integration and unit tests for the /system/metrics endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_system_metrics(
        self, mock_server: PiDashboardServer, mock_request_object: MagicMock, mock_system_metrics: SystemMetrics
    ) -> None:
        """Test the /system/metrics method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.get_system_metrics(mock_request_object))
        assert response.message == "Retrieved system metrics successfully"
        assert isinstance(response.timestamp, str)
        assert response.metrics == mock_system_metrics

    def test_get_system_metrics_endpoint(
        self, mock_server: PiDashboardServer, mock_system_metrics: SystemMetrics
    ) -> None:
        """Test /system/metrics endpoint returns 200 and includes system metrics."""
        app = mock_server.app
        client = TestClient(app)

        response = client.get("/system/metrics")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Retrieved system metrics successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["metrics"] == mock_system_metrics.model_dump()


class TestGetSystemMetricsHistoryEndpoint:
    """Integration and unit tests for the /system/metrics/history endpoint."""

    @pytest.fixture
    def mock_request_body(self) -> GetSystemMetricsHistoryRequest:
        """Provide a mock request body for system metrics history."""
        return GetSystemMetricsHistoryRequest(last_n_seconds=300)

    @pytest.fixture
    def mock_request_object(self, mock_request_body: GetSystemMetricsHistoryRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_request_body.model_dump())
        return request

    def test_get_system_metrics_history(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_system_metrics_history: SystemMetricsHistory,
    ) -> None:
        """Test the /system/metrics/history method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.get_system_metrics_history(mock_request_object))
        assert response.message == "Retrieved system metrics history successfully"
        assert isinstance(response.timestamp, str)
        assert response.history == mock_system_metrics_history

    def test_get_system_metrics_history_endpoint(
        self,
        mock_server: PiDashboardServer,
        mock_request_body: GetSystemMetricsHistoryRequest,
        mock_system_metrics_history: SystemMetricsHistory,
    ) -> None:
        """Test /system/metrics/history endpoint returns 200 and includes system metrics history."""
        app = mock_server.app
        client = TestClient(app)

        response = client.post("/system/metrics/history", json=mock_request_body.model_dump())
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Retrieved system metrics history successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["history"] == mock_system_metrics_history.model_dump()


class TestGetNotesEndpoint:
    """Integration and unit tests for the /notes endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_notes(
        self, mock_server: PiDashboardServer, mock_request_object: MagicMock, mock_notes_handler: NotesHandler
    ) -> None:
        """Test the /notes method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.get_notes(mock_request_object))

        assert response.message == "Retrieved notes successfully"
        assert isinstance(response.timestamp, str)
        assert response.notes == mock_notes_handler.get_all_notes()

    def test_get_notes_endpoint(self, mock_server: PiDashboardServer, mock_notes_handler: NotesHandler) -> None:
        """Test /notes endpoint returns 200 and includes all notes."""
        app = mock_server.app
        client = TestClient(app)

        response = client.get("/notes")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Retrieved notes successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["notes"] == mock_notes_handler.get_all_notes().model_dump()


class TestCreateNoteEndpoint:
    """Integration and unit tests for the /notes endpoint."""

    @pytest.fixture
    def mock_request_body(self) -> CreateNoteRequest:
        """Provide a mock request body for creating a note."""
        return CreateNoteRequest(title="Test Note", content="This is a test note.")

    @pytest.fixture
    def mock_request_object(self, mock_request_body: CreateNoteRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_request_body.model_dump())
        return request

    def test_create_note(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_notes_handler: NotesHandler,
    ) -> None:
        """Test the /notes method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.create_note(mock_request_object))

        assert response.message == "Created note successfully"
        assert isinstance(response.timestamp, str)
        assert response.note.title == mock_request_object.json.return_value["title"]
        assert response.note.content == mock_request_object.json.return_value["content"]

        created_note = mock_server.notes_handler.collection.get_note_by_id(response.note.id)
        assert created_note is not None
        assert created_note.title == mock_request_object.json.return_value["title"]
        assert created_note.content == mock_request_object.json.return_value["content"]

    def test_create_note_endpoint(
        self,
        mock_server: PiDashboardServer,
        mock_request_body: CreateNoteRequest,
        mock_notes_handler: NotesHandler,
    ) -> None:
        """Test /notes endpoint returns 200 and includes created note."""
        app = mock_server.app
        client = TestClient(app)

        response = client.post("/notes", json=mock_request_body.model_dump())
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Created note successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["note"]["title"] == mock_request_body.title
        assert response_body["note"]["content"] == mock_request_body.content


class TestUpdateNoteEndpoint:
    """Integration and unit tests for the /notes/{note_id} endpoint."""

    @pytest.fixture
    def mock_request_body(self) -> UpdateNoteRequest:
        """Provide a mock request body for updating a note."""
        return UpdateNoteRequest(title="Updated Test Note", content="This is an updated test note.")

    @pytest.fixture
    def mock_request_object(self, mock_request_body: UpdateNoteRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_request_body.model_dump())
        return request

    def test_update_note(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_notes_handler: NotesHandler,
        mock_note: Note,
    ) -> None:
        """Test the /notes/{note_id} method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.update_note(mock_request_object, mock_note.id))

        assert response.message == "Updated note successfully"
        assert isinstance(response.timestamp, str)
        assert response.note.title == mock_request_object.json.return_value["title"]
        assert response.note.content == mock_request_object.json.return_value["content"]

        updated_note = mock_server.notes_handler.collection.get_note_by_id(mock_note.id)
        assert updated_note is not None
        assert updated_note.title == mock_request_object.json.return_value["title"]
        assert updated_note.content == mock_request_object.json.return_value["content"]

    def test_update_note_endpoint(
        self,
        mock_server: PiDashboardServer,
        mock_request_body: UpdateNoteRequest,
        mock_notes_handler: NotesHandler,
        mock_note: Note,
    ) -> None:
        """Test /notes/{note_id} endpoint returns 200 and includes updated note."""
        app = mock_server.app
        client = TestClient(app)

        response = client.put(f"/notes/{mock_note.id}", json=mock_request_body.model_dump())
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Updated note successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["note"]["title"] == mock_request_body.title
        assert response_body["note"]["content"] == mock_request_body.content


class TestDeleteNoteEndpoint:
    """Integration and unit tests for the /notes/{note_id} endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_delete_note(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_notes_handler: NotesHandler,
        mock_note: Note,
    ) -> None:
        """Test the /notes/{note_id} method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.delete_note(mock_request_object, mock_note.id))

        assert response.message == "Deleted note successfully"
        assert isinstance(response.timestamp, str)

        deleted_note = mock_server.notes_handler.collection.get_note_by_id(mock_note.id)
        assert deleted_note is None

    def test_delete_note_endpoint(
        self,
        mock_server: PiDashboardServer,
        mock_notes_handler: NotesHandler,
        mock_note: Note,
    ) -> None:
        """Test /notes/{note_id} endpoint returns 200 and confirms deletion."""
        app = mock_server.app
        client = TestClient(app)

        response = client.delete(f"/notes/{mock_note.id}")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Deleted note successfully"
        assert isinstance(response_body["timestamp"], str)


class TestGetWeatherEndpoint:
    """Integration and unit tests for the /weather endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_weather(
        self, mock_server: PiDashboardServer, mock_request_object: MagicMock, mock_weather_data: WeatherData
    ) -> None:
        """Test the /weather method handles valid request and returns weather data."""
        response = asyncio.run(mock_server.get_weather(mock_request_object))

        assert response.message == "Retrieved weather data successfully"
        assert isinstance(response.timestamp, str)
        assert response.weather == mock_weather_data

    def test_get_weather_endpoint(self, mock_server: PiDashboardServer, mock_weather_data: WeatherData) -> None:
        """Test /weather endpoint returns 200 and includes weather data."""
        app = mock_server.app
        client = TestClient(app)

        response = client.get("/weather")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Retrieved weather data successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["weather"] == mock_weather_data.model_dump()


class TestGetWeatherLocationEndpoint:
    """Integration and unit tests for the /weather/location endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        return MagicMock(spec=Request)

    def test_get_weather_location(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_pi_dashboard_config: PiDashboardConfig,
    ) -> None:
        """Test the /weather/location method returns configured location."""
        response = asyncio.run(mock_server.get_weather_location(mock_request_object))

        assert response.message == "Retrieved weather location successfully"
        assert isinstance(response.timestamp, str)
        assert response.location_name == mock_pi_dashboard_config.weather.location_name
        assert response.latitude == mock_pi_dashboard_config.weather.latitude
        assert response.longitude == mock_pi_dashboard_config.weather.longitude

    def test_get_weather_location_endpoint(
        self, mock_server: PiDashboardServer, mock_pi_dashboard_config: PiDashboardConfig
    ) -> None:
        """Test /weather/location endpoint returns 200 and includes location info."""
        app = mock_server.app
        client = TestClient(app)

        response = client.get("/weather/location")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Retrieved weather location successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["location_name"] == mock_pi_dashboard_config.weather.location_name
        assert response_body["latitude"] == mock_pi_dashboard_config.weather.latitude
        assert response_body["longitude"] == mock_pi_dashboard_config.weather.longitude


class TestUpdateWeatherLocationEndpoint:
    """Integration and unit tests for the /weather/location PUT endpoint."""

    @pytest.fixture
    def mock_request_body(self) -> UpdateWeatherLocationRequest:
        """Provide a mock request body for updating weather location."""
        return UpdateWeatherLocationRequest(location="London")

    @pytest.fixture
    def mock_request_object(self, mock_request_body: UpdateWeatherLocationRequest) -> MagicMock:
        """Provide a mock Request object with JSON data."""
        request = MagicMock(spec=Request)
        request.json = AsyncMock(return_value=mock_request_body.model_dump())
        return request

    def test_update_weather_location(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_weather_handler: MagicMock,
        mock_weather_config: WeatherConfig,
    ) -> None:
        """Test the /weather/location PUT method updates location and reinitializes handler."""
        response = asyncio.run(mock_server.update_weather_location(mock_request_object))

        assert response.message == "Updated weather location successfully"
        assert isinstance(response.timestamp, str)
        assert response.latitude == mock_weather_config.latitude
        assert response.longitude == mock_weather_config.longitude
        assert response.location_name == mock_weather_config.location_name

        # Verify WeatherHandler.geocode_location was called
        mock_weather_handler.geocode_location.assert_called_once_with("London")

    def test_update_weather_location_endpoint(
        self,
        mock_server: PiDashboardServer,
        mock_request_body: UpdateWeatherLocationRequest,
        mock_weather_handler: MagicMock,
        mock_weather_config: WeatherConfig,
    ) -> None:
        """Test /weather/location PUT endpoint returns 200 and updates location."""
        app = mock_server.app
        client = TestClient(app)

        response = client.put("/weather/location", json=mock_request_body.model_dump())
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert response_body["message"] == "Updated weather location successfully"
        assert isinstance(response_body["timestamp"], str)
        assert response_body["latitude"] == mock_weather_config.latitude
        assert response_body["longitude"] == mock_weather_config.longitude


class TestListContainersEndpoint:
    """Integration and unit tests for the /containers endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock request object for testing."""
        return MagicMock()

    def test_list_containers(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_container_handler: ContainerHandler,
    ) -> None:
        """Test the /containers method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.list_containers(mock_request_object))

        assert "Retrieved 2 containers" in response.message
        assert isinstance(response.timestamp, str)
        assert len(response.containers) == 2  # noqa: PLR2004

    def test_list_containers_endpoint(
        self, mock_server: PiDashboardServer, mock_docker_containers: list[DockerContainer]
    ) -> None:
        """Test /containers endpoint returns 200 and includes container list."""
        app = mock_server.app
        client = TestClient(app)

        response = client.get("/containers")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert "Retrieved 2 containers" in response_body["message"]
        assert isinstance(response_body["timestamp"], str)
        assert len(response_body["containers"]) == 2  # noqa: PLR2004
        assert response_body["containers"][0] == mock_docker_containers[0].model_dump()


class TestRefreshContainersEndpoint:
    """Integration and unit tests for the /containers/refresh endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock request object for testing."""
        return MagicMock()

    def test_refresh_containers(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_container_handler: ContainerHandler,
    ) -> None:
        """Test the /containers/refresh method handles valid JSON and returns a model reply."""
        response = asyncio.run(mock_server.refresh_containers(mock_request_object))

        assert "Retrieved 2 containers" in response.message
        assert isinstance(response.timestamp, str)
        assert len(response.containers) == 2  # noqa: PLR2004

    def test_refresh_containers_endpoint(
        self, mock_server: PiDashboardServer, mock_docker_containers: list[DockerContainer]
    ) -> None:
        """Test /containers/refresh endpoint returns 200 and includes refreshed container list."""
        app = mock_server.app
        client = TestClient(app)

        response = client.post("/containers/refresh")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert "Retrieved 2 containers" in response_body["message"]
        assert isinstance(response_body["timestamp"], str)
        assert len(response_body["containers"]) == 2  # noqa: PLR2004


class TestStartContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/start endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock request object for testing."""
        return MagicMock()

    def test_start_container(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_container_handler: ContainerHandler,
    ) -> None:
        """Test the /containers/{container_id}/start method handles valid JSON and returns a model reply."""
        container_id = "abc123def456"
        response = asyncio.run(mock_server.start_container(mock_request_object, container_id))

        assert f"Container started: {container_id}" in response.message
        assert isinstance(response.timestamp, str)
        assert response.container_id == container_id
        assert response.action == "start"

    def test_start_container_endpoint(self, mock_server: PiDashboardServer) -> None:
        """Test /containers/{container_id}/start endpoint returns 200 and starts container."""
        app = mock_server.app
        client = TestClient(app)

        container_id = "abc123def456"
        response = client.post(f"/containers/{container_id}/start")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert f"Container started: {container_id}" in response_body["message"]
        assert isinstance(response_body["timestamp"], str)
        assert response_body["container_id"] == container_id
        assert response_body["action"] == "start"


class TestStopContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/stop endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock request object for testing."""
        return MagicMock()

    def test_stop_container(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_container_handler: ContainerHandler,
    ) -> None:
        """Test the /containers/{container_id}/stop method handles valid JSON and returns a model reply."""
        container_id = "abc123def456"
        response = asyncio.run(mock_server.stop_container(mock_request_object, container_id))

        assert f"Container stopped: {container_id}" in response.message
        assert isinstance(response.timestamp, str)
        assert response.container_id == container_id
        assert response.action == "stop"

    def test_stop_container_endpoint(self, mock_server: PiDashboardServer) -> None:
        """Test /containers/{container_id}/stop endpoint returns 200 and stops container."""
        app = mock_server.app
        client = TestClient(app)

        container_id = "abc123def456"
        response = client.post(f"/containers/{container_id}/stop")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert f"Container stopped: {container_id}" in response_body["message"]
        assert isinstance(response_body["timestamp"], str)
        assert response_body["container_id"] == container_id
        assert response_body["action"] == "stop"


class TestRestartContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/restart endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock request object for testing."""
        return MagicMock()

    def test_restart_container(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_container_handler: ContainerHandler,
    ) -> None:
        """Test the /containers/{container_id}/restart method handles valid JSON and returns a model reply."""
        container_id = "abc123def456"
        response = asyncio.run(mock_server.restart_container(mock_request_object, container_id))

        assert f"Container restarted: {container_id}" in response.message
        assert isinstance(response.timestamp, str)
        assert response.container_id == container_id
        assert response.action == "restart"

    def test_restart_container_endpoint(self, mock_server: PiDashboardServer) -> None:
        """Test /containers/{container_id}/restart endpoint returns 200 and restarts container."""
        app = mock_server.app
        client = TestClient(app)

        container_id = "abc123def456"
        response = client.post(f"/containers/{container_id}/restart")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert f"Container restarted: {container_id}" in response_body["message"]
        assert isinstance(response_body["timestamp"], str)
        assert response_body["container_id"] == container_id
        assert response_body["action"] == "restart"


class TestUpdateContainerEndpoint:
    """Integration and unit tests for the /containers/{container_id}/update endpoint."""

    @pytest.fixture
    def mock_request_object(self) -> MagicMock:
        """Provide a mock request object for testing."""
        return MagicMock()

    def test_update_container(
        self,
        mock_server: PiDashboardServer,
        mock_request_object: MagicMock,
        mock_container_handler: ContainerHandler,
    ) -> None:
        """Test the /containers/{container_id}/update method handles valid JSON and returns a model reply."""
        container_id = "abc123def456"
        response = asyncio.run(mock_server.update_container(mock_request_object, container_id))

        assert f"Container updated: {container_id}" in response.message
        assert isinstance(response.timestamp, str)
        assert response.container_id == container_id
        assert response.action == "update"

    def test_update_container_endpoint(self, mock_server: PiDashboardServer) -> None:
        """Test /containers/{container_id}/update endpoint returns 200 and updates container."""
        app = mock_server.app
        client = TestClient(app)

        container_id = "abc123def456"
        response = client.post(f"/containers/{container_id}/update")
        assert response.status_code == ResponseCode.OK

        response_body = response.json()
        assert f"Container updated: {container_id}" in response_body["message"]
        assert isinstance(response_body["timestamp"], str)
        assert response_body["container_id"] == container_id
        assert response_body["action"] == "update"
