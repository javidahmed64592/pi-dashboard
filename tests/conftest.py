"""Pytest fixtures for the application's unit tests."""

from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

from pi_dashboard.models import (
    MetricsConfig,
    Note,
    NotesCollection,
    PiDashboardConfig,
    SystemInfo,
    SystemMetrics,
    SystemMetricsHistory,
    SystemMetricsHistoryEntry,
)
from pi_dashboard.notes_handler import NotesHandler


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
