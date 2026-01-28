"""Pytest fixtures for the application's unit tests."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pi_dashboard.container_handler import ContainerHandler
from pi_dashboard.models import (
    MetricsConfig,
    Note,
    NotesCollection,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
    SystemMetricsHistory,
    SystemMetricsHistoryEntry,
    WeatherConfig,
    WeatherData,
    WeatherForecastHour,
)
from pi_dashboard.notes_handler import NotesHandler


# Pi Dashboard server configuration fixtures
@pytest.fixture
def mock_metrics_config() -> MetricsConfig:
    """Provide a MetricsConfig instance for testing."""
    return MetricsConfig.model_validate({})


@pytest.fixture
def mock_weather_config() -> WeatherConfig:
    """Provide a WeatherConfig instance for testing."""
    return WeatherConfig.model_validate(
        {
            "latitude": 12.34,
            "longitude": 56.78,
            "location_name": "Test Location",
            "forecast_hours": 12,
        }
    )


@pytest.fixture
def mock_pi_dashboard_config(
    mock_metrics_config: MetricsConfig, mock_weather_config: WeatherConfig
) -> PiDashboardConfig:
    """Provide a PiDashboardConfig instance for testing."""
    return PiDashboardConfig(metrics=mock_metrics_config, weather=mock_weather_config)


# General model fixtures
@pytest.fixture
def mock_system_info() -> SystemInfo:
    """Provide a SystemInfo instance for testing."""
    return SystemInfo.model_validate(
        {
            "hostname": "test-host",
            "system": "test-system",
            "release": "1.2.3",
            "version": "test-version",
            "machine": "test-machine",
            "memory_total": 8.0,
            "disk_total": 256.0,
        }
    )


@pytest.fixture
def mock_system_metrics() -> SystemMetrics:
    """Provide a SystemMetrics instance for testing."""
    return SystemMetrics.model_validate(
        {
            "cpu_usage": 45.5,
            "memory_usage": 60.2,
            "disk_usage": 70.1,
            "uptime": 123456,
            "temperature": 55.0,
        }
    )


@pytest.fixture
def mock_system_metrics_history_entry(mock_system_metrics: SystemMetrics) -> SystemMetricsHistoryEntry:
    """Provide a SystemMetricsHistoryEntry instance for testing."""
    return SystemMetricsHistoryEntry.model_validate(
        {
            "metrics": mock_system_metrics.model_dump(),
            "timestamp": 1234,
        }
    )


@pytest.fixture
def mock_system_metrics_history(mock_system_metrics_history_entry: SystemMetricsHistoryEntry) -> SystemMetricsHistory:
    """Provide a SystemMetricsHistory instance for testing."""
    history = SystemMetricsHistory()
    for i in range(10):
        timestamp = mock_system_metrics_history_entry.timestamp + (i * 60)
        entry = SystemMetricsHistoryEntry(
            metrics=mock_system_metrics_history_entry.metrics,
            timestamp=timestamp,
        )
        history.add_entry(entry)
    return history


# Notes model fixtures
@pytest.fixture
def mock_note() -> Note:
    """Provide a Note instance for testing."""
    return Note.model_validate(
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Test Note",
            "content": "This is a test note.",
            "created_at": "2026-01-01T12:00:00Z",
            "updated_at": "2026-01-01T12:00:00Z",
        }
    )


@pytest.fixture
def mock_notes_collection(mock_note: Note) -> NotesCollection:
    """Provide a NotesCollection instance for testing."""
    return NotesCollection.model_validate(
        {
            "notes": [mock_note.model_dump()],
        }
    )


@pytest.fixture
def mock_notes_handler(tmp_path: Path, mock_notes_collection: NotesCollection) -> Generator[NotesHandler]:
    """Provide a NotesHandler instance for testing."""
    with (
        patch.object(NotesHandler, "_load_or_create_notes_file"),
        patch.object(NotesHandler, "_write_notes"),
    ):
        handler = NotesHandler(tmp_path)
        handler.collection = mock_notes_collection
        yield handler


# Weather model fixtures
@pytest.fixture
def mock_weather_forecast_hours() -> list[WeatherForecastHour]:
    """Provide a list of WeatherForecastHour instances for testing."""
    return [
        WeatherForecastHour(time="12PM", temperature=22.5, weather_code=1),
        WeatherForecastHour(time="1PM", temperature=23.0, weather_code=1),
        WeatherForecastHour(time="2PM", temperature=24.5, weather_code=2),
        WeatherForecastHour(time="3PM", temperature=25.0, weather_code=2),
        WeatherForecastHour(time="4PM", temperature=24.0, weather_code=3),
        WeatherForecastHour(time="5PM", temperature=23.5, weather_code=3),
        WeatherForecastHour(time="6PM", temperature=22.0, weather_code=61),
        WeatherForecastHour(time="7PM", temperature=21.0, weather_code=61),
        WeatherForecastHour(time="8PM", temperature=20.5, weather_code=63),
        WeatherForecastHour(time="9PM", temperature=19.5, weather_code=63),
        WeatherForecastHour(time="10PM", temperature=19.0, weather_code=45),
        WeatherForecastHour(time="11PM", temperature=18.5, weather_code=45),
    ]


@pytest.fixture
def mock_weather_data(mock_weather_forecast_hours: list[WeatherForecastHour]) -> WeatherData:
    """Provide a WeatherData instance for testing."""
    return WeatherData.model_validate(
        {
            "location_name": "Test Location",
            "temperature": 22.5,
            "weather_code": 1,
            "high": 25.0,
            "low": 17.5,
            "humidity": 65,
            "wind_speed": 12.5,
            "forecast": [hour.model_dump() for hour in mock_weather_forecast_hours],
        }
    )


# Docker fixtures
@pytest.fixture
def mock_container() -> Mock:
    """Provide a mock Docker container."""
    container = Mock()
    container.short_id = "abc123def456"
    container.name = "test-container"
    container.status = "running"
    container.ports = {
        "443/tcp": [{"HostIp": "0.0.0.0", "HostPort": "443"}],  # noqa: S104
        "80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}],  # noqa: S104
    }

    # Mock image
    mock_image = Mock()
    mock_image.tags = ["test/image:latest"]
    mock_image.id = "sha256:abcdef123456"
    container.image = mock_image

    # Mock attrs
    container.attrs = {
        "Created": "2024-01-01T00:00:00.000000000Z",
        "Config": {
            "Env": ["ENV_VAR=value"],
        },
        "HostConfig": {
            "PortBindings": {"443/tcp": [{"HostPort": "443"}]},
            "Binds": ["/data:/app/data"],
            "NetworkMode": "bridge",
            "RestartPolicy": {"Name": "unless-stopped"},
        },
    }

    return container


@pytest.fixture
def mock_docker_client(mock_container: Mock) -> Mock:
    """Provide a mock Docker client for testing."""
    client = Mock()
    client.ping.return_value = True
    client.containers.list.return_value = [mock_container]
    client.containers.get.return_value = mock_container
    return client


@pytest.fixture
def mock_container_handler(mock_docker_client: Mock) -> ContainerHandler:
    """Provide a ContainerHandler instance with mocked Docker client."""
    with (
        patch("docker.from_env", return_value=mock_docker_client),
    ):
        return ContainerHandler()
