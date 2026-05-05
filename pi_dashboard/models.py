"""Pydantic models for the server."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field
from python_template_server.models import BaseResponse, DatabaseConfig, TemplateServerConfig


# Pi Dashboard server configuration
class DashboardDatabaseConfig(DatabaseConfig):
    """Configuration for the database."""

    metrics_db_filename: str = Field(default="metrics.db", description="The filename for the metrics database.")
    metrics_lifetime_days: int = Field(
        default=7, ge=1, le=365, description="Number of days to keep metrics history in the database."
    )
    notes_db_filename: str = Field(default="notes.db", description="The filename for the notes database.")


class MetricsConfig(BaseModel):
    """Configuration model for system metrics collection."""

    collection_interval: int = Field(
        default=5, ge=1, le=60, description="Interval in seconds between metrics collections"
    )


class PiDashboardConfig(TemplateServerConfig):
    """Configuration model for the Pi Dashboard server."""

    db: DashboardDatabaseConfig = Field(default_factory=DashboardDatabaseConfig, description="Database configuration")
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

    id: int | None = Field(default=None, description="Unique identifier for the metrics entry")
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    uptime: int = Field(..., description="System uptime in seconds")
    temperature: float = Field(..., description="System temperature in Celsius")
    timestamp: int = Field(..., description="Unix timestamp of when the metrics were collected")


# Notes models
class NoteEntry(BaseModel):
    """Model representing a single note entry."""

    id: int | None = Field(default=None, description="Unique identifier for the note entry")
    title: str = Field(..., description="Title of the note entry")
    content: str = Field(..., description="Content of the note entry")
    time_created: int = Field(default=0, description="Unix timestamp when the note was created")
    time_updated: int = Field(default=0, description="Unix timestamp when the note was last updated")


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


# Response models
class GetSystemInfoResponse(BaseResponse):
    """Response model for system information."""

    info: SystemInfo = Field(..., description="System information data")


class GetSystemMetricsResponse(BaseResponse):
    """Response model for system metrics."""

    metrics: SystemMetrics = Field(..., description="System metrics data")


class GetSystemMetricsHistoryResponse(BaseResponse):
    """Response model for system metrics history."""

    history: list[SystemMetrics] = Field(..., description="System metrics history data")


class NotesListResponse(BaseResponse):
    """Response model for listing notes."""

    notes: list[NoteEntry] = Field(..., description="List of note entries")


class NotesActionResponse(BaseResponse):
    """Response model for note actions (create/update/delete)."""

    note_id: int = Field(..., description="Note ID that was acted upon")


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
