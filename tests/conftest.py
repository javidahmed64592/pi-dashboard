"""Pytest fixtures for the application's unit tests."""

from unittest.mock import MagicMock, patch

import pytest

from pi_dashboard.container_handler import ContainerHandler
from pi_dashboard.models import (
    MetricsConfig,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
    SystemMetricsHistory,
    SystemMetricsHistoryEntry,
)


# Pi Dashboard server configuration fixtures
@pytest.fixture
def mock_metrics_config() -> MetricsConfig:
    """Provide a MetricsConfig instance for testing."""
    return MetricsConfig.model_validate({})


@pytest.fixture
def mock_pi_dashboard_config(
    mock_metrics_config: MetricsConfig,
) -> PiDashboardConfig:
    """Provide a PiDashboardConfig instance for testing."""
    return PiDashboardConfig(metrics=mock_metrics_config)


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
def mock_container_handler(mock_docker_client: MagicMock) -> ContainerHandler:
    """Provide a ContainerHandler instance with mocked Docker client."""
    with (
        patch("docker.from_env", return_value=mock_docker_client),
    ):
        return ContainerHandler()
