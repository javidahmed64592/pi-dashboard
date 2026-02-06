"""Unit tests for the pi_dashboard.models module."""

import pytest

from pi_dashboard.models import (
    MetricsConfig,
    Note,
    NotesCollection,
    PiDashboardConfig,
    SystemMetrics,
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
        """Test the get_entries_since method without pruning."""
        # Get entries since 5 minutes ago with max_data_points higher than entries
        seconds_ago = 300
        current_time = mock_system_metrics_history.history[-1].timestamp
        entries = mock_system_metrics_history.get_entries_since(
            seconds_ago=seconds_ago, current_time=current_time, max_data_points=1000
        )

        # Verify that the returned entries are within the specified time frame
        assert all(entry.timestamp >= current_time - seconds_ago for entry in entries)

    @pytest.mark.parametrize(
        ("total_entries", "max_data_points", "expected_count"),
        [
            (100, 25, 25),  # Downsample 100 entries to 25
            (50, 100, 50),  # No downsampling needed (fewer entries than max)
            (100, 100, 100),  # Exact match
        ],
    )
    def test_get_entries_since_with_pruning(
        self,
        mock_system_metrics: SystemMetrics,
        total_entries: int,
        max_data_points: int,
        expected_count: int,
    ) -> None:
        """Test the get_entries_since method with various pruning scenarios."""
        # Create a history with specified number of entries
        history = SystemMetricsHistory()
        base_timestamp = 1000
        for i in range(total_entries):
            entry = SystemMetricsHistoryEntry(
                metrics=mock_system_metrics,
                timestamp=base_timestamp + (i * 5),  # 5 second intervals
            )
            history.add_entry(entry)

        # Get entries with max_data_points
        current_time = history.history[-1].timestamp
        seconds_ago = total_entries * 5  # Enough to include all entries
        entries = history.get_entries_since(
            seconds_ago=seconds_ago, current_time=current_time, max_data_points=max_data_points
        )

        # Verify the count matches expected
        assert len(entries) == expected_count

        # Verify all entries are within the time range
        assert all(entry.timestamp >= current_time - seconds_ago for entry in entries)

        # Verify entries are properly spaced (if downsampling occurred)
        if total_entries > max_data_points:
            # Check that we're getting evenly distributed samples
            assert entries[0].timestamp == history.history[0].timestamp  # First entry
            assert entries[-1].timestamp <= history.history[-1].timestamp  # Last or near-last entry


# Notes models
class TestNotesCollection:
    """Unit tests for the NotesCollection class."""

    def test_get_note_by_id(
        self,
        mock_notes_collection: NotesCollection,
        mock_note: Note,
    ) -> None:
        """Test the get_note_by_id method."""
        retrieved_note = mock_notes_collection.get_note_by_id(mock_note.id)
        assert retrieved_note == mock_note

    def test_get_note_by_id_not_found(
        self,
        mock_notes_collection: NotesCollection,
    ) -> None:
        """Test the get_note_by_id method when note is not found."""
        retrieved_note = mock_notes_collection.get_note_by_id("non-existent-id")
        assert retrieved_note is None

    def test_add_note(
        self,
        mock_notes_collection: NotesCollection,
    ) -> None:
        """Test the add_note method."""
        initial_length = len(mock_notes_collection.notes)
        note = mock_notes_collection.add_note(
            title="New Note",
            content="This is a new note.",
            current_timestamp="2024-01-01T12:00:00Z",
        )
        assert len(mock_notes_collection.notes) == initial_length + 1
        assert note in mock_notes_collection.notes

    def test_update_note(
        self,
        mock_notes_collection: NotesCollection,
        mock_note: Note,
    ) -> None:
        """Test the update_note method."""
        new_title = "Updated Title"
        updated_note = mock_notes_collection.update_note(
            note_id=mock_note.id,
            current_timestamp="2024-01-01T13:00:00Z",
            title=new_title,
            content=None,
        )
        assert updated_note is not None
        assert updated_note.title == new_title
        assert updated_note.content == mock_note.content  # Content should remain unchanged

    def test_update_note_not_found(
        self,
        mock_notes_collection: NotesCollection,
    ) -> None:
        """Test the update_note method when note is not found."""
        updated_note = mock_notes_collection.update_note(
            note_id="non-existent-id",
            current_timestamp="2024-01-01T13:00:00Z",
            title="Title",
            content="Content",
        )
        assert updated_note is None

    def test_delete_note(
        self,
        mock_notes_collection: NotesCollection,
        mock_note: Note,
    ) -> None:
        """Test the delete_note method."""
        success = mock_notes_collection.delete_note(mock_note.id)
        assert success is True
        assert mock_notes_collection.get_note_by_id(mock_note.id) is None

    def test_delete_note_not_found(
        self,
        mock_notes_collection: NotesCollection,
    ) -> None:
        """Test the delete_note method when note is not found."""
        success = mock_notes_collection.delete_note("non-existent-id")
        assert success is False
