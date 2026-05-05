"""Metrics database manager."""

import logging

from python_template_server.db.base_database_manager import BaseDatabaseManager
from sqlmodel import Field, Session, SQLModel, col, select

from pi_dashboard.models import DashboardDatabaseConfig, DatabaseAction, SystemMetrics, current_timestamp_int

logger = logging.getLogger(__name__)


# Database table models
class SystemMetricsDB(SQLModel, table=True):
    """System metrics table."""

    __tablename__ = "metrics"

    id: int | None = Field(default=None, primary_key=True)
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    uptime: int = Field(..., description="System uptime in seconds")
    temperature: float = Field(..., description="System temperature in Celsius")
    timestamp: int = Field(..., description="Unix timestamp of when the metrics were collected")

    @classmethod
    def from_system_metrics(cls, system_metrics: SystemMetrics) -> "SystemMetricsDB":
        """Create a SystemMetricsDB instance from a SystemMetrics."""
        return cls(
            cpu_usage=system_metrics.cpu_usage,
            memory_usage=system_metrics.memory_usage,
            disk_usage=system_metrics.disk_usage,
            uptime=system_metrics.uptime,
            temperature=system_metrics.temperature,
            timestamp=system_metrics.timestamp,
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

    def __init__(self, db_config: DashboardDatabaseConfig) -> None:
        """Initialize the NotesDatabaseManager with the given database configuration."""
        self.db_config: DashboardDatabaseConfig
        super().__init__(db_config)

    @property
    def db_url(self) -> str:
        """Get the database URL."""
        return self.db_config.db_url(self.db_config.metrics_db_filename)  # type: ignore[no-any-return]

    def is_stale(self, entry: SystemMetrics) -> bool:
        """Return True if the metrics entry is older than the specified metrics lifetime.

        :param SystemMetrics entry: The metrics entry to check
        :return bool: True if the entry is stale
        """
        age = current_timestamp_int() - entry.timestamp
        return age >= self.db_config.metrics_lifetime_days * 86400

    def _get_all_system_metrics_entries(self, session: Session) -> list[SystemMetrics]:
        """Retrieve all metrics entries from the database."""
        statement = select(SystemMetricsDB).order_by(col(SystemMetricsDB.timestamp).desc())
        metrics_entries_db = session.exec(statement).all()
        return [metrics_db.to_system_metrics() for metrics_db in metrics_entries_db]

    def _get_system_metrics_by_id(self, session: Session, metrics_id: int) -> SystemMetricsDB | None:
        """Retrieve a SystemMetricsDB by its ID."""
        statement = select(SystemMetricsDB).where(SystemMetricsDB.id == metrics_id)
        return session.exec(statement).first()

    def _get_system_metrics_by_timestamp(self, session: Session, timestamp: int) -> SystemMetricsDB | None:
        """Retrieve a SystemMetricsDB by its timestamp."""
        statement = select(SystemMetricsDB).where(SystemMetricsDB.timestamp == timestamp)
        return session.exec(statement).first()

    def _create_system_metrics_entry(self, session: Session, system_metrics: SystemMetrics) -> int | None:
        """Add a new metrics entry to the database."""
        if existing_entry := self._get_system_metrics_by_timestamp(session=session, timestamp=system_metrics.timestamp):
            logger.warning(
                "Metrics entry with timestamp %d already exists, skipping creation", system_metrics.timestamp
            )
            return existing_entry.id

        metrics_db = SystemMetricsDB.from_system_metrics(system_metrics=system_metrics)
        session.add(metrics_db)
        session.commit()
        session.refresh(metrics_db)
        return metrics_db.id

    def _delete_system_metrics_entry(self, session: Session, metrics_db: SystemMetricsDB) -> int | None:
        """Delete a metrics entry from the database."""
        session.delete(metrics_db)
        session.commit()
        return metrics_db.id

    def get_all_system_metrics_entries(self) -> list[SystemMetrics]:
        """Public method to retrieve all metrics entries."""
        with Session(self.engine) as session:
            return self._get_all_system_metrics_entries(session)

    def get_system_metrics_entries_since(self, last_n_seconds: int, max_data_points: int) -> list[SystemMetrics]:
        """Get metrics entries from the last N seconds with adaptive downsampling."""
        with Session(self.engine) as session:
            cutoff_time = current_timestamp_int() - last_n_seconds
            statement = (
                select(SystemMetricsDB)
                .where(col(SystemMetricsDB.timestamp) >= cutoff_time)
                .order_by(col(SystemMetricsDB.timestamp).asc())
            )
            metrics_entries_db = session.exec(statement).all()

            # Adaptive downsampling if there are more entries than max_data_points
            if len(metrics_entries_db) > max_data_points:
                step = len(metrics_entries_db) // max_data_points
                metrics_entries_db = metrics_entries_db[::step]

            return [metrics_db.to_system_metrics() for metrics_db in metrics_entries_db]

    def perform_system_metrics_action(self, system_metrics: SystemMetrics, action: DatabaseAction) -> int:
        """Perform a metrics action (create/update/delete) on the database."""
        with Session(self.engine) as session:
            match action:
                case DatabaseAction.CREATE:
                    if not (
                        metrics_id := self._create_system_metrics_entry(session=session, system_metrics=system_metrics)
                    ):
                        error_msg = "Failed to create metrics entry."
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    return metrics_id
                case _:
                    error_msg = f"Unsupported action: {action}"
                    logger.error(error_msg)
                    raise NotImplementedError(error_msg)

    def cleanup_old_system_metrics(self) -> None:
        """Delete metrics entries that are older than the specified metrics lifetime."""
        with Session(self.engine) as session:
            all_metrics = self._get_all_system_metrics_entries(session=session)
            stale_metrics = [m for m in all_metrics if self.is_stale(m)]
            deleted_count = 0
            for metrics in stale_metrics:
                metrics_db = self._get_system_metrics_by_id(session=session, metrics_id=metrics.id)  # type: ignore[arg-type]
                if metrics_db:
                    self._delete_system_metrics_entry(session=session, metrics_db=metrics_db)
                    deleted_count += 1

            if deleted_count > 0:
                logger.info("Deleted %d stale metrics entries", deleted_count)
