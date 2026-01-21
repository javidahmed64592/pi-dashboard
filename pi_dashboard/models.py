"""Pydantic models for the server."""

from pydantic import BaseModel, Field
from python_template_server.models import BaseResponse, TemplateServerConfig


# Pi Dashboard server configuration
class MetricsConfig(BaseModel):
    """Configuration model for system metrics collection."""

    collection_interval: int = Field(
        default=5, ge=1, le=60, description="Interval in seconds between metrics collections"
    )
    max_history_duration: int = Field(
        default=1800, ge=60, le=3600, description="Maximum duration in seconds to keep metrics history"
    )


class PiDashboardConfig(TemplateServerConfig):
    """Configuration model for the Pi Dashboard server."""

    metrics: MetricsConfig = Field(default_factory=MetricsConfig, description="System metrics collection configuration")


# Response models
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

    def get_entries_since(self, seconds_ago: int, current_time: int) -> list[SystemMetricsHistoryEntry]:
        """Get entries from the last N seconds.

        :param int seconds_ago: Number of seconds to look back
        :param int current_time: Current Unix timestamp
        :return list[SystemMetricsHistoryEntry]: List of entries from the specified time range
        """
        cutoff_time = current_time - seconds_ago
        return [entry for entry in self.history if entry.timestamp >= cutoff_time]


class GetSystemInfoResponse(BaseResponse):
    """Response model for system information."""

    info: SystemInfo = Field(..., description="System information data")


class GetSystemMetricsResponse(BaseResponse):
    """Response model for system metrics."""

    metrics: SystemMetrics = Field(..., description="System metrics data")


class GetSystemMetricsHistoryResponse(BaseResponse):
    """Response model for system metrics history."""

    history: SystemMetricsHistory = Field(..., description="System metrics history data")


# Request models
class GetSystemMetricsHistoryRequest(BaseModel):
    """Request model for system metrics history."""

    last_n_seconds: int = Field(..., ge=1, description="Number of seconds to retrieve history for")
