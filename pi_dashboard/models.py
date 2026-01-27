"""Pydantic models for the server."""

from typing import Literal
from uuid import uuid4

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


class WeatherConfig(BaseModel):
    """Configuration model for weather data."""

    latitude: float = Field(default=51.5074, ge=-90, le=90, description="Latitude coordinate for weather location")
    longitude: float = Field(default=-0.1278, ge=-180, le=180, description="Longitude coordinate for weather location")
    location_name: str = Field(default="London", description="Human-readable location name")
    forecast_hours: int = Field(
        default=12, ge=1, le=24, description="Number of hours to include in the weather forecast"
    )


class PiDashboardConfig(TemplateServerConfig):
    """Configuration model for the Pi Dashboard server."""

    metrics: MetricsConfig = Field(default_factory=MetricsConfig, description="System metrics collection configuration")
    weather: WeatherConfig = Field(default_factory=WeatherConfig, description="Weather configuration")


# General models
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


# Notes models
class Note(BaseModel):
    """Model representing a single note."""

    id: str = Field(..., description="Unique identifier (UUID) for the note")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    created_at: str = Field(..., description="Timestamp when the note was created")
    updated_at: str = Field(..., description="Timestamp when the note was last updated")


class NotesCollection(BaseModel):
    """Model representing a collection of notes."""

    notes: list[Note] = Field(default_factory=list, description="List of all notes")

    def get_note_by_id(self, note_id: str) -> Note | None:
        """Get a specific note by ID.

        :param str note_id: The UUID of the note to retrieve
        :return Note | None: The note if found, None otherwise
        """
        for note in self.notes:
            if note.id == note_id:
                return note
        return None

    def add_note(self, title: str, content: str, current_timestamp: str) -> Note:
        """Add a new note to the collection.

        :param str title: The title of the note
        :param str content: The content of the note
        :param str current_timestamp: The current timestamp for created_at and updated_at
        :return Note: The created note with generated ID and timestamps
        """
        note = Note(
            id=str(uuid4()),
            title=title,
            content=content,
            created_at=current_timestamp,
            updated_at=current_timestamp,
        )
        self.notes.append(note)
        return note

    def update_note(
        self, note_id: str, current_timestamp: str, title: str | None = None, content: str | None = None
    ) -> Note | None:
        """Update an existing note.

        :param str note_id: The UUID of the note to update
        :param str current_timestamp: The current timestamp for updated_at
        :param str | None title: The new title (if provided)
        :param str | None content: The new content (if provided)
        :return Note | None: The updated note if found, None otherwise
        """
        if (note := self.get_note_by_id(note_id)) is not None:
            note.title = title or note.title
            note.content = content or note.content
            note.updated_at = current_timestamp
        return note

    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID.

        :param str note_id: The UUID of the note to delete
        :return bool: True if the note was deleted, False if not found
        """
        if (note := self.get_note_by_id(note_id)) is not None:
            self.notes.remove(note)
            return True
        return False


# Weather models
class WeatherForecastHour(BaseModel):
    """Model representing a single hour in the weather forecast."""

    time: str = Field(..., description="Time of forecast (e.g., '3PM')")
    temperature: float = Field(..., description="Temperature in Celsius")
    weather_code: int = Field(..., description="WMO weather code")


class WeatherData(BaseModel):
    """Model representing current weather data."""

    location_name: str = Field(..., description="Human-readable location name")
    temperature: float = Field(..., description="Current temperature in Celsius")
    weather_code: int = Field(..., description="WMO weather code")
    high: float = Field(..., description="High temperature for the day in Celsius")
    low: float = Field(..., description="Low temperature for the day in Celsius")
    humidity: int = Field(..., ge=0, le=100, description="Relative humidity percentage")
    wind_speed: float = Field(..., ge=0, description="Wind speed in km/h")
    forecast: list[WeatherForecastHour] = Field(..., description="12-hour forecast")


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

    history: SystemMetricsHistory = Field(..., description="System metrics history data")


class GetNotesResponse(BaseResponse):
    """Response model for listing all notes."""

    notes: NotesCollection = Field(..., description="Collection of all notes")


class CreateNoteResponse(BaseResponse):
    """Response model for creating a note."""

    note: Note = Field(..., description="The created note")


class UpdateNoteResponse(BaseResponse):
    """Response model for updating a note."""

    note: Note = Field(..., description="The updated note")


class DeleteNoteResponse(BaseResponse):
    """Response model for deleting a note."""

    pass


class GetWeatherResponse(BaseResponse):
    """Response model for weather data."""

    weather: WeatherData = Field(..., description="Current weather data")


class GetWeatherLocationResponse(BaseResponse):
    """Response model for weather location."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    location_name: str = Field(..., description="Human-readable location name")


class ContainerListResponse(BaseResponse):
    """Response model for listing containers."""

    containers: list[DockerContainer] = Field(..., description="List of Docker containers")


class ContainerActionResponse(BaseResponse):
    """Response model for container actions (start/stop/restart/update)."""

    container_id: str = Field(..., description="Container ID that was acted upon")
    action: str = Field(..., description="Action that was performed")


# Request models
class GetSystemMetricsHistoryRequest(BaseModel):
    """Request model for system metrics history."""

    last_n_seconds: int = Field(..., ge=1, description="Number of seconds to retrieve history for")


class CreateNoteRequest(BaseModel):
    """Request model for creating a new note."""

    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., description="Note content")


class UpdateNoteRequest(BaseModel):
    """Request model for updating an existing note."""

    title: str | None = Field(None, min_length=1, max_length=200, description="Updated note title")
    content: str | None = Field(None, description="Updated note content")


class UpdateWeatherLocationRequest(BaseModel):
    """Request model for updating weather location."""

    location: str = Field(..., min_length=1, description="Location name to geocode")
