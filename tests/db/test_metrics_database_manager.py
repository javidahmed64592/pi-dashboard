"""Unit tests for the pi_dashboard.db.metrics_database_manager module."""

import pytest
from sqlalchemy.engine import Engine

from pi_dashboard.db import MetricsDatabaseManager
from pi_dashboard.models import DatabaseAction, SystemMetrics


class TestMetricsDatabaseManager:
    """Tests for the MetricsDatabaseManager class."""

    def test_init_creates_database(self, mock_metrics_database_manager: MetricsDatabaseManager) -> None:
        """Test MetricsDatabaseManager initialization creates the database directory and file."""
        assert isinstance(mock_metrics_database_manager.engine, Engine)

    def test_get_all_metrics_entries(self, mock_metrics_database_manager: MetricsDatabaseManager) -> None:
        """Test retrieving all metrics entries."""
        metrics_entries = mock_metrics_database_manager.get_all_metrics_entries()
        assert isinstance(metrics_entries, list)
        assert all(isinstance(metrics, SystemMetrics) for metrics in metrics_entries)

    def test_perform_metrics_action_create(
        self, mock_metrics_database_manager: MetricsDatabaseManager, mock_system_metrics: SystemMetrics
    ) -> None:
        """Test creating a metrics entry."""
        initial_metrics_count = len(mock_metrics_database_manager.get_all_metrics_entries())
        metrics_id = mock_metrics_database_manager.perform_metrics_action(mock_system_metrics, DatabaseAction.CREATE)
        assert isinstance(metrics_id, int)
        assert len(mock_metrics_database_manager.get_all_metrics_entries()) == initial_metrics_count + 1

    def test_perform_metrics_action_unsupported(self, mock_metrics_database_manager: MetricsDatabaseManager) -> None:
        """Test performing an unsupported metrics action."""
        with pytest.raises(NotImplementedError, match=rf"Unsupported action: {DatabaseAction.UPDATE}"):
            mock_metrics_database_manager.perform_metrics_action(
                SystemMetrics(cpu_usage=0, memory_usage=0, disk_usage=0, uptime=0, temperature=0, timestamp=0),
                DatabaseAction.UPDATE,
            )

    def test_cleanup_old_metrics(self, mock_metrics_database_manager: MetricsDatabaseManager) -> None:
        """Test cleaning up old metrics entries."""
        initial_metrics_count = len(mock_metrics_database_manager.get_all_metrics_entries())
        mock_metrics_database_manager.cleanup_old_metrics()
        assert len(mock_metrics_database_manager.get_all_metrics_entries()) == initial_metrics_count - 1
