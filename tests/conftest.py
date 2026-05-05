"""Pytest fixtures for the application's unit tests."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pi_dashboard.db import MetricsDatabaseManager, NotesDatabaseManager
from pi_dashboard.docker_container_handler import DockerContainerHandler
from pi_dashboard.models import (
    DashboardDatabaseConfig,
    DatabaseAction,
    MetricsConfig,
    NoteEntry,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
    current_timestamp_int,
)


# Pi Dashboard server configuration fixtures
@pytest.fixture
def mock_database_config(tmp_path: Path) -> DashboardDatabaseConfig:
    """Provide a DashboardDatabaseConfig instance for testing."""
    return DashboardDatabaseConfig(
        db_directory=tmp_path / "data",
        metrics_db_filename="test_metrics.db",
        metrics_lifetime_days=7,
        notes_db_filename="test_notes.db",
    )


@pytest.fixture
def mock_metrics_config() -> MetricsConfig:
    """Provide a MetricsConfig instance for testing."""
    return MetricsConfig.model_validate({})


@pytest.fixture
def mock_pi_dashboard_config(
    mock_database_config: DashboardDatabaseConfig, mock_metrics_config: MetricsConfig
) -> PiDashboardConfig:
    """Provide a PiDashboardConfig instance for testing."""
    return PiDashboardConfig(db=mock_database_config, metrics=mock_metrics_config)


# Database fixtures
@pytest.fixture
def mock_metrics_database_manager(
    mock_database_config: DashboardDatabaseConfig,
    mock_system_metrics: SystemMetrics,
    mock_system_metrics_old: SystemMetrics,
) -> Generator[MetricsDatabaseManager]:
    """Provide a MetricsDatabaseManager instance for testing."""
    db_manager = MetricsDatabaseManager(db_config=mock_database_config)
    db_manager.perform_system_metrics_action(system_metrics=mock_system_metrics, action=DatabaseAction.CREATE)
    db_manager.perform_system_metrics_action(system_metrics=mock_system_metrics_old, action=DatabaseAction.CREATE)
    yield db_manager
    db_manager.engine.dispose()


@pytest.fixture
def mock_notes_database_manager(
    mock_database_config: DashboardDatabaseConfig, mock_note_entry_1: NoteEntry
) -> Generator[NotesDatabaseManager]:
    """Provide a NotesDatabaseManager instance for testing."""
    db_manager = NotesDatabaseManager(db_config=mock_database_config)
    db_manager.perform_note_action(note_entry=mock_note_entry_1, action=DatabaseAction.CREATE)
    yield db_manager
    db_manager.engine.dispose()


# Metrics model fixtures
@pytest.fixture
def mock_system_info() -> SystemInfo:
    """Provide a SystemInfo instance for testing."""
    return SystemInfo(
        hostname="test-host",
        system="test-system",
        release="1.2.3",
        version="test-version",
        machine="test-machine",
        memory_total=8.0,
        disk_total=256.0,
    )


@pytest.fixture
def mock_system_metrics() -> SystemMetrics:
    """Provide a SystemMetrics instance for testing."""
    return SystemMetrics(
        id=None,
        cpu_usage=45.5,
        memory_usage=60.2,
        disk_usage=70.1,
        uptime=123456,
        temperature=55.0,
        timestamp=current_timestamp_int(),
    )


@pytest.fixture
def mock_system_metrics_old(mock_database_config: DashboardDatabaseConfig) -> SystemMetrics:
    """Provide an old SystemMetrics instance for testing."""
    return SystemMetrics(
        id=None,
        cpu_usage=45.5,
        memory_usage=60.2,
        disk_usage=70.1,
        uptime=123456,
        temperature=55.0,
        timestamp=current_timestamp_int() - ((mock_database_config.metrics_lifetime_days + 1) * 86400),
    )


# Notes models fixtures
@pytest.fixture
def mock_note_entry_1() -> NoteEntry:
    """Provide a NoteEntry instance for testing."""
    return NoteEntry(
        id=None,
        title="Test note",
        content="This is a test note entry.",
        time_created=123,
        time_updated=123,
    )


@pytest.fixture
def mock_note_entry_2() -> NoteEntry:
    """Provide a NoteEntry instance for testing."""
    return NoteEntry(
        id=None,
        title="Test note 2",
        content="This is another test note entry.",
        time_created=234,
        time_updated=234,
    )


# Docker fixtures
@pytest.fixture
def mock_container() -> MagicMock:
    """Provide a mock Docker container."""
    container = MagicMock()
    container.short_id = "container_short_id"
    container.name = "test-container"
    container.status = "running"
    container.ports = {
        "443/tcp": [{"HostIp": "0.0.0.0", "HostPort": "443"}],  # noqa: S104
        "80/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8080"}],  # noqa: S104
    }

    # Mock image
    mock_image = MagicMock()
    mock_image.tags = ["test/image:latest"]
    mock_image.id = "sha256:abcdef123456"
    container.image = mock_image

    # Mock logs
    container.logs.return_value = b"log line 1\nlog line 2\nlog line 3\n"

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
def mock_docker_client(mock_container: MagicMock) -> MagicMock:
    """Provide a mock Docker client for testing."""
    client = MagicMock()
    client.ping.return_value = True
    client.containers.list.return_value = [mock_container]
    client.containers.get.return_value = mock_container

    # Mock the containers.run() method to return a container with proper short_id
    new_container = MagicMock()
    new_container.short_id = "new_container_short_id"
    new_container.name = "test-container"
    client.containers.run.return_value = new_container

    return client


@pytest.fixture
def mock_docker_container_handler(mock_docker_client: MagicMock) -> DockerContainerHandler:
    """Provide a DockerContainerHandler instance with mocked Docker client."""
    with (
        patch("docker.from_env", return_value=mock_docker_client),
    ):
        return DockerContainerHandler()
