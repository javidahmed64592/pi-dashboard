"""Pytest fixtures for the application's unit tests."""

import pytest

from pi_dashboard.models import (
    MetricsConfig,
    PiDashboardConfig,
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
def mock_pi_dashboard_config(mock_metrics_config: MetricsConfig) -> PiDashboardConfig:
    """Provide a PiDashboardConfig instance for testing."""
    return PiDashboardConfig(metrics=mock_metrics_config)


# General model fixtures
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
