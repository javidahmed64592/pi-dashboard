"""Pydantic models for the server."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field
from python_template_server.models import BaseResponse, TemplateServerConfig


# Pi Dashboard server configuration
class DatabaseConfig(BaseModel):
    """Configuration for the database."""

    db_directory: str = Field(
        default="data", description="The directory where the SQLite database file will be stored."
    )
    db_filename: str = Field(default="dashboard.db", description="The filename for the SQLite database.")

    @property
    def db_url(self) -> str:
        """Construct the database URL for SQLAlchemy."""
        return f"sqlite:///{self.db_directory}/{self.db_filename}"


class MetricsConfig(BaseModel):
    """Configuration model for system metrics collection."""

    collection_interval: int = Field(
        default=5, ge=1, le=60, description="Interval in seconds between metrics collections"
    )
    max_history_duration: int = Field(
        default=3600, ge=60, le=86400, description="Maximum duration in seconds to keep metrics history"
    )


class PiDashboardConfig(TemplateServerConfig):
    """Configuration model for the Pi Dashboard server."""

    db: DatabaseConfig = Field(default_factory=DatabaseConfig, description="Database configuration")
    metrics: MetricsConfig = Field(default_factory=MetricsConfig, description="System metrics collection configuration")


# Database
def current_timestamp_int() -> int:
    """Get the current Unix timestamp as an integer.

    :return int: The current Unix timestamp
    """
    return int(datetime.fromisoformat(BaseResponse.current_timestamp().rstrip("Z")).timestamp())


class DatabaseAction(StrEnum):
    """Enumeration for note actions."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


# Metrics models
class SystemInfo(BaseModel):
    """Model representing system information."""

    hostname: str = Field(..., description="System hostname")
    system: str = Field(..., description="System type")
    release: str = Field(..., description="System release")
    version: str = Field(..., description="System version")
    machine: str = Field(..., description="System machine type")
    memory_total: float = Field(..., description="Total memory in GB")
    disk_total: float = Field(..., description="Total disk space in GB")


class SystemMetrics(BaseModel):
    """Model representing system metrics."""

    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    uptime: int = Field(..., description="System uptime in seconds")
    temperature: float = Field(..., description="System temperature in Celsius")


class SystemMetricsHistoryEntry(BaseModel):
    """Model representing a single entry in system metrics history."""

    metrics: SystemMetrics = Field(..., description="System metrics data")
    timestamp: int = Field(..., description="Unix timestamp of the metrics entry")


class SystemMetricsHistory(BaseModel):
    """Model representing system metrics history."""

    history: list[SystemMetricsHistoryEntry] = Field(
        default_factory=list, description="List of system metrics history entries"
    )

    def add_entry(self, entry: SystemMetricsHistoryEntry) -> None:
        """Add a new entry to the metrics history.

        :param SystemMetricsHistoryEntry entry: The metrics history entry to add
        """
        self.history.append(entry)

    def cleanup_old_entries(self, max_age_seconds: int, current_time: int) -> None:
        """Remove entries older than the specified age.

        :param int max_age_seconds: Maximum age of entries to keep in seconds
        :param int current_time: Current Unix timestamp
        """
        cutoff_time = current_time - max_age_seconds
        self.history = [entry for entry in self.history if entry.timestamp >= cutoff_time]

    def get_entries_since(
        self, seconds_ago: int, current_time: int, max_data_points: int
    ) -> list[SystemMetricsHistoryEntry]:
        """Get entries from the last N seconds with adaptive downsampling.

        :param int seconds_ago: Number of seconds to look back
        :param int current_time: Current Unix timestamp
        :param int max_data_points: Maximum number of data points to return
        :return list[SystemMetricsHistoryEntry]: List of entries from the specified time range (downsampled if needed)
        """
        cutoff_time = current_time - seconds_ago
        entries = [entry for entry in self.history if entry.timestamp >= cutoff_time]

        # If we have fewer entries than max_data_points, return all
        if len(entries) <= max_data_points:
            return entries

        # Calculate the interval for downsampling (use float division for precision)
        interval = len(entries) / max_data_points

        # Sample evenly across the time range, always including the most recent entry
        sampled_indices = [int(i * interval) for i in range(max_data_points - 1)]
        sampled_entries = [entries[idx] for idx in sampled_indices]

        # Always include the most recent entry to ensure we show current data
        sampled_entries.append(entries[-1])

        return sampled_entries


# Docker container models
class DockerContainer(BaseModel):
    """Model representing a Docker container."""

    container_id: str = Field(..., description="Docker container ID (12-char short ID)")
    name: str = Field(..., description="Container name (without leading /)")
    image: str = Field(..., description="Full image name with tag")
    status: Literal["running", "stopped", "restarting", "exited", "paused", "dead"] = Field(
        ..., description="Container status"
    )
    port: str | None = Field(None, description="Primary host port")


# Notes models
class NoteEntry(BaseModel):
    """Model representing a single note entry."""

    id: int | None = Field(default=None, description="Unique identifier for the note entry")
    title: str = Field(..., description="Title of the note entry")
    content: str = Field(..., description="Content of the note entry")
    time_created: int = Field(default=0, description="Unix timestamp when the note was created")
    time_updated: int = Field(default=0, description="Unix timestamp when the note was last updated")


# Response models
class GetSystemInfoResponse(BaseResponse):
    """Response model for system information."""

    info: SystemInfo = Field(..., description="System information data")


class GetSystemMetricsResponse(BaseResponse):
    """Response model for system metrics."""

    metrics: SystemMetrics = Field(..., description="System metrics data")


class GetSystemMetricsHistoryResponse(BaseResponse):
    """Response model for system metrics history."""

    history: SystemMetricsHistory = Field(..., description="System metrics history data")


class NotesListResponse(BaseResponse):
    """Response model for listing notes."""

    notes: list[NoteEntry] = Field(..., description="List of note entries")


class NotesActionResponse(BaseResponse):
    """Response model for note actions (create/update/delete)."""

    note_id: str = Field(..., description="Note ID that was acted upon")


class DockerContainerListResponse(BaseResponse):
    """Response model for listing containers."""

    containers: list[DockerContainer] = Field(..., description="List of Docker containers")


class DockerContainerActionResponse(BaseResponse):
    """Response model for container actions (start/stop/restart/update)."""

    container_id: str = Field(..., description="Container ID that was acted upon")


class DockerContainerLogsResponse(BaseResponse):
    """Response model for container logs."""

    container_id: str = Field(..., description="Container ID whose logs were retrieved")
    logs: list[str] = Field(..., description="Log lines from the container")


# Request models
class GetSystemMetricsHistoryRequest(BaseModel):
    """Request model for system metrics history."""

    last_n_seconds: int = Field(..., ge=1, description="Number of seconds to retrieve history for")
    max_data_points: int = Field(..., ge=1, description="Maximum number of data points to return")


class NotesActionRequest(BaseModel):
    """Request model for performing a note action."""

    action: DatabaseAction = Field(..., description="The action to perform on the note entry")
    note: NoteEntry = Field(..., description="The note entry data for the action")
