"""Unit tests for the pi_dashboard.models module."""

from pi_dashboard.models import (
    MetricsConfig,
    PiDashboardConfig,
    SystemMetricsHistory,
    SystemMetricsHistoryEntry,
)


# Pi Dashboard server configuration
class TestPiDashboardConfig:
    """Unit tests for the PiDashboardConfig class."""

    def test_model_dump(
        self,
        mock_pi_dashboard_config: PiDashboardConfig,
        mock_metrics_config: MetricsConfig,
    ) -> None:
        """Test the model_dump method."""
        assert mock_metrics_config.model_dump() == mock_pi_dashboard_config.model_dump()["metrics"]


# General models
class TestSystemMetricsHistory:
    """Unit tests for the SystemMetricsHistory class."""

    def test_add_entry(
        self,
        mock_system_metrics_history: SystemMetricsHistory,
        mock_system_metrics_history_entry: SystemMetricsHistoryEntry,
    ) -> None:
        """Test the add_entry method."""
        initial_length = len(mock_system_metrics_history.history)
        mock_system_metrics_history.add_entry(mock_system_metrics_history_entry)
        assert len(mock_system_metrics_history.history) == initial_length + 1
        assert mock_system_metrics_history.history[-1] == mock_system_metrics_history_entry

    def test_cleanup_old_entries(
        self,
        mock_system_metrics_history: SystemMetricsHistory,
    ) -> None:
        """Test the cleanup_old_entries method."""
        # Cleanup old entries with max_duration of 5 minutes
        max_age_seconds = 300
        current_time = mock_system_metrics_history.history[-1].timestamp
        mock_system_metrics_history.cleanup_old_entries(max_age_seconds=max_age_seconds, current_time=current_time)
        entries = mock_system_metrics_history.history

        # Verify that the old entry has been removed
        assert all(entry.timestamp >= current_time - max_age_seconds for entry in entries)

    def test_get_entries_since(
        self,
        mock_system_metrics_history: SystemMetricsHistory,
    ) -> None:
        """Test the get_entries_since method."""
        # Get entries since 5 minutes ago
        seconds_ago = 300
        current_time = mock_system_metrics_history.history[-1].timestamp
        entries = mock_system_metrics_history.get_entries_since(seconds_ago=seconds_ago, current_time=current_time)

        # Verify that the returned entries are within the specified time frame
        assert all(entry.timestamp >= current_time - seconds_ago for entry in entries)
