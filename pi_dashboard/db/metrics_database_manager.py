"""Metrics database manager."""

import logging

from sqlmodel import Field, Session, SQLModel, col, select

from pi_dashboard.db.base_database_manager import BaseDatabaseManager
from pi_dashboard.models import DatabaseAction, SystemMetrics, current_timestamp_int

logger = logging.getLogger(__name__)


# Database table models
class MetricsEntryDB(SQLModel, table=True):
    """Notes table."""

    __tablename__ = "metrics"

    id: int | None = Field(default=None, primary_key=True)
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    uptime: int = Field(..., description="System uptime in seconds")
    temperature: float = Field(..., description="System temperature in Celsius")
    timestamp: int = Field(..., description="Unix timestamp of when the metrics were collected")

    @classmethod
    def from_system_metrics(cls, metrics_entry: SystemMetrics) -> "MetricsEntryDB":
        """Create a MetricsEntryDB instance from a SystemMetrics."""
        return cls(
            cpu_usage=metrics_entry.cpu_usage,
            memory_usage=metrics_entry.memory_usage,
            disk_usage=metrics_entry.disk_usage,
            uptime=metrics_entry.uptime,
            temperature=metrics_entry.temperature,
            timestamp=metrics_entry.timestamp,
        )

    def to_system_metrics(self) -> SystemMetrics:
        """Convert the database model to a SystemMetrics."""
        return SystemMetrics(
            id=self.id,
            cpu_usage=self.cpu_usage,
            memory_usage=self.memory_usage,
            disk_usage=self.disk_usage,
            uptime=self.uptime,
            temperature=self.temperature,
            timestamp=self.timestamp,
        )


# Database manager class
class MetricsDatabaseManager(BaseDatabaseManager):
    """Manager class for metrics database operations."""

    @property
    def db_url(self) -> str:
        """Get the database URL."""
        return self.db_config.db_url(self.db_config.metrics_db_filename)

    def is_stale(self, entry: SystemMetrics) -> bool:
        """Return True if the metrics entry is older than the specified metrics lifetime.

        :param SystemMetrics entry: The metrics entry to check
        :return bool: True if the entry is stale
        """
        age = current_timestamp_int() - entry.timestamp
        return age >= self.db_config.metrics_lifetime_days * 86400

    def _get_all_metrics_entries(self, session: Session) -> list[SystemMetrics]:
        """Retrieve all metrics entries from the database."""
        statement = select(MetricsEntryDB).order_by(col(MetricsEntryDB.timestamp).desc())
        metrics_entries_db = session.exec(statement).all()
        return [metrics_db.to_system_metrics() for metrics_db in metrics_entries_db]

    def _get_metrics_entry_by_id(self, session: Session, metrics_id: int) -> MetricsEntryDB | None:
        """Retrieve a MetricsEntryDB by its ID."""
        statement = select(MetricsEntryDB).where(MetricsEntryDB.id == metrics_id)
        return session.exec(statement).first()

    def _create_metrics_entry(self, session: Session, metrics_entry: SystemMetrics) -> int | None:
        """Add a new metrics entry to the database."""
        metrics_db = MetricsEntryDB.from_system_metrics(metrics_entry=metrics_entry)
        session.add(metrics_db)
        session.commit()
        session.refresh(metrics_db)
        return metrics_db.id

    def _delete_metrics_entry(self, session: Session, metrics_db: MetricsEntryDB) -> int | None:
        """Delete a metrics entry from the database."""
        session.delete(metrics_db)
        session.commit()
        return metrics_db.id

    def get_all_metrics_entries(self) -> list[SystemMetrics]:
        """Public method to retrieve all metrics entries."""
        with Session(self.engine) as session:
            return self._get_all_metrics_entries(session)

    def perform_metrics_action(self, metrics_entry: SystemMetrics, action: DatabaseAction) -> int:
        """Perform a metrics action (create/update/delete) on the database."""
        with Session(self.engine) as session:
            match action:
                case DatabaseAction.CREATE:
                    if not (metrics_id := self._create_metrics_entry(session=session, metrics_entry=metrics_entry)):
                        error_msg = "Failed to create metrics entry."
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    return metrics_id
                case _:
                    error_msg = f"Unsupported action: {action}"
                    logger.error(error_msg)
                    raise NotImplementedError(error_msg)

    def cleanup_old_metrics(self) -> None:
        """Delete metrics entries that are older than the specified metrics lifetime."""
        with Session(self.engine) as session:
            all_metrics = self._get_all_metrics_entries(session=session)
            stale_metrics = [m for m in all_metrics if self.is_stale(m)]
            deleted_count = 0
            for metrics in stale_metrics:
                metrics_db = self._get_metrics_entry_by_id(session=session, metrics_id=metrics.id)
                if metrics_db:
                    self._delete_metrics_entry(session=session, metrics_db=metrics_db)
                    deleted_count += 1

            logger.info("Deleted %d stale metrics entries", deleted_count)
